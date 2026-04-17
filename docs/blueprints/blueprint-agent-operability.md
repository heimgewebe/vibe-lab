---
title: "Blueprint — Minimaler Agent-Operability-Kern"
status: "idea"
canonicality: "exploratory"
created: "2026-04-17"
updated: "2026-04-17"
author: "unknown-agent"
---

# Minimaler Agent-Operability-Kern

## Ziel

Agents sollen konkrete Entwicklungsaufgaben strukturiert ausführen können.
Nicht mehr. Nicht weniger.

## Architektur

### Status

Diese Blaupause beschreibt einen Zielzustand.
Die beschriebenen Strukturen (z. B. `/agent/`, `wgx task run`, `tasks/`) sind konzeptionell und derzeit nicht vollständig im Repository implementiert.

Sie dienen als Referenz für zukünftige Implementierungen und dürfen nicht als bestehende Systemstruktur interpretiert werden.

Blueprint → Task → Commands → Execution → Ergebnis

Kein:
- Signal-System
- Policy Engine
- Emergenz

Nur Durchstich von Denken → Handeln

## Kernkomponenten

### Command Contracts

WICHTIG:
Diese Commands sind konzeptionelle Contracts und müssen perspektivisch in `contracts/` als maschinenvalidierbare Schemas formalisiert werden. Maßgeblich ist dabei JSON Schema als kanonisches Format, konsistent zur bestehenden Contract-Struktur und Validierung im Repo. Die YAML-Blöcke in dieser Blaupause dienen nur der lesbaren Skizze, nicht als alternative Schema-Quelle.

Zweck: Strukturierte, überprüfbare Aktion.

#### C1: command.read_context
```yaml
id: command.read_context
type: command
input:
  - paths[]
output:
  - extracted_facts
  - uncertainties
constraints:
  - must_reference_files
```
Ersetzt: „lies repo“, „analysiere code“

#### C2: command.write_change
```yaml
id: command.write_change
type: command
input:
  - target_file
  - change_type (create|update|delete)
  - content
constraints:
  - target_proof_required
  - no_generated_files
```
Verbindet mit der bestehenden Diagnose-Regel.

#### C3: command.validate_change
```yaml
id: command.validate_change
type: command
input:
  - checks[]
output:
  - success
  - errors[]
checks:
  - lint
  - test
  - docs-guard
```
Warum genau diese drei?
Weil sie exakt abdecken:
- Phase Verstehen: `read_context`
- Phase Handeln: `write_change`
- Phase Prüfen: `validate_change`

Weitere Commands sind in dieser Phase iterativer Overhead.

### Task-System

Zweck: Strukturierte Arbeitssequenz.

#### Minimal-Template
```yaml
task:
  id: fix_map_submission
  goal: "Formularübermittlung implementieren"
  constraints:
    - no breaking changes
    - contract compliance
  steps:
    - command: command.read_context
    - command: command.write_change
    - command: command.validate_change
```
WICHTIG: Task ≠ Beschreibung. Task = ausführbare Struktur.

### Geplanter Validierungslayer für Agent-Tasks

**Wichtig:** Dies beschreibt das **Zielbild und die Sollstruktur**. Die folgenden Assertions sind **noch nicht kanonisch** und **noch keine bindende Repo-Policy**. Eine spätere Extraktion und Kanonisierung (z. B. in `docs/policies/`) ist erst nach einer Pilot-Erprobung an realen Tasks denkbar.

Um Tasks sauber zu begrenzen, sind folgende Assertions als geplante Invarianten vorgesehen:

- **A0.1 – Discovery-Prädikat**
  Ein Task ist erst gültig definierbar, wenn explizit festgelegt ist:
  - `scope`
  - `counts_as_usage`
  - `does_not_count`

- **A0 – Kontext-Vollständigkeit**
  `read_context` ist nur dann ausreichend, wenn alle Entscheidungen daraus allein begründbar sind.

- **A1 – Kausalkette**
  Eine Scope-Erweiterung ist nur zulässig, wenn eine rekonstruierbare Kausalkette vom Ziel zur neu betroffenen Datei vorliegt.

- **A2 – Unabhängigkeitstest**
  Wenn eine entdeckte Änderung auch ohne das Kernziel als eigener sinnvoller Task bestehen könnte, muss abgebrochen und neu geschnitten werden.

- **A3 – Lokalität**
  Alle Entscheidungen müssen innerhalb eines gemeinsamen Entscheidungskontexts haltbar sein; wenn externer Zusatzkontext nötig wird, ist der Task neu zu schneiden.

