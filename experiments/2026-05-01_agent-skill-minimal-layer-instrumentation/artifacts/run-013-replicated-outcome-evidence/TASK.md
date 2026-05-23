# run-013: Replicated Outcome Evidence — Task Brief

**Status:** PENDING — awaiting agent execution

**Bundle path:**
`experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/artifacts/run-013-replicated-outcome-evidence/`

## Goal

Produce a second non-trivial task-diversity/outcome-evidence run that does NOT upgrade
RM-002/RM-005, but directly tests whether `review_friction_count` and `rework_count`
can be captured across a genuinely different task class.

## Motivation

run-012 self-reports outcome utility as `not_proven`. The roadmap keeps EP-002 blocked
because ≥3 comparable PRs exist but usefulness remains `insufficient_proof`. This run
must provide independent, non-self-reported evidence or write an inability report.

## Task Class

Choose a non-trivial task outside the validator-test-hardening cluster and outside
run-009's task class. Prefer a documentation/contract-alignment task touching exactly
2–4 files with clear before/after reviewability.

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

## Constraints

- Do not edit prior run artifacts.
- Do not mark usefulness/adoption/promotion as proven.
- Do not change schemas unless validation proves impossible.
- Keep overall interpretation `CLAIM_NOT_PROVEN` unless evidence independently supports otherwise.
- Treat validator-green as integrity evidence only, not outcome proof.
- RM-002 and RM-005 must remain open.

## Stop Condition

If any required metric cannot be captured without self-report inflation, stop and write
an inability/limitation report instead of fabricating values.

## Validation (after bundle is created)

```bash
python3 scripts/docmeta/test_validate_run_bundle.py
python3 scripts/docmeta/test_validate_claim_evidence.py
make validate-run-bundle
make validate
```

## Required Updates (after validation passes)

- `experiment manifest.yml`: add run-013 artifacts, bump iteration/date.
- `docs/roadmap.md`: add note that run-013 adds replicated outcome-evidence data
  but does not by itself close RM-002/RM-005.
- Regenerate generated docs if `make validate` requires it.
