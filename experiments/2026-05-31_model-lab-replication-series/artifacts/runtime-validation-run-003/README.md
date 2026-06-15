# Runtime Validation for Run-003

This artifact provides runtime evidence for the implementation produced in
`run-003-rest-api-independent-model-or-tool-condition`, closing the runtime-evidence
gap that the Run-003 bundle recorded as deferred (`MISSING_EVIDENCE`).

It mirrors the approach already used for `runtime-validation-run-001-run-002`: a
separate, post-hoc validation that executes the archived code and archives the
captured outputs **without rewriting the historical Run-003 bundle**.

## What is new here: a machine-readable runtime-evidence gate

`runtime-evidence-gate.yml` is an instance of the `runtime-evidence-gate.v1`
contract (`schemas/runtime-evidence-gate.v1.schema.json`), enforced by
`scripts/docmeta/validate_runtime_evidence_gate.py` and wired into `make validate`.
The gate makes the runtime evidence machine-checkable:

- which runtime commands were executed (with exit codes),
- where each output is archived,
- a per-check rollup (`validation_status`),
- a mandatory `does_not_establish` anti-overclaim list.

The per-claim runtime evidence is **also** recorded in `evidence-pack.yml` using
the existing `run-evidence-pack.v1` contract, so it is validated by the existing
`validate_claim_evidence.py` (via `make validate-claim-evidence`). The new gate
contract is purely additive: it adds only the gate-level semantics
(`validation_status` rollup + mandatory `does_not_establish`) that the existing
run-evidence-pack contract cannot express.

## Result for Run-003

`validation_status: partial`.

| Check | Status | Evidence |
|-------|--------|----------|
| static verifier (`verify-run-003.py`) | pass | `static-verifier-run-003.txt` |
| runtime tests (`npm test` / Vitest) | pass | `vitest-run-003.txt` |
| forced-500 error envelope | pass | `forced-500-run-003.txt` |
| dependency audit (`npm audit`) | partial | `dependency-audit-run-003.txt` |

The functional runtime validation (static verifier, Vitest suite, forced-500
error-envelope assertion) passed with exit code 0. `npm audit --audit-level=moderate`
exited 1 with 5 high-severity advisories in the dev toolchain (esbuild / vite /
vitest), observed and **not** remediated — so the overall gate is `partial`, not
`pass`.

## Interpretation limits

- **No historical rewrite**: the Run-003 bundle is unchanged. This is a separate,
  post-hoc validation.
- **No model-quality claim**, no comparative-superiority claim, no adoption /
  promotion / production-readiness / security-readiness claim.
- **No externally attested model independence**: `independence_status` remains
  `self_reported_different_agent_tool_context` (`external_attestation: false`).
- The dependency-audit finding means this artifact must not be used as a security
  or production-dependency-health approval.

## Evidence included

- `runtime-evidence-gate.yml` — machine-readable gate (new `runtime-evidence-gate.v1`).
- `evidence-pack.yml` — per-claim runtime evidence (`run-evidence-pack.v1`, reused).
- `environment.txt` — captured toolchain versions.
- `replay-commands.txt` — exact commands executed.
- `static-verifier-run-003.txt`, `vitest-run-003.txt`, `forced-500-run-003.txt`,
  `npm-install-run-003.txt`, `dependency-audit-run-003.txt` — captured outputs.
- `forced-500.test.ts` — the canonical forced-500 template used for the assertion.

## Replay note for forced-500.test.ts

`forced-500.test.ts` is archived here as the canonical template. During runtime
validation it was copied into `run-003-.../implementation/tests/forced-500.test.ts`,
executed with `npx vitest run tests/forced-500.test.ts` so the relative import
`../src/server` resolves, and then removed to avoid mutating the historical bundle.
The captured runtime evidence is archived in `forced-500-run-003.txt`.
