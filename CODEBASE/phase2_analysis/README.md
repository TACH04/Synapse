# Clinical Communication Analysis Engine — Phase 2

CCAE Phase 2 turns Phase 1 `conversation.json` transcripts into clinician-ready coaching reports on a single workstation. The pipeline blends deterministic analytics, a fine-tuned Hugging Face classifier, and local LLMs (via Ollama) so protected health information never leaves the device.

## Capabilities
- **Speaker role inference** — map diarized IDs to clinician/patient via a lightweight LLM prompt.
- **Conversational dynamics** — compute talk ratios, pauses, interruptions, and turn statistics.
- **Behavior tagging** — (soon) multi-label DistilBERT classifier for clinician behaviors, empathy, and risk flags.
- **Key-moment scoring** — SPIKES (and future Teach-Back / SDM) scoring windows powered by structured prompts.
- **Feedback synthesis** — empathetic Markdown report citing timestamps and transcript snippets.

## Requirements
### Hardware
- 16 GB RAM minimum (32 GB recommended).
- Apple Silicon (M1 Pro/M2/M3) or NVIDIA GPU ≥8 GB VRAM.
- ~20 GB free disk for Ollama models plus ≤1 GB for HF checkpoints/artifacts.

### Software
- macOS 13+ or Ubuntu 22+.
- Python 3.10+ and `venv`.
- Ollama server with cached models:
  ```bash
  ollama pull llama3:8b
  ollama pull mistral-nemo    # or llama3:8b-instruct
  ```
- Python dependencies (`requirements.txt`): `torch`, `transformers`, `pandas`, `scikit-learn`, `typer`, `pydantic`, `orjson`, `ollama`, `rich`, `pyyaml`.

## Quick Start
```bash
cd /Users/tannerhochberg/Desktop/Synapse/CODEBASE/phase2_analysis
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Cache local LLMs
ollama pull llama3:8b
ollama pull mistral-nemo

# (Optional) copy your fine-tuned classifier
# cp -R /path/to/ccae-behavior-classifier-v1 ./models/

python run_feedback.py \
  --input ../Audio\ Analysis\ Pipeline/data/output/test_audio2.json
```

Outputs land in `data/outputs/<conversation-stem>/` alongside `feedback_report_<stem>.md`.

## Repository Layout
```
phase2_analysis/
  config/                  # Model + prompt overrides (see models.example.yaml)
  data/
    outputs/               # Generated artifacts per conversation
    samples/               # Optional transcripts for testing/demos
  models/                  # Hugging Face classifiers (ccae-behavior-classifier-v{n})
  modules/                 # Pipeline stages + shared data models
  prompts/                 # Speaker, key-moment, and report prompt templates
  DOCUMENTATION/           # Official docs + improvement plan
  run_feedback.py          # Typer CLI orchestrator
  requirements.txt
```

## Pipeline at a Glance
| Stage | Module | Tooling | Artifact |
|-------|--------|---------|----------|
| 1 | `SpeakerRoleClassifier` | Ollama `llama3:8b` | `speaker_map.json` |
| 2 | `ConversationalDynamicsAnalyzer` | Pure Python/pandas | `dynamics.json` |
| 3 | `BehaviorClassifier` | DistilBERT (HF) | `behaviors.json` |
| 4 | `KeyMomentAnalyzer` | Ollama (`llama3:8b` / `mistral-nemo`) | `key_moments.json` (SPIKES, Teach-Back, SDM) |
| 5 | `FeedbackGenerator` | Ollama `mistral-nemo` | `feedback_report_<stem>.md` |

Each module can be toggled or dry-run via CLI flags (`--skip-key-moments`, `--dry-run`, `--clinician SPEAKER_01`, etc.).

## Running the Pipeline
```bash
python run_feedback.py \
  --input /absolute/path/to/conversation.json \
  --output-dir /Users/.../phase2_analysis/data/outputs \
  [--clinician SPEAKER_01] \
  [--models-config ./config/models.yaml] \
  [--skip-key-moments] \
  [--dry-run]
```

The CLI validates the transcript schema, runs modules sequentially with caching, and logs structured progress with Rich.

## Behavior Classifier Weights
- Place the fine-tuned checkpoint under `models/ccae-behavior-classifier-v{n}/` with:
  ```
  config.json
  pytorch_model.bin
  tokenizer.json
  tokenizer_config.json
  vocab.txt
  label_schema.json
  thresholds.json   # optional per-label calibration
  ```
- Configure the active model in `config/models.yaml` or via CLI overrides.
- Training and labeling workflows are captured in `DOCUMENTATION/IMPROVEMENT_PLAN.md`.

## Development & Testing
- **Unit tests:** (WIP) `pytest` + `pytest-mock` for deterministic modules and mocked LLM/HF calls.
- **Smoke tests:** `python run_feedback.py --input data/samples/test_audio2.json --dry-run`.
- **Behavior classifier training:** See `tools/bootstrap_labels.py`, `tools/label_data.py`, and `train_classifier.py` plan in the improvement document.
- **Automation hooks:** Upcoming `watcher.py` monitors Phase 1 output folders and triggers the pipeline automatically.

## Additional Documentation
- `DOCUMENTATION/phase2_official_documentation.md` — consolidated system reference.
- `DOCUMENTATION/IMPROVEMENT_PLAN.md` — milestone-level roadmap.
- `ARCHITECTURE.md` — data flows, module contracts, and configuration deep dive.

Questions or contributions? Start with these docs, then open an issue/PR with context tied to the relevant milestone.
