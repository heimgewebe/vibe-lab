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
- "Drift"             | Zustand, in dem ein Command-Record strukturell valide, aber semantisch widersprüchlich ist — isoliert oder im Kettenkontext. Drift-Fälle werden vom Chain-Validator als `semantic_contradiction` (innerhalb eines Records) oder als eine der Cross-Command-Codes (`target_files_mismatch`, `locator_continuity_violation`, `command_sequence_invalid`) gemeldet. |

## Error-Klassen (strukturiertes Modell)

Der neue Chain-Validator (`scripts/docmeta/validate_command_chain.py`)
gibt strukturierte Fehler mit folgenden `code`-Werten aus. Der bestehende
Einzel-Validator `validate_agent_commands.py` bleibt unverändert bei
String-basiertem `contract_invalid`.

| `code`                         | Bedeutung                                                        |
| ------------------------------ | ---------------------------------------------------------------- |
| `contract_invalid`             | Schema-Validierung eines Einzel-Records fehlgeschlagen.          |
| `command_sequence_invalid`     | Reihenfolge in der Kette falsch (z. B. `validate_change` vor `write_change`). |
| `target_files_mismatch`        | `write_change.target_files` nicht Teilmenge von `read_context.target_files`. |
| `locator_continuity_violation` | `write_change.locator` fehlt oder steht im Widerspruch zu `read_context.extracted_facts`. |
| `semantic_contradiction`       | Feld-Kombination innerhalb eines Records widerspricht sich (siehe Anti-Invarianten). |

Exit-Codes wie gewohnt: `0` OK, `1` Validation-Fehler, `2` Setup-Fehler
(fehlende Schemas, fehlende Fixtures). Das entspricht der Konvention
aller bestehenden Validatoren.

## Command: `read_context`

### Invariants

- `target_files` enthält mindestens einen Pfad (Schema).
- Jeder Pfad ist **repo-relativ**, ohne `./` oder `../`-Prefix.
- Wenn `extracted_facts` gesetzt ist, referenzieren die Fakten **nur**
  Inhalte aus `target_files`. Externe Quellen gelten als Interpolation.
- `uncertainties` dokumentiert bewusst offene Punkte; leere Liste ist
  ausdrücklich erlaubt.

### Anti-Invariants

- `target_files` enthält denselben Pfad mehrfach (redundante Lesung).
- `extracted_facts` enthält einen Fakt, der in keinem `target_file`
  verifizierbar ist (stille Interpolation).
- `target_files` enthält Globs (`**/*.py`) — in v0.1 nicht erlaubt.

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

- Mindestens eines von `locator` oder `target_lines` ist gesetzt
  (Schema-`anyOf`).
- `forbidden_changes` ist immer gesetzt (Schema-`required`), kann aber
  leer sein. Eine leere Liste bedeutet: keine expliziten Ausschlüsse.
- `change_type` ist genau einer von `add`, `modify`, `remove`, `replace`.
- Wenn `exact_before` gesetzt ist, referenziert es eine Stelle, die im
  Original-File existiert (im Chain-Kontext prüfbar).
- Wenn `exact_after` gesetzt ist, ist der Post-Change-Zustand
  deterministisch (kein Platzhalter, kein Timestamp).

### Anti-Invariants

- `change_type: "remove"` mit gesetztem `exact_after`. Ein Remove hat
  keinen Nachher-Zustand.
- `change_type: "add"` mit gesetztem `exact_before`. Ein Add hat keinen
  Vorher-Zustand an derselben Stelle.
- `exact_before == exact_after`. Kein echter Change.
- `target_files` enthält Pfade, die nicht in `read_context.target_files`
  vorkamen — im Chain-Kontext: `target_files_mismatch`.
- `locator` ist leer, aber gesetzt (vom Schema per `minLength: 1`
  geblockt; hier als Semantik-Anker dokumentiert).

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

- `checks[]` ist nicht leer (Schema).
- `success: true` → `errors` ist leer (Schema `if/then`).
- `success: false` → `errors` hat mindestens einen Eintrag (Schema `if/then`).
- Jeder `errors[]`-Eintrag ist auf mindestens einen `checks[]`-Eintrag
  **referenzierbar** (per Präfix `lint: ...`, `test: ...` etc.). Nicht
  schematisch erzwungen — semantisch erwartet.

### Anti-Invariants

- `success: true` mit nicht-leerem `errors` (Schema-Blocker).
- `success: false` mit leerem `errors` (Schema-Blocker).
- `validate_change` steht in einer Chain **vor** `write_change`
  (`command_sequence_invalid`).
- `checks[]` enthält Duplikate (Schema-`uniqueItems`).

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

- Reihenfolge ist fest. Keine andere Permutation ist in v0.1 gültig.
- `write_change.target_files` ⊆ `read_context.target_files`
  (Locator-Continuity auf File-Ebene).
- `write_change.locator` oder `write_change.target_lines` bezieht sich
  auf ein File aus dem gelesenen Kontext.
- `validate_change.success = true` **impliziert** `validate_change.errors = []`.
  Das gilt auch Record-intern (Schema), aber wird auf Chain-Ebene erneut
  geprüft, damit eine Chain-Zusammenfassung nicht widersprüchlich ist.

### Chain Anti-Invariants

- `write_change.target_files \ read_context.target_files ≠ ∅`
  → `target_files_mismatch`.
- Reihenfolge gebrochen (z. B. zwei `write_change` hintereinander,
  `read_context` fehlt) → `command_sequence_invalid`.
- `validate_change.success = false`, aber `errors` enthält keinen Bezug
  zu einem `checks`-Eintrag → **toleriert** (nicht als Anti-Invariant in
  v0.1, nur Hinweis).

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
- `tools/vibe-cli/replay_minimal.py` (neu in dieser Phase, strikter
  Simulations-Pfad ohne Datei-Mutation)
