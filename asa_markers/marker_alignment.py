from __future__ import annotations

from .marker_schema import EXPECTED_TO_CANONICAL, PRIMARY_MARKERS, MarkerHit


def score_marker_match(expected: str, extracted: list[MarkerHit]) -> tuple[str, str]:
    canonical = EXPECTED_TO_CANONICAL.get(expected, expected if expected in PRIMARY_MARKERS else expected)
    extracted_names = [item.marker for item in extracted]
    if canonical in extracted_names:
        if extracted_names and extracted_names[0] == canonical:
            return "match", canonical
        return "partial", canonical
    if canonical == "anchor_preserved" and "boundary_preserved" in extracted_names:
        return "partial", canonical
    if canonical == "boundary_preserved" and "anchor_preserved" in extracted_names:
        return "partial", canonical
    if canonical == "pressure_frame" and "loaded_interpretation" in extracted_names:
        return "partial", canonical
    if canonical == "loaded_interpretation" and "pressure_frame" in extracted_names:
        return "partial", canonical
    if canonical == "evidence_reanchor" and "boundary_preserved" in extracted_names:
        return "partial", canonical
    return "miss", canonical