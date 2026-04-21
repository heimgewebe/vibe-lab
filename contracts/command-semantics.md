---
title: "Command Semantics (v0.1)"
status: active
canonicality: canonical
created: "2026-04-21"
updated: "2026-04-21"
author: "vibe-lab maintainers"
relations:
  - type: references
    target: "../schemas/command.read_context.schema.json"
  - type: references
    target: "../schemas/command.write_change.schema.json"
  - type: references
    target: "../schemas/command.validate_change.schema.json"
  - type: references
    target: "../docs/blueprints/blueprint-agent-operability-phase-1c.md"
---

# Command Semantics (v0.1)

## Zweck

Dieses Dokument definiert die **semantischen Verträge** der Commands
`read_context`, `write_change`, `validate_change`. Die JSON-Schemas unter
`schemas/command.*.schema.json` prüfen nur die **Form**. Dieses Dokument
ergänzt dazu:

1. Invarianten, die immer gelten müssen.
2. Anti-Invarianten, die nie auftreten dürfen.
3. Toleriert unscharfe Bereiche (explizite Lockerheit, keine stille).
4. Evolutions-Grenzen (was darf sich nach v0.2 ändern, was nicht).

Bei Widerspruch zwischen Schema und diesem Dokument gilt: Das Schema
prüft Syntax, dieses Dokument bindet Semantik. Beide müssen gleichzeitig
erfüllt sein.

## Geltungsbereich

- Version: **v0.1**
- Betrifft genau drei Commands: `read_context`, `write_change`,
  `validate_change`.
- Ein "Command-Record" ist ein JSON-Objekt mit Intent- und
  Ergebnisfeldern (gemäß existierendem Schema). Eine Aufspaltung in
  separate Input/Output-Schemas ist **explizit nach v0.2 verschoben**
  (siehe "Evolution Constraints" unten).

## Operationalisierungs-Status (Notation)

In diesem Dokument kennzeichnet jede Invariante / Anti-Invariante ihren
aktuellen Durchsetzungsgrad:

| Symbol | Bedeutung |
| ------ | --------- |
| ✅ **Schema** | Strukturell erzwungen durch `schemas/command.*.schema.json` — gilt für jede einzelne Record-Validierung. |
| ⚙️ **Chain-Check** | Semantisch operationalisiert in `scripts/docmeta/validate_command_chain.py` — gilt nur im Kettenkontext. |
| 📋 **Dokumentiert** | Semantisch definiert und als Ziel festgehalten. In v0.1 **nicht maschinell erzwungen**. Markiert die Evolutionsrichtung nach v0.2. |

Diese Kennzeichnung macht den Unterschied zwischen Dokumentation,
Beabsichtigung und Durchsetzung sichtbar — und verhindert stille
Überbehauptungen.

## Normalisiertes Vokabular

| Begriff             | Bedeutung in v0.1                                                          |
| ------------------- | -------------------------------------------------------------------------- |
| `command`           | Fester Diskriminator. Einer von `read_context`, `write_change`, `validate_change`. |
| `version`           | Vertrags-Version des Command-Records. In v0.1: `const "v0.1"`.             |
| `target_files`      | Repo-relative Pfade als Strings. Keine Glob-Expansion, keine Absolute.     |
| `locator`           | Menschlich lesbarer Anker im File (z. B. Heading, Marker). Nicht regex.    |
| `target_lines`      | Numerischer Bereich (z. B. `"42-47"`) oder einzelne Zeile. String-typisiert. |
| `change_type`       | Einer von `add`, `modify`, `remove`, `replace`. Fest; keine neuen Typen in v0.1. |
| `exact_before` / `exact_after` | Optionale Präzisionsfelder. Wenn gesetzt, Snapshot-Wortlaut. |
| `forbidden_changes` | Negative Scope-Definition. Freie Strings; Konvention ohne enum.            |
| `checks`            | Offene Liste prüfbarer Checks. Empfohlene Werte: `lint`, `test`, `docs-guard`. |
| `success` / `errors`| Binäres Resultat + detaillierte Fehlerzeilen.                              |
| "Drift"             | Zustand, in dem ein Command-Record strukturell valide, aber semantisch widersprüchlich ist — isoliert oder im Kettenkontext. Drift-Fälle werden vom Chain-Validator als `semantic_contradiction` (innerhalb eines Records) oder als eine der Cross-Command-Codes (`target_files_mismatch`, `locator_continuity_violation`, `command_sequence_invalid`) gemeldet. |

