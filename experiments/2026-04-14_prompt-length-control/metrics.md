---
title: "Metrics: Prompt-Length Control"
status: testing
canonicality: operative
---

# Metrics

## Ziel

Messen, ob der Leistungsvorteil von Spec-First auf inhaltlicher Strukturierung (Constraint-Deklaration) beruht oder lediglich auf erzwungener Token-Verzögerung (Chain-of-Thought Proxy durch längere Ausgabe).

## Primäre Metriken

- **test_pass_rate** — Anteil bestandener Tests pro Arm (pytest exit code 0 = 1.0, sonst < 1.0)
- **edge_cases_missed** — Anzahl nicht abgedeckter Randfälle im generierten Parser-Code

## Sekundäre Metriken

Keine. Das Experiment ist bewusst auf eine einzelne Vergleichsdimension beschränkt (missed edge-cases bei Text-Parsing).

## Messmethode

- Drei Arme (Code-First, Spec-First, Ramble-First) generieren jeweils einen Parser
- Jeder Arm wird gegen dieselbe pytest-Testsuite ausgeführt
- Ergebnisse in `results/evidence.jsonl` protokolliert (Felder: `metric`, `value`, `context`, `artifact_ref`)
- Referenzierte Artefakte: `artifacts/code_first_run.txt`, `artifacts/spec_first_run.txt`, `artifacts/ramble_first_run.txt`

## Einschränkungen

- **Einzelne Aufgabe:** Nur ein Text-Parsing-Szenario (escaped asterisk). Keine Verallgemeinerung auf andere Aufgabentypen.
- **Einzelne Iteration:** Kein Wiederholungslauf, keine statistische Absicherung.
- **Keine Zeitmessung:** Ausführungsdauer pro Arm nicht erfasst.
- **Kein Confound-Schutz gegen Ramble-Pivot:** Mögliches Risiko, dass das Modell den Essay-Text implizit zur Strukturierung nutzt (dokumentiert in `failure_modes.md`).
