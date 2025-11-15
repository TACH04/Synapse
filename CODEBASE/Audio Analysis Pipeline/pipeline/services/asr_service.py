"""
ASR (Automatic Speech Recognition) Service
Encapsulates the faster-whisper model for transcription.
"""

import os
import warnings
warnings.filterwarnings('ignore')

import torch
import numpy as np
from faster_whisper import WhisperModel
from typing import Optional


class ASRService:
    """
    Encapsulates the faster-whisper model for speech-to-text transcription.

    This service answers the question: "What was said?"
    """

    def __init__(
        self,
        model_name: str = "base.en",
        device: Optional[str] = None,
        compute_type: Optional[str] = None
    ):
        """
        Initializes the ASR service.

        Args:
            model_name (str): The faster-whisper model to use (e.g., "base.en", "medium.en").
            device (Optional[str]): Preferred device ("cuda", "cpu", "auto"). Defaults to auto-detect.
            compute_type (Optional[str]): ctranslate2 compute type. If omitted we select sensible defaults
                                          per device. Float16 is automatically downgraded on CPU.
        """
        requested_device = (
            device
            or os.environ.get("ASR_DEVICE")
            or os.environ.get("WHISPER_DEVICE")
        )
        self.device = self._resolve_device(requested_device)

        requested_compute_type = (
            compute_type
            or os.environ.get("ASR_COMPUTE_TYPE")
            or os.environ.get("WHISPER_COMPUTE_TYPE")
        )
        self.compute_type = self._resolve_compute_type(self.device, requested_compute_type)

        self.model = WhisperModel(
            model_name,
            device=self.device,
            compute_type=self.compute_type
        )
        print(f"ASRService loaded model '{model_name}' on {self.device} with {self.compute_type}.")

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

    def _resolve_device(self, requested_device: Optional[str]) -> str:
        """
        Decide which device to use across platforms with graceful fallbacks.
        """
        normalized = (requested_device or "auto").lower()

        if normalized == "cpu":
            print("ASRService: Using CPU (requested).")
            return "cpu"

        if normalized in ("cuda", "gpu"):
            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                print(f"ASRService: Using GPU (CUDA) - {gpu_name}")
                return "cuda"
            print("ASRService: CUDA requested but not available. Falling back to CPU.")
            return "cpu"

        if normalized in ("mps", "metal"):
            print("ASRService: MPS/Metal requested but faster-whisper only supports CPU/CUDA. Falling back to CPU.")
            return "cpu"

        # Auto-detect best supported option
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            print(f"ASRService: Auto-detected GPU (CUDA) - {gpu_name}")
            return "cuda"

        print("ASRService: No compatible GPU found, using CPU.")
        return "cpu"

    def _resolve_compute_type(self, device: str, requested_compute: Optional[str]) -> str:
        """
        Pick a compute_type compatible with the chosen device.
        """
        normalized = (requested_compute or "").lower()

        if device == "cpu" and normalized == "float16":
            print("ASRService: float16 not supported on CPU; switching to float32.")
            return "float32"

        if normalized:
            print(f"ASRService: Using compute type '{normalized}'.")
            return normalized

        default = "float16" if device == "cuda" else "float32"
        print(f"ASRService: Using default compute type '{default}' for device '{device}'.")
        return default

