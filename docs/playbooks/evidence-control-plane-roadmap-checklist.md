---
title: "Evidence-Control-Plane v1 — Roadmap-Checkliste"
status: draft
canonicality: exploratory
relations:
  - type: derived_from
    target: ../blueprints/blueprint-evidence-control-plane-v1.md
  - type: references
    target: reconciliation.md
  - type: references
    target: ../policies/interpretation-budget.md
  - type: references
    target: ../blueprints/blueprint-agent-operability.md
  - type: references
    target: ../blueprints/blueprint-agent-skill-minimal-layer-v0.1.md
---

# Evidence-Control-Plane v1 — Roadmap-Checkliste

## Status dieser Roadmap
Diese Datei ist eine operative **Planungscheckliste**, keine implementierte Control-Plane.

Diese Datei:

- erzeugt keine neue Enforcement-Regel.
- ersetzt keinen Blueprint und keine Policy.
- trifft keinen Wirksamkeitsclaim zur Agent/Skill-Schicht.
- gilt erst durch separate validierte PRs als umgesetzt.
- verwendet Checkboxen als geplante Umsetzungsschritte, nicht als Beleg bereits aktiver Enforcement-Regeln.

## PR 1 — Blueprint + Roadmap + Navigation Scaffold

> **Scope:** Reine Dokumentations- und Navigationsstruktur. Kein Code, keine Policy,
> kein Schema, kein Validator, keine Experiment-Runs.
>
> Die folgenden Haken bedeuten: Scaffold-Dokumente sind angelegt und verlinkt.
> Sie bedeuten **nicht**: Evidence-Control-Plane ist aktiv, Claims werden technisch blockiert,
> Policy/Schema/Validator/CI existieren.

- [x] `docs/blueprints/blueprint-evidence-control-plane-v1.md` angelegt und verlinkt.
- [x] Nicht-Ziele explizit: kein Agent/Skill-Wirksamkeitsclaim.
- [x] Architektur- und Falsifikationskriterien dokumentiert.
- [x] Diese Roadmap gegen Blueprint gespiegelt.
- [x] `docs/index.md` auf neue Blueprint/Playbook-Dokumente verlinkt.

**Was PR 1 ausdrücklich NICHT leistet:**
- Kein aktives Enforcement
- Keine Policy-Implementierung
- Kein Schema
- Kein Validator
- Keine CI-Erweiterung
- Kein Experiment-Run

## PR 2 — Policy-only

> **Scope:** Normative Policy-Grenzen. Kein Code, kein Schema, kein Validator,
> keine Make/CI-Aktivierung. PR 2 aktiviert kein technisches Enforcement.

- [x] `docs/policies/pr-run-evidence-policy.md` erstellt.
- [x] `docs/policies/artifact-boundary-policy.md` erstellt.
- [x] Policies deklarieren: keine aktive Enforcement-Regel ohne Schema/Script/Make/CI-Integration.

## PR 3 — Playbook pr-run-evidence-pack
- [x] `docs/playbooks/pr-run-evidence-pack.md` erstellt.

## PR 4 — Evidence-Pack-Schema + Fixtures
- [ ] `schemas/run-evidence-pack.v1.schema.json` erstellt.
- [ ] Fixtures angelegt (`tests/fixtures/claim_evidence/*`).
- [ ] Schema validiert (inkl. invalid status, fehlende `run_id`, path escape, leere Pfade).
- [ ] Keine rot eingebundenen Mainline-Tests.

## PR 5 — Claim-Evidence-Validator
- [x] `scripts/docmeta/validate_claim_evidence.py` implementiert.
- [x] `scripts/docmeta/test_validate_claim_evidence.py` grün.
- [x] Make-Targets ergänzt (`validate-claim-evidence`, `validate-claim-evidence-tests`).
- [x] CI-Step ergänzt (`.github/workflows/validate.yml`).
- [x] Semantische Claim-Evidence-Regeln als Validator + Mainline-Gate aktiv.
- [x] Gate prüft reale `evidence-pack.yml`/`evidence-pack.yaml`-Dateien; bei Abwesenheit erfolgt ein sauberer Skip-Hinweis.
- [x] Semantische Claim-Evidence-Regeln aktiv:
  - [x] No PASS without strong evidence status.
  - [ ] No PASS without existing/archived evidence file.
  - [x] `*.MISSING_EVIDENCE.*` dokumentiert Abwesenheit, beweist keinen Erfolg.
  - [x] Kein quantitativer Testcount-Claim ohne Test-Output-Artefakt.
  - [x] Kein CI-success-Claim ohne archivierte CI-Evidence.
  - [x] Kein `make validate`-Claim ohne Command-Output-Artefakt.
  - [x] Eigene Rule-ID für Command-Mismatch bei `make validate`-Claims (`MAKE_VALIDATE_WITH_COMMAND_MISMATCH`).
  - [x] `external_verified` ist nur mit `source` + `sha256` zulässig.
  - [x] `external_unverified` darf keinen PASS-Prozessclaim begründen.

