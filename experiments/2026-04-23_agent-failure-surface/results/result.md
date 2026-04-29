---
title: "Ergebnis: Agent Failure Surface Mapping (kumulativ)"
status: draft
canonicality: operative
created: "2026-04-29"
updated: "2026-04-29"
author: "Copilot Agent"
triggered_by: user-request-2026-04-29-phase-4-replay-reality-gap
relations:
  - type: references
    target: evidence.jsonl
  - type: references
    target: decision.yml
  - type: references
    target: replay-gap-candidates.md
  - type: references
    target: ../method.md
  - type: references
    target: ../failure_modes.md
---

## Agent Failure Surface Mapping - Kumulativer Serienbericht

## Zusammenfassung

Dieser Stand ergaenzt die Reihe um Phase 4 (Replay Reality Gap) als qualitative Diagnose. Es wurde kein Validator-, Schema-, Fixture- oder CI-Patch vorgenommen.

## Gesamtstatus der Phasen

| Phase | Titel | Stand | Evidenztyp | Patch-Status |
| --- | --- | --- | --- | --- |
| 1 | Drift Injection | vorliegender Reihenkontext (in diesem PR nicht neu verifiziert) | extern uebernommener Reihenstand | nicht Teil dieses PR |
| 2 | Semantic Contradiction | als geschlossen berichtet (SEM-EMPTY-ASSERTED) | extern uebernommener Reihenstand | nicht Teil dieses PR |
| 3 | Chain Integrity Stress | als ohne neue Luecke berichtet | extern uebernommener Reihenstand | nicht Teil dieses PR |
| 4 | Replay Reality Gap | qualitative Kandidateninventur abgeschlossen | qualitative_inventory | kein Patch |
| 5 | Adversarial Agent Simulation | ausstehend | offen | offen |

## Phase 4 - Replay Reality Gap

Phase 4 kartiert die Differenz zwischen Dry-Run-Replay und realer Mutationswelt. Der aktuelle Replay-Vertrag sichert deterministische, non-mutative Dry-Run-Ausgabe (`mode: dry_run`, `would_mutate: false`), bildet aber reale Disk-/Git-/Locator-Folgen nicht direkt nach.

Details und Kandidatenmatrix: `results/replay-gap-candidates.md`.

## Klare Aussage zum Scope

- Kein Patch: Es wurde bewusst keine Validator-, Schema-, Fixture- oder CI-Haertung vorgenommen.
- Kein Sicherheitsbeweis: Phase 4 beweist keine Replay-Sicherheit.
- Ergebnischarakter: qualitative Kartierung der blinden Stellen.

## Naechste Schritte

- Phase 5 als separater Ausfuehrungsschritt.
- Optional danach Phase F mit realer Mutationsausfuehrung fuer priorisierte Replay-Gap-Kandidaten.
