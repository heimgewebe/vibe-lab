---
title: "Policy — Artifact Boundary"
status: draft
canonicality: exploratory
relations:
  - type: references
    target: ../blueprints/blueprint-evidence-control-plane-v1.md
  - type: references
    target: ../playbooks/evidence-control-plane-roadmap-checklist.md
  - type: references
    target: pr-run-evidence-policy.md
---

# Policy — Artifact Boundary

> Diese Policy ist noch nicht technisch enforced.
> Sie definiert Grenzen für Artefaktablage, aktiviert aber kein technisches Enforcement.

## Repo-lokal erlaubt

- kleine YAML/JSON/MD-Summaries
- kompakte Command-Ausgaben
- Evidence-Pack-Manifeste
- Hashes, Herkunft, Retention-Hinweise

## Repo-lokal problematisch (später zu blockieren)

- vollständige PR-Diffs
- große CI-Logs
- API-Dumps
- Screenshots
- lange Transkripte
- große rohe Runtime-Ausgaben

## Regeln für fehlende und externe Evidenz

- Missing-Evidence-Dateien sind Abwesenheitsnachweise, keine Erfolgsbeweise.
- Große Artefakte sollen später extern referenziert werden mit:
  - summary
  - sha256
  - source/ref
  - captured_at
  - retention_note

## Nicht-Ziele dieser Policy

- Noch keine harte Größenregel aktivieren.
- Keine rückwirkende Umbewertung historischer Artefakte in diesem PR.
