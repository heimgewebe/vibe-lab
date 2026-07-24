---
title: "RepoBrief Workbench Usefulness Evaluation — Result"
status: archived
canonicality: operative
---

# Result

## Summary

This experiment now contains a limited executed run series for Bureau task `RPU-V1-T021`.
It records three comparable audited single-run slices from recent Lenskit RepoBrief work:

1. `RBGV-V1-T005` / Lenskit PR #935 — `repobrief ask` CLI under `context_pack`.
2. `RBGV-V1-T006` / Lenskit PR #936 — ask gold-query evaluation under `trace_gated`.
3. `RPU-V1-T020` / Lenskit PR #940 — read-only MCP resource adapter under `context_pack`.

The series is deliberately marked `executed_limited`, not promotion-grade. It has three comparable implementation slices, but zero uncontaminated paired counterfactuals. Re-running the same tasks under another condition after seeing the implementation would contaminate the comparison.

## Observations

- The recorded runs show positive diagnostic signal for localization, evidence completeness, patch-scope discipline, check fit and explicit boundary handling.
- One concrete implementation bug was caught by tests before PR creation in the MCP resources run: artifact paths initially resolved relative to the process working directory instead of the manifest directory.
- Each run includes external observations such as GitHub CI, merged PR metadata and archived pre-merge patch SHA.
- Self-authored tests are treated as observations, not proof of correctness.

## Decision

- `context_pack`: `pilot`
- `trace_gated`: `pilot_diagnostic_gate`
- `reading_pack`: `defer`
- `no_context_no_rlens`: `defer`
- `full_resolved_evidence`: `defer_diagnostic_only`

No condition is promoted to default access. The evidence supports careful pilots only.

## Allowed claims

- A limited run series exists and validates structurally.
- The recorded runs provide useful diagnostic signals for some RepoBrief/Workbench surfaces.
- Context-pack and trace-gated surfaces are plausible pilot candidates.
- The series preserves non-claims and blocks default promotion.

## Disallowed claims

- RepoBrief or Agent Workbench is proven to improve agent quality.
- Any condition is superior to all alternatives.
- Full/resolved evidence is safe as a default.
- Generated or local green checks prove correctness.
- This series establishes runtime correctness, test sufficiency, review completeness, security correctness or merge readiness.
