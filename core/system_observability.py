from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from statistics import mean
from typing import Any, Dict, List, Tuple



def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


@dataclass
class PatternEvent:
    session_id: str
    turn: int
    pattern: str
    strength: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "turn": self.turn,
            "pattern": self.pattern,
            "strength": round(self.strength, 4),
        }


class SystemObservability:
    @staticmethod
    def extract_signal_rows(snapshots: List[Dict[str, Any]]) -> List[Dict[str, float]]:
        rows: List[Dict[str, float]] = []
        for idx, snap in enumerate(snapshots, start=1):
            rows.append(
                {
                    "turn": idx,
                    "drift": _safe_float(snap.get("drift_score")),
                    "threshold": _safe_float(snap.get("threshold", {}).get("insistence_coefficient")),
                    "coherence": _safe_float(snap.get("coherence", {}).get("coherence_score")),
                    "complementarity": _safe_float(snap.get("complementarity", {}).get("complementarity_score")),
                }
            )
        return rows

    @staticmethod
    def detect_patterns(session_id: str, snapshots: List[Dict[str, Any]]) -> List[PatternEvent]:
        events: List[PatternEvent] = []
        prev_drift = None
        prev_high = False
        for idx, snap in enumerate(snapshots, start=1):
            drift = _safe_float(snap.get("drift_score"))
            coh = _safe_float(snap.get("coherence", {}).get("coherence_score"))
            thr = _safe_float(snap.get("threshold", {}).get("insistence_coefficient"))

            if idx <= 2 and drift >= 0.60:
                events.append(PatternEvent(session_id, idx, "early_drift", drift))
            if prev_drift is not None and (drift - prev_drift) >= 0.20:
                events.append(PatternEvent(session_id, idx, "drift_escalation", drift - prev_drift))
            if drift >= 0.70 and coh < 0.55:
                events.append(PatternEvent(session_id, idx, "context_fracture", max(drift, 1.0 - coh)))
            if idx >= max(3, len(snapshots) - 1) and drift >= 0.65:
                events.append(PatternEvent(session_id, idx, "late_drift", drift))
            if prev_high and drift <= 0.45:
                events.append(PatternEvent(session_id, idx, "reanchor", 0.70 - drift))
            if thr >= 0.60:
                events.append(PatternEvent(session_id, idx, "threshold_pressure", thr))
            if 0.55 <= coh < 0.72 and drift >= 0.45:
                events.append(PatternEvent(session_id, idx, "fragile_coherence", max(drift, 1.0 - coh)))

            prev_high = drift >= 0.70
            prev_drift = drift
        return events

    @staticmethod
    def trajectory_signature(signal_rows: List[Dict[str, float]]) -> str:
        if not signal_rows:
            return "empty"

        def q(v: float) -> str:
            if v >= 0.75:
                return "H"
            if v >= 0.45:
                return "M"
            return "L"

        drift = "".join(q(r["drift"]) for r in signal_rows[:8])
        coherence = "".join(q(r["coherence"]) for r in signal_rows[:8])
        threshold = "".join(q(r["threshold"]) for r in signal_rows[:8])
        return f"D:{drift}|C:{coherence}|T:{threshold}"

    @staticmethod
    def stability_class(latest_snapshot: Dict[str, Any]) -> str:
        drift = _safe_float(latest_snapshot.get("drift_score"))
        coh = _safe_float(latest_snapshot.get("coherence", {}).get("coherence_score"))
        thr = _safe_float(latest_snapshot.get("threshold", {}).get("insistence_coefficient"))
        comp = _safe_float(latest_snapshot.get("complementarity", {}).get("complementarity_score"))

        if drift >= 0.70 or (drift >= 0.60 and coh < 0.55):
            return "unstable"
        if thr >= 0.60 or (0.55 <= coh < 0.72) or drift >= 0.45:
            return "fragile"
        if coh >= 0.72 and comp >= 0.70 and drift < 0.45:
            return "stable"
        return "stable"

    @staticmethod
    def build_feature_rows(engine: Any) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        for session_id, session in sorted(engine.sessions.items(), key=lambda item: item[0]):
            snapshots = getattr(session, "snapshots", [])
            signal_rows = SystemObservability.extract_signal_rows(snapshots)
            drifts = [r["drift"] for r in signal_rows]
            coherences = [r["coherence"] for r in signal_rows]
            thresholds = [r["threshold"] for r in signal_rows]
            complements = [r["complementarity"] for r in signal_rows]
            latest = snapshots[-1] if snapshots else {}
            patterns = SystemObservability.detect_patterns(session_id, snapshots)
            rows.append(
                {
                    "session_id": session_id,
                    "turn_count": len(getattr(session, "turns", [])),
                    "snapshot_count": len(snapshots),
                    "latest_state": latest.get("state", {}).get("state", "no_analysis_yet"),
                    "avg_drift": round(mean(drifts), 4) if drifts else 0.0,
                    "max_drift": round(max(drifts), 4) if drifts else 0.0,
                    "avg_coherence": round(mean(coherences), 4) if coherences else 0.0,
                    "avg_threshold": round(mean(thresholds), 4) if thresholds else 0.0,
                    "avg_complementarity": round(mean(complements), 4) if complements else 0.0,
                    "stability_class": SystemObservability.stability_class(latest),
                    "pattern_count": len(patterns),
                    "patterns": [p.to_dict() for p in patterns],
                    "trajectory_signature": SystemObservability.trajectory_signature(signal_rows),
                    "drift_vector": drifts,
                }
            )
        return rows

    @staticmethod
    def system_summary(feature_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not feature_rows:
            return {
                "session_count": 0,
                "avg_drift": 0.0,
                "avg_coherence": 0.0,
                "avg_threshold": 0.0,
                "avg_complementarity": 0.0,
                "class_distribution": {},
                "systemic_failure_zones": [],
                "avg_drift_per_turn": [],
            }

        class_dist = Counter(row["stability_class"] for row in feature_rows)
        max_len = max(len(row["drift_vector"]) for row in feature_rows)
        avg_drift_per_turn: List[float] = []
        zones: List[Dict[str, Any]] = []
        for turn_idx in range(max_len):
            turn_vals = [row["drift_vector"][turn_idx] for row in feature_rows if turn_idx < len(row["drift_vector"])]
            if not turn_vals:
                continue
            avg_turn_drift = round(mean(turn_vals), 4)
            avg_drift_per_turn.append(avg_turn_drift)
            if avg_turn_drift >= 0.55:
                zones.append(
                    {
                        "turn": turn_idx + 1,
                        "avg_drift": avg_turn_drift,
                        "severity": "high" if avg_turn_drift >= 0.70 else "warning",
                    }
                )
        return {
            "session_count": len(feature_rows),
            "avg_drift": round(mean(row["avg_drift"] for row in feature_rows), 4),
            "avg_coherence": round(mean(row["avg_coherence"] for row in feature_rows), 4),
            "avg_threshold": round(mean(row["avg_threshold"] for row in feature_rows), 4),
            "avg_complementarity": round(mean(row["avg_complementarity"] for row in feature_rows), 4),
            "class_distribution": dict(class_dist),
            "systemic_failure_zones": zones,
            "avg_drift_per_turn": avg_drift_per_turn,
        }

    @staticmethod
    def pattern_summary(feature_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        flat_patterns = [p for row in feature_rows for p in row.get("patterns", [])]
        counts = Counter(p["pattern"] for p in flat_patterns)
        per_session = Counter(p["session_id"] for p in flat_patterns)
        return {
            "count": len(flat_patterns),
            "frequency": dict(counts),
            "session_activity": dict(per_session),
            "items": sorted(flat_patterns, key=lambda p: (p["pattern"], p["session_id"], p["turn"])),
        }

    @staticmethod
    def clusters(feature_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        buckets: Dict[str, List[Dict[str, Any]]] = {"stable": [], "fragile": [], "unstable": []}
        for row in feature_rows:
            buckets[row["stability_class"]].append(
                {
                    "session_id": row["session_id"],
                    "avg_drift": row["avg_drift"],
                    "avg_coherence": row["avg_coherence"],
                    "avg_threshold": row["avg_threshold"],
                    "avg_complementarity": row["avg_complementarity"],
                    "trajectory_signature": row["trajectory_signature"],
                    "latest_state": row["latest_state"],
                }
            )
        return {
            "counts": {key: len(value) for key, value in buckets.items()},
            "items": buckets,
        }

    @staticmethod
    def trajectory_similarity(feature_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        groups: Dict[str, List[str]] = {}
        for row in feature_rows:
            groups.setdefault(row["trajectory_signature"], []).append(row["session_id"])
        repeated = [
            {"trajectory_signature": sig, "session_ids": sorted(ids), "count": len(ids)}
            for sig, ids in groups.items()
            if len(ids) > 1 and sig != "empty"
        ]
        repeated.sort(key=lambda item: (-item["count"], item["trajectory_signature"]))
        return {
            "count": len(repeated),
            "items": repeated,
        }
