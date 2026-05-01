---
title: "Agent/Skill Minimal Layer v0.1 — Initiale Situation"
status: draft
canonicality: operative
---

# INITIAL.md — Initiale Situation

## Ausgangslage

Zum Zeitpunkt der Experimentanlage gilt:

- Der `experiment-critic` enthält den **Non-Ideal Task Guard** — eine Instruktion, die Aufgaben mit unklarem Scope oder fehlenden Lokalisierungsangaben frühzeitig beanstandet.
- Der **`evidence-reconciliation-auditor`** existiert als eigenständiger Agent und prüft, ob Behauptungen in PR-Beschreibungen oder Agenten-Outputs durch belegbare Artefakte im Repository gedeckt sind.
- **`docs/evaluations/agent-skill-file-fruitfulness.md`** definiert einen Metriken-Rahmen und ein Interpretation Budget für die Bewertung von Agent/Skill-Aktivitäten.

## Noch nicht vorhanden

- **Noch keine drei vergleichbaren PRs** mit der Agent/Skill Minimal Layer v0.1 beobachtet.
- **Noch kein Wirkungsvotum zulässig** — weder positiv noch negativ.
- Kein Baseline-Datensatz aus der Zeit vor der Schicht, der einen Vergleich ermöglichen würde.

## Zielzustand dieser Initialisierung

Dieses Experiment legt ein **Experimentgerüst** an, das:

1. Metriken und Erfassungslogik vorab definiert (method.md)
2. Bekannte Failure Modes explizit dokumentiert (failure_modes.md)
3. Einen initialen Observation-Eintrag in `results/evidence.jsonl` ablegt, der den Start der Instrumentierung markiert
4. Erste PR-Daten aufnehmen kann, sobald ein realer PR mit Auditor-Beteiligung abgeschlossen ist

## Systemkonfiguration

- `experiment-critic` mit Non-Ideal Task Guard aktiviert
- `evidence-reconciliation-auditor` verfügbar
- Metriken-Rahmen: `docs/evaluations/agent-skill-file-fruitfulness.md`

## Erwartete Baseline

Da keine vergleichbaren Vor-Schicht-PRs dokumentiert sind, gibt es keine quantitative Baseline. Das Experimentgerüst selbst ist die Baseline für zukünftige Vergleiche.
