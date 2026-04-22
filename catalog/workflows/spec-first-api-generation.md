---
schema_version: "0.1.0"
title: "Spec-First API-Generierung"
status: adopted
category: workflow
summary: "Vollständiger Workflow für LLM-gestützte API-Entwicklung: Problem → Spec → Review → Implementierung → Validierung."
evidence_source: "experiments/2026-04-08_spec-first/"
created: "2026-04-20"
updated: "2026-04-20"
author: "heimgewebe"
tags:
  - workflow
  - spec-first
  - api-design
  - vibe-coding
relations:
  - type: references
    target: ../techniques/spec-first-prompting.md
  - type: validated_by
    target: ../../experiments/2026-04-08_spec-first/results/result.md
---

# Workflow: Spec-First API-Generierung

## Übersicht

Ein strukturierter Workflow für die Generierung von APIs mit LLM-Unterstützung, basierend auf den Erkenntnissen des Spec-First-Experiments.

## Schritte

### 1. Problem definieren

- Aufgabe klar beschreiben (Entitäten, Endpunkte, Validierungsregeln)
- Bekannte Edge Cases sammeln
- Nicht-funktionale Anforderungen dokumentieren (Pagination, Fehlerformat)

### 2. Spezifikation generieren lassen

- LLM eine formale Spezifikation (z.B. OpenAPI 3.0) generieren lassen
- Prompt muss explizit fordern: Statuscodes, Schemas, Validierungsregeln, Fehlerfälle

### 3. Spezifikation reviewen

- Vollständigkeit prüfen: Sind alle Endpunkte, Fehler, Edge Cases abgedeckt?
- Konsistenz prüfen: Einheitliches Response-Format, konsistente Namensgebung?
- Fehlende Constraints ergänzen

### 4. Implementierung generieren lassen

- LLM die geprüfte Spezifikation als Implementierungsgrundlage geben
- Explizit auf Einhaltung der Spec verweisen

### 5. Validierung

- Generierten Code gegen Spec prüfen
- Test-Coverage für Edge Cases sicherstellen
- Abweichungen dokumentieren und korrigieren

## Messwerte (aus Experiment)

| Metrik | Mit Workflow | Ohne Workflow |
|--------|-------------|---------------|
| Error-Code-Coverage | 5/5 | 3/5 |
| Nacharbeit (Zeilen) | 4 | 23 |
| Subjektives Vertrauen | 4.0/5 | 2.7/5 |
