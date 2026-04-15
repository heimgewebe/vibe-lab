---
title: "Experiment-Ergebnisse: TDD Vibe (Vorstudie)"
status: inconclusive
canonicality: operative
---

# result.md — Experiment-Ergebnisse

> **Vorstudie.** Fasst die Ergebnisse und die getroffene Entscheidung zusammen.

## Zusammenfassung der Ergebnisse

Das Experiment verglich den klassischen Code-First-Ansatz (Baseline) mit dem TDD-Vibe-Ansatz (Treatment) bei der Implementierung eines komplexen, logik-lastigen Utilities (`roman_to_int` mit strenger Format-Validierung).

- **Baseline (Code-First):** Das Modell erzeugte schnell funktionierenden Code für den *Happy Path*, ignorierte aber subtile Validierungsregeln (wie maximal 3 Wiederholungen, ungültige Subtraktionen). Die nachträglich generierten Tests fielen entweder durch oder testeten diese Edge-Cases gar nicht erst.
- **Treatment (TDD-Vibe):** Durch die strikte Anweisung, *zuerst* umfassende pytest-Tests inklusive Edge-Cases zu schreiben, wurde das Modell gezwungen, das Problem tiefgreifend zu durchdenken. Die darauffolgende Implementierung war deutlich robuster und bestand alle Tests im ersten Anlauf.

## Datenpunkte (Evidence)

Siehe `evidence.jsonl`:
- Baseline test pass rate: 40% (fehlgeschlagen bei `IIII`, `VV`, `IC`).
- Treatment test pass rate: 100% (Alle komplexen Validierungen direkt im ersten Versuch bestanden).

## Erkenntnisse

1. **Test-Abdeckung als Leitplanke:** Tests vorab zu schreiben wirkt wie eine Mini-Spezifikation (ähnlich Spec-First, aber direkt ausführbar).
2. **Reduzierte Iterationen:** Während Code-First bei komplexer Logik oft in einem "Fixing-Loop" endet, reduziert TDD Vibe die Iterationen auf (oft) einen Durchgang, da das Ziel (die Tests) von Anfang an klar ist.
3. **Kontext-Fenster:** Bei sehr großen Dateien könnte der TDD Ansatz an Grenzen stoßen, wenn Tests *und* Implementierung im selben Prompt verlangt werden. Hier müsste man iterativ vorgehen.

## Entscheidung

**Urteil:** Inconclusive (als Vorstudie eingefroren)
**Begründung:** Obwohl das Signal für TDD-Vibe sehr stark war, wurde methodisch nicht sauber unterschieden, ob der Erfolg durch *TDD an sich* oder einfach durch *irgendeine Form von expliziter Vorstrukturierung* zustande kam. Um zu verhindern, dass ein Artefakt der Vorstrukturierung fälschlicherweise als TDD-Spezifikum kanonisiert wird, wird dieses Experiment als Vorstudie eingefroren.

## Nächste Schritte

- [x] Ein neues Folgeexperiment (`experiments/2026-04-14_upfront-structuring`) aufsetzen, um die Kausalfrage zu klären: Vergleiche `code-first`, `spec-first` und `test-first` bei identischer Aufgabe.
