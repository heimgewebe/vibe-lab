---
title: "Incremental vs. Single-Shot: Debuggability — Kontext"
status: testing
canonicality: operative
relations:
  - type: derived_from
    target: ../../experiments/2026-04-14_incremental-refinement/results/result.md
document_role: experiment
---

# CONTEXT.md — Experiment-Kontext

## Ausgangslage

Das Vorgängerexperiment (`2026-04-14_incremental-refinement`) zeigte, dass Incremental Refinement
modulareren Code erzeugt. Das Verdict wurde auf **inconclusive** herabgestuft, weil entscheidende
Evidenz fehlte:

1. **Kein Runtime-Test:** Beide Strategien wurden nur kompiliert, nie ausgeführt.
2. **Fehlende Tests:** method.md verlangte „Tests generieren" (Schritt 6), dieser Schritt
   unterblieb.
3. **Bug im Incremental-Arm:** Task 2 incremental enthielt einen CLI-Parser-Bug (doppeltes `i++`),
   der trotz fehlerfreier Kompilierung zur Laufzeit Argumente übersprang.

Das Vorgängerexperiment beantwortete: *„Welche Strategie erzeugt modulareren Code?"*

Dieses Experiment beantwortet eine orthogonale, wichtigere Frage:

> **„Welche Strategie ist weniger gefährlich? — Welche macht versteckte Fehler sichtbarer?"**

Die Sinnachse verschiebt sich von Code-Architektur zu Fehlerverhalten:
- Single-Shot kann strukturell kompakter sein, aber Fehler bleiben länger verborgen
- Incremental schafft mehr Review-Fenster, aber das schützt nicht automatisch vor semantischen Fehlern

**Alternative Leitfrage (radikal):** Statt „Welche Strategie ist besser?" — testen wir,
welche Strategie Bugs *früher sichtbar* macht. Das führt zu einer anderen Decision Rule:
- **sicherheitskritisch / Produktion:** Incremental (mehr Review-Fenster)
- **Prototyping / Exploration:** Single-Shot (schneller, Qualität sekundär)

## Scope-Einschränkung

Dieses Experiment isoliert **Task 2 (CSV CLI)** aus dem Vorgängerexperiment, weil:
- Der Task bereits einen belegten Laufzeitbug produziert hat
- CLI-Tools eindeutig testbar sind (definierte Inputs → definierte Outputs)
- Beide Varianten (Single-Shot und Incremental) bereits als Artefakte vorliegen

Beide Ausgangsvarianten werden als Startpunkt genommen. Sie werden ausgeführt — nicht
nur kompiliert.

## Umgebung

- **Tools:** GitHub Copilot (Agent-Modus), Claude Sonnet, ts-node
- **Sprache:** TypeScript / Node.js
- **Projekttyp:** CLI-Tool (CSV Parser + Transformer)
- **Ausführungsumgebung:** Node.js mit ts-node oder tsc compile + node
- **Testdaten:** 5 definierte CSV-Eingaben (siehe INITIAL.md)

## Relevante Vorarbeiten

- `experiments/2026-04-14_incremental-refinement/` — Vorgänger; Verdict inconclusive;
  Modularität belegt, Runtime-Qualität offen
- `experiments/2026-04-08_spec-first/` — zeigt Wert von Vorarbeit; orthogonale Dimension

## Einschränkungen

- Nur ein Task (Task 2) wird untersucht — Generalisierbarkeit eingeschränkt
- Beide Varianten wurden vom gleichen Agenten mit gleicher Meta-Intention erzeugt
- „Zeit bis Bug-Entdeckung" kann nicht rückwirkend gemessen werden; sie wird operationalisiert
  als „Anzahl Ausführungsversuche bis erste Fehlerbeobachtung"
- Menschlicher Review-Anteil in Incremental bleibt eine Confounder-Variable
