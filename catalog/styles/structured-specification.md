---
schema_version: "0.1.0"
title: "Structured Specification"
status: adopted
category: style
summary: "Prompting-Stil, der formale Spezifikationsformate (OpenAPI, Interfaces, Schemas) als Zwischenprodukt nutzt — verbessert Vollständigkeit und Konsistenz."
evidence_source: "experiments/2026-04-08_spec-first/"
created: "2026-04-20"
updated: "2026-04-20"
author: "heimgewebe"
tags:
  - style
  - prompting
  - spec-first
  - api-design
relations:
  - type: validated_by
    target: ../../experiments/2026-04-08_spec-first/results/result.md
  - type: references
    target: ../techniques/spec-first-prompting.md
---

# Style: Structured Specification

## Beschreibung

Ein Prompting-Stil, der das LLM dazu auffordert, formale Spezifikationsformate (OpenAPI, TypeScript Interfaces, JSON Schema, Protobuf) als Zwischenprodukt zu erzeugen, bevor die eigentliche Implementierung beginnt.

## Stil-Merkmale

1. **Formales Format:** Nutze industrieübliche Spezifikationsformate — keine Freitext-Beschreibungen
2. **Vollständigkeit durch Struktur:** Das Format selbst erzwingt Abdeckung (z.B. OpenAPI → alle Statuscodes definieren)
3. **Review vor Implementierung:** Die Spec ist ein eigenständiges, reviewbares Artefakt
4. **Trennung von Was und Wie:** Spezifikation beschreibt das Ergebnis, nicht den Weg

## Geeignete Formate

| Kontext | Format |
|---------|--------|
| REST APIs | OpenAPI 3.0 |
| TypeScript | Interface Definitions |
| Datenmodelle | JSON Schema |
| gRPC | Protocol Buffers |
| CLI-Tools | Argument-Schema (docopt, yargs) |

## Evidenz

Aus dem Spec-First-Experiment:
- 5/5 Error-Codes mit Structured Specification vs. 3/5 ohne
- Faktor 5-6× weniger Nacharbeit
- Subjektives Vertrauen 4.0/5 vs. 2.7/5
