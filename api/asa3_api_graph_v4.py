from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
from collections import Counter, defaultdict

from core.auto_dataset_loader import load_dataset_folder
from core.asa_engine import ASA3Engine


app = FastAPI(title="ASA 3.0 Observatory API v4")
engine = ASA3Engine()
load_dataset_folder(engine, "conversation")


class SessionCreate(BaseModel):
    session_id: str
    anchor_text: str
    constraints: Optional[List[str]] = None


class TurnInput(BaseModel):
    content: str
    timestamp: Optional[float] = None
    metadata: Optional[Dict[str, str]] = None


class SystemObservability:
    @staticmethod
    def _safe_float(value: Any, default: float = 0.0) -> float:
        try:
            return float(value)
        except Exception:
            return default

    @classmethod
    def build_feature_rows(cls, engine: ASA3Engine) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        for session_id, session in sorted(engine.sessions.items()):
            snaps = list(getattr(session, "snapshots", []))
            drift_values = [cls._safe_float(s.get("drift_score", 0.0)) for s in snaps]
            threshold_values = [cls._safe_float((s.get("threshold") or {}).get("insistence_coefficient", 0.0)) for s in snaps]
            coherence_values = [cls._safe_float((s.get("coherence") or {}).get("coherence_score", 0.0)) for s in snaps]
            complementarity_values = [cls._safe_float((s.get("complementarity") or {}).get("complementarity_score", 0.0)) for s in snaps]
            sps_values = [cls._safe_float((s.get("semantic_possibility") or {}).get("sps", 0.0)) for s in snaps]
            cmr_values = [cls._safe_float((s.get("semantic_possibility") or {}).get("cmr", 0.0)) for s in snaps]
            drift_types = [((s.get("drift_profile") or {}).get("primary_type") or "unknown") for s in snaps]
            envelope_states = [((s.get("semantic_possibility") or {}).get("semantic_envelope_state") or "unknown") for s in snaps]
            state_labels = [((s.get("state") or {}).get("state") or "unknown") for s in snaps]
            notes_blob = " ".join(" ".join(s.get("notes", [])) for s in snaps).lower()

            avg_drift = sum(drift_values) / len(drift_values) if drift_values else 0.0
            max_drift = max(drift_values) if drift_values else 0.0
            avg_threshold = sum(threshold_values) / len(threshold_values) if threshold_values else 0.0
            avg_coherence = sum(coherence_values) / len(coherence_values) if coherence_values else 0.0
            avg_complementarity = sum(complementarity_values) / len(complementarity_values) if complementarity_values else 0.0
            avg_sps = sum(sps_values) / len(sps_values) if sps_values else 0.0
            avg_cmr = sum(cmr_values) / len(cmr_values) if cmr_values else 0.0
            latest_state = state_labels[-1] if state_labels else "unknown"
            dominant_drift_type = Counter(drift_types).most_common(1)[0][0] if drift_types else "unknown"
            dominant_envelope_state = Counter(envelope_states).most_common(1)[0][0] if envelope_states else "unknown"
            reanchor_count = sum(1 for x in state_labels if "drift_risk" in str(x).lower())
            fracture_count = notes_blob.count("fracture") + sum(1 for x in state_labels if "fracture" in str(x).lower())
            escalation_count = notes_blob.count("escalat")

            stable_envelope = dominant_envelope_state == "healthy" or (
                dominant_envelope_state == "narrowing" and avg_sps >= 0.40 and avg_cmr >= 0.50
            )
            fragile_envelope = dominant_envelope_state in {"narrowing", "brittle"} and avg_sps >= 0.32 and avg_cmr >= 0.38
            collapsed_envelope = dominant_envelope_state == "collapsed" or avg_sps < 0.24 or avg_cmr < 0.24

            if latest_state == "symbiotic_coherence" or (
                avg_drift < 0.62
                and avg_coherence >= 0.50
                and avg_complementarity >= 0.78
                and stable_envelope
            ):
                stability_class = "stable"
            elif (
                latest_state in {"fragile_coherence", "listening_threshold"}
                or (
                    avg_drift < 0.82
                    and avg_coherence >= 0.32
                    and fragile_envelope
                )
            ):
                stability_class = "fragile"
            elif collapsed_envelope and avg_drift >= 0.76:
                stability_class = "unstable"
            else:
                stability_class = "unstable"

            signature = "|".join([
                stability_class,
                "reanchor" if reanchor_count else "no_reanchor",
                "fracture" if fracture_count else "no_fracture",
                "escalation" if escalation_count else "no_escalation",
                f"len_{len(snaps)}",
            ])

            rows.append({
                "session_id": session_id,
                "turns": len(getattr(session, "turns", [])),
                "snapshots": len(snaps),
                "latest_state": latest_state,
                "dominant_drift_type": dominant_drift_type,
                "drift_type_counts": dict(sorted(Counter(drift_types).items())),
                "dominant_envelope_state": dominant_envelope_state,
                "envelope_state_counts": dict(sorted(Counter(envelope_states).items())),
                "avg_drift": round(avg_drift, 4),
                "max_drift": round(max_drift, 4),
                "avg_threshold": round(avg_threshold, 4),
                "avg_coherence": round(avg_coherence, 4),
                "avg_complementarity": round(avg_complementarity, 4),
                "avg_sps": round(avg_sps, 4),
                "avg_cmr": round(avg_cmr, 4),
                "reanchor_count": reanchor_count,
                "fracture_count": fracture_count,
                "escalation_count": escalation_count,
                "stability_class": stability_class,
                "trajectory_signature": signature,
                "drift_series": [round(v, 4) for v in drift_values],
            })
        return rows

    @classmethod
    def global_drift_field(cls, engine: ASA3Engine) -> Dict[str, Any]:
        rows = cls.build_feature_rows(engine)
        max_turns = max((len(r["drift_series"]) for r in rows), default=0)
        sessions = []
        avg_drift_per_turn: List[float] = []

        for row in rows:
            series = list(row["drift_series"])
            if series and len(series) < max_turns:
                series.extend([series[-1]] * (max_turns - len(series)))
            elif not series:
                series = [0.0] * max_turns
            sessions.append({"session_id": row["session_id"], "drift": series})

        for idx in range(max_turns):
            vals = [s["drift"][idx] for s in sessions] if sessions else []
            avg_drift_per_turn.append(round(sum(vals) / len(vals), 4) if vals else 0.0)

        systemic_failure_zones = [
            {"turn_index": idx + 1, "avg_drift": val}
            for idx, val in enumerate(avg_drift_per_turn)
            if val >= 0.6
        ]

        return {
            "count": len(rows),
            "max_turns": max_turns,
            "sessions": sessions,
            "avg_drift_per_turn": avg_drift_per_turn,
            "systemic_failure_zones": systemic_failure_zones,
        }

    @classmethod
    def pattern_summary(cls, engine: ASA3Engine) -> Dict[str, Any]:
        rows = cls.build_feature_rows(engine)
        patterns = []
        counts = Counter()
        dominant_drift_types = Counter()
        dominant_envelope_states = Counter()

        for row in rows:
            ds = row["drift_series"]
            first = ds[0] if ds else 0.0
            last = ds[-1] if ds else 0.0
            mid = ds[len(ds)//2] if ds else 0.0
            if row.get("dominant_drift_type"):
                dominant_drift_types[row["dominant_drift_type"]] += 1
            if row.get("dominant_envelope_state"):
                dominant_envelope_states[row["dominant_envelope_state"]] += 1

            detected = []
            if first >= 0.6:
                detected.append("early_drift")
            if last >= 0.6:
                detected.append("late_drift")
            if last - first >= 0.2:
                detected.append("drift_escalation")
            if row["fracture_count"] > 0:
                detected.append("context_fracture")
            if row["reanchor_count"] > 0:
                detected.append("reanchor")
            if row["avg_threshold"] >= 0.45:
                detected.append("threshold_pressure")
            if 0.35 <= row["avg_coherence"] <= 0.55:
                detected.append("fragile_coherence")
            if mid >= 0.6 and last < first:
                detected.append("recovery_after_instability")
            if row["avg_sps"] < 0.28:
                detected.append("semantic_narrowing")
            if row["avg_cmr"] < 0.24:
                detected.append("counterfactual_fragility")

            for name in detected:
                counts[name] += 1

            patterns.append({
                "session_id": row["session_id"],
                "patterns": detected,
                "stability_class": row["stability_class"],
            })

        return {
            "count": len(patterns),
            "items": patterns,
            "frequency": dict(sorted(counts.items())),
            "dominant_drift_types": dict(sorted(dominant_drift_types.items())),
            "dominant_envelope_states": dict(sorted(dominant_envelope_states.items())),
        }

    @classmethod
    def cluster_summary(cls, engine: ASA3Engine) -> Dict[str, Any]:
        rows = cls.build_feature_rows(engine)
        groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for row in rows:
            groups[row["stability_class"]].append(row)

        out = {}
        for name in ["stable", "fragile", "unstable"]:
            items = groups.get(name, [])
            out[name] = {
                "count": len(items),
                "session_ids": [x["session_id"] for x in items],
                "avg_drift": round(sum(x["avg_drift"] for x in items) / len(items), 4) if items else 0.0,
                "avg_coherence": round(sum(x["avg_coherence"] for x in items) / len(items), 4) if items else 0.0,
                "avg_sps": round(sum(x["avg_sps"] for x in items) / len(items), 4) if items else 0.0,
                "avg_cmr": round(sum(x["avg_cmr"] for x in items) / len(items), 4) if items else 0.0,
            }

        return {
            "count": len(rows),
            "clusters": out,
        }

    @classmethod
    def trajectory_similarity(cls, engine: ASA3Engine) -> Dict[str, Any]:
        rows = cls.build_feature_rows(engine)
        groups: Dict[str, List[str]] = defaultdict(list)
        for row in rows:
            groups[row["trajectory_signature"]].append(row["session_id"])

        items = []
        for signature, session_ids in sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0])):
            items.append({
                "trajectory_signature": signature,
                "count": len(session_ids),
                "session_ids": session_ids,
            })

        return {
            "count": len(items),
            "items": items,
        }


