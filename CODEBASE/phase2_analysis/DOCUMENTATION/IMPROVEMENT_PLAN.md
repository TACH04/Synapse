# CCAE Phase 2 — Improvement Plan

_Last updated: 15 Nov 2025_

This plan enumerates the remaining work required to move the Phase 2 feedback pipeline from a functional prototype to a robust, feature-complete, and maintainable product. Tasks are grouped into six milestones, prioritized by impact and dependency.

1. **Milestone 1:** Ship the real classifier (core functionality)
2. **Milestone 2:** Establish testing & CI harness (stability)
3. **Milestone 3:** Expand key-moment analysis (new features)
4. **Milestone 4:** Build the training & labeling workflow (long-term improvement)
5. **Milestone 5:** Implement automation hooks (usability)
6. **Milestone 6:** Documentation cleanup (maintenance)

---

## Milestone 1 — Ship the Real Classifier (v1)
**Goal:** Replace the keyword-based heuristics in `modules/behavior_classifier.py` with a fine-tuned DistilBERT model. This is the highest-priority milestone and the core of the hybrid-AI stack.

### 1.1 Define Labeling Schema
- Finalize the multi-label schema, covering:
  - `Encounter:Introduction`, `Encounter:AgendaSetting`, `Encounter:Closing`
  - `VRM:Reflection`, `VRM:Advisement`, `VRM:Question_Open`, `VRM:Question_Closed`
  - `Empathy:Opportunity_Acknowledged`, `Empathy:Opportunity_Missed`
  - `Flag:Jargon_Used`
  - `Event:Possible_Bad_News` (additional `Event:*` tags added later)
- Output a canonical `label_schema.json`.

### 1.2 Bootstrap Dataset (Human-in-the-Loop)
- Create `tools/bootstrap_labels.py`:
  1. Scan a directory of `conversation.json` files (e.g., `data/transcripts/`).
  2. Extract all clinician segments.
  3. Call `ollama.chat(model="llama3:8b")` with a structured prompt to zero-shot tag each segment using `label_schema.json`.
  4. Write `data/training/bootstrapped_data.csv` with columns `segment_id`, `text`, `predicted_labels` (JSON string).

### 1.3 Human Correction
- Manual step: subject matter expert reviews `bootstrapped_data.csv` and saves the corrected results as `data/training/corrected_data.csv`.
- Editors adjust only the `predicted_labels` column, keeping transcript text intact.

### 1.4 Create Training Script
- Implement `train_classifier.py`:
  1. Load `corrected_data.csv` via pandas.
  2. Convert label strings into one-hot vectors using `sklearn.preprocessing.MultiLabelBinarizer`.
  3. Initialize tokenizer/model:
     ```python
     tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
     model = AutoModelForSequenceClassification.from_pretrained(
         "distilbert-base-uncased",
         num_labels=len(binarizer.classes_),
         problem_type="multi_label_classification",
     )
     ```
  4. Build a custom PyTorch `Dataset` that returns `input_ids`, `attention_mask`, and `labels`.
  5. Fine-tune with `transformers.Trainer`.
  6. Save artifacts to `models/ccae-behavior-classifier-v1/`: model weights, tokenizer, and `label_schema.json`.

### 1.5 Integrate Model into Pipeline
- Update `modules/behavior_classifier.py`:
  - Read model path from `config/models.yaml` (e.g., `models/ccae-behavior-classifier-v1/`).
  - Load tokenizer/model/schema from disk.
  - Remove heuristic fallbacks in the main loop.
  - Replace with: tokenize -> run forward pass -> apply sigmoid -> threshold -> map indices to label strings -> emit `BehaviorAnalysis` with `source="model"`.

---

## Milestone 2 — Establish Testing & CI Harness
**Goal:** Build a `pytest` suite to lock in current behavior and prevent regressions before adding new features.

### 2.1 Test Bed Setup
- Install `pytest` and `pytest-mock`, create `tests/` with `__init__.py`.

### 2.2 Pure Logic Unit Tests
- `tests/test_dynamics_analyzer.py`:
  - Build a mock `conversation.json` dict + speaker map.
  - Assert `patient_talk_ratio`, `interruption_count`, `avg_pause_sec`, and `turn_stats` calculations.

### 2.3 Mocked AI Module Tests
- `tests/test_speaker_classifier.py`: mock `ollama.chat` to return known JSON and verify parsing.
- `tests/test_behavior_classifier.py`: mock `transformers.AutoModel.from_pretrained` and the forward call to emit deterministic logits; verify sigmoid/threshold → label mapping.
- `tests/test_key_moment_analyzer.py`: mock `ollama.chat` JSON responses for SPIKES (and future frameworks) and assert parser behavior.

