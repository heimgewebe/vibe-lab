---
title: "Initiale Prompt-/Setup-Situation: Upfront Structuring"
status: draft
canonicality: operative
---

# INITIAL.md — Initiale Situation

> **Pflichtdokument für Adopt-Kandidaten.** Dokumentiert den exakten Ausgangszustand zu Beginn des Experiments.

## Initialer Prompt / Setup

Die Aufgabe ist identisch zur Vorstudie: Implementierung eines "Römische Zahlen zu Integer" Konverters (`roman_to_int`) inklusive Fehlererkennung für ungültige Formate (z.B. "IIII", "VV").

### Arm 1: Code-First (Baseline)
Siehe Ergebnisse aus der Vorstudie. Prompt:
`Schreibe eine Python-Funktion roman_to_int(s: str) -> int...`

### Arm 2: Spec-First
`Wir wollen eine Python-Funktion roman_to_int(s: str) -> int implementieren, die römische Zahlen in Integer konvertiert und bei ungültigen Formaten einen ValueError wirft. Schritt 1: Schreibe AUSSCHLIESSLICH eine textuelle Spezifikation aller Edge-Cases und Fehlerregeln. Schritt 2: Erst wenn die Spezifikation steht, generiere die Implementierung der Funktion entsprechend dieser Regeln.`

### Arm 3: Test-First (TDD)
Siehe Ergebnisse aus der Vorstudie. Prompt:
`Schritt 1: Schreibe AUSSCHLIESSLICH die ausführlichen pytest-Tests... Schritt 2: Generiere die Implementierung...`

## Systemkonfiguration

- Standard-Python-Umgebung mit `pytest`.
- Ausführung in `experiments/2026-04-14_upfront-structuring/artifacts/`.

## Erwartete Baseline

Code-First scheitert oft an Edge-Cases. Wir erwarten, dass sowohl Spec-First als auch Test-First die Robustheit signifikant steigern, da beide das LLM zur Problemanalyse zwingen, bevor Code geschrieben wird.
