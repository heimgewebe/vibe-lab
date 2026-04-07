# 🔗 Chain-Template: Feature Development

Eine Multi-Step-Prompt-Kette für die systematische Feature-Entwicklung.

## Übersicht

```
Schritt 1: Anforderungsanalyse
     ↓
Schritt 2: Technisches Design
     ↓
Schritt 3: Implementation
     ↓
Schritt 4: Tests
     ↓
Schritt 5: Review & Refinement
```

## Die Kette

### Prompt 1: Anforderungsanalyse

```
Analysiere folgende Feature-Anforderung:
[FEATURE-BESCHREIBUNG]

Erstelle:
1. User Stories (Als [Rolle] möchte ich [Funktion] damit [Nutzen])
2. Akzeptanzkriterien für jede User Story
3. Edge Cases und Sonderfälle
4. Offene Fragen (falls vorhanden)

Format: Strukturierte Markdown-Liste
```

### Prompt 2: Technisches Design

```
Basierend auf dieser Anforderungsanalyse:
[OUTPUT VON PROMPT 1]

Und unserem bestehenden Tech-Stack:
[TECH-STACK-BESCHREIBUNG ODER REFERENZ]

Erstelle ein technisches Design:
1. Betroffene Komponenten (neue und bestehende)
2. Datenmodell-Änderungen
3. API-Änderungen
4. Abhängigkeiten und Reihenfolge der Implementation
```

### Prompt 3: Implementation

```
Basierend auf diesem technischen Design:
[OUTPUT VON PROMPT 2]

Implementiere die Änderungen in dieser Reihenfolge:
[REIHENFOLGE AUS PROMPT 2]

Beachte unsere Code-Konventionen:
[KONVENTIONEN ODER REFERENZ]
```

### Prompt 4: Tests

```
Basierend auf den Akzeptanzkriterien:
[KRITERIEN AUS PROMPT 1]

Und der Implementation:
[OUTPUT VON PROMPT 3]

Schreibe Tests, die:
1. Jeden Akzeptanzfall abdecken
2. Alle identifizierten Edge Cases testen
3. Zu unserem bestehenden Test-Framework passen
```

### Prompt 5: Review & Refinement

```
Reviewe die gesamte Implementation:
[ALLE BISHERIGEN OUTPUTS]

Prüfe:
1. Erfüllt die Implementation alle Akzeptanzkriterien?
2. Gibt es Security-Bedenken?
3. Gibt es Performance-Bedenken?
4. Ist der Code wartbar und verständlich?
5. Fehlen Tests?

Gib konkretes Feedback und Verbesserungsvorschläge.
```

## Tipps

- Jeden Schritt **validieren** bevor man zum nächsten geht
- **Kontext mitgeben** – Outputs der vorherigen Schritte referenzieren
- Bei Bedarf **Schritte wiederholen** – z.B. Prompt 3 nach Feedback aus Prompt 5
