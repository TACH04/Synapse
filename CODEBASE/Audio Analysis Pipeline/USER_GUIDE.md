# Clinical Audio Analysis Pipeline - User Guide

**Version:** 2.0 (Triple Ensemble with Improvements)  
**Last Updated:** November 6, 2025  
**Status:** Production Ready ✅

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Basic Usage](#basic-usage)
4. [Advanced Usage](#advanced-usage)
5. [Understanding Output](#understanding-output)
6. [Troubleshooting](#troubleshooting)
7. [Configuration](#configuration)

---

## ⚡ Quick Start

### Prerequisites
- Python 3.8+
- 8GB+ RAM
- Optional: NVIDIA GPU with CUDA support

### 5-Minute Setup

```powershell
# 1. Navigate to project directory
cd "C:\Users\elija\OneDrive\Desktop\MAYO REPO\Synapse\CODEBASE\Clinical Audio Analysis Pipeline (nov 5)"

# 2. Activate virtual environment (if using one)
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Get Hugging Face token (one-time setup)
# Visit: https://huggingface.co/pyannote/speaker-diarization-3.1
# Click "Agree and access repository"
# Visit: https://huggingface.co/settings/tokens
# Create a new "read" token

# 5. Set your token (PowerShell)
$env:HF_TOKEN="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# 6. Run analysis on sample audio
python main.py -i "data\input\test_audio2.mp3"
```

**Done!** Check `data/output/test_audio2.json` for results.

---

## 📦 Installation

### Step 1: System Requirements

**Minimum:**
- Windows 10/11, macOS, or Linux
- Python 3.8 or higher
- 8GB RAM
- 5GB disk space (for models)

**Recommended:**
- NVIDIA GPU with 4GB+ VRAM (for faster processing)
- 16GB RAM
- SSD storage

### Step 2: Install Dependencies

The system requires several ML libraries. Install them using:

```bash
pip install -r requirements.txt
```

**Key Dependencies:**
- `pyannote.audio` - Speaker diarization
- `faster-whisper` - Speech-to-text
- `transformers` - Emotion models
- `torch` & `torchaudio` - ML framework
- `praat-parselmouth` - Acoustic analysis

### Step 3: GPU Setup (Optional but Recommended)

If you have an NVIDIA GPU:

```bash
# Check CUDA version
nvidia-smi

# Install PyTorch with CUDA support (example for CUDA 11.8)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Step 4: Hugging Face Authentication

The speaker diarization model requires authentication:

1. **Accept model license:**
   - Go to https://huggingface.co/pyannote/speaker-diarization-3.1
   - Click "Agree and access repository"

2. **Create access token:**
   - Go to https://huggingface.co/settings/tokens
   - Click "New token"
   - Name it (e.g., "audio-pipeline")
   - Select "read" permission
   - Click "Generate"

3. **Set environment variable:**

   **PowerShell:**
   ```powershell
   $env:HF_TOKEN="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
   ```

   **Command Prompt:**
   ```cmd
   set HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

   **Linux/Mac:**
   ```bash
   export HF_TOKEN="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
   ```

   **Permanent (Windows):**
   - Search "Environment Variables" in Windows
   - Add new System Variable: `HF_TOKEN` with your token

### Step 5: Download Models (Optional but Recommended)

Pre-download models to avoid delays during first run:

```bash
python download_models.py
```

This downloads ~1.5GB of models (one-time, takes 5-10 minutes).

---

## 🎯 Basic Usage

### Command Structure

```bash
python main.py -i <input_file> [options]
```

### Essential Options

| Option | Description | Default |
|--------|-------------|---------|
| `-i, --input` | Input audio file (required) | - |
| `-o, --output` | Output JSON file | `data/output/<filename>.json` |
| `--speakers` | Number of speakers | 2 |
| `--asr` | Whisper model size | `base.en` |

### Examples

**1. Basic analysis:**
```bash
python main.py -i "conversation.mp3"
```

**2. Specify output location:**
```bash
python main.py -i "interview.wav" -o "results/interview_analysis.json"
```

**3. Three speakers with better accuracy:**
```bash
python main.py -i "meeting.m4a" --speakers 3 --asr medium.en
```

**4. Fast processing (small model):**
```bash
python main.py -i "short_call.mp3" --asr tiny.en
```

### Supported Audio Formats

- MP3 (`.mp3`)
- WAV (`.wav`)
- M4A (`.m4a`)
- FLAC (`.flac`)
- OGG (`.ogg`)
- Any format supported by `torchaudio`

### Where to Put Files

**Input:** Place audio files in `data/input/` directory

**Output:** Results are saved to `data/output/` directory

---

## 🔬 Advanced Usage

### ASR Model Selection

The `--asr` option controls transcription accuracy vs. speed:

| Model | Speed | Accuracy | RAM | Use Case |
|-------|-------|----------|-----|----------|
| `tiny.en` | Fastest | Lower | 1GB | Quick testing |
| `base.en` | Fast | Good | 1GB | **Default** |
| `small.en` | Medium | Better | 2GB | Better transcription |
| `medium.en` | Slow | Best | 5GB | Maximum accuracy |

**Recommendation:** Start with `base.en`, upgrade to `medium.en` if transcription quality is critical.

### Multi-Speaker Scenarios

```bash
# Clinical consultation (2 speakers - default)
python main.py -i "consultation.mp3"

# Group therapy (3-4 speakers)
python main.py -i "group_session.mp3" --speakers 4

# Family session (5+ speakers)
python main.py -i "family_session.mp3" --speakers 5
```

### Processing Multiple Files

**Batch script (PowerShell):**
```powershell
$files = Get-ChildItem "data\input\*.mp3"
foreach ($file in $files) {
    python main.py -i $file.FullName
    Write-Host "Processed: $($file.Name)"
}
```

**Batch script (Bash):**
```bash
for file in data/input/*.mp3; do
    python main.py -i "$file"
    echo "Processed: $(basename $file)"
done
```

---

## 📊 Understanding Output

### JSON Structure

The output JSON contains:

```json
{
    "file": "conversation.mp3",
    "segments": [
        {
            "segment_id": 0,
            "speaker": "SPEAKER_00",
            "start_time": 22.171,
            "end_time": 25.512,
            "duration": 3.341,
            "transcript": "Joe, have a seat. Finally.",
            "predicted_emotion": { ... },
            "acoustic_features": { ... }
        }
    ]
}
```

### Emotion Analysis

Each segment includes detailed emotion predictions:

```json
"predicted_emotion": {
    "label": "ang",              // Final prediction (neu/hap/ang/sad)
    "score": 0.85,               // Confidence score (0-1)
    "confidence": "high",        // very_high/high/medium/low
    
    "hubert_emotion": "ang",     // Audio model 1 (prosody)
    "hubert_score": 0.90,
    
    "wav2vec2_emotion": "angry", // Audio model 2 (phonetics)
    "wav2vec2_score": 0.75,
    
    "text_emotion": "anger",     // Text model (semantics)
    "text_score": 0.94,
    
    "agreement": "text_veto",    // How models agreed
    "sarcasm_flag": false,       // Text-audio disagreement
    "mixed_emotion_flag": false, // Complex emotion detected
    "method": "triple_ensemble"
}
```

### Agreement Types

| Type | Meaning |
|------|---------|
| `full` | All models agree - very reliable |
| `audio_consensus` | Both audio models agree |
| `text_veto` | Text model >0.90 confidence, overrode audio |
| `hubert_veto` | HuBERT >0.90 confidence, overrode others |
| `text_priority` | Text confident + acoustics support it |
| `partial` | Mixed predictions, weighted vote used |

### Emotion Labels

| Code | Emotion | Description |
|------|---------|-------------|
| `neu` | Neutral | Calm, matter-of-fact tone |
| `hap` | Happy | Positive, upbeat, cheerful |
| `ang` | Anger | Frustrated, irritated, hostile |
| `sad` | Sadness | Upset, worried, distressed |

### Acoustic Features

Objective voice measurements:

```json
"acoustic_features": {
    "pitch_mean_f0": 129.26,     // Average pitch (Hz)
    "jitter_local": 0.018,       // Voice stability
    "shimmer_local": 0.171,      // Amplitude variation
    "hnr_mean": 5.00             // Harmonics-to-noise ratio
}
```

**Interpreting:**
- **High pitch** (>150 Hz) + **high jitter** (>0.02) → Stress/anger
- **Low pitch** (<110 Hz) + **low HNR** (<8) → Sadness/fatigue
- **Moderate values** + **high HNR** (>12) → Calm/neutral

---

## 🔧 Troubleshooting

### Common Issues

#### 1. "No module named 'pyannote'"
**Solution:** Install dependencies
```bash
pip install -r requirements.txt
```

#### 2. "HTTP 401: Unauthorized" (Diarization)
**Solution:** Set Hugging Face token
```powershell
$env:HF_TOKEN="your_token_here"
```

#### 3. "Library cublas64_12.dll not found"
**Solution:** This is a CUDA mismatch. The system will automatically fall back to CPU.
To use GPU, ensure CUDA version matches PyTorch:
```bash
nvidia-smi  # Check CUDA version
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### 4. "Segment took too long" / Freezing
**Solution:** Pre-download models first
```bash
python download_models.py
```

#### 5. Out of Memory Error
**Solutions:**
- Use smaller ASR model: `--asr tiny.en`
- Process shorter audio files
- Close other applications
- If on GPU, fall back to CPU (automatic)

#### 6. Poor Transcription Quality
**Solutions:**
- Use larger ASR model: `--asr medium.en`
- Ensure audio is clear (low background noise)
- Check audio sample rate (16kHz is best)

#### 7. Inaccurate Speaker Labels
**Solution:** Adjust speaker count
```bash
# If 3 people but set to 2:
python main.py -i "audio.mp3" --speakers 3
```

### Performance Tips

**For Faster Processing:**
1. Use GPU if available
2. Use `--asr tiny.en` or `base.en`
3. Pre-download models with `download_models.py`

**For Better Accuracy:**
1. Use `--asr medium.en`
2. Ensure clean audio input
3. Set correct number of speakers

---

## ⚙️ Configuration

### Adjusting Emotion Detection

You can fine-tune emotion detection parameters by editing `pipeline/services/emotion_service.py`:

**Text Model Influence:**
```python
# Line ~350
if text_score > 0.85:  # Lower to 0.80 for more text influence
```

**Segment Merging:**
```python
# In analysis_pipeline.py, line ~170
max_gap=1.0      # Gap between segments to merge (seconds)
min_duration=0.3  # Minimum segment duration (seconds)
max_duration=30.0 # Maximum merged segment duration
```

**Acoustic Validation Boost:**
```python
# emotion_service.py, line ~410
return score * 1.15  # Increase to 1.20 for stronger acoustic influence
```

### Changing Emotion Mode

Edit `analysis_pipeline.py` line ~80:

```python
self.emotion_service = EmotionService(
    mode='triple_ensemble',  # Options: 'dual_audio' or 'triple_ensemble'
    # ...
)
```

- **`triple_ensemble`**: Uses audio + text (most accurate, slower)
- **`dual_audio`**: Uses only audio models (faster, good for sarcasm)

---

## 📞 Support

### Documentation
- **Technical Details:** See `TECHNICAL_DOCUMENTATION.md`
- **Design History:** See `DESIGN_HISTORY.md`
- **Future Plans:** See `PHASE2_ROADMAP.md`

### System Status
- ✅ **Phase 1 Complete** - General-purpose models working
- ✅ **Triple Ensemble** - 3 emotion models implemented
- ✅ **Improvements** - 9 major accuracy enhancements applied
- 🔄 **Phase 2** - Fine-tuned clinical models (planned)

---

**Last Updated:** November 6, 2025  
**Version:** 2.0 with Triple Ensemble and Improvements

