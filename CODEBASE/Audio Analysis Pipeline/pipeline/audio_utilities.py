"""
Audio Utilities Module
Provides stateless helper functions for audio processing.
"""

import torchaudio
import torch
import numpy as np
from typing import Tuple


def load_and_resample_audio(file_path: str, target_sample_rate: int = 16000) -> Tuple[np.ndarray, int]:
    """
    Robustly loads any audio file and resamples to target sample rate.

    This function handles various audio formats (e.g., .wav, .mp3, .m4a) and normalizes
    them to the 16kHz mono format required by downstream ML models.

    Args:
        file_path (str): Path to the audio file to load
        target_sample_rate (int): Target sample rate in Hz (default: 16000)

    Returns:
        Tuple[np.ndarray, int]: A tuple containing:
            - audio: 1D NumPy array of the audio signal
            - target_sample_rate: The sample rate of the returned audio

    Raises:
        FileNotFoundError: If the audio file doesn't exist
        RuntimeError: If the audio file is corrupted or cannot be loaded
    """
    try:
        # Load the audio file
        waveform, original_sample_rate = torchaudio.load(file_path)

        # Convert to Mono: If stereo (shape [2, N]), average the channels
        if waveform.shape[0] > 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True)

        # Resample if necessary
        if original_sample_rate != target_sample_rate:
            resampler = torchaudio.transforms.Resample(
                orig_freq=original_sample_rate,
                new_freq=target_sample_rate
            )
            waveform = resampler(waveform)

        # Convert to 1D NumPy array
        audio_array = waveform.squeeze().numpy()

        return audio_array, target_sample_rate

    except FileNotFoundError:
        raise FileNotFoundError(f"Audio file not found: {file_path}")
    except Exception as e:
        raise RuntimeError(f"Error loading audio file {file_path}: {str(e)}")


def slice_audio(full_audio_array: np.ndarray, sample_rate: int,
                start_time_sec: float, end_time_sec: float) -> np.ndarray:
    """
    Extracts an audio segment from a full audio array based on time boundaries.

    This function performs precise slicing of audio arrays, converting time-based
    indices to sample-based indices. It includes boundary checking to prevent
    index errors.

    Args:
        full_audio_array (np.ndarray): The full 1D audio array
        sample_rate (int): The sample rate of the audio in Hz
        start_time_sec (float): Start time of the slice in seconds
        end_time_sec (float): End time of the slice in seconds

    Returns:
        np.ndarray: The sliced audio segment as a 1D NumPy array

    Note:
        - If start_time_sec < 0, it will be clamped to 0
        - If end_time_sec exceeds audio length, it will be clamped to the array length
        - Returns an empty array if the slice is invalid (start >= end)
    """
    # Calculate sample indices
    start_sample = int(start_time_sec * sample_rate)
    end_sample = int(end_time_sec * sample_rate)

    # Boundary checks
    start_sample = max(0, start_sample)
    end_sample = min(len(full_audio_array), end_sample)

    # Ensure valid slice
    if start_sample >= end_sample:
        return np.array([])

    # Return the slice
    return full_audio_array[start_sample:end_sample]

