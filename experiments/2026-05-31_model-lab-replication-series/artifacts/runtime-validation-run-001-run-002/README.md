# Runtime Validation for Run-001 and Run-002

This artifact provides runtime evidence for the implementations produced in `run-001-rest-api-spec-first-baseline` and `run-002-rest-api-code-first-control`.

The original run bundles successfully generated the implementations and test specifications, but left them as unexecuted artifacts (MISSING_EVIDENCE for runtime validation, particularly the forced 500 error-handling paths).

This artifact closes that evidence gap by actually executing the tests and static verifiers against the archived code, proving that the existing `run-001` and `run-002` implementations are indeed fully executable and pass their assertions.

## Interpretation Limits
- **No historical rewrite**: The original runs remain unchanged. This is a separate, post-hoc validation.
- **No model-quality claim**: This artifact does not evaluate whether Code-First or Spec-First is superior.
- **No adoption/promotion claim**: The implementations remain experimental.

## Evidence Included
- `verifier-run-*.txt`: Output of the static Python verifier.
- `vitest-run-*.txt`: Output of the full Vitest suite.
- `forced-500-run-*.txt`: Output of a targeted test injecting a 500 error to verify the response envelope behavior.
- `runtime-validation.yml`: Structured claims and verdicts.
