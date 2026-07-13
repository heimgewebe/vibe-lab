---
title: "Roadmap — Koordination offener Arbeitsstränge"
status: active
triggered_by: "user-request-vibe-lab-operator-loop-2026-07-01"
canonicality: navigation
role: roadmap_index
created: "2026-05-10"
updated: "2026-07-13"
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
    target: blueprints/blueprint-model-lab-control-plane-v1.md
  - type: references
    target: evaluations/agent-skill-file-fruitfulness.md
  - type: references
    target: evaluations/replay-gap-cross-diagnosis-rrg01-rrg02.md
  - type: references
    target: evaluations/rrg03-remediation-strategy-comparison.md
  - type: references
    target: playbooks/evidence-control-plane-roadmap-checklist.md
  - type: references
    target: playbooks/outcome-evidence-replication-series-gate.md
  - type: references
    target: playbooks/plan-execution-checklist.md
  - type: references
    target: playbooks/operator-lab-loop.md
  - type: references
    target: policies/interpretation-budget.md
  - type: references
    target: policies/model-lab-control-minimum.md
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

# Roadmap — begrenzte aktive Navigation

## Zweck und Grenze

Diese Datei ist eine Wegkarte, kein Aufgabenregister und keine Wahrheitsquelle für aktive Experimente.

- Aktive Experimentwahrheit: `experiments/active.v1.json`.
- Aufgaben, Prioritäten und Promotionsentscheidungen: Bureau.
- Code-, Review-, Merge- und Prüfzustand: GitHub und CI.
- Ausgeführte Operatorarbeit: Grabowski-Receipts.
- Zielbild und Architekturgrenze: `docs/foundations/vision.md` und `docs/foundations/repo-plan.md`.

Bei jedem Widerspruch gilt die höher eingestufte Quelle. Historische Blueprints oder Experimentordner werden nicht durch eine Referenz in dieser Datei reaktiviert.

## Aktueller Zustand

Stand 13. Juli 2026:

- Vibe-Lab ist auf einen kleinen Experiment- und Evidenzraum verengt.
- Die Custom-Agent-Schicht und instruktionsführende Cursor-/Copilot-Projektionsinhalte sind stillgelegt; generierte Kompatibilitätsmarker und ihre blocking Paritätsverträge bleiben aktiv.
- Die 36 Operator-Lab-Karten sind mit `insufficient_evidence` eingefroren.
- Der Operator-Interventions-Effektvergleich ist als praktisch nicht ausführbar archiviert.
- Ein RepoBrief-Workbench-Pilot ist aktiv; der verbindliche Bestand steht ausschließlich in `experiments/active.v1.json`.
- Die Validatorfläche besteht aus 45 Core-, 10 Active- und 48 Legacy-Zielen sowie zwei ergänzenden Checks.
- Das Bureau führt den Survivor-Audit unter `heimgewebe/bureau#442`.

## Aktiver Repository-Ball

### RL-001 — Wahrheitsausrichtung und Survivor-Vertrag

**Ziel:** Alle agentenseitig änderbaren maßgeblichen Vibe-Lab-Dokumente beschreiben dieselbe begrenzte Rolle und dieselben aktuellen Bestandszahlen.

**Umfang:**

- Verträglichkeit des kanonischen Repo-Zwecks prüfen; `repo.meta.yaml` bleibt menschlich gepflegt;
- Grundlagenvision und Repository-Plan;
- README;
- Optimierungsplan und Validatorbericht;
- diese Roadmap;
- PR-Template und Dokumentfrische-Register.

**Nicht enthalten:**

- neue Runtime- oder Toolfunktion;
- neue Agentenrolle;
- neue instruktionsführende Exportprojektion;
- Entfernung bestehender Kompatibilitätsmarker oder ihrer operativen Verträge;
- Änderung an Experimentdaten, Schemas oder Validatorlogik;
- automatischer Bureau-, Routing-, Merge- oder Deploy-Eingriff.

**Erfolg:** vollständige CI, diffgebundener Review und Merge eines reinen Wahrheits- und Navigationsschnitts; kanonische menschengepflegte Quellen bleiben unverändert.

## Nächste Arbeitsstränge

Die Reihenfolge ist verbindlich, soweit Bureau keine neue Prioritätsentscheidung trifft.

### RL-002 — Legacy-Validator-Survivor-Audit

Jedes der 48 Legacy-Ziele erhält eine Disposition:

- `retain_with_consumer`;
- `covered_by_core`;
- `retire`.

Prüfreihenfolge:

1. Agent-Handoff-, Agent-Command- und Command-Chain-Verträge;
2. geschlossene Model-Lab-Spezialprüfungen;
3. historische Replay-, Fixture- und Cross-Contract-Semantik;
4. rLens- und PR-Context-Prüfungen nach Abschluss des aktiven RepoBrief-Piloten.

Zielrichtung bis 1. September 2026: 30–50 Prozent weniger blocking Legacy-Ziele, sofern Archiv- oder Äquivalenzevidenz dies trägt. Der Review eines Entfernungs-PR prüft diesen materiellen Beleg, ersetzt ihn aber nicht.

### RL-003 — RepoBrief-Pilot schließen

Reviewdatum: 15. August 2026. Ablauf: 1. September 2026.

Ohne prospektive Vergleichsevidenz keine Default-Promotion. Abschluss nur als `promote`, `pilot`, `defer`, `reject` oder `archive`; keine automatische Verlängerung.

### RL-004 — Bibliotheksverbrauch prüfen

Katalog, Prompts, Benchmarks und Instruction Blocks auf reale externe Verbraucher, Entscheidungsziele und Reviewregeln prüfen. Nicht konsumierte Flächen archivieren oder als historisch behandeln. Bestehende Kompatibilitätsmarker bleiben erhalten, bis ihre operativen Verträge separat geändert werden.

## Historische Quellen

Die im Frontmatter referenzierten Blueprints, Evaluationen, Playbooks und Entscheidungen bleiben für Provenienz und Survivor-Prüfung erreichbar. Sie sind keine aktiven Arbeitsaufträge, solange sie nicht in `experiments/active.v1.json` oder Bureau ausdrücklich reaktiviert werden.

Insbesondere sind folgende frühere Expansionsrichtungen nicht aktiv:

- Agent-Operability als eigene Agentenschicht;
- Evidence-Control-Plane als Steuerungsebene;
- Model-Lab-Control-Plane als aktive Runtime;
- reaktive State→Signal→Policy→Action-Schleifen;
- automatische Ticketgenerierung;
- neue breite instruktionsführende Tool-Export-Abdeckung;
- Dashboard-, Plexer- oder Heimlern-Integration.

## Neue-Arbeit-Gate

Vor neuer Vibe-Lab-Funktionalität müssen alle Fragen mit Ja beantwortet sein:

1. Gibt es einen aktuellen externen Verbraucher?
2. Verändert das Ergebnis eine konkrete Entscheidung?
3. Ist die Fehlerklasse nicht bereits generisch abgedeckt?
4. Besitzt die Arbeit Reviewdatum oder Ablauf?
5. Entfernt sie mindestens so viel dauerhafte Oberfläche, wie sie hinzufügt?
6. Bleiben Bureau, GitHub, CI, Grabowski und RepoBrief die zuständigen Wahrheitsorgane?

Bei einem Nein wird die Idee roh dokumentiert, zurückgestellt oder archiviert.
