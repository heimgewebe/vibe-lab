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

Dieses Verzeichnis enthält bis zum Execution-PR nur Dokumentation und Templates;
reale Laufspuren entstehen erst bei echter Ausführung.

## Diagnose-First Reihenfolge

Vor jeder Fixture-Materialisierung zuerst:

```bash
make validate
find tests/fixtures/agent_handoff -type f -name '*.json' | sort
```

Diese Baseline-Ausgaben gehören in
`experiments/2026-04-23_phase-1-drift-injection/artifacts/<run-id>/execution.txt`,
bevor
mutierte Stage-Fixtures angelegt werden.

## Danach Erst

1. Stage-Fixtures in
  `experiments/2026-04-23_phase-1-drift-injection/artifacts/staging/phase-1-agent-handoff/`
  materialisieren.
2. Stage-Verzeichnis explizit prüfen:

```bash
python3 scripts/docmeta/validate_agent_handoff.py \
  --fixtures experiments/2026-04-23_phase-1-drift-injection/artifacts/staging/phase-1-agent-handoff \
  --mode strict
```

3. Für jeden Fall einen Eintrag in `results/evidence.jsonl` ergänzen.

## Reale Run-Artefakte

Bei echter Ausführung entstehen pro Run:

- `experiments/2026-04-23_phase-1-drift-injection/artifacts/<run-id>/run_meta.json`
- `experiments/2026-04-23_phase-1-drift-injection/artifacts/<run-id>/execution.txt`

`run_meta.json` wird gegen `schemas/run_meta.schema.json` validiert.

## Bereits systemisch erzwungen

Sobald das Experiment später auf `execution_status: executed` oder
`execution_status: replicated` wechselt, erzwingt das bestehende Repo bereits:

- Existenz von `experiments/2026-04-23_phase-1-drift-injection/artifacts/<run-id>/run_meta.json`
- Schema-Validität von `run_meta.json`
- Existenz von `test_output_file` (z. B. `execution.txt`)
- CI-Ausführung über `scripts/docmeta/validate_execution_proof.py`

Diese Kopplung ist bereits in `make validate` und in `.github/workflows/validate.yml`
verdrahtet.

## Noch nicht systemisch erzwungen

Noch nicht hart gekoppelt ist die inhaltliche Konsistenz zwischen:

- `experiments/2026-04-23_phase-1-drift-injection/artifacts/<run-id>/execution.txt`
- `results/evidence.jsonl`
- `results/decision.yml`

Für Phase 1 bleibt diese Kopplung daher aktuell prozedural: dokumentiert und
reviewbar, aber nicht als eigener Cross-Artifact-Guard implementiert.
