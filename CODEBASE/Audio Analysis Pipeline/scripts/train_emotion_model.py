"""
Model Training Script for Phase 2
Fine-tunes a specialized clinical emotion recognition model.
"""

import pandas as pd
import torch
import torchaudio
import os
from torch.utils.data import Dataset
from transformers import AutoFeatureExtractor, AutoModelForAudioClassification, Trainer, TrainingArguments
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import numpy as np


# 1. Define the Custom Dataset
class ClinicalAudioDataset(Dataset):
    """
    Custom PyTorch Dataset for loading our pre-sliced audio segments.
    """
    def __init__(self, df, feature_extractor, label_encoder, sample_rate=16000):
        self.df = df
        self.feature_extractor = feature_extractor
        self.label_encoder = label_encoder
        self.sample_rate = sample_rate

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        audio_path = row["segment_audio_path"]
        label_str = row["clinical_label"]

        # Load the pre-sliced audio
        waveform, sr = torchaudio.load(audio_path)

        if sr != self.sample_rate:
            resampler = torchaudio.transforms.Resample(sr, self.sample_rate)
            waveform = resampler(waveform)

        if waveform.shape[0] > 1:
            waveform = torch.mean(waveform, dim=0)

        # Extract features
        inputs = self.feature_extractor(
            waveform.numpy().squeeze(),
            sampling_rate=self.sample_rate,
            return_tensors="pt",
            padding="max_length",  # Pad/truncate to a uniform length
            max_length=int(self.sample_rate * 5.0),  # e.g., 5 seconds
            truncation=True
        )

        # Get numerical label
        label_id = self.label_encoder.transform([label_str])[0]

        return {
            "input_values": inputs.input_values.squeeze(0),
            "labels": torch.tensor(label_id)
        }


# Define compute_metrics for evaluation
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    accuracy = np.mean(predictions == labels)
    return {"accuracy": accuracy}


def main_training():
    """
    Main training function for fine-tuning the clinical emotion model.
    """
    # --- Configuration ---
    BASE_MODEL = "superb/hubert-base-superb-er"
    COMPLETED_CSV_PATH = "./data/dataset_human_labeled.csv"  # ASSUMES human has filled this
    MODEL_OUTPUT_DIR = "./models/clinical_ser_model"

    print("=" * 60)
    print("Clinical Emotion Model Training (Phase 2)")
    print("=" * 60)

    # --- 1. Load and Prepare Data ---
    print("\n1. Loading data...")
    if not os.path.exists(COMPLETED_CSV_PATH):
        print(f"Error: {COMPLETED_CSV_PATH} not found.")
        print("\nPlease follow these steps:")
        print("1. Run scripts/prepare_dataset.py to create dataset_for_labeling.csv")
        print("2. Have a human expert label the 'clinical_label' column")
        print("3. Save the completed file as 'dataset_human_labeled.csv'")
        print("4. Re-run this script")
        return

    df = pd.read_csv(COMPLETED_CSV_PATH)
    df = df.dropna(subset=["clinical_label"])  # Remove rows human didn't label

    if len(df) == 0:
        print("Error: No labeled data found in CSV.")
        return

    print(f"   Loaded {len(df)} labeled samples")

    # --- 2. Encode Labels ---
    print("\n2. Encoding labels...")
    label_encoder = LabelEncoder()
    df["clinical_label_id"] = label_encoder.fit_transform(df["clinical_label"])

    new_num_labels = len(label_encoder.classes_)
    new_id2label = {i: label for i, label in enumerate(label_encoder.classes_)}
    new_label2id = {label: i for i, label in new_id2label.items()}

    print(f"   Found {new_num_labels} unique clinical labels:")
    for label in label_encoder.classes_:
        count = (df["clinical_label"] == label).sum()
        print(f"   - {label}: {count} samples")

    # --- 3. Load Base Model and Feature Extractor ---
    print(f"\n3. Loading base model: {BASE_MODEL}")
    feature_extractor = AutoFeatureExtractor.from_pretrained(BASE_MODEL)

    model = AutoModelForAudioClassification.from_pretrained(
        BASE_MODEL,
        num_labels=new_num_labels,  # This is the "re-initialization"
        id2label=new_id2label,
        label2id=new_label2id,
        ignore_mismatched_sizes=True  # Tell transformers to swap the head
    )
    print("   Model loaded with new classification head")

    # --- 4. Create Datasets ---
    print("\n4. Creating train/validation split...")
    train_df, val_df = train_test_split(
        df,
        test_size=0.2,
        random_state=42,
        stratify=df["clinical_label"]
    )

    train_dataset = ClinicalAudioDataset(train_df, feature_extractor, label_encoder)
    val_dataset = ClinicalAudioDataset(val_df, feature_extractor, label_encoder)

    print(f"   Training samples: {len(train_dataset)}")
    print(f"   Validation samples: {len(val_dataset)}")

    # --- 5. Set Up Trainer ---
    print("\n5. Configuring training parameters...")
    training_args = TrainingArguments(
        output_dir=f"{MODEL_OUTPUT_DIR}/checkpoints",
        evaluation_strategy="epoch",
        save_strategy="epoch",
        learning_rate=3e-5,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        num_train_epochs=3,  # Keep low for fine-tuning
        weight_decay=0.01,
        load_best_model_at_end=True,
        metric_for_best_model="accuracy",
        logging_dir=f"{MODEL_OUTPUT_DIR}/logs",
        logging_steps=10,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        tokenizer=feature_extractor,  # Pass the extractor for padding
        compute_metrics=compute_metrics,
    )

    # --- 6. Train ---
    print("\n6. Starting model fine-tuning...")
    print("=" * 60)
    trainer.train()

    # --- 7. Save Final Model ---
    print("\n" + "=" * 60)
    print("Training complete!")
    print("=" * 60)
    print(f"Saving model to {MODEL_OUTPUT_DIR}")
    trainer.save_model(MODEL_OUTPUT_DIR)
    feature_extractor.save_pretrained(MODEL_OUTPUT_DIR)

    print("\nYou can now use the specialized model with main_phase2.py!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main_training()

