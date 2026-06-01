---
title: "Model-Lab Replication-Series — Results"
status: testing
triggered_by: "user-request-2026-06-01-execute-real-model-lab-baseline-run"
canonicality: operative
---

# Model-Lab Replication-Series — Results

## Status

Run-001 is now an executed baseline for `rest-api-v1`. The run
`run-001-rest-api-spec-first-baseline` contains repo-local execution evidence,
keeps opt-in Model-Lab control metadata (`model_lab_control: true`), and remains
bound to `challenge_version: rest-api-v1`.

## What this establishes

- A real baseline execution artifact exists for Run-001.
- AP-1 (`validate_model_lab_control`) Model-Lab metadata is exercised on a real
  run metadata file.
- AP-2 (`validate_challenge_versions`) challenge-version metadata remains bound
  to `rest-api-v1` through the activated decision path.
- The run-local baseline output records a spec-first response artifact for the
  REST API task, including TypeScript/Fastify implementation shape and executable
  verification specification files under `implementation/`.

## What this does NOT establish

- No model-quality verdict.
- No comparative verdict.
- No outcome upgrade.
- No adoption.
- No promotion.
- No staleness reactivation.

## Interpretation limit

This establishes the first executed baseline artifact. Comparability remains
blocked until a second executed run exists. No model-quality, outcome, adoption,
or promotion claim is derived.

## Next step

Add `run-002` with a different condition, model, or tool under the same
`rest-api-v1` challenge version to enable the first genuine comparison.
