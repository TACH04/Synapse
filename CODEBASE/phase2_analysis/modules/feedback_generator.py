from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import List, Optional, Sequence

import ollama

from .data_models import PipelineArtifacts

LOGGER = logging.getLogger(__name__)


class FeedbackGenerator:
    """Synthesizes the final Markdown report using a local LLM."""

    MAX_RETRIES = 2

    def __init__(self, prompt_path: Path, model_name: str = "mistral-nemo", timeout: int = 240) -> None:
        self.prompt_template = prompt_path.read_text(encoding="utf-8")
        self.model_name = model_name
        self.timeout = timeout

    def generate(self, artifacts: PipelineArtifacts, use_model: bool = True) -> str:
        if not use_model:
            LOGGER.info("Skipping feedback LLM; using fallback formatter.")
            return self._fallback_report(artifacts)
        data_json = json.dumps(artifacts.to_serializable(), indent=2, ensure_ascii=False)
        messages = self._build_messages(data_json)
        require_key_moments = bool(artifacts.key_events and artifacts.key_events.events)
        try:
            for attempt in range(1, self.MAX_RETRIES + 1):
                response = ollama.chat(
                    model=self.model_name,
                    messages=messages,
                    options={"timeout": self.timeout},
                )
                content = response.get("message", {}).get("content", "").strip()
                if content and self._looks_valid(content, require_key_moments):
                    return content

                LOGGER.warning(
                    "Feedback generator attempt %s missing required sections.", attempt
                )
                if attempt == self.MAX_RETRIES:
                    break
                messages.extend(
                    [
                        {"role": "assistant", "content": content or "[empty response]"},
                        {
                            "role": "user",
                            "content": (
                                "Your last reply missed one or more required headings "
                                "(# Communication Feedback Report, ## Summary Dashboard, "
                                "## What Went Well, ## Opportunities for Growth, "
                                "## Next Visit Checklist, and ## Key Moments only when key events exist). "
                                "Regenerate the entire report using that template; include placeholder text "
                                "like 'No data available' if a section has no content."
                            ),
                        },
                    ]
                )
        except Exception as exc:
            LOGGER.warning("Feedback generator failed (%s). Returning fallback report.", exc)
            return self._fallback_report(artifacts)

        LOGGER.warning("Feedback generator exhausted retries. Returning fallback report.")
        return self._fallback_report(artifacts)

    def _build_messages(self, data_json: str) -> List[dict]:
        template = self.prompt_template
        system_content = ""
        user_template = template

        if "User instructions:" in template:
            system_raw, user_raw = template.split("User instructions:", 1)
            system_content = system_raw.replace("System role:", "").strip()
            user_template = user_raw.strip()

        user_content = user_template.replace("{{PIPELINE_DATA_JSON}}", data_json)
        messages = []
        if system_content:
            messages.append({"role": "system", "content": system_content})
        messages.append({"role": "user", "content": user_content})
        return messages

    def _looks_valid(self, content: str, require_key_moments: bool) -> bool:
        required_sections: List[str] = [
            "# Communication Feedback Report",
            "## Summary Dashboard",
            "## What Went Well",
            "## Opportunities for Growth",
            "## Next Visit Checklist",
        ]
        if require_key_moments:
            required_sections.append("## Key Moments")
        return all(section in content for section in required_sections)

    def _fallback_report(self, artifacts: PipelineArtifacts) -> str:
        dyn = artifacts.dynamics
        behavior_summary = len(artifacts.behaviors.entries)
        key_event_summary = (
            f"{len(artifacts.key_events.events)} key events analyzed."
            if artifacts.key_events
            else "Key moment analysis unavailable."
        )
        return "\n".join(
            [
                "# Communication Feedback Report",
                "## Summary Dashboard",
                f"- Patient talk ratio: {dyn.patient.talk_ratio:.2f}",
                f"- Clinician talk ratio: {dyn.clinician.talk_ratio:.2f}",
                f"- Avg pause (s): {dyn.avg_pause_seconds:.2f}",
                f"- Interruptions: {dyn.interruption_count}",
                "## What Went Well",
                "- Automated summary unavailable; review clinician reflections manually.",
                "## Opportunities for Growth",
                "- Run `run_feedback.py` once Ollama is available to generate full guidance.",
                "## Key Moments",
                f"- {key_event_summary}",
                "## Next Visit Checklist",
                "- Double-check agenda setting and empathy acknowledgments.",
                f"- {behavior_summary} clinician turns analyzed.",
            ]
        )

