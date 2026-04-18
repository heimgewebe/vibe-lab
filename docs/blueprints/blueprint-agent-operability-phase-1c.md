---
title: "Blueprint — Phase 1c: Systemverankerung des Agent-Operability-Kerns"
status: active
canonicality: exploratory
created: "2026-04-18"
updated: "2026-04-18"
author: "GitHub Copilot"
relations:
  - type: derived_from
    target: "./blueprint-agent-operability.md"
  - type: derived_from
    target: "../../experiments/2026-04-15_agent-task-validity/CONTEXT.md"
  - type: references
    target: "../concepts/execution-bound-epistemics.md"
  - type: references
    target: "../../agent-policy.yaml"
---

## Phase 1c: Systemverankerung des Agent-Operability-Kerns

## Ziel

Den bereits präzisen lokalen Agentenraum in repo-erzwungene Wahrheit überführen:

- `HANDOFF_BLOCK` wird maschinenvalidierbar
- Critic/Operator-Übergabe wird außerhalb des Agenten prüfbar
- konzeptionelle Commands werden zu echten Repo-Artefakten
- CI erzwingt die Mindestintegrität
- späterer Replay-Pfad wird vorbereitet

## Ausgangslage

Das Repo ist bereits darauf ausgelegt, Wahrheit über kanonische Steuerquellen,
Schemas und generierte Diagnoseartefakte zu ordnen; `docs/_generated/*` ist
Diagnose, nicht Wahrheit. Zugleich existieren schon harte Validatoren und CI für
Manifest-, Relations-, Execution-Proof- und Interpretation-Budget-Logik.

Wichtig ist dabei: Das Experiment `2026-04-15_agent-task-validity` hat belegt,
dass ein Task erst testbar wird, wenn `target_files`, ein Locator und
`change_type` explizit vorhanden sind; die Validitätsrate sprang dadurch von
geschätzt `0/6` auf `6/6`.

Parallel ist `interpretation_risk` im aktuellen `epistemic-state` bewusst nur
`unassessed`, bis Phase 2 umgesetzt ist. Das Repo kennt also bereits das
Muster: lieber ehrliche Leerstelle als Pseudopräzision. Genau dieselbe Disziplin
sollte jetzt für Agent-Operability gelten.

## Leitentscheidung

Nicht weiter fragen:

> „Wie mache ich die Agenten noch klüger?“

Sondern:

> „Wie verschiebe ich Wahrheit vom Agenten in das Repo?“

Das ist die alternative Sinnachse. Sie kippt den Fokus von Modellverhalten auf
Systemverhalten.

## Architekturziel

### Zielbild

```text
User / Agent Task
   ↓
experiment-critic
   ↓
HANDOFF_BLOCK (contract-valid)
   ↓
validator / CI
   ↓
experiment-operator
   ↓
traceable execution
   ↓
optional replay runner
```

### Invariante

Ein Agent darf künftig nicht mehr die einzige Instanz sein, die die Gültigkeit
seines eigenen Übergabeobjekts behauptet.

## Arbeitscheckliste

- [ ] Phase A abgeschlossen: `HANDOFF_BLOCK` als Repo-Contract vorhanden
- [ ] Phase B abgeschlossen: Hash/Kanonisierung maschinell validierbar
- [ ] Phase C abgeschlossen: CI erzwingt den Handoff-Validator
- [ ] Phase D abgeschlossen: Command-Schemas v0.1 liegen vor
- [ ] Phase E abgeschlossen: Golden Fixtures / Smoke-Set deckt Drift-Fälle ab
- [ ] Phase F abgeschlossen: optionaler Replay-Runner reproduziert einen Task

## Phase A — HANDOFF_BLOCK als echtes Repo-Contract-Artefakt

### Phase A Zweck

Den Handoff aus dem Promptstatus in den Systemstatus überführen.

### Phase A Umsetzung

- [ ] Neues Schema anlegen: `schemas/agent.handoff.schema.json` oder
      `contracts/agent_handoff.schema.json`
- [ ] Pflichtfelder modellieren:
      `status`, `target_files`, `locator`, `change_type`, `scope`,
      `normalized_task`, `critic_signature`
- [ ] Bedingte Felder modellieren:
      bei `status != PASS` → `blocked_by`, `required_fixes`
- [ ] Bedingte PASS-Felder modellieren:
      `handoff.algo`, `handoff.canon`, `handoff.hash`
- [ ] Optionale Präzisionsfelder modellieren:
      `exact_before`, `exact_after`, `constraints`, `risks`, `validation_plan`

### Phase A Nutzen

- Repo-native Validierbarkeit
- klarer SSOT für Handoff-Struktur
- weniger Prompt-Drift

### Phase A Risiken

- etwas mehr Formalismus
- sauberer Versionswechsel später nötig

### Phase A Stop-Kriterium

- [ ] Handoff-Schema existiert und validiert einen minimalen PASS-Fall

## Phase B — Kanonisierung und Hash maschinell erzwingen

### Phase B Zweck

Nicht nur definieren, sondern prüfen.

### Phase B Umsetzung

- [ ] Neues Skript anlegen: `scripts/docmeta/validate_agent_handoff.py`
- [ ] Schema-Validität prüfen
- [ ] `critic_signature == experiment-critic/v1` prüfen
- [ ] Für `status == PASS` Hash nach `canon: v1` recomputen
- [ ] Fehlerklassen sauber ausgeben:
      `contract_invalid`, `hash_mismatch`, `unsupported_signature`,
      `unsupported_canon`
- [ ] Kanonisierung klein und testgetrieben halten

### Phase B Nutzen

- Handoff wird außerhalb des Agenten prüfbar
- weniger „funktioniert nur in der Session“
- passt zum bestehenden Guard-First-Muster des Repos