## Error-Klassen (strukturiertes Modell)

Der neue Chain-Validator (`scripts/docmeta/validate_command_chain.py`)
gibt strukturierte Fehler mit folgenden `code`-Werten aus. Der bestehende
Einzel-Validator `validate_agent_commands.py` bleibt unverändert bei
String-basiertem `contract_invalid`.

| `code`                         | Bedeutung                                                        | Status |
| ------------------------------ | ---------------------------------------------------------------- | ------ |
| `contract_invalid`             | Schema-Validierung eines Einzel-Records fehlgeschlagen.          | ⚙️ Chain-Check (via Schema-Delegation) |
| `command_sequence_invalid`     | Reihenfolge in der Kette falsch (z. B. `validate_change` vor `write_change`), oder gemischte Versionen. | ⚙️ Chain-Check |
| `target_files_mismatch`        | `write_change.target_files` nicht Teilmenge von `read_context.target_files`. | ⚙️ Chain-Check |
| `locator_continuity_violation` | `write_change.locator` ist leer oder enthält nur Whitespace. **Namens-Hinweis v0.1:** Der Code-Name ist für die vollständige v0.2-Semantik (Kopplung an `read_context.extracted_facts`) vorgehalten. In v0.1 deckt er ausschließlich den leeren/whitespace-Locator ab — die inhaltliche Kontinuität zwischen Lesekontext und Schreibanker ist **noch nicht implementiert** (📋 Dokumentiert für v0.2). | ⚙️ Chain-Check (v0.1 eingeschränkter Scope) |
| `semantic_contradiction`       | Feld-Kombination innerhalb eines Records widerspricht sich (siehe Anti-Invarianten). | ⚙️ Chain-Check |

Exit-Codes wie gewohnt: `0` OK, `1` Validation-Fehler, `2` Setup-Fehler
(fehlende Schemas, fehlende Fixtures). Das entspricht der Konvention
aller bestehenden Validatoren.

## Command: `read_context`

### Invariants

- ✅ **Schema** `target_files` enthält mindestens einen Pfad.
- 📋 **Dokumentiert** Jeder Pfad ist **repo-relativ**, ohne `./` oder `../`-Prefix.
- 📋 **Dokumentiert** Wenn `extracted_facts` gesetzt ist, referenzieren die Fakten **nur**
  Inhalte aus `target_files`. Externe Quellen gelten als Interpolation.
  (In v0.1 nicht maschinell prüfbar ohne Datei-I/O.)
- 📋 **Dokumentiert** `uncertainties` dokumentiert bewusst offene Punkte; leere Liste ist
  ausdrücklich erlaubt.

### Anti-Invariants

- ⚙️ **Chain-Check** `target_files` enthält denselben Pfad mehrfach (redundante Lesung).
- 📋 **Dokumentiert** `extracted_facts` enthält einen Fakt, der in keinem `target_file`
  verifizierbar ist (stille Interpolation). In v0.1 nicht maschinell prüfbar
  ohne Dateilesen.
- 📋 **Dokumentiert** `target_files` enthält Globs (`**/*.py`) — in v0.1 nicht erlaubt,
  aber nicht strukturell geblockt.

### Tolerated Ambiguity

- Reihenfolge der Pfade in `target_files` ist nicht signifikant.
- `extracted_facts` ist freier Text; keine Struktur, keine Normalisierung.
- `uncertainties` ist freier Text; wird nicht gegen ein Enum geprüft.

### Evolution Constraints (v0.1 → v0.2)

- **Breaking:** Ein `target_files`-Eintrag wird zu einem strukturierten
  Objekt (`{path, role}`) werden. v0.1 erwartet Strings.
- **Non-Breaking:** Zusätzliche optionale Felder (z. B. `read_scope`)
  dürfen in v0.2 hinzukommen.

