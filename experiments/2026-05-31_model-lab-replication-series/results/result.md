---
title: "Model-Lab Replication-Series — Results"
status: testing
triggered_by: "user-request-2026-06-06-run-003-semantic-rework"
canonicality: operative
---

# Model-Lab Replication-Series — Results

## Status

Run-001 and Run-002 are now executed runs for `rest-api-v1`. The baseline
`run-001-rest-api-spec-first-baseline` (condition: `spec_first_baseline`) and
the control `run-002-rest-api-code-first-control` (condition: `code_first_control`)
together form a **first-order comparability surface**. Both runs contain repo-local
execution evidence, keep opt-in Model-Lab control metadata (`model_lab_control: true`),
and remain bound to `challenge_version: rest-api-v1`.

## What this establishes

- Two real execution artifacts now exist for `rest-api-v1`.
- AP-1 (`validate_model_lab_control`) Model-Lab metadata is exercised on both executed run metadata files.
- AP-2 (`validate_challenge_versions`) challenge-version metadata remains bound
  to `rest-api-v1` through the series-level execution decision, while Run-001
  and Run-002 carry matching challenge-version metadata in their run-local
  artifacts.
- Both runs produce TypeScript/Fastify implementation shapes, repo-local static verifier scripts,
  and Vitest specifications under `implementation/`.
- A separate runtime-validation artifact now records static verifier execution, Vitest runtime execution, and forced 500 error-envelope assertions for both archived implementations.
- **Comparability structure is now runtime-validated but still inconclusive:** Run-001 and Run-002 address the same challenge version with isolated conditions, but their condition contrast remains too weak for a model-quality or condition-effect verdict.

## What this does NOT establish

- No model-quality verdict.
- No comparative verdict (e.g., "code-first is better" or "spec-first is confirmed").
- No outcome upgrade.
- No adoption.
- No promotion.
- No staleness reactivation.
- **No automatic verdict from the presence of two runs alone.** Comparison structure ≠ comparison result.

## Interpretation limit

This establishes two executed baseline + control artifacts under the same challenge plus separate runtime validation for their archived implementation test surfaces. The structure supports comparison, but the comparison remains inconclusive because the condition contrast is weak and no independent/external auditor comparison exists. Comparability structure and runtime contact are prerequisites for stronger assessment, not a verdict.

Promotion-readiness in `docs/_generated/promotion-readiness.json` denotes
metadata/gate readiness only. It does not authorize outcome upgrade, adoption,
promotion, or model-quality claims.

## Next step

Run-003 execution now exists with `independence_status: self_reported_different_agent_tool_context` and `external_attestation: false`. The separate Run-003 runtime-validation artifact now exists (`artifacts/runtime-validation-run-003/`, gate `validation_status: partial`). A formal `decision_type=result_assessment` remains deferred: runtime contact alone is not a comparison result.

## Run-003 addendum

Run-003 execution surface exists; Run-003 runtime validation is now archived separately in `artifacts/runtime-validation-run-003/` as a machine-readable runtime-evidence gate (`validation_status: partial`). The functional runtime checks (static verifier, Vitest suite, forced-500 error envelope) passed; `npm audit` observed unremediated high-severity dev-toolchain advisories, so the gate is partial, not pass. This is runtime evidence only. No result assessment is performed. The boundary is a self-reported different agent/tool/session context, not externally attested model independence. The series remains inconclusive for model-quality or condition-effect claims, and `comparison_ready` remains false.

## Result-assessment readiness

A machine-readable result-assessment-readiness artifact (`results/result-assessment-readiness.yml`) records that a formal `result_assessment` is currently blocked. The series has runtime contact across three execution surfaces, but `result_assessment_allowed=false` and `comparison_ready=false`: the open blockers are the scoped-but-unremediated dependency-risk caveat, the weak condition contrast, the missing external independent auditor comparison, and Run-003's self-reported (not externally attested) independence. No model-quality, comparative-superiority, condition-effect, outcome-upgrade, outcome-assessment, adoption-readiness, promotion-readiness, production-readiness, production-correctness, security-readiness, absence-of-regressions, absence-of-vulnerabilities, dependency-risk-remediated, dependency-tree-safe, supply-chain-safety, production-dependency-health, security-approval, or externally-attested model independence claim is derived. Runtime evidence is a prerequisite for assessment, not a comparison result.

## Dependency-risk caveat scope

A machine-readable dependency-risk-caveat-scope artifact
(`results/dependency-risk-caveat-scope.yml`) records that the Run-003 npm audit
finding is scoped but not remediated. The scope preserves the limited functional
runtime evidence while keeping security-readiness, production-readiness,
result_assessment, and comparison_ready blocked. It does not establish
absence-of-vulnerabilities, dependency-risk-remediated, dependency-tree-safe,
supply-chain-safety, production-dependency-health, security-approval,
production-correctness, outcome-assessment, or absence-of-regressions.

## Next-blocker triage

A machine-readable next-blocker-triage artifact (`results/next-blocker-triage.yml`)
names the next methodological step: address `weak_condition_contrast` via a
`condition_contrast_design_gate` before Run-004 or any formal assessment. This is
a prioritization only — no result assessment, no dependency remediation, and no
change to the blocked status. `result_assessment_allowed` stays false and
`comparison_ready` stays false.

## State after iteration 10 — condition-contrast design gate

A machine-readable condition-contrast design gate
(`results/condition-contrast-design-gate.yml`) defines the criteria a future
Run-004 condition-contrast design must satisfy.

