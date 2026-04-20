---
schema_version: "0.1.0"
title: "Spec-First + Anti-Pattern-Awareness"
status: adopted
summary: "Spec-First Prompting mit bewusstem Vermeiden des Vague-Prompt-and-Fix Anti-Patterns — reduziert Rework durch disziplinierte Spezifikation."
components:
  - practice: "../techniques/spec-first-prompting.md"
    role: "Positive Praxis: Erzwingt strukturierte Spezifikation"
  - practice: "../anti-patterns/vague-prompt-and-fix.md"
    role: "Negativbeispiel: Dokumentiert, was ohne Spec-First passiert (hoher Rework, inkonsistenter Code)"
evidence_source: "experiments/2026-04-08_spec-first/"
synergy_description: "Das Anti-Pattern 'Vague-Prompt-and-Fix' wird am wirksamsten vermieden, wenn Spec-First nicht nur als Technik, sondern als bewusste Gegenstrategie eingesetzt wird. Die Kenntnis des Anti-Patterns schärft die Motivation für disziplinierte Spezifikation."
created: "2026-04-20"
updated: "2026-04-20"
author: "heimgewebe"
tags:
  - combo
  - spec-first
  - anti-pattern
  - rework-reduction
---

# Spec-First + Anti-Pattern-Awareness

## Synergie

Spec-First Prompting als Technik und Vague-Prompt-and-Fix als Anti-Pattern bilden ein komplementäres Paar: Die Kenntnis des Anti-Patterns verstärkt die Disziplin bei der Spec-First-Anwendung.

## Evidenz

Aus dem Spec-First-Experiment:
- **Mit Spec-First:** 5/5 Error-Codes, 4 Zeilen Nacharbeit, Vertrauen 4.0/5
- **Ohne (Vague-Prompt):** 3/5 Error-Codes, 23 Zeilen Nacharbeit, Vertrauen 2.7/5

## Anwendung

1. Vor jedem LLM-Coding-Task: Bewusst das Anti-Pattern erkennen (Will ich gerade „einfach loslegen"?)
2. Spec-First als Gegenmittel einsetzen: Formale Spezifikation erzwingen
3. Nach der Generierung: Prüfen, ob die Spec eingehalten wurde
