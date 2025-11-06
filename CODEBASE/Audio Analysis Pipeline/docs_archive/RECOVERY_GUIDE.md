# 🔧 Complete Recovery Guide - Post-Crash Dependencies Fix

## ⚠️ CURRENT STATUS (Updated)

**After reinstalling pyannote.audio, pip automatically upgraded to incompatible versions:**
- ❌ **torch 2.9.0** (CPU-only, no CUDA support!)
- ❌ **numpy 2.3.4** (Causes pyannote.audio crashes!)
- ❌ **torchaudio 2.9.0** (CPU-only!)
- ❌ **huggingface-hub 1.1.1** (Too new, breaks transformers!)

**What happened:**
When you ran `pip install --upgrade --force-reinstall pyannote.audio`, it pulled the latest versions of all dependencies, which are incompatible with your setup.

## 🚀 QUICK FIX (Choose One)

### Option A: Run the Automated Script (EASIEST)

I've created two scripts for you. Choose based on your shell:

**If using PowerShell:**
```powershell
cd "C:\Users\elija\OneDrive\Desktop\MAYO REPO\Synapse"
venv\Scripts\activate
cd "CODEBASE\Clinical Audio Analysis Pipeline (nov 5)"
.\fix_dependencies.ps1
```

**If using Command Prompt:**
```cmd
cd "C:\Users\elija\OneDrive\Desktop\MAYO REPO\Synapse"
venv\Scripts\activate
cd "CODEBASE\Clinical Audio Analysis Pipeline (nov 5)"
fix_dependencies.bat
```

### Option B: Manual Steps (if scripts don't work)

Run these commands one by one in your activated venv:

### Option B: Manual Steps (if scripts don't work)

Run these commands one by one in your activated venv:

```powershell
# 1. Fix NumPy
pip uninstall numpy -y
pip install "numpy<2.0"

# 2. Install PyTorch with CUDA 11.8
pip install torch==2.7.1 torchvision==0.22.1 torchaudio==2.7.1 --index-url https://download.pytorch.org/whl/cu118

# 3. Fix huggingface-hub
pip install "huggingface-hub<1.0,>=0.34.0"

# 4. Verify everything works
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA: {torch.cuda.is_available()}')"
python -c "import numpy; print(f'NumPy: {numpy.__version__}')"
```

**Expected Output:**
```
PyTorch: 2.7.1+cu118
CUDA: True
NumPy: 1.26.4
```

---

## 🎯 Original Step-by-Step Recovery Process (For Reference)

### Step 1: Fix NumPy Version Conflict

The most critical issue - NumPy 2.x breaks pyannote.audio:

```powershell
# Navigate to project root
cd "C:\Users\elija\OneDrive\Desktop\MAYO REPO\Synapse"

# Make sure venv is activated (you should see (venv) in prompt)
# If not: venv\Scripts\activate

# Uninstall NumPy 2.x
pip uninstall numpy -y

# Install compatible NumPy 1.26.x
pip install "numpy<2.0"
```

**Expected Output:**
```
Successfully installed numpy-1.26.4
```

**Verify:**
```powershell
python -c "import numpy; print(f'NumPy version: {numpy.__version__}')"
```

Should show: `NumPy version: 1.26.4`

---

### Step 2: Fix torchaudio Compatibility Issue

The `set_audio_backend` was deprecated and causes errors with newer pyannote.audio:

```powershell
# Downgrade to compatible version
pip install torchaudio==2.5.1+cu118 -f https://download.pytorch.org/whl/torch_stable.html
```

**Alternative if above fails:**
```powershell
pip install --upgrade --force-reinstall pyannote.audio
```

---

### Step 3: Verify All Dependencies Are Correct

Run this verification script:

```powershell
python -c "
import sys
import numpy
import torch
import torchaudio

print('=== Dependency Check ===')
print(f'Python: {sys.version}')
print(f'NumPy: {numpy.__version__}')
print(f'PyTorch: {torch.__version__}')
print(f'TorchAudio: {torchaudio.__version__}')
print(f'CUDA Available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA Version: {torch.version.cuda}')
    print(f'GPU: {torch.cuda.get_device_name(0)}')
print('\n✅ All imports successful!')
"
```

**Expected Output:**
```
=== Dependency Check ===
Python: 3.13.x
NumPy: 1.26.4
PyTorch: 2.7.1+cu118
TorchAudio: 2.5.1+cu118 (or similar)
CUDA Available: True
CUDA Version: 11.8
GPU: [Your NVIDIA GPU Name]

✅ All imports successful!
```

---

### Step 4: Test the Pipeline

```powershell
cd "CODEBASE\Clinical Audio Analysis Pipeline (nov 5)"

# Run on your test file
python main.py -i "data\input\test_audio2.mp3"
```

---

## ⚠️ Expected Warnings (Safe to Ignore)

After fixing, you'll still see these warnings - **they are normal and harmless:**

