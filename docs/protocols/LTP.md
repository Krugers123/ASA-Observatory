# LTP

`LTP = Latent Threshold Protocol`

LTP is a foundational protocol in the broader ASA research lineage.
In practical terms, it is one of the earliest threshold-oriented layers that shaped how ASA thinks about early instability, drift escalation, and operator-facing warning zones.

## Purpose

LTP detects early instability zones before dialogue failure becomes obvious on the surface.

## What It Measures

In the public ASA edition, LTP is reflected through:

- zone classification
- risk score
- escalation logic
- recommendation output

Typical public zones:

- `GREEN`
- `YELLOW`
- `ORANGE`
- `RED`
- `WITHDRAWAL`

## How ASA Uses It

ASA uses LTP as the threshold-sensitive runtime layer that translates low-level drift signals into an operator-readable stability state.

This allows the system to say not only "drift is rising," but also:

- how critical the condition is
- whether re-anchoring is needed
- whether the operator should slow, pause, or yield

In that sense, LTP is not merely one module among others.
It is the threshold logic that helped define the transition from abstract drift observation toward operational observability.

## Operator Meaning

LTP is the bridge between analysis and action.

It turns trajectory diagnostics into:

- current zone
- current risk
- next operator step

## Public Scope

The public repository exposes the operational surface of LTP, not the full internal calibration or all research variants.

## Why It Matters Historically

Within the public story of ASA, LTP matters because it made one key idea operational:

`a dialogue may still look coherent locally while already becoming unstable at the trajectory level`

That threshold insight is one of the main bridges between the broader Symbioza research framework and the public ASA Observatory.

## Source Context

Broader protocol background:

[Manifest-Symbiozy-2025](https://github.com/Krugers123/Manifest-Symbiozy-2025)
