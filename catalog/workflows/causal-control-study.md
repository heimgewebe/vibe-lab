---
schema_version: "0.1.0"
title: "Kausale Kontrollstudie"
status: adopted
category: workflow
summary: "Workflow für kausale Kontrollstudien in Vibe-Coding-Experimenten: Isolierung einzelner Variablen durch gezieltes Kontrollarm-Design."
evidence_source: "experiments/2026-04-14_prompt-length-control/"
created: "2026-04-20"
updated: "2026-04-20"
author: "heimgewebe"
tags:
  - workflow
  - experiment-design
  - causal-control
  - methodology
relations:
  - type: validated_by
    target: ../../experiments/2026-04-14_prompt-length-control/results/result.md
---

# Workflow: Kausale Kontrollstudie

## Übersicht

Ein Workflow für die Durchführung kausaler Kontrollstudien in Vibe-Coding-Experimenten. Ziel: Eine einzelne Variable isolieren und alternative Erklärungen systematisch ausschließen.

## Schritte

### 1. Hypothese formulieren

- Welche Variable soll isoliert werden?
- Welche alternativen Erklärungen existieren?
- Beispiel: „Ist es die Struktur oder das Token-Volumen?"

### 2. Kontrollarm designen

- Einen Arm gestalten, der die alternative Erklärung testet
- Der Kontrollarm muss die Konfundierungsvariable reproduzieren, ohne die eigentliche Variable zu enthalten
- Beispiel: Ramble-First reproduziert hohes Token-Volumen ohne Constraint-Struktur

### 3. Messbare Metriken definieren

- Objektive Metrik wählen (z.B. test_pass_rate)
- Gleiche Messmethodik für alle Arme
- Baseline-Arm (z.B. Code-First) als Referenz

### 4. Durchführen und dokumentieren

- Alle Arme unter gleichen Bedingungen ausführen
- evidence.jsonl zeitnah befüllen
- Abweichungen vom Plan dokumentieren

### 5. Kausal interpretieren

- Ergebnis nur auf die isolierte Variable beziehen
- Interpretation Budget explizit setzen
- Ungetestete Variablen als offene Fragen benennen

## Beispiel: Prompt-Length-Control

| Arm | Isolierte Variable | Token-Volumen | Struktur | Ergebnis |
|-----|-------------------|---------------|----------|----------|
| Code-First | Baseline | niedrig | nein | 0.8 |
| Spec-First | Struktur + Volumen | hoch | ja | 1.0 |
| Ramble-First | Nur Volumen | hoch | nein | 0.8 |

**Schluss:** Volumen allein erklärt den Effekt nicht → Struktur ist kausal.
