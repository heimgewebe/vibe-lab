---
name: "Guided YOLO"
category: style
maturity: experimental
tools: [cursor, claude-code, copilot, chatgpt]
synergies: [yolo-prompting, context-stuffing, prompt-priming]
anti-synergies: []
complexity: low
speed_boost: "4x"
quality_impact: "+"
tags: [prompting, speed, guided, balanced]
last_tested: 2026-04-01
---

# 🎯 Guided YOLO

## Beschreibung

Guided YOLO ist die **evolutionäre Weiterentwicklung von YOLO-Prompting**: Man behält die Geschwindigkeit und Spontaneität, fügt aber **leichte Leitplanken** hinzu. Statt völlig freiem Prompting gibt man der KI minimale Constraints mit auf den Weg.

## Wie es funktioniert

1. **Schnelles Briefing** (2-3 Sätze): Was soll gebaut werden?
2. **Leitplanken setzen** (1-2 Sätze): Welche Technologien, welcher Stil?
3. **Generieren lassen**: Output anschauen
4. **Gezieltes Nachbessern**: Spezifische Punkte korrigieren

## Beispiel

```
"Baue eine Todo-App mit React und Tailwind.
Leitplanken: TypeScript strict, Zustand für State, 
Komponentenstruktur: feature-basiert, keine inline-Styles."
```

Vs. reines YOLO:
```
"Baue eine Todo-App"
```

## Wann einsetzen?

- ✅ Wenn YOLO zu chaotisch wird, aber Spec-First zu langsam ist
- ✅ Prototypen, die vielleicht doch zu Produktionscode werden
- ✅ Wenn man klare Tech-Präferenzen hat
- ✅ Für erfahrene Entwickler, die ihre Standards kennen
- ❌ Sicherheitskritischer Code
- ❌ Wenn Anforderungen komplex und detailliert sind

## Stärken

- **Fast so schnell wie YOLO** – minimaler Overhead
- **Deutlich bessere Qualität** – Leitplanken verhindern die gröbsten Fehler
- **Einfach zu lernen** – nur wenige Regeln
- **Flexible** – Leitplanken können pro Aufgabe variieren

## Schwächen

- **Subjektiv** – welche Leitplanken sind die richtigen?
- **Falsche Sicherheit** – man denkt der Code ist besser als er ist
- **Erfordert Erfahrung** – man muss wissen, welche Leitplanken wichtig sind

## Bewertung

| Dimension | Score | Kommentar |
|-----------|:-----:|-----------|
| ⏱️ Geschwindigkeit | 4/5 | Fast so schnell wie reines YOLO |
| 🎯 Treffsicherheit | 3/5 | Deutlich besser als YOLO |
| 🏗️ Codequalität | 3/5 | Leitplanken verbessern die Qualität |
| 🔄 Iterationsfähigkeit | 3/5 | Besser als YOLO, da Constraints bleiben |
| 🧠 Kognitive Last | 4/5 | Minimal mehr Denkarbeit als YOLO |
| 📐 Skalierbarkeit | 2/5 | Für kleine bis mittlere Aufgaben |
| 🎨 Kreativität | 4/5 | Constraints können Kreativität sogar fördern |

## Verwandte Einträge

- **Basis**: [YOLO-Prompting](yolo-prompting.md)
- **Nächste Stufe**: [Spec-First Vibe](spec-first-vibe.md)
