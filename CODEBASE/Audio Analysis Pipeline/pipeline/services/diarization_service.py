"""
Diarization Service
Encapsulates the pyannote.audio pipeline for speaker diarization.
"""

import warnings
import os

# Suppress deprecation warnings for better performance
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

# Suppress torchaudio backend warnings
os.environ['PYTHONWARNINGS'] = 'ignore::UserWarning'

import torch
import torchaudio
from pyannote.audio import Pipeline
from typing import List, Dict, Any


class DiarizationService:
    """
    Encapsulates the pyannote.audio pipeline for speaker diarization.
    Loads the model once and provides an interface to process audio files.

    This service answers the question: "Who spoke, and when?"
    """

    def __init__(self, model_name: str = "pyannote/speaker-diarization-3.1", auth_token: str = None):
        """
        Initializes the service by loading the diarization pipeline.

        Args:
            model_name (str): The name of the pyannote model to load
            auth_token (str): The Hugging Face auth token.
                            Required for gated models like 3.1.

        Raises:
            ValueError: If auth_token is not provided
            RuntimeError: If the model fails to load
        """
        if auth_token is None:
            raise ValueError(
                "Hugging Face auth token is required for pyannote/speaker-diarization-3.1. "
                "Please provide it via HF_TOKEN env var or argument."
            )

        # Create torch.device object (pyannote requires torch.device, not string)
        device_str = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = torch.device(device_str)

        # Show GPU info if available
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            print(f"DiarizationService: Using GPU - {gpu_name}")
        else:
            print(f"DiarizationService: Using CPU (GPU not available)")

        try:
            self.pipeline = Pipeline.from_pretrained(
                model_name,
                token=auth_token
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
            # pyannote.audio 4.0.1 returns a DiarizeOutput object
            # The actual annotation is in the speaker_diarization attribute
            diarization = diarization_output.speaker_diarization

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

