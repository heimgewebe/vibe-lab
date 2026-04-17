---
title: "Blueprint — Minimaler Agent-Operability-Kern"
status: "idea"
canonicality: "exploratory"
created: "2026-04-17"
updated: "2026-04-17"
author: "unknown-agent"
relations:
  - type: derived_from
    target: "../../experiments/2026-04-15_agent-task-validity/CONTEXT.md"
---

# Minimaler Agent-Operability-Kern

## Ziel

Agents sollen konkrete Entwicklungsaufgaben strukturiert ausführen können.
Nicht mehr. Nicht weniger.

## Architektur

### Status

Diese Blaupause beschreibt einen Zielzustand.
Die beschriebenen Strukturen zur Task-Ausführung sind konzeptionell und derzeit nicht vollständig operativ im Repository implementiert, stützen sich aber auf die bereits etablierten Task-Datenstrukturen (z.B. in `tasks.jsonl`).

Blueprint → Task → Commands → Execution → Ergebnis

Kein:
- Signal-System
- Policy Engine
- Emergenz

Nur Durchstich von Denken → Handeln

## Kernkomponenten

### Command Contracts

WICHTIG:
Diese Commands sind konzeptionelle Contracts und müssen perspektivisch in `contracts/` als maschinenvalidierbare Schemas formalisiert werden. Maßgeblich ist dabei JSON Schema als kanonisches Format, konsistent zur bestehenden Contract-Struktur und Validierung im Repo.

Zweck: Strukturierte, überprüfbare Aktion basierend auf der etablierten `task.jsonl` Praxis.

#### C1: command.read_context
```yaml
id: command.read_context
type: command
input:
  - target_files[]
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
  - target_files[]
  - target_lines
  - change_type (edit|create|delete)
  - exact_before
  - exact_after
  - forbidden_changes[]
constraints:
  - target_proof_required
  - no_generated_files
```
Verbindet sich direkt mit der bestehenden Diagnose-Regel und den Eigenschaften aus `experiments/2026-04-15_agent-task-validity/tasks.jsonl`.

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

Zweck: Strukturierte Arbeitssequenz. Nutzt die im Repo existierende Praxis aus `tasks.jsonl` als Fundament.

#### Minimal-Template
```json
{
  "task_id": "T1",
  "description": "Formularübermittlung implementieren",
  "target_files": ["docs/index.md"],
  "target_lines": "n## Laufende Versuche",
  "change_type": "edit",
  "exact_before": "n## Laufende Versuche",
  "exact_after": "## Laufende Versuche",
  "forbidden_changes": ["content restructuring", "new sections"]
}
```
WICHTIG: Task ≠ allgemeine Beschreibung. Task = eng geschnittener, maschinenlesbarer Ausführungsvertrag.

### Geplanter Validierungslayer für Agent-Tasks

Um Tasks sauber zu begrenzen, sind folgende Assertions als geplante Invarianten vorgesehen:

- **A0.1 – Discovery-Prädikat**
  Ein Task ist erst gültig definierbar, wenn explizit `target_files` und `forbidden_changes` festgelegt sind.

- **A0 – Kontext-Vollständigkeit**
  `read_context` ist nur dann ausreichend, wenn alle Entscheidungen daraus allein begründbar sind.

- **A1 – Kausalkette**
  Eine Scope-Erweiterung über die initialen `target_files` hinaus ist nur zulässig, wenn eine rekonstruierbare Kausalkette vorliegt.

- **A2 – Unabhängigkeitstest**
  Wenn eine entdeckte Änderung auch ohne das Kernziel als eigener sinnvoller Task bestehen könnte, muss abgebrochen und neu geschnitten werden.

- **A3 – Lokalität**
  Alle Entscheidungen müssen innerhalb eines gemeinsamen Entscheidungskontexts haltbar sein.

#### Geplante Entscheidungslogik

1. `target_files` und `forbidden_changes` vorhanden? → nein: Task nicht gültig definierbar
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
CLI (bewusst simpel, angebunden an etablierte Entrypoints): `tools/vibe-cli/ task run T1` oder `make run-task T1`

## Integration in bestehende Repo-Mechaniken

Der Agent-Operability-Kern implementiert keine neuen epistemischen Grundstrukturen, sondern nutzt die existierende Architektur strikt gemäß Policy.

1. **Experiment-Struktur:** Bereits in `experiments/` vorhanden, gesteuert via `manifest.yml`, `method.md`, und Output in `evidence.jsonl`.
2. **Evidence-Log (`evidence.jsonl`):** Bereits strikt definiert.
   Beispiel-Nutzung für den Agent-Layer (WICHTIG: `context` und `metric` müssen Strings sein, und `event_type` stammt aus dem erlaubten Vokabular wie `run`, `observation`, `error`):
   ```json
   {
     "event_type": "error",
     "context": "submission_failed in target target_files",
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
- **Ziel:** Erstellung der ersten drei Commands und Validierung gegen bestehende `tasks.jsonl`.
- **Stop-Kriterium:** Konkret festgelegte und belegte Zielpfade für Commands.

### Phase 2: Execution Engine
- **Ziel:** Minimaler Ausführungs-Runner für Agenten-Tasks über `tools/vibe-cli/`.
- **Stop-Kriterium:** Sprache entschieden, Minimalumfang (Runner kann genau 1 Task ausführen) entschieden.

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
