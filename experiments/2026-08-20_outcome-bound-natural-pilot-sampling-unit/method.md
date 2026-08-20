---
title: "Outcome-Bound natural pilot — canonical sampling unit (candidate_identity_birth)"
status: designed
canonicality: operative
created: "2026-08-20"
updated: "2026-08-20"
triggered_by: "bureau-task:OPERATOR-INTEGRATION-LOOP-V1-T035; conversation:user-request-2026-08-20-continue-outcome-bound"
---

# Sampling-unit protocol

## 1. Purpose and limit

This revision freezes exactly one thing: **what counts as one sample element** for a future
Outcome-Bound natural pilot. It answers no question about efficacy, prevalence, feasibility or
cost, and it sets no activation boundary.

S0-R3 admission semantics (C/S/B/E/T/Q) and the S1-R2 canonical-identity and natural-source
contract remain unchanged and are inputs here, not subjects of revision.

This experiment is paper- and adversarial-only. It takes **zero** natural cases, consumes no
Bureau candidate, activates no pilot, and creates no production, validator, routing, queue,
policy, runtime, merge-policy, Chronik or Leitstand surface.

## 2. Unit definition

```text
unit_id            = "sampling-unit/candidate_identity_birth@v1"
unit_key(identity) = canonical_candidate_id(identity_first_event(identity))
```

with the deployed Bureau identity rule carried over unchanged from S1-R2 section 2:

```text
canonical_candidate_id(event) =
  payload.candidate_id                          if present and non-empty
  "candidate-event-" + decimal(event.event_id)  otherwise

identity_first_event(identity) =
  the candidate_task event with the minimum authoritative event_id
  among all candidate_task events whose canonical_candidate_id is that identity
```

**Birth-event anchor.** A sampling unit exists for an identity if and only if that exact
`identity_first_event` itself carries `operator_intake`. The anchor of the unit is that event.
Nothing else anchors a unit: not the observer's first sighting, not the first event carrying
intake, not a wall-clock timestamp, not a PR, not a task registration.

**A unit is a birth, not an arrival.** "Event arrival", "candidate identity birth" and
"supersession" are three different things and are not interchangeable:

| Concept | Anchored by | Creates a unit? |
| --- | --- | --- |
| event arrival | any `candidate_task` event reaching the journal | no |
| candidate identity birth | `identity_first_event` that itself carries `operator_intake` | yes, exactly one |
| supersession / update / correction / enrichment / replay | any later event of an existing identity | no, never |

## 3. Activation boundary

A future pilot must freeze one activation boundary `A` **before** any sampling, where `A` is an
authoritative Bureau `event_id`, not a timestamp and not a date. Event IDs are the only totally
ordered, gap-detectable, observer-independent key available; timestamps are neither unique nor
authoritative for ordering.

`A` is frozen in that pilot's own revision. This revision deliberately does not choose one.

## 4. Inclusion rule

An identity yields exactly one in-sample unit if and only if all of the following hold:

1. `identity_first_event` exists and itself carries `operator_intake`;
2. `identity_first_event.event_id > A`;
3. the birth proof of section 6 is complete;
4. the self-interference boundary of section 7 is not violated.

Conditions 1-3 are decidable from the journal alone. Condition 4 is a **gate on an already fixed
slot**, never a selector (S1-R2 section 3, carried over unchanged).

## 5. Exclusion rule

The following never yield a unit and never consume a slot:

- any identity whose `identity_first_event.event_id <= A` — regardless of how many later events,
  supersessions, corrections, re-registrations or enrichments that identity receives after `A`;
- any event of an identity that already has a unit (one identity, one slot, forever);
- any identity whose `identity_first_event` does not itself carry `operator_intake`, even if a
  later event of the same identity adds intake metadata;
- an idempotent replay that produces no new authoritative event;
- a deduplicated intake request that resolves onto an identity born at or before `A`.

## 6. Birth proof — fail closed

For every candidate unit the pilot must **deterministically prove from the canonical Bureau event
history** that the anchor is the first event of its identity. The proof obligation is:

1. every `candidate_task` event with `event_id <= anchor.event_id` is enumerable without
   truncation, and the projection reports its coverage completeness explicitly;
2. `canonical_candidate_id` resolves without ambiguity for every one of those events;
3. no gap in the authoritative `event_id` sequence below the anchor is unaccounted for.

If any part of the proof is unavailable, ambiguous, or only reconstructible by choosing a rule
after looking at the data, the pilot **stops fail-closed for that slot and for the sequence**. It
must not fall back to a different grouping, widen the window, or pick a semantics after
observation.

Known observability caveat, recorded here rather than assumed away: the Bureau `live-register`
projection reports `history_truncated` together with `history_loaded_records` and
`history_total_records` (observed 2026-08-20: 50 of 3694 loaded, `coverage_complete` true for the
register scope but not for the event history). A pilot therefore needs an explicitly
completeness-reporting read of the event journal, not the default projection.

## 7. Self-interference boundary

The sampling mechanism is passive. It must not:

- create, request or trigger a Bureau candidate;
- delay, accelerate, reprioritize, split, merge or reshape productive work or its candidates;
- ask another actor to time an arrival;
- make its own observation a reason for an arrival to exist.

A candidate that was created, timed or semantically reshaped for the experiment is **excluded**,
and because sequence is fixed before naturalness, that exclusion consumes the fixed ordinal and
falsifies the pilot revision (S1-R2 sections 3-4). It is never a skip.

Operator work unrelated to Outcome-Bound may legitimately produce candidates. The counterfactual
is relative to the Outcome-Bound experiment, not to every cause. But when the pilot observer and
the operator producing candidates are the same identity, independence must be evidenced from
pre-existing artefacts; an unevidenced claim of independence is treated as ambiguous causation and
is fail-closed.

## 8. Ordering rule

In-sample units are ordered by `identity_first_event.event_id` ascending. This order is total, has
no ties, and is fixed the moment the projection is built. Nothing may reorder, skip, replace or
backfill a slot afterwards — not source, risk, repository, distance, D0/`not_applicable`, capture
failure, result knowledge, task state or convenience.

## 9. Stop rule

A future pilot stops at the earliest of:

1. its frozen slot count `N` being filled (`N` frozen before activation; not chosen here);
2. any fail-closed condition of section 6 or section 7;
3. its frozen expiry.

There is no resumption after a fail-closed stop within the same revision, and no backfill of a
consumed or abandoned ordinal.

## 10. Non-claims

This revision does not activate a pilot, does not set `A` or `N`, takes no natural cases, does not
reopen P1, and authorizes neither P2/P3, Minimal-versus-Full, a validator, Bureau or Grabowski
runtime integration, routing, queue, claim, policy, deployment, merge-policy, Chronik, Leitstand
nor product integration. A later pilot requires a separate decision and a separate revision.
