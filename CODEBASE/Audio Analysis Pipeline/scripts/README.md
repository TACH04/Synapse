# Scripts Folder

**Purpose:** Utility scripts for diagnostics and Phase 2 development

---

## 📁 Contents

### 🔍 Diagnostic Tools (Current)

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `check_deps.py` | Verify dependencies installed correctly | After installation, troubleshooting |
| `check_gpu.py` | Check GPU availability and configuration | GPU issues, performance troubleshooting |

### 🚀 Phase 2 Tools (Future)

| Script | Purpose | Status |
|--------|---------|--------|
| `prepare_dataset.py` | Prepare training data for fine-tuning | 📋 Planned |
| `train_emotion_model.py` | Fine-tune emotion model on clinical data | 📋 Planned |

---

## 🔍 Diagnostic Tools Usage

### check_deps.py - Dependency Verification

**Purpose:** Quick check that all dependencies are installed correctly

**Usage:**
```bash
python scripts/check_deps.py
```

**What it checks:**
- ✅ Python version
- ✅ NumPy version (should be 1.26.x, not 2.x)
- ✅ PyTorch version and CUDA support
- ✅ TorchAudio compatibility
- ✅ Pyannote.audio installation

**Example output:**
```
============================================================
DEPENDENCY VERIFICATION
============================================================

✓ Python: 3.10.11

✅ NumPy: 1.26.4 (CORRECT)
✅ PyTorch: 2.7.1+cu118 (CUDA version)
✅ CUDA Available: True
   CUDA Version: 11.8
   GPU: NVIDIA GeForce RTX 3050 Laptop GPU
✅ TorchAudio: 2.7.1+cu118 (matches PyTorch)
✅ Pyannote.audio: 4.0.1

All dependencies installed correctly! ✨
```

**When to use:**
- After first installation
- When troubleshooting issues
- Before running the pipeline
- After dependency updates

---

### check_gpu.py - GPU Diagnostics

**Purpose:** Comprehensive GPU detection and diagnostic report

**Usage:**
```bash
python scripts/check_gpu.py
```

**What it checks:**
- ✅ PyTorch installation and version
- ✅ CUDA availability and version
- ✅ cuDNN version
- ✅ Number of GPUs detected
- ✅ GPU name and compute capability
- ✅ GPU memory (total, reserved, allocated)
- ✅ All required packages (transformers, faster-whisper, pyannote)
- ✅ Simple GPU operation test

**Example output:**
```
======================================================================
GPU DETECTION AND DIAGNOSTIC REPORT
======================================================================

1. Checking PyTorch Installation...
   ✓ PyTorch version: 2.7.1+cu118
   ✓ CUDA available: True
   ✓ CUDA version: 11.8
   ✓ cuDNN version: 8902
   ✓ Number of GPUs: 1

   GPU 0:
      Name: NVIDIA GeForce RTX 3050 Laptop GPU
      Compute Capability: (8, 6)
      Total Memory: 4.00 GB
      Reserved Memory: 0.05 GB
      Allocated Memory: 0.00 GB

2. Checking Transformers Installation...
   ✓ Transformers version: 4.57.1

3. Checking faster-whisper Installation...
   ✓ faster-whisper is installed

4. Checking pyannote.audio Installation...
   ✓ pyannote.audio version: 4.0.1

5. Testing GPU with Simple Operation...
   ✓ GPU test successful!
   ✓ Tensor created on GPU: cuda:0
   ✓ Matrix multiplication on GPU: completed

======================================================================
Summary: ✅ GPU is available and working correctly!
======================================================================
```

**When to use:**
- When pipeline runs slower than expected
- When CUDA errors occur
- To verify GPU is being used
- To check available GPU memory
- Before processing large audio files

---

## 🚀 Phase 2 Tools (Planned)

### prepare_dataset.py

**Purpose:** Prepare clinical conversation data for model fine-tuning

**Features (planned):**
- Load raw clinical audio files
- Extract features using Phase 1 pipeline
- Format data for training
- Create train/validation/test splits
- Generate dataset statistics

**Usage (future):**
```bash
python scripts/prepare_dataset.py \
    --input-dir data/raw_clinical/ \
    --output-dir data/training/ \
    --split 0.7/0.15/0.15
```

---

### train_emotion_model.py

**Purpose:** Fine-tune emotion detection model on clinical data

**Features (planned):**
- Load base model (HuBERT or Wav2Vec2)
- Fine-tune on clinical emotion dataset
- Hyperparameter optimization
- Model evaluation on validation set
- Save fine-tuned model

**Usage (future):**
```bash
python scripts/train_emotion_model.py \
    --base-model superb/hubert-base-superb-er \
    --training-data data/training/ \
    --output models/clinical_emotion_v1 \
    --epochs 20 \
    --batch-size 16
```

---

## 🔧 Adding New Scripts

### Guidelines:

1. **Name clearly** - Script name should indicate purpose
2. **Add docstring** - Explain what the script does
3. **Include usage** - Command-line help text
4. **Handle errors** - Graceful failure with clear messages
5. **Update this README** - Document the new script

### Template:

```python
#!/usr/bin/env python3
"""
Script Name: my_script.py
Purpose: Brief description of what this script does

Usage:
    python scripts/my_script.py [options]

Example:
    python scripts/my_script.py --input data/
"""

import argparse

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="My script description")
    parser.add_argument('-i', '--input', required=True, help='Input path')
    args = parser.parse_args()
    
    # Your code here
    print(f"Processing: {args.input}")

if __name__ == "__main__":
    main()
```

---

## 📚 Related Documentation

- **USER_GUIDE.md** - Complete user manual
- **TECHNICAL_DOCUMENTATION.md** - System architecture
- **PHASE2_ROADMAP.md** - Future development plans

---

## 🗂️ Archived Scripts

Old fix scripts moved to `../scripts_archive/`:
- `fix_dependencies.bat` (outdated)
- `fix_dependencies.ps1` (outdated)
- `fix_numpy.ps1` (outdated)
- `install_gpu_support.ps1` (outdated)

See `../scripts_archive/README.md` for details.

---

**Last Updated:** November 6, 2025  
**Status:** 2 diagnostic scripts active, 2 Phase 2 scripts planned

