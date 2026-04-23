---
title: "Cross-Run-Auswertung: Generated Artifact Contract Validation"
status: draft
canonicality: operative
triggered_by: user-request-2026-04-23-complete-result-assessment
relations:
  - type: references
    target: evidence.jsonl
  - type: informed_by
    target: result.md
---

# Cross-Run-Auswertung — Generated Artifact Contract Validation

## 1. Evidence Aggregation (ohne Interpretation)

### 1.1 Quellen
- `results/evidence.jsonl`
- `artifacts/run-001-pr58/*` bis `artifacts/run-006-pr67/*`
- diese Datei als Cross-Run-Sammelpunkt

### 1.2 Aggregated observations list (dedupliziert)
1. Sechs Runs sind mit `run_meta.json` und `execution.txt` vorhanden (`run-001-pr58` bis `run-006-pr67`).
2. In allen Runs mit PR-Checks (`run-002` bis `run-006`) sind Validate/Diagnostics-Checks dokumentiert.
3. `run-003` hat `ci_blocking_failures: 0` und `unnecessary_commit_delta: 0`.
4. `run-004` enthält eine kontrollierte Schema-Abweichung (fehlender `context`-Key) mit anschließendem Fix.
5. `run-005` enthält erneut eine kontrollierte Schema-Abweichung derselben Klasse (fehlender `context`-Key) mit anschließendem Fix.
6. `run-006` wurde ohne kontrollierte semantische Injektion ausgeführt.
7. In `run-003`, `run-004`, `run-005`, `run-006` ist jeweils ein stale-`docs/_generated/system-map.md`-Pfad bei Konsolidierung dokumentiert.
8. `run-004`, `run-005`, `run-006` enthalten jeweils explizite Zeitmetriken (`detection_latency_seconds`, teils `fix_duration_seconds`).
9. Determinismus-Doppelrun (`make generate` zweimal) ist für `run-002`, `run-003`, `run-005`, `run-006` dokumentiert.
10. Für `run-001` sind `ci_blocking_failures` und `manual_regen_steps` als `not_measured` eingetragen.

### 1.3 Frequency patterns (wiederkehrende Befunde)
- Structural consolidation failure stale `system-map.md`: 4/4 Runs (`run-003` bis `run-006`), 100% in diesem Run-Cluster.
- Kontrollierte semantische Schema-Abweichung (`context` fehlt): 2/6 Runs (`run-004`, `run-005`), 33.3% gesamt.
- Zusätzlicher Fix-Commit nach PR-Open (`unnecessary_commit_delta > 0`): 4/6 Runs (`run-004`, `run-005`, `run-006`, `run-002`), 66.7% gesamt.
- Clean initial CI ohne Blocking-Failure: 1/6 Runs (`run-003`), 16.7% gesamt.
- Diagnoseklarheit hoch (`diagnosis_clarity_score >= 4`) in dokumentierten Scoring-Runs: 4/4 (`run-003`, `run-004`, `run-005`, `run-006`), 100%.

## 2. Pattern Extraction

### 2.1 Stable effects
- Reproduzierbare Trennung semantischer Schemafehler von strukturellen Konsolidierungsfehlern in der Evidenzklassifikation.
- Wiederkehrende Sichtbarkeit des stale-`system-map.md`-Pfads nach Artifact-Write in mehreren unabhängigen Runs.
- Hohe Diagnoseklarheit bei Fehlern mit konkreten file/line- oder contract-basierten Fehlermeldungen.

### 2.2 Failure modes
- Schema-required-key-Fehler in `results/evidence.jsonl` blockieren `validate` sofort (`run-004`, `run-005`).
- Konsolidierung nach Artifact-Write erzeugt canonical drift (`system-map.md`) mit zusätzlichem Fix-Commit (`run-003` bis `run-006`).
- Metrik-Vergleich über Runs ist geschwächt, wenn in frühen Runs Felder als `not_measured` vorliegen (`run-001`).

### 2.3 Boundary conditions
- Funktioniert gut, wenn Evidence-Einträge schemakonform sind und canonical regeneration direkt nach Artifact-Writes erfolgt.
- Funktioniert schlechter, wenn Artifact-Writes nach initial sauberem Lauf erfolgen, ohne unmittelbar canonical nachzuziehen.
- Funktioniert eingeschränkt für harte Trendvergleiche, wenn Run-Instrumentierung nicht über alle Iterationen harmonisiert ist.

### 2.4 Explizite Trennung nach Wirkungsebene
- Structural effects:
  - Wiederkehrender canonical-contract drift bei `system-map.md` nach Artifact-Konsolidierung.
  - Zusätzliche Regenerations-Commits in mehreren Runs.
- Operational effects:
  - CI-Fehler werden reproduzierbar als blocking Events sichtbar.
  - Fix-Zyklen sind klein und mit klaren Schritten dokumentierbar.
- Epistemic effects:
  - Fehlerursachen sind klar referenzierbar (Datei/Key/Check), dadurch höhere Nachvollziehbarkeit.
  - Aussagekraft für "Friktion insgesamt reduziert" bleibt durch ungleich instrumentierte Runs begrenzt.

## 3. Hypothesis Evaluation

Originalhypothese:
> canonical / derived / ephemeral + CI splitting reduces or clarifies friction

```yaml
hypothesis_status:
  confirmed:
    - "clarifies friction": Friktionstypen sind in den Runs klar getrennt sichtbar (semantic vs structural).
    - "clarifies friction": Fehlerlokalisierung ist konsistent hoch (diagnosis_clarity_score 4-5 in Scoring-Runs).
  falsified:
    - "reduces friction" als robuste Gesamtaussage ist durch den Datensatz nicht belegt.
  unresolved:
    - Wie viel der strukturellen Friktion workflowbedingt vs. architekturbedingt ist.
    - Ob mit vollständig harmonisierter Instrumentierung eine belastbare Netto-Reduktion messbar wird.
```
