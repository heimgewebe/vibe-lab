---
name: "Incremental Refinement"
category: style
maturity: proven
tools: [cursor, claude-code, copilot, aider]
synergies: [chain-of-thought, pair-programming-mit-ki, tdd-vibe]
anti-synergies: [full-auto-generation]
complexity: medium
speed_boost: "3x"
quality_impact: "++"
tags: [iterative, refinement, production, systematic]
last_tested: 2026-04-01
---

# 🔄 Incremental Refinement

## Beschreibung

Incremental Refinement folgt dem Prinzip **"Klein anfangen, schrittweise verbessern"**. Statt alles auf einmal zu generieren, wird in kleinen, kontrollierten Schritten gearbeitet. Jeder Schritt baut auf dem vorherigen auf und wird validiert, bevor der nächste beginnt.

## Wie es funktioniert

1. **Minimale Version**: Lass die KI die einfachste funktionierende Version erstellen
2. **Validieren**: Prüfen, ob die Basis stimmt
3. **Nächstes Feature**: Ein Feature/Aspekt hinzufügen
4. **Validieren**: Erneut prüfen
5. **Wiederholen**: Bis das gewünschte Ergebnis erreicht ist

## Beispiel

```
Schritt 1: "Erstelle eine Express-App die auf GET / mit 'Hello World' antwortet."
Schritt 2: "Füge eine PostgreSQL-Verbindung mit Prisma hinzu."
Schritt 3: "Erstelle ein User-Model mit name und email."
Schritt 4: "Füge CRUD-Endpoints für Users hinzu."
Schritt 5: "Füge Input-Validierung mit Zod hinzu."
Schritt 6: "Füge JWT-Authentication hinzu."
Schritt 7: "Schreibe Tests für alle Endpoints."
```

## Wann einsetzen?

- ✅ Komplexe Features mit vielen Abhängigkeiten
- ✅ Wenn man den Code verstehen will
- ✅ Produktionscode mit hohen Qualitätsansprüchen
- ✅ Brownfield-Projekte (Integration in bestehenden Code)
- ❌ Einfache, klar definierte Aufgaben
- ❌ Wenn die Geschwindigkeit das höchste Gut ist

## Stärken

- **Hohe Kontrolle** – jeder Schritt wird validiert
- **Debugging-freundlich** – Fehler sind leicht lokalisierbar
- **Gute Codequalität** – schrittweiser Aufbau erzeugt saubere Struktur
- **Flexibel** – man kann jederzeit die Richtung ändern
- **Lerneffekt** – man versteht den gesamten Code

## Schwächen

- **Langsamer als Full-Auto** – mehr Iterationen nötig
- **Erfordert Planung** – man muss die Schritte sinnvoll wählen
- **KI-Kontext kann verloren gehen** – bei vielen Schritten

## Bewertung

| Dimension | Score | Kommentar |
|-----------|:-----:|-----------|
| ⏱️ Geschwindigkeit | 3/5 | Moderate Geschwindigkeit, aber weniger Rework |
| 🎯 Treffsicherheit | 4/5 | Kleine Schritte = hohe Genauigkeit |
| 🏗️ Codequalität | 4/5 | Saubere, schrittweise aufgebaute Struktur |
| 🔄 Iterationsfähigkeit | 5/5 | Der Stil IST Iteration |
| 🧠 Kognitive Last | 3/5 | Planung der Schritte erfordert Nachdenken |
| 📐 Skalierbarkeit | 4/5 | Gut auch für große Projekte |
| 🎨 Kreativität | 3/5 | Solide, aber nicht besonders kreativ |

## Verwandte Einträge

- **Synergie**: [Chain-of-Thought](../techniques/chain-of-thought.md)
- **Synergie**: [TDD-Vibe](tdd-vibe.md)
- **Gegensatz**: [Full-Auto Generation](full-auto-generation.md)
