---
title: "Experiment-Kontext: Prompt-Length Control"
status: testing
canonicality: operative
---

# CONTEXT.md — Experiment-Kontext

> Kausale Entflechtung von Upfront Structuring.

## Ausgangslage

Bisherige Experimente zeigten, dass Upfront Structuring (Test-First, Spec-First) die Robustheit bei logiklastigen Aufgaben massiv steigert.
Es existiert jedoch ein blinder Fleck: Erzeugt das LLM besseren Code, weil es gezwungen wurde, die *Constraints zu strukturieren* (Declarative Mode), oder erzeugt es besseren Code, *einfach weil es gezwungen wurde, überhaupt erst lange Textmengen vor der Codeausgabe zu generieren*? Letzteres würde als Proxy für "Chain of Thought" agieren.
Dieses Experiment entkoppelt Inhaltsstruktur von reiner Tokenlänge.

## Umgebung

- **Tools:** LLM-Agents.
- **Sprache:** Python.
- **Projekttyp:** Mini-Parser (Extrahiert aus einem String alle Wörter zwischen `**` und `**` unter Berücksichtigung escapeter Sterne `\*\*`).
- **Modell(e):** Standard Vibe-Lab Agent LLM.
