---
schema_version: "0.1.0"
title: "Prompt-Length Control (Cognitive-Mode-Switching)"
status: adopted
category: technique
summary: "Leistungszugewinn bei Upfront-Structuring beruht auf kognitivem Moduswechsel (Constraint-Formulierung), nicht auf Token-Volumen — kausaler Kontrollbeweis."
evidence_source: "experiments/2026-04-14_prompt-length-control/"
created: "2026-04-14"
updated: "2026-04-20"
author: "Jules"
tags:
  - prompting
  - cognitive-modes
  - spec-first
  - causal-control
  - vibe-coding
relations:
  - type: validated_by
    target: ../../experiments/2026-04-14_prompt-length-control/results/result.md
  - type: references
    target: ../../catalog/techniques/spec-first-prompting.md
---

# Prompt-Length Control (Cognitive-Mode-Switching)

## Kernaussage

Der Leistungszugewinn von Spec-First / Test-First Prompting beruht **nicht** auf Token-Volumen oder Chain-of-Thought-Proxy-Effekten, sondern auf einem echten **kognitiven Moduswechsel**: Das Modell formuliert aktiv Constraints, bevor es Code generiert.

## Evidenz

Eine Kontrollstudie mit drei Armen an einem Text-Parsing-Task:

| Arm | Token-Volumen | Struktur | test_pass_rate |
|-----|--------------|----------|----------------|
| Code-First | niedrig | keine | 0.8 |
| Spec-First | hoch | ja (Constraints) | 1.0 |
| Ramble-First | hoch | nein (Essay) | 0.8 |

Ramble-First produzierte hohes Token-Volumen (wie Spec-First), fiel aber in denselben Naiv-Regex-Fehler wie Code-First zurück.

## Wann anwenden

- Wenn Spec-First-Effekte hinterfragt werden: Dieser Befund schließt die Token-Volumen-Hypothese aus.
- Als theoretische Basis für den Einsatz von Upfront-Structuring in Prompt-Designs.
- Bei der Gestaltung neuer Prompting-Strategien: Constraint-Formulierung > reine Textmenge.

## Einschränkungen

- n=1 Task, 1 Modell, 1 Experimentator
- Nur Text-Parsing-Kontext — andere Task-Typen nicht getestet
- Cognitive-Modes-Theorie ist gestützt, aber nicht erschöpfend bewiesen
