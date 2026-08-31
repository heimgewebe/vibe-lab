---
title: "Outcome-Bound natural pilot — R3 v3 prospective activation"
status: testing
canonicality: exploratory
created: "2026-08-30"
updated: "2026-08-31"
triggered_by: "direct-user:outcome-bound-natural-pilot-r3v3-activation-20260830; predecessor:2026-08-24_outcome-bound-natural-pilot-sampling-unit-r3-v3"
---

# R3 v3 Natural-Pilot activation protocol

## 1. Purpose

This revision does not change the passed R3 v3 sampling semantics. When merged, it registers exactly one active testing experiment while `execution_status` remains `designed`; this makes the experiment visible to active-experiment validation and review-date enforcement without fabricating a natural run. The prospective three-slot cohort starts only after a separate authoritative Bureau activation marker exists.

The inherited R3 v3 contract remains authoritative for canonical identity, birth proof, Phase-S ordering, Phase-G naturalness/self-interference and no-backfill semantics. Every fully provable post-A `candidate_identity_birth` therefore owns exactly one fixed ordinal before any admission decision.

## 2. Activation boundary A

The activation boundary is not a wall-clock timestamp and is not chosen from observed candidate outcomes. After this exact revision is independently reviewed and merged, the controller may append exactly one Bureau `candidate_task` operator-intake marker with idempotency key `outcome-bound-natural-pilot-r3v3-activation-20260830-v1`.

The authoritative numeric Bureau event id returned by that append is **A**. The marker itself has `event_id == A`; only births with `identity_first_event.event_id > A` are eligible, so the activation marker itself cannot consume a slot. No repository, PR or review mutation required to establish this activation revision may occur after A.

A may be written only when one pre-marker observation binds all of the following:

- this activation revision is merged on Vibe-Lab `main`;
- `experiments/active.v1.json` contains this experiment with `state: testing`, `primary_metric: binding_failure_count` and `source_ref` bound to this experiment's `results/decision.yml`;
- the manifest remains `status: testing` and `execution_status: designed`, and `results/decision.yml` remains `verdict: not_executed`;
- the R3 v3 predecessor still says `verdict: confirms`, `natural_cases_taken: 0`, `pilot_authorized: false`;
- fresh Bureau candidate projection reports `coverage_complete=true` and `projection_source=complete_event_scan`, together with projection size and the latest displayed pre-marker event;
- no already-observed event is reclassified as post-A;
- a **`slot_capture_contract`** has been frozen for one already-existing durable provider surface, with its exact surface identity and revision. The provider—not the controller—must durably own the complete per-slot state machine described below. If no existing surface satisfies that contract, A MUST NOT be written and the pilot remains `not_executed`.

If the marker append is ambiguous, no second marker is written until exact idempotency-key readback establishes whether the first append exists.

## 3. Required slot-freeze provider contract

The pre-A `slot_capture_contract` must prove all of these properties for one exact existing surface:

1. **Deterministic key:** the caller supplies one `slot_id`; all state for that slot is addressed only by that id.
2. **Provider-owned states:** exact readback returns exactly one of `absent`, `begun` or `terminal`, plus immutable provider receipts. The provider owns the only transitions `absent → begun → terminal`; state never moves backward and the terminal payload is immutable. The terminal payload contains exactly one admission state from §5, including fail-closed `indeterminate` when provider-owned session continuity is lost.
3. **Atomic begin:** `begin(slot_id, birth_binding)` is create-if-absent and durably records the canonical birth binding before returning success. Repeated or concurrent begin for the same id and same binding converges to the same begun session; a different binding is a hard conflict.
4. **Session continuity:** the provider owns the capture-session identity/liveness. Successful admission finalization can succeed only for the still-valid begun session. A replacement controller cannot impersonate or recreate that session after process/session loss. When provider-owned liveness proves that a begun session is irrecoverably lost, the provider must support one atomic fail-closed terminalization of that same slot to admission state `indeterminate`; this transition is derived only from provider-owned session state and requires no reconstructed C/S/B/E/T/Q.
5. **Provider timing:** begin establishes the authoritative handling start; terminalization establishes the authoritative finish and provider-computed elapsed seconds. Client clocks are not the metric authority.
6. **Atomic terminalization:** `finalize(slot_id, payload)` atomically stores the complete exact terminal payload once and transitions provider state to `terminal`. For a valid live session the payload is the controller-supplied admission result; for provider-proven lost-session recovery the provider itself supplies the fixed `indeterminate` failure payload. Same-id/same-payload replay converges; same-id/different-payload is a hard conflict and never overwrites evidence.
7. **Crash/restart durability:** `begun` and `terminal` survive controller/process restart, and a replacement can exact-read the complete state and terminal payload without reconstructing C/S/B/E/T/Q from later knowledge.
8. **Ambiguous transport readback:** after any unknown/ambiguous begin or finalize result, exact provider readback by `slot_id` is authoritative. While the state cannot be resolved, no mutation for that slot and no later ordinal is allowed.
9. **Immutable evidence identity:** provider receipts expose stable evidence identity, including a provider-generated lowercase SHA-256 digest for the durable begun/terminal state and exact readback reproduces that digest.
10. **No operational authority:** begin/read/finalize are experiment-evidence operations only. They create no Bureau candidate identity birth and grant no routing, queue, runtime, merge, deployment, policy or product authority.

