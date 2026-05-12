---
title: "Roadmap — Koordination offener Arbeitsstränge"
status: active
canonicality: navigation
role: roadmap_index
created: "2026-05-10"
updated: "2026-05-12"
relations:
  - type: references
    target: masterplan.md
  - type: references
    target: foundations/vision.md
  - type: references
    target: foundations/repo-plan.md
  - type: references
    target: index.md
  - type: references
    target: blueprints/blueprint-agent-operability.md
  - type: references
    target: blueprints/blueprint-agent-operability-phase-1c.md
  - type: references
    target: blueprints/blueprint-evidence-control-plane-v1.md
  - type: references
    target: blueprints/blueprint-v2-roadmap.md
  - type: references
    target: blueprints/blueprint-v2.md
  - type: references
    target: blueprints/blueprint-agent-skill-minimal-layer-v0.1.md
  - type: references
    target: evaluations/agent-skill-file-fruitfulness.md
  - type: references
    target: evaluations/replay-gap-cross-diagnosis-rrg01-rrg02.md
  - type: references
    target: evaluations/rrg03-remediation-strategy-comparison.md
  - type: references
    target: playbooks/evidence-control-plane-roadmap-checklist.md
  - type: references
    target: playbooks/plan-execution-checklist.md
  - type: references
    target: policies/interpretation-budget.md
  - type: references
    target: ../decisions/process/2026-04-30-rrg03-remediation-boundary.yml
  - type: references
    target: ../decisions/process/2026-05-01-rrg-v02-remediation-preimage.yml
  - type: references
    target: ../decisions/process/p5-validator-scope-boundary.yml
  - type: references
    target: ../decisions/system/2026-04-23-metrics-enabled.yml
  - type: references
    target: ../decisions/system/2026-04-23-catalog-staleness-dormant.yml
---

# Roadmap — Koordination offener Arbeitsstränge

> **Etymologie:** „Roadmap" kommt aus dem Englischen: *road* = Straße/Weg, *map* = Karte. Im Repo-Kontext bedeutet das nicht „Herrschaftsdokument", sondern Wegkarte: Sie zeigt Pfade, Abhängigkeiten und offene Entscheidungen, bleibt aber von den eigentlichen Quellen abhängig.

---

## 0. Zweck und Grenzen

Diese Datei koordiniert offene Arbeit im Vibe-Lab-Repository. Sie ist Navigation und Koordinationsfläche — keine normative Wahrheit.

**Was diese Datei darf:**
- Offene Arbeitsstränge aus bestehenden Quellen sichtbar machen
- Status und Priorität aus Quellen ableiten oder explizit als Roadmap-Einschätzung kennzeichnen
- Abhängigkeiten und offene Entscheidungspunkte bündeln

**Was diese Datei nicht darf:**
- Neue fachliche Wahrheiten, Schlüsse oder Promotion-Entscheidungen erzeugen
- Quellenwahrheit ersetzen oder überschreiben
- Statusangaben ohne Quellenbelege machen
- Generierte Artefakte manuell editieren

**Konflikt-Regel:** Bei Widerspruch zwischen dieser Roadmap und einer referenzierten Quelle gilt die Quelle. Die Roadmap ist abgeleitet, nicht primär.

**Geltende Wahrheitshierarchie** (aus `repo.meta.yaml` und `AGENTS.md`):

```
Kanonisch: repo.meta.yaml, AGENTS.md, agent-policy.yaml, contracts/*, schemas/*
Grundlagen: docs/foundations/vision.md, docs/foundations/repo-plan.md
Operativ:   README.md, CONTRIBUTING.md, .vibe/*
Navigation: docs/index.md, docs/roadmap.md  ← diese Datei
Diagnose:   docs/_generated/*
```

---

## 1. Quellenmodell

Die folgende Tabelle listet die Quellen, aus denen diese Roadmap Koordinationsinformationen ableitet.

