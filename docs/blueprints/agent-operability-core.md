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
  - type: references
    target: "../concepts/execution-bound-epistemics.md"
  - type: references
    target: "../../experiments/2026-04-15_agent-task-validity/method.md"
---

## Minimaler Agent-Operability-Kern

## Ziel

Agents sollen konkrete Entwicklungsaufgaben strukturiert ausfuehren koennen.
Nicht mehr. Nicht weniger.

## Architektur

### Status

Diese Blaupause beschreibt einen Zielzustand.
Die beschriebenen Strukturen zur Task-Ausfuehrung sind konzeptionell und derzeit nicht vollstaendig operativ im Repository implementiert, stuetzen sich aber auf die bereits etablierten Task-Datenstrukturen (z.B. in `tasks.jsonl`).

Blueprint -> Task -> Commands -> Execution -> Ergebnis

Kein:

- Signal-System
- Policy Engine
- Emergenz

Nur Durchstich von Denken -> Handeln

## Kernkomponenten

### Command Contracts

WICHTIG:
Diese Commands sind konzeptionelle Contracts und muessen perspektivisch in `contracts/` als maschinenvalidierbare Schemas formalisiert werden. Massgeblich ist dabei JSON Schema als kanonisches Format, konsistent zur bestehenden Contract-Struktur und Validierung im Repo.

Die heute im Repo belegte Vorstufe ist stark task-zentriert (z.B. `tasks.jsonl` mit engen Aenderungsvertraegen). Das hier vorgeschlagene Command-Modell ist ein moeglicher zukuenftiger Abstraktionsrahmen ueber diese Praxis, nicht bereits die native kanonische Struktur des Repos.

Zweck: Strukturierte, ueberpruefbare Aktion basierend auf der etablierten `task.jsonl` Praxis.

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

Ersetzt: "lies repo", "analysiere code"

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
- Phase Pruefen: `validate_change`

Weitere Commands sind in dieser Phase iterativer Overhead.

### Task-System

Zweck: Strukturierte Arbeitssequenz. Nutzt die im Repo existierende Praxis aus `tasks.jsonl` als Fundament.

#### Minimal-Template

```json
{
  "task_id": "T1",
  "description": "Ueberschrift in docs/index.md korrigieren",
  "target_files": ["docs/index.md"],
  "target_lines": "\n## Laufende Versuche",
  "change_type": "edit",
  "exact_before": "\n## Laufende Versuche",
  "exact_after": "## Laufende Versuche",
  "forbidden_changes": ["new sections", "content restructuring"]
}
```

Hinweis: Das fuehrende `\n` in `target_lines`/`exact_before` ist hier absichtlich gesetzt, um einen newline-sensitiven Matcher zu demonstrieren (Ueberschrift als Block-Anker statt Substring-Treffer).
WICHTIG: Task != allgemeine Beschreibung. Task = eng geschnittener, maschinenlesbarer Ausfuehrungsvertrag.

### Geplanter Validierungslayer fuer Agent-Tasks

Um Tasks sauber zu begrenzen, sind folgende Assertions als geplante Invarianten vorgesehen:

- **A0.1 - Discovery-Praedikat**
  Ein Task ist erst gueltig definierbar, wenn explizit `target_files` und `forbidden_changes` festgelegt sind.

- **A0 - Kontext-Vollstaendigkeit**
  `read_context` ist nur dann ausreichend, wenn alle Entscheidungen daraus allein begruendbar sind.

- **A1 - Kausalkette**
  Eine Scope-Erweiterung ueber die initialen `target_files` hinaus ist nur zulaessig, wenn eine rekonstruierbare Kausalkette vorliegt.

- **A2 - Unabhaengigkeitstest**
  Wenn eine entdeckte Aenderung auch ohne das Kernziel als eigener sinnvoller Task bestehen koennte, muss abgebrochen und neu geschnitten werden.

- **A3 - Lokalitaet**
  Alle Entscheidungen muessen innerhalb eines gemeinsamen Entscheidungskontexts haltbar sein.

#### Geplante Entscheidungslogik

