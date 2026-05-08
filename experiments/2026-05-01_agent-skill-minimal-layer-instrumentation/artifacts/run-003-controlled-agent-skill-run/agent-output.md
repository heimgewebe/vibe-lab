# Agent Output — Run-003 Controlled Agent/Skill Run

run_id: run-003-controlled-agent-skill-run
agent: claude-sonnet-4-6 (claude-code)
run_purpose: PR-10 run capture — candidate/rehearsal run (first phase). Not an effectiveness evaluation. Not counted as comparable.
produced_at: 2026-05-08T10:00:00Z
artifact_type: repo_local_run_record
epistemics: >
  This artifact is a repo-local run record, not an independently verified execution
  transcript. It documents what the agent reported doing; it does not constitute
  machine-verified proof of execution. The agent_usage claim covers this archived
  artifact, not an independent audit of execution.

## Scope of this Agent Run

This agent (claude-sonnet-4-6 via Claude Code CLI) read the following files as part
of this controlled run:

- docs/playbooks/evidence-control-plane-roadmap-checklist.md
- docs/playbooks/pr-run-evidence-pack.md
- docs/policies/pr-run-evidence-policy.md
- docs/policies/interpretation-budget.md
- experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/artifacts/run-002-controlled-agent-skill-run/run.yml
- experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/artifacts/run-002-controlled-agent-skill-run/measurement.yml
- experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/artifacts/run-002-controlled-agent-skill-run/evidence-pack.yml
- experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/artifacts/run-002-controlled-agent-skill-run/auditor-output.yml
- experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/artifacts/run-002-controlled-agent-skill-run/run_meta.json
- experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/manifest.yml
- experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/results/evidence.jsonl
- experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/results/result.md

## Comparability Assessment (Performed Before Artifact Creation)

Before creating run-003 artifacts, the agent verified comparability against run-002:

- Same experiment path: YES — experiments/2026-05-01_agent-skill-minimal-layer-instrumentation
- Similar scope: YES — run capture + manifest/index update (PR 10)
- Similar repo zone: YES — experiments/, docs/playbooks/
- Similar change type: YES — YAML artifact creation + documentation update
- Same metric structure: YES — all 8 metrics: scope_drift_count, unsupported_claim_count, missing_locator_count, validation_gap_count, review_friction_count, rework_count, false_block_count, task_completion_time_observed
- Same claim/evidence discipline: YES — same repo_local / missing_evidence / self_reported conventions

Verdict: run-003 is not comparable to run-002 for PR-10 counting purposes.
**Reason:** comparability.yml shows `independent_task_or_pr_ref: null` — this run is part of the
same PR-10 session as run-004, not an independent controlled run on a separate task or PR.
Run-003 is retained as a candidate/rehearsal run to document the comparability assessment process.
`current_comparable_runs` remains at 1 (only run-002 qualifies).

## Validation Evidence Scope

Archived validation evidence for this run is limited to targeted-tests.txt and make-validate.txt summaries.
No independently verified pre-artifact baseline transcript is archived.

## Preflight Findings (Diagnosis, Not Effectiveness Claims)

PR 10 roadmap status: open (two further comparable runs required).
Run-002 validated: PASS in auditor-output.yml.
No disallowed claims (effect_claim_allowed, promotion_claim_allowed, causal_claim_allowed) found in run-002 artifacts.
Validator baseline: all three test scripts pass (73 + 3 + 15 tests OK); make validate passes.

## What This Run Does NOT Claim

- No claim that the agent/skill layer is better, more reliable, or more effective.
- No claim that the measurement system is production-ready.
- No claim that any previous PR was agent-assisted in a beneficial way.
- No promotion-readiness claim.
- No CI success claim (CI evidence is not archived in this run).
- No cross-run comparison or effect evaluation (that is PR 11 scope).