| Quelle | Typ | Rolle | Darf Roadmap-Status beeinflussen? | Bemerkung |
|--------|-----|-------|----------------------------------|-----------|
| `docs/masterplan.md` | operative | Zielbild, Phasenmodell | Ja | Phasen A–D, epistemische Zustände |
| `docs/foundations/vision.md` | foundational | Systemvision | Ja | Layer-Architektur, Kernprinzipien |
| `docs/foundations/repo-plan.md` | foundational | Umsetzungsplan mit Checklisten | Ja | Phasenchecklisten mit aktuellem Ist-Stand |
| `docs/blueprints/blueprint-agent-operability.md` | exploratory | Minimaler Agent-Operability-Kern | Ja | Phasen 1–3, Umsetzungsstand |
| `docs/blueprints/blueprint-agent-operability-phase-1c.md` | exploratory | Systemverankerung Phase 1c | Ja | Phasen A–F mit Checkboxen |
| `docs/blueprints/blueprint-evidence-control-plane-v1.md` | exploratory | Evidence-Control-Plane v1 | Ja | Status: draft, nicht aktiv |
| `docs/blueprints/blueprint-v2-roadmap.md` | navigation | Offene Punkte Blueprint v2 | Ja | Sichtbarkeitskriterien pro Phase |
| `docs/blueprints/blueprint-v2.md` | operative | Epistemische-Reife-Delta v1→v2 | Ja | Fehlklassen und Hebel |
| `docs/blueprints/blueprint-agent-skill-minimal-layer-v0.1.md` | exploratory | Agent/Skill Minimal Layer | Ja | Status: draft; PR-1 Scope definiert |
| `docs/evaluations/agent-skill-file-fruitfulness.md` | diagnosis | Fruchtbarkeits-Evaluation Agent/Skill | Ja | Evaluation-Plan, noch kein Verdict |
| `docs/evaluations/replay-gap-cross-diagnosis-rrg01-rrg02.md` | operative | Cross-Diagnose RRG-01/RRG-02 | Ja | RRG-01/02 fixture-proven seit 2026-05-01 |
| `docs/evaluations/rrg03-remediation-strategy-comparison.md` | operative | Remediation-Strategie-Vergleich | Ja | Kein finaler Gewinner, proposed |
| `docs/playbooks/evidence-control-plane-roadmap-checklist.md` | exploratory | PR-Checkliste Evidence-Control-Plane | Ja | Enthält ursprüngliche PR-10/11-Checkliste; aktueller Status siehe RM-002 |
| `docs/playbooks/plan-execution-checklist.md` | operative | Plan-Ausführungscheckliste | Ja | Phase 3/4 teilweise offen |
| `docs/playbooks/reconciliation.md` | operative | Prozess-Reconciliation | Nein (Methode, kein Arbeitsstrang) | Referenz für Prozess |
| `docs/playbooks/pr-run-evidence-pack.md` | operative | Evidence-Pack-Struktur | Nein (Methode) | |
| `docs/playbooks/build-reliable-prompt.md` | operative | Prompt-Qualität | Nein (Bibliothek) | |
| `docs/policies/interpretation-budget.md` | operative | Claim-Evidence-Guard | Ja, bei Adoption-Entscheidungen | Promotion-Pflicht |
| `docs/policies/pr-run-evidence-policy.md` | operative | Normative Claim-Grenzen | Nein (Policy-only) | |
| `docs/policies/artifact-boundary-policy.md` | operative | Artefaktgrenzen | Nein (Policy-only) | |
| `docs/policies/privacy-and-ethics.md` | operative | Datenschutz/Ethik | Nein | |
| `decisions/process/2026-04-30-rrg03-remediation-boundary.yml` | operative | RRG-03 Boundary-Entscheidung | Ja | Status: proposed |
| `decisions/process/2026-05-01-rrg-v02-remediation-preimage.yml` | operative | RRG-v0.2 Preimage | Ja | Status: proposed, kein Patch |
| `decisions/process/p5-validator-scope-boundary.yml` | operative | Validator-Scope-Grenzen Phase 5 | Ja | Status: out_of_scope_documented |
| `decisions/system/2026-04-23-metrics-enabled.yml` | operative | Metrics aktiviert | Ja | Status: active |
| `decisions/system/2026-04-23-catalog-staleness-dormant.yml` | operative | Catalog-Staleness dormant | Ja | Status: dormant |

---

## 2. Aktive Arbeitsstränge

> **Legende zu Spalten:**
> - *Quelle-Status*: nur aus Quelle übernommen (belegt)
> - *Roadmap-Einschätzung*: abgeleitet aus Quelle, als Einschätzung gekennzeichnet
> - *Evidenzgrad*: `belegt` = aus Quelle direkt lesbar; `plausibel` = logisch abgeleitet; `unklar` = unzureichende Datenbasis

