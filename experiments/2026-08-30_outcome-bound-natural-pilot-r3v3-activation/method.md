---
title: "Outcome-Bound natural pilot — R3 v3 prospective activation"
status: designed
canonicality: exploratory
created: "2026-08-30"
updated: "2026-08-30"
triggered_by: "direct-user:outcome-bound-natural-pilot-r3v3-activation-20260830; predecessor:2026-08-24_outcome-bound-natural-pilot-sampling-unit-r3-v3"
---

# R3 v3 Natural-Pilot activation protocol

## 1. Purpose

This revision does not change the passed R3 v3 sampling semantics. It activates exactly one prospective three-slot Natural Pilot only after this revision has been independently reviewed, merged, and a separate authoritative Bureau activation marker has been appended. No natural case may be selected, reconstructed or backfilled before that marker exists.

The inherited R3 v3 contract remains authoritative for canonical identity, birth proof, Phase-S slot construction, Phase-G naturalness/self-interference and no-backfill semantics. In particular, every fully provable post-A `candidate_identity_birth` creates exactly one fixed ordinal before any gate decision.

## 2. Activation boundary A

The activation boundary is not a wall-clock timestamp and is not chosen from observed candidate outcomes. After this exact revision is merged, the controller appends exactly one Bureau `candidate_task` operator-intake marker with idempotency key `outcome-bound-natural-pilot-r3v3-activation-20260830-v1`.

The authoritative numeric Bureau event id returned by that append is **A**. The marker itself is experiment-caused but has `event_id == A`; the cohort admits only births with `identity_first_event.event_id > A`, so the marker cannot consume a pilot slot. No repository, PR or review mutation required to establish this revision may occur after A.

Activation is valid only when the marker records and binds all of the following preconditions observed immediately before append:

- this Vibe-Lab activation revision is merged on `main`;
- the R3 v3 result remains `verdict: confirms`, `natural_cases_taken: 0`, `pilot_authorized: false` before this successor activation;
- a fresh Bureau `live-list --kind candidate_task` observation reports `coverage_complete=true` and `projection_source=complete_event_scan`;
- the same observation reports the complete projection size and the latest displayed candidate event used as the pre-marker high-water observation;
- no already-observed event is reclassified as post-A.

If the marker append is ambiguous, no second marker is written until exact idempotency-key readback establishes whether the first append exists.

## 3. Fixed cohort

Before assigning post-A pilot slots, freeze exactly three negative eligibility sentinels: the last three fully provable canonical candidate identity births with `identity_first_event.event_id < A`, ordered by event id. They exist only to verify that the activation boundary excludes pre-A births; they are never pilot cases, do not consume N, and their outcomes are not used for efficacy comparison.

`N = 3`. The cohort consists of the first three **fully provable** canonical candidate-identity births with `identity_first_event.event_id > A`, ordered only by authoritative numeric event id.

For each fully proved birth, Phase S assigns the next ordinal before any admission decision. A slot can never be replaced, skipped, renumbered or backfilled.

A post-A event that is only a supersession or later event of a pre-existing canonical candidate identity consumes no new slot because it is not an identity birth.

## 4. Slot outcomes

Each assigned slot terminates in exactly one admission state:

- `frozen`: C/S/B/E/T/Q were prospectively bound before productive mutation;
- `capture_missed_before_mutation`: productive mutation had already begun before the required binding;
- `capture_not_frozen_in_time`: binding would have delayed productive work;
- `result_informed_binding_failure`: outcome/result knowledge existed before binding;
- `not_applicable`: D0;
- `indeterminate`: C/S/B/E/T/Q could not be bound reproducibly;
- `rejected_interference`: the experiment influenced a fully proved birth;
- `rejected_ambiguous_causation`: independence from the experiment cannot be proved.

The last two states consume their already-assigned slot and stop this revision immediately. They accept zero natural evidence.

## 5. Successful capture payload

A `frozen` slot records only the already established S0-R3 admission bindings:

- C — Claim Snapshot
- S — Subject
- B — Baseline
- E — Target Effect
- T — Transition Path
- Q — Delivery Qualifiers

It additionally records slot/anchor identity, freeze time, handling duration, outcome-distance classification, primary-evidence references and authority violations. It must not copy mutable technical truth and does not create a Full Outcome Case.

## 6. Prospective timing rule

For a potentially capturable birth, C/S/B/E/T/Q must be frozen before productive mutation. The capture observer may not delay, reprioritize, split, merge or reshape productive work. If timely capture is impossible, the slot records the corresponding failure state rather than delaying execution.

## 7. Three-slot stop and review

The pilot stops when three ordinals have been consumed or earlier when R3 v3 requires fail-closed termination. No fourth case can replace an uninformative or failed slot.

After termination, freeze the exact evidence revision. An independent exact-head reviewer must verify: activation-marker identity and A; first-three-birth ordering; no replacement/backfill; complete birth proof; capture-before-mutation; C/S/B/E/T/Q reproducibility; classifications; baseline stability; target-effect versus qualifier separation; authority boundaries; and measured handling time.

## 8. Mechanical S1 decision

PASS requires all of:

- exactly 3/3 slots in canonical order;
- zero binding failures;
- zero material review disagreements;
- zero authority violations;
- zero replacement/backfill;
- median handling time <= 10 minutes;
- at least two definitive non-D0 slots.

REJECT occurs on any real binding failure, experiment interference, ambiguous causation or other preregistered material protocol violation.

INCONCLUSIVE is permitted only when the mechanics succeed but the fixed three slots contain fewer than two informative non-D0 cases. No backfill is allowed; any successor is a new prospective cohort.

## 9. Non-claims

This pilot tests admission feasibility only. It does not test Minimal versus Full, does not establish Outcome-Case efficacy, and authorizes no validator, Bureau field, Grabowski runtime integration, routing, queue, policy, deployment, automatic task creation, Chronik integration, Leitstand integration or product integration. A Decision-Impact pilot requires a separate post-PASS decision.
