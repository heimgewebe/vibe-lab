---
title: "Agent/Skill Minimal Layer Instrumentation — Ergebnis"
status: draft
canonicality: operative
---

# result.md — Ergebnis

## Status

**Runs 1–4 erfasst.** Drei vergleichbare kontrollierte Runs (Run 2–4) mit vollständiger Evidence-Pack-Kopplung dokumentiert. Kein Wirksamkeitsclaim. PR-10-Schwellenwert für cross_comparable_runs=3 ist erreicht.

## Canonical Artifacts

- **`artifacts/run-001-promotion-readiness-prepared-without-measurement/auditor-output.yml`** — kanonischer YAML-Auditor-Output (machine-readable source of truth)
- **`artifacts/run-001-promotion-readiness-prepared-without-measurement/measurement.yml`** — Run-1-Metriken
- `artifacts/run-001-promotion-readiness-prepared-without-measurement/auditor-output.md` — nicht-kanonische Projektion (human-readable view only)
- **`artifacts/run-002-controlled-agent-skill-run/`** — erster vollständiger kontrollierter Run (PR 9)
- **`artifacts/run-003-controlled-agent-skill-run/`** — zweiter vollständiger kontrollierter Run (PR 10, Run 1)
- **`artifacts/run-004-controlled-agent-skill-run/`** — dritter vollständiger kontrollierter Run (PR 10, Run 2)

## Datenlage

- 4 Runs erfasst. Run 1 nicht vergleichbar (fehlende Messung); Run 2–4 sind vergleichbare kontrollierte Agent/Skill-Runs.
- Run 2 Auditor-Verdict: **PASS** (`derived_from_auditor_output`).
- Run 3 Auditor-Verdict: **PASS** (`derived_from_auditor_output`).
- Run 4 Auditor-Verdict: **PASS** (`derived_from_auditor_output`).
- `current_comparable_runs = 3` — Schwellenwert für PR-11-Cross-Run-Assessment erreicht.
- `review_friction_count` und `rework_count` bleiben `null` / `missing_evidence` in allen Runs.
- `task_completion_time_observed` in allen Runs `self_reported`; nicht vergleichbar, kein Kausalclaim.
- Kein Wirkungsclaim möglich oder zulässig.
- Keine Aussage, dass Agent- oder Skill-Dateien nützlich sind.

## Interpretation Budget

### Allowed Claims

- Das Experiment legt einen Erhebungsrahmen für künftige PR-Daten an.
- Run 2–4 wurden als kontrollierte Agent/Skill-Runs mit vollständiger Evidence-Pack-Kopplung erfasst.
- Alle drei vergleichbaren Runs haben Auditor-Verdict PASS mit repo-lokaler Evidence.
- current_comparable_runs=3; der Mindestschwellenwert für PR-11 (cross-run-assessment) ist erreicht.
- Kein Wirksamkeitsclaim.

### Disallowed Claims

- Die Agent-Schicht reduziert Fehler.
- Die Agent-Schicht ist nützlich.
- Skill-Dateien sind bewertet.
- CI-/Script-Rückbindung ist gerechtfertigt.
- Aus drei Messpunkten ohne Kontrollgruppe folgt irgendeine Wirkungsaussage.
- cross-run-assessment.md ist Teil dieses PRs (das ist PR 11).

## Evidence Basis

| Kategorie | Stand |
|---|---|
| Repo-lokal belegt (PASS) | Validator-Logik, Ratchet-Entry, Regressionstests, run-002/003/004-Artefakte (via auditor-output.yml) |
| derived_from_auditor_output | unsupported_claim_count, validation_gap_count (Run 2–4) |
| self_reported | task_completion_time_observed (nicht vergleichbar) |
| MISSING_EVIDENCE | review_friction_count, rework_count (alle Runs); CI-Testprotokoll; experiment-critic-Output |
| Nicht getestet | Wirkung; Kontrollgruppe |
| Offen für PR 11 | Cross-Run-Assessment, Messsystem-Reifebewertung |

## Nächste Schritte

PR 11: `cross-run-assessment.md` auf Basis von Run 2–4 erstellen. Messsystem-Reife beurteilen; kein Wirksamkeitsclaim zulässig.