| ID | Arbeitsstrang | Quelle(n) | Quelle-Status | Roadmap-Einschätzung | Nächster Schritt | Blocker | Priorität | Evidenzgrad |
|----|---------------|-----------|---------------|----------------------|-----------------|---------|-----------|-------------|
| RM-001 | Agent-Operability Phase E — Fixture-Erweiterung | `blueprints/blueprint-agent-operability-phase-1c.md` §Phase E; `playbooks/plan-execution-checklist.md` Phase 3 | Phase E teilweise begonnen: Minimal-Fixtures vorhanden, erweiterter Drift-Smoke-Set offen | Roadmap-Einschätzung: handhabbar, keine harten Blocker | Fixture-Sammlung auf 6–8 Fälle pro Command ausbauen (insbesondere Drift-Fälle für Handoff-Validator) | none | P2 | belegt |
| RM-002 | Evidence-Control-Plane — Sufficient Runs gesammelt, Outcome-Evidence weiter offen | `playbooks/evidence-control-plane-roadmap-checklist.md` PR 10/11; `experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/results/decision.yml` (Verdict: insufficient_proof); `experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/artifacts/run-007-review-rework-outcome-evidence-pilot/review-events.yml`; `experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/artifacts/run-007-review-rework-outcome-evidence-pilot/measurement.yml`; `experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/artifacts/run-008-negative-case-independent-audit-timing/auditor-output.yml`; `experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/artifacts/run-008-negative-case-independent-audit-timing/evidence-pack.yml`; `experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/artifacts/run-008-negative-case-independent-audit-timing/measurement.yml`; `experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/artifacts/run-008-negative-case-independent-audit-timing/timing.txt`; `experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/artifacts/run-009-independent-task-diversity-validation/auditor-output.yml`; `experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/artifacts/run-009-independent-task-diversity-validation/comparability.yml`; `experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/artifacts/run-009-independent-task-diversity-validation/measurement.yml`; `experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/artifacts/run-009-independent-task-diversity-validation/timing.txt`; `experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/results/evidence.jsonl` (iteration 11) | PR 10: ✓ abgeschlossen. 3 vergleichbare Runs gesammelt (run-002, run-005, run-006); PR 11 Cross-Run-Assessment liegt vor, Verdict: `insufficient_proof` wegen Metrik-Lücken/Validierungsblockern. ✓ Review/Rework-Archivierungsmechanismus schema-backed (`schemas/review-events.v1.schema.json`, `.vibe/review-rework-artifact.contract.md` v0.2). ✓ Erster echter Outcome-Evidence-Pilot vorhanden: run-007 mit archiviertem `review-events.yml`; `measurement.yml` dokumentiert `review_friction_count`=`repo_local` und `rework_count`=`repo_local` (single-run Pilot, kein generelles Verdict). ✓ Outcome-Evidence-Negativfall pilotiert: run-008 dokumentiert ein schema-valides `CLAIM_NOT_PROVEN` bei nur partieller Auditor-Unabhängigkeit und archiviert `task_completion_time_observed` über `timing.txt` repo-lokal. ✓ Task-Diversität partiell adressiert: run-009 claim-002 PASS (Multi-artifact-Scaffold-Synthesis außerhalb validator-test-hardening-Cluster); Auditor-Unabhängigkeit weiterhin CLAIM_NOT_PROVEN; Timing-Semantik verbessert auf self_reported mit explizitem capture_mode, evidence_status und upgrade_path. | Nächste Phase: Outcome-Evidence-Mechanismus ist in run-007 pilotiert; Negativfall und repo-lokale Zeitmessung sind in run-008 pilotiert; Task-Diversität ist in run-009 partiell adressiert; offen: (1) unabhängiger Auditor / unabhängige Metrik-Validierung (vollständige Unabhängigkeit), (2) zweiter unabhängiger Run in weiterer Task-Klasse für stärkere Replikation, (3) Timing-Upgrade von self_reported auf repo_local oder external_verified | Auditor und Executor bleiben nur partiell getrennt (CLAIM_NOT_PROVEN in run-008 und run-009); kein vollständig unabhängiger Review; Task-Diversität einmalig belegt aber noch nicht repliziert; Timing ist self_reported, noch nicht unabhängig validiert | P1 | belegt |
| RM-003 | RRG-v0.2 Remediation — Drei getrennte Drift-Klassen | `evaluations/rrg03-remediation-strategy-comparison.md`; `evaluations/replay-gap-cross-diagnosis-rrg01-rrg02.md`; `decisions/process/2026-05-01-rrg-v02-remediation-preimage.yml` | Alle drei RRGs fixture-proven (2026-05-01); Preimage proposed; kein Patch | Roadmap-Einschätzung: Getrennte Probe-Entscheide für jede Drift-Klasse vor Implementierung nötig | Für jede Drift-Klasse einen separaten v0.2-Probe-Entscheid vorbereiten; mit RRG-01 (`exact_before_hash`) beginnen (stärkster Kandidat laut Preimage) | Hypothesen noch nicht durch Implementierungsbeleg eingegrenzt; keine Probe ohne Strategie-Entscheid | P2 | belegt (fixture_only) |
| RM-004 | Blueprint v2 — Phase 2 Falsifizierbarkeitsschutz-Ausbau | `blueprints/blueprint-v2-roadmap.md` Phase 2 / Phase 1 (aktiv, Dry-Run) | Phase 1 (Dry-Run): aktiv, Dry-Run-Report stabil; Phase 2 (Freeze-List / Hard-Fail für neue Experimente): offen | Roadmap-Einschätzung: Phase 2 erfordert menschliche Governance-Entscheidung über Staffelungsmechanismus | Erst-Experiment freiwillig mit `falsifiability`-Block promovieren; danach Staffelungsmechanismus (Grandfather-Liste) entscheiden | Staffelungsmechanismus-Design offen (deterministischer Stichtags-Mechanismus nicht festgelegt) | P3 | plausibel |
| RM-005 | Agent/Skill Minimal Layer — Usefulness-Evaluation (Minimum-Daten erreicht, Outcome-Blocker offen) | `blueprints/blueprint-agent-skill-minimal-layer-v0.1.md`; `evaluations/agent-skill-file-fruitfulness.md`; `experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/results/decision.yml`; `experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/artifacts/run-007-review-rework-outcome-evidence-pilot/comparability.yml`; `experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/artifacts/run-007-review-rework-outcome-evidence-pilot/measurement.yml`; `experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/artifacts/run-008-negative-case-independent-audit-timing/auditor-output.yml`; `experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/artifacts/run-008-negative-case-independent-audit-timing/evidence-pack.yml`; `experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/artifacts/run-008-negative-case-independent-audit-timing/comparability.yml`; `experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/artifacts/run-008-negative-case-independent-audit-timing/measurement.yml`; `experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/artifacts/run-009-independent-task-diversity-validation/auditor-output.yml`; `experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/artifacts/run-009-independent-task-diversity-validation/comparability.yml`; `experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/artifacts/run-009-independent-task-diversity-validation/measurement.yml`; `experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/results/evidence.jsonl` (iteration 11) | draft; ✓ Evaluation-Mindestschwelle bleibt über 3 vergleichbare Runs erreicht (run-002, run-005, run-006). run-007, run-008 und run-009 sind `not_comparable` und zählen **nicht** als weitere Usefulness-Runs. Verdict bleibt `insufficient_proof`. Review/Rework-Metriken sind nicht mehr grundsätzlich unmessbar: im run-007-Pilot sind beide Metriken `repo_local` dokumentiert. run-008 pilotiert zusätzlich einen expliziten Outcome-Evidence-Negativfall mit `CLAIM_NOT_PROVEN` und repo-lokalem Timing-Artefakt. run-009 adressiert Task-Diversität partiell (claim-002 PASS: außerhalb validator-test-hardening-Cluster) und verbessert Timing-Semantik auf self_reported mit explizitem capture_mode. | Aus Preimage (`experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/results/cross-run-assessment.md` §5): Blocker-Beseitigung vor Usefulness-Verdict: (1) ✓ Review/Rework-Mechanismus in run-007 pilotiert, (2) ✓ Task-Diversität partiell adressiert (run-009 claim-002 PASS; weiterer Run für Replikation offen), (3) ✓ Negativfall pilotiert (run-008; nicht voll unabhängig), (4) unabhängige Metrik-Validierung (weiterhin offen) | Usefulness-Verdict bleibt blockiert durch nur partielle Auditor-Unabhängigkeit/Selbst-Review-Bias und fehlende vollständig unabhängige Validierung; Task-Diversität einmalig belegt aber nicht repliziert; Zeitmessung ist self_reported, noch nicht unabhängig belastbar | P1 | belegt |
| RM-006 | Catalog Staleness (dormant) | `decisions/system/2026-04-23-catalog-staleness-dormant.yml`; `playbooks/plan-execution-checklist.md` Phase 4 | dormant — keine vereinbarte Staleness-Semantik, keine `review_cycle`-Felder | Roadmap-Einschätzung: Bewusst inaktiv; kein Handlungsbedarf ohne Semantik-Entscheidung | Semantik per Decision festlegen, wenn erster realer Staleness-Fall vorliegt | Keine vereinbarte Staleness-Semantik; kein realer Staleness-Fall | P3 | belegt |
| RM-007 | Plan-Execution-Checklist Phase 3/4 — Restarbeiten | `playbooks/plan-execution-checklist.md` Phase 3, Phase 4 | Phase 3: offen (Fixture-Erweiterung); Phase 4: teilweise offen (Stub-Zonen-Entscheid) | Roadmap-Einschätzung: klein und handhabbar; kein harter Blocker | Phase 4: Jede leere Zone als `dormant` oder `minimal-seed` markieren; Phase 3 überlappt mit RM-001 | none | P2 | belegt |

