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

1. Keep the series in planned state until the gate playbook is satisfied.
2. Record each later run with the required artifact bundle.
3. Classify each run by task class and comparability.
4. Distinguish full independence from partial independence.
5. Preserve a negative control with expected `CLAIM_NOT_PROVEN`.

### Metrics

- comparability across runs
- task-class diversity
- independence level of review
- stability of the negative control
- evidence completeness across the required artifact bundle

### Success Criteria

The hypothesis is supported only if the full gate criteria are met across the series. Otherwise the series remains a planning scaffold.

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
