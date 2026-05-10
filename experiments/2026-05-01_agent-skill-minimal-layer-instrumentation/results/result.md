---
title: "Agent/Skill Minimal Layer Instrumentation — Ergebnis"
status: draft
canonicality: operative
relations:
  - type: references
    target: evidence.jsonl
  - type: references
    target: cross-run-assessment.md
  - type: references
    target: decision.yml
---

# result.md — Ergebnis

## Status

**Drei vergleichbare kontrollierte Runs abgeschlossen; Cross-Run-Assessment-Schwelle erreicht.** 
Run 2 (run-002; PR#9), Run 5 (run-005; task:validator-test-windows-absolute-path-guard), Run 6 (run-006; task:validator-test-cross-run-changed-files-artifact-path-guard) sind alle als `comparability_verdict: comparable` oder `reference_only` dokumentiert.
Run 3 und Run 4 (run-003, run-004) haben `comparability_verdict: not_comparable` (PR-10-Rehearsal-Kontext, kein `independent_task_or_pr_ref`) und zählen nicht.
`current_comparable_runs = 3`.
Cross-Run-Assessment liegt in `results/cross-run-assessment.md` vor. **Kein result_assessment, kein promotion_readiness, kein usefulness claim** — siehe decision.yml und cross-run-assessment.md §6.

## Canonical Artifacts

**Vergleichbare Runs (in Cross-Run-Assessment einbezogen):**
- **`artifacts/run-002-controlled-agent-skill-run/`** — Referenzanker (PR#9, evidence-capture + Preflight-Diagnose); `comparability_verdict: reference_only`
- **`artifacts/run-005-controlled-agent-skill-run/`** — Small validator-test hardening (windows absolute path guard); `comparability_verdict: comparable`
- **`artifacts/run-006-controlled-agent-skill-run/`** — Small validator-test hardening (cross-run changed_files_artifact path regression); `comparability_verdict: comparable`

**Nicht vergleichbar (ausgeschlossen aus Cross-Run-Assessment):**
- **`artifacts/run-003-controlled-agent-skill-run/`** — Kandidaten-/Rehearsal-Run (PR#10, Session-Phase 1); `comparability_verdict: not_comparable`
- **`artifacts/run-004-controlled-agent-skill-run/`** — Kandidaten-/Rehearsal-Run (PR#10, Session-Phase 2); `comparability_verdict: not_comparable`

**Andere Instrumentierungsklasse (nicht vergleichbar):**
- **`artifacts/run-001-promotion-readiness-prepared-without-measurement/`** — Verschiedene Instrumentierungsklasse (promotion-readiness-prepared-without-measurement, nicht controlled-agent-skill-run); außerhalb Vergleichsbasis

## Datenlage (aus Cross-Run-Assessment)

**Vergleichbare Runs (3):** run-002, run-005, run-006
- Alle drei haben Auditor-Verdict: **PASS**
- Alle drei sind mit vollständigen run-bundle-Artefakten (run.yml, measurement.yml, auditor-output.yml, evidence-pack.yml, comparability.yml) archiviert

**Metrik-Abdeckung über die drei vergleichbaren Runs:**
- Konsistent erfasst: `scope_drift_count` (0 in allen), `unsupported_claim_count` (0 in allen), `missing_locator_count` (0 in allen), `validation_gap_count` (0 in allen), `false_block_count` (0 in allen)
- Persistently unmeasured: `review_friction_count` (null in allen), `rework_count` (null in allen)
- Teilweise: `task_completion_time_observed` (run-002: self_reported ~60 min; run-005, run-006: null)

**Gegenhypothesen-Status (siehe cross-run-assessment.md §2):**
- A (Operator-/Prompt-Effekt): unresolved
- B (Fallselektion): nicht_widerlegt — Task-Cluster vorhanden (zwei runs gleicher Klasse)
- C (Bewertungsbias): nicht_widerlegt — Auditor-Executor == Executor in allen drei Runs
- D (Replizierbarkeit): teilweise_repliziert — nur innerhalb einer Task-Klasse
- E (Dokumentation ≠ Ausführung): strukturell bestätigt

**Promotion-Blocker (detailliert in cross-run-assessment.md §5):**
- review_friction_count und rework_count: fehlende Archivierungs-Mechanik
- Task-Diversität: keine komplexen oder ambiguosen Tasks getestet
- Negativfälle: kein Run mit Auditor-FAIL-Verdict
- Unabhängige Bewertung: alle Runs selbst-auditiert (keine externe Validierung)

## Interpretation Budget

### Allowed Claims

- Das Messgerüst (run-bundle-Struktur, comparability.yml, evidence-reconciliation-auditor) kann über mehrere Runs hinweg konsistente Artefakte erfassen.
- Fünf von acht Metriken sind über die drei vergleichbaren Runs konsistent messbar (scope_drift, unsupported_claim, missing_locator, validation_gap, false_block).
- Run-bundle-Struktur reproduzierbar über die bisher geprüfte Vergleichsbasis; breitere Task-Typ-Varietät bleibt unbewiesen.
- Vergleichbarkeitsregeln (comparability.yml) funktionieren: Run-003/004 werden korrekt als `not_comparable` eingestuft.

### Disallowed Claims

- Die Agent-Schicht reduziert Fehler (kein outcome-level evidence).
- Die Agent-Schicht ist nützlich (kein Wirksamkeitsnachweis).
- Skill-Dateien sind bewertet (keine dedizierten Skill-Dateien im Repo).
- Promotion readiness (persistent metric gaps, keine unabhängige Validierung).
- result_assessment oder adoption_assessment (decision.yml verdict: insufficient_proof).
- Task-Homogenität überwunden (2/3 vergleichbare Runs: gleiche kleine Task-Klasse).

## Evidence Basis

| Kategorie | Stand |
|---|---|
| Repo-lokal belegt (PASS) | Alle run-002/005/006 Artefakte; comparability.yml für alle; auditor-output.yml mit PASS; measurement.yml für alle |
| Konsistent 0 über 3 Runs | scope_drift_count, unsupported_claim_count, missing_locator_count, validation_gap_count, false_block_count |
| Self-reported oder null | task_completion_time_observed (run-002: ~60 min self_reported; run-005/006: null) |
| MISSING_EVIDENCE | review_friction_count, rework_count (alle Runs); unabhängige Metrik-Validierung; task_completion_time (run-005/006) |
| Nicht vergleichbar (ausgeschlossen) | Run-003/004 (comparability_verdict: not_comparable, PR-10-Rehearsal-Kontext) |
| Andere Klasse (ausgeschlossen) | Run-001 (promotion-readiness-prepared-without-measurement, nicht controlled-agent-skill-run) |
| Nicht getestet | Wirkung; Kontrollgruppe; komplexe/ambigue Tasks; Negativfälle (kein FAIL-Verdict) |

## Nächste Schritte (Blocker für Verbesserung des Verdikts)

**Für Beseitigung des insufficient_proof (execution_assessment):**
1. review_friction_count und rework_count: Archivierungs-Mechanismus für externe Review-Events etablieren.
2. Task-Diversitätsnachweis: mindestens ein Run mit komplexem oder ambiguem Scope.
3. Negativfall-Nachweis: mindestens ein Run mit Auditor-FAIL-Verdict und konkretem Artefakt-Rückverweis.
4. Unabhängige Metrik-Validierung: Prüfung durch Reviewer, der nicht Executor ist.

(Detailliert in results/cross-run-assessment.md §5)
