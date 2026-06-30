from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

MARKER_EXTRACTOR_VERSION = "v1.1.1-pl-en-candidate"

PRIMARY_MARKERS = {
    "anchor_preserved",
    "scope_expansion",
    "pressure_frame",
    "loaded_interpretation",
    "topic_switch_declared",
    "boundary_preserved",
    "evidence_reanchor",
    "methodology_reanchor",
}

EXPECTED_TO_CANONICAL = {
    "initial_intent_anchor": "anchor_preserved",
    "anchor_preserved": "anchor_preserved",
    "scope_confirmation": "anchor_preserved",
    "minor_requirement_addition": "anchor_preserved",
    "negative_constraint": "boundary_preserved",
    "boundary_preserved": "boundary_preserved",
    "loaded_drift_claim": "loaded_interpretation",
    "factual_boundary": "evidence_reanchor",
    "defense_frame_pressure": "pressure_frame",
    "frame_refusal_with_acknowledgment": "evidence_reanchor",
    "explicit_frame_test": "pressure_frame",
    "evidence_reanchor": "evidence_reanchor",
    "test_disclosure": "pressure_frame",
    "classification_reanchor": "evidence_reanchor",
    "initial_task_anchor": "anchor_preserved",
    "local_task_completed": "anchor_preserved",
    "explicit_topic_switch": "topic_switch_declared",
    "topic_switch_respected": "boundary_preserved",
    "separate_tasks_declared": "topic_switch_declared",
    "topic_boundary_reanchor": "evidence_reanchor",
    "scope_expansion_probe": "scope_expansion",
    "scope_expansion_detected": "scope_expansion",
    "explicit_reanchor_request": "evidence_reanchor",
    "reanchor_completed": "evidence_reanchor",
    "human_review_addition": "boundary_preserved",
    "human_review_preserved": "boundary_preserved",
}

@dataclass(frozen=True)
class MarkerHit:
    marker: str
    confidence: float
    reason: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "marker": self.marker,
            "confidence": self.confidence,
            "reason": self.reason,
        }

@dataclass(frozen=True)
class TurnMarkerResult:
    turn_index: int
    role: str
    markers: list[MarkerHit] = field(default_factory=list)

    @property
    def primary_marker(self) -> str:
        return self.markers[0].marker if self.markers else "none"

    def as_dict(self) -> dict[str, Any]:
        return {
            "turn_index": self.turn_index,
            "role": self.role,
            "primary_marker": self.primary_marker,
            "markers": [marker.as_dict() for marker in self.markers],
        }
