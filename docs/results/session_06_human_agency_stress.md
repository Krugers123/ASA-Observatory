# Example Result: session_06_human_agency_stress

## Session

- `Session ID`: `session_06_human_agency_stress`
- `Anchor`: `Test complementarity under weaker human control.`
- `Turns / Snapshots`: `8 / 4`

## ASA Result

### Trajectory Summary

- `Mean drift`: `0.9154`
- `Mean coherence`: `0.3000`
- `Mean threshold pressure`: `0.0471`
- `Mean SPS / CMR`: `0.2489 / 0.3222`

### Latest Snapshot

- `State`: `drift_risk`
- `Action`: `reanchor`
- `Confidence`: `0.90`
- `Dominant drift type`: `context_fracture`
- `Semantic envelope`: `brittle`
- `Latest drift`: `0.8885`
- `Latest coherence`: `0.3607`
- `Latest threshold`: `0.1760`
- `Latest complementarity`: `0.9167`

## Why It Matters

This session is useful because it shows that high complementarity alone is not enough to guarantee stability.

ASA still detects a strong instability pattern:

- drift remains very high
- coherence remains weak
- the envelope becomes `brittle`
- the dominant pattern is `context_fracture`

This matters because some conversations can still feel cooperative while the human side is losing effective steering power.

## Operator Meaning

This is a strong example of why ASA tracks agency-sensitive trajectory conditions instead of treating smooth collaboration as automatically safe.

The recommended move is to re-anchor the interaction before the structural frame weakens further.
