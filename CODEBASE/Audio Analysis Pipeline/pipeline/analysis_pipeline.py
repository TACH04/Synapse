"""
Analysis Pipeline Orchestrator
Manages the entire end-to-end data flow of the clinical audio analysis system.
"""

import json
import os
import warnings
import torch
from tqdm import tqdm
from typing import Dict, Any, Optional

# Suppress warnings for performance
warnings.filterwarnings('ignore')

# Enable PyTorch optimizations
if torch.cuda.is_available():
    torch.backends.cudnn.benchmark = True
    torch.backends.cudnn.enabled = True

# Import all our modules
from . import audio_utilities as au
from .services.diarization_service import DiarizationService
from .services.asr_service import ASRService
from .services.acoustic_service import AcousticService
from .services.emotion_service import EmotionService


class AnalysisPipeline:
    """
    Orchestrates the entire audio analysis pipeline from end-to-end.

    This is the "brain" of the system. It initializes all services once
    (loading all ML models into memory) and manages the complete data flow:
    1. Load audio file
    2. Run diarization to get speaker segments
    3. For each segment:
        a. Slice audio
        b. Run ASR (transcription)
        c. Run emotion recognition
        d. Run acoustic feature extraction
    4. Aggregate results and save as JSON
    """

    def __init__(self,
                 hf_token: str,
                 emotion_model_path: str = "superb/hubert-base-superb-er",
                 asr_model: str = "base.en"):
        """
        Initializes the pipeline by loading all ML models into memory.

        Args:
            hf_token (str): Hugging Face auth token (for Diarization)
            emotion_model_path (str): Path for the EmotionService (supports hot-swap)
            asr_model (str): The faster-whisper model to use
        """
        print("=" * 60)
        print("Initializing Clinical Audio Analysis Pipeline...")
        print("=" * 60)

        self.diarization_service = DiarizationService(auth_token=hf_token)
        self.asr_service = ASRService(model_name=asr_model)
        self.acoustic_service = AcousticService()

        # Initialize Triple Ensemble Emotion Service
        # Mode options: 'dual_audio' or 'triple_ensemble'
        self.emotion_service = EmotionService(
            mode='triple_ensemble',  # Use all three models for maximum accuracy
            hubert_model=emotion_model_path,  # Prosody analysis
            wav2vec2_model="ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition",  # Phonetic analysis
            text_model="j-hartmann/emotion-english-distilroberta-base"  # Semantic analysis
        )

        print("=" * 60)
        print("All services initialized successfully!")
        print("=" * 60)

    def run(self, audio_file_path: str, output_json_path: str, num_speakers: int = 2):
        """
        Runs the full analysis pipeline on a single audio file.

        Args:
            audio_file_path (str): Path to the input audio file
            output_json_path (str): Path where the JSON output will be saved
            num_speakers (int): Number of speakers to detect (default: 2)
        """
        print(f"\n{'='*60}")
        print(f"Starting pipeline for: {audio_file_path}")
        print(f"{'='*60}\n")

        # 1. Load and resample audio
        try:
            full_audio_array, sample_rate = au.load_and_resample_audio(audio_file_path)
            duration = len(full_audio_array) / sample_rate
            print(f"✓ Audio loaded successfully")
            print(f"  Duration: {duration:.2f} seconds")
            print(f"  Sample rate: {sample_rate} Hz")
            print(f"  Total samples: {len(full_audio_array):,}\n")
        except Exception as e:
            print(f"✗ Error loading audio file: {e}")
            return

        # 2. Get speaker segments
        print("Step 1/4: Running Speaker Diarization...")
        speaker_segments = self.diarization_service.process(audio_file_path, num_speakers)
        if not speaker_segments:
            print("✗ No speaker segments found. Exiting.")
            return

        print(f"✓ Found {len(speaker_segments)} speaker segments")

        # IMPROVEMENT #7: Merge adjacent same-speaker segments
        merged_segments = self._merge_segments(speaker_segments)
        print(f"✓ Merged to {len(merged_segments)} segments (filtered & merged)\n")

        final_output = {
            "file": os.path.basename(audio_file_path),
            "segments": []
        }

        # 3. Iterate segments and process
        print("Step 2/4: Processing segments...")
        for i, segment in enumerate(tqdm(merged_segments, desc="Analyzing", unit="segment")):
            start_sec = segment["start_time"]
            end_sec = segment["end_time"]

            # IMPROVEMENT #8: Add padding for better context (0.1s before and after)
            padding = 0.1
            padded_start = max(0, start_sec - padding)
            padded_end = min(duration, end_sec + padding)

            # a. Slice audio with padding
            audio_slice = au.slice_audio(full_audio_array, sample_rate, padded_start, padded_end)

            if audio_slice.size == 0:
                continue  # Skip empty slices

            # b. Run analyses (ASR first, then pass transcript to emotion service)
            transcript = self.asr_service.process(audio_slice)

            # Get acoustic features first
            acoustics = self.acoustic_service.process(audio_slice)

            # Pass transcript AND acoustic features to emotion service for hybrid analysis
            emotion = self.emotion_service.process(
                audio_slice,
                transcript=transcript if transcript else "",
                acoustic_features=acoustics
            )

            # c. Collect data into the specified schema
            segment_data = {
                "segment_id": i,
                "speaker": segment["speaker"],
                "start_time": round(start_sec, 3),
                "end_time": round(end_sec, 3),
                "duration": round(end_sec - start_sec, 3),
                "transcript": transcript,
                "predicted_emotion": emotion,
                "acoustic_features": acoustics
            }
            final_output["segments"].append(segment_data)

        # 4. Save final JSON
        print("\nStep 3/4: Saving results...")
        try:
            with open(output_json_path, 'w', encoding='utf-8') as f:
                json.dump(final_output, f, indent=4, ensure_ascii=False)
            print(f"✓ Analysis complete!")
            print(f"  Output saved to: {output_json_path}")
            print(f"  Total segments processed: {len(final_output['segments'])}")
        except Exception as e:
            print(f"✗ Error saving JSON output: {e}")

        print(f"\n{'='*60}")
        print("Pipeline execution completed")
        print(f"{'='*60}\n")

    def _merge_segments(self, segments, max_gap: float = 1.0, min_duration: float = 0.3, max_duration: float = 30.0):
        """
        Merge adjacent segments from the same speaker and filter out too-short segments.

        IMPROVEMENT #7: Segment Merging & Filtering

        Args:
            segments: List of diarization segments
            max_gap: Maximum gap (seconds) to merge across (default: 1.0s)
            min_duration: Minimum segment duration to keep (default: 0.3s)
            max_duration: Maximum merged segment duration (default: 30.0s)

        Returns:
            List of merged and filtered segments
        """
        if not segments:
            return []

        # Sort by start time
        sorted_segments = sorted(segments, key=lambda x: x['start_time'])

        merged = []
        current = sorted_segments[0].copy()

        for next_seg in sorted_segments[1:]:
            same_speaker = (current['speaker'] == next_seg['speaker'])
            gap = next_seg['start_time'] - current['end_time']
            would_be_too_long = (next_seg['end_time'] - current['start_time']) > max_duration

            # Merge if: same speaker, gap small enough, and won't exceed max duration
            if same_speaker and gap <= max_gap and not would_be_too_long:
                # Extend current segment
                current['end_time'] = next_seg['end_time']
            else:
                # Save current and start new
                duration = current['end_time'] - current['start_time']
                if duration >= min_duration:  # Only keep if long enough
                    merged.append(current)
                current = next_seg.copy()

        # Don't forget the last segment
        duration = current['end_time'] - current['start_time']
        if duration >= min_duration:
            merged.append(current)

        return merged

