---
title: "Kanban Board UI/State Challenge v1"
status: active
canonicality: operative
---

# Benchmark Challenge: Kanban Board (v1)

## Zweck

Standardisierte Vergleichsaufgabe zur Bewertung von Vibe-Coding-Techniken bei der Generierung von interaktiven UI-Komponenten und lokalem State-Management.

## Aufgabe

Generiere eine interaktive Kanban-Board-Applikation mit den folgenden Anforderungen:

### Funktionen
1. **Spalten-Management**: Mindestens drei Standardspalten (z.B. "To Do", "In Progress", "Done").
2. **Karten-Erstellung**: Neue Aufgaben als Karten in einer Spalte anlegen.
3. **Drag & Drop**: Karten zwischen Spalten verschieben.
4. **Bearbeiten/Löschen**: Bestehende Karten editieren oder entfernen.
5. **Persistenz**: Zustand (Spalten und Karten) im lokalen Speicher (Local Storage) des Browsers sichern.

### Anforderungen
- Frontend-Framework (React, Vue, oder Svelte) mit TypeScript.
- Sauberes State-Management (kein unnötiges Prop-Drilling).
- Zugänglichkeit (Basic a11y, z.B. Tastaturbedienbarkeit beim Fokus).
- Responsives Layout (Desktop und Mobile).

## Bewertungskriterien

| Kriterium          | Gewicht | Beschreibung                                  |
| ------------------ | ------: | --------------------------------------------- |
| Funktionalität     | 30%     | Alle Kernfunktionen (inkl. Drag & Drop) laufen fehlerfrei |
| UI/UX & State      | 25%     | State-Management ist robust, UI reagiert performant |
| Persistenz         | 15%     | Local Storage funktioniert zuverlässig beim Reload |
| Code-Qualität      | 15%     | Komponenten-Schnittverlauf, Lesbarkeit, Typisierung |
| Nacharbeit         | 15%     | Zeilen manueller Korrektur nach Generierung     |

## Versionierung

- **Version:** v1
- **Erstellt:** 2026-04-11
- **Änderungen:** Initiale Version

> Beim Referenzieren in `decision.yml` bitte `challenge_version: "kanban-board-v1"` angeben.
