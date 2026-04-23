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

## Leitprinzip

- Decision-First statt Generator-First.
- Build nur bei erfüllten Stop-Kriterien.
- Sonst explizit dormant.
- Ein minimaler Meta-Decision-Typ mit Wirkung (`effects`) statt Decision-Taxonomie.

## Stop-Kriterien (harte Gates)

- [ ] Metrics-Gate erfüllt: mindestens 20 Evidence-Events und mindestens 3 `event_type`.
- [ ] Catalog-Staleness-Gate erfüllt: Semantik entschieden und mindestens 5 Catalog-Einträge, davon mindestens 2 reviewbar zeitdifferenziert.
- [ ] Reactive-Loop-Gate erfüllt: mindestens 1 realer Staleness-Fall im gewählten Sinn.

## Phase 1 - Plan-Reconciliation

- [ ] `docs/foundations/repo-plan.md` checkbox-weise auf Ist-Stand ziehen.
- [ ] `docs/blueprints/blueprint-agent-operability.md` von Zielbild auf Ist-Stand synchronisieren.
- [ ] `docs/blueprints/blueprint-agent-operability-phase-1c.md` Phase E/F eindeutig markieren.
- [ ] `docs/blueprints/blueprint-v2-roadmap.md` bereits umgesetzte Punkte nach "Erledigt" verschieben.
- [ ] Reconciliation-Begründung sichtbar dokumentieren (nicht implizit im Diff verstecken).

## Phase 2 - Minimaler Decision-Schnitt

- [ ] Einen einzigen Meta-Decision-Typ für `decisions/` festlegen: `system_decision`.
- [ ] Pflichtkern festlegen: `type`, `scope`, `claim`, `status`, `basis`, `date`, `reviewer`, `rationale`, `effects`.
- [ ] Ersten Referenzfall erstellen: `claim: metrics_enabled`, `effects: enables: metrics`.
- [ ] Optionalen Dormant-Fall erstellen: `claim: catalog_staleness_dormant`, `effects: disables: catalog_staleness`.
- [ ] Decision-Löschtest definieren: ohne aktivierende Decision ist der Schritt nicht freigegeben.

## Phase 3 - Freigegebene Arbeit

### Build

- [ ] Zwangspunkt implementieren: Metrics-Schritt ist standardmaessig gesperrt und wird nur durch eine aktive `system_decision` mit `effects: enables: metrics` freigegeben.
- [ ] Decision-aware Guard ergänzen: `make validate` oder ein dediziertes Script fällt mit Fehler, wenn Metrics ohne aktivierende Decision ausgeführt wird.
- [ ] Metrics-Generator implementieren (`scripts/docmeta/generate_metrics.py`).
- [ ] Metrics-Output erzeugen (`docs/_generated/metrics/trends.md`).
- [ ] Export-Abdeckung um genau ein reales Ziel erweitern.
- [ ] Agent-Operability Phase E Fixture-Sets auf 6-8 Fälle je Command ausbauen.

### Dormant

- [ ] Catalog-Staleness-Generator bleibt dormant bis Semantik + Gate erfüllt.
- [ ] Reactive Loop bleibt dormant bis realer Staleness-Fall existiert.
- [ ] Weak-Links/Knowledge-Gaps/Supersession bleiben dormant.

## Phase 4 - Stub-Zonen hart entscheiden

- [ ] Jede leere Zone als `dormant` oder `minimal-seed` markieren.
- [ ] Kein `queued` verwenden.
- [ ] Bei `minimal-seed` genau ein reales Artefakt liefern, kein Framework.

## Verifikation

- [ ] `make validate` ist grün.
- [ ] `make generate` ist grün.
- [ ] Aktivierte Schritte sind durch Decision + `effects` nachvollziehbar.
- [ ] Decision-Entzug prüfen: Entfernen von `effects: enables: metrics` blockiert den Metrics-Schritt nachweisbar.
- [ ] Keine stillen Aktivierungen ohne sichtbares Artefakt.
