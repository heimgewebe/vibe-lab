---
title: "Playbook: Plan Execution Checklist"
status: active
canonicality: operative
schema_version: "0.1.0"
created: "2026-04-23"
updated: "2026-04-23"
author: "GitHub Copilot"
triggered_by: "user-request-plan-execution-checklist-2026-04-23"
relations:
  - type: references
    target: ../foundations/repo-plan.md
  - type: references
    target: ../blueprints/blueprint-v2-roadmap.md
  - type: references
    target: ../blueprints/blueprint-agent-operability-phase-1c.md
  - type: references
    target: ../../CONTRIBUTING.md
tags:
  - playbook
  - checklist
  - reconciliation
  - decision-first
---

# Playbook: Plan Execution Checklist

Ziel: Restarbeiten als kleine, prüfbare Schritte umsetzen, ohne Meta-Overengineering.

## Leitregel (Obergesetz)

```
Keine neue Automatisierung, kein neuer Generator, kein neuer Repo-Mechanismus
ohne sichtbaren Zwangspunkt + sichtbaren Abschaltpunkt.
```

Jeder neue Mechanismus braucht Aktivierungsgrund, klare Deaktivierung und Nachweis.

**5-Fragen-Test:** Klein? Sichtbar? Reversibel? Wirklich freigeschaltet? Fällt sauber aus ohne Freigabe?

## Nicht jetzt (explizit ausgesperrt)

- Phase D groß öffnen; mehrere Generatoren parallel bauen
- `decisions/` zu einer allgemeinen Meta-Verfassung aufblasen
- Reactive Loops ohne echten Signalbedarf; `catalog/technologies/` künstlich befüllen
- Catalog-Staleness, Reactive Loop, Weak Links, Knowledge Gaps, Supersession gleichzeitig

## Phase 1 — Decision-Kern + Guard (operativer Kern zuerst)

- [ ] Minimalen `system_decision`-Typ definieren: Ablage `decisions/system/*.yml`; Pflichtfelder `type`, `scope`, `claim`, `status`, `basis`, `date`, `reviewer`, `rationale`, `effects[]`
- [ ] Erstes reales Artefakt: `decisions/system/2026-04-23-metrics-enabled.yml`, `status: active`, `effects: [enables: metrics]`
- [ ] Optional: `decisions/system/2026-04-23-catalog-staleness-dormant.yml`, `effects: [disables: catalog_staleness]`
- [ ] Decision-aware Guard bauen (`scripts/docmeta/check_system_decisions.py`): schlägt fehl, wenn kein aktives `system_decision` mit `effects.enables: metrics` existiert
- [ ] Guard in `make validate` oder dediziertes `make check-decisions` einbinden
- [ ] Metrics-Generator implementieren (`scripts/docmeta/generate_metrics.py`), Output: `docs/_generated/metrics/trends.md`
- [ ] Drift-Bericht: Was wurde bewusst nicht gebaut und warum

## Phase 2 — Plan-Reconciliation (danach, nur so weit wie nötig)

- [ ] `docs/foundations/repo-plan.md` checkbox-weise auf Ist-Stand ziehen
- [ ] `docs/blueprints/blueprint-agent-operability.md` `status: active` statt `idea`
- [ ] `docs/blueprints/blueprint-agent-operability-phase-1c.md` Phase F als `satisfied_by_dry_run` markieren
- [ ] `docs/blueprints/blueprint-v2-roadmap.md` Phase 2 nach „Erledigt" verschieben

## Phase 3 — Agent-Operability Phase E (parallel mit Phase 1)

- [ ] Fixture-Erweiterung auf 6–8 Fälle je Command (`hash_mismatch`, `unsupported_canon`, `integrity_mismatch`, promotion-nah)

## Phase 4 — Stub-Zonen hart entscheiden

- [ ] Jede leere Zone als `dormant` oder `minimal-seed` markieren (kein `queued`)
- [ ] Bei `minimal-seed`: genau ein reales Artefakt, kein Framework
- [ ] Reactive Loop: dormant lassen bis echter Staleness-Fall existiert
- [ ] Catalog-Staleness: dormant bis Semantik per Decision festgelegt

## Verifikation

- [ ] `make validate` ist grün
- [ ] Guard schlägt fehl ohne aktive Decision
- [ ] Decision-Entzug prüfen: Entfernen von `effects: enables: metrics` blockiert Metrics nachweisbar
- [ ] Metrics-Ausgabe ist datengetragen, nicht leer
- [ ] Drift-Bericht vorhanden: was wurde dormant gelassen und warum