---

## 3. Entscheidungspunkte

Offene Governance-, Architektur- oder Prozess-Entscheidungen, die in der Roadmap sichtbar sind, aber nicht hier entschieden werden.

| ID | Entscheidung | Warum nötig? | Betroffene Quellen | Entscheidungstyp | Owner/Instanz | Status |
|----|--------------|--------------|-------------------|-----------------|---------------|--------|
| EP-001 | RRG-v0.2 Probe-Reihenfolge: Für welche Drift-Klasse wird zuerst eine v0.2-Probe implementiert? | Drei strukturell getrennte Drift-Klassen (RRG-01 Content-Drift, RRG-02 Git-State-Drift, RRG-03 Locator-Positionsdrift) benötigen getrennte Remediation-Pfade | `decisions/process/2026-05-01-rrg-v02-remediation-preimage.yml`; `evaluations/rrg03-remediation-strategy-comparison.md` | Architektur/Prozess | Mensch | offen |
| EP-002 | Usefulness-Verdict nach Outcome-Evidence-Beseitigung: Soll der Agent/Skill Minimal Layer fortgeführt, revidiert oder superseded werden? | Evaluation-Mindestschwelle (≥3 vergleichbare PRs) erreicht (run-002, run-005, run-006), aber Usefulness-Verdict bleibt `insufficient_proof`. Review/Rework-Outcome-Evidence-Mechanismus ist in run-007 pilotiert (single-run Kontext), zentrale Blocker bleiben offen. Wer entscheidet Fortführung? | `evaluations/agent-skill-file-fruitfulness.md` §Falsifikationskriterien; `blueprints/blueprint-agent-skill-minimal-layer-v0.1.md` §Falsifikationsgrenze; `experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/results/cross-run-assessment.md` §5 Blocker-Liste; `experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/artifacts/run-007-review-rework-outcome-evidence-pilot/measurement.yml` | Governance | Mensch (nach Beseitigung der dokumentierten Blocker) | offen — Review/Rework-Mechanismus in run-007 pilotiert; Entscheidung weiter blockiert durch unabhängigen Auditor, Task-Diversität und Negativfall |
| EP-003 | Soll `docs/roadmap.md` in `AGENTS.md` / `agent-policy.yaml` als Pflichtlektüre verankert werden? | Roadmap ist über `docs/index.md` auffindbar, aber nicht direkt in der Agenten-Lesereihenfolge; Gap dokumentiert in §6 | `AGENTS.md`; `agent-policy.yaml`; `repo.meta.yaml` | Governance | **Mensch** — Agents dürfen AGENTS.md und agent-policy.yaml nicht ändern | **accepted** — PR #177: docs/roadmap.md ist nun Pflichtlektüre in AGENTS.md (Position 4), agent-policy.yaml und repo.meta.yaml (truth_model.navigation) |
| EP-004 | Blueprint v2 Phase 2: Wann und wie wird Hard-Fail für neue Experimente ohne `falsifiability`-Block eingeführt? | Erfordert deterministischen Stichtags-Mechanismus (Grandfather-Liste als committetes Artefakt) | `blueprints/blueprint-v2-roadmap.md` Phase 2 | Prozess/Governance | Mensch | offen — Design fehlt |

