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

<!-- markdownlint-disable-next-line MD025 -->
# Playbook: Plan Execution Checklist

Ziel: Restarbeiten als kleine, prüfbare Schritte umsetzen, ohne Meta-Overengineering.

## Leitregel (Obergesetz)

```text
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

- [x] Minimalen `system_decision`-Typ definieren: Ablage `decisions/system/*.yml`; Pflichtfelder `type`, `scope`, `claim`, `status`, `basis`, `date`, `reviewer`, `rationale`, `effects`
- [x] `effects` eindeutig festgezogen (Contract):

  ```yaml
  effects:
    enables:
      - metrics
    disables:
      - catalog_staleness
  ```

- [x] Erstes reales Artefakt: `decisions/system/2026-04-23-metrics-enabled.yml`, `status: active`, `effects.enables: [metrics]`
- [x] Optional umgesetzt: `decisions/system/2026-04-23-catalog-staleness-dormant.yml`, `effects.disables: [catalog_staleness]`
- [x] Decision-aware Guard gebaut (`scripts/docmeta/check_system_decisions.py`): `effects.disables` übersteuert `effects.enables`; ohne wirksames Enable bleibt das Gate zu
- [x] Guard als dediziertes Ziel eingebunden: `make check-decisions` (noch nicht global in `make validate`)
- [x] Metrics-Generator implementiert (`scripts/docmeta/generate_metrics.py`), Output: `docs/_generated/metrics/trends.md`
- [x] Metrics-Pilot in den Standard-Generate-Vertrag eingehängt (`generate-derived` ruft `generate-metrics` auf)
- [x] Drift-Bericht (Pilot, kurz):
  - `catalog_staleness` bleibt dormant: keine festgezurrte Semantik und keine review-cycle Felder
  - `reactive_loop` bleibt dormant: kein freigegebener realer Staleness-Fall
  - keine weiteren Generatoren gebaut: Pilot bewusst auf Decision + Guard + Metrics begrenzt

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
- [x] Catalog-Staleness: dormant bis Semantik per Decision festgelegt

## Verifikation

- [x] `make validate` ist grün
- [x] Guard schlägt fehl ohne aktive Decision
- [x] Decision-Entzug prüfen: Entfernen von `effects.enables: [metrics]` blockiert Metrics nachweisbar
- [x] Metrics-Ausgabe ist datengetragen, nicht leer (>=20 Events, >=3 event_type, Aggregationen vorhanden, Quellpfade vorhanden)
- [x] Drift-Bericht vorhanden: was wurde dormant gelassen und warum
