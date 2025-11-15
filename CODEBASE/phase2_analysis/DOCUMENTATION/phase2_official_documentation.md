# Clinical Communication Analysis Engine (CCAE) — Phase 2 Official Documentation

_Last updated: 15 Nov 2025_

This document consolidates the blueprint, build notes, development plan, and product briefs that currently live under `DOCUMENTATION/Feedback Report*/`. It is the authoritative reference for the Phase 2 feedback pipeline that transforms Phase 1 `conversation.json` transcripts into clinician-ready `feedback_report.md` files entirely on-device.

---

## 1. Executive Summary
- **Mission**: Provide privacy-preserving, empathetic, and actionable coaching for clinicians by analyzing recorded encounters locally.
- **Scope**: Consume Phase 1 artifacts, produce Markdown feedback plus structured intermediates (`speaker_map.json`, `dynamics.json`, `behaviors.json`, `key_events.json` / `spikes_analysis.json`).
- **Architecture**: Five sequential modules combining deterministic analytics, a fine-tuned Hugging Face classifier, and local LLMs served through Ollama.
- **Deliverable**: `run_feedback.py` CLI that orchestrates the modules, persists artifacts under `data/outputs/<conversation-stem>/`, and emits a clinician-facing report.

---

## 2. Guiding Principles
1. **Local-first**: All computation, model weights, and data remain on the clinician’s machine to satisfy privacy mandates.
2. **Hybrid-AI stack**: Use deterministic math for high-frequency metrics, a compact transformer for turn-level tagging, and local LLMs for sparse reasoning-heavy tasks.
3. **Actionable empathy**: Reports must highlight strengths, growth areas, and cite concrete timestamps/snippets in a kind tone.
4. **Composable modules**: Each module reads/writes JSON, making it individually testable, swappable, and auditable.

---

## 3. System Requirements & Dependencies
### Hardware
- RAM: 16 GB minimum (32 GB recommended).
- GPU: Apple Silicon (M1 Pro/M2/M3) or NVIDIA GPU with ≥8 GB VRAM.
- Storage: ~20 GB to cache local LLM checkpoints plus up to 1 GB for HF model weights and artifacts.

### Software Stack
- macOS 13+/Ubuntu 22+ (tested on macOS 15).
- Python 3.10+ with `venv`.
- `requirements.txt` (key packages): `torch`, `transformers`, `scikit-learn`, `pandas`, `typer`, `pydantic`, `orjson`, `ollama`, `rich`, `pyyaml`.
- Ollama daemon running locally with cached models:
  - `ollama pull llama3:8b`
  - `ollama pull mistral-nemo` (or `llama3:8b-instruct`)
- Local Hugging Face cache containing the fine-tuned behavior classifier at `models/ccae-behavior-classifier-v1/`.

---

## 4. Repository Layout (Phase 2)
```
phase2_analysis/
  run_feedback.py            # Typer CLI orchestrator
  requirements.txt
  README.md, DOCUMENTATION/  # User + engineering docs
  config/
    models.example.yaml      # Override paths, batch sizes, model ids
  data/
    samples/                 # (Optional) transcripts for testing
    outputs/<run>/           # Per-run artifacts & final report
  models/
    ccae-behavior-classifier-v1/  # DistilBERT checkpoint + metadata
  modules/
    __init__.py
    speaker_classifier.py
    dynamics_analyzer.py
    behavior_classifier.py
    key_moment_analyzer.py
    feedback_generator.py
    data_models.py
  prompts/
    speaker_role_prompt.txt
    key_moment_prompt.txt
    feedback_prompt.txt
```

---

## 5. Data Contracts
### 5.1 Input (`conversation.json`)
- **Source**: Phase 1 Audio Analysis Pipeline.
- **Fields consumed**: `segments` (ordered), each with `segment_id`, `speaker` (`SPEAKER_00`, `SPEAKER_01`, ...), `start_time`, `end_time`, `duration`, `transcript`. Acoustic and emotion metadata are passed through for future modules.

### 5.2 Intermediate Artifacts
| File | Producer | Contents |
|------|----------|----------|
| `speaker_map.json` | Module 1 | Clinician/patient mapping + confidence + rationale. |
| `dynamics.json` | Module 2 | Talk ratios, pause/turn statistics, interruption counts, optional emotional aggregates. |
| `behaviors.json` | Module 3 | Per-clinician-utterance tags with confidences and timestamps. |
| `key_events.json` / `spikes_analysis.json` | Module 4 | Structured scores for frameworks such as SPIKES, Teach-Back, Shared Decision Making. |

