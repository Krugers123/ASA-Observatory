# Example Result: session_01_stable_cooperation

## Session

- `Session ID`: `session_01_stable_cooperation`
- `Anchor`: `Maintain semantic stability across long human-AI interaction loops without modifying the model.`
- `Turns / Snapshots`: `6 / 3`

## ASA Result

### Trajectory Summary

- `Mean drift`: `0.7345`
- `Mean coherence`: `0.4770`
- `Mean threshold pressure`: `0.0683`
- `Mean SPS / CMR`: `0.3784 / 0.5075`

### Latest Snapshot

- `State`: `fragile_coherence`
- `Action`: `require_confirmation`
- `Confidence`: `0.72`
- `Dominant drift type`: `anchor_substitution`
- `Semantic envelope`: `narrowing`
- `Latest drift`: `0.7764`
- `Latest coherence`: `0.5363`
- `Latest threshold`: `0.1153`
- `Latest complementarity`: `0.8333`

## Why It Matters

This is a useful public example because the session is not a dramatic collapse case.

It still shows a meaningful ASA pattern:

- local dialogue structure remains readable
- threshold pressure stays low
- but the trajectory still drifts enough to trigger `fragile_coherence`
- the dominant pattern becomes `anchor_substitution`

In other words:

the conversation does not need to fail visibly for ASA to detect that the original frame is starting to shift.

## Operator Meaning

This is the kind of case where the correct move is not hard intervention but confirmation and re-anchoring.

It shows why ASA focuses on trajectory integrity rather than surface fluency alone.
