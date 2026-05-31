---
title: "Model-Lab Replication-Series — Method"
status: designed
canonicality: operative
---

# Model-Lab Replication-Series — Method

## Shape of the series

A small, controlled series that grows one run at a time. The first run is a
baseline anchor only; no quantitative evaluation is performed in this skeleton.

## Run-001 (this skeleton)

- **Challenge:** `rest-api` at `challenge_version: rest-api-v1`.
- **Condition:** `spec_first_baseline`.
- **Control condition:** `future_control_pending` (no control run exists yet;
  the baseline stands alone in this skeleton).
- **Execution:** not executed. `run_meta.command` is `not executed; skeleton only`
  and `exit_code` is recorded as `0` for the skeleton placeholder.
- **Activation:** `run_meta.json` sets `model_lab_control: true` (AP-1) and
  `results/decision.yml` opts in as a Model-Lab / comparative decision against
  `rest-api-v1` (AP-2).

## What is measured now

Nothing quantitative. `measurement.yml` records `measurement_status: skeleton_only`,
every observed metric is either `missing_evidence` or a structural `0`, and no
timing is treated as hard evidence. No model comparison is performed.

## Later extension (out of scope for this skeleton)

- Execute a real baseline run for `rest-api-v1`.
- Add a second run with a different condition, model, or tool, so that a first
  genuine comparison becomes possible.
- Only then consider any comparative assessment — never inside this skeleton.