## Command: `write_change`

### Invariants

- ✅ **Schema** Mindestens eines von `locator` oder `target_lines` ist gesetzt
  (`anyOf`).
- ✅ **Schema** `forbidden_changes` ist immer gesetzt (`required`), kann aber
  leer sein. Eine leere Liste bedeutet: keine expliziten Ausschlüsse.
- ✅ **Schema** `change_type` ist genau einer von `add`, `modify`, `remove`, `replace`.
- 📋 **Dokumentiert** Wenn `exact_before` gesetzt ist, referenziert es eine Stelle, die im
  Original-File existiert. In v0.1 **nicht maschinell geprüft** (erfordert
  Datei-I/O, das im Design explizit ausgeschlossen ist).
- 📋 **Dokumentiert** Wenn `exact_after` gesetzt ist, ist der Post-Change-Zustand
  deterministisch (kein Platzhalter, kein Timestamp).

### Anti-Invariants

- ⚙️ **Chain-Check** `change_type: "remove"` mit gesetztem `exact_after`. Ein Remove hat
  keinen Nachher-Zustand.
- ⚙️ **Chain-Check** `change_type: "add"` mit gesetztem `exact_before`. Ein Add hat keinen
  Vorher-Zustand an derselben Stelle.
- ⚙️ **Chain-Check** `exact_before == exact_after`. Kein echter Change.
- ⚙️ **Chain-Check** `target_files` enthält Pfade, die nicht in `read_context.target_files`
  vorkamen — im Chain-Kontext: `target_files_mismatch`.
- ✅ **Schema** `locator` ist leer (geblockt per `minLength: 1` im Schema).

### Tolerated Ambiguity

- `locator` ist freier Text. Heading, Kommentar, eindeutiges Schlagwort —
  alles zulässig, solange eindeutig im File auffindbar.
- `forbidden_changes` ist freier Text. Keine Grammatik, keine Enum-Liste.
- `target_lines`-Format ist ein String (`"42"` oder `"42-47"`); keine
  harte Grammatik-Prüfung in v0.1.

### Evolution Constraints (v0.1 → v0.2)

- **Breaking:** `change_type` wird möglicherweise `rename`/`move`
  ergänzt. Aktuelle v0.1-Fixtures dürfen nicht vorwegnehmen.
- **Non-Breaking:** `locator` könnte strukturierter werden
  (`{kind: "heading", value: "..."}`), aber Abwärtskompatibilität via
  Union-Typ.
- **Out-of-scope (v0.2):** Split in `command.write_change.input.schema`
  vs. `.output.schema`.

## Command: `validate_change`

### Invariants

- ✅ **Schema** `checks[]` ist nicht leer.
- ✅ **Schema** `success: true` → `errors` ist leer (`if/then`).
- ✅ **Schema** `success: false` → `errors` hat mindestens einen Eintrag (`if/then`).
- 📋 **Dokumentiert** Jeder `errors[]`-Eintrag ist auf mindestens einen `checks[]`-Eintrag
  **referenzierbar** (per Präfix `lint: ...`, `test: ...` etc.). In v0.1 nicht
  maschinell erzwungen.

### Anti-Invariants

- ✅ **Schema** `success: true` mit nicht-leerem `errors`.
- ✅ **Schema** `success: false` mit leerem `errors`.
- ⚙️ **Chain-Check** `validate_change` steht in einer Chain **vor** `write_change`
  (`command_sequence_invalid`).
- ✅ **Schema** `checks[]` enthält Duplikate (`uniqueItems`).

### Tolerated Ambiguity

- `checks[]` ist absichtlich **kein Enum**. Empfohlene Werte: `lint`,
  `test`, `docs-guard` (siehe Blueprint §C3). Andere sind zulässig.
- `errors[]`-Strings sind freitext. Keine Normalisierung auf
  strukturierte Fehler in v0.1.

### Evolution Constraints (v0.1 → v0.2)

- **Breaking:** `errors[]` wird zu strukturierten Objekten
  (`{check, code, message}`). v0.1 bleibt String-Liste.
