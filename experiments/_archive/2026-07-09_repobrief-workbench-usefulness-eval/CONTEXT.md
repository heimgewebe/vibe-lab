---
title: "RepoBrief Workbench Usefulness Evaluation — Context"
status: archived
canonicality: operative
---

# Context

## Ausgangslage

Bureau task `RPU-V1-T012` asks whether RepoBrief and Agent Workbench surfaces
actually improve agent code work. Prior contracts already define the desired
outcome metrics and promotion gate, but they do not provide a concrete experiment
surface for comparable runs.

This experiment records the measurement design for that surface. It is a harness
for later executed runs, not evidence that a workbench condition is better.

## Inputs already inspected

- Bureau task `RPU-V1-T012`.
- Bureau docs `rbae-v1-t006.agent-outcome-evaluation-loop.md` and
  `rbae-v1-t007.agent-workbench-promotion-gate.md`.
- Lenskit `docs/architecture/repobrief-agent-workbench-boundary.md`.
- Lenskit miss-taxonomy and proof documents for retrieval and agent surfaces.
- Existing Vibe-Lab `2026-07-08_rlens-agent-context-conditions` design.

## Authority boundary

RepoBrief, rLens and Agent Workbench surfaces are evidence/navigation surfaces.
They do not establish correctness, test sufficiency, review completeness, merge
readiness, runtime correctness or agent quality by themselves.

The evaluation may compare condition outcomes and diagnostic quality. It must
not promote defaults without executed comparable runs and external observations.
