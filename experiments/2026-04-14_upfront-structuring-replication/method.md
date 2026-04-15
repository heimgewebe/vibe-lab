---
title: "Experiment-Methode: Upfront Structuring Replication"
status: testing
canonicality: operative
---

# method.md — Experiment-Methode

> Beschreibt das strukturierte Vorgehen zur Prüfung der Hypothese.

## Hypothese

Explizite Vorstrukturierung (Spec-First oder Test-First) vor der Code-Generierung führt im Vergleich zu Code-First replizierbar zu höherer Robustheit bei der Fehlerbehandlung in logiklastigen Aufgaben.

## Methode

### Vorgehen

1. **Setup:** Python-Umgebung in `artifacts/` vorbereiten.
2. **Arm 1 (Code-First):** LLM-Output für direkten Code simulieren/ausführen. Tests schreiben und ausführen, Resultate loggen.
3. **Arm 2 (Spec-First):** Modell auffordern, erst eine Regel-Spezifikation und dann den Code zu generieren. Tests schreiben/ausführen, Resultate loggen.
4. **Arm 3 (Test-First):** Modell auffordern, erst Tests und dann Code zu generieren. Tests ausführen, Resultate loggen.
5. **Beobachtungen:** Alle Resultate von Null an neu erzeugen und in `evidence.jsonl` loggen.

### Metriken

- Zahl verpasster Constraints im ersten Versuch.
- Qualität der Fehlerbehandlung (Robuste Typprüfung und bedingte Logik).

### Erfolgskriterien

Die Replikation ist erfolgreich, wenn bei einem komplett neuen Task (Validator statt Roman Numerals) die Arme `spec-first` und `test-first` die bedingten und typspezifischen Constraints signifikant besser im ersten Versuch abfangen als der naive `code-first` Arm.

## Variablen

| Variable              | Beschreibung                    | Kontrolle / Treatment |
| --------------------- | ------------------------------- | --------------------- |
| Prompt-Strategie      | Art der Vorstrukturierung       | Unabhängige Variable (Code/Spec/Test) |
| Missed Constraints    | Anzahl übersehener Fehlerfälle  | Abhängige Variable |
