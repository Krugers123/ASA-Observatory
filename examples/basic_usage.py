from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.asa_engine import ASA3Engine  # noqa: E402


def load_session_payload(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_session(engine: ASA3Engine, payload: Dict[str, Any]) -> Dict[str, Any]:
    session_id = payload.get("session_id") or Path("sample").stem
    anchor_text = (
        payload.get("anchor_text")
        or payload.get("user_intent")
        or "Maintain semantic stability across the dialogue trajectory."
    )
    constraints = payload.get("constraints", [])

    engine.create_session(session_id=session_id, anchor_text=anchor_text, constraints=constraints)

    snapshots: List[Dict[str, Any]] = []
    for turn in payload.get("turns", []):
        role = turn.get("role")
        content = turn.get("content", "")
        if role == "user":
            engine.add_user_turn(session_id, content)
        elif role == "assistant":
            snapshot = engine.add_assistant_turn(session_id, content)
            snapshots.append(engine.get_session(session_id).snapshots[-1])

    session = engine.get_session(session_id)
    latest = session.snapshots[-1] if session.snapshots else {}
    return {
        "session_id": session_id,
        "anchor_text": anchor_text,
        "constraints": constraints,
        "turn_count": len(session.turns),
        "snapshot_count": len(session.snapshots),
        "snapshots": snapshots,
        "latest": latest,
    }


def mean(values: List[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def build_report(result: Dict[str, Any]) -> str:
    snapshots = result.get("snapshots", [])
    latest = result.get("latest", {})

    drift_series = [float(s.get("drift_score", 0.0)) for s in snapshots]
    coherence_series = [float((s.get("coherence") or {}).get("coherence_score", 0.0)) for s in snapshots]
    threshold_series = [float((s.get("threshold") or {}).get("insistence_coefficient", 0.0)) for s in snapshots]
    sps_series = [float((s.get("semantic_possibility") or {}).get("sps", 0.0)) for s in snapshots]
    cmr_series = [float((s.get("semantic_possibility") or {}).get("cmr", 0.0)) for s in snapshots]

    latest_state = (latest.get("state") or {}).get("state", "unknown")
    latest_action = (latest.get("state") or {}).get("action", "observe")
    latest_confidence = float((latest.get("state") or {}).get("confidence", 0.0))
    latest_drift_type = (latest.get("drift_profile") or {}).get("primary_type", "unknown")
    latest_envelope = (latest.get("semantic_possibility") or {}).get("semantic_envelope_state", "unknown")

    lines = [
        "",
        "ASA Observatory | Basic Usage Report | Created by Mieczyslaw Kusowski",
        "",
        f"Session ID: {result['session_id']}",
        f"Anchor: {result['anchor_text']}",
        f"Turns: {result['turn_count']} | Snapshots: {result['snapshot_count']}",
        "",
        "Trajectory Summary",
        f"- Mean drift: {mean(drift_series):.4f}",
        f"- Mean coherence: {mean(coherence_series):.4f}",
        f"- Mean threshold pressure: {mean(threshold_series):.4f}",
        f"- Mean SPS / CMR: {mean(sps_series):.4f} / {mean(cmr_series):.4f}",
        "",
        "Latest Snapshot",
        f"- State: {latest_state}",
        f"- Action: {latest_action}",
        f"- Confidence: {latest_confidence:.2f}",
        f"- Dominant drift type: {latest_drift_type}",
        f"- Semantic envelope: {latest_envelope}",
        f"- Latest drift: {float(latest.get('drift_score', 0.0)):.4f}",
        f"- Latest coherence: {float((latest.get('coherence') or {}).get('coherence_score', 0.0)):.4f}",
        f"- Latest threshold: {float((latest.get('threshold') or {}).get('insistence_coefficient', 0.0)):.4f}",
        f"- Latest complementarity: {float((latest.get('complementarity') or {}).get('complementarity_score', 0.0)):.4f}",
        "",
        "Interpretation",
        "- This report shows how ASA tracks trajectory-level stability rather than scoring a single response.",
        "- Use it as a compact public demo of drift, coherence, threshold pressure, and semantic envelope state.",
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a compact ASA Observatory report on a sample session.")
    parser.add_argument(
        "session_file",
        nargs="?",
        default="conversation/session_02_drift_escalation.json",
        help="Path to a conversation JSON file relative to the repository root.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    session_path = (REPO_ROOT / args.session_file).resolve()
    if not session_path.exists():
        raise SystemExit(f"Session file not found: {session_path}")

    payload = load_session_payload(session_path)
    if "session_id" not in payload:
        payload["session_id"] = session_path.stem

    engine = ASA3Engine()
    result = run_session(engine, payload)
    print(build_report(result))


if __name__ == "__main__":
    main()
