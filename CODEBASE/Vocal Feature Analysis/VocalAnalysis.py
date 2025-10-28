import torch
import torchaudio
import whisper
from pyannote.audio import Pipeline
from transformers import Wav2Vec2ForSequenceClassification, Wav2Vec2FeatureExtractor
import numpy as np
import os
import sys
from convert_audio import convert_to_wav
import noisereduce as nr
from scipy import signal
from langdetect import detect, LangDetectException

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
        print("Loading Emotion Recognition model (Wav2Vec2)...")
        model_name = "ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition"
        self.emotion_model = Wav2Vec2ForSequenceClassification.from_pretrained(
            model_name,
            cache_dir="pretrained_models/emotion_model"
        ).to(self.device)
        self.emotion_feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(
            model_name,
            cache_dir="pretrained_models/emotion_model"
        )
        self.emotion_model.eval()

        # Emotion labels for this model
        self.emotion_labels = ['angry', 'calm', 'disgust', 'fearful', 'happy', 'neutral', 'sad', 'surprised']
        print("Emotion Recognition model loaded.")

    def _preprocess_audio(self, waveform, sample_rate=16000):
        """
        Apply comprehensive audio preprocessing for better analysis quality.
        Args:
            waveform (torch.Tensor): The audio signal (1D or 2D tensor).
            sample_rate (int): The sample rate of the audio.

        Returns:
            torch.Tensor: Preprocessed audio waveform
        """
        # Convert to numpy for processing
        if isinstance(waveform, torch.Tensor):
            audio_np = waveform.squeeze().cpu().numpy()
        else:
            audio_np = waveform

        # 1. Noise Reduction using spectral gating
        print("  Applying noise reduction...")
        try:
            # Use first 0.5 seconds as noise profile (if available)
            audio_np = nr.reduce_noise(
                y=audio_np,
                sr=sample_rate,
                stationary=True,
                prop_decrease=0.8
            )
        except Exception as e:
            print(f"  Warning: Noise reduction failed: {e}, continuing without it")

        # 2. Normalize audio amplitude
        print("  Normalizing audio amplitude...")
        max_val = np.abs(audio_np).max()
        if max_val > 0:
            audio_np = audio_np / max_val * 0.95  # Normalize to 95% to avoid clipping

        # 3. Apply high-pass filter to remove low-frequency noise (< 80Hz)
        print("  Applying high-pass filter...")
        sos = signal.butter(4, 80, 'hp', fs=sample_rate, output='sos')
        audio_np = signal.sosfilt(sos, audio_np)

        # 4. Apply low-pass filter to remove high-frequency noise (> 7.5kHz)
        # Note: Cutoff must be < fs/2 (Nyquist frequency)
        print("  Applying low-pass filter...")
        sos = signal.butter(4, 7500, 'lp', fs=sample_rate, output='sos')
        audio_np = signal.sosfilt(sos, audio_np)

        # Convert back to tensor
        return torch.from_numpy(audio_np).float().unsqueeze(0)

    def _detect_language(self, text):
        """
        Detect the language of the transcribed text.
        Args:
            text (str): The transcribed text.

        Returns:
            str: ISO 639-1 language code (e.g., 'en', 'ru', 'ko') or 'unknown'
        """
        if not text or len(text.strip()) < 3:
            return 'unknown'

        try:
            lang = detect(text)
            return lang
        except LangDetectException:
            return 'unknown'

    def _is_valid_segment(self, transcript, duration_sec, min_duration=1.0):
        """
        Check if a segment is valid for analysis.
        Args:
            transcript (str): The transcribed text.
            duration_sec (float): Duration of the segment in seconds.
            min_duration (float): Minimum duration threshold in seconds.

        Returns:
            tuple: (is_valid, reason) where is_valid is bool and reason is str
        """
        # Filter 1: Check minimum duration
        if duration_sec < min_duration:
            return False, f"too_short ({duration_sec:.2f}s < {min_duration}s)"

        # Filter 2: Check for empty or very short transcripts
        if not transcript or len(transcript.strip()) < 2:
            return False, "empty_transcript"

        # Filter 3: Language detection - only accept English
        detected_lang = self._detect_language(transcript)
        if detected_lang != 'en' and detected_lang != 'unknown':
            return False, f"non_english (detected: {detected_lang})"

        # Filter 4: Check for hallucination indicators (non-ASCII characters suggesting wrong language)
        try:
            transcript.encode('ascii')
        except UnicodeEncodeError:
            # Contains non-ASCII characters - likely a hallucination
            return False, "non_ascii_characters"

        return True, "valid"

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

    def _recognize_emotion(self, waveform, sample_rate=16000):
        """
        Recognize emotion from audio waveform using Wav2Vec2 model.
        Args:
            waveform (torch.Tensor): The audio signal (1D or 2D tensor).
            sample_rate (int): The sample rate of the audio.

        Returns:
            tuple: (dominant_emotion, emotion_scores_dict)
        """
        try:
            # Ensure waveform is 1D numpy array
            if isinstance(waveform, torch.Tensor):
                waveform_np = waveform.squeeze().cpu().numpy()
            else:
                waveform_np = waveform

            # Ensure it's 1D
            if waveform_np.ndim > 1:
                waveform_np = waveform_np[0]

            # Minimum length check
            min_samples = 16000  # 1 second minimum
            if len(waveform_np) < min_samples:
                # Pad if too short
                padding = min_samples - len(waveform_np)
                waveform_np = np.pad(waveform_np, (0, padding), mode='constant')

            # Extract features
            inputs = self.emotion_feature_extractor(
                waveform_np,
                sampling_rate=sample_rate,
                return_tensors="pt",
                padding=True
            )

            # Move to device
            input_values = inputs.input_values.to(self.device)

            # Get predictions
            with torch.no_grad():
                logits = self.emotion_model(input_values).logits
                probabilities = torch.nn.functional.softmax(logits, dim=-1)

            # Get emotion scores
            probs = probabilities[0].cpu().numpy()
            emotion_scores = {self.emotion_labels[i]: float(probs[i]) for i in range(len(self.emotion_labels))}

            # Get dominant emotion
            dominant_idx = np.argmax(probs)
            dominant_emotion = self.emotion_labels[dominant_idx]

            return dominant_emotion, emotion_scores

        except Exception as e:
            print(f"Warning: Emotion recognition failed: {e}")
            return "unknown", {}

    def process_audio(self, audio_path, practitioner_speaker_id="SPEAKER_01", min_segment_duration=1.0):
        """
        Processes a single audio file through the full pipeline.
        Args:
            audio_path (str): Path to the audio file.
            practitioner_speaker_id (str): The label assigned to the practitioner by the diarization model.
                                           This may need to be determined dynamically. For this example, we assume a fixed ID.
            min_segment_duration (float): Minimum duration for segments to be analyzed (in seconds).

        Returns:
            list: A list of dictionaries, where each dictionary represents a speech segment.
        """
        print(f"\nProcessing audio file: {audio_path}")

        # Check if the file is not a WAV file - if so, convert it first
        file_ext = os.path.splitext(audio_path)[1].lower()
        converted_file = None

        if file_ext != '.wav':
            print(f"Detected non-WAV file format ({file_ext}). Converting to WAV format...")
            try:
                # Use the existing convert_audio module to convert the file
                converted_file = convert_to_wav(audio_path)
                audio_path = converted_file
                print(f"Using converted file: {audio_path}")
            except Exception as e:
                print(f"\nError during audio conversion: {e}")
                print("Please ensure ffmpeg is installed and in your system PATH.")
                print("Download from: https://ffmpeg.org/download.html")
                return None

        # --- Step 1: Load Audio ---
        try:
            waveform, sample_rate = torchaudio.load(audio_path)
            print("Audio loaded successfully.")
        except Exception as e:
            print(f"Error loading audio file: {e}")
            return None

        # Resample to 16kHz, convert to mono
        if sample_rate != 16000:
            resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
            waveform = resampler(waveform)

        if waveform.shape[0] > 1:  # If stereo, convert to mono
            waveform = torch.mean(waveform, dim=0, keepdim=True)

        print("Audio preprocessed (16kHz, mono).")

        # --- Step 1.5: Apply Advanced Preprocessing ---
        print("\nApplying advanced audio preprocessing...")
        waveform = self._preprocess_audio(waveform, sample_rate=16000)
        print("Advanced preprocessing complete.")

        # --- Step 2: Perform Speaker Diarization ---
        print("\nRunning diarization...")
        diarization_result = self.diarization_pipeline({"waveform": waveform, "sample_rate": 16000})
        print("Diarization complete.")

        conversation_data = []
        segment_id_counter = 0
        filtered_count = 0
        filter_reasons = {}

        # --- Steps 3, 4, 5: Iterate, Transcribe, and Analyze ---
        print(f"\nIterating through segments for transcription and analysis...")
        print(f"Filtering segments shorter than {min_segment_duration}s and non-English content...")
        # In pyannote.audio 3.x+, DiarizeOutput has a 'speaker_diarization' attribute
        # that contains the annotation object
        annotation = diarization_result.speaker_diarization

        # Now iterate over the annotation
        for segment, track, speaker in annotation.itertracks(yield_label=True):
            segment_start_sec = segment.start
            segment_end_sec = segment.end
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

            # Check if segment is valid (duration, language, etc.)
            is_valid, filter_reason = self._is_valid_segment(transcript, duration_sec, min_segment_duration)

            if not is_valid:
                filtered_count += 1
                filter_reasons[filter_reason] = filter_reasons.get(filter_reason, 0) + 1
                print(f"  Skipping segment {segment_id_counter} ({speaker}): {filter_reason}")
                continue

            segment_data = {
                "segment_id": segment_id_counter,
                "speaker_label": "Patient" if speaker != practitioner_speaker_id else "Practitioner",
                "start_time": round(segment_start_sec, 3),
                "end_time": round(segment_end_sec, 3),
                "duration": round(duration_sec, 3),
                "transcript": transcript,
                "vocal_analysis": None
            }

            # Perform vocal analysis for ALL speakers (not just practitioner)
            if segment_waveform.numel() > 0:
                # Speech Rate
                word_count = len(transcript.split())
                speech_rate_wps = word_count / duration_sec if duration_sec > 0 else 0

                # Emotion Recognition for all speakers
                print(f"  Analyzing emotions for segment {segment_id_counter} ({segment_data['speaker_label']})...")
                dominant_emotion, emotion_scores = self._recognize_emotion(segment_waveform, 16000)

                # Low-level vocal features
                vocal_features = self._extract_vocal_features(segment_waveform, 16000)
                vocal_features["speech_rate_wps"] = round(speech_rate_wps, 2)
                vocal_features["emotion_recognition"] = {
                    "dominant_emotion": dominant_emotion,
                    "scores": emotion_scores
                }
                segment_data["vocal_analysis"] = vocal_features

            conversation_data.append(segment_data)
            segment_id_counter += 1

        print(f"\nProcessing complete.")
        print(f"Total segments analyzed: {len(conversation_data)}")
        print(f"Segments filtered out: {filtered_count}")
        if filter_reasons:
            print(f"Filter breakdown:")
            for reason, count in filter_reasons.items():
                print(f"  - {reason}: {count}")

        return conversation_data