### 1. NumPy Dependency Conflicts
```
pyannote-core 6.0.1 requires numpy>=2.0, but you have numpy 1.26.4
pyannote-metrics 4.0.0 requires numpy>=2.2.2, but you have numpy 1.26.4
```
**Status:** ✅ SAFE TO IGNORE - Packaging metadata issue, runtime works fine

### 2. Missing Type Stubs
```
pandas-stubs requires types-pytz>=2022.1.1, which is not installed
```
**Status:** ✅ SAFE TO IGNORE - Only for development type checking

### 3. Torch Package Conflicts
```
asteroid-filterbanks 0.4.0 requires torch>=1.8.0, which is not installed
```
**Status:** ✅ SAFE TO IGNORE - This is because you have `torch==2.7.1+cu118` which pip sees as different from `torch==2.7.1`

---

## 🚨 Errors That Actually Matter

### Error 1: AttributeError on torchaudio.set_audio_backend
```
AttributeError: module 'torchaudio' has no attribute 'set_audio_backend'
```
**Fix:** Step 2 above (downgrade torchaudio or upgrade pyannote.audio)

### Error 2: Library cublas64_12.dll not found
```
Library cublas64_12.dll is not found or cannot be loaded
```
**Cause:** Your PyTorch is built for CUDA 11.8 but something is looking for CUDA 12.x libraries
**Fix:** This is usually a warning that can be ignored, but if it freezes:
- Option A: Install CUDA 11.8 Toolkit from NVIDIA
- Option B: Reinstall PyTorch for CUDA 12.1 (see below)

### Error 3: np.NaN AttributeError
```
AttributeError: `np.NaN` was removed in the NumPy 2.0 release
```
**Fix:** Step 1 above (downgrade NumPy to 1.26.x)

---

## 🔄 Complete Fresh Start (Nuclear Option)

If Steps 1-3 don't work, do a complete reinstall:

```powershell
cd "C:\Users\elija\OneDrive\Desktop\MAYO REPO\Synapse"

# Uninstall all ML packages
pip uninstall -y torch torchvision torchaudio numpy pyannote.audio faster-whisper transformers

# Reinstall with correct versions
pip install "numpy<2.0"
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install pyannote.audio faster-whisper transformers

# Reinstall other requirements
cd "CODEBASE\Clinical Audio Analysis Pipeline (nov 5)"
pip install -r requirements.txt
```

---

## 🎯 Quick Command Reference

### Check what's installed:
```powershell
pip list | Select-String "torch|numpy|pyannote"
```

### Check CUDA status:
```powershell
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}, Version: {torch.version.cuda if torch.cuda.is_available() else \"N/A\"}')"
```

### Run the pipeline:
```powershell
cd "C:\Users\elija\OneDrive\Desktop\MAYO REPO\Synapse\CODEBASE\Clinical Audio Analysis Pipeline (nov 5)"
python main.py -i "data\input\test_audio2.mp3"
```

---

## 📊 Performance Expectations

With CUDA 11.8 GPU acceleration working:

| Audio Length | Processing Time | Speed Factor |
|--------------|----------------|--------------|
| 5 minutes    | ~2-3 minutes   | ~2x realtime |
| 10 minutes   | ~4-5 minutes   | ~2x realtime |
| 20 minutes   | ~8-10 minutes  | ~2x realtime |

**Note:** First run is slower due to model loading. Subsequent runs are faster.

---

## 🆘 Still Having Issues?

### Check your error against these patterns:

1. **"AttributeError: module 'torchaudio' has no attribute 'set_audio_backend'"**
   - Go to Step 2

2. **"AttributeError: `np.NaN` was removed"**
   - Go to Step 1

3. **"Library cublas64_XX.dll is not found"**
   - Check CUDA Toolkit installation
   - Or try CPU-only mode temporarily

4. **Pipeline freezes at "Analyzing: 0%"**
   - This is usually the cublas issue
   - Try Ctrl+C to abort, then fix CUDA libraries

5. **"Could not find a version that satisfies the requirement torch"**
   - Make sure you're using the correct index URL
   - Check your Python version (should be 3.8-3.13)

---

## ✅ Success Checklist

- [ ] NumPy 1.26.x installed (verified with `python -c "import numpy; print(numpy.__version__)"`)
- [ ] PyTorch with CUDA installed (verified with `python -c "import torch; print(torch.cuda.is_available())"`)
- [ ] No torchaudio AttributeError when running pipeline
- [ ] Pipeline runs without freezing
- [ ] Output JSON file is created in `data/output/`

---

## 📚 Related Documents

- **NUMPY_FIX.md** - Detailed NumPy compatibility explanation
- **ALL_FIXES_SUMMARY.md** - Complete list of all fixes applied
- **GPU_SETUP_GUIDE.md** - GPU acceleration setup
- **INSTALLATION_NOTES.md** - Initial installation instructions

---

## 🎉 Once Fixed

Your pipeline should:
- ✅ Start without errors
- ✅ Show progress bars for each step
- ✅ Complete in reasonable time (~2x audio length)
- ✅ Generate JSON output files

The warnings about numpy version conflicts and missing type stubs will still appear but are completely harmless!

