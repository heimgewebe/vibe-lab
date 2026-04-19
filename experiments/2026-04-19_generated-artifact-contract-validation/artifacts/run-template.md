# PR Run Template

Use this template for each real PR run in this experiment.

## Required fields

- pr_ref:
- baseline_ref:
- run_id:
- changed_canonical_count:
- changed_derived_count:
- changed_ephemeral_count:
- ci_blocking_failures:
- ci_non_blocking_warnings:
- manual_regen_steps:
- unnecessary_commit_delta:
- diagnosis_clarity_score:
- notes:

## Output artifacts

Create:

- artifacts/<run-id>/run_meta.json
- artifacts/<run-id>/execution.txt

Append corresponding entries to results/evidence.jsonl.
