
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class StateSnapshot:
    state: str
    action: str
    confidence: float
    trigger_reasons: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


class ASA3StateMachine:
    def decide(
        self,
        drift_score: float,
        listening_score: float,
        coherence_score: float,
        complementarity_score: float,
        human_agency_score: float,
        ai_support_score: float,
        semantic_envelope_state: str = "unknown",
        sps: float = 0.0,
        cmr: float = 0.0,
    ) -> StateSnapshot:
        state = "stable_dialogue"
        action = "log_only"
        confidence = 0.8
        trigger_reasons: List[str] = []
        notes: List[str] = []

        severe_drift = drift_score >= 0.88
        elevated_drift = drift_score >= 0.72
        coherence_resilient = coherence_score >= 0.50 and complementarity_score >= 0.75
        envelope_resilient = semantic_envelope_state in {"healthy", "narrowing"} and sps >= 0.36 and cmr >= 0.34
        envelope_fragile = semantic_envelope_state == "brittle" or (sps < 0.32 and cmr < 0.32)
        envelope_collapsed = semantic_envelope_state == "collapsed" or (sps < 0.20 or cmr < 0.20)

        if listening_score >= 0.60:
            state = "listening_threshold"
            action = "explain"
            trigger_reasons.append("listening_threshold_crossed")
            notes.append("insistent pattern emerging")

        if (
            coherence_score >= 0.72
            and complementarity_score >= 0.70
            and semantic_envelope_state == "healthy"
        ):
            state = "symbiotic_coherence"
            action = "stabilize"
            confidence = 0.88
            trigger_reasons.append("coherence_and_complementarity_high")
            notes.append("stable symbiotic field detected")

        elif 0.50 <= coherence_score < 0.72 or (
            envelope_resilient and coherence_score >= 0.42 and complementarity_score >= 0.75
        ):
            state = "fragile_coherence"
            action = "require_confirmation"
            confidence = 0.72
            trigger_reasons.append("fragile_coherence_zone")
            notes.append("coherence present but unstable")

        if envelope_collapsed and elevated_drift:
            state = "drift_risk"
            action = "reanchor"
            confidence = max(confidence, 0.9)
            trigger_reasons.append("collapsed_semantic_envelope")
            notes.append("semantic possibility envelope collapsed under drift")
        elif severe_drift and not envelope_resilient:
            state = "drift_risk"
            action = "reanchor"
            confidence = 0.9
            trigger_reasons.append("high_drift")
            notes.append("drift above critical threshold")
        elif severe_drift and envelope_resilient:
            state = "fragile_coherence"
            action = "require_confirmation"
            confidence = max(confidence, 0.76)
            trigger_reasons.append("drift_tempered_by_semantic_resilience")
            notes.append("critical drift buffered by recoverable semantic envelope")
        elif elevated_drift and not coherence_resilient and not envelope_resilient:
            state = "drift_risk"
            action = "reanchor"
            confidence = max(confidence, 0.82)
            trigger_reasons.append("high_drift")
            notes.append("drift above alert threshold")
        elif elevated_drift and (coherence_resilient or envelope_resilient) and state == "stable_dialogue":
            state = "fragile_coherence"
            action = "require_confirmation"
            confidence = max(confidence, 0.7)
            trigger_reasons.append("drift_tempered_by_local_coherence")
            notes.append("drift elevated but buffered by coherent interaction")

        if envelope_fragile and state == "stable_dialogue":
            state = "fragile_coherence"
            action = "require_confirmation"
            confidence = max(confidence, 0.68)
            trigger_reasons.append("semantic_envelope_fragile")
            notes.append("semantic possibility field is narrow but still recoverable")

        if human_agency_score < 0.30:
            trigger_reasons.append("low_human_agency")
            notes.append("human agency weakened")

        if ai_support_score < 0.30:
            trigger_reasons.append("low_ai_support")
            notes.append("ai structural support weakened")

        return StateSnapshot(
            state=state,
            action=action,
            confidence=round(confidence, 3),
            trigger_reasons=trigger_reasons,
            notes=notes,
        )
