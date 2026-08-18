---
title: "Outcome-Bound S1-R1 — Natural identity sampling protocol"
status: designed
canonicality: operative
created: "2026-08-18"
updated: "2026-08-18"
triggered_by: "conversation:user-request-2026-08-18-continue-outcome-bound"
---

# S1-R1 protocol

## 1. Purpose

Test whether the unchanged S0-R3 C/S/B/E/T/Q admission rule is prospectively usable on a tiny natural Bureau sample after removing the exact sampling ambiguity that rejected S1.

S1-R1 is not an efficacy experiment and does not compare Minimal versus Full.

## 2. Frozen semantic authority

The admission semantics are exactly the S0-R3 protocol merged in PR #344. S1-R1 does not redefine C, S, B, E, T, Q, subject equivalence, baseline rules, or the prior-act decision procedure.

## 3. Sampling unit — one candidate identity

One natural treatment unit is exactly one canonical Bureau `candidate_id` whose **first-ever canonical `candidate_task` event of any provenance** itself carries `operator_intake` and occurs after S1-R1 activation.

For each candidate identity, define:

`identity_first_event_id = min(event_id)` across the complete authoritative Bureau StateStore event journal for every `live-register` event whose payload is `kind=candidate_task` and contains that exact `candidate_id`, regardless of whether the event already carries `operator_intake`.

The identity creates an S1-R1 sampling unit only when that exact first-ever event carries `operator_intake`. A candidate identity with any older candidate event is pre-existing forever for S1-R1, even if `operator_intake` is attached only by a later revision. The identity-first event is the only event that can create a sampling unit.

Consequences:

- a candidate identity that existed before activation is never an S1-R1 unit, even if it receives later supersession events or acquires `operator_intake` only later;
- a new post-activation identity consumes at most one slot;
- later corrections, refinements, supersessions, repeated source observations or status updates for that identity create no new slot;
- an idempotent replay that creates no new canonical event creates no unit;
- deduplication onto a pre-existing candidate identity creates no new unit;
- no content, repository, risk, distance, outcome, capture state or task state may filter identities after the identity-first rule.

This identity definition is frozen before any natural S1-R1 treatment arrival.

## 4. Activation boundary

The PR branch is pre-activation only: declaring the experiment as `testing` in that branch creates no natural-sampling effect before merge. Natural sampling is prohibited until the exact final author revision has passed repository validation and an independent exact-head semantic review with zero material sampling-contract findings.

If that exact reviewed revision is merged, define:

`activation_at = GitHub merged_at + 300 seconds`.

The five-minute cooling interval is part of the frozen protocol. It prevents merge handling itself from becoming an implicit case-capture race.

A candidate identity is post-activation only when its identity-first Bureau event has `created_at >= activation_at`. If the authoritative merge timestamp or the identity-first event timestamp cannot be read exactly, stop and reject rather than infer ordering.

## 5. Deterministic treatment sequence

Build the complete candidate-identity projection from the authoritative StateStore journal, compute the first canonical `candidate_task` event per identity across all provenance shapes, require that exact first event to carry `operator_intake`, keep only identities whose first event is post-activation, then sort by `identity_first_event_id` ascending.

The first three identities are exactly `S1R1-N01`, `S1R1-N02`, `S1R1-N03`.

Every selected identity consumes its slot permanently. D0, already-mutating, unbindable, result-known, or otherwise inconvenient cases remain selected evidence. There is no replacement or backfill.

If two identity-first events have the same timestamp, event id determines order. Timestamp does not break event-id ordering.

## 6. Capture contract

For each selected identity, S1-R1 attempts one shadow capture without delaying productive work. The capture is bound to the exact identity-first event, never to a later superseding event.

Record:

- slot and identity-first event id;
- candidate id and exact identity-first event digest/reference;
- capture start/freeze or stop time;
- productive-mutation state at capture start;
- C/S/B/E/T/Q bindings under unchanged S0-R3;
- S0-R3 classification;
- bounded failure reason when binding cannot complete;
- elapsed handling time;
- authority-violation count.

If productive mutation already began, record `capture_missed_before_mutation`. If the result is already known, record `result_informed_binding_failure`. If capture would delay productive work, record `capture_not_frozen_in_time`. A non-D0 case whose C/S/B/E/T cannot be bound prospectively is a binding failure. The slot remains consumed.

Later supersession evidence may be referenced as later context but may not replace the identity-first claim snapshot C.

## 7. Pre-activation adversarial review gate

Before merge, an independent exact-head reviewer must reproduce the sampling outcome for the fixed U01-U13 cases in `sampling-cases.md` and attack at least:

- pre-existing identity plus post-activation supersession;
- new identity plus multiple later supersessions;
- deduplication onto old identity;
- correction arriving before observer capture;
- D0 new identity;
- missed capture;
- event timestamp tie;
- result-informed relabelling.

Any material disagreement, post-observation degree of freedom, need for a new production field/validator, or ambiguity about which event creates a unit rejects the author revision before activation.

## 8. Natural-sample independent review

After all three slots are consumed, an independent exact-revision reviewer verifies:

1. exact activation timestamp;
2. complete identity-first candidate projection;
3. first three post-activation identities in event-id order;
4. no replacement/backfill;
5. exact identity-first-event binding for every capture;
6. C/S/B/E/T/Q reproduction where attempted;
7. capture timing and cost;
8. zero productive authority effects.

A changed slot identity, changed classification, required semantic downgrade, retrospective substitution, or unrecorded authority effect is material.

## 9. Metrics and gate

Primary metric: `natural_identity_binding_failure_count`.

Count one failure for each selected slot with capture-missed, late freeze, result-informed binding, material review disagreement, authority violation, or non-D0 prospective C/S/B/E/T failure.

PASS only if:

- exactly three identities are selected by the frozen identity-first rule;
- all three slots are consumed without replacement/backfill;
- failure count is zero;
- independent material disagreements are zero;
- authority violations are zero;
- median capture effort is at most 600 seconds;
- at least two selected cases are non-D0 with definitive complete C/S/B/E/T bindings.

REJECT on any sampling-integrity ambiguity, any binding failure, any authority/integrity violation, or median effort above 600 seconds.

INCONCLUSIVE only when the sequence and captures are valid with zero failures but fewer than two informative non-D0 cases occur. Never backfill.

## 10. Stop and non-promotion rules

Stop immediately if the complete identity-first sequence cannot be proven, an identity-first record would need rewriting, case selection would require outcome knowledge, productive work would be delayed, technical truth would need copying instead of referencing, or a new validator/runtime/control surface would be required.

S1-R1 cannot reopen P1, authorize P2/P3, compare Minimal versus Full, alter Bureau/Grabowski/Chronik/Leitstand, or change routing, queue, policy, merge or deployment behavior.