# Example Usage
if __name__ == '__main__':
    # Check for CUDA availability
    selected_device = "cuda" if torch.cuda.is_available() else "cpu"

    # Instantiate the pipeline
    pipeline = VocalAnalysisPipeline(device=selected_device)

    # Use the real audio file
    audio_path = r"C:\Users\elija\OneDrive\Desktop\MAYO REPO\Synapse\CODEBASE\Vocal Feature Analysis\test_audio.m4a"

    # Check if file exists
    if not os.path.exists(audio_path):
        print(f"Error: Audio file not found at {audio_path}")
        sys.exit(1)

    print(f"Using audio file: {audio_path}")

    # Process the audio file
    # Note: The practitioner_speaker_id may need to be adjusted based on which speaker
    # the diarization model assigns to the practitioner. You may need to run it once
    # and check the output to determine the correct speaker ID.
    analysis_result = pipeline.process_audio(audio_path, practitioner_speaker_id="SPEAKER_00")

    # Print the result in a readable format
    import json

    # Save results even if processing had issues
    output_file = "analysis_result.json"

    if analysis_result is not None:
        print("\n--- Analysis Result ---")
        print(json.dumps(analysis_result, indent=2))

        # Save to a file
        with open(output_file, 'w') as f:
            json.dump(analysis_result, f, indent=2)
        print(f"\nResults saved to: {output_file}")
    else:
        print("\n--- Analysis Failed ---")
        print("No results to save. Check error messages above.")
        # Save an empty result with error indication
        with open(output_file, 'w') as f:
            json.dump({"error": "Processing failed", "segments": []}, f, indent=2)
        print(f"\nError status saved to: {output_file}")