---

## 4. Abhängigkeiten

| Von | Nach | Abhängigkeit | Risiko bei falscher Reihenfolge |
|-----|------|--------------|--------------------------------|
| EP-001 (RRG Probe-Entscheid) | RM-003 Implementierung | Preimage muss vor Schema/Validator-Patch in accepted-Status übergehen | Kein accepted Decision → Breaking Changes ohne Strategie-Grundlage |
| RM-002 PR 10/11 (Outcome-Evidence abgeleitet) | RM-005 / EP-002 (Usefulness-Verdict) | Outcome-Evidence-Blocker müssen vor Verdict-Treffen beseitigt sein; RM-005 kann nicht zu Promotion führen ohne Blocker-Resolve | Usefulness-Verdict ohne Outcome-Evidence → falsche Blueprint-Klassifikation; Premature superseded oder continued |
| EP-004 Staffelungsmechanismus-Entscheid | RM-004 Phase 2 Aktivierung | Phase 2 (Hard-Fail neue Experimente) erfordert festgelegten Mechanismus | Hard-Fail ohne Grandfather-Liste bricht historische Experimente |
| RM-001 Fixture-Erweiterung | Phase E Stop-Kriterium | Smoke-Set muss typische Drift-Fälle reproduzierbar erkennen | Unvollständiger Smoke-Set schützt nicht vor Regression bei Phase F |

