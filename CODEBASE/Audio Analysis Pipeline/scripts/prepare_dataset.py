"""
Dataset Preparation Script for Phase 2
Aggregates Phase 1 JSON outputs into a CSV for human labeling
and extracts audio segments for efficient training.
"""

import os
import json
import glob
import pandas as pd
from tqdm import tqdm
from typing import List, Dict, Any
import sys

# Add project root to path to import pipeline modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pipeline import audio_utilities as au

# We will use torchaudio to save the wave files
import torchaudio
import torch


def create_labeling_dataset(
    json_input_dir: str,
    original_audio_dir: str,
    output_csv_path: str,
    output_segments_dir: str
):
    """
    Aggregates all Phase 1 JSON outputs into a single CSV for human labeling,
    and extracts all audio segments into a new directory.

    This optimization pre-slices all audio segments, so the training script
    doesn't need to repeatedly load and slice large audio files.

    Args:
        json_input_dir (str): Directory containing Phase 1 JSON outputs
        original_audio_dir (str): Directory containing original audio files
        output_csv_path (str): Path where the CSV will be saved
        output_segments_dir (str): Directory where audio segments will be saved
    """
    os.makedirs(output_segments_dir, exist_ok=True)

    all_segments_data = []

    json_files = glob.glob(os.path.join(json_input_dir, "*.json"))
    if not json_files:
        print(f"No JSON files found in {json_input_dir}")
        return

    print(f"Aggregating {len(json_files)} JSON files...")

    for json_path in tqdm(json_files, desc="Processing JSONs"):
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        original_audio_filename = data["file"]
        original_audio_path = os.path.join(original_audio_dir, original_audio_filename)

        if not os.path.exists(original_audio_path):
            print(f"Warning: Original audio {original_audio_path} not found. Skipping.")
            continue

        # Load the original audio *once* per file
        try:
            full_audio, sr = au.load_and_resample_audio(original_audio_path, target_sample_rate=16000)
        except Exception as e:
            print(f"Warning: Could not load {original_audio_path}. Skipping. Error: {e}")
            continue

        for segment in data["segments"]:
            # 1. Prepare Metadata
            segment_id = segment["segment_id"]
            start_time = segment["start_time"]
            end_time = segment["end_time"]

            # 2. Create the new audio slice file (The Optimization)
            segment_filename = f"{os.path.splitext(original_audio_filename)[0]}_seg{segment_id}.wav"
            segment_output_path = os.path.join(output_segments_dir, segment_filename)

            audio_slice_np = au.slice_audio(full_audio, sr, start_time, end_time)

            # Save the slice as a .wav
            # Convert numpy to torch tensor for saving
            audio_slice_tensor = torch.from_numpy(audio_slice_np).float().unsqueeze(0)
            torchaudio.save(segment_output_path, audio_slice_tensor, sample_rate=sr)

            # 3. Assemble data for CSV
            csv_row = {
                "segment_audio_path": segment_output_path,
                "original_file": original_audio_filename,
                "start_time": start_time,
                "end_time": end_time,
                "transcript": segment["transcript"],
                "phase1_emotion_guess": segment.get("predicted_emotion", {}).get("label") if segment.get("predicted_emotion") else None,
                "phase1_emotion_score": segment.get("predicted_emotion", {}).get("score") if segment.get("predicted_emotion") else None,
                "clinical_label": ""  # This is the column for the human expert
            }
            all_segments_data.append(csv_row)

    # Create and save the final CSV
    df = pd.DataFrame(all_segments_data)
    df.to_csv(output_csv_path, index=False, encoding='utf-8')
    print(f"\n{'='*60}")
    print(f"Dataset aggregation complete!")
    print(f"{'='*60}")
    print(f"CSV saved to: {output_csv_path}")
    print(f"Total segments: {len(df)}")
    print(f"Audio segments saved to: {output_segments_dir}")
    print(f"\nNext steps:")
    print(f"1. Open {output_csv_path}")
    print(f"2. Fill in the 'clinical_label' column with your expert labels")
    print(f"3. Save the file as 'dataset_human_labeled.csv'")
    print(f"4. Run train_emotion_model.py to fine-tune the model")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    # Example usage
    create_labeling_dataset(
        json_input_dir="./data/output/",
        original_audio_dir="./data/input/",
        output_csv_path="./data/dataset_for_labeling.csv",
        output_segments_dir="./data/segments/"
    )