#### Geplante Entscheidungslogik

1. Discovery-Prädikat vorhanden? → nein: Task nicht gültig definierbar
2. `read_context` vollständig? → nein: Kontext erweitern
3. neue Artefakte entdeckt? → nein: `write_change` | ja: A1 prüfen
4. A1 gültig? → nein: A2 prüfen
5. A2 verletzt? → ja: abbrechen / Scope neu schneiden
6. A3 verletzt? → ja: abbrechen / Task neu schneiden
7. sonst → `write_change`, danach `validate_change`

### Agent-Loop
1. read_context
2. decide (implizit im Agent)
3. write_change
4. validate_change

Kein Planner-Agent in dieser Iteration erforderlich.

### Execution
CLI (bewusst simpel): `wgx task run fix_map_submission`
*(Hinweis: `wgx` dient hier als möglicher CLI-Einstiegspunkt; daraus folgt keine allgemeine Repo-Abhängigkeit des Weltgewebe-Kerns von externen Systemstrukturen. Weltgewebe bleibt eigenständig.)*

## Integration in bestehende Repo-Mechaniken

Die initialen Vorgaben beschrieben Konzepte (Experiments, Evidence-Log, Decision Artifacts, Schema-Versionierung), die im `vibe-lab` Repo bereits operativ verankert sind. Der Agent-Operability-Kern *implementiert diese nicht neu*, sondern nutzt die existierende Architektur strikt gemäß Policy.

1. **Experiment-Struktur (Kernmodul):** Bereits in `experiments/` vorhanden, gesteuert via `manifest.yml`, `method.md`, und Output in `evidence.jsonl`.
2. **Evidence-Log (`evidence.jsonl`):** Bereits strikt definiert.
   Beispiel-Nutzung für den Agent-Layer (WICHTIG: `context` und `metric` müssen Strings sein, und `event_type` stammt aus dem erlaubten Vokabular wie `run`, `observation`, `error`, etc.):
   ```json
   {
     "event_type": "error",
     "context": "submission_failed in map_form",
     "metric": "count: 7",
     "timestamp": "2026-04-09T12:00:00Z"
   }
   ```
3. **Decision Artifacts:** Bereits bindend in `decisions/` für architekturrelevante Entscheidungen.
4. **Golden Example:** Ist eine bestehende Anforderung für Promotion von `experiments/` zu `catalog/`.
5. **Schema-Versionierung:** Wird via `contracts/` und `schemas/` für alle Kern-Artefakte validiert.
6. **Contribution Contract:** Über Typisierung von Issue-Forms (z.B. `experiment-proposal`, `promotion-request`) bereits geregelt.

## Roadmap

### Ausführungsprinzip
- Jede Phase beginnt mit Diagnose (Ist-Zustand erfassen)
- Keine Implementierung ohne Target-Proof
- Jede Aktion muss auf konkrete Dateien/Outputs referenzieren
- Die Roadmap ist kein To-do, sondern ein kontrollierter Ausführungsprozess

### Phase 1: Minimaler Kern (Command & Task Definitionen)
- **Ziel:** Erstellung der ersten drei Commands und einer validen Task.
- **Stop-Kriterium:** Konkret festgelegte und belegte Zielpfade für Commands und Task.

### Phase 2: Execution Engine
- **Ziel:** Minimaler Ausführungs-Runner für Agenten-Tasks.
- **Stop-Kriterium:** Sprache entschieden, Zielpfad entschieden, Minimalumfang (Runner kann genau 1 Task ausführen) entschieden.

### Phase 3: Integration & Erprobung
- **Ziel:** Vollständiger Durchlauf einer Task.
- **Stop-Kriterium:** Eindeutiger, nachweisbarer Erfolgsnachweis des gesamten Loops (read -> write -> validate).

## Aktivierung

Diese Blaupause wird angewendet, wenn:
- Agent Entwicklungsaufgaben ausführt
- Blueprint → Implementation überführt wird
- PR-Erstellung automatisiert wird

Nicht anzuwenden für:
- reine Analyse
- Dokumentationsaufgaben ohne Codeänderung

## Maschinenlesbarer Kern

```yaml
agent_operability:
  commands:
    - id: command.read_context
    - id: command.write_change
    - id: command.validate_change
  task_template:
    required_steps:
      - command.read_context
      - command.write_change
      - command.validate_change
  execution:
    type: cli
    entrypoint: scripts/run-task
```
