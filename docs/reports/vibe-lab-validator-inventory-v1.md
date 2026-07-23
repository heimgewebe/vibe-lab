---
title: "Vibe-Lab Validator Inventory v1"
status: active
canonicality: operative
created: "2026-07-12"
updated: "2026-07-23"
triggered_by: "vibe-lab-optimization-plan-v1-phase-c"
relations:
  - type: informs
    target: ../plans/vibe-lab-optimization-plan-v1.md
---

# Vibe-Lab Validator Inventory v1

## Current result

The current machine-readable source is `.vibe/validator-inventory.v1.json`. After the operator-intervention effect-evaluator experiment was archived, the effect-evaluator test target moved from the active group into the generic core group.

| Group | Targets | Current consumer |
| --- | ---: | --- |
| Core | 45 | Repository contracts, generic evidence integrity and every experiment |
| Active | 11 | Active registry, frozen Operator-Lab closeout, RepoBrief pilot and routing-readiness audit |
| Legacy | 48 | Grandfathered historical experiments, retired agent-operability corpus and closed specialist families |
| Supplemental | 2 | Replay non-mutation and committed generated artifacts |

The grouped inventory therefore contains 104 classified `validate-*` targets plus two supplemental checks. GitHub exposes a compact grouped frontdoor while all groups remain blocking on pull requests and `main`.

The active registry currently contains the RepoBrief diagnostic pilot, the designed Chronik history-brief comparison and the operator-routing ML-readiness shadow experiment. Chronik uses the existing generic registration, active-registry and evaluator contracts. The routing-readiness experiment adds one focused regression target for its aggregate-only audit because the audit has executable parsing, privacy and cross-source coverage semantics that generic registration validation does not exercise.

## Correction of the previous report

The earlier report stated 44 core and 11 active targets and still named the effect-evaluator pilot as active. That became stale when PR #314 archived the registered experiment and reassigned `validate-effect-evaluator-tests` to core. PR #316 then added the prospectively registered Chronik comparison without changing the grouped target counts.

## Safety boundary

Classification is not a usefulness claim. In particular:

- 48 legacy targets are not presumed useful forever;
- historical evidence retention does not require every historical specialist validator to remain permanently blocking;
- a green validator proves its encoded contract, not practical workflow benefit;
- full CI does not give Vibe-Lab runtime, routing, queue, merge, deployment or policy authority.

Every new `validate-*` target must be classified. The inventory validator fails when:

- a target is unclassified or listed twice;
- Makefile group dependencies drift from the inventory;
- the active specialist budget exceeds 12 targets;
- GitHub bypasses the grouped frontdoor with direct validator commands;
- a referenced scope or target disappears.

The existing active-experiment validator additionally requires a canonical `results/decision.yml` source. For registered entries it enforces exact consumer, decision question, primary metric, review date and expiry coherence; missing registration is permitted only before the registration enforcement date.

## Survivor disposition

### Keep as active core

- schemas and schema counterevidence;
- execution-proof and run-bundle integrity;
- relation, claim/evidence and promotion-readiness boundaries;
- active-registry and prospective-registration integrity;
- evidence-bound observation capture and generic effect-evaluator regression tests;
- generated-artifact non-mutation and drift protection.

These surfaces have a current consumer or protect a generic failure class used by every experiment.

### Keep temporarily as active specialist surface

- active experiment registry checks;
- frozen Operator-Lab closeout checks;
- RepoBrief Workbench usefulness and run-series checks;
- prospective experiment registration checks;
- operator-routing ML-readiness aggregate-audit regression checks.

The specialist group is 11 of the permitted maximum 12 targets. No new specialist target is justified merely by a new idea; it needs an active consumer and named failure class. The Chronik comparison stays inside the generic contracts. The routing-readiness audit consumes one specialist slot because it protects executable parsing, privacy redaction and canonical-route coverage logic for an active experiment.

### Review for retirement

The 48 legacy targets are reviewed in this order:

1. retired agent-handoff, agent-command and command-chain contracts;
2. closed Model-Lab control, access, runtime, workspace and condition-design contracts;
3. historical replay, fixture and cross-contract semantics that may duplicate generic core gates;
4. rLens and PR-context historical validators after the active RepoBrief pilot closes.

A legacy target may move to removal only when one of these material proofs exists:

1. its protected experiment family is closed and archived and no active contract imports it; or
2. a core validator demonstrably covers the same failure class and relevant fixtures.

A head- and diff-bound review is still mandatory for the removal PR, but it verifies one of those proofs and is not an independent substitute for archive or equivalent core coverage.

## Quantitative reduction gate

The legacy review date remains 2026-09-01. By that date each of the 48 targets must be classified as:

- `retain_with_consumer`;
- `covered_by_core`;
- `retire`.

The directional objective is a 30–50 percent reduction of the blocking legacy group. It is a review target, not permission for blind deletion.

## Practical effect

- Current active specialist surface: 10 targets instead of an undifferentiated 103-target frontdoor.
- Current active experiments: two — one diagnostic pilot and one designed comparison.
- Full regression breadth: retained while survivor proof is gathered.
- Retired custom-agent and instruction-bearing projection content: no longer active authority; generated compatibility markers and parity contracts remain active.
- Next engineering work: remove proven-redundant legacy groups rather than add new Vibe-Lab capabilities.
