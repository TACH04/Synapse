"""
Phase 2 analysis pipeline modules.

Each module exposes a class with a single public method (`classify`, `analyze`, or
`generate`) so they can be orchestrated by `run_feedback.py` or imported elsewhere.
"""

from . import behavior_classifier, data_models, dynamics_analyzer, feedback_generator, key_moment_analyzer, speaker_classifier  # noqa: F401


