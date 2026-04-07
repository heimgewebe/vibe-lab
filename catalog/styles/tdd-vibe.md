---
name: "TDD-Vibe"
category: style
maturity: proven
tools: [cursor, claude-code, aider, copilot]
synergies: [spec-first-vibe, chain-of-thought, red-green-refactor]
anti-synergies: [yolo-prompting]
complexity: medium
speed_boost: "2x"
quality_impact: "+++"
tags: [testing, tdd, quality, production, methodology]
last_tested: 2026-04-01
---

# 🧪 TDD-Vibe

## Beschreibung

TDD-Vibe überträgt Test-Driven Development in die Vibe-Coding-Welt: **Zuerst die Tests schreiben (oder schreiben lassen), dann den Code generieren lassen, der die Tests bestehen muss.** Die Tests dienen als ausführbare Spezifikation.

## Wie es funktioniert

1. **Tests definieren**: Beschreibe die gewünschten Tests oder lass sie generieren
2. **Red Phase**: Stelle sicher, dass die Tests fehlschlagen
3. **Green Phase**: Lass die KI Code schreiben, der die Tests besteht
4. **Refactor Phase**: Lass die KI den Code verbessern (Tests müssen weiter bestehen)

## Beispiel

```
Schritt 1 – Tests generieren:
"Schreibe mir Tests für eine Funktion `parseCSV(input: string): Row[]` 
die folgende Fälle abdeckt:
- Normales CSV mit Header
- Leere Eingabe → leeres Array
- Felder mit Kommas in Anführungszeichen
- Fehlende Felder → null-Werte
- Unicode-Zeichen"

Schritt 2 – Implementation:
"Implementiere die Funktion `parseCSV` so, dass alle Tests bestehen."

Schritt 3 – Refactor:
"Refactore die Implementation für bessere Lesbarkeit und Performance.
Alle Tests müssen weiterhin bestehen."
```

## Wann einsetzen?

- ✅ Funktionen mit klarem Input/Output
- ✅ Businesslogik und Datenverarbeitung
- ✅ Sicherheitskritischer Code
- ✅ Bibliotheken und wiederverwendbare Module
- ❌ UI/Frontend-Entwicklung (schwerer testbar)
- ❌ Explorative Prototypen
- ❌ Einmal-Skripte

## Stärken

- **Höchste Codequalität** – Tests erzwingen Korrektheit
- **Regressionssicher** – Änderungen werden sofort validiert
- **Klare Konversation** – Tests sind eine universelle Sprache
- **Selbstdokumentierend** – Tests beschreiben das Verhalten
- **Ideal für Iteration** – "Füge diesen Test hinzu, passe den Code an"

## Schwächen

- **Höherer Aufwand** – Tests schreiben dauert
- **Schwierig bei vagen Anforderungen** – man muss wissen, was man will
- **Test-Qualität entscheidend** – schlechte Tests = schlechter Code
- **Nicht für alles geeignet** – UI, Integrationen, Infrastruktur

## Bewertung

| Dimension | Score | Kommentar |
|-----------|:-----:|-----------|
| ⏱️ Geschwindigkeit | 2/5 | Langsamer durch Test-Erstellung |
| 🎯 Treffsicherheit | 5/5 | Tests erzwingen Korrektheit |
| 🏗️ Codequalität | 5/5 | Beste Qualität aller Stile |
| 🔄 Iterationsfähigkeit | 5/5 | Neue Tests → neue Iteration |
| 🧠 Kognitive Last | 3/5 | Test-Design erfordert Nachdenken |
| 📐 Skalierbarkeit | 4/5 | Gut, wenn Test-Suite mitwächst |
| 🎨 Kreativität | 2/5 | Tests schränken Lösungsraum ein |

## Verwandte Einträge

- **Synergie**: [Spec-First Vibe](spec-first-vibe.md)
- **Synergie**: [Chain-of-Thought](../techniques/chain-of-thought.md)
- **Gegensatz**: [YOLO-Prompting](yolo-prompting.md)
