---
title: "Ergebnisse: Upfront Structuring Replication"
status: testing
canonicality: operative
validates:
  - "../../../catalog/techniques/spec-first-prompting.md"
---

# result.md — Experiment-Ergebnisse

> **Replikation.** Bestätigt Ergebnisse der vergleichenden Anschlussanalyse.

## Zusammenfassung der Ergebnisse

Dieses Experiment repliziert die Analyse von `2026-04-14_upfront-structuring` auf einem komplett neuen Task (einem streng typisierten User-Validator). Alle drei Arme wurden *from scratch* neu generiert.

1. **Code-First:** Naives Prompting erzeugte eine Funktion, die Typprüfungen (`age='25'`) und bedingte Logik (Wenn `admin`, dann `admin_id`) übersah. 2 fehlgeschlagene Edge-Cases.
2. **Spec-First:** Die Vorab-Extraktion einer Text-Spezifikation führte zu einer robusteren Implementierung mit Typprüfungen (`isinstance`) und korrekter bedingter Logik. 0 verpasste Edge-Cases.
3. **Test-First (TDD):** Die Vorab-Extraktion von Tests führte ebenfalls zu einer robusten Implementierung, die sofort alle Tests bestand. 0 verpasste Edge-Cases.

## Datenpunkte (Evidence)

Siehe `evidence.jsonl`:
- `test_pass_rate_code_first`: 0.5
- `test_pass_rate_spec_first`: 1.0
- `test_pass_rate_test_first`: 1.0

## Erkenntnisse

1. **Replikation erfolgreich:** Das Phänomen ist nicht auf einen spezifischen Task beschränkt.
2. **Kausalität bestätigt:** Die Vorstrukturierung (egal ob Spec oder Test) zwingt das Modell in eine Problem-Explorations-Phase, die spätere Fehler bei der Code-Generierung drastisch reduziert.

## Entscheidung

**Urteil:** Testing (Replikation erfolgreich, vor Promotion zu diskutieren).
**Begründung:** Die Replikation bestätigt den Befund, dass `Spec-First` und `Test-First` dem `Code-First` bei logiklastigen Aufgaben systematisch überlegen sind. Da Spec-First bereits im Katalog existiert, stärkt dies das Vertrauen in diese Technik. Über eine formelle Erweiterung oder Adaption als `adopted` für `Test-First` kann nach Konsolidierung entschieden werden.
