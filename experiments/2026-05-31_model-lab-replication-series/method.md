---
title: "Model-Lab Replication-Series — Method"
status: designed
triggered_by: "user-request-2026-06-06-run-003-semantic-rework"
canonicality: operative
relations:
  - type: references
    target: "artifacts/run-003-rest-api-independent-model-or-tool-condition/condition-input.md"
  - type: references
    target: "artifacts/run-003-rest-api-independent-model-or-tool-condition/run-output.md"
---

# Model-Lab Replication-Series — Method

## Shape of the series

A small, controlled series that grows one run at a time. Three execution surfaces now exist under `rest-api-v1`: a baseline anchor (spec-first), a control run (code-first), and Run-003 under `independent_model_or_tool_condition`. All three runs now have separate runtime-validation artifacts; Run-003's machine-readable gate is `partial`. No result assessment or model-quality evaluation is performed.

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
- **Activation:** `run_meta.json` sets `model_lab_control: true` (AP-1), while `comparability.yml` records
  `compared_against: run-001`. The control run links to the same `rest-api-v1`
  challenge version, enabling first-order comparability structure.
- **Comparability:** `comparability.yml` in Run-002 records
  `verdict: comparable_surface_available`, but comparison remains deferred.

## Run-003 (executed, self-reported different agent/tool/session condition)

Run-003 executes the same `rest-api-v1` challenge under the retained label `independent_model_or_tool_condition`. Its calibrated independence status is `self_reported_different_agent_tool_context`; `external_attestation` is false, so the label does not establish model independence.

The concrete condition boundary is recorded in `artifacts/run-003-rest-api-independent-model-or-tool-condition/condition-input.md`.

Run-003 adds a third execution surface but does not establish model quality, comparative superiority, outcome upgrade, adoption, promotion, production readiness, or security readiness.

Run-003 execution surface exists; Run-003 runtime validation is now archived separately in `artifacts/runtime-validation-run-003/` (machine-readable gate, `validation_status: partial`); no result assessment is performed.

## What is measured now

Three executed run surfaces now exist under the same challenge version. The series
tracks repo-local observations:

- Run-001 and Run-002 both execute deterministically and have separate runtime validation evidence.
- Run-003 execution surface exists; Run-003 runtime validation is now archived separately (gate `validation_status: partial`); no result assessment is performed.
- All three target `rest-api-v1` with identical API surface requirements.
- All three produce implementation and verification artifacts.
- None makes model-quality, comparative, outcome, adoption, promotion, production-readiness, or security-readiness claims.

**Measurement status:** `executed_three_surface_run003_runtime_validation_partial`.

`measurement.yml` in each run records execution completeness, locator presence,
verification evidence, and comparability structure availability. No model comparison
is performed inside the runs. Actual comparison (assessment, verdict, model-quality
judgment) is deferred to later, separate assessment artifacts.

* **Note on Runtime Validation**: Following the creation of the run bundles, a distinct phase was executed to runtime-validate the implementations without mutating the original artifacts. The logs and verification metrics for these executions are isolated in the `runtime-validation-run-001-run-002` directory. Run-003 is runtime-validated in the same way in `runtime-validation-run-003`, expressed as a machine-readable runtime-evidence gate (`validation_status: partial`).

## Methodological Strength Note

Methodological strength: weak structural control. The condition `code_first_control` in Run-002 establishes a second execution surface under the same challenge, but does not by itself prove a materially different generation method. Comparative claims remain blocked until a separate assessment artifact evaluates the actual differences.

## Condition-contrast design gate

- Condition-contrast design criteria now exist (`results/condition-contrast-design-gate.yml`, contract `model-lab-condition-contrast-design-gate.v1`).
- Run-004 design may begin as a separate task.
- No primary axis or concrete condition has been selected.
- The gate fixes how dimensions must be controlled or documented whenever they are not selected as the single primary intervention axis by the later design; it does not decide which dimensions are eligible to become that primary axis.
- No Run-004 execution is allowed.
- Methodological strength remains weak until a compliant contrast is designed, executed and assessed.

## Run-004 condition design (frozen, not executed)

- A frozen condition design now exists (`artifacts/run-004-condition-contrast-design/`, contract `model-lab-condition-design.v1`).
- The single primary axis is `workflow_protocol` with semantics `assigned_instruction_requirement`:
  it varies an **assigned** Spec-First instruction (present vs absent), not an enforced internal
  thought process, and does not require control to actually write code immediately.
- The two future arms are `control: direct_implementation` (no assigned upfront-specification
  requirement) and `treatment: spec_first` (a complete, completeness-checked upfront
  specification is required before any implementation). The treatment overlay is bound by
  `derived_from.snapshot_ref` to the frozen byte-snapshot of the adopted Spec-First
  instruction block (`instruction-blocks/spec-first.md`).
- Both arm overlays are rendered deterministically from one structured workflow-instruction
  source (`workflow-instruction-protocol.yml`) whose shared instruction surface is identical for
  both arms; the validator re-renders and byte-checks them, so no free-form prose can add a
  second axis.
- The input assembly composes, in a fixed order identical for both arms, the frozen benchmark
  byte-snapshot, the shared condition, and the arm overlay; the benchmark component is bound to
  the frozen challenge snapshot.
- Assigned condition vs observed compliance are separated: the design declares the future
  compliance/contamination evidence to collect (e.g. a control arm that voluntarily produces a
  full prior specification is later recorded as `contamination_status: observed`); it does not
  claim to have observed any compliance.
- Prompt scope is an explicit interpretation limit: the axis is a bundled workflow-instruction
  protocol, so a later observed difference must not be attributed to ordering/length/structure
  alone; outer structure, tone, examples, and permissions are held constant across arms.
- All other experimentally relevant dimensions are bound identically across arms; runtime values
  (model, tooling, sampling, dependency/runtime environment, harness) are deferred to a single
  shared execution-readiness binding. Condition semantics are frozen; runtime values are unbound.
- Gate and readiness preconditions are frozen as immutable byte-snapshots under
  `source-snapshots/` (verified once against the base commit `41fa203`); the permanent validator
  reads only those snapshots, never the mutable live files, and derives the required control
  dimensions and confounders by parsing the frozen full gate (no editable reduced list that could
  weaken its own requirements).
- Timing on abort is explicit: `time_to_validated_change_seconds` ends at the shared verification
  pass and is null for an arm that stops earlier; the abort time is a separate metric.
- Historical Run-001/002/003 bundles are context only and are not a clean control arm: they
  differ on more than one uncontrolled dimension (e.g. generation method and self-reported
  model identity).
- The design is frozen before execution via a SHA-256 freeze manifest. No Run-004 arm is
  executed, no runtime environment is bound, and no result is assessed. `weak_condition_contrast`
  remains open; the only permitted next step is a separate execution-readiness / authorization check.

## Next extension

- Cross-Run-Assessment exists as a separate artifact (`results/cross-run-assessment.md`).
- Runtime validation for Run-001 and Run-002 exists in `artifacts/runtime-validation-run-001-run-002`.
- Run-003 execution exists with a self-reported different agent/tool/session boundary; externally attested model independence is not established.
- Run-003 is now runtime-validated in a separate artifact (`runtime-validation-run-003`, gate `validation_status: partial`). A formal `decision_type=result_assessment` remains deferred; runtime contact is a prerequisite, not a result.
- Model-quality, comparative-superiority, outcome, adoption, promotion, production-readiness, and security-readiness claims remain blocked.
