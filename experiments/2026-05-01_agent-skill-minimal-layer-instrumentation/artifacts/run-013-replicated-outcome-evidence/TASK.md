# run-013: Replicated Outcome Evidence — Task Brief

**Status:** EXECUTED / HISTORICAL TASK BRIEF — run bundle created; this file is not itself outcome evidence

This file is a pre-execution task brief. It is not itself the run-013 evidence bundle
and must not be counted as outcome evidence.

**Bundle path:**
`experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/artifacts/run-013-replicated-outcome-evidence/`

## Goal

Produce a second non-trivial task-diversity/outcome-evidence run that does NOT upgrade
RM-002/RM-005, but directly tests whether `review_friction_count` and `rework_count`
can be captured across a genuinely different task class.

## Motivation

run-012 self-reports outcome utility as `not_proven`. The roadmap keeps RM-002/RM-005
blocked because ≥3 comparable PRs exist but usefulness remains `insufficient_proof`.
This run must provide independently reviewable source artifacts for review/rework
metrics or write an inability report. Self-authored absence records may document
missing review/rework evidence, but must not upgrade metric confidence beyond
`repo_local` and must not be treated as independent outcome evidence.

## Task Class

Choose a non-trivial task outside the validator-test-hardening cluster and outside
run-009's task class. Prefer a documentation/contract-alignment task touching exactly
2–4 files with clear before/after reviewability.

## Concrete Execution Target

The executing agent must first propose the exact target task before creating the run bundle.

The target task must satisfy all of the following:

- touches exactly 2–4 files;
- changes at least one normative or semi-normative document, not only generated output;
- is outside validator-test-hardening and outside run-009's task class;
- has a clear before/after claim that can be reviewed by another agent or reviewer;
- produces changed-files evidence;
- can receive or record review feedback before final metric interpretation;
- does not upgrade RM-002 or RM-005.

Suggested target class:
Documentation/contract-alignment around roadmap/usefulness evidence semantics, for example
clarifying how `review_friction_count`, `rework_count`, and
`task_completion_time_observed` may and may not support RM-002/RM-005.

## Required Artifacts

1. `run.yml`
2. `measurement.yml`
3. `auditor-output.yml`
4. `evidence-pack.yml`
5. `comparability.yml`
6. `changed-files.txt`
7. `targeted-tests.txt`
8. `make-validate.txt`
9. `review-events.yml`
10. `timing.txt`
11. `review-source.txt` or `review-source.md`
12. `inability-report.md` if any required evidence cannot be captured

## Constraints

- Do not edit prior run artifacts.
- Do not mark usefulness/adoption/promotion as proven.
- Do not change schemas in this run. If current schemas cannot represent the required
  evidence without distortion, stop and write an inability/limitation report.
- Keep overall interpretation `CLAIM_NOT_PROVEN` unless evidence independently supports otherwise.
- Treat validator-green as integrity evidence only, not outcome proof.
- RM-002 and RM-005 must remain open.
- Do not create the final run bundle until the exact target task is named and checked
  against the constraints in this brief.

## Metric Evidence Rule

A metric may only be non-null if it is backed by an explicit source artifact.

Allowed sources include:

- PR review export;
- Copilot review comments;
- human review comment;
- `git log` showing rework commits;
- explicit no-review/no-rework artifact with timestamp and scope, only to document `MISSING_EVIDENCE` or absence-of-review context; it must not by itself justify `review_friction_count: 0` or `rework_count: 0`.

Do not infer `review_friction_count` or `rework_count` from absence of evidence.
Absence of review evidence is `MISSING_EVIDENCE`, not zero.

## Stop Condition

If any required metric cannot be captured without self-report inflation, stop and write
an inability/limitation report instead of fabricating values.

If review or rework evidence is absent, record the absence as `MISSING_EVIDENCE` with
reason and add an explicit source artifact instead of inferring a zero value.

If an inability report is written before a schema-valid run bundle can be produced, do
not register run-013 as completed evidence. Register only the pre-execution/inability
artifact if the manifest requires discoverability. If a schema-valid minimal bundle can
be produced, all unavailable metrics must remain null/`MISSING_EVIDENCE` and
`overall_verdict` must remain `CLAIM_NOT_PROVEN`.

## Validation (after bundle is created)

```bash
python3 scripts/docmeta/test_validate_run_bundle.py
python3 scripts/docmeta/test_validate_claim_evidence.py
make validate-run-bundle
make validate
```

## Required Updates (after validation passes)

- `experiment manifest.yml`: add run-013 artifacts, bump iteration/date.
- `docs/roadmap.md`: add a note that run-013 records a replicated
  outcome-evidence attempt, with evidence strength determined by the produced
  artifacts; do not state that replicated outcome evidence exists unless
  review/rework/timing evidence is actually captured. In all cases,
  RM-002/RM-005 remain open unless separately supported by stronger evidence.
- Regenerate generated docs if `make validate` requires it.
