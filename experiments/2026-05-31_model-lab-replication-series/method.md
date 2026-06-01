---
title: "Model-Lab Replication-Series — Method"
status: designed
triggered_by: "user-request-2026-06-01-execute-real-model-lab-baseline-run"
canonicality: operative
---

# Model-Lab Replication-Series — Method

## Shape of the series

A small, controlled series that grows one run at a time. The first run is now
an executed baseline anchor only; no comparative or model-quality evaluation is
performed from this single run.

## Run-001 (executed baseline)

- **Challenge:** `rest-api` at `challenge_version: rest-api-v1`.
- **Condition:** `spec_first_baseline`.
- **Control condition:** `future_control_pending` (no control run exists yet;
  the executed baseline still stands alone).
- **Execution:** executed repo-locally via
  `python3 experiments/2026-05-31_model-lab-replication-series/artifacts/run-001-rest-api-spec-first-baseline/execute-baseline.py`;
  the command wrote `baseline-output.md`, an `implementation/` bundle with
  TypeScript/Fastify source plus Vitest verification specification, and archived
  `execution.txt`, `changed-files.txt`, and `timing.txt`.
- **Activation:** `run_meta.json` sets `model_lab_control: true` (AP-1) and
  `results/decision.yml` opts in as a Model-Lab / comparative decision against
  `rest-api-v1` (AP-2).

## What is measured now

`measurement.yml` records `measurement_status: executed_baseline_only`. It
tracks only repo-local observations that are directly evidenced by the run
artifacts: baseline execution presence, locator completeness, conservative
validation gaps, scope drift, and weak wall-clock timing. No model comparison is
performed.

## Later extension (out of scope for this baseline run)

- Add a second run with a different condition, model, or tool, so that a first
  genuine comparison becomes possible.
- Only then consider any comparative assessment — never inside this single-run
  baseline.
