"""
Download Models Script
Pre-downloads all required models for the Triple Ensemble Emotion Recognition system.
Run this ONCE before running main.py for the first time.

This prevents the pipeline from freezing during model downloads.
"""

import sys
from tqdm import tqdm

print("=" * 60)
print("Triple Ensemble Model Downloader")
print("=" * 60)
print("\nThis will download ~1.5GB of models (one-time only)")
print("Internet connection required\n")

try:
    from transformers import AutoFeatureExtractor, AutoModelForAudioClassification, pipeline
    import torch
except ImportError as e:
    print(f"❌ Error: Missing required package: {e}")
    print("\nPlease install requirements first:")
    print("  pip install transformers torch tqdm")
    sys.exit(1)

# Check device
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Device: {device}")
if device == "cuda":
    print(f"GPU: {torch.cuda.get_device_name(0)}\n")
else:
    print("⚠️  No GPU detected - models will use CPU\n")

print("=" * 60)

# Model 1: HuBERT (Audio - Prosody)
print("\n[1/3] Downloading HuBERT (prosody analysis)...")
print("      Model: superb/hubert-base-superb-er (~300MB)")
try:
    hubert_extractor = AutoFeatureExtractor.from_pretrained("superb/hubert-base-superb-er")
    hubert_model = AutoModelForAudioClassification.from_pretrained("superb/hubert-base-superb-er")
    print("      ✅ HuBERT downloaded successfully!")
except Exception as e:
    print(f"      ❌ Error downloading HuBERT: {e}")
    sys.exit(1)

# Model 2: Wav2Vec2 (Audio - Phonetic)
print("\n[2/3] Downloading Wav2Vec2 (phonetic analysis)...")
print("      Model: ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition (~400MB)")
try:
    wav2vec2_extractor = AutoFeatureExtractor.from_pretrained(
        "ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition"
    )
    wav2vec2_model = AutoModelForAudioClassification.from_pretrained(
        "ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition"
    )
    print("      ✅ Wav2Vec2 downloaded successfully!")
except Exception as e:
    print(f"      ❌ Error downloading Wav2Vec2: {e}")
    sys.exit(1)

# Model 3: Text Model (Semantic)
print("\n[3/3] Downloading DistilRoBERTa (text/semantic analysis)...")
print("      Model: j-hartmann/emotion-english-distilroberta-base (~250MB)")
try:
    # Using pipeline to download model + tokenizer
    text_classifier = pipeline(
        "text-classification",
        model="j-hartmann/emotion-english-distilroberta-base",
        device=-1  # CPU for text model
    )
    print("      ✅ DistilRoBERTa downloaded successfully!")
except Exception as e:
    print(f"      ❌ Error downloading text model: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ ALL MODELS DOWNLOADED SUCCESSFULLY!")
print("=" * 60)

print("\nModel Information:")
print(f"  HuBERT labels: {hubert_model.config.id2label}")
print(f"  Wav2Vec2 labels: {wav2vec2_model.config.id2label}")
print(f"  Text labels: ['anger', 'disgust', 'fear', 'joy', 'neutral', 'sadness', 'surprise']")

print("\n" + "=" * 60)
print("Next Steps:")
print("=" * 60)
print("\nYou can now run the pipeline:")
print('  python main.py -i "data\\input\\test_audio2.mp3"')
print("\nThe pipeline will load instantly (models are cached)")
print("=" * 60)

