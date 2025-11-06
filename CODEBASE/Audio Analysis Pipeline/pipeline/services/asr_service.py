"""
ASR (Automatic Speech Recognition) Service
Encapsulates the faster-whisper model for transcription.
"""

import warnings
warnings.filterwarnings('ignore')

import torch
import numpy as np
from faster_whisper import WhisperModel
from typing import List, Dict, Any


class ASRService:
    """
    Encapsulates the faster-whisper model for speech-to-text transcription.

    This service answers the question: "What was said?"
    """

    def __init__(self, model_name: str = "base.en", device: str = None, compute_type: str = "float16"):
        """
        Initializes the ASR service.

        Args:
            model_name (str): The faster-whisper model to use
                            (e.g., "base.en", "medium.en")
            device (str): "cuda" or "cpu". Auto-detects if None.
            compute_type (str): Optimization level (e.g., "float16", "int8", "float32")
                              Note: float16 is not supported on CPU
        """
        # WORKAROUND: Force CPU mode to avoid CUDA library mismatch
        # ctranslate2 4.6.0 requires CUDA 12.x but PyTorch uses CUDA 11.8
        # This causes "cublas64_12.dll not found" errors
        # CPU mode is slower but stable
        if device is None:
            # Force CPU to avoid CUDA library conflicts
            self.device = "cpu"
            print("ASRService: Using CPU (forced to avoid CUDA library mismatch)")
        else:
            self.device = device

        # float16 is not supported on CPU, so default to float32
        if self.device == "cpu" and compute_type == "float16":
            compute_type = "float32"
            print("ASRService: Using float32 on CPU (float16 not supported)")

        # Show GPU info if available (but we're using CPU)
        if self.device == "cuda" and torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            print(f"ASRService: Using GPU - {gpu_name}")
        else:
            print(f"ASRService: Using CPU")

        self.model = WhisperModel(model_name, device=self.device, compute_type=compute_type)
        print(f"ASRService loaded model '{model_name}' on {self.device} with {compute_type}.")

    def process(self, audio_slice: np.ndarray) -> str:
        """
        Transcribes a single audio slice (NumPy array).

        Args:
            audio_slice (np.ndarray): The 1D audio array (at 16kHz)

        Returns:
            str: The transcribed text

        Note:
            Returns an empty string if transcription fails or audio is empty.
        """
        if audio_slice.size == 0:
            return ""

        try:
            # faster-whisper expects a 16kHz float32 NumPy array
            if audio_slice.dtype != np.float32:
                audio_slice = audio_slice.astype(np.float32)

            # We are transcribing short, pre-segmented audio
            segments, _ = self.model.transcribe(audio_slice, language="en")

            # Concatenate segments for a single transcript
            transcript = " ".join(segment.text for segment in segments).strip()

            return transcript
        except Exception as e:
            print(f"⚠ ASR processing error: {e}")
            return ""

