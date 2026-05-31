---
title: "Legacy Refactoring Challenge v1"
status: active
canonicality: operative
challenge_id: "legacy-refactoring"
version: "v1"
task_family: "legacy_refactoring"
expected_outputs:
  - "Behavior-preserving refactor"
  - "Regression tests or verification evidence"
  - "Reduced complexity or documented structure improvement"
evaluation_criteria:
  - "Behavior preservation"
  - "Readable decomposition"
  - "Minimal unintended surface change"
  - "Reproducible evidence artifacts"
known_confounders:
  - "Incomplete legacy behavior specification"
  - "Hidden coupling"
  - "Ambiguous acceptable refactor scope"
---

# Benchmark Challenge: Legacy Refactoring (v1)

## Zweck

Standardisierte Vergleichsaufgabe zur Bewertung von Vibe-Coding-Techniken bei der Modernisierung und Refaktorierung von bestehendem, unsauberem ("Brownfield") Code.

## Aufgabe

Refaktorierung einer vorgegebenen, stark gekoppelten und monolithischen "Legacy"-Klasse (z.B. ein historisch gewachsener `OrderProcessor` mit gemischter Geschäftslogik, Datenbankzugriffen und Nebenwirkungen).

### Anforderungen an das Zielsystem
1. **Entkopplung**: Trennung von Geschäftslogik, Datenzugriff und externen Services (z.B. Dependency Injection).
2. **Testbarkeit**: Der neue Code muss durch Unit-Tests abgedeckt werden können (Mocking muss möglich sein).
3. **Verhalten**: Die äußere Funktionalität (Schnittstelle/Verhalten) muss strikt erhalten bleiben.
4. **Fehlerbehandlung**: Einführung einer sauberen und einheitlichen Fehlerbehandlungsstrategie, wo vorher nur stille "Try-Catch"-Blöcke waren.

### Setup
*(Ein fiktives Legacy-Modul wird in den Kontext geladen)*
- Sprache: Python oder TypeScript (abhängig von der Agenten-Konfiguration).
- Ausgangscode: Ein Monolith mit ~300-500 Zeilen voller "Code Smells".

## Bewertungskriterien

| Kriterium          | Gewicht | Beschreibung                                  |
| ------------------ | ------: | --------------------------------------------- |
| Regression         | 35%     | Bestehendes Verhalten bleibt fehlerfrei erhalten |
| Architektur        | 25%     | Trennung der Anliegen (SoC), saubere Schnittstellen |
| Testbarkeit        | 20%     | Code ermöglicht einfaches Mocken und Testen    |
| Code-Qualität      | 10%     | Namensgebung, Typisierung, Lesbarkeit          |
| Nacharbeit         | 10%     | Notwendige Korrekturen zur Wiederherstellung der Funktion |

## Versionierung

- **Version:** v1
- **Erstellt:** 2026-04-11
- **Änderungen:** Initiale Version

> Beim Referenzieren in `decision.yml` bitte `challenge_version: "legacy-refactoring-v1"` angeben.
