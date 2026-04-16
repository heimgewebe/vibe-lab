---
title: "Initiale Prompt-/Setup-Situation: Upfront Structuring Replication"
status: testing
canonicality: operative
document_role: experiment
---

# INITIAL.md — Initiale Situation

> Dokumentiert den exakten Ausgangszustand zu Beginn des Experiments.

## Initialer Prompt / Setup

Die Aufgabe ist ein einfacher, strenger Validator für User-Events.
Eingabe ist ein Dictionary. Der Validator `validate_user(data: dict) -> bool` soll prüfen:
1. `username` muss ein String sein, min 3 Zeichen.
2. `age` muss ein Integer sein >= 18.
3. `role` darf nur "user" oder "admin" sein.
4. WICHTIG: Wenn `role` == "admin", MUSS das Feld `admin_id` existieren und mit "A-" beginnen.
Wenn Regeln verletzt werden, soll `ValueError` geworfen werden.

### Arm 1: Code-First
`Schreibe eine Python-Funktion validate_user(data: dict), die User-Dictionaries validiert (Regeln siehe oben). Wirf ValueError bei Fehlern.`

### Arm 2: Spec-First
`Schritt 1: Schreibe AUSSCHLIESSLICH eine textuelle Spezifikation der Fehlerfälle für die validate_user Funktion (Regeln siehe oben). Schritt 2: Erst wenn die Spezifikation steht, generiere die Implementierung der Funktion entsprechend dieser Regeln.`

### Arm 3: Test-First (TDD)
`Schritt 1: Schreibe AUSSCHLIESSLICH ausführliche pytest-Tests für die validate_user Funktion (Regeln siehe oben), inklusive aller Edge-Cases. Schritt 2: Erst danach generiere die Implementierung der Funktion, sodass die Tests grün werden.`

## Systemkonfiguration

- Standard-Python-Umgebung mit `pytest`.
- Ausführung in `experiments/2026-04-14_upfront-structuring-replication/artifacts/`.
