# Example Result: session_05_fragile_coherence

## Session

- `Session ID`: `session_05_fragile_coherence`
- `Anchor`: `Detect a situation where coherence exists but becomes unstable.`
- `Turns / Snapshots`: `8 / 4`

## ASA Result

### Trajectory Summary

- `Mean drift`: `0.8055`
- `Mean coherence`: `0.4136`
- `Mean threshold pressure`: `0.2795`
- `Mean SPS / CMR`: `0.3758 / 0.4471`

### Latest Snapshot

- `State`: `drift_risk`
- `Action`: `reanchor`
- `Confidence`: `0.82`
- `Dominant drift type`: `context_fracture`
- `Semantic envelope`: `brittle`
- `Latest drift`: `0.8314`
- `Latest coherence`: `0.4956`
- `Latest threshold`: `0.3617`
- `Latest complementarity`: `0.8750`

## Why It Matters

This session is a strong public example of a dialogue that still contains coherence, but no longer carries it safely.

The key pattern is:

- coherence is not absent
- complementarity is still relatively high
- but drift rises enough for the state to become `drift_risk`
- the semantic envelope hardens into `brittle`
- the dominant pattern becomes `context_fracture`

This is exactly the kind of case where ASA helps distinguish:

- fluent interaction
- from stable interaction

## Operator Meaning

The recommended move is `reanchor`.

That makes this session a good demonstration of why observability is useful:

the conversation does not have to look broken for the system to show that the shared frame is becoming structurally fragile.
