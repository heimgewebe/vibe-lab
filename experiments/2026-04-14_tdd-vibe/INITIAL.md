---
title: "Initiale Prompt-/Setup-Situation: TDD Vibe"
status: draft
canonicality: operative
---

# INITIAL.md — Initiale Situation

> **Pflichtdokument für Adopt-Kandidaten.** Dokumentiert den exakten Ausgangszustand zu Beginn des Experiments.

## Initialer Prompt / Setup

Die Aufgabe ist das Implementieren eines "Römische Zahlen zu Integer" Konverters (`roman_to_int`) inklusive Fehlererkennung für ungültige Formate (z.B. "IIII", "VV").

### Baseline Prompt (Code-First)

```
Schreibe eine Python-Funktion `roman_to_int(s: str) -> int`, die römische Zahlen in Integer konvertiert.
Die Funktion muss auch ungültige Formate (z.B. 'IIII', 'VV', 'IC') erkennen und einen ValueError werfen.
Schreibe danach Tests mit pytest, um das zu validieren.
```

### Treatment Prompt (TDD Vibe)

```
Wir wollen eine Python-Funktion `roman_to_int(s: str) -> int` implementieren, die römische Zahlen in Integer konvertiert und bei ungültigen Formaten (z.B. 'IIII', 'VV', 'IC') einen ValueError wirft.
Schritt 1: Schreibe AUSSCHLIESSLICH die ausführlichen pytest-Tests für diese Funktion, inklusive aller Edge-Cases und Fehlerfälle.
Schritt 2: Erst wenn die Tests vollständig und korrekt geschrieben sind, generiere die Implementierung der Funktion, sodass die Tests grün werden.
```

## Systemkonfiguration

- Standard-Python-Umgebung mit `pytest`.
- Ausführung erfolgt als bash-Skript in `experiments/2026-04-14_tdd-vibe/artifacts/`.

## Erwartete Baseline

Beim Code-First Ansatz generiert das LLM oft zuerst eine naive Implementierung, die komplexe Fehlerfälle ("IC", "IIII") nicht richtig abfängt, und schreibt dann Tests, die entweder genau das falsche Verhalten testen (Bestätigungsfehler) oder fehlschlagen, was Nacharbeit erfordert.
Wir erwarten, dass der TDD Vibe Ansatz umfassendere Tests generiert, da der Fokus zunächst nur auf den Anforderungen (Tests) liegt, und die darauffolgende Implementierung robuster ist.
