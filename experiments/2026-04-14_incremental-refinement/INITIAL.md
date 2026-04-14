---
title: "Incremental Refinement vs. Single-Shot — Initiale Situation"
status: testing
canonicality: operative
---

# INITIAL.md — Initiale Situation

## Initialer Prompt / Setup

### Single-Shot (Kontrollgruppe)

Beispiel-Prompt für Task 1 (Bookmark-API):

```
Erstelle eine vollständige REST-API für ein Bookmark-System in TypeScript mit Express.js.
Anforderungen:
- CRUD-Operationen für Bookmarks (URL, Titel, Beschreibung, Tags)
- Tag-basierte Filterung
- Volltextsuche über Titel und Beschreibung
- Input-Validierung
- Fehlerbehandlung mit passenden HTTP-Statuscodes
- TypeScript-Typen für alle Datenstrukturen
```

### Incremental (Treatmentgruppe)

Derselbe Task, zerlegt in Teilprompts:

```
Schritt 1: "Definiere die TypeScript-Typen für ein Bookmark-System (Bookmark, Tag, Suchparameter)."
Schritt 2: "Erstelle das Express-Routing für CRUD-Operationen auf Bookmarks."
Schritt 3: "Implementiere die Kernlogik für Create, Read, Update, Delete."
Schritt 4: "Ergänze Fehlerbehandlung mit passenden HTTP-Statuscodes."
Schritt 5: "Füge Input-Validierung für alle Endpoints hinzu."
Schritt 6: "Erstelle Tests für die wichtigsten Pfade."
```

## Systemkonfiguration

- Frisches TypeScript-Projekt (`npm init`, `tsc --init`)
- Express.js installiert
- Keine vordefinierten Patterns oder Boilerplate
- Standard-Copilot-Konfiguration ohne custom instructions

## Erwartete Baseline

Ohne bewusste Strategie (weder Single-Shot noch Incremental) würde ein typischer Vibe-Coding-Ansatz vermutlich 2–3 Prompts verwenden — mehr als Single-Shot, aber weniger strukturiert als Incremental. Erwartete Schwächen: inkonsistente Fehlerbehandlung, lückenhafte Validierung, fehlende Tests.
