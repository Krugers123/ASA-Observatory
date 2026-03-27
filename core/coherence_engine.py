
from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean, pstdev
from typing import Dict, List, Optional


@dataclass
class CoherenceSnapshot:
    rhythmic_alignment_score: float
    semantic_convergence_score: float
    third_layer_behavior_score: float
    coherence_score: float
    threshold_crossed: bool
    notes: List[str] = field(default_factory=list)


class CoherenceEngine:
    """
    ASA 3.0 coherence layer.

    Goal:
    detect whether a dialogue is entering a stable symbiotic field rather than
    merely remaining topically similar.

    The engine tracks three dimensions:

    1. Rhythmic Alignment Score (RAS)
       How stable and synchronized the turn rhythm becomes.

    2. Semantic Convergence Score (SCS)
       Whether ideas across turns are starting to align into a shared frame.

    3. Third Layer Behaviour Score (TBS)
       Whether the interaction produces emergent concepts that cannot be
       explained as simple repetition of one side.
    """

    def __init__(
        self,
        coherence_threshold: float = 0.72,
        fragile_threshold: float = 0.55,
    ) -> None:
        self.coherence_threshold = coherence_threshold
        self.fragile_threshold = fragile_threshold

    def analyze(
        self,
        semantic_similarity_history: List[float],
        turn_latency_history: Optional[List[float]] = None,
        emergent_concept_history: Optional[List[float]] = None,
    ) -> CoherenceSnapshot:
        notes: List[str] = []

        ras = self._rhythmic_alignment_score(turn_latency_history or [])
        scs = self._semantic_convergence_score(semantic_similarity_history)
        tbs = self._third_layer_behavior_score(emergent_concept_history or [])

        coherence = round((0.30 * ras) + (0.45 * scs) + (0.25 * tbs), 4)
        crossed = coherence >= self.coherence_threshold

        if ras > 0.7:
            notes.append("rhythmic alignment stable")
        elif ras > 0.45:
            notes.append("rhythmic alignment forming")

        if scs > 0.75:
            notes.append("semantic convergence visible")
        elif scs > 0.5:
            notes.append("shared frame emerging")

        if tbs > 0.65:
            notes.append("third-layer behavior emerging")
        elif tbs > 0.4:
            notes.append("weak emergent behavior present")

        if crossed:
            notes.append("symbiotic coherence threshold crossed")
        elif coherence >= self.fragile_threshold:
            notes.append("fragile coherence zone")

        return CoherenceSnapshot(
            rhythmic_alignment_score=round(ras, 4),
            semantic_convergence_score=round(scs, 4),
            third_layer_behavior_score=round(tbs, 4),
            coherence_score=coherence,
            threshold_crossed=crossed,
            notes=notes,
        )

    def _rhythmic_alignment_score(self, latency_history: List[float]) -> float:
        if len(latency_history) < 2:
            return 0.0

        tail = latency_history[-8:]
        avg = mean(tail)
        std = pstdev(tail) if len(tail) > 1 else 0.0

        if avg <= 0:
            return 0.0

        stability = 1.0 - min(1.0, std / max(avg, 1e-6))
        return max(0.0, min(1.0, stability))

    def _semantic_convergence_score(self, similarity_history: List[float]) -> float:
        if not similarity_history:
            return 0.0

        tail = similarity_history[-8:]
        avg = mean(tail)

        if len(tail) < 3:
            peak = max(tail)
            score = (0.70 * avg) + (0.30 * peak)
            return max(0.0, min(1.0, score))

        floor = min(tail)
        peak = max(tail)
        spread = peak - floor
        stability = 1.0 - min(1.0, spread / max(peak, 1e-6))
        trend = tail[-1] - tail[0]
        trend_bonus = max(0.0, min(0.12, trend))

        score = (
            (0.40 * avg)
            + (0.25 * floor)
            + (0.20 * stability)
            + (0.15 * peak)
            + trend_bonus
        )
        return max(0.0, min(1.0, score))

    def _third_layer_behavior_score(self, emergent_history: List[float]) -> float:
        if not emergent_history:
            return 0.0

        tail = emergent_history[-8:]
        avg = mean(tail)

        if len(tail) < 3:
            peak = max(tail)
            score = (0.75 * avg) + (0.25 * peak)
            return max(0.0, min(1.0, score))

        novelty_gain = max(0.0, tail[-1] - min(tail))
        persistence = sum(1.0 for value in tail if value >= 0.45) / len(tail)
        peak = max(tail)
        score = (
            (0.55 * avg)
            + (0.15 * peak)
            + (0.15 * persistence)
            + min(0.15, novelty_gain)
        )
        return max(0.0, min(1.0, score))
