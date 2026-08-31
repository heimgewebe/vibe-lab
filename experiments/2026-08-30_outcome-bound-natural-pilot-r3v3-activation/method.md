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
- no already-observed event is reclassified as post-A;
- a `terminal_journal_contract` has been frozen for one **already existing** durable controller evidence journal. The frozen contract names the exact append/read surface and revision and proves, before A, all of: create-if-absent writes keyed by caller-supplied record id; repeated or concurrent append of the same record id with byte-identical caller payload converges to exactly one immutable record or returns that exact existing record; the same record id with a different payload is a detectable conflict and is never overwritten; exact readback by record id including the original caller payload bytes or an exact byte-equivalent representation; authoritative presence/absence classification; process-restart durability; and an immutable provider-returned lowercase SHA-256 `record_sha256` that exact readback reproduces. The journal operation must not create a Bureau candidate identity birth and must grant no routing, queue, runtime, policy or product authority. If no existing surface satisfies this contract, A MUST NOT be written and the pilot remains not executed.

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

1. `handling_started_at_monotonic_ns` is sampled immediately **before** issuing the first authoritative candidate-task read in the scan that discovers the candidate or begins the proof that it is the next eligible canonical identity birth. Candidate detection, complete-projection checks, identity/birth proof and Phase-S ordering therefore begin inside the clock.
2. Once the canonical birth and ordinal are proved, the slot receives deterministic identity `slot_id = sha256(experiment_id || A || ordinal || canonical_candidate_id || birth_event_id)`. This identity digest is SHA-256 over UTF-8 bytes of the five textual fields joined by the single byte `0x1f`, with decimal base-10 representations for A, ordinal and birth event id and no surrounding whitespace.
3. **Before any C/S/B/E/T/Q analysis**, append and exact-readback-verify one immutable `slot_claim` with deterministic `claim_id = "slot-claim:" + slot_id`. Its payload is derived only from authoritative birth evidence and contains `slot_id`, A, ordinal, canonical candidate id, birth event id, birth-proof evidence refs, `handling_started_at_monotonic_ns`, a UTC start timestamp and a `monotonic_clock_domain` identifying the host/boot domain in which that monotonic value is valid. The claim append follows the same same-id/same-payload read-before-retry rule as all other journal records. A controller that crashes before a claim is verified is, by contract, forbidden to have started C/S/B/E/T/Q analysis; a replacement re-runs Phase S for the same earliest birth and cannot skip it.
4. After a verified claim exists, the observer constructs a complete **provisional terminal payload** containing the proposed admission state, fixed `binding_failure_increment`, required primary-evidence references, C/S/B/E/T/Q when applicable, outcome-distance classification, authority findings and UTC provenance timestamps. Failed-capture classification is inside this payload and therefore inside the clock.
5. `handling_finished_at_monotonic_ns` is sampled immediately after that provisional terminal payload is fully determined in memory and **before** journal persistence. `handling_seconds = (handling_finished_at_monotonic_ns - handling_started_at_monotonic_ns) / 1_000_000_000`. No candidate detection, completeness scan, identity/birth proof, evidence read or analysis interval before this boundary may be subtracted. If the current process cannot prove continuity with the claim's `monotonic_clock_domain`, the provisional admission state is `indeterminate` with increment one.
6. Before attempting the terminal record, construct the **complete exact terminal record bytes once**. The record has deterministic `terminal_id = "slot-terminal:" + slot_id`; it binds `claim_id`, `intent_id`, the admission state and all frozen payload/timing fields. Freeze these exact bytes as `terminal_record_bytes_b64` plus `terminal_record_bytes_sha256 = sha256(exact_terminal_record_bytes)`. No later controller is permitted to reserialize logical fields to recreate the terminal payload.
7. Append one immutable write-ahead `slot_terminal_intent` with deterministic `intent_id = "slot-terminal-intent:" + slot_id`. The intent contains `claim_id`, `slot_id`, `terminal_id`, `terminal_record_bytes_b64`, `terminal_record_bytes_sha256`, the logical provisional payload for human review, start, finish and `handling_seconds`. The append receipt's immutable provider-generated `record_sha256` becomes `intent_record_sha256`. Exact-read the same `intent_id` and require the journal to reproduce both its record digest and the frozen terminal byte blob/hash. If the intent append is ambiguous, only exact readback by `intent_id` is permitted before any retry. Authoritative absence permits only a byte-identical idempotent retry of the same intent; an existing same-id record with different content is a material protocol violation and immediate REJECT.
8. After a verified intent exists, every terminal append or retry uses **only** the exact bytes decoded from the intent's `terminal_record_bytes_b64`, under the same deterministic `terminal_id`. The controller verifies the bytes against `terminal_record_bytes_sha256` before append and never serializes a new terminal object. Persistence/readback latency is explicitly excluded from `handling_seconds`; it is a separate hard validity gate.
9. After **every** terminal-append outcome—success, definite error or ambiguous/unknown result—the controller performs exact readback by `terminal_id` before another terminal append. Reconciliation has exactly three states:
   - a matching terminal record exists and its caller payload bytes/hash equal the intent-frozen terminal bytes/hash: terminalize the slot;
   - the journal authoritatively reports `terminal_id` absent: retry the same byte-identical terminal bytes under the same deterministic id. A definite write error and an ambiguous write followed by authoritative absence use this identical recovery path. Because the frozen journal contract makes same-id/same-payload appends converge, a delayed original append and a retry cannot create contradictory records;
   - presence versus absence cannot be established: derive `persistence_outcome_unknown`, perform no terminal mutation, handle no later ordinal and permit neither PASS nor INCONCLUSIVE until exact readback becomes possible.
