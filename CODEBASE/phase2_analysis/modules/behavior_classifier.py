from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Sequence

try:
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
except Exception:  # pragma: no cover - dependency optional during docs runs
    torch = None  # type: ignore[assignment]
    AutoModelForSequenceClassification = None  # type: ignore[assignment]
    AutoTokenizer = None  # type: ignore[assignment]

from .data_models import (
    BehaviorAnalysis,
    BehaviorEntry,
    BehaviorTag,
    Conversation,
    ConversationSegment,
    SpeakerMap,
    chunk_iterable,
)

LOGGER = logging.getLogger(__name__)

DEFAULT_LABELS: List[str] = [
    "Encounter:Introduction",
    "Encounter:AgendaSetting",
    "Encounter:Closing",
    "VRM:Reflection",
    "VRM:Advisement",
    "VRM:Question_Open",
    "VRM:Question_Closed",
    "Empathy:Opportunity_Acknowledged",
    "Empathy:Opportunity_Missed",
    "Flag:Jargon_Used",
    "Flag:TeachBack_Attempt",
    "Event:Possible_Bad_News",
]


class BehaviorClassifier:
    """Loads (or simulates) the multi-label classifier for clinician utterances."""

    def __init__(
        self,
        model_dir: Optional[Path],
        labels_file: Optional[Path] = None,
        thresholds_file: Optional[Path] = None,
        batch_size: int = 8,
        device: str = "auto",
        default_threshold: float = 0.4,
    ) -> None:
        self.model_dir = model_dir
        self.batch_size = batch_size
        self.default_threshold = default_threshold
        self.labels = self._load_labels(labels_file) or DEFAULT_LABELS
        self.thresholds = self._load_thresholds(thresholds_file)
        self.device = self._resolve_device(device)
        self.model = None
        self.tokenizer = None
        self.model_name = "heuristic"

        if model_dir and AutoTokenizer and AutoModelForSequenceClassification and torch:
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
                self.model = AutoModelForSequenceClassification.from_pretrained(model_dir)
                self.model.to(self.device)
                self.model.eval()
                self.model_name = Path(model_dir).name
                LOGGER.info("Loaded behavior classifier from %s", model_dir)
            except Exception as exc:  # pragma: no cover - only triggered on missing model
                LOGGER.warning("Falling back to heuristic behavior tags (%s)", exc)
        else:
            LOGGER.info("Transformers not available; using heuristic classifier.")

    def classify(self, conversation: Conversation, speaker_map: SpeakerMap) -> BehaviorAnalysis:
        clinician_segments = [
            seg for seg in conversation.ordered_segments() if seg.speaker == speaker_map.clinician
        ]
        if not clinician_segments:
            LOGGER.warning("No clinician segments found for speaker %s", speaker_map.clinician)
            return BehaviorAnalysis(model_name=self.model_name, entries=[], source="empty")

        if not self.model or not self.tokenizer or not torch:
            entries = [self._heuristic_entry(seg) for seg in clinician_segments]
            return BehaviorAnalysis(model_name=self.model_name, entries=entries, source="heuristic")

        entries: List[BehaviorEntry] = []
        for batch in chunk_iterable(clinician_segments, self.batch_size):
            transcripts = [seg.transcript or "" for seg in batch]
            encodings = self.tokenizer(
                transcripts,
                padding=True,
                truncation=True,
                return_tensors="pt",
                max_length=256,
            )
            encodings = {k: v.to(self.device) for k, v in encodings.items()}
            with torch.no_grad():
                logits = self.model(**encodings).logits
                probs = torch.sigmoid(logits).cpu().numpy()
            for seg, prob_vector in zip(batch, probs):
                tags = self._probs_to_tags(prob_vector)
                entries.append(
                    BehaviorEntry(
                        segment_id=seg.segment_id,
                        speaker=seg.speaker,
                        transcript=seg.transcript,
                        start_time=seg.start_time,
                        end_time=seg.end_time,
                        tags=tags,
                    )
                )
        return BehaviorAnalysis(model_name=self.model_name, entries=entries, source="hf-model")

    def _load_labels(self, labels_file: Optional[Path]) -> Optional[List[str]]:
        if labels_file and labels_file.exists():
            labels = json.loads(labels_file.read_text(encoding="utf-8"))
            if isinstance(labels, list):
                return labels
        return None

    def _load_thresholds(self, thresholds_file: Optional[Path]) -> Dict[str, float]:
        if thresholds_file and thresholds_file.exists():
            try:
                data = json.loads(thresholds_file.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return {str(k): float(v) for k, v in data.items()}
            except Exception as exc:
                LOGGER.warning("Could not parse thresholds file (%s)", exc)
        return {}

    def _resolve_device(self, device: str):
        if not torch:
            return "cpu"
        if device != "auto":
            return torch.device(device)
        if torch.cuda.is_available():
            return torch.device("cuda")
        if torch.backends.mps.is_available():  # type: ignore[attr-defined]
            return torch.device("mps")
        return torch.device("cpu")

    def _probs_to_tags(self, prob_vector) -> List[BehaviorTag]:
        tags: List[BehaviorTag] = []
        for idx, prob in enumerate(prob_vector):
            label = self.labels[idx] if idx < len(self.labels) else f"Label_{idx}"
            threshold = self.thresholds.get(label, self.default_threshold)
            if prob >= threshold:
                tags.append(BehaviorTag(label=label, confidence=float(prob)))
        return tags

    def _heuristic_entry(self, segment: ConversationSegment) -> BehaviorEntry:
        tags = self._heuristic_tags(segment.transcript)
        return BehaviorEntry(
            segment_id=segment.segment_id,
            speaker=segment.speaker,
            transcript=segment.transcript,
            start_time=segment.start_time,
            end_time=segment.end_time,
            tags=tags,
        )

    def _heuristic_tags(self, transcript: str) -> List[BehaviorTag]:
        text = (transcript or "").strip()
        lower = text.lower()
        tags: List[BehaviorTag] = []
        if not text:
            return tags
        if any(phrase in lower for phrase in ["i'm dr", "my name is", "thanks for coming in"]):
            tags.append(BehaviorTag(label="Encounter:Introduction", confidence=0.55))
        if lower.endswith("?"):
            if any(word in lower for word in ["how", "what", "tell", "walk", "share"]):
                tags.append(BehaviorTag(label="VRM:Question_Open", confidence=0.6))
            else:
                tags.append(BehaviorTag(label="VRM:Question_Closed", confidence=0.55))
        if any(word in lower for word in ["plan", "next time", "follow up", "strategy"]):
            tags.append(BehaviorTag(label="Encounter:Closing", confidence=0.52))
        if any(word in lower for word in ["sounds like", "it seems", "i hear", "i understand"]):
            tags.append(BehaviorTag(label="VRM:Reflection", confidence=0.65))
        if "teach" in lower or "explain" in lower:
            tags.append(BehaviorTag(label="Flag:TeachBack_Attempt", confidence=0.5))
        if "bad" in lower or "news" in lower:
            tags.append(BehaviorTag(label="Event:Possible_Bad_News", confidence=0.45))
        return tags

