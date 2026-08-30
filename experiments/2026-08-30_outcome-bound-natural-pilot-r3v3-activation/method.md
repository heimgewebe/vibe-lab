---
title: "Outcome-Bound natural pilot — R3 v3 prospective activation"
status: testing
canonicality: exploratory
created: "2026-08-30"
updated: "2026-08-30"
triggered_by: "direct-user:outcome-bound-natural-pilot-r3v3-activation-20260830; predecessor:2026-08-24_outcome-bound-natural-pilot-sampling-unit-r3-v3"
---

# R3 v3 Natural-Pilot activation protocol

## 1. Purpose

This revision does not change the passed R3 v3 sampling semantics. When merged, it registers exactly one active testing experiment while `execution_status` remains `designed`; this makes the experiment visible to active-experiment validation and review-date enforcement before any natural case exists. The prospective three-slot cohort itself starts only after a separate authoritative Bureau activation marker has been appended. No natural case may be selected, reconstructed or backfilled before that marker exists.

The inherited R3 v3 contract remains authoritative for canonical identity, birth proof, Phase-S slot construction, Phase-G naturalness/self-interference and no-backfill semantics. In particular, every fully provable post-A `candidate_identity_birth` creates exactly one fixed ordinal before any gate decision.

## 2. Activation boundary A

The activation boundary is not a wall-clock timestamp and is not chosen from observed candidate outcomes. After this exact revision is independently reviewed and merged, the controller appends exactly one Bureau `candidate_task` operator-intake marker with idempotency key `outcome-bound-natural-pilot-r3v3-activation-20260830-v1`.

The authoritative numeric Bureau event id returned by that append is **A**. The marker itself is experiment-caused but has `event_id == A`; the cohort admits only births with `identity_first_event.event_id > A`, so the marker cannot consume a pilot slot. No repository, PR or review mutation required to establish this revision may occur after A.

Activation is valid only when the marker records and binds all of the following preconditions observed immediately before append:

- this Vibe-Lab activation revision is merged on `main`;
- `experiments/active.v1.json` contains this experiment with `state: testing`, `primary_metric: binding_failure_count` and `source_ref` bound to this experiment's `results/decision.yml`;
- the manifest remains `status: testing` and `execution_status: designed`, and `results/decision.yml` remains `verdict: not_executed`, proving that registry activation did not fabricate a natural run;
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

## 4. Slot outcomes and primary-metric mapping

Each assigned slot terminates in exactly one admission state. The state fixes both its contribution to `binding_failure_count` and its mechanical decision effect before any case is observed:

- `frozen`: C/S/B/E/T/Q were prospectively bound before productive mutation; `binding_failure_increment=0`; continue until the fixed cohort ends. It is informative only when its outcome-distance classification is non-D0.
- `not_applicable`: D0; `binding_failure_increment=0`; continue. It is explicitly non-informative and can never be replaced.
- `capture_missed_before_mutation`: productive mutation had already begun before the required binding; `binding_failure_increment=1`; immediate REJECT.
- `capture_not_frozen_in_time`: binding could not be completed without delaying productive work; `binding_failure_increment=1`; immediate REJECT.
- `result_informed_binding_failure`: outcome/result knowledge existed before binding; `binding_failure_increment=1`; immediate REJECT.
- `indeterminate`: C/S/B/E/T/Q or required timing evidence could not be bound reproducibly; `binding_failure_increment=1`; immediate REJECT.
- `rejected_interference`: the experiment influenced a fully proved birth; `binding_failure_increment=1`; immediate REJECT and zero accepted natural evidence.
- `rejected_ambiguous_causation`: independence from the experiment cannot be proved; `binding_failure_increment=1`; immediate REJECT and zero accepted natural evidence.

`binding_failure_count` is the sum of the frozen per-slot increments above. There is no reviewer discretion to reclassify an increment after seeing later slots. Any of the six failure states already falsifies this revision; later births cannot repair, replace or dilute that failure. Authority violations, noncanonical ordering, backfill/replacement or other preregistered material protocol violations also cause REJECT even if `binding_failure_count` remains zero.

## 5. Successful capture payload

A `frozen` slot records only the already established S0-R3 admission bindings:

- C — Claim Snapshot
- S — Subject
- B — Baseline
- E — Target Effect
- T — Transition Path
- Q — Delivery Qualifiers

It additionally records slot/anchor identity, the timing fields defined below, outcome-distance classification, primary-evidence references and authority violations. It must not copy mutable technical truth and does not create a Full Outcome Case.

## 6. Prospective timing and durable terminalization

For a potentially capturable birth, C/S/B/E/T/Q must be frozen before productive mutation. The capture observer may not delay, reprioritize, split, merge or reshape productive work. If timely capture is impossible, the slot records the corresponding failure state rather than delaying execution.

The handling-time and terminalization contract is fixed as follows for every consumed slot:

