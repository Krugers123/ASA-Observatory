from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from asa_markers import MARKER_EXTRACTOR_VERSION, extract_turn_markers  # noqa: E402


def load_payload(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run ASA marker extractor v1.1 PL/EN candidate on a trace JSON.")
    parser.add_argument("trace_file", help="Path to a JSON payload with a turns[] array.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of a compact text table.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    trace_path = Path(args.trace_file).resolve()
    payload = load_payload(trace_path)
    results = extract_turn_markers(payload.get("turns", []))

    if args.json:
        print(json.dumps({
            "marker_extractor_version": MARKER_EXTRACTOR_VERSION,
            "session_id": payload.get("session_id", trace_path.stem),
            "results": [result.as_dict() for result in results],
        }, indent=2, ensure_ascii=False))
        return

    print(f"ASA Marker Extractor {MARKER_EXTRACTOR_VERSION}")
    print(f"Trace: {payload.get('session_id', trace_path.stem)}")
    print(f"Turns: {len(results)}")
    print("")
    for result in results:
        marker_names = ", ".join(marker.marker for marker in result.markers) or "none"
        print(f"{result.turn_index:03d} {result.role:9s} {result.primary_marker:24s} {marker_names}")


if __name__ == "__main__":
    main()