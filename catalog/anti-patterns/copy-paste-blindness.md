---
name: "Copy-Paste-Blindness"
category: anti-pattern
maturity: proven
tools: [cursor, claude-code, copilot, chatgpt, aider]
synergies: []
anti-synergies: []
complexity: low
speed_boost: "-2x"
quality_impact: "---"
tags: [anti-pattern, quality, review, universal]
last_tested: 2026-04-01
---

# 🚫 Copy-Paste-Blindness

## Was ist es?

Den generierten Code **blind akzeptieren und einfügen**, ohne ihn zu lesen, zu verstehen oder zu testen. Man vertraut der KI vollständig und merkt nicht, dass der Code fehlerhaft, unsicher oder unpassend ist.

## Symptome

- Bugs in Production, die beim Lesen sofort aufgefallen wären
- Sicherheitslücken durch ungeprüfte KI-Vorschläge
- Code, der nicht zum Projekt-Stil passt
- Duplizierter Code, weil die KI bestehende Funktionen nicht kennt
- "Es hat bei der KI funktioniert" als Erklärung für kaputten Code

## Warum passiert es?

- **Zeitdruck** – keine Zeit zum Review
- **Übermäßiges Vertrauen** – "Die KI wird schon wissen was sie tut"
- **Kognitive Faulheit** – Review ist anstrengend
- **Fehlende Expertise** – man erkennt die Fehler nicht

## Wie vermeiden?

### ✅ Immer lesen
Jeden generierten Code mindestens einmal durchlesen.

### ✅ Tests schreiben (oder schreiben lassen)
TDD-Vibe: Tests VORHER schreiben, dann generieren lassen.

### ✅ Erklären lassen
"Erkläre mir was dieser Code tut und warum du dich so entschieden hast."

### ✅ Diff-Review
In Cursor/IDE: Diff anschauen bevor man Accept klickt.

### ✅ Security-Check
Bei sicherheitsrelevantem Code: Explizit nach Schwachstellen fragen.

## Schweregrad: 🔴 Hoch

Dieses Anti-Pattern untergräbt den gesamten Wert von Vibe-Coding. Code, den man nicht versteht, sollte man nicht deployen.
