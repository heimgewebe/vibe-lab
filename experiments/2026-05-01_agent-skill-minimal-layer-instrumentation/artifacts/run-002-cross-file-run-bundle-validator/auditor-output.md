# Run-002 Auditor Output — Human Projection
<!-- Non-kanonisch. Kanonische Quelle: auditor-output.yml -->

## Übersicht

| Feld | Wert |
|---|---|
| run_id | run-002-cross-file-run-bundle-validator |
| PR | [#148](https://github.com/heimgewebe/vibe-lab/pull/148) |
| Titel | Add cross-file validator for experiment run bundles |
| Auditor | evidence-reconciliation-auditor |
| Datum | 2026-05-02 |
| Overall Verdict | **CONTRADICTION** |

## Claims

| ID | Text | Verdict |
|---|---|---|
| claim-001 | validate_run_bundle.py added (631 lines) | ✅ PASS |
| claim-002 | test_validate_run_bundle.py added (1530 lines) | ✅ PASS |
| claim-003 | 3 neue JSON-Schemas hinzugefügt | ✅ PASS |
| claim-004 | Makefile: validate-run-bundle Targets hinzugefügt | ✅ PASS |
| claim-005 | CI-Workflow: run-bundle Steps hinzugefügt | ✅ PASS |
| claim-006 | Experiment-Fixture aktualisiert (measurement.yml + run.yml) | ✅ PASS |
| claim-007 | manifest.yml: execution_ref für run.yml ergänzt | ✅ PASS |
| claim-008 | Alle 10 geänderten Dateien im deklarierten Scope | ⚠️ MISSING_EVIDENCE |
| claim-009 | PR-Body behauptet 657 Regressionstests | ❌ CONTRADICTION |
| claim-010 | make validate bestanden | ⚠️ MISSING_EVIDENCE |
| claim-011 | CI-Checks bestanden | ⚠️ MISSING_EVIDENCE |
| claim-012 | experiment-critic wurde genutzt | ⚠️ MISSING_EVIDENCE |

## Widersprüche

- PR-Body und PR-Beschreibung behaupten „657 regression tests". Repo-lokale Verifikation:
  `python3 scripts/docmeta/test_validate_run_bundle.py` → „Ran 56 tests in ~1.24s OK".
  Datei enthält 56 `def test_*`-Methoden. Tests laufen durch (56/56), aber die Zahl 657 ist
  durch den Repo-Zustand widerlegt.

## Fehlende Evidenz

- Archiviertes PR-Diff-Artefakt (Scope-Adherence nicht unabhängig verifikabel)
- make validate Output-Artefakt
- CI-Log (GitHub-API gibt 0 check_runs für PR #148 zurück)
- experiment-critic Output-Artefakt
- Archiviertes PR-Metadaten-Artefakt

## Empfohlene nächste Schritte

- make validate Output als Repo-Artefakt archivieren.
- experiment-critic Output archivieren, falls Critic-Nutzung behauptet wird.
- PR-Body-Testanzahl-Claims mit tatsächlichem Testcode abgleichen.