---

## 5. Nicht-Ziele

Diese Roadmap trifft explizit **keine** der folgenden Entscheidungen:

- **Keine Promotion-Entscheidungen** — Kein Experiment wird durch diese Datei von `testing` auf `adopted` gesetzt.
- **Keine Adoption-Entscheidungen** — Kein Catalog-Eintrag, kein Prompt, keine Practice wird hier adoptiert.
- **Keine Änderung der Wahrheitshierarchie** — Die Roadmap ordnet sich unterhalb von kanonischen, grundlegenden und operativen Dokumenten ein.
- **Keine manuelle Änderung generierter Artefakte** — `docs/_generated/*` bleibt maschinell erzeugt und wird nicht durch diese Datei beeinflusst.
- **Keine Statusglättung bei Widersprüchen** — Wenn Quellen widersprüchlichen Status zeigen, wird der Widerspruch sichtbar gemacht, nicht geglättet.
- **Keine Änderung von AGENTS.md, agent-policy.yaml oder repo.meta.yaml** — Diese Steuerungsdokumente bleiben ausschließlich handgepflegt durch Menschen.
- **Keine neuen Blueprint-Inhalte oder Policy-Aussagen** — Die Roadmap verweist auf bestehende Dokumente; sie schreibt keine fachlichen Inhalte fort.

---

## 6. Governance-Gaps

Beobachtungen, die eine menschliche Governance-Entscheidung erfordern. Diese Gaps werden hier dokumentiert, nicht geschlossen.