### 5.3 Output (`feedback_report_<stem>.md`)
- Fixed sections: Summary Dashboard, What Went Well, Opportunities for Growth, Key Moments Deep Dive, Next Visit Checklist.
- Tone: Kind, specific, cites timestamps (`[mm:ss]`) and transcripts.
- Metadata footer should cite model versions and execution timestamp.

---

## 6. Pipeline Modules

### 6.1 Module 1 — Speaker Role Classifier (`modules/speaker_classifier.py`)
- **Dependency**: Ollama `llama3:8b`.
- **Logic**: Prompt on the first 10–15 turns (or until both speakers appear), parse JSON response, and persist clinician/patient IDs with confidence/rationale.
- **Fallbacks**: CLI overrides (`--clinician SPEAKER_01`) and deterministic heuristics when confidence is low or Ollama unavailable.

### 6.2 Module 2 — Conversational Dynamics Analyzer (`modules/dynamics_analyzer.py`)
- **Dependency**: Pure Python/pandas.
- **Metrics**: Talk ratios, average/median pause durations, interruption count, mean/median turn lengths per speaker, optional emotion aggregation.
- **Output schema**: Numeric JSON friendly to downstream scoring; includes `turn_stats` block for each speaker.

### 6.3 Module 3 — Behavior Classifier (`modules/behavior_classifier.py`)
- **Dependency**: Fine-tuned DistilBERT or MiniLM checkpoint loaded from `models/ccae-behavior-classifier-v1/`.
- **Label schema** (multi-label): Encounter structure (`Encounter:Introduction`, ...), Verbal Relationship Maintenance (`VRM:*`), Empathy flags, Risk flags (`Flag:Jargon_Used`, `Flag:TeachBack_Attempt`, `Flag:Interrupt`), Event seeds (`Event:Possible_Bad_News`, etc.).
- **Serving plan**: Tokenize each clinician segment (max length 256), run forward pass, apply per-label thresholds (from `thresholds.json`, default 0.4). Emit per-segment tag arrays with confidences.
- **Fallback**: Deterministic heuristics + `--dry-run` path keep pipeline operational without weights.

### 6.4 Module 4 — Key Moment Analyzer (`modules/key_moment_analyzer.py`)
- **Trigger sources**: Behavior tags containing `Event:*` or empathy opportunities.
- **Windowing**: Gather ±3 turns around flagged events for context.
- **Prompting**: Structured prompts (SPIKES example included in `prompts/key_moment_prompt.txt`) executed via Ollama (`format="json"`). Responses include framework scores and annotated quotes.
- **Throughput guardrails**: Default maximum of three windows per run; automatically disabled when `--skip-key-moments` or `--dry-run` is set.

### 6.5 Module 5 — Feedback Generator (`modules/feedback_generator.py`)
- **Inputs**: Aggregated JSON payload containing conversation metadata, dynamics, behaviors, and key events.
- **Prompting**: `prompts/feedback_prompt.txt` enforces tone and Markdown structure; `mistral-nemo` preferred for stylistic control, `llama3:8b-instruct` as fallback.
- **Post-processing**: Validates Markdown sections, inserts timestamp references, and enriches with actionable coaching points even when upstream modules degrade.
- **Graceful degradation**: When LLM unavailable, a deterministic formatter produces a minimal report referencing available metrics.

---

## 7. Orchestration & CLI (`run_feedback.py`)
- Typer-based interface with rich progress indicators per module.
- **Signature**:
  ```
  python run_feedback.py \
    --input /absolute/path/to/conversation.json \
    --output-dir /absolute/path/to/phase2_analysis/data/outputs \
    [--clinician SPEAKER_01] \
    [--models-config /path/to/config/models.yaml] \
    [--skip-key-moments] \
    [--dry-run]
  ```
- **Execution order**: Validate schema via `modules/data_models.py`, run modules 1–5 sequentially with caching, and write artifacts under `data/outputs/<conversation-stem>/`.
- **Error handling**: Module-specific exceptions are caught; the orchestrator logs failures, annotates the report when partial data is used, and continues when safe.
- **Logging**: Structured (JSON) logs plus Rich console spinner bars; all module outputs include metadata describing model versions, prompt ids, and timestamps.

---

## 8. Model & Prompt Management
### 8.1 Behavior Classifier Files (`models/ccae-behavior-classifier-v1/`)
```
config.json
pytorch_model.bin
tokenizer.json
tokenizer_config.json
vocab.txt
labels.json          # Ordered label list used at inference
thresholds.json      # Optional per-label thresholds
model_card.md        # (Recommended) dataset + ethical notes
```

