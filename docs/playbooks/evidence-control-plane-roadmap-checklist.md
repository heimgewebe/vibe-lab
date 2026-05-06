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
- [ ] Neuer Run mit vollständigem Evidence-Pack erfasst.
- [ ] Kein Reuse des alten nicht-gemergten Run-2-Forensik-Diffs.
- [ ] Nur Measurement-System-Readiness, kein Wirksamkeitsclaim.

## PR 10 — Weitere vergleichbare Runs erfassen
- [ ] Mindestens zwei weitere vergleichbare Runs (insgesamt >= 3) durchgeführt.
- [ ] Claim-/Evidence-Metriken pro Run konsistent erhoben.

## PR 11 — Cross-Run-Assessment
- [ ] `cross-run-assessment.md` erstellt.
- [ ] Bewertet Messsystem-Reife vor Nutzenaussagen.
- [ ] Verdict gesetzt: `not_ready` | `partially_ready` | `ready_for_effect_evaluation`.

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
