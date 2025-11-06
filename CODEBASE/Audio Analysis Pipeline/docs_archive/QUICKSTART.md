# Quick Start Guide
## Clinical Audio Analysis Pipeline - Phase 1

---

## ⚡ Quick Setup (5 Minutes)

### 1. Install Dependencies
```bash
cd "C:\Users\elija\OneDrive\Desktop\MAYO REPO\Synapse\CODEBASE\Clinical Audio Analysis Pipeline (nov 5)"
pip install -r requirements.txt
```

### 2. Get Hugging Face Token
1. Go to: https://huggingface.co/pyannote/speaker-diarization-3.1
2. Click "Agree and access repository"
3. Go to: https://huggingface.co/settings/tokens
4. Click "New token" → Give it a name → Select "read" → Create

### 3. Set Environment Variable
**PowerShell:**
```powershell
$env:HF_TOKEN="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

**Command Prompt:**
```cmd
set HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 4. Run Your First Analysis
```bash
# Place an audio file in data/input/
python main.py -i ./data/input/your_audio.mp3
```

**Done!** Check `data/output/your_audio.json` for results.

---

## 📋 Command Reference

### Basic Usage
```bash
python main.py -i <audio_file>
```

### All Options
```bash
python main.py -i <input_file> -o <output_dir> --asr <model> --speakers <num>
```

**Parameters:**
- `-i, --input`: Path to audio file (REQUIRED)
- `-o, --output_dir`: Output directory (default: ./data/output/)
- `--asr`: ASR model: "base.en" or "medium.en" (default: base.en)
- `--speakers`: Number of speakers (default: 2)

### Examples
```bash
# Basic
python main.py -i ./data/input/conversation.mp3

# With better transcription
python main.py -i ./data/input/conversation.mp3 --asr medium.en

# 3-person conversation
python main.py -i ./data/input/meeting.wav --speakers 3

# Custom output location
python main.py -i ./audio.m4a -o ./results/
```

---

## 📊 What You Get

**Input:** Audio file (any format: .mp3, .wav, .m4a, etc.)

**Output:** JSON file with:
- 👥 Who spoke (speaker labels)
- ⏱️ When they spoke (timestamps)
- 💬 What they said (transcription)
- 😊 How they said it - subjective (emotion: happy, sad, angry, neutral)
- 🎵 How they said it - objective (pitch, jitter, shimmer, HNR)

---

## 🔧 Troubleshooting

### "HF_TOKEN not set"
→ Follow Step 3 above to set your Hugging Face token

### "File not found"
→ Check file path is correct and file exists

### "CUDA out of memory"
→ Pipeline will auto-switch to CPU (slower but works)

### Slow processing
→ Use `--asr base.en` (faster) instead of medium.en

### ffmpeg errors
→ Install ffmpeg:
- Windows: `choco install ffmpeg`
- Or download from: https://ffmpeg.org/download.html

---

## 🎯 Quick Phase 2 Workflow

Want a specialized clinical emotion model?

```bash
# 1. Process multiple audio files
python main.py -i ./data/input/file1.mp3
python main.py -i ./data/input/file2.mp3
python main.py -i ./data/input/file3.mp3

# 2. Create dataset for labeling
python scripts/prepare_dataset.py

# 3. Open data/dataset_for_labeling.csv
#    Fill in the "clinical_label" column
#    Save as data/dataset_human_labeled.csv

# 4. Train specialized model
python scripts/train_emotion_model.py

# 5. Use specialized model
python main_phase2.py -i ./data/input/new_file.mp3
```

---

## 📁 File Organization

**Where to put things:**
- 📥 Input audio → `data/input/`
- 📤 Output JSON → `data/output/`
- 🏷️ Labeled datasets → `data/`
- 🤖 Trained models → `models/`

**Don't touch:**
- `pipeline/` - Core code
- `scripts/` - Training scripts
- `main.py` - Entry point

---

## ⚙️ System Requirements

**Minimum:**
- Python 3.8+
- 8 GB RAM
- 5 GB disk space

**Recommended:**
- Python 3.9+
- 16 GB RAM
- NVIDIA GPU with 6+ GB VRAM (for CUDA acceleration)
- 10 GB disk space

---

## 🆘 Getting Help

1. Check `README.md` for detailed documentation
2. Check `PHASE1_SUMMARY.md` for complete implementation details
3. Review error messages - they contain helpful instructions
4. Verify all dependencies are installed: `pip list`

---

## ✅ Success Checklist

Before processing important files, verify:
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] HF_TOKEN environment variable set
- [ ] Test file processed successfully
- [ ] JSON output looks correct
- [ ] All 4 services working (diarization, ASR, emotion, acoustics)

---

## 🚀 Performance Tips

**Faster Processing:**
- Use GPU/CUDA if available
- Use `--asr base.en` (instead of medium.en)
- Process shorter clips (< 5 minutes)

**Better Accuracy:**
- Use `--asr medium.en`
- Ensure clean audio (minimal background noise)
- Correct number of speakers with `--speakers`

**For Large Batches:**
- Create a simple loop in Python or shell script
- Process overnight if you have many files
- Monitor disk space (JSON outputs accumulate)

---

**Quick Start Complete!** 🎉

For detailed information, see:
- `README.md` - Full documentation
- `PHASE1_SUMMARY.md` - Development details

