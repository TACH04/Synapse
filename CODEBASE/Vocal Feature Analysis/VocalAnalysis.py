import torch
import torchaudio
import whisper
from pyannote.audio import Pipeline
from speechbrain.inference.classifiers import EncoderClassifier
from speechbrain.utils.fetching import LocalStrategy
import numpy as np
import os
import sys

# Hugging Face token for accessing gated models
HF_TOKEN = "REDACTED"

if HF_TOKEN is None or HF_TOKEN == "YOUR_HF_TOKEN":
    print("\n" + "="*80)
    print("ERROR: Hugging Face Token Not Set!")
    print("="*80)
    print("\nTo fix this, you need to:")
    print("\n1. Visit https://huggingface.co/pyannote/speaker-diarization-3.1")
    print("   and click 'Agree and access repository' to accept the terms")
    print("\n2. Create a token at https://huggingface.co/settings/tokens")
    print("   - Click 'New token'")
    print("   - Give it a name (e.g., 'synapse-vocal-analysis')")
    print("   - Select 'Read' permissions")
    print("   - Copy the token (starts with 'hf_')")
    print("\n3. Set the token as an environment variable:")
    print("   In PowerShell, run:")
    print("   $env:HF_TOKEN = \"hf_your_token_here\"")
    print("\n   OR edit this file and replace line 12 with:")
    print("   HF_TOKEN = \"hf_your_actual_token_here\"")
    print("\n" + "="*80 + "\n")
    sys.exit(1)


class VocalAnalysisPipeline:
    """
    A comprehensive pipeline for processing doctor-patient conversations.
    It performs speaker diarization, transcription, and vocal feature analysis
    for the practitioner's speech segments.
    """

    def __init__(self, device="cpu"):
        """
        Initializes the pipeline by loading all necessary models.
        Args:
            device (str): The device to run the models on ('cpu' or 'cuda').
        """
        print(f"Initializing pipeline on device: {device}")
        self.device = torch.device(device)

        # Step 1: Load Diarization Model
        print("Loading Diarization model (pyannote.audio)...")
        self.diarization_pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            token=HF_TOKEN
        ).to(self.device)
        print("Diarization model loaded.")

        # Step 2: Load Transcription Model
        print("Loading Transcription model (Whisper)...")
        self.transcription_model = whisper.load_model("base").to(self.device)
        print("Transcription model loaded.")

        # Step 3: Load Speech Emotion Recognition Model
        print("Loading Emotion Recognition model (SpeechBrain)...")
        self.emotion_classifier = EncoderClassifier.from_hparams(
            source="speechbrain/emotion-recognition-wav2vec2-IEMOCAP",
            savedir="pretrained_models/ser_model",
            local_strategy=LocalStrategy.COPY  # Use COPY instead of SYMLINK for Windows compatibility
        ).to(self.device)
        print("Emotion Recognition model loaded.")

    def _extract_vocal_features(self, waveform, sample_rate):
        """
        Extracts low-level vocal features from a single audio waveform.
        Args:
            waveform (torch.Tensor): The audio signal.
            sample_rate (int): The sample rate of the audio.

        Returns:
            dict: A dictionary containing prosody and voice quality features.
        """
        # Ensure waveform is on the correct device
        waveform = waveform.to(self.device)

        # --- Prosody: Intensity ---
        # Calculate RMS energy as intensity
        intensity_db = 20 * torch.log10(torch.sqrt(torch.mean(waveform ** 2)) + 1e-8).item()

        # --- Voice Quality Features (Simplified) ---
        # Note: For production use, consider using libraries like praat-parselmouth
        # for more accurate jitter, shimmer, and HNR calculations.
        # These are simplified placeholder implementations.

        # Basic pitch estimation using autocorrelation (simplified)
        # Frame the signal
        frame_length = 800  # 50ms at 16kHz
        hop_length = 400    # 25ms at 16kHz

        # Simplified placeholder values for voice quality
        # In production, use proper algorithms or libraries like parselmouth
        features = {
            "prosody": {
                "pitch_hz": {"mean": 150.0, "std_dev": 25.0},  # Placeholder values
                "intensity_db": {"mean": intensity_db}
            },
            "voice_quality": {
                "jitter_percent": None,  # Requires proper pitch period analysis
                "shimmer_percent": None,  # Requires proper amplitude perturbation analysis
                "hnr_db": None  # Requires proper harmonic-to-noise ratio calculation
            }
        }
        return features

    def process_audio(self, audio_path, practitioner_speaker_id="SPEAKER_01"):
        """
        Processes a single audio file through the full pipeline.
        Args:
            audio_path (str): Path to the audio file.
            practitioner_speaker_id (str): The label assigned to the practitioner by the diarization model.
                                           This may need to be determined dynamically. For this example, we assume a fixed ID.

        Returns:
            list: A list of dictionaries, where each dictionary represents a speech segment.
        """
        print(f"\nProcessing audio file: {audio_path}")

        # --- Step 1: Load and Resample Audio ---
        try:
            waveform, sample_rate = torchaudio.load(audio_path)
        except Exception as e:
            print(f"Error loading audio file: {e}")
            return

        # Resample to 16kHz, convert to mono
        if sample_rate != 16000:
            resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
            waveform = resampler(waveform)

        if waveform.shape[0] > 1:  # If stereo, convert to mono
            waveform = torch.mean(waveform, dim=0, keepdim=True)

        print("Audio loaded and preprocessed.")

        # --- Step 2: Perform Speaker Diarization ---
        print("Running diarization...")
        diarization = self.diarization_pipeline({"waveform": waveform, "sample_rate": 16000})
        print("Diarization complete.")

        conversation_data = []
        segment_id_counter = 0

        # --- Steps 3, 4, 5: Iterate, Transcribe, and Analyze ---
        print("Iterating through segments for transcription and analysis...")
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segment_start_sec = turn.start
            segment_end_sec = turn.end
            duration_sec = segment_end_sec - segment_start_sec

            # Extract audio chunk for this segment
            start_frame = int(segment_start_sec * 16000)
            end_frame = int(segment_end_sec * 16000)
            segment_waveform = waveform[:, start_frame:end_frame]

            # Perform Transcription
            result = self.transcription_model.transcribe(
                segment_waveform.squeeze(0).cpu().numpy(),
                fp16=False if self.device.type == 'cpu' else True
            )
            transcript = result['text'].strip()

            segment_data = {
                "segment_id": segment_id_counter,
                "speaker_label": "Patient" if speaker != practitioner_speaker_id else "Practitioner",
                "start_time": round(segment_start_sec, 3),
                "end_time": round(segment_end_sec, 3),
                "transcript": transcript,
                "vocal_analysis": None
            }

            # If the speaker is the practitioner, perform vocal analysis
            if segment_data["speaker_label"] == "Practitioner" and segment_waveform.numel() > 0:
                # Speech Rate
                word_count = len(transcript.split())
                speech_rate_wps = word_count / duration_sec if duration_sec > 0 else 0

                # Emotion Recognition
                out_prob, score, index, text_lab = self.emotion_classifier.classify_batch(segment_waveform)

                emotion_scores = {label.lower(): prob.item() for label, prob in
                                  zip(self.emotion_classifier.hparams.label_encoder.get_ind2lab().values(), out_prob)}

                # Low-level vocal features
                vocal_features = self._extract_vocal_features(segment_waveform, 16000)
                vocal_features["speech_rate_wps"] = round(speech_rate_wps, 2)
                vocal_features["emotion_recognition"] = {
                    "dominant_emotion": text_lab.lower(),
                    "scores": emotion_scores
                }
                segment_data["vocal_analysis"] = vocal_features

            conversation_data.append(segment_data)
            segment_id_counter += 1

        print("Processing complete.")
        return conversation_data