### Phase B Risiken

- False Positives bei unsauber definierter Kanonisierung
- Agent-Engine-Verhalten bleibt davon unberührt

### Phase B Stop-Kriterium

- [ ] Validator meldet PASS/FAIL für mindestens einen gültigen und einen ungültigen Handoff korrekt

## Phase C — CI-Integration

### Phase C Zweck

Wahrheit nicht nur beschreiben, sondern erzwingen.

### Phase C Umsetzung

- [ ] `.github/workflows/validate.yml` um `validate_agent_handoff.py` erweitern
- [ ] Optional Fixture-/Golden-Pfad definieren, falls Beispielartefakte genutzt werden
- [ ] CI nur Struktur/Canon/Hash prüfen lassen, nicht Agent-Ausführung simulieren

### Phase C Nutzen

- gleiche Wahrheit für Agent und CI
- weniger lokale Sonderwirklichkeiten

### Phase C Risiken

- kurzfristig mehr Friktion im PR-Flow

### Phase C Stop-Kriterium

- [ ] CI schlägt bei ungültigem Handoff reproduzierbar fehl

## Phase D — Konzeptionelle Commands in echte Schemas überführen

### Phase D Zweck

`command.read_context`, `command.write_change`, `command.validate_change` aus
dem rein semantischen Status holen.

### Phase D Umsetzung

- [ ] `schemas/command.read_context.schema.json` anlegen
- [ ] `schemas/command.write_change.schema.json` anlegen
- [ ] `schemas/command.validate_change.schema.json` anlegen
- [ ] v0.1 bewusst klein halten und nur praktisch belegte Felder modellieren

### Minimalumfang

#### `command.read_context`

- [ ] `target_files[]`
- [ ] optional `extracted_facts`
- [ ] optional `uncertainties`

#### `command.write_change`

- [ ] `target_files[]`
- [ ] `target_lines` oder `locator`
- [ ] `change_type`
- [ ] optional `exact_before`
- [ ] optional `exact_after`
- [ ] `forbidden_changes[]`

#### `command.validate_change`

- [ ] `checks[]`
- [ ] `success`
- [ ] `errors[]`

### Phase D Stop-Kriterium

- [ ] Drei Command-Schemas vorhanden und je ein minimales Golden-Beispiel dokumentiert

## Phase E — Golden Fixtures / Smoke-Set

### Phase E Zweck

Nicht nur Theorie prüfen, sondern Vollzugssituationen.

### Phase E Umsetzung

- [ ] Fixture-Sammlung mit 6–8 Fällen anlegen
- [ ] Folgende Fälle mindestens abdecken:
      PASS, FAIL ohne `target_files`, PARTIAL ohne Locator, `hash_mismatch`,
      `unsupported_canon`, Integrity-Mismatch bei `normalized_task`,
      optional `exact_before`/`exact_after`, promotion-naher Fall

### Phase E Nutzen

- Regression-Schutz
- Debugbarkeit
- erleichtert spätere CI-Härtung

### Phase E Stop-Kriterium

- [ ] Smoke-Set erkennt typische Drift-Fälle reproduzierbar

## Phase F — Optional: Replay-Runner

### Phase F Zweck

Vom Agenten-Dialog zur reproduzierbaren Ausführung.

### Phase F Umsetzung

- [ ] Minimalen Runner entwerfen, der genau einen validierten Handoff abspielt
- [ ] Contract + Hash vor Ausführung prüfen
- [ ] `read_context` / `write_change` / `validate_change` als Minimalpfad ausführen
- [ ] kleines Ergebnisartefakt erzeugen

### Phase F Risiken

- zu frühe halbe Execution Engine
- hoher Interpolationsanteil bei unklarem Toolingpfad

### Phase F Stop-Kriterium

- [ ] Ein einzelner validierter Task kann reproduzierbar abgespielt werden

## Deliverables

- [ ] D1: `schemas/agent.handoff.schema.json`
- [ ] D2: `scripts/docmeta/validate_agent_handoff.py`
- [ ] D3: CI-Erweiterung in `.github/workflows/validate.yml`
- [ ] D4: `schemas/command.read_context.schema.json`
- [ ] D5: `schemas/command.write_change.schema.json`
- [ ] D6: `schemas/command.validate_change.schema.json`
- [ ] D7: Fixture-/Smoke-Set (`tests/fixtures/agent_handoff/` oder äquivalent)
- [ ] D8: Optionaler Replay-Runner unter `tools/vibe-cli/` oder äquivalent

## Was ausdrücklich nicht zuerst getan wird

- [ ] Kein dritter Agent als Priorität 1
- [ ] Keine neue Prompt-Feinmechanik als Priorität 1
- [ ] Keine große Agenten-Policy-Sprache als Priorität 1
- [ ] Keine frühe Planner-/Orchestrator-Schicht als Priorität 1

## Risiko- und Nutzenbilanz

### Nutzenklassen

- technisch: mehr Determinismus, weniger Drift
- epistemisch: Wahrheit wandert vom Modell ins Repo
- organisatorisch: PRs werden klarer reviewbar
- architektonisch: Blaupause wird operationalisiert statt nur referenziert

### Risikoklassen

- technisch: falsche Kanonisierung erzeugt Fehlalarme
- organisatorisch: mehr Friktion im Beitragspfad
- semantisch: zu frühe Contract-Verhärtung kann Praxisfälle ausschließen
- strategisch: Replay zu früh begonnen → Overengineering

## Essenz

Der nächste Fortschritt liegt nicht im Agenten, sondern in der Repo-Durchsetzung
seiner Wahrheit. Die empfohlene Reihenfolge lautet:

1. Contract
2. Validator
3. CI
4. Command-Schemas
5. Smoke-Set
6. Optional Replay