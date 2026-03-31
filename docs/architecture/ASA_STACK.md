# ASA Protocol Stack

ASA Observatory is the public technical surface of a broader research architecture.

In public form, the stack can be read as three layers:

1. `Human-AI Interaction Layer`
   - the visible dialogue surface
   - user prompts, model responses, follow-up turns

2. `Drift Observability Layer (DOL)`
   - trajectory-level observation of meaning over time
   - tracks drift, coherence, threshold pressure, complementarity, and semantic envelope change
   - this is where protocol layers such as `LTP`, `CBP`, `SRE`, `OCSP`, and `SCE` become operational

3. `Sovereignty Gate (SG)`
   - the operator-facing decision layer
   - turns signals into readable action:
     - zone
     - risk
     - recommendation
     - session summary
   - keeps decision sovereignty on the human/operator side

## Why "Asymmetric"

The asymmetry is intentional:

- the monitored model does not need access to the monitoring layer
- the observability logic remains external
- the operator keeps final control over meaning, escalation, and intervention

ASA is therefore not a model-control system.
It is an external observability architecture for long-horizon stability.

## Public Protocol Surface

The public edition of ASA Observatory exposes a compact protocol surface:

- `LTP` - threshold zone and instability escalation logic
- `CBP` - cognitive buffer protection / agency pressure
- `SRE` - semantic resonance and entropy balance
- `OCSP` - observability scope and propagation risk
- `SCE` - counterfactual robustness and intervention priority

These protocol cards describe the public technical role of each layer.
Within this stack, `LTP` should be read as the foundational threshold protocol from which much of the public ASA runtime logic historically grew:

- [LTP (foundational protocol)](../protocols/LTP.md)
- [CBP](../protocols/CBP.md)
- [SRE](../protocols/SRE.md)
- [OCSP](../protocols/OCSP.md)
- [SCE](../protocols/SCE.md)

## Relation to the Manifest Repository

`ASA-Observatory` is the technical instrument.

`Manifest-Symbiozy-2025` remains the source repository for the broader conceptual, philosophical, and doctrinal framework:

[Manifest-Symbiozy-2025](https://github.com/Krugers123/Manifest-Symbiozy-2025)

This split is deliberate:

- `ASA-Observatory` = public working system and technical observability layer
- `Manifest-Symbiozy-2025` = source doctrine, research framing, and deeper protocol background
