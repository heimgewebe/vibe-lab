---
title: "Experiment-Kontext: TDD Vibe"
status: inconclusive
canonicality: operative
---

# CONTEXT.md — Experiment-Kontext

> **Pflichtdokument für Adopt-Kandidaten.** Beschreibt den vollständigen Kontext, in dem das Experiment stattfindet.

## Ausgangslage

Es existiert die Hypothese, dass Test-Driven Development (TDD) auch beim Code-Generieren durch LLMs Vorteile bietet ("TDD Vibe"). Anstatt dem LLM aufzugeben "Schreibe eine Funktion X", wird es angewiesen "Schreibe zuerst Tests für die Funktion X, und sobald diese stehen, generiere die Implementierung".
Es soll evaluiert werden, ob dieser "Test-First"-Ansatz robusteren Code und weniger Iterationen für Fehlerbehebungen erzeugt, verglichen mit direktem Generieren von Code (Code-First).

## Umgebung

- **Tools:** LLM-Agents im Vibe-Lab.
- **Sprache:** Python (als Beispielsprache für leichte Test-Iterierbarkeit via `pytest`).
- **Projekttyp:** Einfaches Utility/Algorithmus-Skript, um klar isolierte Testfälle zu haben (z. B. ein komplexer Text-Parser oder eine mathematische Transformation).
- **Modell(e):** Standard Vibe-Lab Agent LLM.

## Relevante Vorarbeiten

- Experiment `2026-04-11_yolo-vs-spec-first` zeigte, dass Strukturierungsansätze (wie Spec-First) Vorteile bei der Iterierbarkeit bieten.
- Raw Vibes: `catalog-candidates.md` listet "TDD Vibe" als Hypothese auf.

## Einschränkungen

- Bei sehr simplen Funktionen könnte der TDD-Vibe Overhead verursachen, ohne signifikanten Vorteil zu bringen. Wir müssen eine ausreichend komplexe Aufgabe wählen.
