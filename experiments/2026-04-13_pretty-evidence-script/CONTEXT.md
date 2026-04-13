---
title: "Experiment-Kontext: Pretty Evidence Script"
status: adopted
canonicality: operative
---

# CONTEXT.md — Experiment-Kontext

> **Pflichtdokument für Adopt-Kandidaten.** Beschreibt den vollständigen Kontext, in dem das Experiment stattfindet.

## Ausgangslage

- In vibe-lab werden experimentelle Abläufe direkt in `evidence.jsonl` geloggt. Dies ist die einzige valide Form eines echten Verlaufs (Proof-of-Run).
- Rohe JSONL-Daten sind schwer zu lesen. Ein Skript, um diese Logs schöner im Terminal auszugeben, fehlt, ist aber für die Diagnostik hilfreich.
- Das Experiment testet, ob die Erstellung eines solchen Skripts (Python) sauber dokumentiert und nach Repo-Regeln umgesetzt werden kann (Trennung Beobachtung/Deutung, echte Durchführungsbeweise in evidence.jsonl etc.).

## Umgebung

- **Tools:** Terminal, python, make, git
- **Sprache:** Python
- **Projekttyp:** CLI-Tool / Scripting im Repo
- **Modell(e):** n/a (Manuelle/Agent-Ausführung)

## Relevante Vorarbeiten

- Struktur des Repo (schemas, experiment-struktur, rules).
- Vorherige Experimente (z.B. spec-first).

## Einschränkungen

- Das Script darf nicht die `evidence.jsonl` manipulieren.
- Das Script muss als echtes Artefakt referenzierbar sein.
