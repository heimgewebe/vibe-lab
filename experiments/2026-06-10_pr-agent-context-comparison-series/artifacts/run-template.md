# Run Template — PR Agent Context Comparison Series

## Required metadata

- run_id:
- condition:
- task_class:
- source_pr_or_review_ref:
- executor:
- started_at:
- finished_at:
- validation_possible: true | false

## Required files

- `run.yml`
- `run_meta.json`
- `condition-input.md`
- `agent-output.md`
- `changed-files.txt` or `no-changes.txt`
- `targeted-tests.txt` or `diagnostic-checks.txt`
- `measurement.yml`
- `comparability.yml`
- `auditor-output.yml`
- `evidence-pack.yml`
- `timing.txt`

## Measurement checklist

Record these metrics explicitly:

- unsupported_claim_count
- missing_locator_count
- scope_drift_count
- validation_gap_count
- review_friction_count
- rework_count
- false_block_count
- task_completion_time_observed
- evidence_quality_score
- reviewer_correction_rounds
- context_preparation_cost
- output_reuse_value

## Claim boundary

Allowed:

- "This run produced these observed metrics."
- "This output needed this many correction rounds."
- "This evidence pack supports or does not support the run-local execution claim."

Disallowed:

- "Condition X is better" from one run.
- "Lenskit improves agent quality" without repeated comparable tasks.
- "Vibe-Lab is proven useful" without cross-run assessment.
