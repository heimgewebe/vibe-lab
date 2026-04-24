---
title: "Failure Modes: Phase 1b Classification Sharpness"
status: draft
canonicality: operative
created: "2026-04-24"
updated: "2026-04-24"
author: "GPT-5.3-Codex"
relations:
  - type: references
    target: method.md
  - type: references
    target: ../../tests/fixtures/cross_contract/invalid/handoff_locator_drift/locator_drift.json
---

# failure_modes.md - Failure Modes

## Wann funktioniert diese Diagnose nicht?

- Wenn die Analyse Rejection correctness und classification sharpness vermischt.
- Wenn Layer-Grenzen zwischen agent_handoff und cross_contract nicht explizit
  dokumentiert werden.
- Wenn aus Designannahmen versehentlich Ausfuehrungsclaims gemacht werden.

## Bekannte Fehlannahmen (Design-Stand)

- "Rejected" bedeutet nicht automatisch "scharf klassifiziert".
- hash_mismatch im agent_handoff-Layer kann semantischen Drift verdecken,
  statt ihn explizit zu benennen.
- Ein einzelner Fixture-Hinweis reicht nicht fuer belastbare Generalisierung
  ohne spaetere Ausfuehrungsdaten.

## Grenzen der Evidenz

- Dieses Artefakt ist design-only (execution_status: designed).
- Es gibt in diesem PR keine neuen Messdaten in results/evidence.jsonl.
- Aussagen bleiben als Diagnoseplanung formuliert, nicht als Ergebnis.

## Risiko bei Fehlanwendung

Wird die Layer-Grenze nicht sauber kommuniziert, kann ein gruener Rejection-Check
faelschlich als vollstaendig scharfe Fehlerklassifikation interpretiert werden.
