title: "Initiale Situation: Generated Artifact Contract Validation"
status: draft
canonicality: operative
---

# INITIAL.md — Initiale Situation

> **Pflichtdokument für Adopt-Kandidaten.** Dokumentiert den exakten Ausgangszustand zu Beginn des Experiments.

## Initialer Prompt / Setup

Das Meta-Experiment startet mit der Frage:

"Reduziert der neue Generated-Artifact-Contract (`canonical/derived/ephemeral`) in Kombination mit dem CI-Split (`blocking/non-blocking/artifact-only`) messbar Drift, Friction und kognitive Last?"

```
Arbeite auf realen PRs im Repository.
Miss pro PR: Contract-Verletzungen, CI-Fehlertypen, manuelle Eingriffe und Diagnoseklarheit.
Trenne strikt Beobachtung (evidence.jsonl) von Interpretation (result.md / decision.yml).
```

## Systemkonfiguration

- Branch: laufender Feature-Branch mit bereits eingefuehrtem Artifact-Contract
- CI: `.github/workflows/validate.yml` mit drei Diagnosepfaden
- Contract-Quelle: `.vibe/generated-artifacts.yml`
- Lokale Pruefung: `make validate`

## Erwartete Baseline

Ohne den neuen Contract waeren haeufiger zu erwarten:

- nicht-semantische CI-Fehler ohne klare Ursache
- mehr manuelle Nachzuege bei generated files
- hoehere Unsicherheit, welche Drift wirklich merge-blockierend ist
