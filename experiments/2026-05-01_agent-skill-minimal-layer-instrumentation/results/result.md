---
title: "Agent/Skill Minimal Layer Instrumentation — Ergebnis"
status: draft
canonicality: operative
---

# result.md — Ergebnis

## Status

**Run 2 erfasst.** Run 002 ist der erste kontrollierte Agent/Skill-Run mit vollständiger Evidence-Pack-Kopplung. Run 001 bleibt ein Vorläufer (`promotion_readiness_prepared_without_measurement`) mit Auditor-Verdict **MISSING_EVIDENCE** und zählt nicht als vergleichbarer kontrollierter Run.

## Canonical Artifacts

- **`artifacts/run-002-controlled-agent-skill-run/auditor-output.yml`** — kanonischer YAML-Auditor-Output für Run 002 (machine-readable source of truth)
- **`artifacts/run-002-controlled-agent-skill-run/measurement.yml`** — Run-002-Metriken
- **`artifacts/run-002-controlled-agent-skill-run/run.yml`** — kanonischer Run-Bundle-Envelope (inkl. Evidence-Pack-Referenz)
- **`artifacts/run-002-controlled-agent-skill-run/evidence-pack.yml`** — kanonisches Evidence-Pack für Run 002
- `artifacts/run-002-controlled-agent-skill-run/auditor-output.md` — nicht-kanonische Projektion (human-readable view only)
- `artifacts/run-001-promotion-readiness-prepared-without-measurement/*` — Vorläufer-Run mit MISSING_EVIDENCE (nicht vergleichbar)

## Datenlage

- Run 001 bleibt Vorläufer (`promotion_readiness_prepared_without_measurement`) mit Run-Level-Verdict **MISSING_EVIDENCE**; nicht als vergleichbarer kontrollierter Agent/Skill-Run gezählt.
- Run 002 ist der erste kontrollierte Agent/Skill-Run mit vollständiger Evidence-Pack-Kopplung und Run-Level-Auditor-Verdict **PASS**.
- `current_comparable_runs=1` (nur Run 002).
- Metric-level gaps bleiben sichtbar: `review_friction_count` und `rework_count` sind `null` mit `evidence_status: missing_evidence`.
- `task_completion_time_observed="~60 min"` ist `self_reported`, deskriptiv und nicht vergleichbar.
- Kein Wirksamkeitsclaim, kein Promotion-Claim, kein Kausalclaim.

## Interpretation Budget

### Allowed Claims

- Das Experiment führt den Evidence-Control-Plane-Pfad mit einem ersten kontrollierten Agent/Skill-Run fort.
- Run 001 ist Vorläufer mit MISSING_EVIDENCE und nicht vergleichbar.
- Run 002 ist als kontrollierter Run mit vollständiger Evidence-Pack-Kopplung dokumentiert.
- `current_comparable_runs=1`.
- Metric-level gaps (`review_friction_count`, `rework_count`) bleiben als `missing_evidence` sichtbar.
- `task_completion_time_observed` ist self-reported und nicht vergleichbar.

### Disallowed Claims

- Die Agent-Schicht reduziert Fehler.
- Die Agent-Schicht ist nützlich.
- Skill-Dateien sind bewertet.
- Aus Run 002 folgt ein Promotion-Verdict.
- Aus `~60 min` folgt eine Kausalaussage.
- Aus einem einzelnen vergleichbaren Run folgt irgendeine Wirkungsaussage.

## Evidence Basis

| Kategorie | Stand |
|---|---|
| Repo-lokal belegt (PASS) | Run-002-Bundle (`run.yml`, `measurement.yml`, `auditor-output.yml`, `run_meta.json`, `evidence-pack.yml`) |
| derived_from_auditor_output | Run-002 `unsupported_claim_count=0`, `validation_gap_count=0` |
| missing_evidence (metric-level) | `review_friction_count`, `rework_count` |
| self_reported | `task_completion_time_observed="~60 min"`, Run-002-Provenance |
| Nicht getestet | Wirkung der Agent/Skill-Schicht |
| Nicht vorhanden | Mindestens zwei weitere vergleichbare kontrollierte Runs für Cross-Run-Assessment |

## Nächste Schritte

PR 10 separat vorbereiten: zwei weitere vergleichbare kontrollierte Runs (`run-003-controlled-agent-skill-run`, `run-004-controlled-agent-skill-run`) im identischen Artefaktmuster erfassen. Danach erst PR 11 Cross-Run-Assessment.
