# 📚 Documentation Index
## Clinical Audio Analysis Pipeline

Welcome! This index will help you find the right documentation for your needs.

---

## 🚀 Getting Started (New Users)

**Start here if this is your first time:**

1. **[QUICKSTART.md](QUICKSTART.md)** ⭐ START HERE
   - 5-minute setup guide
   - Basic commands
   - Quick examples
   - Common troubleshooting

2. **[README.md](README.md)** 
   - Complete project overview
   - Detailed installation instructions
   - Full usage documentation
   - Output format specification

---

## 🏗️ Understanding the System

**Read these to understand how it works:**

3. **[ARCHITECTURE.md](ARCHITECTURE.md)**
   - Visual system diagrams
   - Data flow explanation
   - Service details
   - Phase 2 workflow
   - Design decisions

4. **[PHASE1_SUMMARY.md](PHASE1_SUMMARY.md)**
   - What was built
   - Problems solved
   - Development decisions
   - Testing recommendations

---

## ✅ For Developers

**Technical reference and validation:**

5. **[COMPLETION_CHECKLIST.md](COMPLETION_CHECKLIST.md)**
   - Complete file list
   - Requirements verification
   - Success criteria
   - Known limitations

6. **[requirements.txt](requirements.txt)**
   - All Python dependencies
   - Version specifications

---

## 📖 Quick Reference Guide

### Which Document Should I Read?

| Your Goal | Read This |
|-----------|-----------|
| Just want to run the pipeline ASAP | [QUICKSTART.md](QUICKSTART.md) |
| Need complete installation instructions | [README.md](README.md) |
| Want to understand the architecture | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Need to know what was implemented | [PHASE1_SUMMARY.md](PHASE1_SUMMARY.md) |
| Verifying all components are complete | [COMPLETION_CHECKLIST.md](COMPLETION_CHECKLIST.md) |
| Installing dependencies | [requirements.txt](requirements.txt) |

---

## 🎯 Common Tasks

### First Time Setup
```
1. Read: QUICKSTART.md (Steps 1-3)
2. Run: pip install -r requirements.txt
3. Set: HF_TOKEN environment variable
4. Test: python main.py -i ./data/input/test.mp3
```

### Running Analysis
```
See: QUICKSTART.md → "Command Reference"
Or:  README.md → "Usage" section
```

### Understanding Output
```
See: README.md → "Output Format" section
Or:  ARCHITECTURE.md → "Output JSON Structure"
```

### Troubleshooting
```
1st: QUICKSTART.md → "Troubleshooting"
2nd: README.md → "Troubleshooting"
3rd: PHASE1_SUMMARY.md → "Potential Issues & Solutions"
```

### Phase 2 Training
```
See: QUICKSTART.md → "Quick Phase 2 Workflow"
Or:  ARCHITECTURE.md → "Phase 2 Workflow"
Or:  README.md → "Phase 2: Building the Specialized Tool"
```

### Architecture Details
```
See: ARCHITECTURE.md → Complete visual guide
Or:  PHASE1_SUMMARY.md → "Architecture Highlights"
```

---

## 📁 Code Files Reference

### Main Execution
- `main.py` - Phase 1 pipeline (general models)
- `main_phase2.py` - Phase 2 pipeline (specialized model)

### Core Pipeline
- `pipeline/analysis_pipeline.py` - Main orchestrator
- `pipeline/audio_utilities.py` - Audio loading/slicing
- `pipeline/services/diarization_service.py` - Speaker identification
- `pipeline/services/asr_service.py` - Transcription
- `pipeline/services/emotion_service.py` - Emotion recognition
- `pipeline/services/acoustic_service.py` - Acoustic features

### Phase 2 Scripts
- `scripts/prepare_dataset.py` - Create training dataset
- `scripts/train_emotion_model.py` - Fine-tune model

---

## 🆘 Getting Help

### Step-by-Step Troubleshooting

**Problem: Don't know where to start**
→ Read [QUICKSTART.md](QUICKSTART.md)

**Problem: Installation failing**
→ Check [README.md](README.md) "Installation" section
→ Verify Python version (3.8+)
→ Check [requirements.txt](requirements.txt)

**Problem: HF_TOKEN errors**
→ Read [QUICKSTART.md](QUICKSTART.md) Step 2-3
→ Or [README.md](README.md) "CRITICAL: Hugging Face Authentication"

