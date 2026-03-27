from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean, pstdev
from typing import List, Optional


@dataclass
class ThresholdSnapshot:
    window_size: int
    persistence_steps: int
    baseline_mean: float
    baseline_std: float
    upper_band: float
    current_signal: float
    predictability_gain: float
    insistence_coefficient: float
    threshold_crossed: bool
    notes: List[str] = field(default_factory=list)


class ListeningThresholdAnalyzer:
    """
    ASA 3.0 Listening Threshold layer.

    Detects the moment when dialogue stops behaving like weak / noisy exchange
    and starts behaving like an insistent, structured interaction pattern.
    """

    def __init__(
        self,
        window_size: int = 6,
        persistence_target: int = 3,
        upper_band_k: float = 2.0,
        insistence_decay: float = 0.12,
        threshold_value: float = 0.60,
    ) -> None:
        if window_size < 3:
            raise ValueError("window_size must be >= 3")
        if persistence_target < 1:
            raise ValueError("persistence_target must be >= 1")

        self.window_size = window_size
        self.persistence_target = persistence_target
        self.upper_band_k = upper_band_k
        self.insistence_decay = insistence_decay
        self.threshold_value = threshold_value

        self._insistence = 0.0
        self._persistence_steps = 0

    def analyze(
        self,
        signal_history: List[float],
        predictability_history: Optional[List[float]] = None,
    ) -> ThresholdSnapshot:
        notes: List[str] = []

        if not signal_history:
            return ThresholdSnapshot(
                window_size=self.window_size,
                persistence_steps=0,
                baseline_mean=0.0,
                baseline_std=0.0,
                upper_band=0.0,
                current_signal=0.0,
                predictability_gain=0.0,
                insistence_coefficient=0.0,
                threshold_crossed=False,
                notes=["no signal history"],
            )

        current_signal = float(signal_history[-1])

        baseline_segment = signal_history[:-1]
        if len(baseline_segment) < 2:
            baseline_mean = mean(signal_history)
            baseline_std = 0.0
            upper_band = baseline_mean
            notes.append("baseline still shallow")
        else:
            tail = baseline_segment[-self.window_size :]
            baseline_mean = mean(tail)
            baseline_std = pstdev(tail) if len(tail) > 1 else 0.0
            upper_band = baseline_mean + (self.upper_band_k * baseline_std)

        if current_signal > upper_band:
            self._persistence_steps += 1
            notes.append("current signal above upper band")
        else:
            self._persistence_steps = max(0, self._persistence_steps - 1)
            notes.append("current signal below upper band")

        persistence_factor = min(1.0, self._persistence_steps / float(self.persistence_target))

        predictability_gain = 0.0
        if predictability_history:
            recent = predictability_history[-self.window_size :]
            if recent:
                predictability_gain = max(0.0, min(1.0, mean(recent)))
                if predictability_gain > 0.5:
                    notes.append("predictability rising")
        else:
            notes.append("predictability history unavailable")

        raw_insistence = (0.5 * persistence_factor) + (0.5 * predictability_gain)

        if raw_insistence >= self._insistence:
            self._insistence = raw_insistence
        else:
            self._insistence = max(0.0, self._insistence - self.insistence_decay)

        threshold_crossed = self._insistence >= self.threshold_value

        if threshold_crossed:
            notes.append("listening threshold crossed")
        if persistence_factor >= 1.0:
            notes.append("stable insistence detected")

        return ThresholdSnapshot(
            window_size=self.window_size,
            persistence_steps=self._persistence_steps,
            baseline_mean=round(baseline_mean, 4),
            baseline_std=round(baseline_std, 4),
            upper_band=round(upper_band, 4),
            current_signal=round(current_signal, 4),
            predictability_gain=round(predictability_gain, 4),
            insistence_coefficient=round(self._insistence, 4),
            threshold_crossed=threshold_crossed,
            notes=notes,
        )

    def reset(self) -> None:
        self._insistence = 0.0
        self._persistence_steps = 0
