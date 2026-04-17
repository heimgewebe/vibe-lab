---
title: "Ergebnisse: Prompt-Length Control"
status: adopted
canonicality: operative
validates:
  - "../../../catalog/techniques/spec-first-prompting.md"
---

# result.md — Experiment-Ergebnisse

> **Kausale Kontrollstudie.** Entkoppelt Tokenlänge von Struktur.

## Zusammenfassung der Ergebnisse

Um sicherzustellen, dass die Erfolge von Spec-First und Test-First (Upfront Structuring) nicht nur ein Artefakt davon sind, dass das LLM mehr Tokens produziert (und sich so implizit mehr Zeit für "Chain of Thought" nimmt), wurde eine Kontrollstudie an einem Text-Parsing-Task durchgeführt.

1. **Code-First:** Naives Regex, verpasst escapete Constraints am Wortende (1 Fehler).
2. **Spec-First:** Vorab spezifizierte Fehlerregeln, führte zu robusten Lookbehinds (0 Fehler).
3. **Ramble-First:** Das Modell wurde gezwungen, vorab einen irrelevanten Essay (historischer Kontext) auszugeben, bevor es Code schrieb. Das Token-Volumen war hoch (wie bei Spec-First). Es fiel jedoch exakt in denselben Naiv-Regex-Fehler wie Code-First zurück (1 Fehler).

## Datenpunkte (Evidence)

Siehe `evidence.jsonl`:
- `test_pass_rate_code_first`: 0.8
- `test_pass_rate_spec_first`: 1.0
- `test_pass_rate_ramble_first`: 0.8

## Erkenntnisse

1. **Struktur vs. Token-Volumen:** Der Leistungszugewinn von Upfront Structuring beruht **nicht** auf bloßer Output-Verzögerung oder Chain-of-Thought-Proxy-Effekten.
2. **Kognitiver Modus:** Der Effekt beruht tatsächlich auf dem Wechsel in einen `declarative` (oder `executable`) Modus: Das Modell muss *Constraints aktiv formulieren*, um bei der anschließenden Code-Generierung darauf konditioniert zu sein.

## Entscheidung

**Urteil:** Adopt (Hypothese bestätigt).
**Begründung:** Diese Studie schließt die wichtigste kausale Erklärungslücke der vorangegangenen Experimente (`tdd-vibe`, `upfront-structuring`). Es belegt, dass Spec-First/Test-First als echte epistemologische Werkzeuge wirken, die das Modellverhalten verändern, und nicht nur als Prompt-Hacks, die das Kontextfenster strecken. Damit ist die theoretische Basis für `catalog/techniques/spec-first-prompting.md` massiv gehärtet.

## Nächste Schritte

- Weiterer Ausbau der Cognitive-Modes-Theorie im Projekt.

## Interpretation Budget

### Allowed Claims
- Der Leistungszugewinn von Spec-First beruht nicht auf Token-Volumen oder Chain-of-Thought-Proxy-Effekten (kausaler Kontrollbeweis für diesen Task und dieses Modell).
- Der Wechsel in einen deklarativen/ausführbaren Modus (aktives Formulieren von Constraints) ist der kausale Mechanismus für den Spec-First-Effekt bei diesem Task.
- Ramble-First (hohes Token-Volumen ohne Struktur) bringt keinen Vorteil gegenüber Code-First.

### Disallowed Claims
- Dieser Befund gilt für alle Task-Typen – er basiert auf einem einzelnen Text-Parsing-Task.
- Die Theorie der Cognitive Modes ist damit vollständig bewiesen – sie ist gestützt, aber nicht erschöpfend getestet.
- Das Ergebnis gilt modellübergreifend – nur ein LLM wurde getestet.
- Token-Volumen ist niemals relevant – der Befund gilt spezifisch für die getestete Aufgabenklasse.

### Evidence Basis
- Direkt beobachtet: test_pass_rate für Code-First (0.8), Spec-First (1.0), Ramble-First (0.8) an einem Text-Parsing-Task
- Indirekt gestützt: Konvergiert mit Beobachtungen aus 2026-04-08_spec-first und 2026-04-14_upfront-structuring
- Nicht getestet: Andere Task-Typen, andere Modelle, multi-step Tasks, Teams