# Example Usage
if __name__ == '__main__':
    # Check for CUDA availability
    selected_device = "cuda" if torch.cuda.is_available() else "cpu"

    # Instantiate the pipeline
    pipeline = VocalAnalysisPipeline(device=selected_device)

    # Create a dummy audio file for demonstration
    # In a real scenario, you would use an actual recording path.
    dummy_audio_path = "sample_conversation.wav"
    sample_rate = 16000
    # Create a 10-second silent audio file with two speech segments
    # Segment 1 (Patient): 1s - 4s
    # Segment 2 (Practitioner): 5s - 9s
    t = torch.linspace(0., 10., 160000)
    patient_speech = torch.cos(2 * torch.pi * 220 * t[1 * sample_rate:4 * sample_rate]) * 0.5
    practitioner_speech = torch.cos(2 * torch.pi * 150 * t[5 * sample_rate:9 * sample_rate]) * 0.5
    dummy_waveform = torch.zeros(1, 10 * sample_rate)
    dummy_waveform[0, 1 * sample_rate:4 * sample_rate] = patient_speech
    dummy_waveform[0, 5 * sample_rate:9 * sample_rate] = practitioner_speech
    torchaudio.save(dummy_audio_path, dummy_waveform, sample_rate)

    # Process the audio file
    # Note: Diarization models are trained on real speech and may not perform perfectly on synthetic tones.
    # The output structure is the key takeaway.
    # We assume the model correctly identifies the practitioner as SPEAKER_01. This might change file to file.
    analysis_result = pipeline.process_audio(dummy_audio_path, practitioner_speaker_id="SPEAKER_01")

    # Print the result in a readable format
    import json

    print("\n--- Analysis Result ---")
    print(json.dumps(analysis_result, indent=2))