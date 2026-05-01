---
title: "Agent/Skill Minimal Layer Instrumentation — Ergebnis"
status: draft
canonicality: operative
---

# result.md — Ergebnis

## Status

**Run 1 erfasst.** PR #145 als erster realer Messdatensatz dokumentiert. Kein Wirksamkeitsclaim.

## Datenlage

- 1 PR-Datensatz erhoben (Run 1: PR #145).
- Metriken teilweise gemessen; CI-Artefakte nicht im Repo vorhanden (MISSING_EVIDENCE für validation_gap_count).
- Kein Wirkungsclaim möglich oder zulässig (einzelner Messpunkt, keine Kontrollgruppe).
- Keine Aussage, dass Agent- oder Skill-Dateien nützlich sind.

## Interpretation Budget

### Allowed Claims

- Das Experiment legt einen Erhebungsrahmen für künftige PR-Daten an.
- Run 1 (PR #145) wurde erfasst: scope_drift=0, unsupported_claims=0, validation_gaps=1, review_friction=2, rework=1.
- CI-Artefakte sind für Run 1 nicht im Repo vorhanden (MISSING_EVIDENCE).

### Disallowed Claims

- Die Agent-Schicht reduziert Fehler.
- Die Agent-Schicht ist nützlich.
- Skill-Dateien sind bewertet.
- CI-/Script-Rückbindung ist gerechtfertigt.
- Aus einem einzelnen Messpunkt folgt irgendeine Wirkungsaussage.

## Evidence Basis

| Kategorie | Stand |
|---|---|
| Direkt beobachtet | Experimentgerüst angelegt; Run 1 (PR #145) erfasst |
| Teilweise beobachtet | scope_drift, unsupported_claims, missing_locators, review_friction, rework, false_blocks, completion_time (Run 1) |
| MISSING_EVIDENCE | CI-Testprotokoll, make-Ausgaben, experiment-critic-Output (Run 1) |
| Nicht getestet | Wirkung, Vergleichbarkeit |
| Nicht vorhanden | Kontrollgruppe, mindestens 3 vergleichbare PRs für Zwischenauswertung |

## Nächste Schritte

Mindestens zwei weitere reale PRs mit `experiment-critic` und `evidence-reconciliation-auditor`-Beteiligung als Datensätze erfassen. Zwischenauswertung nach drei vergleichbaren PRs.
