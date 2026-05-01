---
title: "Blaupause — Agent/Skill Minimal Layer v0.1"
status: draft
canonicality: exploratory
origin: "agent-skill-minimal-layer-design"
implementation_status: not_implemented
authority: planning_blueprint
enforcement: none
motivation: "Reduce task ambiguity, scope drift, unsupported execution claims, and formal validity without semantic proof."
---

# Blaupause: Agent/Skill Minimal Layer v0.1

## Ziel

Minimale Agent-/Skill-Schicht zur Reduktion von:

1. Task-Unschärfe
2. Scope Drift
3. unbelegten Erfolgsclaims
4. formaler Gültigkeit ohne semantischen Nachweis

Nicht-Ziel: Zusätzliche Rollen- oder Prompt-Komplexität ohne belegbaren operativen Nutzen.

## Autoritätsgrenze

Diese Datei ist ein explorativer Blueprint.
Sie implementiert den Agent/Skill Minimal Layer nicht.
Sie erzeugt keine neue Enforcement-Autorität.
Verbindliche Durchsetzung entsteht erst durch spätere Agent-Dateien, Scripts, Schemas oder CI-Checks.

## Begriffliche Grenze

In dieser Blaupause führt „Skill“ keine neue Repository-Artefaktklasse ein.
Der Begriff bezeichnet wiederverwendbare Instruktionsmuster.
PR-1 legt keine dedizierten Skill-Dateien an.

## Evidenzbasis

Diese Blaupause reagiert auf bisher beobachtete Fehlerklassen:

- vage oder nicht ausführbare Tasks
- Scope Drift
- unbelegte Ausführungsclaims
- formal gültige, aber semantisch nicht hinreichend geprüfte Agentenartefakte

Diese Datei beweist nicht, dass Agent-/Skill-Dateien nützlich sind.
Sie definiert eine minimal prüfbare nächste Schicht.

## Zielarchitektur

```text
experiment-critic (bestehend)
  → Task-Contract-Härtung (Non-Ideal Task Guard)
experiment-operator (bestehend)
  → Ausführung
new: evidence-reconciliation-auditor (transitional)
  → Claim ↔ Evidence Reconciliation
new: evaluation document
  → Nutzennachweis/Falsifikation
später: Script-/CI-Enforcement statt reiner Agentendisziplin
```

## Folge-PR Scope: PR-1 normative Verdichtung

### Genau diese Änderungen

1. `.github/agents/experiment-critic.agent.md` erweitern (Abschnitt „Non-Ideal Task Guard“)
2. `.github/agents/evidence-reconciliation-auditor.agent.md` neu anlegen
3. `docs/evaluations/agent-skill-file-fruitfulness.md` neu anlegen

### Explizit nicht ändern

- `scripts/`
- `schemas/`
- `.github/workflows/`
- `docs/_generated/` (manuell)

## Geplanter Inhalt: Non-Ideal Task Guard

Task ist nicht execution-ready, wenn mindestens einer zutrifft:

- target files fehlen oder sind zu breit
- locator ist nicht eindeutig auflösbar
- change_type ist unklar
- validation trennt Erfolg nicht von no-op
- notwendiger Repo-Read wurde nicht durchgeführt
- exact_before/exact_after ist erforderlich, aber fehlt
- unabhängige Änderungen werden still kombiniert

Wenn zutreffend:

- `PARTIAL` oder `FAIL` (kein `PASS`)
- Gaps als `MISSING`, `UNKNOWN` oder `BLOCKED_BY`
- Task-Split statt Scope-Expansion bevorzugen

## Geplanter Inhalt: Evidence Reconciliation Auditor

### Zweck

Nachlaufprüfung, ob behauptete Änderungen und Validierungsergebnisse durch Repo-Evidence belegt sind.

### Kernprinzip

Kein Claim ohne Evidence.

### Feste Verdicts

- `PASS`
- `CLAIM_NOT_PROVEN`
- `CONTRADICTION`
- `MISSING_EVIDENCE`
- `OUT_OF_SCOPE`
- `NOT_REPRODUCIBLE`

### Pflichtausgabe

- Verdict
- Proven Claims
- Unproven Claims
- Contradictions
- Missing Evidence
- Required Next Proof

### Grenze

Transitional Agent; harte Enforcement-Autorität später in Scripts/CI.

## Geplanter Inhalt: Evaluation-Dokument

Datei: `docs/evaluations/agent-skill-file-fruitfulness.md`

Enthält:

- Frage: Wann verbessern Agent-/Skill-Dateien die Repo-Arbeit?
- Definitions: Agent file vs. Skill file
- Hypothese + Non-Hypothesis
- Evaluation Matrix
- Metriken:
  - scope_drift_count
  - unsupported_claim_count
  - missing_locator_count
  - validation_gap_count
  - review_friction_count
  - rework_count
  - false_block_count
  - task_completion_time_delta
- Falsifikationskriterien (über 3 vergleichbare PRs)
- Interpretation Budget (allowed/disallowed claims + evidence basis)

## Was bewusst nicht gebaut wird

- `task-contract-critic.agent.md` (redundant)
- `claim-budget.md` (bestehende Policy vorhanden)
- `locator-bound-change.md` (zu schmal; ggf. später strukturell lösen)
- `diagnose-before-patch.md` (bereits im Operator-Konzept enthalten)

## Geplante Checks nach Umsetzung

1. `make generate-blocking`
2. `make validate`

Regeln:

- Änderungen aus `make generate-blocking` ggf. mitführen
- bei `make validate`-Fehlern exakten Output dokumentieren, nicht heuristisch reparieren

## Folge-PR-Akzeptanzkriterien

Diese Kriterien gelten für die spätere PR-1-Umsetzung, nicht für diese Blueprint-Datei.

- Scope strikt auf die drei PR-1-Dateien
- Keine unerlaubten Nebenänderungen
- Guard-Logik eindeutig
- Auditor mit festen Verdicts + strukturierter Ausgabe
- Evaluation falsifizierbar, nicht dogmatisch

## Falsifikationsgrenze dieser Blaupause

Diese Blaupause ist zu verwerfen oder zu überarbeiten, wenn:

- die neue Agent-Schicht unbelegte Claims nicht reduziert
- Scope Drift nicht sinkt
- False Blocks stärker steigen als Fehler sinken
- die Schicht ohne spätere Script-/CI-Rückbindung bleibt
- neue Begriffsdrift zwischen Agent, Skill, Policy und Contract entsteht

## Risiko/Nutzen

- Nutzen: klare Autoritätsstruktur, bessere Claim-Prüfung, messbare Weiterentwicklung
- Risiko: anfängliche Scheinsicherheit ohne CI-Rückbindung
- Minderung: zuerst normativ stabilisieren, danach maschinell erzwingen
