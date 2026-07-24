---
title: "Archive Decision: RepoBrief Workbench Usefulness Evaluation"
status: archived
canonicality: operative
---

# Archive decision

## Finding

The experiment remains historically valid as a limited, reconstructed RepoBrief/rLens diagnostic pilot. Its recorded decision is still `insufficient_proof`: the three audited single-run slices did not contain uncontaminated paired counterfactuals and therefore did not establish condition superiority or default-promotion readiness.

## Why it leaves the active registry

The active registry names `Bureau RPU-V1` as the consumer. The canonical Bureau initiative `REPOBRIEF-PRACTICAL-UTILITY-V1` is completed as of 2026-07-15. An experiment without a current named consumer no longer satisfies Vibe-Lab's consumer-bound admission rule.

RepoGround is a separate current component and initiative. Rebinding this historical RepoBrief experiment to RepoGround would change the consumer and intervention after evidence collection, so this archive does not do that.

## Disposition

- Remove the RepoBrief Workbench experiment from `experiments/active.v1.json`.
- Preserve the experiment directory and all existing evidence under `experiments/_archive/`.
- Preserve the historical `results/decision.yml` unchanged.
- Retire the four RepoBrief-pilot-only validator targets from the blocking grouped validation frontdoor; keep their scripts and tests as historical audit material.
- Do not infer anything about RepoGround utility from this archive. Any RepoGround effectiveness question requires its own prospective, consumer-bound decision.

## Non-claims

This archive does not prove that RepoBrief diagnostics were ineffective, that RepoGround is better or worse, that the historical validators are incorrect, or that all rLens/PR-context legacy validation can already be removed. It closes only the stale active-consumer binding and its dedicated blocking surface.
