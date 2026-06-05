---
title: "Run-003 Plan — Stronger Condition Contrast"
status: designed
canonicality: operative
created: "2026-06-05"
updated: "2026-06-05"
triggered_by: "user-request-2026-06-05-model-lab-next-step-diagnosis"
relations:
  - type: references
    target: "../../results/cross-run-assessment.md"
  - type: references
    target: "../runtime-validation-run-001-run-002/runtime-validation.yml"
  - type: references
    target: "../run-001-rest-api-spec-first-baseline/run.yml"
  - type: references
    target: "../run-002-rest-api-code-first-control/run.yml"
---

# Run-003 Plan — Stronger Condition Contrast

## Purpose

This plan records the next implementation step after the existing Run-001/Run-002 runtime-validation addendum.
It is a planning artifact only: it does not execute Run-003, does not generate an implementation, and does not create a result assessment.

## Diagnosis basis

- Run-001 and Run-002 are runtime-validated through `artifacts/runtime-validation-run-001-run-002/`.
- The cross-run assessment still treats the quality result as inconclusive.
- The documented blocker for stronger comparison is no longer missing runtime contact; it is the weak condition contrast between `spec_first_baseline` and `code_first_control`.

## Planned Run-003 condition

Run-003 should use the same `rest-api-v1` challenge while changing the execution condition more materially than the Run-001/Run-002 label difference.

Planned condition label:

```text
independent_model_or_tool_condition
```

Minimum contrast requirements before execution:

- Use a different model or toolchain from the one that produced the archived Run-001/Run-002 implementation bundles, or document why the model/tool boundary is genuinely different.
- Keep `challenge_version: rest-api-v1` unchanged.
- Keep Model-Lab control metadata opt-in and explicit.
- Archive condition input, execution trace, changed-files artifact, run metadata, measurement, comparability, and auditor output before making any comparison claim.

## Runtime-validation expectation after execution

If Run-003 is executed, a separate post-run validation artifact should record:

- repo-local static verifier execution,
- Vitest runtime execution,
- forced 500 error-envelope runtime assertion,
- npm audit or dependency-risk observations if present.

The validation artifact should remain append-only and separate from the historical run bundle.

## Non-claims

This plan does not establish:

- model quality,
- comparative superiority,
- condition effect,
- outcome upgrade,
- adoption,
- promotion,
- production readiness,
- security readiness.

## Next gate

Before building Run-003, confirm the concrete model/tool/condition boundary and record it in the run-local condition input. If that boundary cannot be made concrete, do not execute Run-003 and keep the series at an inconclusive comparison surface.
