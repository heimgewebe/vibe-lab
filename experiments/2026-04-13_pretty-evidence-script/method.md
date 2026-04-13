---
title: "Experiment-Methode: Pretty Evidence Script"
status: testing
canonicality: operative
---

# method.md — Experiment-Methode

> Beschreibt das strukturierte Vorgehen zur Prüfung der Hypothese.

## Hypothese

Ein einfaches Python-Skript kann die Lesbarkeit von `evidence.jsonl` verbessern, ohne die repo-invarianten Regeln zu verletzen. Die Architektur von vibe-lab erzwingt sauberes Denken bei der Erstellung.

## Methode

### Vorgehen

1. Erstellen von `scripts/pretty_evidence.py`.
2. Das Skript liest ein als Argument übergebenes `evidence.jsonl` File ein und gibt dessen Inhalte übersichtlich (als formatierter Text) aus.
3. Test des Skripts mit dem `results/evidence.jsonl` dieses Experiments.
4. Ausgabeprotokoll in `artifacts/test_output.txt` speichern.
5. In `evidence.jsonl` einen Datensatz mit `event_type: "run"` loggen, der auf das Artefakt verweist, inklusive `exit_code: 0`.
6. Danach Beobachtungen in `evidence.jsonl` festhalten (z. B. wo die Repo-Regeln griffen, wo man unsicher war).
7. Formulierung von Erkenntnissen in `results/result.md` (Beobachtung vs. Deutung).

### Metriken

- Reibung (Aufwand): Wie viel Aufwand bedeutet die Repo-Governance (Frontmatter, JSONL Logging) bei einer simplen Skript-Entwicklung?
- Erkenntnis: Unterscheidung von reiner Ausführung und Deutung im Resultat-Dokument.

### Erfolgskriterien

- Ein funktionales Skript ist in `scripts/` erstellt.
- Das Experiment ist vollständig durchlaufen und validiert (`make validate`).
- `results/result.md` trennt explizit zwischen Beobachtung und Deutung, und listet die Reibungspunkte und Gewinne der Repo-Struktur auf.

## Einschränkungen

Das Experiment stellt eine Meta-Untersuchung der Agenten-Disziplin unter den Governance-Regeln von vibe-lab dar.
