---
title: "Kontext: Agent Failure Surface Mapping"
status: draft
canonicality: operative
created: "2026-04-23"
updated: "2026-04-23"
author: "Claude Opus 4.7"
relations:
  - type: references
    target: ../../contracts/command-semantics.md
  - type: references
    target: ../../docs/reference/agent-operability-fixture-matrix.md
  - type: references
    target: ../../docs/blueprints/blueprint-agent-operability-phase-1c.md
  - type: informed_by
    target: ../2026-04-15_agent-task-validity/CONTEXT.md
---

# CONTEXT.md — Agent Failure Surface Mapping

## Ausgangslage

Phasen A–D und Phase 1c des Agent-Operability-Blueprints sind wirksam:

- Command-Semantik (`contracts/command-semantics.md`)
- Schemas für `read_context`, `write_change`, `validate_change`, Handoff, Chain
- Fixture-Korpus in `tests/fixtures/{agent_commands,agent_handoff,command_chains,cross_contract,experiment_structure_phase1c}/`
- Dry-run Replay (Phase F-light)
- `make validate` als zentrale Prüfebene
- Fixture-Matrix mit Gap-Audit (`docs/reference/agent-operability-fixture-matrix.md`)

Phase E (adversariale Härtung) ist **nicht abgeschlossen**. Die Fixture-Matrix
listet offene Äquivalenzklassen (z.B. `version-const`-Verletzung für
`validate_change`), aber nicht alle gefährlichen Drift- und Widerspruchsklassen
sind kartiert.

## Problemrahmen (alternative Sinnachse)

Diese Reihe fragt nicht:

> „Wie gut funktioniert der Agent?"

sondern:

> **„Wo ist die Grenze zwischen korrekt und falsch unscharf — und wie
> reproduzierbar lässt sich das ausnutzen?"**

Das verschiebt den Erkenntnismodus: Nicht Funktionsnachweis, sondern
Grenzflächen-Kartierung.

## Hybrid-Modus (operative Kopplung)

Die Reihe ist **kein Beobachtungsprojekt**. Jede identifizierte Toleranzzone
muss im selben oder einem direkt nachfolgenden PR in eine harte
Strukturkonsequenz überführt werden:

- **Fixture** (neuer Testfall unter `tests/fixtures/…`)
- **Test** (erweiterter Validator-Test mit Erwartungswerten)
- **Validator-Änderung** (wenn eine Fehlklasse bisher nicht erkennbar war)

Erkenntnisse ohne strukturelle Folge werden im Manifest als `inconclusive`
markiert oder — bei bewusster Nicht-Operationalisierung — in
`failure_modes.md` begründet abgelegt.

## Umgebung

- **Tools:** `make validate`, JSON Schema (Draft 2020-12), Python 3.11,
  bestehende Validator-Suite (`scripts/…`), LLM-Agent
- **Sprache:** Markdown, YAML, JSON, Python
- **Projekttyp:** Policy-gesteuertes Repo mit CI-Validierung
- **Modell(e):** Claude Opus 4.7 (Design); konkrete Ausführungsmodelle werden
  je Run in `run_meta.json` festgehalten

## Einschränkungen

- **Modell-Varianz:** Drift-Toleranz und Widerspruchserkennung können
  modellabhängig sein. Jeder Run muss Modell + Temperatur dokumentieren.
- **Fixture-Overfitting:** Risiko, dass neue Fixtures nur die geprüften
  Spezialfälle abdecken. Gegenmittel: Äquivalenzklassen explizit benennen, nicht
  Einzelfälle.
- **Analyse-Schleife:** Reihe kann zur epistemischen Prokrastination werden.
  Gegenmittel: harte Stop-Regel je Phase (`method.md`), PR pro Phase.
- **Replay-Phase (4) ist qualitativ:** Unterschiede zwischen Dry-Run und
  hypothetischer Realausführung sind ohne echten Runner nur argumentativ
  greifbar. Ergebnis ist eine Kandidatenliste für Phase F, keine quantitative
  Aussage.

## Traceability

- **triggered_by:** user-request-2026-04-23-phase-e-experiment-series-hybrid
- **policy:** `repo.meta.yaml`, `AGENTS.md`, `agent-policy.yaml`
- **action:** Experimentreihe als einzelnes Experiment mit fünf benannten
  Phasen angelegt; jede Phase hat einen eigenen Subschritt in `method.md`.
- **outcome:** offen — Phase 1 noch nicht ausgeführt. Manifest steht auf
  `status: designed` und `execution_status: designed`.