**Problem: Pipeline errors during execution**
→ Check [QUICKSTART.md](QUICKSTART.md) "Troubleshooting"
→ Verify input file exists and is valid audio
→ Check error message for specific guidance

**Problem: Don't understand the output**
→ See [README.md](README.md) "Output Format"
→ See [ARCHITECTURE.md](ARCHITECTURE.md) "Output JSON Structure"

**Problem: Want to customize or modify**
→ Read [ARCHITECTURE.md](ARCHITECTURE.md) for system understanding
→ Read [PHASE1_SUMMARY.md](PHASE1_SUMMARY.md) for implementation details
→ Code has comprehensive docstrings

---

## 📊 Document Summary

| Document | Length | Best For |
|----------|--------|----------|
| QUICKSTART.md | Short | Getting started fast |
| README.md | Medium | Complete reference |
| ARCHITECTURE.md | Visual | Understanding system |
| PHASE1_SUMMARY.md | Long | Development details |
| COMPLETION_CHECKLIST.md | Reference | Verification |
| INDEX.md (this file) | Navigation | Finding help |

---

## 🎓 Learning Path

### For End Users (Just Want to Use It)
1. [QUICKSTART.md](QUICKSTART.md) - Setup and run
2. [README.md](README.md) - Reference when needed
3. [ARCHITECTURE.md](ARCHITECTURE.md) - Understand output

### For Developers (Want to Modify/Extend)
1. [README.md](README.md) - Understand capabilities
2. [ARCHITECTURE.md](ARCHITECTURE.md) - Understand design
3. [PHASE1_SUMMARY.md](PHASE1_SUMMARY.md) - Implementation details
4. Code files with docstrings - Specific implementations

### For Project Managers (Want Overview)
1. [README.md](README.md) - Project overview
2. [COMPLETION_CHECKLIST.md](COMPLETION_CHECKLIST.md) - What's done
3. [PHASE1_SUMMARY.md](PHASE1_SUMMARY.md) - Executive summary

---

## ⚡ Most Important Files

**Essential Reading:**
1. ⭐⭐⭐ [QUICKSTART.md](QUICKSTART.md) - Everyone should read this first
2. ⭐⭐ [README.md](README.md) - Complete reference guide
3. ⭐⭐ [INSTALLATION_NOTES.md](INSTALLATION_NOTES.md) - Installation troubleshooting & status

**For Understanding:**
3. ⭐⭐ [ARCHITECTURE.md](ARCHITECTURE.md) - How everything works

**For Reference:**
4. ⭐ [PHASE1_SUMMARY.md](PHASE1_SUMMARY.md) - Development summary
5. ⭐ [COMPLETION_CHECKLIST.md](COMPLETION_CHECKLIST.md) - Verification

---

## 📞 Quick Answers

**Q: How do I install?**
A: `pip install -r requirements.txt` (See QUICKSTART.md Step 1)

**Q: How do I run?**
A: `python main.py -i your_audio.mp3` (See QUICKSTART.md Step 4)

**Q: What's HF_TOKEN?**
A: Hugging Face authentication (See QUICKSTART.md Step 2-3)

**Q: What models does it use?**
A: See README.md "Project Dependency" table

**Q: What's the output format?**
A: JSON with segments (See README.md "Output Format")

**Q: How do I do Phase 2?**
A: See QUICKSTART.md "Quick Phase 2 Workflow"

**Q: Is Phase 1 complete?**
A: Yes! See COMPLETION_CHECKLIST.md

**Q: Can I use my own models?**
A: Yes! The architecture is modular (See ARCHITECTURE.md)

---

## ✅ Pre-Flight Checklist

Before you start, verify you have:
- [ ] Python 3.8 or higher installed
- [ ] Read QUICKSTART.md
- [ ] Created Hugging Face account
- [ ] Obtained HF_TOKEN
- [ ] Installed dependencies (`pip install -r requirements.txt`)
- [ ] Test audio file ready

**All checked?** You're ready to go! Run:
```bash
python main.py -i ./data/input/your_audio.mp3
```

---

**Happy analyzing!** 🎉

If you need help, start with [QUICKSTART.md](QUICKSTART.md) or [README.md](README.md).