1. `handling_started_at_monotonic_ns` is sampled immediately **before** issuing the first authoritative candidate-task read in the scan that discovers the candidate or begins the proof that it is the next eligible canonical identity birth. Candidate detection, complete-projection checks, identity/birth proof, naturalness checks and all C/S/B/E/T/Q analysis are therefore inside the clock.
2. Once the canonical birth and ordinal are proved, the slot receives deterministic identity `slot_id = sha256(experiment_id || A || ordinal || canonical_candidate_id || birth_event_id)`. All terminal persistence and reconciliation keys are derived from this identity; a later retry cannot silently create a different slot.
3. The observer constructs a complete **provisional terminal payload** containing the proposed admission state, fixed `binding_failure_increment`, required primary-evidence references, C/S/B/E/T/Q when applicable, outcome-distance classification, authority findings and UTC provenance timestamps. Failed-capture classification is inside this payload and therefore inside the clock.
4. `handling_finished_at_monotonic_ns` is sampled immediately after that provisional terminal payload is fully determined in memory and **before** any terminal persistence. `handling_seconds = (handling_finished_at_monotonic_ns - handling_started_at_monotonic_ns) / 1_000_000_000`. No candidate detection, completeness scan, identity/birth proof, evidence read, retry or analysis interval before this boundary may be subtracted.
5. The observer constructs one immutable `slot_terminal_intent` with deterministic `terminal_id = "slot-terminal:" + slot_id`. It binds the provisional payload hash, start, finish and `handling_seconds`. The terminal intent is appended idempotently and then read back by exact `terminal_id`. Persistence/readback latency is explicitly excluded from `handling_seconds`; it is a separate hard validity gate.
6. A slot becomes terminal only when exact readback yields one valid terminal record whose `terminal_id`, `slot_id`, provisional-payload hash, timing fields and state all match the intended record. A returned write error or an unknown/ambiguous write outcome never authorizes an immediate second mutation. It enters `terminal_reconciliation` and first performs read-only lookup by exact `terminal_id`.
7. Reconciliation has only three outcomes:
   - matching terminal record found: accept that record and terminalize the slot;
   - authoritative absence of the intended terminal record proved: append exactly one idempotent failure record with `failure_id = "slot-terminal-failure:" + slot_id`, state `indeterminate`, `binding_failure_increment=1`, reason `terminal_persistence_verification_failed`, and hashes of the intended terminal intent and provisional payload; exact readback of that failure record terminalizes the slot and immediately REJECTS;
   - neither presence nor absence can be established: set experiment control state `persistence_outcome_unknown`, stop all further slot handling and prohibit PASS or INCONCLUSIVE until reconciliation becomes possible.
8. If the failure-record append itself has an ambiguous outcome, the controller again performs read-only lookup by exact `failure_id` before any retry. A retry of the same idempotent failure record is permitted only after authoritative absence is proved. While neither a matching terminal record nor a verified failure record exists, the experiment remains halted at `persistence_outcome_unknown`; no later birth can be consumed. If that ambiguity remains unresolved at closeout, it is a preregistered material protocol violation and the cohort cannot pass.
9. A separate `persistence_verified_at_monotonic_ns` may be sampled after successful readback for audit provenance only and is never part of the cost metric. If monotonic-clock continuity is lost before `handling_finished_at_monotonic_ns`, the intended terminal state is `indeterminate` with increment one and follows the same deterministic terminalization/reconciliation path.
10. If productive mutation begins before a successful C/S/B/E/T/Q freeze, the state cannot be `frozen`; it must take the applicable failure state. The observer never delays productive execution merely to improve the measured duration.

For a scan that finds no new eligible identity birth, no slot is consumed and no handling duration is recorded. Once a scan discovers or begins proof of a birth that becomes a consumed slot, its request-start boundary above is authoritative and cannot be moved later.

## 7. Three-slot stop and review

The pilot stops when three ordinals have been consumed or immediately when a failure state or inherited R3 v3 rule requires fail-closed termination. No fourth case can replace an uninformative or failed slot.

After termination, freeze the exact evidence revision. An independent exact-head reviewer must verify: activation-marker identity and A; first-three-birth ordering; no replacement/backfill; complete birth proof; capture-before-mutation; C/S/B/E/T/Q reproducibility; exhaustive state-to-metric mapping; classifications; baseline stability; target-effect versus qualifier separation; authority boundaries; measured handling time with the fixed in-memory finish boundary; deterministic slot/terminal identities; and the terminal persistence/reconciliation state machine.

## 8. Mechanical S1 decision

PASS requires all of:

- exactly 3/3 slots in canonical order;
- `binding_failure_count == 0` under the fixed state mapping;
- zero material review disagreements;
- zero authority violations;
- zero replacement/backfill;
- median `handling_seconds` across the three consumed slots <= 600 seconds;
- at least two definitive non-D0 slots;
- no unresolved `persistence_outcome_unknown` state.

REJECT occurs immediately on any slot with `binding_failure_increment=1`, experiment interference, ambiguous causation, authority violation, replacement/backfill, noncanonical ordering or other preregistered material protocol violation. An unresolved `persistence_outcome_unknown` state cannot be treated as PASS or INCONCLUSIVE and, if still unresolved at closeout, is itself a material protocol violation.

INCONCLUSIVE is permitted only when the mechanics succeed, `binding_failure_count == 0`, all three fixed slots are consumed, no persistence ambiguity remains, and fewer than two are informative non-D0 cases. No backfill is allowed; any successor is a new prospective cohort.

## 9. Non-claims

This pilot tests admission feasibility only. It does not test Minimal versus Full, does not establish Outcome-Case efficacy, and authorizes no validator, Bureau field, Grabowski runtime integration, routing, queue, policy, deployment, automatic task creation, Chronik integration, Leitstand integration or product integration. A Decision-Impact pilot requires a separate post-PASS decision.
