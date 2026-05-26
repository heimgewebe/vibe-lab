---
title: "Outcome-Evidence-Replication-Series — Method"
status: designed
canonicality: operative
---

# Outcome-Evidence-Replication-Series — Method

## Hypothesis

A usable outcome conclusion requires task diversity, auditor independence, a stable negative control, and run-over-run evidence.

## Method

### Procedure

1. Execute `run-001-contract-documentation-alignment` as the first real series run.
2. Record the run with the required artifact bundle (`run.yml`, `measurement.yml`, `auditor-output.yml`, `evidence-pack.yml`, `comparability.yml`, `changed-files.txt`, `timing.txt`, `make-validate.txt`).
3. Classify the run as `task_class: contract_documentation_alignment` within the same outcome-evidence gate family.
4. Mark independence as `partial` unless a Human Reviewer or another AI system / model family is involved.
5. Keep `outcome_upgrade_allowed: false` and do not claim promotion, adoption, or outcome upgrade from this run.
6. Preserve a negative control with expected `CLAIM_NOT_PROVEN` in later runs.

### Metrics

- comparability across runs
- task-class diversity
- independence level of review
- stability of the negative control
- evidence completeness across the required artifact bundle

### Success Criteria

The hypothesis is supported only if the full gate criteria are met across multiple runs. A single run may improve alignment evidence but does not justify outcome upgrade.

## Variables

| Variable | Description | Control / Treatment |
| --- | --- | --- |
| task_class | Declared task class for each run | Must vary across the series |
| independence_level | Partial vs full independence | Must include at least one full independence case |
| negative_control | Expected `CLAIM_NOT_PROVEN` case | Must remain stable |

## Risks and Constraints

- A single run can look convincing while still being only local evidence.
- Same-family different-session review is not full independence.
- Without a stable negative control, the series can overstate its claim.
- Contract-/documentation-alignment evidence is necessary but not sufficient for RM-002/RM-005/EP-002 closure.
