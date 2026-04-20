---
schema_version: "0.1.0"
title: "Constraint-First"
status: adopted
category: style
summary: "Prompting-Stil, der LLMs zuerst zur expliziten Formulierung von Constraints zwingt, bevor Code generiert wird — maximiert den kognitiven Moduswechsel."
evidence_source: "experiments/2026-04-14_prompt-length-control/"
created: "2026-04-20"
updated: "2026-04-20"
author: "heimgewebe"
tags:
  - style
  - prompting
  - constraint-design
  - cognitive-modes
relations:
  - type: validated_by
    target: ../../experiments/2026-04-14_prompt-length-control/results/result.md
  - type: references
    target: ../techniques/spec-first-prompting.md
---

# Style: Constraint-First

## Beschreibung

Ein Prompting-Stil, der das LLM **zuerst zur aktiven Formulierung von Constraints** auffordert, bevor Code generiert wird. Unterscheidet sich von bloßem „Erkläre erst" (Ramble-First) durch den Fokus auf operative, testbare Einschränkungen.

## Stil-Merkmale

1. **Constraints vor Code:** Jeder Prompt beginnt mit der Aufforderung, Eingangs-/Ausgangs-Constraints, Edge Cases und Fehlerfälle zu definieren.
2. **Deklarativ statt narrativ:** Constraints werden in strukturierter Form formuliert (Listen, Tabellen, Schemas) — nicht als Prosa.
3. **Testbare Aussagen:** Jede Constraint-Formulierung muss in einen Test überführbar sein.
4. **Verzicht auf Padding:** Kein „Erkläre erst ausführlich" — nur relevante Constraints.

## Abgrenzung

| Aspekt | Constraint-First | Ramble-First | Code-First |
|--------|-----------------|--------------|------------|
| Struktur | Deklarative Constraints | Narrativer Essay | Keine |
| Token-Volumen | Variabel | Hoch | Niedrig |
| Qualitätseffekt | Nachgewiesen (+20%) | Kein Effekt | Baseline |

## Beispiel

```
Bevor du Code schreibst, definiere:
1. Input-Constraints: [Format, Grenzen, Sonderfälle]
2. Output-Constraints: [Struktur, Typen, Formatierung]
3. Fehlerverhalten: [Ungültige Inputs → erwartetes Verhalten]
4. Edge Cases: [Leere Eingabe, Maximalwerte, Sonderzeichen]

Erst dann: Implementiere.
```