This revision does not authorize building such a surface. It only permits A if a qualifying surface already exists and is proved against the exact contract before activation.

## 4. Fixed cohort and ordinal reconstruction

Before any post-A slot is handled, freeze exactly three negative eligibility sentinels: the last three fully provable canonical identity births with `identity_first_event.event_id < A`, ordered by numeric event id. They are eligibility checks only and never consume N.

`N = 3`. The cohort is the first three fully provable canonical `candidate_identity_birth` events with `identity_first_event.event_id > A`, ordered only by authoritative numeric event id.

Before handling ordinal `n`, the controller reconstructs the canonical births for ordinals `1..n` and reads provider state for every earlier `slot_id`. A later ordinal is never eligible while an earlier ordinal is `absent`, `begun`, unresolved, or otherwise nonterminal. An earlier `terminal` slot is never recomputed; its immutable admission state is authoritative. A supersession/later event of an already-existing canonical candidate identity is not a new birth and consumes no slot.

`slot_id` is SHA-256 over UTF-8 bytes of `experiment_id`, decimal A, decimal ordinal, canonical candidate id and decimal birth event id joined by the single byte `0x1f`, with no surrounding whitespace.

## 5. Slot outcomes and binding-failure metric

Each consumed ordinal has exactly one admission state:

- `frozen`: C/S/B/E/T/Q were bound before productive mutation; increment `0`.
- `not_applicable`: D0; increment `0`; non-informative and never replaced.
- `capture_missed_before_mutation`: productive mutation had already begun before the required binding; increment `1`; REJECT.
- `capture_not_frozen_in_time`: binding could not complete without delaying productive work; increment `1`; REJECT.
- `result_informed_binding_failure`: result/outcome knowledge existed before binding; increment `1`; REJECT.
- `indeterminate`: required admission or provider evidence could not be established reproducibly; increment `1`; REJECT.
- `rejected_interference`: the experiment influenced the fully proved birth; increment `1`; REJECT and zero accepted natural evidence.
- `rejected_ambiguous_causation`: independence from the experiment cannot be proved; increment `1`; REJECT and zero accepted natural evidence.

`binding_failure_count` is the sum of these fixed increments. No later slot can repair, replace or dilute an earlier failure.

## 6. One provider-owned capture transaction per slot

For the earliest eligible nonterminal ordinal:

