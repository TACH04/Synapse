# Analysis of Utility Scripts (.bat, .ps1, .py)

**Date:** November 6, 2025  
**Purpose:** Determine which scripts are outdated/unnecessary

---

## 📊 Analysis Summary

### Files Analyzed: 6 total

| File | Type | Purpose | Status | Recommendation |
|------|------|---------|--------|----------------|
| `check_deps.py` | Python | Verify dependencies installed correctly | ✅ Useful | **KEEP** |
| `check_gpu.py` | Python | GPU detection & diagnostics | ✅ Useful | **KEEP** |
| `fix_dependencies.bat` | Batch | Fix dependency issues (Windows CMD) | ⚠️ Outdated | **ARCHIVE** |
| `fix_dependencies.ps1` | PowerShell | Fix dependency issues (PowerShell) | ⚠️ Outdated | **ARCHIVE** |
| `fix_numpy.ps1` | PowerShell | Fix NumPy 2.x compatibility | ⚠️ Outdated | **ARCHIVE** |
| `install_gpu_support.ps1` | PowerShell | Install PyTorch with CUDA | ⚠️ Outdated | **ARCHIVE** |

---

## 🔍 Detailed Analysis

### ✅ KEEP (2 files) - Still Useful

#### 1. `check_deps.py` - ✅ KEEP
**Purpose:** Quick verification of dependencies

**Why keep:**
- Helps users verify installation
- Checks for common issues (NumPy version, CUDA availability)
- Simple, harmless diagnostic tool
- Still relevant to current setup

**Recommendation:** Keep in root, maybe move to `scripts/` folder for organization

---

#### 2. `check_gpu.py` - ✅ KEEP
**Purpose:** Comprehensive GPU diagnostics

**Why keep:**
- Helps troubleshoot GPU issues
- Detailed memory and CUDA information
- Useful for users with GPU problems
- Tests GPU with actual operation

**Recommendation:** Keep in root, maybe move to `scripts/` folder for organization

---

### ⚠️ ARCHIVE (4 files) - Outdated/No Longer Needed

#### 3. `fix_dependencies.bat` - ⚠️ ARCHIVE
**Purpose:** Fix dependency conflicts (Windows CMD version)

**Why outdated:**
- Installs specific old versions: `torch==2.7.1+cu118`
- NumPy fix is automated now (in requirements.txt: `numpy<2.0`)
- CUDA 11.8 is old (system has CUDA 13.0)
- Dependencies are stable now - no longer needed
- Issues documented in USER_GUIDE.md troubleshooting

**Current approach:** Users install from requirements.txt, which handles versions correctly

---

#### 4. `fix_dependencies.ps1` - ⚠️ ARCHIVE
**Purpose:** Fix dependency conflicts (PowerShell version)

**Why outdated:**
- Same as .bat version, just PowerShell syntax
- Installs old specific versions
- Issues are resolved by requirements.txt now
- Troubleshooting in USER_GUIDE.md

**Current approach:** `pip install -r requirements.txt` handles everything

---

#### 5. `fix_numpy.ps1` - ⚠️ ARCHIVE
**Purpose:** Downgrade NumPy 2.x to 1.x

**Why outdated:**
- requirements.txt now specifies `numpy>=1.24,<2.0`
- Automatic when installing from requirements.txt
- Issue is documented in history but no longer occurs
- Script is redundant

**Current approach:** requirements.txt constraint handles this automatically

---

#### 6. `install_gpu_support.ps1` - ⚠️ ARCHIVE
**Purpose:** Install PyTorch with CUDA support

**Why outdated:**
- Hardcoded to CUDA 12.1 (user has CUDA 13.0)
- Hardcoded project path: `C:\Users\elija\OneDrive\Desktop\MAYO REPO\Synapse`
- GPU installation now documented in USER_GUIDE.md
- One-size-fits-all approach doesn't work (CUDA versions vary)
- ASR service uses CPU by design (to avoid CUDA issues)

**Current approach:** Manual GPU setup in USER_GUIDE.md with flexible instructions

---

