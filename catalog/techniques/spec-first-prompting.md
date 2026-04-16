---
schema_version: "0.1.0"
title: "Spec-First Prompting"
status: adopted
category: technique
summary: "Vor der Code-Generierung eine formale Spezifikation (z.B. OpenAPI) generieren und reviewen lassen — verbessert Vollständigkeit, Konsistenz und Vertrauen messbar."
evidence_source: "experiments/2026-04-08_spec-first/"
created: "2026-04-08"
updated: "2026-04-10"
author: "heimgewebe"
tags:
  - prompting
  - spec-first
  - api-design
  - vibe-coding
relations:
  - type: validated_by
    target: ../../experiments/2026-04-08_spec-first/results/result.md
document_role: concept
---

# Spec-First Prompting

## Was

Vor der eigentlichen Code-Generierung wird das LLM aufgefordert, zuerst eine formale Spezifikation zu erstellen (z.B. OpenAPI, JSON-Schema, Interface-Definition). Diese Spec wird vom Menschen reviewt und angepasst, bevor die Implementierung beginnt.

## Warum

- Erzwingt Präzisierung der Anforderungen vor der Implementierung
- Reduziert Fehlercodes, Validierungslücken und Inkonsistenzen im generierten Code
- Senkt die Nacharbeit um Faktor 5-6× (gemessen: 4 vs. 23 Zeilen)
- Erhöht subjektives Vertrauen in den Output (4.0/5 vs. 2.7/5)

## Wann einsetzen

- REST-APIs und datenintensive Services
- Wenn das Ergebnis exakte Strukturen erfordert (Schemas, Interfaces, Protokolle)
- Bei mittlerer bis hoher Komplexität (>1 Endpunkt, >1 Entity)

## Wann NICHT einsetzen

- Schnelle Prototypen, bei denen Geschwindigkeit wichtiger ist als Vollständigkeit
- Triviale Einzeloperationen (z.B. eine Hilfsfunktion)

## Evidenz

Experiment: [2026-04-08_spec-first](../../experiments/2026-04-08_spec-first/)

- Vollständigkeit: 5/5 vs. 3/5 Fehlercodes
- Nacharbeit: 4 vs. 23 Zeilen
- Flow-Vertrauen: 4.0/5 vs. 2.7/5

## Einschränkungen

- Bisher nur mit GPT-4o via Copilot getestet
- Kleine Stichprobe (3 Tasks, 1 Person)
- Spec-Format (OpenAPI) ist domänenspezifisch; für CLI/UI sind andere Formate nötig
