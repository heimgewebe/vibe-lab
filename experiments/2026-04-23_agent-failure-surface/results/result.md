---
title: "Result: Agent Failure Surface Mapping - Serienbericht (Phase 2 + 3 + 4)"
status: draft
canonicality: operative
created: "2026-04-29"
updated: "2026-04-29"
author: "Copilot Agent (GPT-5.3-Codex)"
relations:
  - type: references
    target: ../method.md
  - type: references
    target: ../../../contracts/command-semantics.md
  - type: references
    target: ../../../docs/reference/agent-operability-fixture-matrix.md
  - type: references
    target: decision.yml
  - type: references
    target: replay-gap-candidates.md
---

## result.md - Serienbericht (Phase 2 + 3 + 4)

## Zusammenfassung

Dieser Bericht ist der kumulative Ergebnisstand der Reihe
Agent Failure Surface Mapping fuer die bisher abgeschlossenen Phasen.

Phase 2 und Phase 3 bleiben unveraendert erhalten; Phase 4 wird als
qualitative Replay-Gap-Kandidateninventur ergaenzt (no_patch).

## Gesamtstatus der Phasen

| Phase | Titel | Stand | Evidenztyp | Patch-Status |
| --- | --- | --- | --- | --- |
| 1 | Drift Injection | in eigenem PR dokumentiert | bestehender Reihenstand | nicht Teil dieser Aenderung |
| 2 | Semantic Contradiction | confirms (SEM-EMPTY-ASSERTED) | ausgefuehrte Phase mit Signalwechsel | Strukturkonsequenz belegt |
| 3 | Chain Integrity Stress | refutes (im geprueften Kandidatenraum) | ausgefuehrte Phase mit 0/7 toleriert | no_patch |
| 4 | Replay Reality Gap | qualitative Kandidateninventur | qualitative_inventory | no_patch |
| 5 | Adversarial Agent Simulation | ausstehend | offen | offen |

## Phase 2 - Semantic Contradiction (confirms)

Belegte Kernaussage: Die Subklasse SEM-EMPTY-ASSERTED (empty asserted state)
wurde als reale semantic_contradiction-Luecke reproduzierbar gefunden und
geschlossen.

- Vor Patch wurde der relevante Kandidatenraum toleriert.
- Nach Patch wurde die Klasse mit semantic_contradiction abgewiesen.
- Positiv-Kontrast blieb gueltig.
- Strukturkonsequenz (Validator + Fixtures + Tests) wurde verankert.

Die Phase-2-Aussage bleibt in diesem kumulativen Bericht unveraendert erhalten.

## Phase 3 - Chain Integrity Stress (refutes phase-3 hypothesis)

Belegte Kernaussage: Im geprueften Kandidatenraum wurden keine neuen
Chain-Integrity-Luecken gefunden.

- 7/7 Kandidaten loesten dokumentierte Fehlercodes aus.
- Toleranz-Rate im geprueften Raum: 0/7.
- Folgeentscheidung: no_patch nach Patch-Gate (kein tolerated_but_wrong).

Die Phase-3-Aussage bleibt unveraendert erhalten.

## Phase 4 - Replay Reality Gap

Phase 4 kartiert die Differenz zwischen Dry-Run-Replay und realer
Mutationswelt. Der aktuelle Replay-Vertrag sichert deterministische,
non-mutative Dry-Run-Ausgabe (`mode: dry_run`, `would_mutate: false`), bildet
aber reale Disk-/Git-/Locator-Folgen nicht direkt nach.

Outcome:

- qualitative_inventory
- no_patch
- kein Sicherheitsbeweis fuer Replay
- Verweis: `results/replay-gap-candidates.md`

## Klare Aussage zum Scope

- Phase 4 ergaenzt Phase 2/3 und ersetzt sie nicht.
- Kein Patch in Phase 4: keine neuen Validatoren, Schemas oder Fixtures.
- Kein Sicherheitsbeweis: Die Inventur bleibt qualitativ.

## Naechste Schritte

- Phase 5 als separater Ausfuehrungsschritt.
- Phase F optional mit realer Mutationsausfuehrung planen.
- Priorisierung fuer Phase F: RRG-03, danach RRG-01 und RRG-02.