1. Prove canonical birth identity and ordinal from the complete Bureau projection. If productive mutation or outcome knowledge already makes successful prospective capture impossible, that fact determines the appropriate failure payload below; the ordinal is still not skipped.
2. Call provider `begin(slot_id, birth_binding)` **before C/S/B/E/T/Q analysis**. Exact-readback-verify provider state `begun` and the canonical birth binding before continuing. Provider begin time starts the handling metric.
3. If provider state is already `begun` from a prior controller/session, provider-owned liveness decides the only two legal paths: the same still-valid session continues, or the provider atomically terminalizes that slot to `indeterminate`, increment `1`, with reason `capture_session_lost`. A replacement never reconstructs a successful capture for that begun session.
4. Under the same valid provider session, derive the terminal payload. A successful `frozen` payload contains only C/S/B/E/T/Q, slot/birth identity, outcome-distance classification, bounded primary-evidence references and authority findings. A `not_applicable` payload contains slot/birth identity, state `not_applicable`, `binding_failure_increment=0`, the prospective D0 classification, the inherited Phase-G naturalness/self-interference and independence findings, authority findings, and bounded primary-evidence references sufficient to reproduce both D0 and Phase-G PASS; it contains no fabricated C/S/B/E/T/Q binding. Failure states contain only the evidence needed to prove that state. No Full Outcome Case or mutable technical-truth copy is permitted.
5. For admission state `frozen`, call provider `finalize(slot_id, complete_terminal_payload)` **before productive mutation**. `not_applicable` is permitted only after the inherited Phase-G gate has reproducibly proved naturalness, no experiment interference, and unambiguous independence **and** the D0 classification is established prospectively before productive mutation and before outcome/result knowledge. `rejected_interference` or `rejected_ambiguous_causation` always takes precedence over D0 and immediately REJECTS. After Phase-G PASS plus D0 proof, finalize the `not_applicable` payload immediately and before productive mutation. If productive mutation or outcome/result knowledge arrives before those prerequisites are established, the slot cannot be `not_applicable` and must take the applicable failure state. For a failure state whose defining trigger is itself productive mutation or later outcome/result knowledge—especially `capture_missed_before_mutation` or `result_informed_binding_failure`—finalize that failure payload immediately after the triggering condition is authoritatively established; the pre-mutation deadline does not apply to recording the already-triggered failure. Other failure states finalize as soon as their defining evidence is complete. Provider terminalization time ends the handling metric. Exact readback must return `terminal`, the exact immutable payload, its provider digest and provider-computed elapsed seconds.
6. Any ambiguous begin/finalize result is handled only by exact provider readback. If provider readback proves `begun` and the original session is irrecoverably lost, invoke only the provider-owned lost-session terminalization above; exact readback must then return terminal `indeterminate`. If provider state cannot be resolved without delaying productive execution, stop all slot handling and REJECT on unresolved provider state. No client-side alternate intent, failure record, reserialization path, or second record id exists.
7. A provider hard conflict, illegal state transition, payload mismatch, or evidence-integrity mismatch is a material protocol violation and immediate REJECT.

For a slot whose provider state is `terminal` and whose admission state is `frozen` or `not_applicable`, continue only to the next fixed ordinal. For every other terminal state, stop immediately. No fourth case exists.

## 7. Timing rule

The cost metric is provider-owned elapsed capture time from durable successful `begin` to durable provider `terminal` for each consumed slot. It includes C/S/B/E/T/Q analysis and terminal payload construction. It excludes pre-slot Bureau birth discovery/proof and post-terminalization review. A begun slot that cannot reach a valid terminal state is a binding failure or unresolved-provider-state REJECT rather than a censored timing observation.

The observer must never delay, reprioritize, split, merge or reshape productive work to improve this metric. If capture cannot finish without delaying productive work, finalize `capture_not_frozen_in_time` if the same provider session remains valid; otherwise provider-owned lost-session terminalization yields `indeterminate` and REJECT.

## 8. Stop, review and mechanical S1 decision

The pilot stops after three consumed ordinals or immediately on any failure state/material protocol violation.

After termination, freeze the exact evidence revision. Independent exact-head review must verify: A and activation preconditions; the exact `slot_capture_contract`; first-three-birth ordering; negative sentinels; no replacement/backfill; provider state transitions and session continuity; capture-before-mutation; C/S/B/E/T/Q reproducibility; state-to-metric mapping; provider elapsed times; authority boundaries; and absence of any unreviewed operational integration.

PASS requires all of:

- exactly 3/3 fixed slots in canonical order;
- `binding_failure_count == 0`;
- zero material review disagreements;
- zero authority violations;
- zero replacement/backfill;
- all three provider states durably `terminal` with valid immutable evidence;
- median provider elapsed handling time <= 600 seconds;
- at least two definitive non-D0 slots.

REJECT occurs on any binding failure, provider/session/payload conflict, unresolved provider state, experiment interference, ambiguous causation, authority violation, replacement/backfill, noncanonical ordering or other preregistered material protocol violation.

INCONCLUSIVE is permitted only when all mechanics succeed with `binding_failure_count == 0`, all three provider states are validly terminal, but fewer than two slots are informative non-D0. No backfill is allowed; any successor requires a new prospective cohort.

## 9. Non-claims

This pilot tests admission feasibility only. It does not test Minimal versus Full, does not establish Outcome-Case efficacy, and authorizes no validator, Bureau field, Grabowski runtime integration, routing, queue, policy, deployment, automatic task creation, Chronik integration, Leitstand integration or product integration. A Decision-Impact pilot requires a separate post-PASS decision.
