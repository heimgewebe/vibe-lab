---
title: "Experiment-Methode: Upfront Structuring"
status: testing
canonicality: operative
---

# method.md — Experiment-Methode

> Beschreibt das strukturierte Vorgehen zur Prüfung der Hypothese.

## Hypothese

Explizite Vorstrukturierung vor Implementierung (wie Spec-First oder Test-First) erhöht die Robustheit logiklastiger Agentenarbeit signifikant gegenüber dem direkten Codieren (Code-First). TDD (Test-First) ist lediglich eine spezifische, ausführbare Form dieser Vorstrukturierung.

## Methode

### Vorgehen

1. **Setup:** Python-Umgebung in `artifacts/` vorbereiten.
2. **Arm 1 (Code-First):** Daten aus Vorstudie `2026-04-14_tdd-vibe` übernehmen.
3. **Arm 2 (Spec-First):** Modell auffordern, erst eine Regel-Spezifikation und dann den Code (inkl. Tests) zu generieren. Tests ausführen, Resultate loggen.
4. **Arm 3 (Test-First):** Daten aus Vorstudie `2026-04-14_tdd-vibe` übernehmen.
5. **Beobachtungen:** Ergebnisse, Testabdeckung, Fehler und Erfolge aller drei Arme in `evidence.jsonl` festhalten.

### Metriken

- Test-Pass-Rate beim ersten Run (First-Shot Success).
- Zahl übersehener Edge-Cases (z.B. "IIII", "VV", "IC").
- Qualität der Fehlerbehandlung (Robuste vs. naive Regex/Logik).

### Erfolgskriterien

Die Hypothese gilt als bestätigt, wenn Spec-First ähnlich gute Robustheits- und Edge-Case-Ergebnisse liefert wie Test-First, und beide signifikant besser abschneiden als Code-First.

## Variablen

| Variable              | Beschreibung                    | Kontrolle / Treatment |
| --------------------- | ------------------------------- | --------------------- |
| Prompt-Strategie      | Art der Vorstrukturierung       | Unabhängige Variable (Code/Spec/Test) |
| Test-Pass-Rate        | Erfolgsquote initialer Tests    | Abhängige Variable |
| Edge-Case Misses      | Anzahl nicht abgefangener Fehler| Abhängige Variable |

## Risiken und Einschränkungen

Das Modell könnte bei Spec-First die Spezifikation zwar gut schreiben, sie aber bei der Code-Generierung im selben Prompt ignorieren.