| Gap | Quelle / Beobachtung | Warum relevant? | Benötigte Entscheidung | Status |
|-----|---------------------|-----------------|----------------------|--------|
| **GAP-001**: Roadmap nicht direkt in Agenten-Lesereihenfolge verankert | Vor PR #177 war `docs/roadmap.md` nur über `docs/index.md` auffindbar. Seit PR #177 ist `docs/roadmap.md` direkt in `AGENTS.md` und `agent-policy.yaml` als Pflichtlektüre eingetragen. | Agenten, die nur die Lesereihenfolge befolgen, finden die Roadmap nur indirekt | Soll `docs/roadmap.md` in `AGENTS.md` und `agent-policy.yaml` als Pflichtlektüre aufgenommen werden? | **resolved** — PR #177: docs/roadmap.md ist nun Position 4 in AGENTS.md und agent-policy.yaml read_order (nach agent-policy.yaml, vor README.md) |
| **GAP-002**: `blueprint-evidence-control-plane-v1.md` hat keine direkte Relation zu `masterplan.md` | `docs/blueprints/blueprint-evidence-control-plane-v1.md` Frontmatter; `docs/masterplan.md` | Blueprint ohne Masterplan-Relation erschwert Orientierung in der Wahrheitshierarchie | Soll ein `informs`- oder `references`-Link zu `masterplan.md` hinzugefügt werden? | Gap beobachtet; Entscheidung optional |
| **GAP-003**: Blueprint-Entscheidungspunkt nach Outcome-Evidence | `blueprints/blueprint-agent-skill-minimal-layer-v0.1.md` §Falsifikationsgrenze; `evaluations/agent-skill-file-fruitfulness.md` (Evaluation-Schwelle erreicht); `experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/results/cross-run-assessment.md` (§5 Blocker dokumentiert); `experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/artifacts/run-007-review-rework-outcome-evidence-pilot/measurement.yml`; `experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/artifacts/run-007-review-rework-outcome-evidence-pilot/review-events.yml`; `experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/artifacts/run-008-negative-case-independent-audit-timing/auditor-output.yml`; `experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/artifacts/run-008-negative-case-independent-audit-timing/evidence-pack.yml`; `experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/artifacts/run-008-negative-case-independent-audit-timing/measurement.yml`; `experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/artifacts/run-008-negative-case-independent-audit-timing/timing.txt` | Execution-Assessment-Mindestschwelle (3 Runs) ist erreicht. Usefulness-Verdict bleibt `insufficient_proof`. Blueprint deklariert: nach ≥3 PRs und Falsifikationskriterien-Bewertung entscheiden (fortführen, revidieren, superseded). Wer trifft diese Entscheidung auf Basis der dokumentierten Blocker? | Nach Beseitigung von: (1) ✓ Review/Rework-Mechanismus etabliert und pilotiert (run-007), (2) ✓ dokumentierter Negativfall pilotiert (run-008; `CLAIM_NOT_PROVEN`, Auditor-Unabhängigkeit nur partial), (3) Task-Diversitätsnachweis, (4) unabhängiger Auditor bzw. unabhängige Metrik-Validierung — dann Usefulness-Verdict treffen | offen — Mechanismus und negative case pilotiert; partielle Auditor-Unabhängigkeit, fehlende unabhängige Validierung und Task-Diversität bleiben Vorbedingung |
| **GAP-004**: `docs/roadmap.md` hat keine Relation in bestehenden kanonischen Quellen (nur über `docs/index.md` auffindbar) | Vor PR #177 war `docs/roadmap.md` nicht in `repo.meta.yaml` §truth_model §navigation eingetragen. Seit PR #177 ist `docs/roadmap.md` dort explizit gelistet. | Neue Navigation-Dateien werden in `repo.meta.yaml` nicht explizit gelistet | Soll `docs/roadmap.md` in `repo.meta.yaml` §truth_model §navigation explizit aufgenommen werden? | **resolved** — PR #177: docs/roadmap.md ist nun in repo.meta.yaml §truth_model §navigation eingetragen |

---

## 7. Aktualisierungsregeln

**Wann wird diese Roadmap aktualisiert?**

1. **Neue Blueprints, Plans, Roadmap-artige oder Evaluation-Dokumente**: Wenn ein neues Dokument in `docs/blueprints/`, `docs/evaluations/`, `docs/playbooks/` oder `decisions/` angelegt wird, muss geprüft werden, ob ein Arbeitsstrang in §2 oder ein Entscheidungspunkt in §3 ergänzt werden muss.

2. **Statusänderungen in Quellen**: Wenn eine Quelle (Blueprint, Decision, Experiment-Decision) ihren Status ändert (z.B. von `proposed` auf `accepted`, oder ein Checkbox-Status wechselt), muss der betroffene Roadmap-Eintrag aktualisiert werden.

3. **Erledigte Punkte**: Abgeschlossene Arbeitsstränge werden nicht gelöscht, sondern mit `done` und Quellennachweis in einen Abschnitt **§8 Erledigt / Superseded** verschoben (sobald dieser Abschnitt bei Bedarf angelegt wird).

**Regeln für Roadmap-Einträge:**

- Jede Zeile in §2 muss mindestens eine konkrete Quelle mit Pfad nennen.
- `Quelle-Status` wird nur aus der Quelle übernommen — keine Eigeninterpretation.
- `Roadmap-Einschätzung` ist explizit als Ableitung zu kennzeichnen.
- `Nächster Schritt` muss konkret und quellgebunden sein.
- `Blocker` darf `none` sein, aber nicht leer bleiben.
- Die Roadmap ändert nur, was sie selbst koordiniert — niemals die Quelldokumente.

**Was diese Roadmap nicht ändert:**

- `AGENTS.md`, `agent-policy.yaml`, `repo.meta.yaml` — nie durch Agents änderbar.
- `docs/_generated/*` — nur durch Generatoren, nie manuell.
- Status-Felder in Quell-Experimenten oder Decisions — nur durch Menschen oder belegte Prozesse.
