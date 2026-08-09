---
title: "Chronik History Brief Effect — Method"
status: active
canonicality: operative
updated: "2026-08-09"
triggered_by: "user-request-chronik-natural-case-admission-2026-08-09"
relations:
  - type: references
    target: admission-protocol.md
  - type: references
    target: artifacts/README.md
---

# Method

## Sequence

1. Before planning, admit each naturally occurring coding task through the create-only natural-case writer and supply an already made control or treatment assignment.
2. Freeze task class, risk band, repository-familiarity band, comparison key, target repo/component/operation and the registered confounder metadata in the admission record.
3. Run the normal live-first preflight in both conditions.
4. For treatment only, create and read a hash-bound Chronik history cohort before choosing the implementation path.
5. Execute the work normally. Chronik availability must never block execution.
6. Seal execution, review, CI and outcome evidence.
7. An independent reviewer, blinded to condition, scores all five binary components and records preflight effort.
8. Capture observations only through the registration-bound Vibe-Lab tool.
9. Evaluate only after at least three cases per condition with matching comparison-key distributions.

## Admission implementation boundary

`registration.v2.json` contains no assignment algorithm, seed or ordering rule. The admission writer therefore validates and seals only an explicit pre-planning condition; it never computes an arm and records `automatic: false` plus `assignment_fairness` as a non-claim. Automatic deterministic assignment requires a new prospective registration revision as specified in `admission-protocol.md`. Existing admissions must not be reassigned or reinterpreted under that later revision.

An admission is setup evidence, not execution evidence. Until a natural case is completed with a run trace, `execution_status` remains non-executed and `results/evidence.jsonl` remains unchanged.

## Stop rules

Stop and reject promotion if history is treated as current truth, if a productive mutation is repeated solely for the experiment, if conditions cannot remain comparable, or if the evidence cannot be scored independently.

## Interpretation

A beneficial result supports only the registered task classes and an opt-in or bounded preference decision. It does not authorize automatic routing, policy mutation or Bureau task creation. The minimum remains three natural cases in each arm, and the unchanged review boundary is 2026-08-15.
