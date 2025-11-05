# Vocal Feature Analysis Module - Setup Guide

## Phase 1: Environment Setup

This guide will help you set up the development environment for the Vocal Feature Analysis Module.

---

## Prerequisites

- **Python**: Version 3.10 or higher (tested with Python 3.12)
- **ffmpeg**: Required for audio file conversion
- **Git**: For version control
- **CUDA** (Optional): For GPU acceleration (recommended for faster processing)

---

## 1. Python Environment Setup

### Option A: Using venv (Recommended)

```bash
# Navigate to the project directory
cd "CODEBASE/Vocal Feature Analysis"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

### Option B: Using conda

```bash
# Create conda environment
conda create -n vocal-analysis python=3.12

# Activate environment
conda activate vocal-analysis

# Upgrade pip
pip install --upgrade pip
```

---

## 2. Install Dependencies

Install all required packages from requirements.txt:

```bash
pip install -r requirements.txt
```

**Note**: The installation may take several minutes as it downloads PyTorch, Whisper, and other large packages.

### Troubleshooting Installation

If you encounter issues:

1. **PyTorch installation**: Visit [pytorch.org](https://pytorch.org/) to get the correct installation command for your system
2. **CUDA issues**: Ensure your NVIDIA drivers are up to date if using GPU
3. **ffmpeg errors**: Make sure ffmpeg is installed and in your system PATH

---

## 3. Install ffmpeg

ffmpeg is required for audio format conversion.

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install ffmpeg
```

### macOS (using Homebrew)
```bash
brew install ffmpeg
```

### Windows
1. Download from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract to a directory (e.g., `C:\ffmpeg`)
3. Add to system PATH:
   - Search for "Environment Variables" in Windows
   - Edit "Path" variable
   - Add the `bin` folder path (e.g., `C:\ffmpeg\bin`)

Verify installation:
```bash
ffmpeg -version
```

---

## 4. Hugging Face Token Setup

The diarization model requires a Hugging Face token.

### Step 1: Create an Account
- Visit [huggingface.co](https://huggingface.co) and create an account

### Step 2: Accept Model Terms
- Visit [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)
- Click "Agree and access repository"

### Step 3: Generate Token
1. Go to [Settings > Access Tokens](https://huggingface.co/settings/tokens)
2. Click "New token"
3. Name it (e.g., "synapse-vocal-analysis")
4. Select "Read" permissions
5. Copy the token (starts with `hf_`)

### Step 4: Set Environment Variable

#### Option A: Using .env file (Recommended)
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your token
# HF_TOKEN=hf_your_actual_token_here
```

#### Option B: System Environment Variable

**Linux/Mac:**
```bash
export HF_TOKEN="hf_your_actual_token_here"
```

**Windows PowerShell:**
```powershell
$env:HF_TOKEN = "hf_your_actual_token_here"
```

**Windows Command Prompt:**
```cmd
set HF_TOKEN=hf_your_actual_token_here
```

---

## 5. Verify Installation

Run the environment validation script:

```bash
python validate_environment.py
```

This will check:
- ✓ Python version
- ✓ All required packages
- ✓ ffmpeg availability
- ✓ HF_TOKEN configuration
- ✓ CUDA availability (if applicable)

---

## 6. Test the Pipeline

Run a simple test to ensure everything works:

```bash
# Create a test audio file (requires an audio file)
python VocalAnalysis.py
```

---

## Directory Structure

After setup, your directory should look like:

```
Vocal Feature Analysis/
├── .env                    # Your environment variables (DO NOT COMMIT)
├── .env.example           # Template for environment variables
├── requirements.txt       # Python dependencies
├── SETUP.md              # This file
├── VocalAnalysis.py      # Main pipeline script
├── convert_audio.py      # Audio conversion utility
├── validate_environment.py # Environment validation script
├── pretrained_models/    # Downloaded models (auto-created)
└── venv/                 # Virtual environment (if using venv)
```

---

## Next Steps

After completing the setup:

1. **Review the Development Plan**: See `DevelopmentPlan.md` for the full project roadmap
2. **Data Preparation**: See Task 1.2 in the development plan
3. **Feature Research**: See Task 1.3 in the development plan

---

## Common Issues

### Issue: "HF_TOKEN not set" error
**Solution**: Make sure you've set the HF_TOKEN environment variable (see Step 4)

### Issue: "ffmpeg not found" error
**Solution**: Install ffmpeg and ensure it's in your system PATH (see Step 3)

### Issue: CUDA out of memory
**Solution**: 
- Use CPU mode: Set `device="cpu"` in VocalAnalysis.py
- Or use smaller batch sizes

### Issue: Module import errors
**Solution**: 
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the project documentation
3. Contact the development team

---

**Last Updated**: November 2025  
**Phase**: Phase 1 - Setup, Data Curation & Feature Research
