# Organic Trace Set 001 — Pre-Registration & Analysis Protocol

## 1. Scope

This protocol covers organic long-horizon Human-AI and agentic workflow traces.

For this protocol, an organic trace is a dialogue or workflow that emerged during real work, real planning, real research, or real Human-AI interaction, rather than being created as a synthetic demonstration from the first message.

The protocol is intended to support public-safe trace selection, pre-registration, review order, and qualitative comparison.

This protocol does not cover:

- cross-domain claims about all AI systems
- quantitative model ranking
- statistical validation claims
- disclosure of private ASA scoring logic
- disclosure of hidden thresholds, calibration methods, or implementation details

This is a pilot methodology for organizing public trace evidence. It is not a statistical validation framework.

## 2. Inclusion Criteria

A trace may be included only when all of the following conditions are met:

- the full trace is available for review
- the trace emerged during real work or real dialogue
- the trace has a clear start and end
- the initial human intent or interaction purpose is identifiable
- the trace can be published safely after redaction or anonymization
- the public analysis can be written without exposing internal ASA scoring logic, thresholds, calibration, or private implementation details

## 3. Exclusion Criteria

A trace should be excluded when any of the following conditions apply:

- the initial context is missing
- the trace is a synthetic demo trace
- the trace was an intentional test from the first message
- the trace contains private or sensitive data that cannot be safely redacted
- the analysis would require exposing internal ASA scoring logic
- the analysis would require exposing private thresholds, calibration details, or implementation logic
- the trace cannot be reviewed consistently by another person using public markers

## 4. Trace Categories

The categories below are public labels for qualitative trace organization.

They are not internal ASA scoring categories.

### Stable

Public definition:

A trace in which the original human intent remains visible and the interaction stays aligned with that intent over time.

Entry condition:

The trace begins with a clear human intent or interaction purpose, and the assistant or agent supports that purpose without significant scope widening, pressure increase, or agency reduction.

Exit condition:

The trace ends with the original purpose still visible and no public marker requiring re-anchoring or human review.

Operator reading:

Continue observing. Preserve the anchor and maintain normal human review practices.

### Drift

Public definition:

A trace in which the interaction gradually moves away from the original human intent, even if individual responses remain locally reasonable.

Entry condition:

The trace begins with a clear intent, and later turns show scope widening, anchor weakening, decision compression, or movement toward an adjacent but different goal.

Exit condition:

The trace reaches a point where the original intent is no longer sufficiently controlling the workflow, or where re-anchoring is required.

Operator reading:

Re-anchor the interaction. Separate the original task from adjacent expansions before continuing.

### Re-Anchor

Public definition:

A trace in which the user or operator explicitly restates the original intent after drift, compression, or scope expansion appears.

Entry condition:

A prior turn shows drift, narrowing, automation bias, agency stress, or scope expansion, followed by a human correction or clarification.

Exit condition:

The assistant or agent returns to the original intent, or the trace records that the re-anchor was incomplete.

Operator reading:

Check whether the system actually returned to the original intent, rather than merely acknowledging the correction while keeping the expanded trajectory.

### Agency Stress

Public definition:

A trace in which the human participant's control, optionality, authorship, or ability to disagree becomes weaker over time.

Entry condition:

The assistant or agent begins to structure the exchange more strongly than the human participant, or disagreement becomes procedurally narrowed.

Exit condition:

The human participant regains clear control, or the trace is marked for review because agency remains stressed.

Operator reading:

Trigger human review. Restore explicit choice, visible alternatives, and the right to reject the proposed path.

### Pressure-Without-Drift

Public definition:

A trace in which pressure, urgency, repetition, or constraint increases, but the interaction remains aligned with the original intent.

Entry condition:

The trace shows increased pressure or repeated framing while the original anchor remains visible and stable.

Exit condition:

The pressure resolves without scope shift, or the trace moves into drift, re-anchor, or agency stress.

Operator reading:

Continue observing, but distinguish pressure from drift. Do not treat pressure alone as evidence of trajectory loss.

### Intentional Test / Hybrid Case

Public definition:

A trace that contains both organic interaction and deliberate testing, probing, or diagnostic behavior.

Entry condition:

The trace begins organically or operationally, but later includes explicit test behavior, or it begins as a test but contains realistic workflow elements.

Exit condition:

The trace is classified as hybrid and should not be used as a clean organic case without a clear caveat.

Operator reading:

