---
title: "Chronik History Brief Effect — Natural-Case Admission Protocol"
status: active
canonicality: operative
created: "2026-08-09"
updated: "2026-08-09"
triggered_by: "user-request-chronik-natural-case-admission-2026-08-09"
relations:
  - type: references
    target: registration.v2.json
  - type: references
    target: ../../schemas/natural-case-admission.v1.schema.json
  - type: references
    target: ../../tools/vibe-cli/admit_natural_case.py
  - type: validated_by
    target: ../../tools/vibe-cli/test_admit_natural_case.py
  - type: references
    target: ../../tests/fixtures/natural_case_admission/valid-control-request.json
  - type: references
    target: ../../tools/vibe-cli/capture_effect_observation.py
---

# Natural-case admission protocol

## Purpose and authority boundary

This protocol makes the registered comparison prospectively admission-capable before agent planning. It is a manual, one-case-at-a-time evidence writer. It does not discover tasks, select work, mutate a queue, call Grabowski or Chronik, start an agent, create a Chronik cohort, route a case or authorize runtime behavior.

The frozen `registration.v2.json` is unchanged. It defines the two conditions and comparison requirements but contains no assignment algorithm, seed, stratum order or tie-break rule. Therefore the current writer accepts only a caller-supplied condition that was recorded before planning. It refuses to compute an arm and records that assignment fairness is not established.

## Required request

Start from `tests/fixtures/natural_case_admission/valid-control-request.json` and replace every fixture value with the real case metadata and immutable evidence references. The request freezes:

- a natural, in-scope case attestation;
- `planning_started=false`, `execution_started=false`, `outcome_known=false` and `prior_observation=false`;
- case-open and eligibility-receipt times after registration and before admission;
- task class, risk band, repository-familiarity band and comparison key;
- target repository, component, operation and live-preflight contract;
- repository revision, operator, model/tool version, task-difficulty band and prior-Chronik-event band;
- one explicit registered condition plus its assignment receipt and digest;
- `triggered_by` provenance.

Then run, before planning:

```bash
python3 tools/vibe-cli/admit_natural_case.py \
  --registration experiments/2026-07-13_chronik-history-brief-effect/registration.v2.json \
  --request /path/to/bounded-admission-request.json
```

The only valid condition values are `live_preflight_only` and `live_preflight_plus_history`. The command creates `artifacts/admissions/<case-id>/admission.json` with create-only publication, file and directory sync, a private process lock and read-only file mode.

## Refusal and idempotency

The writer fails closed before publication when the case predates registration, admission occurs at or after expiry, planning or execution has started, the outcome is known, the case was already observed, timestamps are out of order, the condition is unregistered, paths or symlinks are unsafe, or evidence identity is already bound to another case.

An identical retry returns the original admission without rewriting bytes or timestamps. The same case ID with changed metadata, condition, evidence or registration digest is an immutable conflict. A different case ID cannot reuse eligibility or assignment evidence. These checks prevent tool-level backfill and rewrite; independent review must still verify that the upstream receipts are truthful.

## Independent review handoff

Each record prepares, but does not perform, the later review. It binds a condition-independent `blinded_case_id`, the registered measurement digest, allowed evidence-source names, independent-observation requirement, both three-case minima and the unchanged review timestamp.

Before scoring, give the reviewer the blinded case ID plus immutable execution, GitHub/CI, diff-bound review and outcome evidence. Do not give the assignment-bearing admission record or the Chronik/no-Chronik label. Seal all five registered binary score components and effort first; reveal the condition only for registration-bound observation capture. Distinct reviewer and decision-maker references remain mandatory in `capture_effect_observation.py`. If blindness or independence cannot be supported, preserve that failure rather than manufacturing a score.

## Registration revision required for automatic assignment

Automatic fair/deterministic assignment is not permitted under the current registration. A new prospective registration revision must be reviewed and frozen before its first case. At minimum it must add:

1. an assignment contract and version, for example `stratified_permuted_blocks.v1`;
2. the exact strata and canonicalization rules, limited to the already registered task class, risk band and repository-familiarity band;
3. a precommitted seed or seed digest, block size, arm order derivation and tie-break behavior;
4. a create-only sequence index allocated under one cohort lock so concurrent arrivals have one deterministic order;
5. a balance invariant, such as an arm-count difference of at most one within every completed or partial two-case block;
6. idempotency, duplicate-evidence and immutable-conflict rules;
7. an activation timestamp and a new registration digest; earlier admissions remain bound to v2 and are never reassigned or backfilled;
8. the same no-policy, no-routing, no-queue and no-runtime boundary.

The revision must retain at least three natural cases per arm and the existing 2026-08-15 review and 2026-09-01 expiry unless a separately approved prospective experiment replaces this one. Merely implementing the algorithm is not registration; no automatic-assignment code is active in this change.
