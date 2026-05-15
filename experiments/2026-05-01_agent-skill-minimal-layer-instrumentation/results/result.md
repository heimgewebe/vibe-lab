---
title: "Agent/Skill Minimal Layer Instrumentation — Ergebnis"
status: draft
canonicality: operative
---

# result.md — Ergebnis

## Status

**Drei vergleichbare Runs erfasst (run-002, run-005, run-006). PR-11-Schwellenwert erreicht.**
Run 3 und Run 4 (run-003, run-004) entstanden im selben PR-10-Session-Durchlauf und haben
`comparability_verdict: not_comparable`. `current_comparable_runs = 3`.
Cross-Run-Assessment erstellt; Messsystem-Reifegrad: `partially_ready`.

## Canonical Artifacts

- **`artifacts/run-001-promotion-readiness-prepared-without-measurement/auditor-output.yml`** — kanonischer YAML-Auditor-Output (machine-readable source of truth)
- **`artifacts/run-001-promotion-readiness-prepared-without-measurement/measurement.yml`** — Run-1-Metriken
- `artifacts/run-001-promotion-readiness-prepared-without-measurement/auditor-output.md` — nicht-kanonische Projektion (human-readable view only)
- **`artifacts/run-002-controlled-agent-skill-run/`** — erster vollständiger kontrollierter Run (PR 9); `comparability_verdict: reference_only`
- **`artifacts/run-003-controlled-agent-skill-run/`** — Kandidaten-/Rehearsal-Run (PR 10, Session-Phase 1); `comparability_verdict: not_comparable`
- **`artifacts/run-004-controlled-agent-skill-run/`** — Kandidaten-/Rehearsal-Run (PR 10, Session-Phase 2); `comparability_verdict: not_comparable`
- **`artifacts/run-005-controlled-agent-skill-run/`** — zweiter vergleichbarer kontrollierter Run (PR 10); `comparability_verdict: comparable`
- **`artifacts/run-006-controlled-agent-skill-run/`** — dritter vergleichbarer kontrollierter Run (PR 11); `comparability_verdict: comparable`
- **`results/cross-run-assessment.md`** — Messsystem-Reifegrad-Bewertung; Verdict: `partially_ready`

## Datenlage

- 6 Runs erfasst. Run 1 nicht vergleichbar (fehlende Messung). Run 2, 5, 6 bestätigte vergleichbare Runs. Run 3–4 Kandidaten/Rehearsal, nicht vergleichbar.
- `current_comparable_runs = 3` — PR-11-Schwellenwert erreicht.
- Auditor-Verdict: **PASS** in Run 2, 5, 6 (je `derived_from_auditor_output`).
- `review_friction_count` und `rework_count` bleiben `null` / `missing_evidence` in allen Runs.
- `scope_drift_count` in Run 3/4 `null` / `missing_evidence` (kein changed-files-Artefakt archiviert).
- `task_completion_time_observed` in allen Runs `self_reported`; nicht vergleichbar, kein Kausalclaim.
- Kein Wirkungsclaim möglich oder zulässig.
- Messsystem-Reifegrad: `partially_ready` (5 von 8 Metriken operativ belegt).

## Interpretation Budget

### Allowed Claims

- Das Experiment legt einen Erhebungsrahmen für künftige PR-Daten an.
- Run 2, 5 und 6 wurden als kontrollierte Agent/Skill-Runs mit vollständiger Evidence-Pack-Kopplung erfasst.
- Run 3 und Run 4 wurden als Kandidaten-/Rehearsal-Runs erfasst und haben die Vergleichbarkeitsregeln dokumentiert.
- Die Vergleichbarkeitsregeln (comparability.yml) funktionieren: Run 3/4 werden korrekt als `not_comparable` eingestuft.
- Das Messgerät ist für 5 von 8 Metriken konsistent messbar.
- Kein Wirksamkeitsclaim.

### Disallowed Claims

- Die Agent-Schicht reduziert Fehler.
- Die Agent-Schicht ist nützlich.
- Skill-Dateien sind bewertet.
- CI-/Script-Rückbindung ist gerechtfertigt.
- Null-Werte bei Metriken belegen Abwesenheit der gemessenen Probleme (keine Kontrollgruppe).
- Das Messsystem ist vollständig (review_friction_count, rework_count operativ offen).

## Evidence Basis

| Kategorie | Stand |
|---|---|
| Repo-lokal belegt (PASS) | Validator-Logik, Ratchet-Entry, Regressionstests, run-002/005/006-Artefakte |
| derived_from_auditor_output | unsupported_claim_count, validation_gap_count (Run 2/5/6) |
| self_reported | task_completion_time_observed (nicht vergleichbar) |
| MISSING_EVIDENCE | scope_drift_count (Run 3/4); review_friction_count, rework_count (alle Runs) |
| Nicht vergleichbar | Run 3/4 (comparability_verdict: not_comparable) |
| Nicht getestet | Wirkung; Kontrollgruppe |

## Nächste Schritte

Cross-Run-Assessment erstellt. Messsystem-Reifegrad: `partially_ready`.
Für `ready_for_effect_evaluation` müssen entweder `review_friction_count`/`rework_count` operationalisiert
oder explizit als out-of-scope deklariert werden. Eine Baseline für Kontrollgruppen-Vergleiche fehlt noch.
