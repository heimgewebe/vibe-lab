---
title: "Initiale Situation: Phase 1b Classification Sharpness"
status: draft
canonicality: operative
created: "2026-04-24"
updated: "2026-04-24"
author: "GPT-5.3-Codex"
relations:
  - type: references
    target: ../2026-04-23_phase-1-drift-injection/results/result.md
  - type: references
    target: ../2026-04-23_phase-1-drift-injection/results/decision.yml
  - type: references
    target: ../../tests/fixtures/cross_contract/invalid/handoff_locator_drift/locator_drift.json
---

# INITIAL.md - Initiale Situation

## Ausgangslage aus Phase 1 Drift Injection

Der Drift-Injection-Run wurde bereits ausgeführt und zeigt folgendes Muster:

- A1, A2, B1, B2, C1: rejected via hash_mismatch
- D1: rejected via contract_invalid

Diese Ablehnungen sind als Rejection-Verhalten akzeptabel.

## Diagnosebedarf

Die Klassifikationsschärfe bleibt jedoch gemischt, weil Locator-/Target-Drift
im agent_handoff-Layer nicht als dedizierte Locator-/Target-Fehlerklasse
sichtbar wird, sondern in der Praxis über hash_mismatch signalisiert werden kann.

## Layer-Referenz für den Vergleich

Der semantische Drift-Layer wird über bestehende Cross-Contract-Fixtures
adressiert, insbesondere:

- tests/fixtures/cross_contract/invalid/handoff_locator_drift/locator_drift.json

Dieses Experiment ist ein Design-Artefakt und enthält keine Run-Behauptungen.
