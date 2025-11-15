"""
Diarization Service
Encapsulates the pyannote.audio pipeline for speaker diarization.
"""

import warnings
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

# Suppress deprecation warnings for better performance
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

# Suppress torchaudio backend warnings
os.environ['PYTHONWARNINGS'] = 'ignore::UserWarning'

import torch
import torchaudio
from pyannote.audio import Pipeline

try:
    from huggingface_hub import HfFolder
except ImportError:
    HfFolder = None


class DiarizationService:
    """
    Encapsulates the pyannote.audio pipeline for speaker diarization.
    Loads the model once and provides an interface to process audio files.

    This service answers the question: "Who spoke, and when?"
    """

    def __init__(self, model_name: str = "pyannote/speaker-diarization-3.1", auth_token: Optional[str] = None):
        """
        Initializes the service by loading the diarization pipeline.

        Args:
            model_name (str): The name of the pyannote model to load
            auth_token (Optional[str]): Hugging Face auth token. If omitted, we look for
                                        HF_TOKEN / HUGGINGFACEHUB_API_TOKEN env vars or
                                        cached CLI credentials.

        Raises:
            ValueError: If no auth token can be found
            RuntimeError: If the model fails to load
        """
        hf_token, token_source = self._resolve_hf_token(auth_token)
        if hf_token is None:
            raise ValueError(
                "Hugging Face auth token is required for pyannote/speaker-diarization-3.1. "
                "Provide it via the 'auth_token' argument, the HF_TOKEN or HUGGINGFACEHUB_API_TOKEN "
                "environment variables, or run 'huggingface-cli login'."
            )

        self.hf_token = hf_token
        self.hf_token_source = token_source
        os.environ.setdefault("HF_TOKEN", self.hf_token)
        print(f"DiarizationService: Using Hugging Face token from {self.hf_token_source}.")

        # Detect device: CUDA (NVIDIA) > MPS (Apple Silicon) > CPU
        if torch.cuda.is_available():
            device_str = "cuda"
            gpu_name = torch.cuda.get_device_name(0)
            print(f"DiarizationService: Using GPU (CUDA) - {gpu_name}")
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            device_str = "mps"
            print(f"DiarizationService: Using GPU (Apple Silicon MPS)")
        else:
            device_str = "cpu"
            print(f"DiarizationService: Using CPU (GPU not available)")
        
        self.device = torch.device(device_str)

        try:
            self.pipeline = Pipeline.from_pretrained(
                model_name,
                use_auth_token=self.hf_token
            ).to(self.device)
            print(f"DiarizationService loaded on {device_str}.")
        except Exception as e:
            print(f"Error loading pyannote pipeline: {e}")
            raise

    def process(self, audio_file_path: str, num_speakers: int = 2) -> List[Dict[str, Any]]:
        """
        Processes a single audio file to identify speaker segments.

        Args:
            audio_file_path (str): The path to the audio file
            num_speakers (int): The number of speakers to detect
                              (default: 2, for clinical practitioner-patient conversations)

        Returns:
            List[Dict[str, Any]]: A list of segment dictionaries, each containing:
                - speaker (str): Speaker label (e.g., "SPEAKER_00", "SPEAKER_01")
                - start_time (float): Segment start time in seconds
                - end_time (float): Segment end time in seconds

        Note:
            Returns an empty list if diarization fails.
        """
        try:
            # Load audio with torchaudio and prepare for pyannote.audio 4.0.1
            # This works around torchcodec issues on Windows
            waveform, sample_rate = torchaudio.load(audio_file_path)

            # Prepare audio dictionary format required by pyannote.audio 4.0.1
            audio = {
                'waveform': waveform,
                'sample_rate': sample_rate
            }

            # The pipeline is configured for a specific number of speakers
            diarization_output = self.pipeline(audio, num_speakers=num_speakers)

            segments = []
            # Handle different pyannote.audio API versions:
            # - Newer versions return DiarizeOutput with .speaker_diarization attribute
            # - Older versions or certain configurations return Annotation directly
            if hasattr(diarization_output, 'speaker_diarization'):
                # pyannote.audio 4.0.1+ returns a DiarizeOutput object
                diarization = diarization_output.speaker_diarization
            else:
                # Direct Annotation object (older API or different configuration)
                diarization = diarization_output

            # Now iterate through the annotation using itertracks
            for segment, _, label in diarization.itertracks(yield_label=True):
                seg_dict = {
                    "speaker": label,  # e.g., "SPEAKER_00", "SPEAKER_01"
                    "start_time": segment.start,
                    "end_time": segment.end
                }
                segments.append(seg_dict)

            return segments
        except Exception as e:
            print(f"Error during diarization processing: {e}")
            return []

    def _resolve_hf_token(self, auth_token: Optional[str]) -> Tuple[Optional[str], str]:
        """
        Resolve the Hugging Face token from multiple sources for robustness.
        Returns (token, source_description).
        """
        if auth_token:
            return auth_token.strip(), "constructor argument"

        env_vars = ["HF_TOKEN", "HUGGINGFACEHUB_API_TOKEN", "HUGGINGFACE_TOKEN"]
        for env_var in env_vars:
            value = os.environ.get(env_var)
            if value:
                return value.strip(), f"environment variable {env_var}"

        if HfFolder:
            stored = HfFolder.get_token()
            if stored:
                return stored.strip(), "huggingface_hub cache"

        token_path = Path.home() / ".huggingface" / "token"
        if token_path.exists():
            try:
                return token_path.read_text().strip(), str(token_path)
            except OSError:
                pass

        return None, ""