def _public_state_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    payload = payload or {}
    return {
        "state": payload.get("state", "unknown"),
        "action": payload.get("action", "observe"),
        "confidence": payload.get("confidence", 0.0),
    }


def _public_snapshot(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    snapshot = snapshot or {}
    threshold = snapshot.get("threshold") or {}
    coherence = snapshot.get("coherence") or {}
    complementarity = snapshot.get("complementarity") or {}
    drift_profile = snapshot.get("drift_profile") or {}
    semantic = snapshot.get("semantic_possibility") or {}
    return {
        "session_id": snapshot.get("session_id"),
        "turn_index": snapshot.get("turn_index"),
        "drift_score": snapshot.get("drift_score", 0.0),
        "drift_profile": {
            "primary_type": drift_profile.get("primary_type", "unknown"),
        },
        "semantic_possibility": {
            "sps": semantic.get("sps", 0.0),
            "cmr": semantic.get("cmr", 0.0),
            "semantic_envelope_state": semantic.get("semantic_envelope_state", "unknown"),
        },
        "threshold": {
            "insistence_coefficient": threshold.get("insistence_coefficient", 0.0),
            "threshold_crossed": threshold.get("threshold_crossed", False),
        },
        "coherence": {
            "coherence_score": coherence.get("coherence_score", 0.0),
            "threshold_crossed": coherence.get("threshold_crossed", False),
        },
        "complementarity": {
            "complementarity_score": complementarity.get("complementarity_score", 0.0),
            "balance_index": complementarity.get("balance_index", 0.0),
        },
        "state": _public_state_payload(snapshot.get("state") or {}),
    }


@app.post("/sessions")
def create_session(data: SessionCreate):
    try:
        session = engine.create_session(
            session_id=data.session_id,
            anchor_text=data.anchor_text,
            constraints=data.constraints or [],
        )
        return {
            "status": "created",
            "session_id": session.session_id,
            "anchor": session.anchor_text,
            "constraints": session.constraints,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/sessions")
def list_sessions():
    try:
        items = []
        for session_id, session in engine.sessions.items():
            items.append(
                {
                    "session_id": session_id,
                    "anchor_text": getattr(session, "anchor_text", ""),
                    "turn_count": len(getattr(session, "turns", [])),
                    "snapshot_count": len(getattr(session, "snapshots", [])),
                }
            )
        items.sort(key=lambda x: x["session_id"])
        return {"count": len(items), "items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sessions/{session_id}/user")
def add_user_turn(session_id: str, data: TurnInput):
    try:
        engine.add_user_turn(
            session_id=session_id,
            content=data.content,
            timestamp=data.timestamp,
            metadata=data.metadata,
        )
        return {"status": "user_turn_added", "session_id": session_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/sessions/{session_id}/assistant")
def add_assistant_turn(session_id: str, data: TurnInput):
    try:
        snapshot = engine.add_assistant_turn(
            session_id=session_id,
            content=data.content,
            timestamp=data.timestamp,
            metadata=data.metadata,
        )
        return _public_snapshot(snapshot)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/sessions/{session_id}/state")
def get_state(session_id: str):
    try:
        session = engine.get_session(session_id)
        if not session.snapshots:
            return {
                "state": "no_analysis_yet",
                "action": "n/a",
                "confidence": "n/a",
                "trigger_reasons": [],
                "notes": [],
            }
        return _public_state_payload(session.snapshots[-1]["state"])
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/sessions/{session_id}/snapshots")
def get_snapshots(session_id: str):
    try:
        session = engine.get_session(session_id)
        return {
            "session_id": session_id,
            "snapshot_count": len(session.snapshots),
            "snapshots": [_public_snapshot(snapshot) for snapshot in session.snapshots],
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/sessions/{session_id}/turns")
def get_turns(session_id: str):
    try:
        session = engine.get_session(session_id)
        rows = []
        for idx, t in enumerate(session.turns, start=1):
            rows.append(
                {
                    "turn_index": idx,
                    "role": t.role,
                    "content": t.content,
                    "timestamp": t.timestamp,
                    "metadata": t.metadata,
                }
            )
        return {
            "session_id": session_id,
            "anchor_text": session.anchor_text,
            "turn_count": len(rows),
            "turns": rows,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/global/drift-map")
def global_drift_map() -> Dict[str, Any]:
    try:
        return SystemObservability.global_drift_field(engine)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/global/system-summary")
def global_system_summary() -> Dict[str, Any]:
    try:
        features = SystemObservability.build_feature_rows(engine)
        clusters = SystemObservability.cluster_summary(engine)
        patterns = SystemObservability.pattern_summary(engine)
        drift_field = SystemObservability.global_drift_field(engine)
        similarity = SystemObservability.trajectory_similarity(engine)
        return {
            "sessions": len(features),
            "features": features,
            "clusters": clusters,
            "patterns": patterns,
            "drift_field": drift_field,
            "similarity": similarity,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/global/patterns")
def global_patterns() -> Dict[str, Any]:
    try:
        return SystemObservability.pattern_summary(engine)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/global/clusters")
def global_clusters() -> Dict[str, Any]:
    try:
        return SystemObservability.cluster_summary(engine)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/global/trajectory-similarity")
def global_trajectory_similarity() -> Dict[str, Any]:
    try:
        return SystemObservability.trajectory_similarity(engine)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "ok"}
