from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import List, Optional, Sequence

import ollama

from .data_models import (
    BehaviorAnalysis,
    BehaviorEntry,
    Conversation,
    KeyEventAnalysis,
    KeyEventReport,
    KeyEventScore,
)

LOGGER = logging.getLogger(__name__)


class KeyMomentAnalyzer:
    """Uses a local LLM to score complex, multi-turn sequences (SPIKES, etc.)."""

    def __init__(
        self,
        prompt_path: Path,
        model_name: str = "llama3:8b",
        window_radius: int = 3,
        max_events: int = 3,
        timeout: int = 180,
        enabled: bool = True,
        trigger_prefixes: Optional[Sequence[str]] = None,
    ) -> None:
        self.prompt_template = prompt_path.read_text(encoding="utf-8")
        self.model_name = model_name
        self.window_radius = window_radius
        self.max_events = max_events
        self.timeout = timeout
        self.enabled = enabled
        self.trigger_prefixes = trigger_prefixes or ("Event:", "Empathy:Opportunity")

    def analyze(self, conversation: Conversation, behaviors: BehaviorAnalysis) -> Optional[KeyEventReport]:
        if not self.enabled:
            LOGGER.info("Key moment analyzer disabled via configuration.")
            return None

        triggers = self._select_triggers(behaviors)
        if not triggers:
            LOGGER.info("No candidate key moments detected.")
            return None

        events: List[KeyEventAnalysis] = []
        for entry in triggers[: self.max_events]:
            event_id = f"segment-{entry.segment_id}"
            window_segments = conversation.window(entry.segment_id, radius=self.window_radius)
            transcript_window = "\n".join(
                f"[{seg.speaker} {seg.start_time:0.1f}-{seg.end_time:0.1f}] {seg.transcript}"
                for seg in window_segments
            )
            prompt = (
                self.prompt_template.replace("{{EVENT_ID}}", event_id).replace("{{TRANSCRIPT_WINDOW}}", transcript_window)
            )
            try:
                response = ollama.chat(
                    model=self.model_name,
                    messages=[{"role": "system", "content": prompt}],
                    format="json",
                    options={"timeout": self.timeout},
                )
                payload = response.get("message", {}).get("content", "")
                data = json.loads(payload)
                events.append(self._parse_event(data))
            except Exception as exc:
                LOGGER.warning("Key moment model failed for %s (%s)", event_id, exc)
        if not events:
            return None
        return KeyEventReport(events=events, model_name=self.model_name)

    def _select_triggers(self, behaviors: BehaviorAnalysis) -> List[BehaviorEntry]:
        return behaviors.events(self.trigger_prefixes)

    def _parse_event(self, payload: dict) -> KeyEventAnalysis:
        score_objects = {}
        for key, value in payload.get("scores", {}).items():
            if isinstance(value, dict):
                score_objects[key] = KeyEventScore(
                    category=key,
                    score=float(value.get("score", 0)),
                    rationale=value.get("rationale", ""),
                )
        return KeyEventAnalysis(
            event_id=payload.get("event_id", "unknown"),
            scores=score_objects,
            overall_score=float(payload.get("overall_score", 0)),
            summary=payload.get("summary", ""),
            quotes=payload.get("quotes", []),
        )

