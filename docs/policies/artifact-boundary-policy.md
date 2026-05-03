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

> Status: `draft` / `exploratory`
>
> Diese Policy ist noch nicht technisch enforced.
> Sie definiert Grenzen fuer Artefaktablage, aktiviert aber kein technisches Enforcement.

## Repo-lokal erlaubt

- kleine YAML/JSON/MD-Summaries
- kompakte Command-Ausgaben
- Evidence-Pack-Manifeste
- Hashes, Herkunft, Retention-Hinweise

## Repo-lokal problematisch (spaeter zu blockieren)

- vollstaendige PR-Diffs
- grosse CI-Logs
- API-Dumps
- Screenshots
- lange Transkripte
- grosse rohe Runtime-Ausgaben

## Regeln fuer fehlende und externe Evidenz

- Missing-Evidence-Dateien sind Abwesenheitsnachweise, keine Erfolgsbeweise.
- Grosse Artefakte sollen spaeter extern referenziert werden mit:
  - summary
  - sha256
  - source/ref
  - captured_at
  - retention_note

## Nicht-Ziele dieser Policy

- Noch keine harte Groessenregel aktivieren.
- Keine rueckwirkende Umbewertung historischer Artefakte in diesem PR.
