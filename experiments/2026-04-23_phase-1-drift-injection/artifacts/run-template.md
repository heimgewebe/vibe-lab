---
title: "Run Template: Phase 1 Drift Injection"
status: draft
canonicality: operative
created: "2026-04-24"
updated: "2026-04-24"
author: "GPT-5.4"
relations:
  - type: references
    target: README.md
  - type: references
    target: ../results/README.md
---

# Diagnose-First Run-Template

Dieses Template dient für den ersten realen Phase-1-Execution-PR-Run.

## Reihenfolge

1. Baseline-Guard:

```bash
make validate
```

2. Fixture-Inventar sichern:

```bash
find tests/fixtures/agent_handoff -type f -name '*.json' | sort
```

3. Beide Outputs in
  `experiments/2026-04-23_phase-1-drift-injection/artifacts/<run-id>/execution.txt`
  festhalten.
4. Erst danach Stage-Fixtures unter
  `experiments/2026-04-23_phase-1-drift-injection/artifacts/staging/phase-1-agent-handoff/`
  anlegen.
5. Validator gegen das Stage-Verzeichnis laufen lassen.
6. Pro Fall (`A1`, `A2`, `B1`, `B2`, `C1`, `D1`) einen Evidence-Eintrag schreiben.

## Run-Protokoll

- run_id:
- baseline_ref:
- fixture_inventory_snapshot:
- staged_fixture_dir:
- validator_command:
- evidence_cases_recorded:
- notes:
