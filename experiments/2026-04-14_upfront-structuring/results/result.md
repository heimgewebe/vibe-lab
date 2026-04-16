---
title: "Ergebnisse: Upfront Structuring Comparison (Zwischenstand)"
status: testing
canonicality: operative
document_role: experiment
---

# result.md — Experiment-Ergebnisse

> **Anschlussanalyse.** Vergleicht Strukturierungsansätze, verwendet asymmetrische Datenbasis.

## Zusammenfassung der Ergebnisse

Das Experiment entflechtet die Erkenntnisse der Vorstudie `2026-04-14_tdd-vibe`. Es wurden drei Strategien bei der Implementierung einer logiklastigen Funktion (`roman_to_int`) verglichen. **Achtung: Dies ist ein asymmetrischer Vergleich.** Die Daten für Code-First und Test-First stammen aus der Vorstudie, nur Spec-First wurde neu ausgeführt.

1. **Code-First:** (Daten aus Vorstudie) Naives Prompting. Führt zu funktionierendem Happy-Path, verfehlt aber 3 komplexe Edge-Cases im ersten Versuch.
2. **Test-First (TDD):** (Daten aus Vorstudie) Tests vor Code generiert. Führt zu 0 verfehlten Edge-Cases im ersten Versuch.
3. **Spec-First:** Textuelle Spezifikation der Fehlerregeln vor Code generiert. Führt ebenfalls zu 0 verfehlten Edge-Cases im ersten Versuch.

## Datenpunkte (Evidence)

Siehe `evidence.jsonl`:
- `test_pass_rate` (Spec-First): 1.0 (100% im ersten Lauf)
- `edge_cases_missed_code_first`: 3
- `edge_cases_missed_test_first`: 0
- `edge_cases_missed_spec_first`: 0

## Erkenntnisse

1. **Strukturierung ist ein starker Indikator:** Der Performance-Gewinn von TDD (Test-First) gegenüber Code-First scheint primär auf die Tatsache zurückzugehen, dass das Modell das Problem *vor der Implementierung* explizit durchdenken muss.
2. **Methodenvergleich:** Ob dieses "Durchdenken" als ausführbare Tests (Test-First) oder als textuelle Constraint-Spezifikation (Spec-First) erfolgt, macht im reinen *First-Shot-Success* bei diesem speziellen Task keinen Unterschied.

## Entscheidung

**Urteil:** Testing (Als vergleichende Anschlussanalyse markiert)
**Begründung:** Der Befund liefert ein starkes Indiz dafür, dass Upfront Structuring der eigentliche Wirkmechanismus ist. Aufgrund der asymmetrischen Datenbasis (Recycling von 2 von 3 Armen) und der Beschränkung auf einen einzigen Task darf dies jedoch noch nicht als gesicherte Praxis (`adopted`) kanonisiert werden.

## Nächste Schritte

- Replikation ansetzen: Ein neuer, unabhängiger Task (z.B. Parser oder Validator) muss sauber mit allen drei Armen (`code-first`, `spec-first`, `test-first`) von Grund auf durchgeführt werden.
