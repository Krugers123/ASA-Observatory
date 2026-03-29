# ASA External Operator API

Minimal operator-facing API for external systems that only need drift, state, and next-step information.

## Purpose

This layer is intended for:

- external operator consoles
- monitoring services
- lightweight integrations
- other AI systems that need compact ASA results

The goal is to expose only the minimum actionable observability surface.

## Endpoints

### `GET /operator/overview`

Returns a compact overview of warning and critical sessions.

Use this when an external system needs fast triage.

### `GET /operator/sessions/{session_id}/drift`

Returns the current drift/instability summary for a single session.

Use this when an external client needs:

- current drift level
- latest state
- dominant drift type
- semantic envelope state
- LTP zone
- LTP risk
- next operator step

## Recommended read flow

1. Poll `GET /operator/overview`
2. Detect critical or warning sessions
3. Query `GET /operator/sessions/{session_id}/drift`
4. Route the result to:
   - an operator UI
   - an alerting service
   - another AI system

## Minimum fields to read

If you want only the essential drift/stability payload, read:

- `drift_score`
- `latest_state`
- `dominant_drift_type`
- `semantic_envelope_state`
- `ltp.zone`
- `ltp.risk`
- `ltp.recommendation`

This is enough for most operator-facing decisions.

## Example PowerShell

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/operator/overview" | ConvertTo-Json -Depth 6
```

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/operator/sessions/session_05_fragile_coherence/drift" | ConvertTo-Json -Depth 6
```
