# Copilot instructions for this repo (Synapse)

Focus areas
- Two active apps: `CODEBASE/Audio Analysis Pipeline` (batch JSON analysis) and `conversation_simulator` (Flask + Gemini patient sim).
- Stay inside these directories unless the user calls out DHF docs (read-only reference).

Audio pipeline map
- Entry: `main.py` → `pipeline/analysis_pipeline.py` orchestrates diarization → ASR → acoustics → emotion.
- Services live under `pipeline/services/`; each loads models in `__init__` and exposes a cheap `process(...)` method.
- JSON output shape: `{"file", "segments":[{"segment_id","speaker","start_time","end_time","duration","transcript","predicted_emotion","acoustic_features"}]}` saved to `data/output/`.

Core workflows
- Install deps: `pip install -r CODEBASE/Audio Analysis Pipeline/requirements.txt` (PowerShell).
- Hugging Face token is required for diarization: `$env:HF_TOKEN="<token>"` before running.
- Optional prep: `python CODEBASE/Audio Analysis Pipeline/download_models.py` to cache models; GPU install path is in `USER_GUIDE.md`.
- Run sample: `python CODEBASE/Audio Analysis Pipeline/main.py -i "CODEBASE/Audio Analysis Pipeline/data/input/test_audio2.mp3" --speakers 2 --asr base.en`.

PowerShell command syntax
- User shells are PowerShell; chain commands with `;`, not `&&`.
- Prefer one command per line; if chaining, keep it minimal: `cd <path> ; python main.py ...`.

Pipeline conventions
- `DiarizationService` handles pyannote versions: uses `token=` for v4+, falls back to `use_auth_token=` for v3.x; keep passing raw `HF_TOKEN`.
- Diarization returns `Annotation` on v3 and `DiarizeOutput.speaker_diarization` on v4—guard for both when extending.
- `_merge_segments(...)` in `analysis_pipeline.py` merges same-speaker spans with gap≈1.0s; adjust only if downstream consumers are updated.
- Audio slices add 0.1s padding before ASR/emotion; preserve this when tweaking segment logic.

Conversation simulator quickstart
- `cd conversation_simulator` → copy `.env.example` to `.env` and set `GOOGLE_API_KEY` (optional `GEMINI_MODEL`).
- Launch with `python run.py`, browse at `http://localhost:5000`; without a key it falls back to scripted mock responses.
- `app/conversation_engine.py` maintains history, initial greeting guardrails, and heuristic emotion tags.

Extension tips
- Add new analysis services under `pipeline/services/<name>_service.py`, load models once, and wire calls inside `AnalysisPipeline.run()`.
- Include a smoke test run on `data/input/test_audio2.mp3` after significant changes; results land in `data/output/`.

Safety & secrets
- Never log or commit tokens (`HF_TOKEN`, `GOOGLE_API_KEY`).
- Ignore cached model weights and JSON outputs when committing; keep them out of PRs unless explicitly requested.

