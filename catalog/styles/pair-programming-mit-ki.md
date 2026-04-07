---
name: "Pair-Programming mit KI"
category: style
maturity: proven
tools: [cursor, copilot, claude-code, windsurf]
synergies: [rubber-duck-prompting, chain-of-thought, incremental-building]
anti-synergies: [full-auto-generation]
complexity: low
speed_boost: "3x"
quality_impact: "+"
tags: [collaboration, interactive, learning, pair-programming]
last_tested: 2026-04-01
---

# 👥 Pair-Programming mit KI

## Beschreibung

Statt die KI den gesamten Code generieren zu lassen, arbeitet man **interaktiv und Zeile für Zeile** zusammen – wie beim klassischen Pair Programming, nur dass der Partner eine KI ist. Der Mensch bleibt im Driver-Seat.

## Wie es funktioniert

1. **Mensch denkt und plant**: Die grobe Richtung vorgeben
2. **KI ergänzt**: Autocomplete, Vorschläge, Implementierungsdetails
3. **Mensch reviewed**: Jeden Vorschlag prüfen und ggf. anpassen
4. **Dialog**: Bei Unklarheiten direkt nachfragen
5. **Iterieren**: Kleinteilig vorwärts arbeiten

## Beispiel

```
Mensch: "Ich brauche eine Funktion die eine Liste von Users nach Rolle filtert."
KI: [schlägt Implementation vor]
Mensch: "Gut, aber füge noch Pagination hinzu. Und mach die Rolle case-insensitive."
KI: [passt an]
Mensch: "Jetzt noch Error Handling für ungültige Rollen."
KI: [ergänzt]
```

## Wann einsetzen?

- ✅ Alltägliche Entwicklungsarbeit
- ✅ Wenn man den Code verstehen will
- ✅ Zum Lernen neuer Technologien
- ✅ Komplexe Logik, die schrittweise aufgebaut wird
- ❌ Wenn Geschwindigkeit oberste Priorität hat
- ❌ Für repetitive, klar definierte Aufgaben
- ❌ Boilerplate-Generierung

## Stärken

- **Hohes Verständnis** – man versteht jeden generierten Code
- **Hohe Kontrolle** – jeder Schritt wird validiert
- **Natürlicher Workflow** – fühlt sich an wie echtes Pair Programming
- **Lerneffekt** – man lernt von den KI-Vorschlägen
- **Fehler werden früh erkannt**

## Schwächen

- **Langsamer als Vollautomatisierung** – menschlicher Review-Overhead
- **Abhängig von IDE-Integration** – funktioniert am besten in Cursor/Copilot
- **Kann ermüdend sein** – ständiges Review erfordert Konzentration

## Bewertung

| Dimension | Score | Kommentar |
|-----------|:-----:|-----------|
| ⏱️ Geschwindigkeit | 3/5 | Schneller als manuell, langsamer als YOLO |
| 🎯 Treffsicherheit | 4/5 | Hohe Kontrolle = hohe Treffsicherheit |
| 🏗️ Codequalität | 4/5 | Durch Review wird Qualität sichergestellt |
| 🔄 Iterationsfähigkeit | 4/5 | Natürlich iterativ |
| 🧠 Kognitive Last | 3/5 | Erfordert ständige Aufmerksamkeit |
| 📐 Skalierbarkeit | 3/5 | Gut für mittlere Projekte |
| 🎨 Kreativität | 3/5 | KI-Vorschläge können inspirieren |

## Verwandte Einträge

- **Synergie**: [Rubber-Duck-Prompting](../techniques/rubber-duck-prompting.md)
- **Gegensatz**: [Full-Auto Generation](full-auto-generation.md)
