"""
Acoustic Service
Extracts objective acoustic features from audio using parselmouth-praat.
"""

import parselmouth
import numpy as np
from typing import Dict, Optional, Any


class AcousticService:
    """
    Extracts objective acoustic features from an audio slice using parselmouth-praat.

    This service answers the question: "How was it said? (Objective)"
    Provides quantitative, physical features of speech.
    """

    def __init__(self, sample_rate: int = 16000):
        """
        Initializes the service.

        Args:
            sample_rate (int): The sample rate of the incoming audio
        """
        self.sample_rate = sample_rate
        # A small floor to prevent Praat from crashing on near-silence
        self.silence_threshold = 0.01

    def process(self, audio_slice: np.ndarray) -> Optional[Dict[str, Any]]:
        """
        Analyzes an audio slice for pitch, jitter, shimmer, and HNR.

        Args:
            audio_slice (np.ndarray): The 1D audio array (at 16kHz)

        Returns:
            Optional[Dict[str, Any]]: A dictionary of features containing:
                - pitch_mean_f0: Mean fundamental frequency (Hz)
                - jitter_local: Local jitter (vocal stability measure)
                - shimmer_local: Local shimmer (amplitude variation)
                - hnr_mean: Mean Harmonics-to-Noise Ratio (voice quality)
            Returns None if analysis fails.

        Note:
            Praat is fragile and will fail on very short or silent audio.
            This method handles failures gracefully to prevent pipeline crashes.
        """
        # Check for silence to prevent Praat crashes
        if audio_slice.size == 0 or np.max(np.abs(audio_slice)) < self.silence_threshold:
            return None

        try:
            # Load audio slice into parselmouth
            snd = parselmouth.Sound(audio_slice, sampling_frequency=self.sample_rate)

            # Get pitch
            # Pitch floor/ceiling appropriate for human speech
            pitch = snd.to_pitch(pitch_floor=75.0, pitch_ceiling=600.0)
            # Use Praat call to get mean pitch
            mean_f0 = parselmouth.praat.call(pitch, "Get mean", 0, 0, "Hertz")

            # Get jitter and shimmer
            # PointProcess is needed for jitter/shimmer calculations
            point_process = parselmouth.praat.call(pitch, "To PointProcess")
            jitter_local = parselmouth.praat.call(
                point_process, "Get jitter (local)",
                0.0, 0.0, 0.0001, 0.02, 1.3
            )
            shimmer_local = parselmouth.praat.call(
                [snd, point_process], "Get shimmer (local)",
                0.0, 0.0, 0.0001, 0.02, 1.3, 1.6
            )

            # Get HNR (Harmonics-to-Noise Ratio)
            harmonicity = snd.to_harmonicity(time_step=0.01, minimum_pitch=75.0)
            # Use Praat call to get mean HNR
            hnr = parselmouth.praat.call(harmonicity, "Get mean", 0, 0)

            return {
                "pitch_mean_f0": mean_f0 if not np.isnan(mean_f0) else None,
                "jitter_local": jitter_local if not np.isnan(jitter_local) else None,
                "shimmer_local": shimmer_local if not np.isnan(shimmer_local) else None,
                "hnr_mean": hnr if not np.isnan(hnr) else None
            }

        except Exception as e:
            # Praat errors are common on very short or unusual audio
            # We must not crash the whole pipeline
            print(f"⚠ Could not process acoustic features: {e}")
            return None