## PR 6 — Run-Bundle-Kopplung
- [x] `schemas/experiment-run-bundle.v1.schema.json` erweitert.
- [x] `scripts/docmeta/validate_run_bundle.py` erweitert.
- [x] `scripts/docmeta/test_validate_run_bundle.py` erweitert.
- [x] `run.yml` referenziert Evidence-Pack (`path`, `contract`, `canonical`).
- [x] Legacy-Bundles nur im Warn-/Ratchet-Modus.
- [x] Echte repo-lokale Evidence-Pfade gegen Dateiexistenz prüfen.

## PR 7 — PR-Scope-Guard
- [x] `.vibe/pr-scope-policy.yml` erstellt.
- [x] `scripts/docmeta/validate_pr_scope.py` + Tests erstellt.
- [x] Make/CI integriert.
- [x] Guards blockieren Full-Diffs, übergroße Artefakte und unzulässige Self-Observation.

## PR 8 — PR-Template-Härtung
- [x] `.github/pull_request_template.md` ergänzt.
- [x] Claims-Sektion fordert Evidence-Artefakte für Testcount/CI/make/critic-Claims.
- [x] Missing-Evidence muss als fehlend markiert sein, nie als Erfolg.

## PR 9 — Ersten kontrollierten Agent/Skill-Run erfassen
- [x] Neuer Run mit vollständigem Evidence-Pack erfasst.
  - `experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/artifacts/run-002-controlled-agent-skill-run/`
  - run.yml, evidence-pack.yml, auditor-output.yml, measurement.yml, run_meta.json, agent-output.md, targeted-tests.txt, make-validate.txt
  - Vollständig für die kanonischen PR-9-Claims; metric-level gaps bleiben in measurement.yml explizit markiert: review_friction_count und rework_count = null/missing_evidence; task_completion_time_observed = "~60 min"/self_reported (nicht vergleichbar, kein Wirksamkeitsclaim).
- [x] Kein Reuse des alten nicht-gemergten Run-2-Forensik-Diffs.
- [x] Nur Measurement-System-Readiness, kein Wirksamkeitsclaim.
  - verdict.effect_claim_allowed: false; verdict.promotion_claim_allowed: false
  - interpretation_limits.causal_claim_allowed: false

## PR 10 — Weitere vergleichbare Runs erfassen
- [x] Mindestens zwei weitere vergleichbare Runs (insgesamt >= 3) durchgeführt.
  - run-005 (task:validator-test-windows-absolute-path-guard): `comparability_verdict: comparable`. `current_comparable_runs = 2`.
  - run-006 (task:validator-test-cross-run-changed-files-artifact-path-guard): `comparability_verdict: comparable`. `current_comparable_runs = 3`. Schwellenwert erreicht.
  - Comparability-Regeln sind durch comparability.yml dokumentiert und funktionieren korrekt.
  - Evidence: `artifacts/run-005-controlled-agent-skill-run/comparability.yml`, `artifacts/run-006-controlled-agent-skill-run/comparability.yml`
- [x] Claim-/Evidence-Metriken pro Run konsistent erhoben.
  - 8 Metriken in run-005 und run-006 strukturell vorhanden; 5/8 operativ belegt, review_friction_count und rework_count bleiben null/missing_evidence, task_completion_time_observed bleibt self_reported/nicht belastbar vergleichbar.
  - scope_drift_count: 0 in allen drei vergleichbaren Runs (002, 005, 006).
  - review_friction_count und rework_count: null/missing_evidence in Runs 002/005/006 — bis run-007-Pilot nicht behebbar.
  - Kein Wirksamkeitsclaim, kein Promotion-Claim, kein Kausalclaim.

## PR 11 — Cross-Run-Assessment
- [x] `cross-run-assessment.md` erstellt.
  - Pfad: `experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/results/cross-run-assessment.md`
- [x] Bewertet Messsystem-Reife vor Nutzenaussagen.
  - Vergleichsbasis: run-002, run-005, run-006. Drei Gegenhypothesen teilweise geprüft. Persistente Blocker dokumentiert.
- [x] Verdict gesetzt: `partially_ready`
  - Messsystem-Reife: 5/8 Metriken operativ belegt in engem Task-Korridor; 3/8 strukturell unvollständig (cross-run-assessment.md §6).
  - Mapping: Experiment-/Decision-Verdict bleibt `insufficient_proof` (decision.yml): kein usefulness claim, kein promotion claim.

## Durchgehende Qualitätsgates
- [ ] `claim_to_evidence_binding_rate` steigt.
- [ ] `unsupported_claim_count` sinkt.
- [ ] `validation_gap_count` sinkt.
- [ ] `contradiction_count` wird vor Merge abgefangen.
- [ ] `external_unverified_ratio` bleibt kontrolliert.

## Definition of Done
- [ ] Evidence-Control-Plane ist über Policy + Schema + Validator + Make + CI verbindlich verankert.
- [ ] Unbelegte PASS-Claims können nicht durchrutschen.
- [ ] Self-Observation und Artefakt-Grenzen sind technisch abgesichert.
