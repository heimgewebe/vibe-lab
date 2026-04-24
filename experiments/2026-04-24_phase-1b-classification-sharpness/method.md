---
title: "Methode: Phase 1b Classification Sharpness"
status: draft
canonicality: operative
created: "2026-04-24"
updated: "2026-04-24"
author: "GPT-5.3-Codex"
relations:
  - type: references
    target: INITIAL.md
  - type: references
    target: failure_modes.md
  - type: references
    target: ../../tests/fixtures/cross_contract/invalid/handoff_locator_drift/locator_drift.json
---

# method.md - Methode

## Hypothese

Rejection correctness und classification sharpness sind unterschiedliche
Qualitaetsachsen.

- Rejection correctness: Ein invalider Fall wird abgelehnt.
- Classification sharpness: Die Ablehnung wird in der semantisch passenden
  Fehlerklasse sichtbar gemacht.

## Diagnostischer Vergleich (Design)

Dieses Experiment vergleicht bewusst nur Validator-Layer und ihre Grenzen:

1. agent_handoff hash/schema detection
2. cross_contract semantic drift detection
3. dokumentierte Boundary zwischen beiden

## Geplanter Future-Execution-Run (noch nicht ausgefuehrt)

Die kuenftige Ausfuehrung soll in dieser Reihenfolge erfolgen:

1. make validate
2. python3 -m unittest tests/contracts/test_cross_contract_chain.py
3. python3 scripts/docmeta/validate_agent_handoff.py --fixtures tests/fixtures/agent_handoff

## Erwartete Auswertungsfrage

Wenn agent_handoff korrekt ablehnt, aber Locator-/Target-Drift nicht als eigene
Fehlerklasse sichtbar macht, bleibt die Klassifikationsschaerfe fuer diesen
Layer gemischt, auch bei insgesamt korrektem Rejection-Verhalten.

## Scope-Grenzen

- Keine Aenderung an Validatoren
- Keine Aenderung an Schemas
- Keine neuen CI-Guards
- Kein Start von Phase 2
- Kein Execution-Claim in diesem Design-PR
