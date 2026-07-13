---
title: "Effect Observation Capture"
status: active
canonicality: operative
relations:
  - type: references
    target: ../../tools/vibe-cli/capture_effect_observation.py
  - type: validated_by
    target: ../../tools/vibe-cli/test_capture_effect_observation.py
  - type: references
    target: ../../schemas/effect-evaluation.observations.v2.schema.json
  - type: informs
    target: ../../experiments/_archive/2026-07-12_operator-intervention-effect-evaluator/registration.v2.json
---

# Effect Observation Capture

## Purpose

`capture_effect_observation.py` is the only supported writer for real effect-evaluation observations. The archived operator-intervention registration remains historical design evidence only and must not receive new observations. It prepares evidence for review. For a registered scorecard it computes only the frozen weighted sum; it does not judge the criteria, change routing, mutate Bureau, or claim that the evaluator is useful.

## Preconditions

- The experiment has a valid and frozen `registration.v2.json`.
- The output is inside that experiment's `results/` directory.
- The observation belongs to the registered control or treatment condition.
- The primary evidence has an immutable SHA-256 digest.
- The decision maker and independent scorer are named separately.
- Total handling effort is measured in seconds, including condition preparation, evaluator generation when applicable, decision and scoring.
- The scorer receives randomized decisions without condition labels; any failure is recorded explicitly.
- Independence is stated explicitly and remains subject to later review.
- A registered scorecard is completed component by component; a free numeric value is then forbidden.
- The capture timestamp is not later than the registered expiry.

## Capture

```bash
python3 tools/vibe-cli/capture_effect_observation.py \
  --registration /path/to/active-experiment/registration.v2.json \
  --observations /path/to/active-experiment/results/observations.v2.json \
  --observation-id pilot-01-manual \
  --condition manual_review \
  --score-component decision_aligned=1 \
  --score-component uncertainty_preserved=1 \
  --score-component non_obvious_value=0 \
  --score-component overclaim_free=1 \
  --effort-seconds 180 \
  --scoring-blinded \
  --comparison-key pilot-01 \
  --pair-id pilot-01 \
  --evidence-ref receipt:pilot-01-manual \
  --evidence-file /path/to/frozen-scorecard-and-review-receipt.json \
  --decision-maker-ref receipt:manual-decider-01 \
  --observer-ref receipt:independent-scorer-01 \
  --independent
```

For remote evidence, `--evidence-sha256` may replace `--evidence-file`. That digest remains caller-supplied and must be checked during review.

## Guarantees

The writer:

- binds the observation aggregate to the canonical JSON digest of the registration;
- binds every evidence item to SHA-256;
- rejects duplicate observation IDs, evidence references and evidence digests;
- serializes concurrent writers with a private per-user runtime advisory lock;
- publishes through same-directory temporary file, file `fsync`, atomic replace and directory `fsync`;
- rejects symlink targets and output paths outside the experiment `results/` directory;
- requires distinct decision makers for both sides of a completed pair and prevents self-scoring;
- derives registered score values from the complete frozen component set;
- records measured effort and condition-label blinding for the later cost and comparability review;
- sorts observations by ID so repeated capture order does not affect the stored document.

## Non-claims

A successful capture does not establish evidence truth, observer independence, successful blinding, causal effect, cost-effectiveness, experiment usefulness, promotion readiness or any automatic action.
