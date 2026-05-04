---
title: "Policy — Artifact Boundary"
status: active
canonicality: exploratory
relations:
  - type: references
    target: ../blueprints/blueprint-evidence-control-plane-v1.md
  - type: references
    target: ../playbooks/evidence-control-plane-roadmap-checklist.md
  - type: references
    target: pr-run-evidence-policy.md
  - type: references
    target: ../../.vibe/pr-scope-policy.yml
---

# Policy — Artifact Boundary

> **Boundary Guard aktiv (PR 7).**
> `.vibe/pr-scope-policy.yml` ist die maschinenlesbare Quelle dieser Policy.
> `scripts/docmeta/validate_pr_scope.py` enforced die untenstehenden Regeln in Make/CI.
> Historische Artefakte außerhalb der konfigurierten `artifact_roots` werden im Repo-Scan-Modus nicht retroaktiv blockiert.

## Repo-lokal erlaubt

- kleine YAML/JSON/MD-Summaries
- kompakte Command-Ausgaben
- Evidence-Pack-Manifeste
- Hashes, Herkunft, Retention-Hinweise

## Repo-lokal blockiert (Boundary Guard aktiv)

Unter `experiments/**/` und `artifacts/**/` werden folgende Dateitypen blockiert:

- vollständige PR-Diffs (`*.patch`, `*.diff`, `*full*diff*`, `*pr*diff*`)
- große CI-Logs (`*ci*full*log*`, `*workflow*full*log*`)
- API-Dumps (`*api*dump*`, `*raw*response*`)
- Screenshots (`*screenshot*`)
- Transkripte (`*transcript*`)
- Artefakte > 262.144 Bytes — Dateinamen wie `evidence-pack.yml`, `test-output.txt`, `ci-output.txt`, `make-validate.txt` oder `summary.md` befreien nicht vom Größenlimit
- Evidence-Packs mit PASS-Verdict, die ausschließlich sich selbst als `repo_local`-Evidence referenzieren

## Regeln für fehlende und externe Evidenz

- Missing-Evidence-Dateien sind Abwesenheitsnachweise, keine Erfolgsbeweise.
- Große Artefakte sollen extern referenziert werden mit:
  - summary
  - sha256
  - source/ref
  - captured_at
  - retention_note

## Nicht-Ziele dieser Policy

- Keine rückwirkende Umbewertung historischer Artefakte außerhalb der artifact_roots.
- Keine Aussage über Agentenwirksamkeit.
