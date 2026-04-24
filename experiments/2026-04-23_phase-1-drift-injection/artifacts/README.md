---
title: "Artifacts: Phase 1 Drift Injection"
status: draft
canonicality: operative
created: "2026-04-24"
updated: "2026-04-24"
author: "GPT-5.4"
relations:
  - type: references
    target: ../../../schemas/run_meta.schema.json
  - type: references
    target: ../method.md
  - type: references
    target: ../results/README.md
---

# artifacts/

Dieses Verzeichnis bleibt leer, bis der Execution-PR reale Laufspuren erzeugt.

## Diagnose-First Reihenfolge

Vor jeder Fixture-Materialisierung zuerst:

```bash
make validate
find tests/fixtures/agent_handoff -type f -name '*.json' | sort
```

Diese Baseline-Ausgaben gehören in `artifacts/<run-id>/execution.txt`, bevor
mutierte Stage-Fixtures angelegt werden.

## Danach Erst

1. Stage-Fixtures in `artifacts/staging/phase-1-agent-handoff/` materialisieren.
2. Stage-Verzeichnis explizit prüfen:

```bash
python3 scripts/docmeta/validate_agent_handoff.py \
  --fixtures artifacts/staging/phase-1-agent-handoff \
  --mode strict
```

3. Für jeden Fall einen Eintrag in `results/evidence.jsonl` ergänzen.

## Reale Run-Artefakte

Bei echter Ausführung entstehen pro Run:

- `artifacts/<run-id>/run_meta.json`
- `artifacts/<run-id>/execution.txt`

`run_meta.json` wird gegen `schemas/run_meta.schema.json` validiert.