### 8.2 Training Plan (summary)
1. **Data curation**: Aggregate clinician utterances from Phase 1 runs; bootstrap tags with local LLMs and have SMEs correct them.
2. **Training**: Use `DistilBertTokenizerFast`, multi-label `BCEWithLogitsLoss`, 80/10/10 stratified split, optional focal loss for imbalance.
3. **Evaluation**: Track micro/macro F1 per label group and run empathy-specific audits.
4. **Export & versioning**: Save artifacts under semantic folders (`ccae-behavior-classifier-v{n}`) and update CLI defaults accordingly.
5. **Future work**: Add `train_classifier.py` and labeling UI in Phase 3.

### 8.3 Prompt Assets
- `prompts/speaker_role_prompt.txt`: JSON-only classifier for diarized IDs.
- `prompts/key_moment_prompt.txt`: SPIKES template; can be duplicated for Shared Decision Making, Teach-Back, etc.
- `prompts/feedback_prompt.txt`: Defines report sections, tone, and quoting expectations.
- Prompt IDs and model versions should be logged within each artifact to maintain auditability.

---

## 9. Testing, Validation, and QA
- **Unit tests** (planned): Prompt parsing, dynamics math edge cases, classifier data model validation.
- **Integration tests**: Run pipeline against `data/samples/test_audio2.json` with `--dry-run`, snapshotting intermediate files for regression checks.
- **Human-in-the-loop**: SMEs review feedback reports for tone accuracy; compare SPIKES scores to expert rubrics.
- **Operational smoke test**:
  1. `python3 -m venv .venv && source .venv/bin/activate`
  2. `pip install -r requirements.txt`
  3. `python run_feedback.py --input ../Audio\ Analysis\ Pipeline/data/output/test_audio2.json --dry-run`
  4. Inspect `data/outputs/test_audio2/` for JSON + Markdown artifacts.

---

## 10. Observability, UX, and Operations
- Rich-powered progress bars announce each module; CLI clearly labels whether Ollama/HF models are engaged or skipped.
- Intermediate artifacts are intentionally preserved for audits; add `report_metadata.json` (timestamp, git SHA, model versions, hardware) to each run directory for compliance review.
- Optional automation: A Watchdog-style daemon (patterned after `OllamaAnalysis/main.py`) can watch a folder and invoke `run_feedback.py` automatically when new transcripts drop.
- Logging should remain JSON-formatted to simplify ingestion into future monitoring tools.

---

## 11. Roadmap & Known Gaps
1. **Finalize Behavior Classifier v1**: Train, evaluate, and ship `ccae-behavior-classifier-v1` plus `train_classifier.py`.
2. **Prompt coverage**: Extend Key Moment analyzers beyond SPIKES (Teach-Back, Shared Decision Making, Delivering Med Changes).
3. **Testing**: Add pytest suite with mocked Ollama interfaces and deterministic fixture data.
4. **Labeling UX**: Build lightweight UI or spreadsheet workflow to curate classifier training data.
5. **Automation**: Optional background watcher to auto-run pipeline on new Phase 1 outputs.
6. **Documentation**: Incorporate content from `DOCUMENTATION/IMPROVEMENT PLAN.pdf` once an accessible text version is available.

---

## 12. Quick Start (Step-by-Step)
1. **Clone & enter repo**
   ```
   git clone <repo-url>
   cd /Users/tannerhochberg/Desktop/Synapse/CODEBASE/phase2_analysis
   ```
2. **Create environment**
   ```
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Prime local models**
   ```
   ollama pull llama3:8b
   ollama pull mistral-nemo
   ```
4. **Place HF weights**
   ```
   cp -R /path/to/ccae-behavior-classifier-v1 ./models/
   ```
5. **Run pipeline**
   ```
   python run_feedback.py \
     --input ../Audio\ Analysis\ Pipeline/data/output/test_audio2.json
   ```
6. **Review outputs**: `data/outputs/test_audio2/feedback_report_test_audio2.md` plus intermediate JSONs.

---

## 13. Appendices
### A. CLI Flags
| Flag | Description |
|------|-------------|
| `--input PATH` | Absolute path to `conversation.json` (required). |
| `--output-dir PATH` | Base directory for artifacts (default `data/outputs`). |
| `--clinician SPEAKER_XY` | Manual override for clinician speaker ID. |
| `--models-config PATH` | YAML override for model/prompt settings. |
| `--skip-key-moments` | Disable Module 4. |
| `--dry-run` | Skip all Ollama/HF calls and emit heuristic placeholders. |

### B. Artifact Directory Example
```
data/outputs/RES0084/
  speaker_map.json
  dynamics.json
  behaviors.json
  key_events.json          # Optional
  feedback_report_RES0084.md
  report_metadata.json     # Recommended
```

---

For clarifications or contributions, reference this document before editing legacy files under `DOCUMENTATION/Feedback Report*/`. Update this official doc whenever functionality changes so it remains the single source of truth.

