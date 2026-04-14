---
title: "Experiment-Kontext: Upfront Structuring Comparison"
status: draft
canonicality: operative
---

# CONTEXT.md — Experiment-Kontext

> **Pflichtdokument für Adopt-Kandidaten.** Beschreibt den vollständigen Kontext, in dem das Experiment stattfindet.

## Ausgangslage

Eine Vorstudie (`2026-04-14_tdd-vibe`) zeigte stark positive Signale dafür, dass Test-Driven Development (TDD) bei LLM-Aufgaben (Tests vor Code generieren) robusteren Code erzeugt. Es blieb jedoch ungeklärt, ob dieser Erfolg spezifisch auf *Testen* zurückzuführen ist, oder allgemein auf *explizite Vorstrukturierung* (Spezifikation vs. Tests).

Dieses Experiment entflechtet diese Ursache, indem es `code-first`, `spec-first` und `test-first` bei der identischen logiklastigen Aufgabe (`roman_to_int`) vergleicht.

## Umgebung

- **Tools:** LLM-Agents im Vibe-Lab.
- **Sprache:** Python
- **Projekttyp:** Isolierte logiklastige Aufgabe (Roman Numeral Converter)
- **Modell(e):** Standard Vibe-Lab Agent LLM

## Relevante Vorarbeiten

- `experiments/2026-04-14_tdd-vibe/` (Vorstudie)
- `experiments/2026-04-08_spec-first/`

## Einschränkungen

- Wir vergleichen hier nur drei Varianten an einem Task. Um generelle Aussagen zu treffen, müssten später weitere Task-Typen (Parser, Validator etc.) hinzugezogen werden.
