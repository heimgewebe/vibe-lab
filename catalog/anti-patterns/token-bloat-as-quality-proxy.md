---
schema_version: "0.1.0"
title: "Token-Bloat-as-Quality-Proxy"
status: adopted
category: anti-pattern
summary: "Mehr Output-Tokens erzwingen in der Annahme, das Modell 'denke dann besser' — widerlegt durch kausale Kontrollstudie."
evidence_source: "experiments/2026-04-14_prompt-length-control/"
created: "2026-04-20"
updated: "2026-04-20"
author: "Jules"
tags:
  - prompting
  - anti-pattern
  - cognitive-modes
  - chain-of-thought
relations:
  - type: validated_by
    target: ../../experiments/2026-04-14_prompt-length-control/results/result.md
  - type: references
    target: ../../catalog/techniques/prompt-length-control.md
---

# Token-Bloat-as-Quality-Proxy

## Warum ist das ein Anti-Pattern?

Die Annahme: „Wenn ich das Modell dazu bringe, mehr Text auszugeben (z.B. durch Chain-of-Thought-Prompting oder Aufforderung zu ausführlichen Erklärungen), wird der nachfolgende Code besser."

**Widerlegt durch:** Prompt-Length-Control-Experiment. Ramble-First (hohes Token-Volumen ohne Struktur) erzielte identische Ergebnisse wie Code-First (0.8 vs. 0.8 test_pass_rate). Nur Spec-First (strukturierte Constraint-Formulierung) verbesserte die Leistung auf 1.0.

## Evidenz

- **Ramble-First:** test_pass_rate 0.8 — identisch mit Code-First trotz hohem Token-Volumen
- **Spec-First:** test_pass_rate 1.0 — mit gleichem Token-Volumen wie Ramble-First
- Der Unterschied: Inhaltliche Strukturierung (Constraint-Formulierung) vs. bloße Textmenge

## Typische Manifestationen

- „Erkläre erst ausführlich, was du tun willst, bevor du codierst" — ohne strukturierte Constraints
- Lange Chain-of-Thought-Prompts, die das Modell zum Schreiben irrelevanter Erklärungen zwingen
- Annahme, dass verboses Reasoning automatisch besseren Code erzeugt

## Stattdessen

Statt Token-Volumen zu maximieren:
→ **Constraint-Formulierung erzwingen** (Spec-First, Test-First)
→ Der kognitive Modus entscheidet, nicht die Textmenge
