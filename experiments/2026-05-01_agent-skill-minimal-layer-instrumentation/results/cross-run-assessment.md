---
title: "Cross-Run Assessment — Agent/Skill Minimal Layer Instrumentation"
status: draft
canonicality: operative
created: "2026-05-15"
relations:
  - type: derived_from
    target: ../../../docs/playbooks/evidence-control-plane-roadmap-checklist.md
  - type: references
    target: ../artifacts/run-002-controlled-agent-skill-run/measurement.yml
  - type: references
    target: ../artifacts/run-005-controlled-agent-skill-run/measurement.yml
  - type: references
    target: ../artifacts/run-006-controlled-agent-skill-run/measurement.yml
---

# Cross-Run Assessment — Messsystem-Reifegrad

## Zweck

Diese Datei bewertet, ob das Messsystem (Experiment-Scaffolding, Run-Bundle, Evidence-Pack, Auditor-Output) über mindestens drei vergleichbare Runs hinweg stabil, konsistent und aussagekräftig genug ist, um künftige Wirksamkeitsaussagen zu tragen.

**Nicht-Ziel:** Wirksamkeitsaussage zur Agent/Skill-Schicht. Diese Bewertung prüft das Messgerät, nicht das Gemessene.

---

## Vergleichbare Runs

| Run | Datum | Task | Auditor-Verdict | comparability_verdict |
|-----|-------|------|-----------------|----------------------|
| run-002 | 2026-05-06 | Evidence-capture und Preflight-Diagnose (PR 9) | PASS | comparable (Referenz) |
| run-005 | 2026-05-09 | Validator-Test-Härtung Windows-Pfad-Guard (PR 10) | PASS | comparable |
| run-006 | 2026-05-15 | Cross-Run-Assessment-Erstellung (PR 11) | PASS | comparable |

Nicht vergleichbare Runs (zur Vollständigkeit):
- run-001: Anderer Run-Typ (promotion-readiness-prepared-without-measurement), kein vergleichbarer Messsatz
- run-003, run-004: Kandidaten-/Rehearsal-Runs (PR 10), `comparability_verdict: not_comparable`

---

## Metriken über 3 vergleichbare Runs

| Metrik | run-002 | run-005 | run-006 | Trend | Belastbarkeit |
|--------|---------|---------|---------|-------|---------------|
| scope_drift_count | 0 | 0 | 0 | stabil | repo_local |
| unsupported_claim_count | 0 | 0 | 0 | stabil | derived_from_auditor_output |
| missing_locator_count | 0 | 0 | 0 | stabil | repo_local |
| validation_gap_count | 0 | 0 | 0 | stabil | derived_from_auditor_output |
| false_block_count | 0 | 0 | 0 | stabil | repo_local |
| review_friction_count | null | null | null | nicht erhoben | missing_evidence |
| rework_count | null | null | null | nicht erhoben | missing_evidence |
| task_completion_time_observed | ~60 min | ~20 min | ~30 min | self_reported | nicht vergleichbar |

---

## Befunde

### Was konsistent funktioniert

- Die Run-Bundle-Struktur (run.yml, evidence-pack.yml, auditor-output.yml, measurement.yml, comparability.yml, changed-files.txt) ist in allen drei Runs vollständig und korrekt archiviert.
- Die Comparability-Regeln (`independent_task_or_pr_ref`, `changed_files_artifact`) funktionieren: run-003/004 werden korrekt als `not_comparable` klassifiziert; run-002/005/006 korrekt als `comparable`.
- `scope_drift_count`, `unsupported_claim_count`, `missing_locator_count`, `validation_gap_count`, `false_block_count` sind in allen drei Runs konsistent messbar und durch repo-lokale Evidence belegt.
- `make validate` und der `test_validate_run_bundle.py`-Test-Suite laufen in allen Runs ohne Fehler durch.

### Persistente Lücken

1. **`review_friction_count`** — null in allen drei Runs. Kein Review-Kommentar-Artefakt archiviert. Ursache: die Metrik erfordert ein strukturiertes PR-Review-Protokoll, das bisher nicht als Pflichtartefakt eingeführt wurde.

2. **`rework_count`** — null in allen drei Runs. Kein Rework-Artefakt archiviert. Ursache: Rework-Ereignisse entstehen aus Review-Zyklen; ohne review_friction_count ist rework_count nicht messbar.

3. **`task_completion_time_observed`** — self_reported in allen Runs, nicht unabhängig verifizierbar. Nicht als Vergleichsmetrik geeignet.

Diese Lücken sind bekannt und dokumentiert; sie widerlegen die Hypothese nicht. Sie bedeuten: **zwei der acht Metriken sind operativ nicht erhoben**.

---

## Verdict

**`partially_ready`**

Das Messsystem ist operativ für 5 von 8 Metriken. Die Grundstruktur ist stabil. Die persistenten Lücken bei `review_friction_count` und `rework_count` sind methodisch dokumentiert, aber nicht behoben. Eine Wirksamkeitsbewertung der Agent/Skill-Schicht ist noch nicht zulässig.

### Bedingungen für `ready_for_effect_evaluation`

- `review_friction_count` und `rework_count` müssen in mindestens einem weiteren Run belegt (≠ null) sein, oder ihr dauerhaftes Fehlen muss als bewusste Designentscheidung formalisiert werden.
- Ein Baseline-Vergleich (Runs ohne Agent/Skill-Schicht) ist definiert oder explizit als außerhalb des Scope erklärt.
- Kein neuer Claim-Typ eingeführt, ohne dass der entsprechende Evidence-Typ definiert ist.

---

## Interpretation Budget

### Zulässige Aussagen

- Das Messgerät ist für 5 von 8 Metriken über drei unabhängige Runs hinweg konsistent und stabil.
- Die Comparability-Regeln funktionieren korrekt.
- Die Evidence-Pack- und Run-Bundle-Struktur ist als Datenerhebungsrahmen einsatzbereit.
- Zwei Metriken (review_friction_count, rework_count) sind methodisch offen — keine Aussage über ihre tatsächlichen Werte möglich.

### Unzulässige Aussagen

- Die Agent/Skill-Schicht reduziert Fehler oder erhöht Qualität.
- Null-Werte bei scope_drift_count etc. belegen Abwesenheit dieser Probleme (keine Kontrollgruppe).
- Das Messystem ist vollständig (zwei Metriken fehlen operativ).
- Die drei Runs sind repräsentativ für den allgemeinen Betrieb (alle Runs führten kleine, gut abgegrenzte Tasks aus).

---

## Nächste Schritte (nach diesem PR)

1. **`review_friction_count` operationalisieren** oder explizit als out-of-scope deklarieren und das Metrik-Set entsprechend anpassen.
2. **Baseline-Design**: definieren, wie Runs ohne Agent/Skill-Schicht gemessen würden (Kontrollgruppe), falls ein Wirksamkeitsclaim angestrebt wird.
3. **Erst dann**: Wirksamkeitsbewertung (`ready_for_effect_evaluation`) anstreben.
