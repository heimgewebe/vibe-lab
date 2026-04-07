---
name: "YOLO vs. Spec-First: REST-API Challenge"
date: 2026-04-07
hypothesis: "Spec-First Vibe liefert bei der REST-API-Challenge bessere Codequalität als YOLO-Prompting, braucht aber deutlich länger"
tools: [cursor]
techniques: [prompt-priming]
styles: [yolo-prompting, spec-first-vibe]
status: completed
result: confirmed
ratings:
  speed: 4
  accuracy: 3
  code_quality: 3
  iterability: 3
  cognitive_load: 3
  scalability: 3
  creativity: 3
tags: [comparison, rest-api, challenge-01, style-comparison]
---

# 🧪 Experiment: YOLO vs. Spec-First bei REST-API Challenge

## Hypothese

> Spec-First Vibe liefert bei der REST-API-Challenge (Challenge 01) bessere Codequalität als YOLO-Prompting, braucht aber deutlich mehr Zeit.

## Setup

### Tools
- Cursor (Version: aktuell, April 2026)
- Claude Sonnet als Modell

### Aufgabe
[Challenge 01: REST-API von Grund auf](../../benchmarks/challenges/01-rest-api.md)

### Durchgang A: YOLO-Prompting

**Prompt:**
```
Bau mir eine REST-API für einen Task Manager. 
Node.js, TypeScript, SQLite. CRUD für Tasks und Projekte.
Tasks gehören zu Projekten. Filtering und Pagination. 
Tests nicht vergessen.
```

### Durchgang B: Spec-First Vibe

**Schritt 1 – Spec:**
```
Erstelle eine technische Spezifikation für eine Task-Manager REST-API:
- CRUD für Tasks (title, description, status, priority, dueDate)
- CRUD für Projekte (name, description)
- Tasks gehören zu Projekten (1:N)
- Filtern nach Status und Priorität
- Pagination für Listen-Endpoints
- Tech: Node.js, Express, TypeScript, Prisma, SQLite
- Input-Validierung mit Zod
- Sinnvolle HTTP-Status-Codes
```

**Schritt 2 – Review:**
```
Reviewe die Spec und ergänze fehlende Edge Cases.
```

**Schritt 3 – Implementation:**
```
Implementiere die API basierend auf der Spec. Alle Dateien.
```

**Schritt 4 – Tests:**
```
Schreibe Tests für alle Endpoints basierend auf der Spec.
```

## Ergebnis

### Durchgang A: YOLO-Prompting

| Dimension | Score | Kommentar |
|-----------|:-----:|-----------|
| ⏱️ Geschwindigkeit | 5/5 | Alles in einem Prompt, ~3 Minuten |
| 🎯 Treffsicherheit | 3/5 | 80% funktionierte, Pagination fehlte |
| 🏗️ Codequalität | 2/5 | Funktional, aber keine klare Struktur |
| 🔄 Iterationsfähigkeit | 2/5 | Schwer einzelne Teile zu ändern |
| 🧠 Kognitive Last | 4/5 | Kaum Denkarbeit nötig |

**Zeit**: ~8 Minuten (inkl. 2 Korrektur-Iterationen)

### Durchgang B: Spec-First Vibe

| Dimension | Score | Kommentar |
|-----------|:-----:|-----------|
| ⏱️ Geschwindigkeit | 3/5 | 4 Schritte, jeweils 3-5 Minuten |
| 🎯 Treffsicherheit | 5/5 | Alle Anforderungen erfüllt |
| 🏗️ Codequalität | 4/5 | Saubere Struktur, klare Trennung |
| 🔄 Iterationsfähigkeit | 4/5 | Einzelne Module leicht anpassbar |
| 🧠 Kognitive Last | 3/5 | Spec-Erstellung erforderte Nachdenken |

**Zeit**: ~20 Minuten

## Learnings

1. **YOLO ist 2.5x schneller** – aber mit deutlich mehr Rework-Bedarf
2. **Spec-First liefert konsistentere Qualität** – weniger Überraschungen
3. **Die Spec ist wiederverwendbar** – für Dokumentation und zukünftige Iterationen
4. **YOLO vergisst Edge Cases** – Pagination, Validierung, Error Handling oft lückenhaft
5. **Für MVPs ist YOLO gut genug** – wenn man den Code nicht lange pflegen muss

## Nächste Schritte

- [ ] Gleiches Experiment mit TDD-Vibe durchführen
- [ ] Experiment mit Challenge 03 (Refactoring) wiederholen
- [ ] Langzeit-Vergleich: Wie viel Rework braucht YOLO-Code nach 1 Woche?
