---
title: "Model-Lab Replication-Series — Results"
status: designed
canonicality: operative
---

# Model-Lab Replication-Series — Results

## Status

Skeleton only. The AP-4 Model-Lab replication-series structure exists with one
**activated** baseline run (`run-001-rest-api-spec-first-baseline`) carrying
opt-in Model-Lab control metadata (`model_lab_control: true`) and a challenge
reference to `rest-api-v1`.

## What this establishes

- AP-1 (`validate_model_lab_control`) now has a real activated `run_meta.json`
  metadata surface to check.
- AP-2 (`validate_challenge_versions`) now has a real activated `decision.yml` to
  check against the `rest-api-v1` challenge version.

## What this does NOT establish

- No model-quality or comparative verdict ("Model X is better" is **not** claimed).
- No outcome upgrade, no adoption, no promotion, no staleness reactivation.
- The execution verdict is `not_executed`; nothing was actually run.

## Next step (later, out of scope here)

Execute a real baseline run for `rest-api-v1`, then add a second run with a
different condition, model, or tool to enable a first genuine comparison.
