from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .marker_alignment import score_marker_match
from .marker_extractor import extract_turn_markers


def run_marker_calibration(trace_files: list[Path], out_csv: Path | None = None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for trace_file in trace_files:
        payload = json.loads(trace_file.read_text(encoding="utf-8-sig"))
        expected_by_turn = {int(item["turn_index"]): item for item in payload.get("expected_turn_markers", [])}
        results = extract_turn_markers(payload.get("turns", []))
        for result in results:
            expected = expected_by_turn.get(result.turn_index, {})
            status, canonical = score_marker_match(expected.get("expected_marker", ""), result.markers)
            rows.append({
                "trace_id": payload.get("session_id", trace_file.stem),
                "turn_index": result.turn_index,
                "role": result.role,
                "expected_marker": expected.get("expected_marker", ""),
                "expected_canonical_marker": canonical,
                "extracted_primary_marker": result.primary_marker,
                "extracted_markers": ";".join(item.marker for item in result.markers),
                "match_status": status,
            })
    if out_csv is not None and rows:
        with out_csv.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    return rows