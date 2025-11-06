# Scripts Archive

**Archived:** November 6, 2025  
**Reason:** Outdated - No longer needed with current setup

---

## 📦 Contents

This folder contains **4 outdated utility scripts** that were used during development to fix dependency issues.

| File | Purpose | Why Archived |
|------|---------|--------------|
| `fix_dependencies.bat` | Fix dependency conflicts (CMD) | Issues resolved by requirements.txt |
| `fix_dependencies.ps1` | Fix dependency conflicts (PS) | Issues resolved by requirements.txt |
| `fix_numpy.ps1` | Downgrade NumPy 2.x → 1.x | Constraint now in requirements.txt |
| `install_gpu_support.ps1` | Install PyTorch with CUDA | Documented in USER_GUIDE.md instead |

---

## 🔍 Why These Scripts Existed

### Historical Context (Nov 2025)

During initial development, several dependency issues emerged:

1. **NumPy 2.x Incompatibility:**
   - pyannote.audio didn't support NumPy 2.x
   - Needed to downgrade to 1.26.x
   - **Fixed:** Added `numpy<2.0` constraint to requirements.txt

2. **CUDA Library Mismatches:**
   - PyTorch CUDA version mismatches with system CUDA
   - Missing cublas64_12.dll errors
   - **Fixed:** ASR service now uses CPU by default (stable)

3. **Conflicting Package Versions:**
   - huggingface-hub version conflicts
   - torch/torchaudio version mismatches
   - **Fixed:** Pinned versions in requirements.txt

---

## ⚠️ Why Not Use These Scripts Now

### 1. Problems with Automated Fix Scripts

**Hardcoded versions:**
```powershell
# These scripts install specific old versions
pip install torch==2.7.1 --index-url .../cu118
```
- User has CUDA 13.0, scripts use CUDA 11.8
- Versions may be outdated by now
- Doesn't adapt to user's system

**Hardcoded paths:**
```powershell
$projectPath = "C:\Users\elija\OneDrive\Desktop\MAYO REPO\Synapse"
```
- Only works on one specific machine
- Breaks for other users

**Dangerous operations:**
```powershell
pip uninstall torch -y  # Removes without confirmation
```
- Can break working installations
- No safety checks

### 2. Better Approaches Now

**Instead of fix_numpy.ps1:**
```bash
# Old way: Run script
powershell .\fix_numpy.ps1

# New way: Install from requirements
pip install -r requirements.txt
# requirements.txt has: numpy>=1.24,<2.0
```

**Instead of fix_dependencies scripts:**
```bash
# Old way: Run fix script with hardcoded versions
.\fix_dependencies.bat

# New way: Follow USER_GUIDE.md troubleshooting
# Clear instructions, user-controlled, flexible
```

**Instead of install_gpu_support.ps1:**
```bash
# Old way: Script guesses CUDA version
.\install_gpu_support.ps1  # Installs CUDA 12.1

# New way: USER_GUIDE.md has instructions
# 1. Check your CUDA version: nvidia-smi
# 2. Install matching PyTorch from pytorch.org
# 3. User chooses correct version for their system
```

---

## 📚 Current Approach (Nov 6, 2025)

### Installation Process:
1. **Install from requirements.txt** (handles versions automatically)
2. **GPU setup** (optional, documented in USER_GUIDE.md)
3. **Diagnostic scripts** (in `scripts/` folder for verification)

### If Issues Occur:
1. **Run diagnostics:** `python scripts/check_deps.py`
2. **Check GPU:** `python scripts/check_gpu.py`
3. **Read troubleshooting:** USER_GUIDE.md
4. **Manual fix** with clear instructions (not automated)

---

## 🔄 What Replaced These Scripts

### Diagnostic Scripts (in `scripts/`):
- `check_deps.py` - Verify dependencies are correct
- `check_gpu.py` - Check GPU availability and status

### Documentation (in root):
- **USER_GUIDE.md** - Complete troubleshooting guide
- **TECHNICAL_DOCUMENTATION.md** - System requirements
- **requirements.txt** - Correct dependency versions

### Why Better:
- ✅ Diagnostic only (safe, can't break things)
- ✅ Clear instructions (user-controlled)
- ✅ Flexible (adapts to different systems)
- ✅ Documented (explanation of issues)

---

## 🗂️ When to Use These Archives

**Rarely needed, but kept for:**

1. **Historical reference** - Understanding past issues
2. **Debugging** - If similar issues reoccur
3. **Learning** - See how problems were solved
4. **Emergency** - Worst-case scenario recovery

**How to use if needed:**
1. Check if issue still exists (may be resolved)
2. Adapt script to your system (change paths, versions)
3. Review before running (don't blindly execute)
4. Prefer manual fixes from USER_GUIDE.md

---

## 📋 Summary

**Status:** Archived (not deleted)  
**Reason:** Issues resolved by better approaches  
**Current Solution:** requirements.txt + USER_GUIDE.md  
**Use Archives:** Only if you understand the scripts and adapt them  

**Recommendation:** Use the current setup process, not these old scripts.

---

**Archived:** November 6, 2025  
**By:** Development team cleanup  
**Status:** Preserved for reference only

