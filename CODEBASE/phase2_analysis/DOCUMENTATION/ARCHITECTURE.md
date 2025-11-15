# CCAE Phase 2 — Architecture

_Last updated: 15 Nov 2025_

This document describes the software architecture for the Clinical Communication Analysis Engine (CCAE) Phase 2 feedback pipeline. It complements `README.md` (usage) and `DOCUMENTATION/phase2_official_documentation.md` (single source of truth) with a deep dive into module boundaries, data contracts, configuration, and operational concerns.

---

## 1. System Overview
The pipeline transforms a Phase 1 `conversation.json` transcript into a clinician-facing Markdown report entirely on-device.

```
conversation.json
      │
      ▼
┌───────────────────────┐
│ Module 1: Speaker Role│──▶ speaker_map.json
└──────────┬────────────┘
           │
           ▼
┌───────────────────────┐
│ Module 2: Dynamics    │──▶ dynamics.json
└──────────┬────────────┘
           │
           ▼
┌───────────────────────┐
│ Module 3: Behaviors   │──▶ behaviors.json
└──────────┬────────────┘
           │
           ▼
┌───────────────────────┐
│ Module 4: Key Moments │──▶ key_moments.json
└──────────┬────────────┘
           │
           ▼
┌───────────────────────┐
│ Module 5: Feedback    │──▶ feedback_report_<stem>.md
└───────────────────────┘
```

- **Local-first:** All analytics, HF inference, and LLM prompts execute on the workstation (Ollama + Hugging Face local cache).
- **Hybrid stack:** Deterministic Python handles aggregations, a compact transformer handles turn-level behaviors, and local LLMs take on sparse reasoning-heavy tasks (role identification, key moments, narrative feedback).
- **Composable modules:** Each stage reads and writes JSON files, enabling caching, targeted retries, and isolated testing.

---

## 2. Module Breakdown

| Module | Location | Tech | Primary Input | Output | Notes |
|--------|----------|------|---------------|--------|-------|
| SpeakerRoleClassifier | `modules/speaker_classifier.py` | Ollama `llama3:8b` | First 10–15 turns of transcript | `speaker_map.json` | JSON-only prompt with manual override support (`--clinician`). |
| ConversationalDynamicsAnalyzer | `modules/dynamics_analyzer.py` | Pure Python/pandas | Full transcript + speaker map | `dynamics.json` | Deterministic metrics (talk ratios, pauses, interruptions, turn stats). |
| BehaviorClassifier | `modules/behavior_classifier.py` | DistilBERT (HF) | Clinician turns, label schema, thresholds | `behaviors.json` | Multi-label inference (Encounter, VRM, Empathy, Risk, Event tags). |
| KeyMomentAnalyzer | `modules/key_moment_analyzer.py` | Ollama `llama3:8b`/`mistral-nemo` | Trigger windows around `Event:*` tags | `key_moments.json` | SPIKES implemented; Teach-Back + SDM prompts upcoming. |
| FeedbackGenerator | `modules/feedback_generator.py` | Ollama `mistral-nemo` | Aggregated JSON payload (meta, dynamics, behaviors, key moments) | `feedback_report_<stem>.md` | Enforces empathetic Markdown template with citations. |

### 2.1 Speaker Role Classifier
- **Prompt:** `prompts/speaker_role_prompt.txt` instructs the LLM to emit JSON containing clinician/patient IDs, confidence, and rationale.
- **Fallbacks:** CLI override (`--clinician`), heuristic fallback when Ollama is unavailable (used by `--dry-run`).
- **Contract:** 
  ```json
  {
    "clinician": "SPEAKER_01",
    "patient": "SPEAKER_00",
    "confidence": "high",
    "rationale": "..."
  }
  ```

### 2.2 Conversational Dynamics Analyzer
- Converts ordered segments into a pandas DataFrame.
- Computes talk ratios, pauses, interruptions, and per-speaker turn-length statistics.
- Optional hooks exist for aggregating Phase 1 acoustic/emotion metadata for future UX.

### 2.3 Behavior Classifier
- Loads tokenizer, model, `label_schema.json`, and optional `thresholds.json` from `models/ccae-behavior-classifier-v{n}/`.
- For each clinician segment:
  1. Tokenize (max length 256).
  2. Run forward pass on DistilBERT (multi-label head).
  3. Apply sigmoid + per-label thresholds.
  4. Emit `BehaviorTag` list with confidences.
- Maintains compatibility with `--dry-run` by falling back to deterministic heuristics when weights are missing (until v1 ships).

### 2.4 Key Moment Analyzer
- Consumes `Event:*` and empathy tags to select focus windows (±3 turns).
- Uses prompt templates:
  - `prompts/key_moment_prompt.txt` (SPIKES)
  - Planned: `prompts/teach_back_prompt.txt`, `prompts/sdm_prompt.txt`
- Outputs a consolidated `key_moments.json` structure with framework scores, summaries, and supporting quotes.
- Guardrails: configurable max windows per run, automatic skip in `--dry-run` mode, CLI toggles for future frameworks.

### 2.5 Feedback Generator
- Builds a structured payload:
  ```json
  {
    "conversation_meta": {...},
    "speaker_map": {...},
    "dynamics": {...},
    "behaviors": [...],
    "key_moments": {...}
  }
  ```
