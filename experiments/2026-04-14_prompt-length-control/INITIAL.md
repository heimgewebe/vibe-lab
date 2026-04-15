---
title: "Initiale Prompt-/Setup-Situation: Prompt-Length Control"
status: testing
canonicality: operative
---

# INITIAL.md — Initiale Situation

> Dokumentiert den exakten Ausgangszustand zu Beginn des Experiments.

## Initialer Prompt / Setup

Aufgabe: `extract_bold_text(text: str) -> list[str]`.
Logik: Extrahiere alle Wörter, die von exakt zwei nicht-escapeten Sternen `**` umschlossen sind. Escapete Sterne `\*\*` oder einzelne Sterne `*` zählen nicht als Begrenzer. Wenn Sterne innerhalb der Begrenzer stehen, gelten sie als Teil des Textes.

### Arm 1: Code-First (Baseline)
`Schreibe eine Python-Funktion extract_bold_text(text: str), die Wörter extrahiert, die von ** umschlossen sind. Escapete Sterne oder einzelne Sterne zählen nicht. Gib direkt den Code aus.`

### Arm 2: Spec-First (Declarative Control)
`Schritt 1: Schreibe AUSSCHLIESSLICH eine präzise Liste von Edge-Cases für die extract_bold_text Funktion. Schritt 2: Erst dann generiere den Code.`

### Arm 3: Ramble-First (Token Bloat Proxy)
`Schritt 1: Schreibe AUSSCHLIESSLICH einen 300-Wörter Essay über die historische Bedeutung von Markupsprachen und Parsern. Schritt 2: Erst dann generiere den Code für die extract_bold_text Funktion.`

## Systemkonfiguration

- Python mit `pytest`.
- Ausführung in `experiments/2026-04-14_prompt-length-control/artifacts/`.
