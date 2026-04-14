---
title: "Ergebnisse: Upfront Structuring Comparison"
status: adopted
canonicality: operative
validates:
  - "../../../catalog/techniques/spec-first-prompting.md"
---

# result.md — Experiment-Ergebnisse

> **Pflichtdokument für Adopt-Kandidaten.** Fasst die Ergebnisse und die getroffene Entscheidung zusammen.

## Zusammenfassung der Ergebnisse

Das Experiment entflechtet die Erkenntnisse der Vorstudie `2026-04-14_tdd-vibe`. Es wurden drei Strategien bei der Implementierung einer logiklastigen Funktion (`roman_to_int`) verglichen:
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

1. **Strukturierung ist die wahre Ursache:** Der Performance-Gewinn von TDD (Test-First) gegenüber Code-First geht nicht exklusiv auf das *Testen* zurück, sondern primär auf die Tatsache, dass das Modell das Problem *vor der Implementierung* explizit durchdenken muss.
2. **Parität der Strukturierungsmethoden:** Ob dieses "Durchdenken" als ausführbare Tests (Test-First) oder als textuelle Constraint-Spezifikation (Spec-First) erfolgt, macht im reinen *First-Shot-Success* bei diesem Task-Umfang keinen signifikanten Unterschied. Beide Methoden zwingen das LLM in einen analytischen Zustand.

## Entscheidung

**Urteil:** Adopt (Hypothese bestätigt)
**Begründung:** Die Hypothese, dass "Explizite Vorstrukturierung" die tatsächliche Ursache für robustere Agentenarbeit bei logiklastigen Aufgaben ist, wurde bestätigt. TDD ist eine Form, Spec-First eine andere. Da `Spec-First` bereits im Katalog existiert (`catalog/techniques/spec-first-prompting.md`), liefert dieses Experiment eine starke unabhängige Validierung für diesen Eintrag.

## Nächste Schritte

- Das Experiment validiert `catalog/techniques/spec-first-prompting.md` als Best-Practice für Vorstrukturierung.
