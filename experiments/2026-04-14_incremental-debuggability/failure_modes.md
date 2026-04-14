---
title: "Failure Modes — Incremental vs. Single-Shot: Debuggability"
status: designed
canonicality: operative
---

# Failure Modes — Incremental Debuggability

## Wann funktioniert diese Praxis NICHT?

- [ ] Wenn beide Varianten keine Laufzeitbugs produzieren — dann misst das Experiment nur
  Ausführungsaufwand, nicht Bug-Detection
- [ ] Wenn der bekannte Bug trivial genug ist, um sofort bei Input 1 sichtbar zu werden —
  dann ist `time_to_first_bug_detection` für beide Arme identisch = 1
- [ ] Wenn der Fix trivial ist und keinen strukturellen Unterschied zwischen Single-Shot
  und Incremental zeigt (beide brauchen 1 Prompt)
- [ ] Wenn das Modell bei Incremental den Bug sofort aus dem Kontext der Schritte
  „erinnert" (Modell-Leakage durch Kontext-Akkumulation)

## Bekannte Fehlannahmen

- [ ] Annahme, dass Modularität das Finden und Fixen von Bugs erleichtert — das muss erst
  gemessen werden; es ist die eigentliche Hypothese
- [ ] Annahme, dass 5 Testinputs repräsentativ für das Fehlerverhalten sind — kleine Menge,
  ausgewählt um den bekannten Bug zu triggern (Selektion-Bias)
- [ ] Annahme, dass der revertierte Bug den Originalzustand korrekt rekonstruiert — wenn
  andere Korrekturen im selben Commit gemacht wurden, könnte die Rekonstruktion unvollständig sein
- [ ] Annahme, dass „Anzahl Prompts bis Fix" eine faire Aufwandsmessung ist — Incremental
  kann strukturell einfacher zu fixen sein (Modul-Isolation), auch wenn mehr Prompts nötig sind

## Grenzen der Evidenz

- **Stichprobengröße:** 1 Task, 5 Inputs — nicht generalisierbar; statistisch nicht signifikant
- **Kontext-Abhängigkeit:** CLI-Tools haben definierte Input-Output-Semantik — andere
  Domänen (APIs, UI, Datenverarbeitung) verhalten sich anders
- **Bug ist bekannt:** Kein Blind-Test möglich, da der Parser-Bug aus dem Vorgänger bereits
  dokumentiert ist; echte „Discovery"-Dynamik ist damit begrenzt
- **Einzelnes Modell:** Nur Claude Sonnet; andere Modelle könnten unterschiedliche Bug-Muster
  erzeugen
- **Kein Langzeit-Horizont:** Das Experiment misst Kurzzeit-Debug-Aufwand, nicht
  Langzeit-Wartbarkeit

## Risiko einer Fehlanwendung

Wenn dieses Experiment „Incremental ist schneller beim Bug-Fixen" zeigt, könnte das
zu vorschneller Adoption führen — auch wenn die Ursache der Modul-Isolation und nicht
der Incremental-Strategie zuzuschreiben ist. Modul-Isolation ist mit Single-Shot ebenfalls
erreichbar (z.B. durch explizites Dateiaufteilungs-Prompting).

Das Experiment misst nicht: „Ist Incremental besser?" — sondern: „Hat Incremental
bei diesem spezifischen Fehlertyp in diesem spezifischen Task strukturelle Vorteile?"

Der Scope muss bei der Interpretation strikt eingehalten werden.