- condition-contrast criteria defined
- Run-004 design may begin
- Run-004 execution remains blocked
- `weak_condition_contrast` remains open
- result assessment remains blocked
- `comparison_ready` remains false
- no primary intervention axis or concrete condition has been selected
- the gate defines only criteria and the control treatment of non-primary dimensions

## State after iteration 13 — frozen condition design (source-bound)

A machine-readable, frozen condition design now exists
(`artifacts/run-004-condition-contrast-design/`, contract `model-lab-condition-design.v1`).
It records only a design-state transition; it asserts no effect, quality, or comparison.
This supersedes (does not contradict) the iteration-10 gate state above: the gate defined
criteria; this design selects and freezes the concrete contrast and binds it to verified
immutable source byte-snapshots.

- the single primary axis is `workflow_protocol` with semantics `assigned_instruction_requirement`
  (an assigned Spec-First instruction present vs absent, not an enforced internal thought process)
- two future arms are concretised: `control: direct_implementation` and `treatment: spec_first`
- the arms differ operationally only along the assigned workflow-instruction overlay; all other
  dimensions are bound identically
- the gate/readiness/challenge/spec-first sources are frozen as immutable byte-snapshots under
  `source-snapshots/` with verified provenance; gate requirements are derived from the frozen full
  gate (no editable reduced list)
- the input assembly composes the frozen benchmark, the shared condition, and the arm overlay in a
  fixed order identical for both arms; overlays are rendered from one structured workflow source and
  byte-checked, so no free-form prose can add a second axis
- the protocols, structured source, snapshots, and design are frozen via a SHA-256 freeze manifest
  that records no self-reference and no commit/tree/head SHA
- gate/readiness preconditions are read from the frozen snapshots, not from mutable live state
- condition semantics are frozen; concrete runtime values are still unbound
  (`execution_binding_status: pending`)
- the assigned condition and the later observed compliance are separated; compliance is a
  declared future measurement, not something this design claims to have observed
- prompt scope is an interpretation limit: a later observed difference must not be attributed
  to ordering/length/structure alone
- no condition was executed, measured, or assessed; `weak_condition_contrast` remains open
- result assessment remains blocked and `comparison_ready` remains false
- the only permitted next step is a separate execution-readiness / authorization check

## State after iteration 14 — blinded delivery and bound provenance roles

Iteration 14 hardens the same frozen design (no new state transition, no execution): it closes
four trust boundaries that hash-integrity alone left open. It still asserts no effect, quality, or
comparison.

- **Source role/provenance binding.** Each frozen source must come from its exact canonical path
  (gate/readiness under `results/`, challenge derived from `challenge_version`, spec-first under
  `instruction-blocks/`), carry the role's `artifact_type`, and share the freeze
  `source_base_commit_sha`. A correctly-hashed but mislabelled or mis-located source is now rejected.
- **Prompt-component role binding.** `shared_condition` must be the bundle's `common-condition.md`;
  the eight operative files must be pairwise distinct; the treatment arm is grounded in the frozen
  spec-first snapshot via `spec_first_basis` (renamed from `derived_from`) while the control arm is
  forbidden any grounding (enforced role-specifically by the schema).
- **Blinded delivered prompt.** The text actually delivered to the future agent (shared condition +
  both overlays) carries no role names, axis names, hypothesis, or experiment framing; the framing
  lives only in the design, `method.md`, and the non-delivered `control_metadata`.
- **Control = absence.** The control overlay is the neutral task baseline (no specification mention,
  no negative instruction); the treatment overlay is that exact baseline plus a positive Spec-First
  requirement whose body is the frozen spec-first snapshot embedded verbatim. The only delta between
  the two delivered prompts is the added requirement.
- Delivered files are decoded strictly (UTF-8, LF-only, final newline; no `errors="replace"`).
- The frozen-source provenance was re-verified once against base commit `41fa203` (all four sources
  MATCH `git show 41fa203:<path>`); the freeze manifest was recomputed for the changed files.
- no condition was executed, measured, or assessed; `weak_condition_contrast` remains open;
  `result_assessment_allowed` and `comparison_ready` remain false; the only permitted next step is a
  separate execution-readiness / authorization check.

## State after iteration 16 — Run-004 execution-readiness preflight

A machine-readable Run-004-v1 execution-readiness bundle now exists at
`artifacts/run-004-execution-readiness/`. It validates the readiness contract and freezes the
readiness bundle before any execution.

The real readiness status is `blocked`: `runtime_values_bound=false`,
`authorization_status=not_authorized`, `run_004_execution_allowed=false`,
`run_004_executed=false`, `result_assessment_allowed=false`, and `comparison_ready=false`.

Open blocking readiness blockers are:

- `MODEL_BINDING_UNRESOLVED`
- `AGENT_BINDING_UNRESOLVED`
- `SAMPLING_BINDING_UNRESOLVED`
- `EXECUTION_SEED_UNRESOLVED`
- `BLINDED_WORKSPACE_UNRESOLVED`
- `SESSION_ISOLATION_UNPROVEN`
- `FRAMEWORK_NEUTRAL_HARNESS_UNRESOLVED`
- `FORCED_500_TRIGGER_UNRESOLVED`
- `FIRST_MUTATION_TRACE_UNRESOLVED`

`WEAK_CONDITION_CONTRAST_OPEN` remains open as an informational blocker in the readiness artifact and
as a methodological blocker for later assessment. No Run-004 arm was executed, no measurement or
comparison evidence was produced, and no model-quality, comparative-superiority, condition-effect,
outcome-upgrade, adoption, promotion, production-readiness, or security-readiness claim is derived.