### 2.4 Pipeline Smoke Test
- `tests/test_run_feedback.py`:
  1. Place a 5–10 segment fixture under `tests/fixtures/test_convo.json`.
  2. Invoke `python run_feedback.py --input tests/fixtures/test_convo.json`.
  3. Assert return code 0 and the creation of `feedback_report_test_convo.md`.
  4. Mark as `@pytest.mark.slow` since it exercises real AI calls.

---

## Milestone 3 — Expand Key-Moment Analysis
**Goal:** Support Teach-Back and Shared Decision Making (SDM) in Module 4 and surface them in Module 5.

### 3.1 Update Classifier Schema
- Add `Event:TeachBack_Attempt` and `Event:SharedDecisionMaking_Start` to the schema.
- Label corresponding examples in `corrected_data.csv`.
- Retrain to produce `models/ccae-behavior-classifier-v2/` and update `config/models.yaml`.

### 3.2 Author New Prompts
- `prompts/teach_back_prompt.txt`: Ask–Tell–Ask scoring (JSON output: `ask1`, `tell`, `ask2`, `summary`).
- `prompts/sdm_prompt.txt`: THREE-TALK scoring (JSON output: `team_talk`, `option_talk`, `decision_talk`, `summary`).

### 3.3 Extend Module 4 Logic
- Iterate over all `Event:*` tags emitted by Module 3.
- Use `match`/`if` statements to select the correct prompt/model combo for SPIKES, Teach-Back, and SDM.
- Consolidate results under a single `key_moments.json` with keys like `"spikes"`, `"teach_back"`, `"sdm"`.

### 3.4 Update Module 5 & CLI Toggles
- Teach Module 5 to conditionally include new key-moment sections when data exists.
- In `run_feedback.py`, add optional flags (e.g., `--run-teach-back`, `--run-sdm`) to control heavier analyses.

---

## Milestone 4 — Build the Training & Labeling Workflow
**Goal:** Provide a repeatable process for collecting human corrections and shipping new classifier versions.

### 4.1 Command-Line Labeling UI
- Implement `tools/label_data.py`:
  1. Scan `data/needs_labeling/` for new transcripts.
  2. Pre-label clinician turns with the current best model.
  3. Present each segment:
     ```
     Text: "So, the results of the scan..."
     Model Labels: [Event:Possible_Bad_News]
     Your correction (comma-separated, ENTER to accept):
     ```
  4. Accept Enter as confirmation, or take comma-separated overrides.
  5. Append reviewed entries to `data/training/corrected_data.csv`.

### 4.2 Versioned Training
- Extend `train_classifier.py` with `--version` flag.
- Save outputs into `models/ccae-behavior-classifier-v{n}/`, enabling semantic versioning as data grows.

---

## Milestone 5 — Implement Automation Hooks
**Goal:** Enable “hands-free” execution when new Phase 1 transcripts appear.

### 5.1 Dependencies
- Add `watchdog` to `requirements.txt`.

### 5.2 Watcher Daemon
- Create `watcher.py`:
  1. CLI accepts `--watch-dir`.
  2. Use `watchdog.FileSystemEventHandler` to watch new files.
  3. On `on_created`:
     - Ignore non-`.json` files.
     - Debounce with `time.sleep(5)` to ensure writes finish.
     - Log detection and call `subprocess.run(["python", "run_feedback.py", "--input", event.src_path])`.
     - Wrap calls in `try/except` for resilience.
     - Move processed transcripts to `data/processed/`.

---

## Milestone 6 — Documentation Cleanup
**Goal:** Consolidate design rationale so future contributors understand the “why” without jumping between legacy files.

### 6.1 Restore Historical Context
- Recover the content from:
  - `DOCUMENTATION/Feedback Report/phase2_pipeline_blueprint.md`
  - `DOCUMENTATION/Feedback Report/phase2_build_notes.md`

### 6.2 Merge Into README
- Update `README.md` (or `readme.txt`, if maintained) to include:
  1. **Core Philosophy:** Local-first, hybrid-AI rationale.
  2. **Architecture Rationale:** Explain why each module uses its current tooling.
  3. **Training Section:** Reference `tools/label_data.py` and the versioned classifier workflow.

### 6.3 De-duplicate Legacy Notes
- After merging valuable content, remove outdated blueprint/notes to keep `DOCUMENTATION/phase2_official_documentation.md` and `README.md` as the sources of truth.

---

_For additional technical depth, see `DOCUMENTATION/phase2_official_documentation.md` and `ARCHITECTURE.md`._

