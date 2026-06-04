---
title: "Model-Lab Replication-Series — Results"
status: testing
triggered_by: "user-request-2026-06-01-execute-real-model-lab-baseline-run"
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
  and executable (but unrun) Vitest specifications under `implementation/`.
- **Comparability structure is now available:** Run-001 and Run-002 address the same challenge
  version with isolated, different conditions, enabling a first-order comparison surface.

## What this does NOT establish

- No model-quality verdict.
- No comparative verdict (e.g., "code-first is better" or "spec-first is confirmed").
- No outcome upgrade.
- No adoption.
- No promotion.
- No staleness reactivation.
- **No automatic verdict from the presence of two runs alone.** Comparison structure ≠ comparison result.

## Interpretation limit

This establishes two executed baseline + control artifacts under the same challenge.
The structure supports comparison, but the comparison itself remains blocked until
an **explicit, separate comparison artifact** is created. Comparability structure
is a prerequisite for comparison, not a verdict.

Promotion-readiness in `docs/_generated/promotion-readiness.json` denotes
metadata/gate readiness only. It does not authorize outcome upgrade, adoption,
promotion, or model-quality claims.

## Next step

Create an explicit, separate comparison artifact that places Run-001 and Run-002
side-by-side, comparing their implementation, verification coverage, and behavior
without automatic quality/outcome judgment. This artifact should remain separate
from the run bundles, allowing future runs (third, fourth, etc.) to be added
without disrupting the comparison structure.
