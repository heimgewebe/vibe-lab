---
title: "Agent/Skill Minimal Layer Instrumentation — Ergebnis"
status: draft
canonicality: operative
---

# result.md — Ergebnis

## Status

**Run 1 und Run 2 erfasst; Run 3–4 als Kandidaten-/Rehearsal-Runs erfasst.** Run 2 (run-002) ist der einzige bestätigte vergleichbare kontrollierte Run. Run 3 und Run 4 (run-003, run-004) sind während desselben PR-10-Sessions-Durchlaufs entstanden und haben `comparability_verdict: not_comparable` (kein `independent_task_or_pr_ref`). `current_comparable_runs = 1`. PR 10 bleibt offen bis zwei weitere wirklich unabhängige vergleichbare Runs vorliegen.

## Canonical Artifacts

- **`artifacts/run-001-promotion-readiness-prepared-without-measurement/auditor-output.yml`** — kanonischer YAML-Auditor-Output (machine-readable source of truth)
- **`artifacts/run-001-promotion-readiness-prepared-without-measurement/measurement.yml`** — Run-1-Metriken
- `artifacts/run-001-promotion-readiness-prepared-without-measurement/auditor-output.md` — nicht-kanonische Projektion (human-readable view only)
- **`artifacts/run-002-controlled-agent-skill-run/`** — erster vollständiger kontrollierter Run (PR 9); `comparability_verdict: reference_only`
- **`artifacts/run-003-controlled-agent-skill-run/`** — Kandidaten-/Rehearsal-Run (PR 10, Session-Phase 1); `comparability_verdict: not_comparable`
- **`artifacts/run-004-controlled-agent-skill-run/`** — Kandidaten-/Rehearsal-Run (PR 10, Session-Phase 2); `comparability_verdict: not_comparable`

## Datenlage

- 4 Runs erfasst. Run 1 nicht vergleichbar (fehlende Messung). Run 2 bestätigter vergleichbarer Run. Run 3–4 Kandidaten/Rehearsal, nicht vergleichbar.
- `current_comparable_runs = 1` — Schwellenwert für PR-11 (mindestens 3) nicht erreicht.
- Run 2 Auditor-Verdict: **PASS** (`derived_from_auditor_output`).
- Run 3 Auditor-Verdict: **PASS** — aber `comparability_verdict: not_comparable`; zählt nicht.
- Run 4 Auditor-Verdict: **PASS** — aber `comparability_verdict: not_comparable`; zählt nicht.
- `review_friction_count` und `rework_count` bleiben `null` / `missing_evidence` in allen Runs.
- `scope_drift_count` in Run 3/4 `null` / `missing_evidence` (kein changed-files-Artefakt archiviert).
- `task_completion_time_observed` in allen Runs `self_reported`; nicht vergleichbar, kein Kausalclaim.
- Kein Wirkungsclaim möglich oder zulässig.

## Interpretation Budget

### Allowed Claims

- Das Experiment legt einen Erhebungsrahmen für künftige PR-Daten an.
- Run 2 wurde als erster kontrollierter Agent/Skill-Run mit vollständiger Evidence-Pack-Kopplung erfasst.
- Run 3 und Run 4 wurden als Kandidaten-/Rehearsal-Runs erfasst und haben die Vergleichbarkeitsregeln dokumentiert.
- Die Vergleichbarkeitsregeln (comparability.yml) funktionieren: Run 3/4 werden korrekt als `not_comparable` eingestuft.
- Kein Wirksamkeitsclaim.

### Disallowed Claims

- Die Agent-Schicht reduziert Fehler.
- Die Agent-Schicht ist nützlich.
- Skill-Dateien sind bewertet.
- CI-/Script-Rückbindung ist gerechtfertigt.
- current_comparable_runs=3 oder >=3 (aktuell: 1).
- PR-11 kann gestartet werden (Schwellenwert nicht erreicht).
- Run 3/4 zählen als vergleichbare Runs.

## Evidence Basis

| Kategorie | Stand |
|---|---|
| Repo-lokal belegt (PASS) | Validator-Logik, Ratchet-Entry, Regressionstests, run-002-Artefakte; comparability.yml für Run 3/4 |
| derived_from_auditor_output | unsupported_claim_count, validation_gap_count (Run 2) |
| self_reported | task_completion_time_observed (nicht vergleichbar) |
| MISSING_EVIDENCE | scope_drift_count (Run 3/4); review_friction_count, rework_count (alle Runs); CI-Testprotokoll; experiment-critic-Output |
| Nicht vergleichbar | Run 3/4 (comparability_verdict: not_comparable) |
| Nicht getestet | Wirkung; Kontrollgruppe |
| Offen für PR 10 | Zwei weitere unabhängige vergleichbare Runs mit independent_task_or_pr_ref |

## Nächste Schritte

PR 10 bleibt offen: Zwei weitere Runs mit echten unabhängigen `independent_task_or_pr_ref`-Werten (separate PRs oder Tasks) erfassen. Nach Erreichen von `current_comparable_runs=3` kann PR 11 (`cross-run-assessment.md`) starten.