10. If exact readback finds `terminal_id` with bytes, digest or intent binding different from the verified intent, or the journal reports a same-id/different-payload conflict, the controller MUST NOT overwrite or reinterpret it. This is `terminal_identity_conflict`, a preregistered material protocol violation and immediate REJECT.
11. Before handling ordinal `n+1`, every controller—including a replacement after crash/restart—must reconstruct the first `n` canonical post-A births and verify for each earlier ordinal the deterministic `claim_id`, `intent_id` and `terminal_id`. An earlier birth may never be skipped because one of those records is absent. If an earlier claim exists but its intent does not, that ordinal remains the only admissible work item: the replacement may continue the capture only when it can prove the same monotonic clock domain and that productive mutation/result knowledge have not invalidated prospectivity; otherwise it must freeze the applicable failure state, never reconstruct a successful C/S/B/E/T/Q binding from later knowledge, then persist its intent/terminal through the same path. If an earlier deterministic birth has no verified claim, the controller must process that birth first; because analysis before claim is forbidden, it re-runs Phase S for that same birth and then either claims it prospectively or records the applicable failure state if productive work has already advanced. No later ordinal is eligible while an earlier claim, intent or terminal remains unresolved.
12. Terminal-journal transport does **not** retroactively change the slot's admission state or `binding_failure_count`. A verified eventual terminal record preserves the state already frozen in the intent. Persistence is a separate protocol-validity gate: any `terminal_identity_conflict` rejects immediately, and any earlier slot still lacking a verified claim/intent/terminal at registered review/closeout is a material protocol violation and REJECT.
13. A separate `persistence_verified_at_monotonic_ns` may be sampled after successful terminal readback for audit provenance only and is never part of the cost metric.
14. If productive mutation begins before a successful C/S/B/E/T/Q freeze, the state cannot be `frozen`; it must take the applicable failure state. The observer never delays productive execution merely to improve the measured duration.

For a scan that finds no new eligible identity birth, no slot is consumed and no handling duration is recorded. Once a scan proves a birth and its claim is verified, that fixed ordinal cannot be abandoned, replaced or backfilled.

## 7. Three-slot stop and review

The pilot stops when three ordinals have been consumed or immediately when a failure state or inherited R3 v3 rule requires fail-closed termination. No fourth case can replace an uninformative or failed slot.

After termination, freeze the exact evidence revision. An independent exact-head reviewer must verify: activation-marker identity and A; first-three-birth ordering; no replacement/backfill; complete birth proof; claim-before-analysis; capture-before-mutation; C/S/B/E/T/Q reproducibility; exhaustive state-to-metric mapping; classifications; baseline stability; target-effect versus qualifier separation; authority boundaries; measured handling time and monotonic-clock domain; frozen terminal-journal contract; deterministic claim/intent/terminal identities; exact terminal bytes frozen inside the intent; provider-returned intent record digest; same-id/same-payload retry convergence; absence of terminal-identity conflicts; restart reconstruction without skipping earlier ordinals; and the single-terminal-record reconciliation path.

## 8. Mechanical S1 decision

PASS requires all of:

- exactly 3/3 slots in canonical order;
- `binding_failure_count == 0` under the fixed state mapping;
- zero material review disagreements;
- zero authority violations;
- zero replacement/backfill;
- zero terminal-identity conflicts;
- median `handling_seconds` across the three consumed slots <= 600 seconds;
- at least two definitive non-D0 slots;
- no earlier slot with unresolved claim, intent or terminal evidence.

REJECT occurs immediately on any slot with `binding_failure_increment=1`, experiment interference, ambiguous causation, authority violation, replacement/backfill, noncanonical ordering, terminal-identity conflict or other preregistered material protocol violation. An earlier slot with unresolved claim/intent/terminal evidence can never be treated as PASS or INCONCLUSIVE and, if still unresolved at registered review/closeout, is itself a material protocol violation.

INCONCLUSIVE is permitted only when the mechanics succeed, `binding_failure_count == 0`, all three fixed slots are consumed, no terminal-identity conflict or unresolved earlier slot evidence remains, and fewer than two are informative non-D0 cases. No backfill is allowed; any successor is a new prospective cohort.

## 9. Non-claims

This pilot tests admission feasibility only. It does not test Minimal versus Full, does not establish Outcome-Case efficacy, and authorizes no validator, Bureau field, Grabowski runtime integration, routing, queue, policy, deployment, automatic task creation, Chronik integration, Leitstand integration or product integration. A Decision-Impact pilot requires a separate post-PASS decision.
