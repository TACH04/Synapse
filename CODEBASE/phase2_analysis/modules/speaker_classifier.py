from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

import ollama

from .data_models import Conversation, SpeakerMap

LOGGER = logging.getLogger(__name__)


class SpeakerRoleClassifier:
    """Determines which diarized speaker id maps to clinician vs patient."""

    def __init__(
        self,
        prompt_path: Path,
        model_name: str = "llama3:8b",
        max_turns: int = 14,
        timeout: int = 120,
    ) -> None:
        self.prompt_template = prompt_path.read_text(encoding="utf-8")
        self.model_name = model_name
        self.max_turns = max_turns
        self.timeout = timeout

    def classify(
        self,
        conversation: Conversation,
        clinician_override: Optional[str] = None,
        use_model: bool = True,
    ) -> SpeakerMap:
        if clinician_override:
            LOGGER.info("Clinician override provided: %s", clinician_override)
            patient_guess = self._fallback_patient_id(conversation, clinician_override)
            return SpeakerMap(clinician=clinician_override, patient=patient_guess, confidence="manual")

        if not use_model:
            LOGGER.info("Skipping speaker role model; using heuristic map.")
            return self._heuristic_map(conversation)

        prompt = self._build_prompt(conversation)
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a careful analyst. Follow the template strictly.",
                    },
                    {"role": "user", "content": prompt},
                ],
                format="json",
                options={"timeout": self.timeout},
            )
            payload = response.get("message", {}).get("content", "")
            result = json.loads(payload)
            LOGGER.debug("Speaker model raw response: %s", payload)
            return SpeakerMap(
                clinician=result.get("clinician", "SPEAKER_01"),
                patient=result.get("patient", "SPEAKER_00"),
                confidence=result.get("confidence"),
                rationale=result.get("rationale"),
            )
        except Exception as exc:
            LOGGER.warning("Speaker role model failed (%s). Falling back to heuristic.", exc)
            return self._heuristic_map(conversation)

    def _build_prompt(self, conversation: Conversation) -> str:
        snippet = conversation.snippet(max_turns=self.max_turns)
        return self.prompt_template.replace("{{TRANSCRIPT_SNIPPET}}", snippet or "Transcript unavailable.")

    def _fallback_patient_id(self, conversation: Conversation, clinician_id: str) -> str:
        speakers = {seg.speaker for seg in conversation.segments}
        for speaker in sorted(speakers):
            if speaker != clinician_id:
                return speaker
        return clinician_id

    def _heuristic_map(self, conversation: Conversation) -> SpeakerMap:
        talk_time = {}
        for seg in conversation.segments:
            talk_time[seg.speaker] = talk_time.get(seg.speaker, 0.0) + seg.duration
        if not talk_time:
            return SpeakerMap(clinician="SPEAKER_01", patient="SPEAKER_00", confidence="low")
        sorted_speakers = sorted(talk_time.items(), key=lambda item: item[1], reverse=True)
        clinician = sorted_speakers[0][0]
        patient = sorted_speakers[1][0] if len(sorted_speakers) > 1 else clinician
        return SpeakerMap(clinician=clinician, patient=patient, confidence="heuristic")