## 🎯 Recommendations

### Immediate Actions

1. **KEEP** (Move to `scripts/` for organization):
   - `check_deps.py`
   - `check_gpu.py`

2. **ARCHIVE** (Move to `scripts_archive/`):
   - `fix_dependencies.bat`
   - `fix_dependencies.ps1`
   - `fix_numpy.ps1`
   - `install_gpu_support.ps1`

### Why Archive Instead of Delete?

- **Historical reference** - Shows what issues existed
- **May be useful** - If similar issues return
- **Safe approach** - Can recover if needed
- **Documentation value** - Shows evolution of setup process

---

## 📂 Proposed New Structure

### Current:
```
Clinical Audio Analysis Pipeline/
├── check_deps.py
├── check_gpu.py
├── fix_dependencies.bat          ← Outdated
├── fix_dependencies.ps1          ← Outdated
├── fix_numpy.ps1                 ← Outdated
├── install_gpu_support.ps1       ← Outdated
└── ...
```

### Proposed:
```
Clinical Audio Analysis Pipeline/
├── scripts/                       ← NEW folder
│   ├── check_deps.py             ← Moved here (useful)
│   ├── check_gpu.py              ← Moved here (useful)
│   ├── prepare_dataset.py        ← Already here
│   └── train_emotion_model.py    ← Already here
│
├── scripts_archive/               ← NEW folder
│   ├── fix_dependencies.bat      ← Archived
│   ├── fix_dependencies.ps1      ← Archived
│   ├── fix_numpy.ps1             ← Archived
│   └── install_gpu_support.ps1   ← Archived
│
└── ...
```

---

## 🔧 Alternative: Enhanced Check Scripts

Instead of old fix scripts, we could create **one modern diagnostic script**:

### `scripts/diagnose_setup.py`
```python
"""
Comprehensive setup diagnostics.
Checks everything and provides clear instructions if issues found.
"""

def check_all():
    - Check Python version
    - Check all dependencies
    - Check GPU availability
    - Check CUDA compatibility
    - Run test audio snippet
    - Provide clear next steps if issues
```

**Benefits:**
- One tool instead of multiple fix scripts
- Diagnostic only (doesn't change anything)
- Provides instructions for user to fix
- Safer than automated fix scripts

---

## 📝 Impact on Documentation

### Files to Update:

**USER_GUIDE.md:**
- Update "Troubleshooting" section
- Mention `scripts/check_deps.py` and `scripts/check_gpu.py`
- Remove references to fix scripts (if any)

**README.md:**
- Update project structure if needed
- Mention diagnostic scripts location

---

## ✅ Rationale

### Why These Scripts Are Outdated:

1. **Dependency Issues Resolved:**
   - NumPy constraint now in requirements.txt
   - Package versions stable
   - No more conflicts

2. **Better Documentation:**
   - USER_GUIDE.md has comprehensive troubleshooting
   - Clear instructions for manual fixes
   - More flexible than hardcoded scripts

3. **CUDA Complexity:**
   - Every system has different CUDA version
   - Hardcoded CUDA version doesn't work universally
   - ASR uses CPU by design (avoids CUDA issues)

4. **Changed Approach:**
   - From "automated fixes" → "clear diagnostics + manual fix"
   - More reliable and user-controlled
   - Less likely to break things

---

## 🎯 Final Recommendation

### KEEP (Organize):
- ✅ `check_deps.py` → Move to `scripts/`
- ✅ `check_gpu.py` → Move to `scripts/`

### ARCHIVE:
- 📦 `fix_dependencies.bat` → Move to `scripts_archive/`
- 📦 `fix_dependencies.ps1` → Move to `scripts_archive/`
- 📦 `fix_numpy.ps1` → Move to `scripts_archive/`
- 📦 `install_gpu_support.ps1` → Move to `scripts_archive/`

### OPTIONAL (Future):
- 💡 Create `scripts/diagnose_setup.py` (comprehensive diagnostic tool)

---

**Analysis Complete:** Ready to organize files

**Next Step:** Execute file moves

