---
title: "Chronik History Brief Effect — Natural-Case Admission Protocol"
status: active
canonicality: operative
created: "2026-08-09"
updated: "2026-08-11"
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

This protocol makes the registered comparison prospectively admission-capable before agent planning. It is a manually invoked, one-case-at-a-time evidence writer; condition assignment itself follows the frozen registration contract. It does not discover tasks, select work, mutate a queue, call Grabowski or Chronik, start an agent, create a Chronik cohort, route a case or authorize runtime behavior.

The experiment registration was prospectively revised on 2026-08-11 before the first admitted case. Its `assignment` block freezes `stratified_permuted_blocks.v1`, the exact three comparison strata, a seed digest, two-case blocks, per-stratum create-only sequencing and a maximum arm-count difference of one in a partial block. The admission writer now computes the registered arm under the same exclusive cohort lock; callers no longer choose control versus treatment. This establishes bounded deterministic balance only, not randomization or causal identification.

## Required request

Start from `tests/fixtures/natural_case_admission/valid-control-request.json` and replace every fixture value with the real case metadata and immutable evidence references. The request freezes:

- a natural, in-scope case attestation;
- `planning_started=false`, `execution_started=false`, `outcome_known=false` and `prior_observation=false`;
- case-open and eligibility-receipt times after registration and before admission;
- task class, risk band, repository-familiarity band and comparison key;
- target repository, component, operation and live-preflight contract;
- repository revision, operator, model/tool version, task-difficulty band and prior-Chronik-event band;
- `assignment.mode=registered_automatic`; the registered writer seals the resulting condition and assignment evidence;
- `triggered_by` provenance.

Then run, before planning:

```bash
python3 tools/vibe-cli/admit_natural_case.py \
  --registration experiments/2026-07-13_chronik-history-brief-effect/registration.v2.json \
  --request /path/to/bounded-admission-request.json
```

The request does not contain a condition. The writer derives either `live_preflight_only` or `live_preflight_plus_history` from the frozen registration and creates `artifacts/admissions/<case-id>/admission.json` with create-only publication, file and directory sync, a private process lock and read-only file mode.

## Refusal and idempotency

The writer fails closed before publication when the case predates registration, admission occurs at or after expiry, planning or execution has started, the outcome is known, the case was already observed, timestamps are out of order, the condition is unregistered, paths or symlinks are unsafe, or evidence identity is already bound to another case.

An identical retry returns the original admission without rewriting bytes or timestamps. The same case ID with changed metadata, condition, evidence or registration digest is an immutable conflict. A different case ID cannot reuse eligibility or assignment evidence. These checks prevent tool-level backfill and rewrite; independent review must still verify that the upstream receipts are truthful.

## Independent review handoff

Each record prepares, but does not perform, the later review. It binds a condition-independent `blinded_case_id`, the registered measurement digest, allowed evidence-source names, independent-observation requirement, both three-case minima and the unchanged review timestamp.

Before scoring, give the reviewer the blinded case ID plus immutable execution, GitHub/CI, diff-bound review and outcome evidence. Do not give the assignment-bearing admission record or the Chronik/no-Chronik label. Seal all five registered binary score components and effort first; reveal the condition only for registration-bound observation capture. Distinct reviewer and decision-maker references remain mandatory in `capture_effect_observation.py`. If blindness or independence cannot be supported, preserve that failure rather than manufacturing a score.

## Prospective assignment and observation binding

The 2026-08-11 registration revision is active only for admissions carrying its new registration digest. The writer assigns each new case under the create-only cohort lock and validates all earlier automatic records in the same stratum before allocating the next sequence index. Any gap, seed drift, registration mismatch or derived-arm mismatch fails closed. Git history preserves the prior registration; no old admission may be rewritten or reinterpreted.

Later scoring must consume the exact `artifacts/admissions/<case-id>/admission.json`. `capture_effect_observation.py` requires that admission for this assigned experiment and verifies the registration digest, condition, comparison key and blinded case identifier before writing an observation. The stored observation includes the case id, admission id and file digest. The evaluator independently re-resolves that immutable admission file and rechecks its digest, registration, blinded identifier, condition and comparison key before computing an effect. Scoring remains independently blinded; admission assignment is not disclosed until the score is sealed. None of these contracts may choose Bureau work, alter a queue, select a production route or trigger runtime behavior.
