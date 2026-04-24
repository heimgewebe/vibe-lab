---
title: "Results: Phase 1 Drift Injection"
status: draft
canonicality: operative
created: "2026-04-23"
updated: "2026-04-24"
author: "GPT-5.3-Codex"
relations:
  - type: references
    target: ../../../schemas/decision.schema.json
  - type: references
    target: ../../../schemas/agent.handoff.schema.json
---

# Phase 1 Results

> Status: **EXECUTED**
> Run: run-2026-04-24-phase1-001
> Evidence: results/evidence.jsonl
> Decision: results/decision.yml
> Result: results/result.md

---

## Artifacts

- [run_meta.json](../artifacts/run-2026-04-24-phase1-001/run_meta.json) — Run metadata
- [execution.txt](../artifacts/run-2026-04-24-phase1-001/execution.txt) — Execution transcript
- [evidence.jsonl](evidence.jsonl) — Per-case evidence entries
- [decision.yml](decision.yml) — Phase 1 verdict
- [result.md](result.md) — Narrative summary

---

## Execution Summary

- Executor: local:developer
- Run completed: 2026-04-24
- Strict validator exit code: 1 (expected — all 6 fixtures contain intentional drift)
- Final `make validate` exit code: 0 (hygiene guard passed)

---

## Constraints (Reference)

- **Scope:** agent_handoff validator only
- **Test count:** exactly 6 cases (no additions mid-Phase)
- **Stop condition:** all 6 executed AND evidence complete ✅
- **CI requirement:** make validate must pass throughout ✅
