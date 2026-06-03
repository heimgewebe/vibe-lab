---
title: "Model-Lab Replication-Series — Method"
status: designed
triggered_by: "user-request-2026-06-01-execute-real-model-lab-baseline-run"
canonicality: operative
---

# Model-Lab Replication-Series — Method

## Shape of the series

A small, controlled series that grows one run at a time. Two runs are now
executed under `rest-api-v1`: a baseline anchor (spec-first) and a control
run (code-first). They form a first-order comparability structure. No comparative
or model-quality evaluation is performed inside this bundle; comparison remains
deferred to later assessment artifacts.

## Run-001 (executed baseline)

- **Challenge:** `rest-api` at `challenge_version: rest-api-v1`.
- **Condition:** `spec_first_baseline`.
- **Execution:** executed repo-locally via
  `python3 experiments/2026-05-31_model-lab-replication-series/artifacts/run-001-rest-api-spec-first-baseline/execute-baseline.py`;
  the command wrote `baseline-output.md`, an `implementation/` bundle with
  TypeScript/Fastify source plus Vitest verification specification, and archived
  `execution.txt`, `changed-files.txt`, and `timing.txt`.
- **Activation:** `run_meta.json` sets `model_lab_control: true` (AP-1) and
  `results/decision.yml` opts in as a Model-Lab / comparative decision against
  `rest-api-v1` (AP-2).

## Run-002 (executed control)

- **Challenge:** `rest-api` at `challenge_version: rest-api-v1` (same as Run-001).
- **Condition:** `code_first_control` (different from Run-001).
- **Execution:** executed repo-locally via
  `python3 experiments/2026-05-31_model-lab-replication-series/artifacts/run-002-rest-api-code-first-control/execute-control.py`;
  the command wrote `control-output.md`, an `implementation/` bundle with
  TypeScript/Fastify source plus Vitest verification specification, and archived
  `execution.txt`, `changed-files.txt`, and `timing.txt`.
- **Activation:** `run_meta.json` sets `model_lab_control: true` (AP-1),
  `compared_against: run-001`, and the control run links to the same `rest-api-v1`
  challenge version, enabling first-order comparability structure.
- **Comparability:** `comparability.yml` in Run-002 records
  `verdict: comparable_surface_available`, but comparison remains deferred.

## What is measured now

Two executed run surfaces exist under the same challenge version. The series
tracks repo-local observations:

- Run-001 and Run-002 both execute deterministically.
- Both target `rest-api-v1` with identical API surface requirements.
- Both produce implementation and verification artifacts.
- Neither makes model-quality, comparative, outcome, adoption, or promotion claims.

**Measurement status:** `executed_two_run_surface`.

`measurement.yml` in each run records execution completeness, locator presence,
verification evidence, and comparability structure availability. No model comparison
is performed inside the runs. Actual comparison (assessment, verdict, model-quality
judgment) is deferred to later, separate assessment artifacts.

## Methodological Strength Note

Methodological strength: weak structural control. The condition `code_first_control` in Run-002 establishes a second execution surface under the same challenge, but does not by itself prove a materially different generation method. Comparative claims remain blocked until a separate assessment artifact evaluates the actual differences.

## Later extension (out of scope for this series update)

- Create an explicit comparison artifact that places Run-001 and Run-002 side-by-side
  without automatic quality/outcome judgment.
- Only then consider any comparative assessment — never inside the run bundles themselves.
- If a third run is added (different tool, model, or condition), repeat the same pattern:
  execute, document, defer comparison.
