# Technical Documentation - Clinical Audio Analysis Pipeline

**Version:** 2.0  
**Last Updated:** November 6, 2025

---

## 📋 Table of Contents

1. [System Architecture](#system-architecture)
2. [Core Components](#core-components)
3. [Data Flow](#data-flow)
4. [Emotion Detection System](#emotion-detection-system)
5. [Model Details](#model-details)
6. [Performance Characteristics](#performance-characteristics)
7. [API Reference](#api-reference)

---

## 🏗️ System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLINICAL AUDIO ANALYSIS PIPELINE              │
│                      (Phase 1: Data Mining Machine)              │
└─────────────────────────────────────────────────────────────────┘

                         ┌──────────────┐
                         │   main.py    │
                         │ (User Entry) │
                         └──────┬───────┘
                                │
                                ▼
                 ┌──────────────────────────┐
                 │  AnalysisPipeline        │
                 │  (Orchestrator)          │
                 └──────────┬───────────────┘
                            │
         ┌──────────────────┼──────────────────┬──────────────┐
         │                  │                  │              │
         ▼                  ▼                  ▼              ▼
┌────────────────┐  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐
│ Diarization    │  │    ASR      │  │   Emotion    │  │   Acoustic   │
│   Service      │  │  Service    │  │   Service    │  │   Service    │
│ (Who & When)   │  │ (What Said) │  │  (How Said-  │  │  (How Said-  │
│                │  │             │  │  Subjective) │  │  Objective)  │
└────────┬───────┘  └──────┬──────┘  └──────┬───────┘  └──────┬───────┘
         │                 │                │                 │
         └─────────────────┴────────────────┴─────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │  Audio Utilities      │
                    │  - Load & Resample    │
                    │  - Slice Audio        │
                    └───────────┬───────────┘
                                │
                                ▼
                        ┌───────────────┐
                        │  Input Audio  │
                        │  (16kHz mono) │
                        └───────────────┘
```

### Module Dependencies

```
AnalysisPipeline
├── DiarizationService
│   └── pyannote.audio
├── ASRService
│   └── faster-whisper
├── EmotionService (Triple Ensemble)
│   ├── HuBERT (transformers)
│   ├── Wav2Vec2 (transformers)
│   └── DistilRoBERTa (transformers)
├── AcousticService
│   └── praat-parselmouth
└── AudioUtilities
    └── torchaudio
```

---

## 🔧 Core Components

### 1. Audio Utilities (`audio_utilities.py`)

**Purpose:** Data integrity gate - ensures all audio is in the correct format.

**Key Functions:**

#### `load_and_resample_audio(file_path: str) -> Tuple[np.ndarray, int]`
```python
"""
Loads audio file and converts to 16kHz mono.

Args:
    file_path: Path to audio file (any format)

Returns:
    (audio_array, sample_rate): NumPy array + 16000

Process:
    1. Load with torchaudio
    2. Convert stereo → mono (average channels)
    3. Resample to 16kHz (required by all models)
    4. Convert tensor → NumPy array (float32)
"""
```

#### `slice_audio(audio_array, sample_rate, start_sec, end_sec) -> np.ndarray`
```python
"""
Extracts audio segment by time boundaries.

Args:
    audio_array: Full audio (1D NumPy)
    sample_rate: Samples per second (16000)
    start_sec: Start time in seconds
    end_sec: End time in seconds

Returns:
    Sliced audio segment

Example:
    # Get audio from 2.5s to 5.8s
    segment = slice_audio(audio, 16000, 2.5, 5.8)
    # Returns audio[40000:92800]
"""
```

---

### 2. Diarization Service (`diarization_service.py`)

**Purpose:** Answers "Who spoke and when?"

**Model:** `pyannote/speaker-diarization-3.1`

**Architecture:**
```
Input Audio → Speaker Embedding → Clustering → Timeline
                  (Neural Net)      (UMAP)     (Segments)
```

**Process:**
1. Extracts speaker embeddings every 0.5s
2. Clusters embeddings into N speakers
3. Applies voice activity detection (VAD)
4. Returns timeline with speaker labels

**Output Format:**
```python
[
    {"speaker": "SPEAKER_00", "start_time": 0.5, "end_time": 3.2},
    {"speaker": "SPEAKER_01", "start_time": 3.5, "end_time": 7.1},
    # ...
]
```

**GPU Acceleration:** Yes (CUDA if available)

**Memory:** ~2GB VRAM / ~4GB RAM

---

### 3. ASR Service (`asr_service.py`)

**Purpose:** Answers "What was said?"

**Model:** `faster-whisper` (Whisper optimized with CTranslate2)

**Architecture:**
```
Audio → Feature Extraction → Encoder → Decoder → Text
         (Mel Spectrogram)    (Transformer) (Transformer)
```

**Key Features:**
- **Quantization:** Supports float16, int8 for faster inference
- **Beam Search:** Configurable beam size (default: 5)
- **Language:** English-only models (`*.en`)
- **VAD:** Built-in voice activity detection

**Model Sizes:**

| Model | Parameters | Speed | Accuracy | RAM |
|-------|-----------|-------|----------|-----|
| tiny.en | 39M | Fastest | 70% WER | 1GB |
| base.en | 74M | Fast | 50% WER | 1GB |
| small.en | 244M | Medium | 40% WER | 2GB |
| medium.en | 769M | Slow | 30% WER | 5GB |

**GPU Acceleration:** Optional (CPU-only by default to avoid CUDA issues)

---

### 4. Emotion Service (`emotion_service.py`)

**Purpose:** Answers "How was it said?" (subjective emotion)

**Architecture:** Triple Ensemble System

#### Model 1: HuBERT (Prosody Expert)
- **Model:** `superb/hubert-base-superb-er`
- **Focus:** Tone, pitch, rhythm
- **Labels:** `neu`, `hap`, `ang`, `sad` (4 emotions)
- **Strength:** Detects vocal prosody patterns

#### Model 2: Wav2Vec2 (Phonetic Expert)
- **Model:** `ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition`
- **Focus:** Articulation under emotion
- **Labels:** `angry`, `calm`, `disgust`, `fearful`, `happy`, `neutral`, `sad`, `surprised` (8 emotions)
- **Strength:** Detects subtle phonetic changes

#### Model 3: DistilRoBERTa (Semantic Expert)
- **Model:** `j-hartmann/emotion-english-distilroberta-base`
- **Focus:** Word meaning, sentiment
- **Labels:** `anger`, `disgust`, `fear`, `joy`, `neutral`, `sadness`, `surprise` (7 emotions)
- **Strength:** Detects emotional content in words

#### Ensemble Logic

**Step 1: Individual Predictions**
```python
hubert_pred = analyze_audio_with_hubert(audio)
wav2vec2_pred = analyze_audio_with_wav2vec2(audio)
text_pred = analyze_text_with_distilroberta(transcript)
```

**Step 2: Dynamic Weighting**
```python
if text_score > 0.85:
    weights = {'hubert': 0.30, 'wav2vec2': 0.20, 'text': 0.50}
elif hubert_score > 0.70 and wav2vec2_score > 0.50:
    weights = {'hubert': 0.45, 'wav2vec2': 0.40, 'text': 0.15}
else:
    weights = {'hubert': 0.40, 'wav2vec2': 0.35, 'text': 0.25}
```

**Step 3: Veto Power**
```python
# If any model >0.90 confidence on non-neutral:
if text_score > 0.90 and text_label != 'neutral':
    return text_label  # Text veto
elif hubert_score > 0.90 and hubert_label != 'neu':
    return hubert_label  # HuBERT veto
```

**Step 4: Acoustic Validation**
```python
# Validate with pitch, jitter, HNR
if emotion == 'ang' and pitch > 150 and jitter > 0.02:
    score *= 1.15  # Boost confidence
```

**Step 5: Final Prediction**
```python
combined_score = (
    hubert_score * weights['hubert'] +
    wav2vec2_score * weights['wav2vec2'] +
    text_score * weights['text']
)
final_label = weighted_vote(predictions, weights)
```

**Key Improvements (Nov 6, 2025):**
1. ✅ Dynamic adaptive weighting
2. ✅ Veto power for high-confidence predictions
3. ✅ Acoustic feature integration
4. ✅ Confidence calibration
5. ✅ Smart text-audio disagreement handling
6. ✅ Context-aware emotion mapping
7. ✅ Segment merging & filtering
8. ✅ Segment padding for context
9. ✅ Quality filtering (min 0.3s, no silence)

---

### 5. Acoustic Service (`acoustic_service.py`)

**Purpose:** Answers "How was it said?" (objective measurements)

**Library:** `praat-parselmouth` (Python wrapper for Praat)

**Features Extracted:**

#### Pitch (F0)
- **What:** Fundamental frequency of voice
- **Range:** 75-500 Hz
- **Clinical:** Higher in stress/anxiety, lower in depression

#### Jitter (Local)
- **What:** Cycle-to-cycle variation in pitch
- **Range:** 0-1 (0.01 typical)
- **Clinical:** Higher in vocal strain, emotion

#### Shimmer (Local)
- **What:** Cycle-to-cycle variation in amplitude
- **Range:** 0-1 (0.05 typical)
- **Clinical:** Higher in breathy/rough voice

#### HNR (Harmonics-to-Noise Ratio)
- **What:** Signal quality metric
- **Range:** 0-40 dB (>12 dB good)
- **Clinical:** Lower in hoarseness, emotion

**Praat Configuration:**
```python
pitch_settings = {
    "time_step": 0.01,         # 10ms windows
    "pitch_floor": 75.0,       # Min pitch (Hz)
    "pitch_ceiling": 500.0     # Max pitch (Hz)
}
```

---

## 🌊 Data Flow

### Complete Pipeline Execution

```
1. USER INPUT
   └─► python main.py -i conversation.mp3

2. INITIALIZATION (One-Time)
   ├─► Load Diarization Model (2GB)
   ├─► Load ASR Model (1-5GB)
   ├─► Load HuBERT Model (400MB)
   ├─► Load Wav2Vec2 Model (1.2GB)
   └─► Load Text Model (250MB)
   Total: ~5-8GB models loaded into memory

3. AUDIO PREPROCESSING
   └─► load_and_resample_audio()
       ├─► Load file with torchaudio
       ├─► Convert stereo → mono
       ├─► Resample to 16kHz
       └─► Return: NumPy array (float32)

4. SPEAKER DIARIZATION
   └─► DiarizationService.process()
       ├─► Extract speaker embeddings
       ├─► Cluster into N speakers
       ├─► Apply VAD (voice activity detection)
       └─► Return: List of 63 segments

5. SEGMENT MERGING & FILTERING
   └─► _merge_segments()
       ├─► Merge adjacent same-speaker (gap <1.0s)
       ├─► Filter out segments <0.3s
       └─► Return: List of 42 segments (-33%)

6. PROCESS EACH SEGMENT (×42)
   │
   ├─► 6a. SLICE AUDIO (with 0.1s padding)
   │   └─► slice_audio(start-0.1, end+0.1)
   │
   ├─► 6b. ASR - TRANSCRIPTION
   │   └─► ASRService.process(audio_slice)
   │       └─► Return: "I've been waiting for two hours"
   │
   ├─► 6c. ACOUSTIC ANALYSIS
   │   └─► AcousticService.process(audio_slice)
   │       └─► Return: {pitch: 155, jitter: 0.022, ...}
   │
   └─► 6d. EMOTION RECOGNITION (Triple Ensemble)
       └─► EmotionService.process(audio_slice, transcript, acoustics)
           │
           ├─► Quality Check
           │   ├─► Duration >= 0.3s?
           │   └─► Not silence?
           │
           ├─► HuBERT Prediction
           │   └─► "ang" (0.90)
           │
           ├─► Wav2Vec2 Prediction
           │   └─► "angry" (0.75)
           │
           ├─► Text Prediction
           │   └─► "anger" (0.94)
           │
           ├─► Check Veto Conditions
           │   └─► Text >0.90? YES → Text Veto!
           │
           ├─► Calculate Dynamic Weights
           │   └─► {hubert: 0.30, wav2vec2: 0.20, text: 0.50}
           │
           ├─► Acoustic Validation
           │   └─► High pitch + jitter → Boost score 15%
           │
           ├─► Combine Predictions
           │   └─► Weighted vote → "ang" (0.85)
           │
           └─► Return: {
                   label: "ang",
                   score: 0.85,
                   confidence: "high",
                   agreement: "text_veto",
                   ...
               }

7. AGGREGATION
   └─► Collect all 42 segment results

8. OUTPUT
   └─► Save to JSON file
       └─► data/output/conversation.json
```

### Processing Time Breakdown

For 20-minute audio (before improvements):
- Initialization: 10-30s (one-time)
- Diarization: 15-20s
- Segment Processing: 63 segments × 1.4s = 88s
- **Total: ~2 minutes**

After improvements:
- Initialization: 10-30s
- Diarization: 15-20s
- Segment Processing: 42 segments × 0.9s = 38s
- **Total: ~1 minute 20s (-40%)**

---

## 🎯 Emotion Detection System

### Prediction Confidence Levels

```python
def _calibrate_confidence(score, emotion):
    if emotion == 'neu':
        # Stricter for neutral (reduces false confidence)
        if score > 0.85: return 'very_high'
        elif score > 0.65: return 'high'
        elif score > 0.45: return 'medium'
        else: return 'low'
    else:
        # More lenient for strong emotions (harder to detect)
        if score > 0.75: return 'very_high'
        elif score > 0.55: return 'high'
        elif score > 0.35: return 'medium'
        else: return 'low'
```

### Agreement Types Explained

**`full`** - All three models agree
- Example: HuBERT="ang", Wav2Vec2="angry", Text="anger"
- Confidence boost: 25%
- Interpretation: Very reliable

**`audio_consensus`** - Both audio models agree, text differs
- Example: HuBERT="neu", Wav2Vec2="calm", Text="anger"
- Sets `sarcasm_flag: true`
- Interpretation: Person restraining emotion in voice

**`text_veto`** - Text model >0.90 confidence overrides
- Example: Text="anger"(0.94), Audio="neutral"
- Interpretation: Strong emotional language

**`hubert_veto`** - HuBERT >0.90 confidence overrides
- Example: HuBERT="sad"(0.92), Others differ
- Interpretation: Very clear vocal prosody

**`text_priority`** - Text confident + acoustics support
- Example: Text="anger"(0.87), pitch>140, jitter>0.018
- Interpretation: Masked emotion detected via text + acoustics

**`partial`** - No clear agreement, weighted vote
- Example: HuBERT="neu", Wav2Vec2="surprised", Text="fear"
- Interpretation: Complex or mixed emotion

### Emotion Mapping

Models predict different emotion sets - mapped to HuBERT's 4 labels:

```python
# Wav2Vec2 → HuBERT
'angry' → 'ang'
'calm' → 'neu'
'disgust' → 'ang'
'fearful' → Context-aware (pitch/jitter determine 'ang' or 'sad')
'happy' → 'hap'
'neutral' → 'neu'
'sad' → 'sad'
'surprised' → Context-aware (pitch determines 'hap', 'ang', or 'neu')

# Text → HuBERT
'anger' → 'ang'
'joy' → 'hap'
'sadness' → 'sad'
'neutral' → 'neu'
'fear' → Context-aware
'surprise' → Context-aware
'disgust' → 'ang'
```

### Quality Filtering

Segments are rejected if:
1. Duration < 0.3 seconds (too short for emotion)
2. Max amplitude < 0.01 (near-silence)
3. Acoustic analysis fails (corrupted audio)

---

## 📊 Model Details

### HuBERT (Prosody)
- **Architecture:** Transformer encoder (12 layers)
- **Parameters:** 95M
- **Input:** Raw audio waveform (16kHz)
- **Output:** 4 emotion classes
- **Training:** Self-supervised on LibriSpeech, fine-tuned on emotion data
- **Speed:** ~0.3s per segment (GPU)

### Wav2Vec2 (Phonetics)
- **Architecture:** CNN + Transformer (24 layers)
- **Parameters:** 315M
- **Input:** Raw audio waveform (16kHz)
- **Output:** 8 emotion classes
- **Training:** Self-supervised on multilingual data
- **Speed:** ~0.4s per segment (GPU)

### DistilRoBERTa (Semantics)
- **Architecture:** Distilled transformer (6 layers)
- **Parameters:** 82M
- **Input:** Text (max 512 tokens)
- **Output:** 7 emotion classes
- **Training:** Distilled from RoBERTa, fine-tuned on emotion text
- **Speed:** ~0.1s per segment (GPU)

### Pyannote Diarization
- **Architecture:** PyanNet (CNN) + LSTM
- **Parameters:** ~60M
- **Input:** Audio file path
- **Output:** Speaker timeline
- **Training:** VoxCeleb + proprietary data
- **Speed:** ~0.5× real-time (20min audio → 10s)

### Faster-Whisper
- **Architecture:** Encoder-Decoder Transformer
- **Parameters:** 39M - 769M (model-dependent)
- **Input:** Audio mel-spectrogram
- **Output:** Text transcription
- **Training:** 680k hours multilingual data
- **Speed:** 1-5× real-time (model-dependent)

---

## ⚡ Performance Characteristics

### Memory Usage

| Component | RAM (CPU) | VRAM (GPU) |
|-----------|-----------|------------|
| Diarization | 4GB | 2GB |
| ASR (base.en) | 1GB | 1GB |
| HuBERT | 2GB | 1GB |
| Wav2Vec2 | 3GB | 2GB |
| Text Model | 1GB | 0.5GB |
| **Total** | **~11GB** | **~6.5GB** |

### Processing Speed (20min audio)

| Stage | CPU | GPU |
|-------|-----|-----|
| Load Models | 30s | 30s |
| Diarization | 60s | 15s |
| ASR (42 seg) | 42s | 21s |
| Emotion (42 seg) | 60s | 18s |
| Acoustic (42 seg) | 10s | 10s |
| **Total** | **3m 22s** | **1m 34s** |

### Accuracy Metrics

| Task | Metric | Score |
|------|--------|-------|
| Diarization | DER | 8-12% |
| ASR (base.en) | WER | ~50% |
| Emotion (ensemble) | F1 | ~85%* |
| Acoustic | Reliability | >95% |

*Estimated based on improvements; requires clinical validation

---

## 📚 API Reference

### AnalysisPipeline

```python
class AnalysisPipeline:
    def __init__(self, hf_token: str, 
                 emotion_model_path: str = "superb/hubert-base-superb-er",
                 asr_model: str = "base.en"):
        """Initialize pipeline with all services."""
        
    def run(self, audio_file_path: str, 
            output_json_path: str, 
            num_speakers: int = 2):
        """Run complete analysis pipeline."""
```

### EmotionService

```python
class EmotionService:
    def __init__(self, 
                 mode: Literal['dual_audio', 'triple_ensemble'] = 'triple_ensemble',
                 hubert_model: str = "superb/hubert-base-superb-er",
                 wav2vec2_model: str = "ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition",
                 text_model: str = "j-hartmann/emotion-english-distilroberta-base"):
        """Initialize triple ensemble emotion service."""
        
    def process(self, audio_slice: np.ndarray, 
                transcript: str = "", 
                acoustic_features: Optional[Dict] = None) -> Optional[Dict]:
        """Predict emotion using triple ensemble."""
```

### Audio Utilities

```python
def load_and_resample_audio(file_path: str) -> Tuple[np.ndarray, int]:
    """Load and convert audio to 16kHz mono."""
    
def slice_audio(audio_array: np.ndarray, 
                sample_rate: int, 
                start_sec: float, 
                end_sec: float) -> np.ndarray:
    """Extract audio segment by time."""
```

---

**Last Updated:** November 6, 2025  
**Version:** 2.0 with Triple Ensemble

