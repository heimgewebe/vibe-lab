---
title: "Failure Modes — RepoBrief Workbench Usefulness Evaluation"
status: designed
canonicality: operative
---

# Failure Modes

| Failure mode | Effect | Mitigation |
| --- | --- | --- |
| Task difficulty dominates condition | Condition comparison becomes non-attributable | Pair task kind, diff size, expected contracts and difficulty before comparing. |
| Full context increases confidence without grounding | Agent output sounds better while using stale or uncited evidence | Track unsupported claims, citation coverage and stale evidence use. |
| Self-authored tests become false proof | Agent treats its own tests or local green checks as correctness proof | Record `self_authored_check_only` and `self_proof_violation`. |
| Missing live state hidden by snapshot | PR/CI/runtime facts are inferred from stale RepoBrief evidence | Require live Git/GitHub/CI observations for those claims. |
| Trace-gated condition adds too much ceremony | Auditability improves but total effort worsens | Track preparation, execution, review and correction effort separately. |
| Reviewer learning confounds order | Later runs improve because operator learned the task domain | Rotate conditions and record repeated-domain exposure. |
| Mixed-condition contamination | A run uses evidence forbidden by its condition | Mark the run contaminated and exclude it from promotion evidence. |

## Evidence boundary

This experiment can measure observations once runs exist. The design itself does
not establish condition superiority, agent quality improvement, repo
understanding, patch correctness, test sufficiency or merge readiness.
