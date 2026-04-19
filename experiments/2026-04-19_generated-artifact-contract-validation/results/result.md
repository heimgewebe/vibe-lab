---
title: "Experiment-Ergebnis (Template)"
status: draft
canonicality: operative
---

# result.md — Experiment-Ergebnis

> Zusammenfassung der Ergebnisse in menschenlesbarer Form.

## Zusammenfassung

Run-001 wurde auf PR 58 dokumentiert. Die Klassentrennung erscheint im realen Diff sichtbar (canonical, derived, ephemeral jeweils betroffen), aber CI-Friction und manuelle Nacharbeit wurden in diesem ersten Lauf noch nicht vollstaendig erhoben.

## Beobachtungen

<!-- Messbar/sichtbar Beobachtetes, gestützt auf evidence.jsonl. Keine Schlüsse hier — die gehören in ## Deutung. -->

### Wirksamkeit (Effektivität)
Im ersten Lauf ist die Contract-Sicht auf Artefaktklassen direkt aus dem PR-Diff auswertbar.

### Reibung (Aufwand)
Noch nicht belastbar gemessen; wird in Run-002 und Run-003 explizit erhoben.

### Flow (subjektive Qualität)
<!-- Wie wurde die subjektive Qualität empfunden? -->

## Deutung

<!-- Was bedeuten diese Beobachtungen? Schlüsse, Hypothesenprüfung, Einschränkungen.
     Beobachtet und Gedeutet trennen: Was war messbar/sichtbar — und was ist Interpretation? -->

## Verdict

Vorlaeufig: noch offen. Execution ist gestartet, Ergebnisbewertung folgt nach weiteren Runs.

## Lessons Learned

<!-- Was wurde gelernt, unabhängig vom Verdict? -->

## Nächste Schritte

- Run-002 und Run-003 unter realen PRs erfassen
- CI-Statuschecks je Lauf miterheben
- danach `decision.yml` auf result_assessment umstellen

## Interpretation Budget

<!-- Pflicht bei adopted status / promotion-relevanten Experimenten (catalog/, prompts/). Muss ausgefüllt sein, bevor promoted wird. -->

### Allowed Claims
<!-- Was darf aus diesem Experiment direkt gefolgert werden? -->
- ...

### Disallowed Claims
<!-- Was darf NICHT gefolgert werden? Grenzen, Übertragbarkeits-Einschränkungen. -->
- ...

### Evidence Basis
- Direkt beobachtet:
- Indirekt gestützt:
- Nicht getestet:
