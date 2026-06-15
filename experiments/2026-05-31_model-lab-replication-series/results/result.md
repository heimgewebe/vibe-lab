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
