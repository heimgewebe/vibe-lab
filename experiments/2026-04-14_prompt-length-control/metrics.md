---
title: "Metrics: Prompt-Length Control"
status: testing
canonicality: operative
---

# Metrics

## Ziel

Messen, ob der Leistungsvorteil von Spec-First auf inhaltlicher Strukturierung (Constraint-Deklaration) beruht oder lediglich auf erzwungener Token-Verzögerung (Chain-of-Thought Proxy durch längere Ausgabe).

## Primäre Metriken

`test_pass_rate` und `edge_cases_missed` sind abstrakte Vergleichsmetriken; in `results/evidence.jsonl` sind sie pro Arm als konkrete Metriken mit Suffix operationalisiert:

| Abstrakte Metrik | Operationalisierung pro Arm |
|---|---|
| `test_pass_rate` | `test_pass_rate_code_first`, `test_pass_rate_spec_first`, `test_pass_rate_ramble_first` |
| `edge_cases_missed` | `edge_cases_missed_code_first`, `edge_cases_missed_spec_first`, `edge_cases_missed_ramble_first` |

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

---

*Dieses metrics.md ist ein Phase-3-Artefakt (Blueprint v2 — Method Calibration) und gilt nur für dieses Experiment: `adoption_basis: executed`, explizites Vergleichsdesign (3 Arme). Es ist kein Pflichtmuster für alle Experimente.*
