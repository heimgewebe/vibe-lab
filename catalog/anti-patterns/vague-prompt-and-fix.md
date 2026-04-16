---
schema_version: "0.1.0"
title: "Vague-Prompt-and-Fix"
status: adopted
category: anti-pattern
summary: "Vage Aufgabenbeschreibung an LLM geben und dann iterativ nachbessern — führt zu inkonsistentem Code und hohem Rework."
evidence_source: "experiments/2026-04-08_spec-first/"
created: "2026-04-10"
updated: "2026-04-10"
author: "heimgewebe"
tags:
  - anti-pattern
  - prompting
  - vibe-coding
relations:
  - type: references
    target: ../../experiments/2026-04-08_spec-first/results/result.md
document_role: concept
---

# Anti-Pattern: Vague-Prompt-and-Fix

## Beschreibung

Das häufigste Vibe-Coding-Anti-Pattern: Eine vage, natürlichsprachliche Beschreibung wird direkt an ein LLM gegeben ("Bau mir eine API"), und die Lücken im Ergebnis werden dann iterativ per Nachfragen und manueller Nacharbeit geschlossen.

## Warum es ein Anti-Pattern ist

- **Inkonsistenz:** Ohne vorab definierte Struktur generiert das LLM unterschiedliche Response-Formate für ähnliche Endpunkte.
- **Fehlende Edge Cases:** Das LLM "vergisst" Fehlercodes, Validierung und Grenzfälle, die nicht explizit genannt wurden.
- **Hoher Rework:** Nacharbeit von ~23 Zeilen pro Task (gemessen), statt 4 Zeilen bei strukturiertem Vorgehen.
- **Falsches Vertrauen:** Der initiale Output sieht funktional aus, verbirgt aber strukturelle Mängel.

## Evidenz

Im Spec-First-Experiment (2026-04-08) wurde dieses Anti-Pattern als Kontrollgruppe verwendet:
- 3/5 Fehlercodes fehlten (statt 5/5 bei Spec-First)
- 2/4 Validierungen fehlten beim Auth-Task
- Inkonsistente Response-Strukturen bei Pagination
- Vertrauenswert: 2.7/5 (vs. 4.0/5 bei Spec-First)

## Bessere Alternative

→ [Spec-First Prompting](../techniques/spec-first-prompting.md)

## Fehlermodus

| Dimension       | Auswirkung                                   |
| --------------- | -------------------------------------------- |
| Vollständigkeit | Lückenhaft (fehlende Fehlercodes, Validierung) |
| Konsistenz      | Strukturell inkonsistent                      |
| Nacharbeit      | 5-6× höher als bei strukturiertem Vorgehen    |
| Vertrauen       | Täuschend — sieht besser aus als es ist       |
