---
canonical: false
derived_from: "./auditor-output.yml"
role: "human_projection"
source_of_truth: false
run_id: "run-002-controlled-agent-skill-run"
pr_ref: "github:heimgewebe/vibe-lab/pull/TBD"
auditor_date: "2026-05-07"
auditor: "evidence-reconciliation-auditor (copilot-agent)"
---

> **Non-canonical projection.** The machine-readable source of truth is [`auditor-output.yml`](./auditor-output.yml). This Markdown file is a human-readable view only.

## Verdict

PASS

## Proven Claims

- Run bundle exists and references canonical run artifacts including evidence-pack coupling.
- Measurement exists and keeps metric-level gaps explicit (`review_friction_count`, `rework_count`).
- `run_meta.json` binds targeted command chain to `targeted-tests.txt`.
- Run interpretation boundaries explicitly forbid effect, promotion, and causal claims.

## Missing Evidence

none (run-level auditor claims)

## Interpretation Limits

- Metric-level gaps remain in `measurement.yml` and are not treated as run-level auditor missing evidence.
- `task_completion_time_observed` is self-reported and not cross-run comparable.
- No effectiveness, promotion, or causal claim is allowed.
