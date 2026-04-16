# Task Validity Check — Iteration 2

- date: 2026-04-16
- triggered_by: user_feedback_wrong_measurement_object
- purpose: verify whether tasks are operationalized enough to test the primary hypothesis
- proof_artifact: artifacts/task-validity-proof.txt

## Rule Set (M0)
A task is valid iff it contains:
1. `target_files`
2. `target_lines` locator
3. `change_type`

## Verification Outcome

| task_id | has_target_files | locator_found_in_repo | has_change_type | valid |
| --- | --- | --- | --- | --- |
| T1 | yes | yes (`docs/index.md:66`) | yes | yes |
| T2 | yes | yes (`.github/workflows/validate.yml:24`) | yes | yes |
| T3 | yes | yes (`scripts/docmeta/validate_schema.py:14`) | yes | yes |
| T4 | yes | yes (`CONTRIBUTING.md:35`) | yes | yes |
| T5 | yes | yes (`README.md:33`) | yes | yes |
| T6 | yes | yes (`experiments/2026-04-15_agent-task-validity/method.md:21`) | yes | yes |

## Result

- M0 (task_validity_rate) = 6 / 6 = **1.0**
- Iteration-1 baseline (old task set) estimated M0 = 0 / 6 = **0.0**

## Interpretation

Iteration 1 measured *task operationalization quality* rather than *task protocol impact*.
Iteration 2 establishes testability with explicit locator evidence.
Primary hypothesis execution is pending Iteration 3.
