---
title: "Failure Modes: Generated Artifact Contract Validation"
status: draft
canonicality: operative
triggered_by: user-request-2026-04-23-complete-result-assessment
relations:
  - type: references
      target: results/evidence.jsonl
  - type: references
      target: results/cross-run-assessment.md
---

# Failure Modes — Generated Artifact Contract Validation

## Konkrete Failure Modes (run-gebunden)

1. **Schema-required-key fehlt in Evidence-Eintrag**
     - Beobachtet in: `run-004-pr63`, `run-005-pr64`
     - Symptom: `validate` blockiert wegen fehlendem required key `context` in `results/evidence.jsonl`
     - Auswirkung: mindestens ein zusätzlicher Fix-Zyklus vor grünem CI

2. **Structural consolidation drift nach Artifact-Write**
     - Beobachtet in: `run-003-pr62`, `run-004-pr63`, `run-005-pr64`, `run-006-pr67`
     - Symptom: stale `docs/_generated/system-map.md` im canonical-contract-Check
     - Auswirkung: zusätzlicher Regenerations-Commit trotz initial sauberem oder fast sauberem Lauf

3. **Uneinheitliche Messabdeckung über Runs**
     - Beobachtet in: `run-001-pr58` vs. spätere Runs
     - Symptom: zentrale Vergleichsmetriken (`ci_blocking_failures`, `manual_regen_steps`) in frühen Daten als `not_measured`
     - Auswirkung: eingeschränkte belastbare Aussagen zu Netto-Trends über alle Runs

## Wann der Ansatz versagt oder kontraproduktiv wird

- Wenn schemapflichtige Evidence-Felder nicht strikt eingehalten werden.
- Wenn Artifact-Konsolidierung ohne unmittelbaren canonical-Regenerationsschritt erfolgt.
- Wenn aus teilweise instrumentierten Runs generalisierte Effizienzbehauptungen abgeleitet werden.

## Grenzen der Evidenz

- Stichprobe: sechs dokumentierte Runs in einem Repository-Kontext.
- Externe Validitaet: nicht fuer andere Repos/CI-Topologien belegt.
- Vergleichbarkeit: fruehe Runs haben unvollstaendige Messfelder, dadurch eingeschraenkte Trendhaerte.

## Risiko bei Fehlanwendung

Ein blinder Fokus auf "weniger rote CI" ohne Friktionstyp-Trennung kann strukturelle Drift maskieren oder spaeter teurer machen.