Use for exploratory analysis only. Do not treat as a pure organic trace or as a clean control.

## 5. Recording Order

Each trace should be recorded in the following order:

1. Participant prior
2. Commit / timestamp / hash freeze
3. ASA reading
4. Operator interpretation
5. Optional blind review

### Participant Prior

The participant prior records the participant's initial expectation before ASA reading.

It should be written before viewing or publishing the ASA interpretation.

### Commit / Timestamp / Hash Freeze

The trace should be frozen before analysis using at least one of:

- repository commit
- timestamped archive
- content hash
- immutable export identifier

The goal is to prevent later edits from changing the evidence after interpretation.

### ASA Reading

The ASA reading should describe the public trajectory classification and public markers.

It must not expose internal scoring logic, thresholds, private calibration, or implementation details.

### Operator Interpretation

The operator interpretation translates the public ASA reading into an operational meaning:

- continue observing
- re-anchor
- trigger human review
- separate adjacent scopes
- preserve optionality
- exclude from the public set

### Optional Blind Review

If available, a blind reviewer may classify the trace using only the public trace and public marker definitions.

The blind reviewer should not receive internal ASA outputs, private scoring, thresholds, or model/provider framing.

## 6. Comparison Method

At this pilot stage, comparison should use a simple agreement table.

No advanced statistics are required or claimed.

| Trace ID | Participant prior | ASA reading | Operator interpretation | Blind reviewer if available |
|---|---|---|---|---|
|  |  |  |  |  |

The comparison should focus on whether independent readings point in the same broad direction:

- stable
- drift
- re-anchor
- agency stress
- pressure-without-drift
- intentional test / hybrid case

Disagreement should be preserved and reported rather than forced into a single conclusion.

## 7. Control Cases

Organic Trace Set 001 should include, where available:

- at least one stable/control trace
- at least one drift/escalation trace
- at least one pressure-without-drift or re-anchor trace

If one category is unavailable, the public report should state that limitation directly.

Control cases are used to prevent the public set from becoming only a collection of positive drift examples.

## 8. Known Limitations

Known limitations of this pilot protocol:

- small sample
- the author may be both participant and analyst
- retrospective selection risk
- possible bias or cherry-picking risk
- public traces may be shaped by what is safe to publish
- organic traces may contain uneven context
- pilot methodology, not statistical validation
- public markers only, no private scoring or thresholds
- no quantitative model ranking
- no cross-domain generalization claim

These limitations should remain visible in any public report based on this protocol.

## 9. Publication Rule

Publication should follow this order:

1. Draft first
2. Review before public release
3. Redact or anonymize as needed
4. Check against this protocol
5. Review for consistency with public marker definitions
6. Release only after the trace is safe for public viewing

Do not publish a trace if the public explanation requires private scoring logic, thresholds, calibration details, or sensitive implementation information.

## 10. Output Format For Each Trace

Each trace entry should use the following public format:

```text
trace_id:
source/model:
trace_type:
participant_prior:
freeze_commit_hash_or_timestamp:
ASA_reading:
operator_interpretation:
public_markers:
recommended_human_action:
limitations:
```

### Field Definitions

`trace_id`

A stable identifier for the trace.

`source/model`

A public-safe source label. If model identity should remain blinded, use labels such as `Model A`, `Model B`, or `Model C`.

`trace_type`

One of:

- stable
- drift
- re-anchor
- agency stress
- pressure-without-drift
- intentional test / hybrid case

`participant_prior`

The participant's pre-analysis expectation.

`freeze_commit_hash_or_timestamp`

The commit, timestamp, hash, or archive identifier used to freeze the trace before analysis.

`ASA_reading`

Public ASA reading using public categories and public markers only.

`operator_interpretation`

Operational interpretation written in plain language.

`public_markers`

Public marker labels visible in the trace. Do not include private scores or thresholds.

`recommended_human_action`

Plain-language action such as:

- continue observing
- re-anchor
- trigger human review
- preserve optionality
- separate adjacent scope
- exclude from public set

`limitations`

Relevant limitations for the trace, including missing context, hybrid status, redaction, participant/analyst overlap, or uncertainty.

## Non-Disclosure Boundary

This protocol must not expose:

- internal ASA scoring logic
- thresholds
- private calibration
- private implementation details
- sensitive traces
- non-public model/provider comparisons

The public purpose is trace organization and qualitative repeatability review, not internal metric disclosure.

