---
title: "Initial: Phase 1 Drift Injection"
status: draft
canonicality: operative
created: "2026-04-23"
updated: "2026-04-24"
author: "GPT-5.3-Codex"
relations:
  - type: references
    target: ../../schemas/agent.handoff.schema.json
---

# Phase 1 Initial State (Design Baseline)

## Zweck

Dieses Dokument definiert den **zu reproduzierenden Baseline-Check** für Phase 1.
Es ist kein Ausführungsprotokoll.

## Baseline-Quellen

- Fixture-Bereich: `tests/fixtures/agent_handoff/`
- Validator-Kontext: `schemas/agent.handoff.schema.json`
- Reproduzierbarer Gesamtcheck: `make validate`

## Zu erhebender Baseline-Check (im Execution-PR)

1. Fixture-Inventar für `agent_handoff` erfassen:

```bash
find tests/fixtures/agent_handoff -type f -name '*.json' | wc -l
```

2. Reproduzierbaren Validator-Check laufen lassen:

```bash
make validate
```

3. Ergebnisse im Execution-PR in `results/evidence.jsonl` überführen:
- akzeptiert/abgelehnt je Testfall,
- relevante Validator-Ausgabe,
- keine Interpretation ohne Output.

## Letzter bekannter Repo-Befund (orientierend)

Die bestehende Suite enthält bereits grüne `agent_handoff`-Checks.
Dieser Hinweis ist nur Orientierung und ersetzt **nicht** den erneuten
Baseline-Check im Execution-PR.

## Geplanter Testaufbau für Phase 1

- Die kanonische Fallliste liegt in `method.md` und `fixtures/README.md`.
- Mutationen mit Einzelfeld-Änderung
- Kontrastpaar-Regel pro Äquivalenzklasse

## Vorbedingungen für Ausführung

- Design-Stand gemergt
- Baseline-Check im aktuellen Branch reproduziert
- Fixtures und Ergebnisse werden erst im Execution-PR angelegt

## Notiz zur Wahrheitsdisziplin

`designed` bleibt `designed`, bis Laufspuren (`evidence.jsonl`, Ergebnisdokumente)
im Experimentkontext vorliegen.
