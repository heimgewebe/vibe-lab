---
schema_version: "0.1.0"
title: "Spec-First + Constraint-Control"
status: adopted
summary: "Spec-First Prompting mit bewusster Constraint-Formulierung kombinieren — maximiert Strukturgewinn durch kognitiven Moduswechsel."
components:
  - practice: "../techniques/spec-first-prompting.md"
    role: "Strukturgeber: Erzwingt formale Spezifikation vor Code-Generierung"
  - practice: "../techniques/prompt-length-control.md"
    role: "Kausaler Mechanismus: Stellt sicher, dass die Spec echte Constraints formuliert statt bloßes Token-Volumen zu erzeugen"
evidence_source: "experiments/2026-04-14_prompt-length-control/"
synergy_description: "Spec-First allein könnte zum Ritual verkommen (lange Specs ohne echte Constraints). Die Einsicht aus Prompt-Length-Control schärft den Blick: Nur aktive Constraint-Formulierung — nicht die Spec-Länge — erzeugt den Qualitätsgewinn. Die Kombination macht Spec-First epistemisch robust."
created: "2026-04-20"
updated: "2026-04-20"
author: "heimgewebe"
tags:
  - combo
  - spec-first
  - cognitive-modes
  - constraint-design
---

# Spec-First + Constraint-Control

## Synergie

Spec-First Prompting erzwingt eine Spezifikation vor der Code-Generierung. Prompt-Length-Control zeigt, dass **nicht die Länge** der Spezifikation den Effekt erzeugt, sondern die **aktive Formulierung von Constraints**. Zusammen ergibt sich ein geschärftes Vorgehen:

1. **Spec-First:** Schreibe eine formale Spezifikation (z.B. OpenAPI, Interface-Definition).
2. **Constraint-Control:** Stelle sicher, dass die Spec echte Constraints enthält (Edge Cases, Validierungsregeln, Fehlerfälle) — nicht nur Struktur-Boilerplate.

## Wann kombinieren

- Bei jedem Spec-First-Einsatz: Prüfe, ob die Spec tatsächlich Constraints formuliert
- Besonders bei komplexen APIs mit vielen Edge Cases
- Wenn der Verdacht besteht, dass Specs zum rituellen Overhead werden

## Anti-Synergie vermeiden

- Spec-First ohne Constraint-Bewusstsein → lange Specs, gleiche Fehler
- Constraint-Formulierung ohne Spec-Struktur → unorganisierte Constraint-Listen
