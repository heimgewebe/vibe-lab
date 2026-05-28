---
title: "Outcome-Evidence-Replication-Series — Results"
status: designed
canonicality: operative
---

# Outcome-Evidence-Replication-Series — Results

## Summary

The first real run was executed (`run-001-contract-documentation-alignment`) with a contract-/documentation-alignment scope only. There is still no outcome upgrade, no CLAIM_NOT_PROVEN upgrade, and no adoption basis.

Run-003 adds a new task class, `validator_test_hardening`, but only as a conservative evidence-/artifact-level hardening run. No validator or test code path effect is claimed from this run.

Run-004 delivers a **real** validator effect: `scripts/docmeta/validate_outcome_evidence_replication_series.py` (new), 30 regression tests, a file-based fixture corpus under `tests/fixtures/outcome_evidence_replication_series/`, and Makefile integration (`make validate-outcome-series`, `make validate-outcome-series-tests`). This is the first run with actual `scripts/` and `tests/` changes. No outcome upgrade is claimed.

## Observations

- Run-001 artifacts are present under `artifacts/run-001-contract-documentation-alignment/`.
- The run is explicitly constrained to `outcome_upgrade_allowed: false`.
- Independence is documented as `partial` for this run.
- No negative control was executed in run-001.
- Run-002 adds a stable negative control under `artifacts/run-002-negative-control-claim-not-proven/`.
- `CLAIM_NOT_PROVEN` remains stable for Run-002, but there are still not four comparable runs.
- Run-003 adds `artifacts/run-003-validator-test-hardening/` as a small validator-/test-hardening-scoped bundle.
- Run-003 is explicitly documented as evidence-/artifact-level hardening only; no real validator or test code change is asserted.
- Run-004 adds `artifacts/run-004-real-validator-test-hardening/` with a real gate validator and 30 tests. `changed-files.txt` records `scripts/`, `tests/`, and `Makefile` paths.
- The series still has no outcome upgrade, no usefulness verdict, and no adoption or promotion basis.

## Interpretation

The gate is now applied across a slightly broader set of run types, including a negative control and a validator-/test-hardening documentation slice. The run-003 task class is tracked for bookkeeping only and must not be counted as outcome-gate task diversity while no real validator or test code path is changed. It still does not create comparable outcome evidence or justify any outcome conclusion.

## Verdict

Executed, but outcome not upgraded.

## Promotion-Readiness Note

`docs/_generated/promotion-readiness.json` may still mark this experiment as
`promotion_ready=true`, now with `execution_status=executed` and warning
`falsifiability_assessment_inconclusive`. This is only a dry-run schema/readiness
classification.

It must not be interpreted as outcome readiness, adoption readiness, promotion,
usefulness evidence, or a `CLAIM_NOT_PROVEN` upgrade. Run-001 is partial,
not comparable yet, and has no negative control.

## Lessons Learned

- Gate-first planning is required before adding more outcome runs.
- Partial independence is not enough for outcome upgrade decisions.
- A stable negative control must be part of the series before promotion is considered.
- Contract-/documentation-alignment runs can harden gate usage without changing outcome status.
- Validator-/test-hardening runs must state clearly whether they changed real validator or test code or only hardened evidence artifacts. Artifact-level hardening alone does not justify an effect claim.

## External Cross-Family Audit Note

Run-001 now has an additive external cross-family audit:
`artifacts/run-001-contract-documentation-alignment/external-audit-claude-opus-4-7.yml`.

This audit is supplementary. It does not replace `auditor-output.yml`.
It supports auditor independence for this audit via the different-AI-system /
different-model-family branch of the gate, but it does not change
`comparability.yml verdict: not_comparable`.

This audit itself does not satisfy the four-comparable-runs threshold and does
not add a negative control. Run-002 later adds a separate negative-control run,
but the series still lacks four comparable runs and no outcome, usefulness,
promotion, adoption, or `CLAIM_NOT_PROVEN` upgrade is justified.

## Next Steps

Continue with additional task classes, stronger independence, and more comparable runs while keeping outcome upgrades disabled until gate criteria are met.
