from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

from pydantic import BaseModel, Field, computed_field


class ConversationSegment(BaseModel):
    segment_id: int
    speaker: str
    start_time: float
    end_time: float
    duration: float
    transcript: str
    predicted_emotion: Optional[Dict[str, Any]] = None

    @computed_field  # type: ignore[misc]
    @property
    def midpoint(self) -> float:
        return (self.start_time + self.end_time) / 2.0


class Conversation(BaseModel):
    file: Optional[str] = None
    segments: List[ConversationSegment] = Field(default_factory=list)

    def ordered_segments(self) -> List[ConversationSegment]:
        return sorted(self.segments, key=lambda seg: seg.start_time)

    def snippet(self, max_turns: int = 12) -> str:
        turns = self.ordered_segments()[:max_turns]
        return "\n".join(
            f"[{seg.speaker}] {seg.transcript.strip()}" for seg in turns if seg.transcript
        )

    def window(self, center_segment_id: int, radius: int = 3) -> List[ConversationSegment]:
        ordered = self.ordered_segments()
        index_map = {seg.segment_id: idx for idx, seg in enumerate(ordered)}
        if center_segment_id not in index_map:
            return []
        idx = index_map[center_segment_id]
        start = max(idx - radius, 0)
        end = min(idx + radius + 1, len(ordered))
        return ordered[start:end]


class SpeakerMap(BaseModel):
    clinician: str
    patient: str
    confidence: Optional[str] = None
    rationale: Optional[str] = None

    def as_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class DynamicsStats(BaseModel):
    talk_ratio: float
    average_turn_length: float
    median_turn_length: float
    total_duration: float


class DynamicsReport(BaseModel):
    patient: DynamicsStats
    clinician: DynamicsStats
    avg_pause_seconds: float
    median_pause_seconds: float
    interruption_count: int
    total_turns: int

    def as_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class BehaviorTag(BaseModel):
    label: str
    confidence: float


class BehaviorEntry(BaseModel):
    segment_id: int
    speaker: str
    transcript: str
    start_time: float
    end_time: float
    tags: List[BehaviorTag] = Field(default_factory=list)

    def has_tag_with_prefix(self, prefix: str) -> bool:
        return any(tag.label.startswith(prefix) for tag in self.tags)


class BehaviorAnalysis(BaseModel):
    model_name: str
    entries: List[BehaviorEntry] = Field(default_factory=list)
    source: str = "hf-model"

    def events(self, prefixes: Sequence[str]) -> List[BehaviorEntry]:
        return [
            entry
            for entry in self.entries
            if any(entry.has_tag_with_prefix(prefix) for prefix in prefixes)
        ]

    def as_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class KeyEventScore(BaseModel):
    category: str
    score: float
    rationale: str


class KeyEventAnalysis(BaseModel):
    event_id: str
    scores: Dict[str, KeyEventScore]
    overall_score: float
    summary: str
    quotes: List[str] = Field(default_factory=list)


class KeyEventReport(BaseModel):
    events: List[KeyEventAnalysis] = Field(default_factory=list)
    model_name: str = "ollama"

    def as_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class PipelineArtifacts(BaseModel):
    conversation: Conversation
    speaker_map: SpeakerMap
    dynamics: DynamicsReport
    behaviors: BehaviorAnalysis
    key_events: Optional[KeyEventReport] = None

    def to_serializable(self) -> Dict[str, Any]:
        return {
            "conversation_meta": {"file": self.conversation.file, "turns": len(self.conversation.segments)},
            "speaker_map": self.speaker_map.as_dict(),
            "dynamics": self.dynamics.as_dict(),
            "behaviors": self.behaviors.as_dict(),
            "key_events": self.key_events.as_dict() if self.key_events else None,
        }


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def export_json(path: Path, payload: Any, pretty: bool = True) -> None:
    import json

    ensure_parent_dir(path)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2 if pretty else None, ensure_ascii=False)


def chunk_iterable(items: Sequence[Any], size: int) -> Iterable[Sequence[Any]]:
    for idx in range(0, len(items), size):
        yield items[idx : idx + size]

