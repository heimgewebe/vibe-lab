---
title: "Agent/Skill Minimal Layer Instrumentation — Ergebnis"
status: draft
canonicality: operative
---

# result.md — Ergebnis

## Status

**Run 2 erfasst.** PR #148 als zweiter realer Messdatensatz dokumentiert. Kein Wirksamkeitsclaim.

## Canonical Artifacts

### Run 1 (PR #145)
- **`artifacts/run-001-promotion-readiness-prepared-without-measurement/run.yml`** — kanonischer Run-Bundle-Envelope
- **`artifacts/run-001-promotion-readiness-prepared-without-measurement/auditor-output.yml`** — kanonischer YAML-Auditor-Output
- **`artifacts/run-001-promotion-readiness-prepared-without-measurement/measurement.yml`** — Run-1-Metriken
- `artifacts/run-001-promotion-readiness-prepared-without-measurement/auditor-output.md` — nicht-kanonische Projektion (human-readable only)

### Run 2 (PR #148)
- **`artifacts/run-002-cross-file-run-bundle-validator/run.yml`** — kanonischer Run-Bundle-Envelope
- **`artifacts/run-002-cross-file-run-bundle-validator/auditor-output.yml`** — kanonischer YAML-Auditor-Output
- **`artifacts/run-002-cross-file-run-bundle-validator/measurement.yml`** — Run-2-Metriken
- `artifacts/run-002-cross-file-run-bundle-validator/auditor-output.md` — nicht-kanonische Projektion (human-readable only)

## Datenlage

- 2 PR-Datensätze erhoben (Run 1: PR #145, Run 2: PR #148).
- Run-1 Auditor-Verdict: **MISSING_EVIDENCE**. `unsupported_claim_count=5`, `validation_gap_count=3`.
- Run-2 Auditor-Verdict: **CONTRADICTION** (PR-Body behauptet 657 Tests; Repo-Zustand zeigt 56 Test-Methoden). `unsupported_claim_count=3`, `validation_gap_count=1`.
- PR-Metadaten (commits, additions, review_friction, rework, completion_time) nicht vollständig als Repo-Artefakt archiviert (`partial_repo_local` / `external_unverified`).
- Diff und changed-files nun repo-lokal archiviert (`changed-files.txt`, `pr-148.diff`, via git diff).
- Kein Wirkungsclaim möglich oder zulässig (zwei Messpunkte, keine Kontrollgruppe).

## Metriken-Vergleich (Run 1 vs. Run 2)

| Metrik | Run 1 (PR #145) | Run 2 (PR #148) |
|---|---|---|
| auditor_verdict | MISSING_EVIDENCE | CONTRADICTION |
| scope_drift_count | 0 | 0 |
| unsupported_claim_count | 5 | 3 |
| missing_locator_count | 0 | 0 |
| validation_gap_count | 3 | 1 |
| review_friction_count | 2 | 6 |
| rework_count | 1 | 1 |
| false_block_count | 0 | 0 |
| task_completion_time_observed | ~105 min | ~98 min |

Alle Metriken sind `external_unverified` oder `derived_from_auditor_output`; keine sind repo-lokal vollständig beobachtet.

## Interpretation Budget

### Allowed Claims

- Das Experiment legt einen Erhebungsrahmen für künftige PR-Daten an.
- Run 1 (PR #145) und Run 2 (PR #148) wurden erfasst; kanonische Auditor-Outputs in `auditor-output.yml`.
- Run-1-Verdict: MISSING_EVIDENCE; Run-2-Verdict: CONTRADICTION.
- Keine Wirksamkeitsclaims; zwei Messpunkte sind keine Grundlage für Generalisierung.

### Disallowed Claims

- Die Agent-Schicht reduziert Fehler.
- Die Agent-Schicht ist nützlich.
- Skill-Dateien sind bewertet.
- CI-/Script-Rückbindung ist gerechtfertigt.
- Aus zwei Messpunkten folgt irgendeine Wirkungsaussage.

## Evidence Basis

| Kategorie | Stand |
|---|---|
| Repo-lokal belegt (PASS) | Validator-Logik, Schemata, Regressionstests, generierte Artefakte (via auditor-output.yml) |
| derived_from_auditor_output | unsupported_claim_count, validation_gap_count |
| external_unverified | PR-Metadaten (commits, additions, deletions, review_friction, rework, completion_time, scope_drift) |
| MISSING_EVIDENCE | CI-Logs, make-Ausgaben, experiment-critic-Outputs, archivierte PR-Metadaten-Artefakte |
| CONTRADICTION | Run-2: PR-Body Testanzahl-Claim (657 vs. 56 tatsächliche Test-Methoden) |
| Nicht getestet | Wirkung, Vergleichbarkeit |
| Nicht vorhanden | Kontrollgruppe, mindestens 3 vergleichbare PRs für Zwischenauswertung |

## Nächste Schritte

Mindestens ein weiterer realer PR mit `experiment-critic` und `evidence-reconciliation-auditor`-Beteiligung als Datensatz erfassen. CI/make-Outputs und PR-Metadaten als Repo-Artefakte archivieren. Zwischenauswertung nach drei vergleichbaren PRs.
