---
title: "Spec-First Vibe-Coding — Initiale Situation"
status: adopted
canonicality: operative
---

# INITIAL.md — Initiale Situation

## Initialer Prompt / Setup

### Kontrollgruppe (ohne Spec-First)
```
Erstelle eine REST-API mit Express.js und TypeScript für eine Benutzerverwaltung.
Die API soll CRUD-Operationen unterstützen.
```

### Treatmentgruppe (mit Spec-First)
```
Erstelle zuerst eine OpenAPI 3.0 Spezifikation für eine REST-API zur Benutzerverwaltung
mit CRUD-Operationen. Definiere alle Endpunkte, Request/Response-Schemas, Fehlercodes
und Validierungsregeln. Implementiere erst nach Review der Spec.
```

## Systemkonfiguration

- GitHub Copilot Chat in VS Code
- Keine besonderen System-Prompts oder Copilot Instructions
- Frisches TypeScript-Projekt (`npm init -y`, `tsc --init`)
- Express.js + @types/express installiert

## Erwartete Baseline

Ohne Spec-First-Ansatz:
- Wahrscheinlich funktionierender CRUD-Code, aber mit Lücken in Fehlercodes, Validierung und Edge Cases
- Manuelle Nacharbeit für konsistente Response-Strukturen erwartet
