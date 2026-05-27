---
title: "Playbook — Outcome-Evidence-Replication-Series Gate"
status: draft
canonicality: operative
---

# Outcome-Evidence-Replication-Series Gate

## Zweck

Minimales Gate, damit neue Outcome-Evidence-Runs nicht erneut nur run-lokale oder partiell unabhängige Evidenz produzieren.

## Mindestkriterien vor Outcome-Upgrade

- [ ] **Mindestens 4 vergleichbare Runs** im Serienkontext
- [ ] **Task-Diversität**: mindestens 3 unterschiedliche Task-Klassen, inkl. nicht-trivialem Scope
- [ ] **Auditor-Unabhängigkeit**:
  - Auditor != Executor
  - mindestens 2 Runs mit unabhängiger Prüfung
  - davon mindestens 1 Run mit **full_independence** (Human Reviewer oder anderes AI-System / andere Modellfamilie)
  - gleiche Modellfamilie + andere Session zählt nur als `partial_independence`, nicht als full independence
- [ ] **Negativkontrolle**: mindestens 1 Run mit erwartetem und stabil gehaltenem `CLAIM_NOT_PROVEN`


## Definition: vergleichbarer Run

Ein Run gilt im Serienkontext nur als vergleichbar, wenn alle Punkte erfüllt sind:

- gleicher Claim-/Outcome-Bezug wie die übrigen Serienruns
- konsistente Pflichtartefakte gemäß diesem Gate
- nachvollziehbar deklarierte Task-Klasse
- keine Vermischung von Scaffold-, Execution- und Outcome-Claims

## Pflichtartefakte pro Run

- [ ] `run.yml`
- [ ] `measurement.yml`
- [ ] `auditor-output.yml`
- [ ] `evidence-pack.yml`
- [ ] `comparability.yml`
- [ ] `review-events.yml` (falls Review/Rework-Claims gemacht werden)
- [ ] Timing-Artefakt (falls Dauer/Reibung behauptet wird)
- [ ] `make-validate.txt` oder CI-Beleg (falls Validität behauptet wird)

## Harte Regeln

1. **Kein Outcome-Upgrade** bei nur run-lokaler, self-reported oder partiell unabhängiger Evidence.
2. **Kein Outcome-Upgrade** ohne stabilen Negativfall, der `CLAIM_NOT_PROVEN` aufrechterhalten kann.
3. **Keine Adoption/Promotion-Aussage** aus Serienplanung allein.
