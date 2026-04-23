---
title: "Initiale Situation: Agent Failure Surface Mapping"
status: draft
canonicality: operative
created: "2026-04-23"
updated: "2026-04-23"
author: "Claude Opus 4.7"
---

# INITIAL.md — Initiale Situation

## Baseline-Zustand des Agent-Operability-Layers (2026-04-23)

Quelle: Fixture-Matrix (`docs/reference/agent-operability-fixture-matrix.md`),
letzter grüner `make validate`-Lauf auf `main` @ `852461d`.

### Vorhandene Fixture-Klassen

| Bereich                   | Pfad                                                | Anzahl Fixtures |
| ------------------------- | --------------------------------------------------- | --------------- |
| Command `read_context`    | `tests/fixtures/agent_commands/read_context/`       | 7               |
| Command `write_change`    | `tests/fixtures/agent_commands/write_change/`       | 9               |
| Command `validate_change` | `tests/fixtures/agent_commands/validate_change/`    | 8               |
| Handoff                   | `tests/fixtures/agent_handoff/`                     | 4               |
| Chain                     | `tests/fixtures/command_chains/`                    | 15              |
| Cross-Contract            | `tests/fixtures/cross_contract/{valid,invalid}/`    | 9               |
| Phase-1c Structure        | `tests/fixtures/experiment_structure_phase1c/`      | 3 Klassen       |

Tatsächliche Zählung ist per `find tests/fixtures -type f -name '*.json' | wc -l` zu Beginn
jeder Phase zu reproduzieren und in `evidence.jsonl` festzuhalten.

### Bereits dokumentierte Gaps (Fixture-Matrix, Stand 2026-04-23)

Aus `docs/reference/agent-operability-fixture-matrix.md` übernommen, nicht
reinterpretiert:

- `validate_change`: Version-const-Verletzung ist dokumentiert als
  `covered: false; gap: missing`.
- Weitere Gaps: siehe Matrix, Abschnitt „Known Gaps".

Die Phasen dieser Reihe dürfen diese Liste **ergänzen**, aber nicht
**verkürzen** ohne Evidenzgrundlage.

## Erwartete Baseline (ohne Treatment)

- `make validate` ist grün.
- Handoff-, Command-, Chain- und Cross-Contract-Validatoren akzeptieren alle
  vorhandenen `valid-*.json` und lehnen alle vorhandenen `contract-invalid-*.json`
  mit der dokumentierten Fehlerklasse ab.
- Drift-, Widerspruchs-, Chain- und Replay-Klassen, die unten pro Phase
  injiziert werden, sind in der jetzigen Konfiguration **entweder nicht
  abgedeckt oder noch nicht empirisch getestet**.

## Systemkonfiguration

- Repo-Stand: `main` @ `852461d` (post PR #92 Merge).
- Python-Venv: `.venv/`, Pflichtpfad für alle Scripts.
- CI: `.github/workflows/validate.yml` (nicht Teil dieses PRs).
- Keine Modifikation bestehender Schemas oder Validatoren ohne explizites
  Patch-Gate (siehe `method.md` §Patch-Gate).

## Stopbedingungen (Initial)

Dieser PR ist der **Design-PR**. Er enthält:

- Manifest mit `status: designed`, `execution_status: designed`
- Vollständige Methodenbeschreibung aller fünf Phasen
- Keine `evidence.jsonl`, keine Runs, keine neuen Fixtures

Phase-Ausführungen erfolgen in nachgelagerten PRs, jeweils mit eigenem
`run_meta.json` und Evidenz-Anhängen. Das Manifest wird bei jeder Phase
aktualisiert (`execution_status`, `execution_refs`, `iteration`).