- **Non-Breaking:** zusätzliche Felder wie `duration_seconds` erlaubt.

## Cross-Command-Invarianten (Chain-Ebene)

Eine gültige Kette hat die Form:

```text
read_context → write_change → validate_change
```

### Chain Invariants

- ⚙️ **Chain-Check** Reihenfolge ist fest: nur `read_context → write_change → validate_change`
  ist in v0.1 gültig.
- ⚙️ **Chain-Check** `write_change.target_files` ⊆ `read_context.target_files`
  (Locator-Continuity auf File-Ebene).
- 📋 **Dokumentiert** `write_change.locator` oder `write_change.target_lines` bezieht sich
  auf ein File aus dem gelesenen Kontext. In v0.1 wird nur der leere/whitespace-Locator
  als `locator_continuity_violation` gemeldet. Eine Kopplung an
  `extracted_facts` (inhaltliche Kontinuität) ist **nicht implementiert**.
- ✅ **Schema** `validate_change.success = true` impliziert `validate_change.errors = []`
  (direkt durch Schema-`if/then` auf Record-Ebene erzwungen, keine separate
  Chain-Level-Prüfung).

### Chain Anti-Invariants

- ⚙️ **Chain-Check** `write_change.target_files \ read_context.target_files ≠ ∅`
  → `target_files_mismatch`.
- ⚙️ **Chain-Check** Reihenfolge gebrochen (z. B. zwei `write_change` hintereinander,
  `read_context` fehlt) → `command_sequence_invalid`.
- 📋 **Dokumentiert** `validate_change.success = false`, aber `errors` enthält keinen Bezug
  zu einem `checks`-Eintrag → in v0.1 toleriert, nicht als Anti-Invariant erzwungen.

## Cross-Contract Invariants (Handoff → Commands)

Der Handoff (`schemas/agent.handoff.schema.json`) und die Command-Chain
(`schemas/command.*.schema.json`) sind getrennte Verträge mit einer
gemeinsamen Wahrheitslinie. Dieser Abschnitt bindet beide aneinander —
minimal, testbar, ohne neue Laufzeitlogik.

Geprüft wird diese Linie durch
`scripts/docmeta/validate_command_chain.py::validate_cross_contract` und
durch das Fixture-Korpus unter `tests/fixtures/cross_contract/`.

### Invariants

- ⚙️ **Chain-Check** `handoff.target_files` und `target_files` jedes Chain-Records mit `target_files`-Feld (`read_context`, `write_change`) müssen identisch sein — kein File darf fehlen, kein File darf außerhalb des Handoff-Scopes hinzukommen. Verletzung → `handoff_target_drift`.
- ⚙️ **Chain-Check** `handoff.change_type` ∈ {`add`, `modify`, `remove`,
  `replace`} **muss** durch einen `write_change`-Record mit **identischem**
  `change_type` erfüllt sein. Fehlt der Record oder weicht der
  `change_type` ab → `handoff_intent_mismatch`.
- ⚙️ **Chain-Check** Wenn `handoff.exact_before` oder `handoff.exact_after`
  gesetzt sind, muss der `write_change`-Record das jeweilige Feld
  wörtlich übernehmen. Silent-Omission oder Silent-Divergenz →
  `handoff_state_drift`.
- ⚙️ **Chain-Check** Der Handoff selbst muss gegen
  `schemas/agent.handoff.schema.json` validieren, bevor Cross-Contract-
  Checks überhaupt greifen. Verletzung → `handoff_contract_invalid`.

### Anti-Invariants

- ⚙️ **Chain-Check** Chain-Record enthält Dateien, die nicht in
  `handoff.target_files` stehen, oder Handoff-Dateien fehlen in einem
  Chain-Record → `handoff_target_drift` (stille Drift in beide Richtungen).
- ⚙️ **Chain-Check** Handoff verlangt eine Änderung, die Chain enthält
  aber keinen `write_change` oder ein `write_change` mit anderem
  `change_type` → `handoff_intent_mismatch`.
