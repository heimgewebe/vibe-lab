---
title: "Experiment-Kontext: Upfront Structuring Replication"
status: testing
canonicality: operative
---

# CONTEXT.md — Experiment-Kontext

> Beschreibt den vollständigen Kontext, in dem das Experiment stattfindet.

## Ausgangslage

Eine Vorstudie (`2026-04-14_tdd-vibe`) und eine darauffolgende vergleichende Analyse (`2026-04-14_upfront-structuring`) legten den Schluss nahe, dass explizite Vorstrukturierung (egal ob via TDD oder textueller Spezifikation) die Robustheit von generiertem Code signifikant erhöht, indem das LLM zur Problemanalyse gezwungen wird, bevor Code generiert wird.
Dieses Experiment zielt darauf ab, diese Hypothese auf einen komplett neuen Task zu replizieren, um sicherzustellen, dass das Phänomen generalisierbar und nicht an die spezifische Eigenheit römischer Zahlen gekoppelt ist.

## Umgebung

- **Tools:** LLM-Agents im Vibe-Lab.
- **Sprache:** Python
- **Projekttyp:** Isolierte logiklastige Aufgabe (Zustandsmaschine zur Validierung eines einfachen `User` JSON-Strings, mit strikten Abhängigkeiten, z.B. wenn "role"=="admin", muss "admin_id" vorhanden sein).
- **Modell(e):** Standard Vibe-Lab Agent LLM

## Relevante Vorarbeiten

- `experiments/2026-04-14_upfront-structuring/` (Originalexperiment)
- `experiments/2026-04-14_tdd-vibe/` (Initiale Vorstudie)

## Einschränkungen

- Der Task ist weiterhin recht kurz und logiklastig. Die Ergebnisse gelten womöglich nicht für weitläufige Architekturaufgaben.
