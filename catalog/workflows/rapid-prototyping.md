---
name: "Von Idee zu MVP in 2 Stunden"
category: workflow
maturity: experimental
tools: [cursor, claude-code]
synergies: [guided-yolo, full-auto-generation, prompt-chaining]
anti-synergies: []
complexity: medium
speed_boost: "10x"
quality_impact: "neutral"
tags: [mvp, prototyping, speed, workflow, full-stack]
last_tested: 2026-04-01
---

# 🚀 Von Idee zu MVP in 2 Stunden

## Beschreibung

Ein systematischer Workflow, der eine vage Idee in ein funktionierendes MVP verwandelt – in maximal 2 Stunden. Nutzt eine Kombination aus KI-gestützter Planung und aggressiver Code-Generierung.

## Der Workflow

### Phase 1: Ideation (15 Min)

```
Prompt an die KI:
"Ich habe folgende Produktidee: [IDEE]

Hilf mir die Idee zu schärfen:
1. Was ist der Kern-Use-Case?
2. Was ist das absolute Minimum für ein funktionierendes MVP?
3. Welche Features sind nice-to-have und kommen NICHT ins MVP?
4. Welcher Tech-Stack ist am schnellsten zu implementieren?"
```

### Phase 2: Spec (15 Min)

```
"Basierend auf unserer Diskussion, erstelle eine MVP-Spec:
- User Stories (max 3-5)
- Datenmodell
- UI-Skizze (Textbeschreibung der Seiten)
- API-Endpoints (falls Backend nötig)
- Tech-Stack-Entscheidung"
```

### Phase 3: Scaffolding (15 Min)

```
"Erstelle das komplette Projekt-Scaffold:
- Projektstruktur
- Alle Config-Dateien
- Basis-Setup mit gewähltem Tech-Stack
- Leere Komponenten/Module als Platzhalter"
```

### Phase 4: Core Implementation (45 Min)

```
"Implementiere die Kern-Features in dieser Reihenfolge:
1. [Feature 1 – User Story 1]
2. [Feature 2 – User Story 2]
3. [Feature 3 – User Story 3]"
```

### Phase 5: Polish & Deploy (30 Min)

```
"1. Füge grundlegendes Error Handling hinzu
2. Mache die UI halbwegs ansehnlich
3. Erstelle ein Docker Compose Setup oder Deployment-Config
4. Schreibe eine README mit Setup-Anleitung"
```

## Tipps

- **Nicht perfektionieren** – es ist ein MVP, kein Produktionscode
- **Ein Tech-Stack, den man kennt** – keine Zeit für Lernkurven
- **Scope gnadenlos kürzen** – alles was "nice-to-have" ist, fliegt raus
- **KI für Boilerplate nutzen** – eigene Energie für Kernlogik sparen
- **Timer setzen** – 2 Stunden sind 2 Stunden

## Bewertung

| Dimension | Score | Kommentar |
|-----------|:-----:|-----------|
| ⏱️ Geschwindigkeit | 5/5 | Maximale Geschwindigkeit ist das Ziel |
| 🎯 Treffsicherheit | 3/5 | MVP-Qualität, nicht Perfektion |
| 🏗️ Codequalität | 2/5 | Bewusst niedrig für Geschwindigkeit |
| 🔄 Iterationsfähigkeit | 3/5 | Scaffold ist ausbaubar |
| 🧠 Kognitive Last | 3/5 | Timer-Druck erhöht Last |
| 📐 Skalierbarkeit | 2/5 | MVP skaliert selten |
| 🎨 Kreativität | 4/5 | Zeitdruck erzwingt kreative Lösungen |
