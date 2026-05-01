---
title: "Agent/Skill Minimal Layer v0.1 — Instrumentierungskontext"
status: draft
canonicality: operative
---

# CONTEXT.md — Experiment-Kontext

## Ausgangslage

Die Agent/Skill Minimal Layer v0.1 wurde eingeführt. Diese Schicht besteht aus drei Komponenten:

- **Non-Ideal Task Guard** im `experiment-critic` (Agent-Instruktion, die nicht-ideale Aufgaben frühzeitig abfängt)
- **`evidence-reconciliation-auditor`** (Agent, der Behauptungen gegen Repository-Artefakte prüft)
- **`docs/evaluations/agent-skill-file-fruitfulness.md`** (Bewertungsrahmen: Metriken und Interpretation Budget für Agent/Skill-Dateien)

Diese Schicht ist neu. Es liegen noch keine vergleichbaren PR-Datensätze vor, die eine Wirksamkeitsbewertung erlauben würden.

## Ziel dieses Experiments

Dieses Experiment prüft ausschließlich **Messbarkeit, Erhebbarkeit und Vergleichbarkeit** künftiger PR-Daten, die mit der Agent/Skill Minimal Layer v0.1 entstehen.

Es stellt keine Wirksamkeitsbehauptung auf.

## Explizite Grenzen

- **Kein Kausalclaim:** Dieses Experiment behauptet nicht, dass die Agent-Schicht irgendeinen Effekt erzeugt.
- **Kein Wirksamkeitsclaim:** Ohne Kontrollgruppe und ohne mindestens drei vergleichbare PRs wäre jeder Effektclaim methodisch unzulässig.
- **Kein Urteil über Skill-Dateien:** Es wurden keine dedizierten Skill-Dateien als eigener Repo-Artefakttyp eingeführt. Eine Bewertung von Skill-Dateien ist daher nicht Gegenstand dieses Experiments.

## Umgebung

- **Tools:** experiment-critic (mit Non-Ideal Task Guard), evidence-reconciliation-auditor
- **Sprache:** Mixed (Markdown, YAML, JSONL)
- **Projekttyp:** vibe-lab (Experiment-Repository)
- **Modell(e):** LLM-Agent (variiert je PR)

## Relevante Vorarbeiten

- `docs/evaluations/agent-skill-file-fruitfulness.md` — Metriken und Interpretation Budget
- `experiments/2026-04-23_agent-failure-surface/` — Vorgänger-Experiment zur Agent-Fehlerflächenkartierung
- `experiments/2026-04-15_agent-task-validity/` — Task-Validity-Experiment als methodischer Vorläufer

## Einschränkungen

- Noch keine vergleichbaren Baseline-PRs ohne Agent-Schicht vorhanden.
- Keine Kontrollgruppe in dieser Phase.
- Auditor-Nutzung ist freiwillig und hängt von der jeweiligen PR-Durchführung ab.
- Metriken sind noch nicht geeicht — Zähldefinitionen können sich in frühen PRs stabilisieren.