1. `target_files` und `forbidden_changes` vorhanden? -> nein: Task nicht gueltig definierbar
2. `read_context` vollstaendig? -> nein: Kontext erweitern
3. neue Artefakte entdeckt? -> nein: `write_change` | ja: A1 pruefen
4. A1 gueltig? -> nein: A2 pruefen
5. A2 verletzt? -> ja: abbrechen / Scope neu schneiden
6. A3 verletzt? -> ja: abbrechen / Task neu schneiden
7. sonst -> `write_change`, danach `validate_change`

### Agent-Loop

1. read_context
2. decide (implizit im Agent)
3. write_change
4. validate_change

Kein Planner-Agent in dieser Iteration erforderlich.

### Execution

Ein spaeterer CLI- oder Make-Einstiegspunkt ist denkbar; konkrete Entrypoints (wie `tools/vibe-cli/` oder `scripts/`) sind aktuell noch nicht entschieden, abhaengig von der Pilotierung.

## Integration in bestehende Repo-Mechaniken

Der Agent-Operability-Kern implementiert keine neuen epistemischen Grundstrukturen, sondern nutzt die existierende Architektur strikt gemaess Policy.

1. **Experiment-Struktur:** Bereits in `experiments/` vorhanden, gesteuert via `manifest.yml`, `method.md`, und Output in `evidence.jsonl`.
2. **Evidence-Log (`evidence.jsonl`):** Bereits strikt definiert.
   Beispiel-Nutzung fuer den Agent-Layer (`event_type` muss aus dem erlaubten Vokabular stammen, z.B. `observation`, `measurement`, `decision`, `run`; Pflichtfelder wie `iteration` und `value` muessen gesetzt sein; `context` kann je nach Eintrag auch strukturiert als Objekt vorliegen):

   ```json
   {
      "event_type": "observation",
      "context": {
        "target": "target_files",
        "status": "submission_failed"
      },
      "metric": "failed_submissions",
      "iteration": 1,
      "value": 7,
      "timestamp": "2026-04-09T12:00:00Z"
   }
   ```

   Aktueller Validator-Stand (`scripts/docmeta/validate_schema.py`): Pflichtfelder + `event_type`-Allowlist werden erzwungen; `context` wird nicht auf einen konkreten Datentyp eingeschraenkt.
3. **Decision Artifacts:** Bereits bindend in `decisions/` fuer architekturrelevante Entscheidungen.
4. **Golden Example:** Ist eine bestehende Anforderung fuer Promotion von `experiments/` zu `catalog/`.
5. **Schema-Versionierung:** Wird via `contracts/` und `schemas/` fuer alle Kern-Artefakte validiert.
6. **Contribution Contract:** Ueber Typisierung von Issue-Forms (z.B. `experiment-proposal`, `promotion-request`) bereits geregelt.

## Roadmap

### Ausfuehrungsprinzip

- Jede Phase beginnt mit Diagnose (Ist-Zustand erfassen)
- Keine Implementierung ohne Target-Proof
- Jede Aktion muss auf konkrete Dateien/Outputs referenzieren
- Die Roadmap ist kein To-do, sondern ein kontrollierter Ausfuehrungsprozess

### Phase 1: Minimaler Kern (Command & Task Definitionen)

- **Ziel:** Erstellung der ersten drei Commands und Validierung gegen bestehende `tasks.jsonl`.
- **Stop-Kriterium:** Konkret festgelegte und belegte Zielpfade fuer Commands.

### Phase 2: Execution Engine

- **Ziel:** Minimaler Ausfuehrungs-Runner; konkreter Einstiegspfad erst nach Pilotklaerung entscheiden.
- **Stop-Kriterium:** Sprache entschieden, Minimalumfang (Runner kann genau 1 Task ausfuehren) entschieden.

### Phase 3: Integration & Erprobung

- **Ziel:** Vollstaendiger Durchlauf einer Task.
- **Stop-Kriterium:** Eindeutiger, nachweisbarer Erfolgsnachweis des gesamten Loops (read -> write -> validate).

## Aktivierung

Diese Blaupause wird angewendet, wenn:

- Agent Entwicklungsaufgaben ausfuehrt
- Blueprint -> Implementation ueberfuehrt wird
- PR-Erstellung automatisiert wird

Nicht anzuwenden fuer:

- reine Analyse
- Dokumentationsaufgaben ohne Codeaenderung
