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
Qualitätsachsen.

- Rejection correctness: Ein invalider Fall wird abgelehnt.
- Classification sharpness: Die Ablehnung wird in der semantisch passenden
  Fehlerklasse sichtbar gemacht.

## Diagnostischer Vergleich (Design)

Dieses Experiment vergleicht bewusst nur Validator-Layer und ihre Grenzen:

1. agent_handoff hash/schema detection
2. cross_contract semantic drift detection
3. dokumentierte Boundary zwischen beiden

Die Layer sind komplementär, nicht ersetzend: cross_contract kompensiert keine
fehlende Benennung im agent_handoff-Layer, sondern bildet eine eigene
epistemische Ebene ab.

## Klassifikations-Mapping (Design-Level)

Diese Zuordnung definiert den Sollzustand ohne Ausführung und ohne
Implementierungsänderung.

Hinweis: Die erwarteten Cross-Contract-Klassen sind Soll-/Diagnosebegriffe auf
Design-Level, keine Behauptung über aktuelle Validator-Labels.

| Drift-Typ | Erwartete agent_handoff Klasse | Erwartete cross_contract Klasse |
| --- | --- | --- |
| locator_drift | locator_error (derzeit nicht explizit vorhanden) | locator_drift_detected |
| target_drift | target_error (derzeit nicht explizit vorhanden) | target_drift_detected |
| structural mismatch | contract_invalid | contract_invalid |
| content mutation | hash_mismatch | optional semantic mismatch |

## Diagnoseziel (ohne Ausführung)

Classification sharpness ist gegeben, wenn:

- Drift-Typ zu Fehlerklasse je Layer deterministisch abbildbar ist.
- keine Information ausschließlich implizit über Hash-Signale transportiert wird.
- die Ebenen ihre eigene Drift explizit benennen, statt Verantwortung zu verschieben.

Eine Klassifikation gilt als zu grob, wenn für denselben Drift-Typ mehrere
inhaltlich verschiedene Fehlerursachen nur als hash_mismatch erscheinen und die
ursächliche Driftinformation erst außerhalb des Layers rekonstruiert werden muss.

## Alternative Diagnoseachse

Neben Klassifikation wird Informationsverlust zwischen Layern als zweite,
rein definitorische Achse dokumentiert:

- agent_handoff hash_mismatch kann Information komprimieren.
- cross_contract kann semantische Drift rekonstruieren.
- diagnostisch scharf ist das System erst, wenn diese Kompression je Drift-Typ
  bewusst begrenzt und transparent ist.

## Geplanter Future-Execution-Run (noch nicht ausgeführt)

Die künftige Ausführung soll in dieser Reihenfolge erfolgen:

1. make validate
2. python3 -m unittest tests/contracts/test_cross_contract_chain.py
3. python3 scripts/docmeta/validate_agent_handoff.py --fixtures tests/fixtures/agent_handoff

## Erwartete Auswertungsfrage

Wenn agent_handoff korrekt ablehnt, aber Locator-/Target-Drift nicht als eigene
Fehlerklasse sichtbar macht, bleibt die Klassifikationsschärfe für diesen
Layer gemischt, auch bei insgesamt korrektem Rejection-Verhalten.

## Scope-Grenzen

- Keine Änderung an Validatoren
- Keine Änderung an Schemas
- Keine neuen CI-Guards
- Kein Start von Phase 2
- Kein Execution-Claim in diesem Design-PR
