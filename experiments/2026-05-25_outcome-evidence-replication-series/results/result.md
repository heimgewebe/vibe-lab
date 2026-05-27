---
title: "Outcome-Evidence-Replication-Series — Results"
status: designed
canonicality: operative
---

# Outcome-Evidence-Replication-Series — Results

## Summary

The first real run was executed (`run-001-contract-documentation-alignment`) with a contract-/documentation-alignment scope only. There is still no outcome upgrade, no CLAIM_NOT_PROVEN upgrade, and no adoption basis.

## Observations

- Run-001 artifacts are present under `artifacts/run-001-contract-documentation-alignment/`.
- The run is explicitly constrained to `outcome_upgrade_allowed: false`.
- Independence is documented as `partial` for this run.
- No negative control was executed in run-001.
- Run-002 adds a stable negative control under `artifacts/run-002-negative-control-claim-not-proven/`.
- `CLAIM_NOT_PROVEN` remains stable for Run-002, but there are still not four comparable runs.
- The series still has no outcome upgrade, no usefulness verdict, and no adoption or promotion basis.

## Interpretation

The gate is now applied in a real run context, but this remains a narrow alignment run. The current state supports artifact discipline and comparability labeling, not an outcome conclusion.

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

## External Cross-Family Audit Note

Run-001 now has an additive external cross-family audit:
`artifacts/run-001-contract-documentation-alignment/external-audit-claude-opus-4-7.yml`.

This audit is supplementary. It does not replace `auditor-output.yml`.
It supports auditor independence for this audit via the different-AI-system /
different-model-family branch of the gate, but it does not change
`comparability.yml verdict: not_comparable`.

It does not satisfy the four-comparable-runs threshold, does not add a negative
control, does not upgrade `CLAIM_NOT_PROVEN`, and does not justify promotion,
adoption, usefulness, or outcome upgrade.

## Next Steps

Continue with additional task classes and stronger independence while keeping outcome upgrades disabled until gate criteria are met.
