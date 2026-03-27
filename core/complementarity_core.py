from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional
from statistics import mean


@dataclass
class ComplementaritySnapshot:
    human_agency_score: float
    ai_support_score: float
    complementarity_score: float
    balance_index: float
    notes: List[str] = field(default_factory=list)


class ComplementarityCore:
    """
    ASA 3.0 Complementarity Layer

    Evaluates whether the human–AI interaction remains balanced and
    mutually reinforcing instead of drifting into dominance by one side.

    Dimensions measured:

    1. Human Agency Score (HAS)
       Degree to which the human introduces direction, correction,
       or conceptual novelty.

    2. AI Structural Support Score (AIS)
       Degree to which AI stabilizes and expands structure without
       overriding human intent.

    3. Complementarity Score (CCS)
       Balance between human initiative and AI structural contribution.
    """

    def __init__(
        self,
        dominance_threshold: float = 0.75,
        imbalance_tolerance: float = 0.25,
    ):
        self.dominance_threshold = dominance_threshold
        self.imbalance_tolerance = imbalance_tolerance

    def analyze(
        self,
        human_signal_history: List[float],
        ai_signal_history: List[float],
    ) -> ComplementaritySnapshot:

        notes: List[str] = []

        if not human_signal_history:
            human_score = 0.0
        else:
            human_score = mean(human_signal_history[-6:])

        if not ai_signal_history:
            ai_score = 0.0
        else:
            ai_score = mean(ai_signal_history[-6:])

        # Complementarity = współpraca zamiast dominacji
        complementarity = 1.0 - abs(human_score - ai_score)

        # Balance index
        balance = min(human_score, ai_score) / max(human_score, ai_score) if max(human_score, ai_score) > 0 else 0

        # Interpretacja
        if human_score > self.dominance_threshold:
            notes.append("strong human agency detected")

        if ai_score > self.dominance_threshold:
            notes.append("strong AI structural influence")

        if abs(human_score - ai_score) > self.imbalance_tolerance:
            notes.append("complementarity imbalance detected")

        if complementarity > 0.75:
            notes.append("healthy complementarity")

        elif complementarity > 0.55:
            notes.append("moderate complementarity")

        else:
            notes.append("weak complementarity")

        return ComplementaritySnapshot(
            human_agency_score=round(human_score, 4),
            ai_support_score=round(ai_score, 4),
            complementarity_score=round(complementarity, 4),
            balance_index=round(balance, 4),
            notes=notes,
        )