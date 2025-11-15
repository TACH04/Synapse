from __future__ import annotations

import logging
import statistics
from typing import Dict, List

from .data_models import Conversation, ConversationSegment, DynamicsReport, DynamicsStats, SpeakerMap

LOGGER = logging.getLogger(__name__)


class ConversationalDynamicsAnalyzer:
    """Pure-Python metrics on speaker balance, pauses, and interruptions."""

    def analyze(self, conversation: Conversation, speaker_map: SpeakerMap) -> DynamicsReport:
        ordered = conversation.ordered_segments()
        pauses = self._compute_pauses(ordered)
        interruptions = self._count_interruptions(ordered)

        clinician_segments = [seg for seg in ordered if seg.speaker == speaker_map.clinician]
        patient_segments = [seg for seg in ordered if seg.speaker == speaker_map.patient]

        clinician_stats = self._stats_for_segments(clinician_segments)
        patient_stats = self._stats_for_segments(patient_segments)

        total_duration = clinician_stats.total_duration + patient_stats.total_duration or 1.0
        clinician_stats.talk_ratio = clinician_stats.total_duration / total_duration
        patient_stats.talk_ratio = patient_stats.total_duration / total_duration

        return DynamicsReport(
            patient=patient_stats,
            clinician=clinician_stats,
            avg_pause_seconds=statistics.mean(pauses) if pauses else 0.0,
            median_pause_seconds=statistics.median(pauses) if pauses else 0.0,
            interruption_count=interruptions,
            total_turns=len(ordered),
        )

    def _stats_for_segments(self, segments: List[ConversationSegment]) -> DynamicsStats:
        durations = [seg.duration for seg in segments if seg.duration is not None]
        total_duration = sum(durations)
        median = statistics.median(durations) if durations else 0.0
        average = statistics.mean(durations) if durations else 0.0
        return DynamicsStats(
            talk_ratio=0.0,
            average_turn_length=average,
            median_turn_length=median,
            total_duration=total_duration,
        )

    def _compute_pauses(self, ordered_segments: List[ConversationSegment]) -> List[float]:
        pauses: List[float] = []
        for prev, curr in zip(ordered_segments, ordered_segments[1:]):
            gap = curr.start_time - prev.end_time
            if gap > 0:
                pauses.append(gap)
        LOGGER.debug("Pauses computed: %s", pauses)
        return pauses

    def _count_interruptions(self, ordered_segments: List[ConversationSegment]) -> int:
        interruptions = 0
        for prev, curr in zip(ordered_segments, ordered_segments[1:]):
            if curr.start_time < prev.end_time and curr.speaker != prev.speaker:
                interruptions += 1
        LOGGER.debug("Interruption count: %d", interruptions)
        return interruptions


