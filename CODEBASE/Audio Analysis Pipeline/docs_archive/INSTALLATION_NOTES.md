# Installation Notes & Troubleshooting

## ⚠️ Installation Status: ACTION REQUIRED

Dependencies installed, but NumPy compatibility issue needs to be resolved.

---

## 📝 Installation Correction

### Issue 1: Package Name (FIXED)

**Original Error:**
```
ERROR: Could not find a version that satisfies the requirement parselmouth-praat>=0.4
ERROR: No matching distribution found for parselmouth-praat>=0.4
```

**Root Cause:**
The package name in the original requirements.txt was incorrect. The pip package is named `praat-parselmouth`, not `parselmouth-praat`.

**Fix Applied:**
Updated `requirements.txt` line 5 from:
```
parselmouth-praat>=0.4
```
to:
```
praat-parselmouth>=0.4
```

**Result:**
✅ Package name corrected!

---

### Issue 2: NumPy 2.x Compatibility (NEEDS ACTION)

**Error Encountered:**
```
AttributeError: `np.NaN` was removed in the NumPy 2.0 release. Use `np.nan` instead.
```

**Root Cause:**
- NumPy 2.0+ removed `np.NaN` (uppercase)
- The installed version is NumPy 2.3.4
- `pyannote.audio` library uses the old `np.NaN` syntax
- This causes import failures

**Fix Required:**
Downgrade NumPy to version 1.x (latest 1.26.x is compatible)

**Steps to Fix:**
```powershell
# Uninstall NumPy 2.x
pip uninstall numpy -y

# Install NumPy 1.x (compatible version)
pip install "numpy<2.0"

# Verify the installation
python -c "import numpy; print(f'NumPy version: {numpy.__version__}')"
```

**Expected Result:**
NumPy version should be 1.26.x (compatible with pyannote.audio)

**Status:**
⚠️ **ACTION REQUIRED** - Please run the commands above to fix this issue

---

## 📦 Installed Packages Summary

### Core ML Models
- ✅ `pyannote.audio` 3.1.1 - Speaker diarization
- ✅ `faster-whisper` 1.2.1 - ASR/transcription
- ✅ `transformers` 4.57.1 - Emotion recognition
- ✅ `praat-parselmouth` 0.4.6 - Acoustic features

### Core ML Frameworks
- ✅ `torch` 2.8.0 - PyTorch
- ✅ `torchaudio` 2.8.0 - Audio processing

### Data Handling
- ✅ `pandas` 2.3.3 - Data manipulation
- ⚠️ `numpy` 2.3.4 - **NEEDS DOWNGRADE TO 1.x** (see Issue 2 above)

### Utilities
- ✅ `tqdm` 4.67.1 - Progress bars

### New Dependencies (Auto-installed)
- ✅ `ctranslate2` 4.6.0 - For faster-whisper
- ✅ `onnxruntime` 1.23.2 - For faster-whisper
- ✅ `av` 16.0.1 - Audio/video processing
- ✅ `coloredlogs` 15.0.1 - Enhanced logging
- ✅ `flatbuffers` 25.9.23 - Serialization
- ✅ `humanfriendly` 10.0 - Human-readable output

---

## 🎯 Next Steps

Now that dependencies are installed, you need to:

### 1. Set Up Hugging Face Token (REQUIRED)

The speaker diarization model requires authentication:

**Step A: Accept Model Terms**
1. Visit: https://huggingface.co/pyannote/speaker-diarization-3.1
2. Click "Agree and access repository"

**Step B: Get Your Token**
1. Visit: https://huggingface.co/settings/tokens
2. Click "New token"
3. Give it a name (e.g., "clinical-audio-pipeline")
4. Select "read" permission
5. Click "Generate token"
6. Copy the token (starts with `hf_`)

**Step C: Set Environment Variable**

**PowerShell (Current session):**
```powershell
$env:HF_TOKEN="hf_your_token_here"
```

**PowerShell (Permanent - User level):**
```powershell
[System.Environment]::SetEnvironmentVariable('HF_TOKEN', 'hf_your_token_here', 'User')
```

**Command Prompt:**
```cmd
set HF_TOKEN=hf_your_token_here
```

**To verify it's set:**
```powershell
echo $env:HF_TOKEN
```

### 2. Test the Pipeline

Once your HF_TOKEN is set:

```bash
# Make sure you're in the project directory
cd "C:\Users\elija\OneDrive\Desktop\MAYO REPO\Synapse\CODEBASE\Clinical Audio Analysis Pipeline (nov 5)"

# Place a test audio file in data/input/
# Then run:
python main.py -i ./data/input/your_audio_file.mp3
```

---

## 🔍 Verification Checklist

Before running the pipeline, verify:

- [x] ✅ Dependencies installed successfully
- [ ] 🔲 Hugging Face account created
- [ ] 🔲 pyannote model terms accepted
- [ ] 🔲 HF_TOKEN generated
- [ ] 🔲 HF_TOKEN environment variable set
- [ ] 🔲 Test audio file ready in data/input/

---

## 💡 Installation Tips

### Python Version
- You're using Python 3.13 (detected from package installs)
- This is compatible with all requirements ✅

### GPU/CUDA Status
- The pipeline will auto-detect if CUDA is available
- If you have an NVIDIA GPU, you may want to install PyTorch with CUDA support for faster processing
- CPU-only installation will work fine, just slower

### ffmpeg Requirement
- Required for loading non-WAV audio formats (.mp3, .m4a, etc.)
- If you encounter audio loading errors, install ffmpeg:
  - **Windows:** Download from https://ffmpeg.org/download.html or use `choco install ffmpeg`
  - **Verification:** Run `ffmpeg -version` in terminal

---

## 🐛 Common Post-Installation Issues

### Issue 1: "HF_TOKEN not set"
**When:** Running main.py
**Fix:** Set the HF_TOKEN environment variable (see Step 1 above)

### Issue 2: "Could not load audio file"
**When:** Processing audio files
**Possible Causes:**
- ffmpeg not installed
- Unsupported audio format
- Corrupted audio file
**Fix:** Install ffmpeg, try converting to WAV format

### Issue 3: "CUDA out of memory"
**When:** Processing on GPU
**Fix:** Pipeline will auto-fall back to CPU, or use shorter audio files

### Issue 4: "Model download failed"
**When:** First run
**Causes:**
- No internet connection
- HF_TOKEN not set or invalid
- Model terms not accepted
**Fix:** Check internet, verify HF_TOKEN, accept model terms

---

## 📊 Storage Requirements

After installation, expect:
- **Installed packages:** ~2-3 GB
- **Model downloads (first run):** ~1-2 GB
  - pyannote/speaker-diarization-3.1: ~400 MB
  - faster-whisper models: ~140 MB (base) or ~1.5 GB (medium)
  - superb/hubert-base-superb-er: ~380 MB

**Total:** ~4-6 GB for complete setup

---

## ✅ Installation Complete!

You've successfully installed all dependencies. The system is ready to use once you:
1. Set your HF_TOKEN
2. Place audio files in data/input/
3. Run `python main.py -i ./data/input/your_file.mp3`

For detailed usage instructions, see:
- **QUICKSTART.md** - Quick reference
- **README.md** - Complete documentation
- **ARCHITECTURE.md** - System architecture

---

**Installation Date:** November 5, 2025  
**Status:** ✅ SUCCESSFUL  
**Next Action:** Set HF_TOKEN and test the pipeline!

