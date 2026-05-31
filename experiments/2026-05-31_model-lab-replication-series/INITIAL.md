---
title: "Model-Lab Replication-Series — Initial State"
status: designed
canonicality: operative
---

# Model-Lab Replication-Series — Initial State

## Starting point

- **AP-1 present:** the Lab-Control-Minimum validator
  (`scripts/docmeta/validate_model_lab_control.py`) and its tests are merged and
  wired into `make validate`.
- **AP-2 present:** the challenge-version validator
  (`scripts/docmeta/validate_challenge_versions.py`) and its tests are merged and
  wired into `make validate`; `benchmarks/challenges/rest-api-v1.md` is a known
  challenge version.
- **No activated Model-Lab run yet:** before this skeleton, no experiment set
  `model_lab_control: true` on a `run_meta.json`, so the AP-1 validator had
  nothing to enforce; no comparative `decision.yml` referenced a
  `challenge_version`, so the AP-2 decision path was never exercised on a real
  experiment.

## Goal of this skeleton

Provide the first **minimal, activated** baseline run as a structural anchor:

- one run (`run-001-rest-api-spec-first-baseline`) with opt-in Model-Lab control
  metadata so AP-1 engages;
- one activated `decision.yml` against `rest-api-v1` so AP-2 engages;
- no executed comparison and no comparative verdict.

The execution status is `prepared` and the execution verdict is `not_executed`:
the structure exists, but nothing was actually run.
