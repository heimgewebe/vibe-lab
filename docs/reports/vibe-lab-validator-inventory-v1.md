---
title: "Vibe-Lab Validator Inventory v1"
status: active
canonicality: operative
created: "2026-07-12"
updated: "2026-07-12"
triggered_by: "vibe-lab-optimization-plan-v1-phase-c"
relations:
  - type: informs
    target: ../plans/vibe-lab-optimization-plan-v1.md
---

# Vibe-Lab Validator Inventory v1

## Result

The validation surface is classified without deleting historical evidence:

| Group | Targets | Consumer |
| --- | ---: | --- |
| Core | 44 | Repository contracts and all experiments |
| Active | 11 | Active registry, effect-evaluator pilot, RepoBrief pilot and frozen Operator-Lab closeout |
| Legacy | 48 | Grandfathered historical experiments and agent-operability corpus |
| Supplemental | 2 | Replay non-mutation and committed generated artifacts |

The previous GitHub `validate` job exposed 85 named steps. The grouped job exposes six validation and generation steps—nine named steps including checkout, Python setup and dependency installation—while executing all 103 grouped Make targets, plus both supplemental checks.

## Safety boundary

This slice does not claim that 48 legacy validators are useful forever. It preserves them as blocking evidence until their protected artifact family is archived or equivalent generic coverage is proven. The legacy group has a review date of 2026-09-01 and an explicit retirement rule.

Every new `validate-*` target must be classified. The inventory validator fails when:

- a target is unclassified or listed twice;
- Makefile group dependencies drift from the inventory;
- the active specialist budget exceeds 12 targets;
- GitHub bypasses the grouped frontdoor with direct validator commands;
- a referenced scope or target disappears.

## Practical effect

- Current operational surface: 11 active specialist targets instead of an undifferentiated 99-target frontdoor.
- Full regression coverage: retained on pull requests and `main`.
- CI presentation: substantially smaller and easier to diagnose by authority group.
- Historical deletion: none.
- Runtime, routing, queue or policy authority: none.

## Next reduction gate

A legacy target may move to removal only with one of these proofs:

1. its experiment family is closed and archived and no active contract imports it;
2. a core validator demonstrably covers the same failure class and fixtures;
3. a head- and diff-bound review confirms removal does not weaken current active or historical evidence integrity.
