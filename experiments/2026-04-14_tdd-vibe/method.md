---
title: "Experiment-Methode: TDD Vibe"
status: inconclusive
canonicality: operative
---

# method.md — Experiment-Methode

> Beschreibt das strukturierte Vorgehen zur Prüfung der Hypothese.

## Hypothese

Test-Driven Development im Vibe-Coding-Kontext (erst Tests, dann Code generieren lassen) führt zu robusterem Code und weniger Iterationen für Fehlerbehebungen im Vergleich zum direkten Generieren von Code (Code-First), insbesondere bei komplexen Edge-Cases.

## Methode

### Vorgehen

1. **Setup:** Python-Umgebung mit `pytest` in `artifacts/` vorbereiten.
2. **Kontrolle (Code-First):** Den Baseline Prompt an das Modell übergeben. Den Output (Code + Tests) speichern. Ausführen und prüfen, ob alle Edge-Cases abgedeckt sind und die Tests grün sind. Falls nicht, Anzahl der benötigten Iterationen notieren.
3. **Treatment (TDD Vibe):** Den Treatment Prompt an das Modell übergeben (erst Tests, dann Implementierung in einem Durchgang, aber logisch getrennt). Den Output speichern. Ausführen und prüfen.
4. **Beobachtungen:** Ergebnisse, Testabdeckung, Fehler und Erfolge in `evidence.jsonl` festhalten.

### Metriken

- Wirksamkeit: Anzahl der initial erkannten und korrekt abgefangenen Edge-Cases (z.B. "IIII", "VV", "IC").
- Reibung: Anzahl der Prompts / Iterationen, bis ein valider, grüner Testlauf für alle Edge-Cases erreicht ist.
- Code-Qualität: Subjektive Beurteilung der Test-Vollständigkeit und Klarheit der Implementierung.

### Erfolgskriterien

Die Hypothese gilt als bestätigt, wenn der TDD Vibe Ansatz out-of-the-box (oder mit signifikant weniger Iterationen) eine höhere Edge-Case-Abdeckung und fehlerfreie Testläufe erzielt als der Code-First Ansatz.

## Variablen

| Variable              | Beschreibung                    | Kontrolle / Treatment |
| --------------------- | ------------------------------- | --------------------- |
| Prompt-Struktur       | Reihenfolge der Anweisungen     | Code -> Tests vs. Tests -> Code |
| Edge-Case Coverage    | Anteil abgedeckter Fehlerfälle  | Abhängige Variable |
| Iterationen           | Zahl der Fixes bis 'grün'       | Abhängige Variable |

## Risiken und Einschränkungen

Das Modell könnte beim TDD-Vibe Prompt in Schritt 1 stecken bleiben oder den Kontext für Schritt 2 verlieren. Wir verlangen beides in einem Prompt, um die Latenz gering zu halten. Falls dies scheitert, muss es auf zwei separate Prompts aufgeteilt werden (was dem wahren TDD-Spirit näher käme, aber mehr Friction bedeutet).