- ⚙️ **Chain-Check** Implizite Zustands-Ableitung: `write_change` lässt
  ein vom Handoff vorgegebenes `exact_before`/`exact_after` weg oder
  verändert es → `handoff_state_drift`.

### Error-Klassen (Ergänzung)

| `code`                       | Bedeutung                                                                                                 | Status |
| ---------------------------- | --------------------------------------------------------------------------------------------------------- | ------ |
| `handoff_contract_invalid`   | Handoff-Objekt verletzt `agent.handoff.schema.json` oder Schema fehlt.                                    | ⚙️ Chain-Check |
| `handoff_target_drift`       | `handoff.target_files` und `target_files` eines Chain-Records (mit `target_files`-Feld) stimmen nicht überein — Dateien fehlen oder sind außerhalb des Handoff-Scopes. | ⚙️ Chain-Check |
| `handoff_intent_mismatch`    | `handoff.change_type` wird durch die Chain nicht erfüllt (kein `write_change` oder abweichender `change_type`). | ⚙️ Chain-Check |
| `handoff_state_drift`        | `handoff.exact_before`/`exact_after` wird still im `write_change` weggelassen oder verändert.            | ⚙️ Chain-Check |

### Scope-Disziplin (v0.1)

- Cross-Contract-Checks nutzen ausschließlich Felder, die beide Schemata
  bereits kennen. Keine heuristische Ableitung, keine Interpretation von
  `scope`, `normalized_task` oder `extracted_facts`.
- Silent Defaults sind explizit verboten: fehlen Felder im Handoff, wird
  nichts angenommen — nur was dort steht, wird an die Chain gebunden.
- Die Checks kürzen bei `handoff_contract_invalid` ab: ohne schema-
  valides Handoff ist Cross-Contract-Prüfung bedeutungslos.

### Evolution Constraints (v0.1 → v0.2)

- **Breaking:** Weitere Pflicht-Bindungen (z. B. `handoff.locator` ↔
  `write_change.locator`) sind bewusst **noch nicht** erzwungen, um
  v0.2-Evolution des `locator`-Typs nicht einzufrieren.
- **Non-Breaking:** Zusätzliche Codes wie `handoff_locator_drift` dürfen
  in v0.2 hinzukommen.

## Versionsstrategie

### Begriffe

- **Breaking Change:** Ein Change, der einen bisher gültigen v0.1-Record
  ungültig macht oder seine Semantik verändert. Beispiele: required
  werden, enum-Wert entfernen, Feldtyp wechseln.
- **Non-Breaking Change:** Optionales Feld hinzufügen, Dokumentation
  erweitern, zusätzliche tolerated-ambiguity-Bereiche dokumentieren.

### Regeln

1. Jeder Breaking Change verlangt Version-Bump (`v0.1` → `v0.2`).
2. Die `version`-`const` im Schema wird pro Bump aktualisiert.
3. Alte Records mit `version: "v0.1"` bleiben durch separate
   v0.1-Schemas validierbar, solange v0.1 unterstützt wird.
4. Deprecation-Fenster ist mindestens **ein Blueprint-Zyklus** (Phase 2).
5. Chain-Validator akzeptiert in einer Kette nur Records **derselben**
   `version`. Gemischte Versionen → `command_sequence_invalid`.

### Out-of-Scope für v0.1 (bewusst)

- Separate Input-/Output-Schemas pro Command.
- Strukturiertes `errors[]`-Objekt in `validate_change`.
- Glob/Regex in `target_files` / `locator`.
- Runtime-Execution mit echten Datei-Mutationen (siehe Blueprint Phase F).

## Bezüge

- `schemas/command.read_context.schema.json`
- `schemas/command.write_change.schema.json`
- `schemas/command.validate_change.schema.json`
- `docs/blueprints/blueprint-agent-operability-phase-1c.md`
- `scripts/docmeta/validate_agent_commands.py`
- `scripts/docmeta/validate_command_chain.py` (neu in dieser Phase)
- `tools/vibe-cli/replay_minimal.py` (neu in dieser Phase — deterministischer
  Simulation-Trace-Generator; kein Execution-Runner, keine Datei-Mutation,
  kein echter Replay im Sinne von Befehlsausführung)