- Prompt (`prompts/feedback_prompt.txt`) enforces:
  - Markdown sections: Summary Dashboard, What Went Well, Opportunities for Growth, Key Moments, Next Visit Checklist.
  - Tone: kind, specific, timestamp references `[mm:ss]`.
- Provides deterministic fallback messaging when Ollama is unavailable (ensuring CI/dev flows keep running).

---

## 3. Data Contracts

| Artifact | Location | Producer | Consumer(s) | Key Fields |
|----------|----------|----------|-------------|------------|
| `conversation.json` | Phase 1 output | Phase 1 pipeline | All modules | `segments[]` with `segment_id`, `speaker`, `start_time`, `end_time`, `duration`, `transcript`, optional acoustics. |
| `speaker_map.json` | `data/outputs/<stem>/` | Module 1 | Modules 2–5 | Clinician/patient mapping, confidence, rationale, overrides metadata. |
| `dynamics.json` | same | Module 2 | Modules 4–5 | Talk ratios, pause stats, interruption counts, per-speaker turn metrics. |
| `behaviors.json` | same | Module 3 | Modules 4–5 | Array of per-segment tags with confidences, timestamps, transcripts. |
| `key_moments.json` | same | Module 4 | Module 5 | Sectioned framework scores and annotated quotes. |
| `feedback_report_<stem>.md` | same | Module 5 | End user | Markdown report referencing upstream metrics. |
| `report_metadata.json` (recommended) | same | Orchestrator | Ops tooling | Git SHA, model versions, timestamps, hardware info. |

All JSON payloads are validated with shared Pydantic models in `modules/data_models.py`, ensuring schema drift is caught early.

---

## 4. Configuration & Environment

### 4.1 Model Configuration (`config/models.example.yaml`)
- Defines default paths for classifier checkpoints, prompt IDs, Ollama model names, batch sizes, and hardware settings (CPU vs GPU).
- Users can provide a custom file via `--models-config` or set environment variables for ad hoc overrides.

### 4.2 Execution Flags (`run_feedback.py`)
- `--input` (required): absolute path to Phase 1 transcript.
- `--output-dir`: base folder for artifacts (`data/outputs` by default).
- `--clinician SPEAKER_XY`: manual override for Module 1.
- `--models-config PATH`: alternate YAML config.
- `--skip-key-moments`: bypass Module 4.
- `--dry-run`: skip Ollama/HF calls, inject deterministic placeholders (for CI/onboarding).

### 4.3 Dependencies
- **Ollama:** `llama3:8b` for Modules 1 & 4, `mistral-nemo` (or `llama3:8b-instruct`) for Module 5.
- **Hugging Face:** DistilBERT-based classifier stored locally under `models/`.
- **Python packages:** pinned in `requirements.txt`, aligned with the Phase 1 environment to allow shared virtualenvs.

---

## 5. Orchestration & Control Flow

1. **Validation:** `run_feedback.py` loads `conversation.json`, validates against Pydantic models, and resolves CLI/config overrides.
2. **Module Execution:** Modules run sequentially with clear logging and progress bars (Rich). Each module can short-circuit if artifacts already exist and caching is permitted.
3. **Error Handling:** Module-specific exceptions bubble to the orchestrator, which:
   - Logs the failure.
   - Annotates downstream outputs (e.g., feedback report notes if key-moment analysis was skipped).
   - Continues when safe (e.g., missing Module 4 results still allow Module 5 to run without that section).
4. **Artifacts:** Each run creates `data/outputs/<stem>/` containing JSON intermediates, the Markdown report, and (optionally) `report_metadata.json`.

---

## 6. Observability & Automation

- **Logging:** Structured (JSON) logs capture module timings, model versions, prompt IDs, and hardware info for audits.
- **Progress UI:** Rich renders per-module status with success/failure annotations to aid clinicians and developers monitoring long runs.
- **Watcher (planned):** `watcher.py` will monitor a Phase 1 output directory (via `watchdog`) and automatically invoke the pipeline when new transcripts appear, moving processed files to `data/processed/`.
- **Metadata:** Persisting `report_metadata.json` alongside outputs enables downstream dashboards and simplifies compliance reviews.

---

## 7. Roadmap Highlights
- **Classifier v1:** Finish Milestone 1 from the Improvement Plan to replace heuristics with the fine-tuned DistilBERT checkpoint.
- **Testing:** Stand up `pytest` suites (unit, mocked integration, and smoke) before expanding functionality.
- **Key-moment coverage:** Add Teach-Back and Shared Decision Making prompts + toggles.
- **Labeling workflow:** Build `tools/bootstrap_labels.py`, `tools/label_data.py`, and version-aware `train_classifier.py`.
- **Automation hooks:** Deliver the watcher daemon for hands-free operation.
- **Documentation:** Keep `README.md`, `ARCHITECTURE.md`, `DOCUMENTATION/phase2_official_documentation.md`, and `DOCUMENTATION/IMPROVEMENT_PLAN.md` in sync as functionality evolves.

---

For implementation specifics, refer to:
- `DOCUMENTATION/phase2_official_documentation.md` — canonical blueprint + build notes.
- `DOCUMENTATION/IMPROVEMENT_PLAN.md` — milestone-level execution plan.
- Source modules under `modules/` for code-level details.

