# ASA Markers v1.1.1 PL/EN Candidate

Status: public-safe experimental marker layer.

This module extracts local trajectory markers per turn and supports public demo inspection, dashboard readouts, and lightweight operator review.

It does not replace ASA final state/action logic and should not be presented as statistical validation by itself.

## Public Markers

- `anchor_preserved`
- `scope_expansion`
- `pressure_frame`
- `loaded_interpretation`
- `topic_switch_declared`
- `boundary_preserved`
- `evidence_reanchor`
- `methodology_reanchor`

## Public Integration Rule

Use this as an observational marker layer feeding public dashboards, examples, and demo reports.

Do not expose private scoring thresholds, calibration internals, proprietary algorithms, or sensitive deployment details.

## Version Note

`v1.1.1-pl-en-candidate` expands the public marker vocabulary for short research traces such as `session_01_stable_cooperation` and `session_02_drift_escalation`, while preserving the same public-safe boundary.
