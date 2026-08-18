---
title: "Outcome-Bound S1-R1 — Pre-activation rejection"
status: rejected
canonicality: operative
created: "2026-08-18"
updated: "2026-08-18"
triggered_by: "conversation:user-request-2026-08-18-continue-outcome-bound"
---

# Pre-activation rejection

## Binding

Frozen author revision: `9e3033adb2a394fd871e0a1a30f9709afdc35321` on PR #348.

The author revision was locally fully validated and all hosted PR checks were green. Those technical results do not override the semantic pre-activation gate.

Two independent read-only Opus reviews were bound to the exact author revision:

- reviewer A job `grabowski-job-0bad1b9c2b3e`, finalization receipt `81384fd850473fec0f43c260964e35e180da448e3b81c8ee4d99179f2af7db2c`, payload `cc8b3ee50b459870ea2f4fdd4520ad876ae93b29ed81c69366100d0c2827cba9`, verdict `REJECT_THIS_REVISION` with one material finding;
- reviewer B job `grabowski-job-110713c2f555`, finalization receipt `a8aa6c7a6d12dd3f9bc507a80c001bd878e369d426211b01f00ec10da06a1385`, payload `1d25524ede54e3fa568f6fc72cc353414c5cdbb5f49c17196941ec2622627b3d`, verdict `PASS_THIS_REVISION`, while explicitly noting naturalness as an unfenced assumption.

The disagreement is itself not resolved by majority. Reviewer A identified a valid protocol escape, and a separate controller readback found an additional concrete canonical-identity escape. Either one is sufficient for the frozen zero-material-finding gate to fail.

## Merge-gate incident

Both exact-head reviews were already terminal before PR #348 was merged:

- reviewer A terminal receipt timestamp: `2026-08-18T11:18:27Z`;
- reviewer B terminal receipt timestamp: `2026-08-18T11:19:14Z`;
- PR #348 merged at: `2026-08-18T11:20:40Z`;
- PR #348 merge commit: `e142b1d11614abb4f307b6654940b60afb0b2dc3`.

The controller merged after reading reviewer B but before reconciling reviewer A. That violated the preregistered zero-material-finding merge gate. The merge is therefore negative process evidence, not activation authority. The failed semantic gate existed before merge, so the later nominal `merged_at + 300 s` timestamp cannot create a valid treatment window. No S1-R1 natural candidate was selected or consumed before or after that timestamp.

The corrective closeout does not rewrite or revert the frozen author revision. It marks that exact revision rejected and removes S1-R1 from the active experiment projection.

## Material finding M1 — natural-source independence is not frozen

Reviewer A found that S1-R1 defines which candidate identities count but does not preserve S1's earlier requirement that treatment arrivals be independently created outside the experiment and not manufactured, timed, delayed, selected, reprioritized or reshaped for S1.

A protocol-conforming controller could therefore merge the experiment, wait through the fixed 300-second cooling interval, deliberately create three easy-to-bind Operator-Intake candidates, then obtain a formal PASS that says nothing about natural-case feasibility.

This is a sampling-validity failure, not a productivity trade-off. It requires no new validator or production field to fix; a successor must freeze source independence before activation.

## Material finding M2 — canonical legacy identity is not normalized

A read-only query of the authoritative Bureau StateStore found 3,450 `candidate_task` live-register events at the recorded closeout snapshot, including **34 legacy events without a stored `candidate_id`**. A later read-only recheck observed 3,451 candidate-task events while the legacy counts remained unchanged: 34 no-ID roots, 14 with direct identity-bearing successors.

The deployed immutable Bureau runtime is source commit `fe41fe6e12569eb433542c47b8f2bdd84902789a`, StateStore schema version 5, integrity `ok`. Its canonical identity contract is:

```text
legacy event without candidate_id -> candidate-event-<event_id>
otherwise                         -> stored candidate_id
```

The deployed `live_register.py` implements `_candidate_identity(item)` by returning the stored `candidate_id` when present and otherwise `_legacy_candidate_id(event_id)`.

The StateStore already contains concrete legacy-successor examples, such as event 25 later represented by candidate identity `candidate-event-25`. Fourteen of the 34 no-id legacy roots have direct identity-bearing successors in the observed journal.

The frozen S1-R1 method instead computes the first event by scanning events that *contain the exact candidate_id*. That omits a legacy root whose canonical identity is implicit rather than stored. If a future successor of such an old identity first acquires `operator_intake` after activation, S1-R1 could incorrectly treat that old identity as newly born.

This is a real contract mismatch between S1-R1 and Bureau's canonical identity function. A successor must normalize every candidate event through the existing Bureau identity rule before grouping or ordering it.

## Gate result

**REJECT_THIS_REVISION.**

The author revision failed the pre-activation requirement of zero material sampling-contract findings. Therefore:

- no natural S1-R1 treatment window is valid;
- no candidate identity is consumed by S1-R1;
- no natural binding metric is computed;
- no P2/P3 or Minimal-versus-Full work is authorized;
- no Bureau, Grabowski runtime/routing, Chronik, Leitstand, queue, policy, merge-policy or deployment authority changes.

The frozen method, registration and paper cases remain negative evidence. They are not repaired in place. Any next attempt must be a separately identified successor revision.

## Nonclaims

This rejection does not reject S0-R3 paper semantics, does not establish that Outcome Cases are ineffective, and does not establish that a corrected natural identity sampler will pass. It establishes only that S1-R1 cannot validly activate as written.
