---
title: "Agent Operability — Fixture-Matrix (v0.1)"
status: active
canonicality: derived
created: "2026-04-21"
updated: "2026-04-23"
author: "vibe-lab maintainers"
relations:
  - type: references
    target: "../../contracts/command-semantics.md"
  - type: references
    target: "../../tests/fixtures/agent_commands"
  - type: references
    target: "../../tests/fixtures/command_chains"
  - type: references
    target: "../../tests/fixtures/cross_contract"
---

# Agent Operability — Fixture-Matrix (v0.1)

Dieses Dokument ist ein Referenzartefakt, das Coverage-Kartierung anstrebt —
nicht Validator-Wahrheit. Die Äquivalenzklassen und Gap-Liste beschreiben den
Ist-Zustand der Fixtures; sie ersetzen keine maschinelle Prüfung. Es enthält
**keine neue Validierungslogik** und keine Schema-Änderungen.

Quellen:
- `tests/fixtures/agent_commands/**`
- `tests/fixtures/command_chains/**`
- `tests/fixtures/cross_contract/**`
- `contracts/command-semantics.md`

Audit-Notation (Minimalstandard):
- `covered: true|false`
- `test_ref: <Fixture- oder Testreferenz>`
- `gap: missing|intentional (v0.2)` nur fuer offene Abdeckungsluecken

---

## 1. Command-Level Coverage

### 1.1 `read_context`

**Audit-Oberflaeche**

| Pruefbereich | Audit |
| ------------ | ----- |
| Schema-Validitaet inkl. optionaler Felder | `covered: true; test_ref: tests/fixtures/agent_commands/read_context/valid-minimal.json, tests/fixtures/agent_commands/read_context/valid-edge-complex.json` |
| Required-/Version-/Diskriminator-Guards | `covered: true; test_ref: tests/fixtures/agent_commands/read_context/contract-invalid-missing-version.json, tests/fixtures/agent_commands/read_context/contract-invalid-wrong-version.json, tests/fixtures/agent_commands/read_context/contract-invalid-wrong-command.json` |
| Collection-/Constraint-Guards | `covered: true; test_ref: tests/fixtures/agent_commands/read_context/contract-invalid-empty-target-files.json, tests/fixtures/agent_commands/read_context/contract-invalid-empty-fact-string.json` |

**Gültige Fixtures**

| Fixture | Beschreibung |
| ------- | ------------ |
| `tests/fixtures/agent_commands/read_context/valid-minimal.json` | Minimaler Record mit zwei `target_files`, `extracted_facts`, `uncertainties`. |
| `tests/fixtures/agent_commands/read_context/valid-edge-complex.json` | Vier `target_files`, drei `extracted_facts`, zwei `uncertainties` — volle optionale Feldnutzung. |

**Ungültige Fixtures (contract_invalid)**

| Fixture | Fehlerklasse | Was getestet wird |
| ------- | ------------ | ----------------- |
| `tests/fixtures/agent_commands/read_context/contract-invalid-empty-target-files.json` | `contract_invalid` | `target_files: []` — verletzt `minItems: 1`. |
| `tests/fixtures/agent_commands/read_context/contract-invalid-missing-version.json` | `contract_invalid` | Fehlendes Pflichtfeld `version`. |
| `tests/fixtures/agent_commands/read_context/contract-invalid-wrong-version.json` | `contract_invalid` | `version: "v0.2"` — verletzt `const: "v0.1"`. |
| `tests/fixtures/agent_commands/read_context/contract-invalid-wrong-command.json` | `contract_invalid` | `command: "read_context_v2"` — unbekannter Diskriminator. |
| `tests/fixtures/agent_commands/read_context/contract-invalid-empty-fact-string.json` | `contract_invalid` | `extracted_facts: [""]` — leerer String in Array verletzt `minLength: 1`. |

---

### 1.2 `write_change`

**Audit-Oberflaeche**

| Pruefbereich | Audit |
| ------------ | ----- |
| Schema-Validitaet inkl. Locality-Varianten | `covered: true; test_ref: tests/fixtures/agent_commands/write_change/valid-minimal.json, tests/fixtures/agent_commands/write_change/valid-edge-add-with-target-lines.json, tests/fixtures/agent_commands/write_change/valid-edge-remove.json` |
| Version-/Diskriminator-/Change-Type-Guards | `covered: true; test_ref: tests/fixtures/agent_commands/write_change/contract-invalid-wrong-version.json, tests/fixtures/agent_commands/write_change/contract-invalid-wrong-command.json, tests/fixtures/agent_commands/write_change/contract-invalid-missing-change-type.json, tests/fixtures/agent_commands/write_change/contract-invalid-invalid-change-type.json` |
| Required-/AnyOf-/Collection-Guards | `covered: true; test_ref: tests/fixtures/agent_commands/write_change/contract-invalid-empty-target-files.json, tests/fixtures/agent_commands/write_change/contract-invalid-missing-locator.json` |

**Gültige Fixtures**

| Fixture | Beschreibung |
| ------- | ------------ |
| `tests/fixtures/agent_commands/write_change/valid-minimal.json` | `change_type: modify`, `locator` + `exact_before/exact_after`, nicht-leeres `forbidden_changes`. |
| `tests/fixtures/agent_commands/write_change/valid-edge-add-with-target-lines.json` | `change_type: add`, `target_lines` statt `locator`, `exact_after` gesetzt. |
| `tests/fixtures/agent_commands/write_change/valid-edge-remove.json` | `change_type: remove`, `locator` + `exact_before`, `forbidden_changes` mit Eintrag. |

**Ungültige Fixtures (contract_invalid)**

| Fixture | Fehlerklasse | Was getestet wird |
| ------- | ------------ | ----------------- |
| `tests/fixtures/agent_commands/write_change/contract-invalid-empty-target-files.json` | `contract_invalid` | `target_files: []` — verletzt `minItems: 1`. |
| `tests/fixtures/agent_commands/write_change/contract-invalid-wrong-version.json` | `contract_invalid` | `version: "v0.2"` — verletzt `const: "v0.1"`. |
| `tests/fixtures/agent_commands/write_change/contract-invalid-wrong-command.json` | `contract_invalid` | `command: "write_change_v2"` — unbekannter Diskriminator. |
| `tests/fixtures/agent_commands/write_change/contract-invalid-missing-change-type.json` | `contract_invalid` | Fehlendes Pflichtfeld `change_type`. |
| `tests/fixtures/agent_commands/write_change/contract-invalid-invalid-change-type.json` | `contract_invalid` | `change_type: "rename"` — kein gültiger Enum-Wert in v0.1. |
| `tests/fixtures/agent_commands/write_change/contract-invalid-missing-locator.json` | `contract_invalid` | Weder `locator` noch `target_lines` gesetzt — verletzt `anyOf`. |

---

### 1.3 `validate_change`

**Audit-Oberflaeche**

| Pruefbereich | Audit |
| ------------ | ----- |
| Schema-Validitaet fuer Erfolgs-/Fehlerpfad | `covered: true; test_ref: tests/fixtures/agent_commands/validate_change/valid-success.json, tests/fixtures/agent_commands/validate_change/valid-failure.json, tests/fixtures/agent_commands/validate_change/valid-edge-multi-checks.json` |
| Checks-/Errors-Constraint-Guards | `covered: true; test_ref: tests/fixtures/agent_commands/validate_change/contract-invalid-empty-checks.json, tests/fixtures/agent_commands/validate_change/contract-invalid-duplicate-checks.json, tests/fixtures/agent_commands/validate_change/contract-invalid-success-with-errors.json, tests/fixtures/agent_commands/validate_change/contract-invalid-failure-empty-errors.json` |
| Version-const-Verletzung fuer `validate_change` | `covered: false; test_ref: —; gap: missing` |

**Gültige Fixtures**

| Fixture | Beschreibung |
| ------- | ------------ |
| `tests/fixtures/agent_commands/validate_change/valid-success.json` | `success: true`, `errors: []`, zwei Checks. |
| `tests/fixtures/agent_commands/validate_change/valid-failure.json` | `success: false`, `errors` mit einem Eintrag, drei Checks. |
| `tests/fixtures/agent_commands/validate_change/valid-edge-multi-checks.json` | `success: true`, drei Checks (`lint`, `test`, `docs-guard`). |

**Ungültige Fixtures (contract_invalid)**

| Fixture | Fehlerklasse | Was getestet wird |
| ------- | ------------ | ----------------- |
| `tests/fixtures/agent_commands/validate_change/contract-invalid-wrong-command.json` | `contract_invalid` | `command: "validate_change_v2"` — unbekannter Diskriminator. |
| `tests/fixtures/agent_commands/validate_change/contract-invalid-empty-checks.json` | `contract_invalid` | `checks: []` — verletzt `minItems: 1`. |
| `tests/fixtures/agent_commands/validate_change/contract-invalid-duplicate-checks.json` | `contract_invalid` | `checks: ["lint", "lint"]` — verletzt `uniqueItems`. |
| `tests/fixtures/agent_commands/validate_change/contract-invalid-success-with-errors.json` | `contract_invalid` | `success: true` + nicht-leeres `errors` — verletzt `if/then`. |
| `tests/fixtures/agent_commands/validate_change/contract-invalid-failure-empty-errors.json` | `contract_invalid` | `success: false` + `errors: []` — verletzt `if/then`. |

---

## 2. Chain-Level Coverage

Alle Chain-Fixtures liegen unter `tests/fixtures/command_chains/`. Sidecars
(`*.expected.json`) deklarieren `expected_errors: [codes]`. Fehlt ein
Sidecar, muss die Chain fehlerfrei validieren.

**Gültige Fixtures**

| Fixture | Was getestet wird |
| ------- | ----------------- |
| `tests/fixtures/command_chains/valid-minimal.json` | Korrekte Reihenfolge `read_context → write_change → validate_change`, alle Felder konsistent, `target_files` übereinstimmend. |
| `tests/fixtures/command_chains/valid-errors-with-check-prefix.json` | `validate_change` mit `success: false` und korrekt gebundenen `errors[]` — beide Einträge beginnen mit einem gültigen `<check>:`-Präfix aus `checks[]`. |

**Ungültige Fixtures**

| Fixture | Sidecar | Erwartete Fehler | Was getestet wird |
| ------- | ------- | ---------------- | ----------------- |
| `tests/fixtures/command_chains/invalid-wrong-order.json` | `invalid-wrong-order.expected.json` | `command_sequence_invalid` | `write_change` vor `read_context` — gebrochene Reihenfolge. |
| `tests/fixtures/command_chains/invalid-target-files-mismatch.json` | `invalid-target-files-mismatch.expected.json` | `target_files_mismatch` | `write_change.target_files` enthält `README.md`, das nicht in `read_context.target_files` steht. |
| `tests/fixtures/command_chains/invalid-remove-with-exact-after.json` | `invalid-remove-with-exact-after.expected.json` | `semantic_contradiction` | `change_type: remove` mit gesetztem `exact_after` — semantisch widersprüchlich. |
| `tests/fixtures/command_chains/invalid-mixed-versions.json` | `invalid-mixed-versions.expected.json` | `command_sequence_invalid`, `contract_invalid` | `write_change.version: "v0.2"` in ansonsten v0.1-Kette — gemischte Versionen. |
| `tests/fixtures/command_chains/invalid-empty-locator.json` | `invalid-empty-locator.expected.json` | `locator_continuity_violation` | `write_change.locator` enthält nur Whitespace (`"   "`) — verletzt Locator-Kontinuität (v0.1-Scope). |
| `tests/fixtures/command_chains/invalid-add-with-exact-before.json` | `invalid-add-with-exact-before.expected.json` | `semantic_contradiction` | `change_type: add` mit gesetztem `exact_before` — ein Add hat keinen Vorher-Zustand an derselben Stelle. |
| `tests/fixtures/command_chains/invalid-error-no-check-prefix.json` | `invalid-error-no-check-prefix.expected.json` | `validate_error_unbindable` | `errors[]`-Eintrag ohne `<check>:`-Präfix (`"something went wrong"`) — kein Bezug zu `checks[]`. |
| `tests/fixtures/command_chains/invalid-error-unknown-check-prefix.json` | `invalid-error-unknown-check-prefix.expected.json` | `validate_error_unbindable` | `errors[]`-Eintrag mit Präfix `test:`, aber `checks: ["lint"]` — Präfix ist nicht in `checks[]`. |
| `tests/fixtures/command_chains/invalid-error-partial-binding.json` | `invalid-error-partial-binding.expected.json` | `validate_error_unbindable` | Partiell gebundene `errors[]`: ein gültiger Eintrag (`lint:`) + ein ungebundener (`"broken link detected"`) — nur der ungebundene Eintrag löst Fehler aus. |
| `tests/fixtures/command_chains/invalid-validate-without-write.json` | `invalid-validate-without-write.expected.json` | `command_sequence_invalid`, `validate_without_write` | `validate_change` ohne vorangehendes `write_change` — `read_context → validate_change`-Sequenz. |
| `tests/fixtures/command_chains/invalid-validate-empty-targets.json` | `invalid-validate-empty-targets.expected.json` | `contract_invalid`, `validate_targets_out_of_scope` | `write_change.target_files: []` — leere Target-Liste (verletzt Schema + Plausibilitätsprüfung). |
| `tests/fixtures/command_chains/invalid-validate-orphaned.json` | `invalid-validate-orphaned.expected.json` | `contract_invalid`, `validate_targets_out_of_scope` | `write_change` ohne `target_files`-Schlüssel — `validate_change` ohne plausiblen Datei-Scope. |

**Audit-Oberflaeche Chain-Level**

| Kategorie | Audit |
| --------- | ----- |
| Korrekte Reihenfolge | `covered: true; test_ref: tests/fixtures/command_chains/valid-minimal.json` |
| Gebrochene Reihenfolge | `covered: true; test_ref: tests/fixtures/command_chains/invalid-wrong-order.json` |
| Target-Kontinuitaet (Datei-Ebene) | `covered: true; test_ref: tests/fixtures/command_chains/invalid-target-files-mismatch.json` |
| Semantischer Widerspruch (remove+exact_after) | `covered: true; test_ref: tests/fixtures/command_chains/invalid-remove-with-exact-after.json` |
| Semantischer Widerspruch (add+exact_before) | `covered: true; test_ref: tests/fixtures/command_chains/invalid-add-with-exact-before.json` |
| Versionskonsistenz | `covered: true; test_ref: tests/fixtures/command_chains/invalid-mixed-versions.json, scripts/docmeta/test_command_version_policy.py` |
| Locator-Kontinuitaet (leerer/whitespace Locator) | `covered: true; test_ref: tests/fixtures/command_chains/invalid-empty-locator.json` |
| `validate_error_unbindable` — gueltig (korrekte Praefixe) | `covered: true; test_ref: tests/fixtures/command_chains/valid-errors-with-check-prefix.json` |
| `validate_error_unbindable` — ungueltig (kein Praefix) | `covered: true; test_ref: tests/fixtures/command_chains/invalid-error-no-check-prefix.json` |
| `validate_error_unbindable` — ungueltig (unbekanntes Praefix) | `covered: true; test_ref: tests/fixtures/command_chains/invalid-error-unknown-check-prefix.json` |
| `validate_error_unbindable` — partiell gebunden | `covered: true; test_ref: tests/fixtures/command_chains/invalid-error-partial-binding.json` |
| `validate_without_write` — validate ohne write | `covered: true; test_ref: tests/fixtures/command_chains/invalid-validate-without-write.json` |
| `validate_targets_out_of_scope` — write mit leerem target_files | `covered: true; test_ref: tests/fixtures/command_chains/invalid-validate-empty-targets.json` |
| `validate_targets_out_of_scope` — write ohne target_files-Schluessel | `covered: true; test_ref: tests/fixtures/command_chains/invalid-validate-orphaned.json` |

---

## 3. Cross-Contract Coverage

Alle Cross-Contract-Fixtures liegen unter `tests/fixtures/cross_contract/`
und binden ein `handoff`-Objekt an eine `chain`. Abgedeckt werden die
Invarianten aus `contracts/command-semantics.md` — Abschnitt "Cross-Contract
Invariants (Handoff → Commands)".

**Gültige Fixtures**

| Fixture | Was getestet wird |
| ------- | ----------------- |
| `tests/fixtures/cross_contract/valid/minimal_chain.json` | Handoff (PASS, mit `exact_before/exact_after`) vollständig durch Chain erfüllt. `target_files`, `change_type`, `exact_before/exact_after` übereinstimmend. |
| `tests/fixtures/cross_contract/valid/minimal_chain_add.json` | Nahkontrast für SEM-EMPTY-ASSERTED: `change_type=add` mit nicht-leerem `exact_after` — valide Post-Zustandsbehauptung. Belegt, dass die Regel nicht zu `add` mit gültigem Post-Zustand über-feuert. |

**Ungültige Fixtures**

| Fixture | Erwartete Fehler | Fehlerklasse | Was getestet wird |
| ------- | ---------------- | ------------ | ----------------- |
| `tests/fixtures/cross_contract/invalid/contract_invalid.json` | `handoff_contract_invalid` | Handoff-Schema-Verletzung | Handoff ohne `status`-Feld — verletzt `agent.handoff.schema.json`. Cross-Contract-Checks werden abgebrochen. |
| `tests/fixtures/cross_contract/invalid/target_drift.json` | `handoff_target_drift` | Target-Drift | `handoff.target_files: ["docs/foundations/vision.md"]`, Chain verwendet `docs/index.md` — Dateien stimmen nicht überein. |
| `tests/fixtures/cross_contract/invalid/target_drift_extra.json` | `handoff_target_drift` | Target-Drift (umgekehrt) | Handoff hat ein File, Chain hat zwei — Chain enthält Dateien außerhalb des Handoff-Scopes. |
| `tests/fixtures/cross_contract/invalid/state_drift.json` | `handoff_state_drift` | State-Drift | Handoff setzt `exact_before/exact_after`, `write_change` lässt beide weg — stille Divergenz. |
| `tests/fixtures/cross_contract/invalid/contradiction.json` | `semantic_contradiction` | Semantischer Widerspruch | `change_type: remove` mit `exact_after` im `write_change` — Record-interne Verletzung innerhalb eines Cross-Contract-Tests. |
| `tests/fixtures/cross_contract/invalid/empty_change_state.json` | `semantic_contradiction` | Empty asserted state | `change_type: add` mit `exact_after=""` — Post-Zustand wird behauptet, ist aber leer. Nahkontrast: `cross_contract/valid/minimal_chain_add.json` (gleiche Form, `exact_after` nicht-leer). Phase-2-Strukturkonsequenz aus Experiment `2026-04-23_agent-failure-surface`. |
| `tests/fixtures/cross_contract/invalid/semantic_mismatch.json` | `command_sequence_invalid`, `handoff_intent_mismatch`, `validate_without_write` | Handoff-Intent + Sequenz | Handoff verlangt `modify`, Chain enthält kein `write_change` (nur `read_context → validate_change`) — Intent nicht erfüllt, Reihenfolge gebrochen, validate ohne write. |
| `tests/fixtures/cross_contract/invalid/version_conflict.json` | `command_sequence_invalid`, `contract_invalid` | Versions- + Contract-Verletzung | `write_change.version: "v0.2"` in Cross-Contract-Kontext — gleiche Prüfung wie im reinen Chain-Fall, aber eingebettet in Handoff-Szenario. |
| `tests/fixtures/cross_contract/invalid/handoff_locator_drift/locator_drift.json` | `handoff_locator_drift` | Locator-Drift | `handoff.locator` und `write_change.locator` gesetzt, aber verschieden — stille Drift zwischen Handoff-Erwartung und tatsächlichem Locator. |

**Audit-Oberflaeche Cross-Contract**

| Kategorie | Audit |
| --------- | ----- |
| Handoff-Schema-Validierung | `covered: true; test_ref: tests/fixtures/cross_contract/invalid/contract_invalid.json` |
| Target-Drift (Handoff → Chain, fehlende Datei) | `covered: true; test_ref: tests/fixtures/cross_contract/invalid/target_drift.json` |
| Target-Drift (Chain → Handoff, extra Datei) | `covered: true; test_ref: tests/fixtures/cross_contract/invalid/target_drift_extra.json` |
| State-Drift (exact_before/exact_after weggelassen) | `covered: true; test_ref: tests/fixtures/cross_contract/invalid/state_drift.json` |
| Intent-Mismatch (kein write_change fuer Handoff-change_type) | `covered: true; test_ref: tests/fixtures/cross_contract/invalid/semantic_mismatch.json` |
| Semantischer Widerspruch im Cross-Contract-Kontext | `covered: true; test_ref: tests/fixtures/cross_contract/invalid/contradiction.json` |
| Version-Konflikt im Cross-Contract-Kontext | `covered: true; test_ref: tests/fixtures/cross_contract/invalid/version_conflict.json` |
| Handoff-Locator-Drift (locator abweichend) | `covered: true; test_ref: tests/fixtures/cross_contract/invalid/handoff_locator_drift/locator_drift.json` |

---

## 4. Äquivalenzklassen

### 4.1 Structural Validity

Betrifft: Schema-Konformität eines einzelnen Records.

| Klasse | Beschreibung | Vertreter |
| ------ | ------------ | --------- |
| SV-OK | Record ist schema-konform (alle Pflichtfelder, korrekter Typ, gültige Enum-Werte). | `read_context/valid-minimal.json`, `write_change/valid-minimal.json`, `validate_change/valid-success.json` |
| SV-MISS-FIELD | Pflichtfeld fehlt (`version`, `change_type`, etc.). | `read_context/contract-invalid-missing-version.json`, `write_change/contract-invalid-missing-change-type.json` |
| SV-WRONG-VALUE | Feld mit ungültigem Wert (falscher `const`, unbekannter Enum, falscher Typ). | `read_context/contract-invalid-wrong-version.json`, `write_change/contract-invalid-invalid-change-type.json`, `read_context/contract-invalid-wrong-command.json` |
| SV-EMPTY-REQUIRED | Pflicht-Collection leer (`target_files: []`, `checks: []`). | `read_context/contract-invalid-empty-target-files.json`, `validate_change/contract-invalid-empty-checks.json` |
| SV-CONSTRAINT | Inhaltliche Schema-Constraint verletzt (`uniqueItems`, `minLength`, `anyOf`). | `validate_change/contract-invalid-duplicate-checks.json`, `read_context/contract-invalid-empty-fact-string.json`, `write_change/contract-invalid-missing-locator.json` |

### 4.2 Semantic Validity

Betrifft: Feld-Kombinationen, die schema-konform sind, aber semantisch
widersprüchlich (record-intern, durch `if/then` oder Chain-Check erkennbar).

| Klasse | Beschreibung | Vertreter |
| ------ | ------------ | --------- |
| SEM-OK | Record ist strukturell und semantisch konsistent. | `validate_change/valid-success.json`, `validate_change/valid-failure.json` |
| SEM-SUCCESS-ERRORS | `success: true` + nicht-leeres `errors`. | `validate_change/contract-invalid-success-with-errors.json` |
| SEM-FAILURE-EMPTY | `success: false` + leeres `errors`. | `validate_change/contract-invalid-failure-empty-errors.json` |
| SEM-REMOVE-AFTER | `change_type: remove` + `exact_after` gesetzt. | `command_chains/invalid-remove-with-exact-after.json`, `cross_contract/invalid/contradiction.json` |
| SEM-EMPTY-ASSERTED | `exact_*` auf der vom `change_type` geforderten Seite ist gesetzt, aber leer (`""`). | `command_chains/invalid-empty-asserted-state.json` (add, Chain-Direktbeweis); `command_chains/invalid-empty-asserted-state-remove.json` (remove); `command_chains/invalid-empty-asserted-state-modify.json` (modify); `cross_contract/invalid/empty_change_state.json` (negativ); `cross_contract/valid/minimal_chain_add.json` (positiver Kontrast) |

### 4.3 Cross-Step Continuity

Betrifft: Konsistenz zwischen Records innerhalb einer Chain.

| Klasse | Beschreibung | Vertreter |
| ------ | ------------ | --------- |
| CC-OK | `write_change.target_files ⊆ read_context.target_files`. | `command_chains/valid-minimal.json` |
| CC-TARGET-MISMATCH | `write_change.target_files` enthält Dateien außerhalb von `read_context.target_files`. | `command_chains/invalid-target-files-mismatch.json` |
| CC-SEQ-INVALID | Reihenfolge der Commands gebrochen. | `command_chains/invalid-wrong-order.json`, `cross_contract/invalid/semantic_mismatch.json` |

### 4.4 Version Consistency

Betrifft: Einheitlichkeit der `version`-Felder in einer Kette.

Diese Fälle sind zusätzlich durch `scripts/docmeta/test_command_version_policy.py` als explizite Policy-Schicht regressionsgesichert.

| Klasse | Beschreibung | Vertreter |
| ------ | ------------ | --------- |
| VER-OK | Alle Records mit identischer `version`. | `command_chains/valid-minimal.json` |
| VER-MIXED | Unterschiedliche `version`-Werte in einer Chain. | `command_chains/invalid-mixed-versions.json`, `cross_contract/invalid/version_conflict.json` |

### 4.5 Cross-Contract Continuity

Betrifft: Bindung Handoff → Chain.

| Klasse | Beschreibung | Vertreter |
| ------ | ------------ | --------- |
| XC-OK | Handoff vollständig durch Chain erfüllt. | `cross_contract/valid/minimal_chain.json` |
| XC-CONTRACT-INVALID | Handoff selbst schema-ungültig. | `cross_contract/invalid/contract_invalid.json` |
| XC-TARGET-DRIFT | `target_files` zwischen Handoff und Chain inkonsistent. | `cross_contract/invalid/target_drift.json`, `cross_contract/invalid/target_drift_extra.json` |
| XC-STATE-DRIFT | `exact_before/exact_after` im Handoff, aber im `write_change` weggelassen. | `cross_contract/invalid/state_drift.json` |
| XC-INTENT-MISMATCH | `handoff.change_type` durch Chain nicht erfüllt. | `cross_contract/invalid/semantic_mismatch.json` |

### 4.6 Error-Check-Bindung (`validate_error_unbindable`)

Betrifft: Kohärenz zwischen `errors[]` und `checks[]` innerhalb eines `validate_change`-Records.
Prüfebene: intra-record (kein Cross-Command-Check).

| Klasse | Beschreibung | Vertreter |
| ------ | ------------ | --------- |
| ERR-BIND-OK | Alle `errors[]`-Einträge tragen ein gültiges `<check>:`-Präfix aus `checks[]`. | `command_chains/valid-errors-with-check-prefix.json` |
| ERR-BIND-NO-PREFIX | `errors[]`-Eintrag ohne jedes `<check>:`-Präfix (Freitext). | `command_chains/invalid-error-no-check-prefix.json` |
| ERR-BIND-UNKNOWN-PREFIX | Präfix vorhanden, aber nicht in `checks[]` (unbekannter Check). | `command_chains/invalid-error-unknown-check-prefix.json` |
| ERR-BIND-PARTIAL | Ein gebundener + ein ungebundener Eintrag — partiell; ungebundener Eintrag löst Fehler aus. | `command_chains/invalid-error-partial-binding.json` |

### 4.7 Validate→Result Seam (v0.1 minimal)

Betrifft: Plausibilitätsbindung zwischen `validate_change` und dem vorangehenden `write_change`.
Prüfebene: cross-record. Keine neue Result-Semantik; keine v0.2-Vorwegnahme.

| Klasse | Beschreibung | Vertreter |
| ------ | ------------ | --------- |
| VR-OK | `validate_change` folgt auf `write_change` mit nicht-leerem `target_files`. | `command_chains/valid-validate-with-write.json` |
| VR-NO-WRITE | `validate_change` ohne vorangehendes `write_change` in der Chain. | `command_chains/invalid-validate-without-write.json` |
| VR-EMPTY-TARGET | `write_change.target_files` leer (`[]`) — kein Datei-Scope für Validierung. | `command_chains/invalid-validate-empty-targets.json` |
| VR-ORPHAN | `write_change` ohne `target_files`-Schlüssel — `validate_change` hat keinen plausiblen Scope. | `command_chains/invalid-validate-orphaned.json` |

---

## 5. Known Gaps

Diese Sektion dokumentiert ausschließlich belegbare Lücken — keine Spekulation.
Offene Gaps erscheinen ausschließlich als einzelne Unterabschnitte mit eigener
Audit-Oberfläche. Geschlossene Punkte werden hier nicht separat fortgeführt.

### 5.1 Validate/Result Seam — Schritt-übergreifende Traceability

Die minimale Plausibilitätsprüfung zwischen `validate_change` und `write_change` ist implementiert. Die Cross-Record-Checks `validate_without_write` und `validate_targets_out_of_scope` schließen die Naht auf struktureller Ebene. Jedoch: Schritt-übergreifende Traceability (welcher Fehler stammt von welchem Schritt) erfordert strukturierte `errors[]`-Objekte, ein Breaking Change für v0.2.

**Audit:**
- `covered: true`
- `test_ref: tests/fixtures/command_chains/valid-validate-with-write.json, tests/fixtures/command_chains/invalid-validate-without-write.json, tests/fixtures/command_chains/invalid-validate-empty-targets.json, tests/fixtures/command_chains/invalid-validate-orphaned.json`
- `gap: intentional (v0.2)`

### 5.2 `locator` ↔ `extracted_facts`

Der Error-Code `locator_continuity_violation` prüft in v0.1 nur leeren/whitespace-Locator. Eine inhaltliche Kopplung zwischen Locator und Facts ist nicht maschinell erzwungen.

**Audit:**
- `covered: false`
- `test_ref: —`
- `gap: intentional (v0.2)`

### 5.3 Strukturiertes `errors[]`

Alle `errors[]`-Einträge in Fixtures sind Freitext-Strings (z.B. `"lint: E501 line too long"`). Strukturierte Fehler (`{check, code, message}`) bleiben v0.2-Scope.

**Audit:**
- `covered: false`
- `test_ref: —`
- `gap: intentional (v0.2)`

---

## 6. Mapping-Tabelle

| Layer | Case | Fixture | Expected Errors | Covered |
| ----- | ---- | ------- | --------------- | ------- |
| Command | read_context valid minimal | `agent_commands/read_context/valid-minimal.json` | — | ✅ |
| Command | read_context valid complex | `agent_commands/read_context/valid-edge-complex.json` | — | ✅ |
| Command | read_context empty target_files | `agent_commands/read_context/contract-invalid-empty-target-files.json` | `contract_invalid` | ✅ |
| Command | read_context missing version | `agent_commands/read_context/contract-invalid-missing-version.json` | `contract_invalid` | ✅ |
| Command | read_context wrong version | `agent_commands/read_context/contract-invalid-wrong-version.json` | `contract_invalid` | ✅ |
| Command | read_context wrong command | `agent_commands/read_context/contract-invalid-wrong-command.json` | `contract_invalid` | ✅ |
| Command | read_context empty fact string | `agent_commands/read_context/contract-invalid-empty-fact-string.json` | `contract_invalid` | ✅ |
| Command | write_change valid minimal | `agent_commands/write_change/valid-minimal.json` | — | ✅ |
| Command | write_change valid add+target_lines | `agent_commands/write_change/valid-edge-add-with-target-lines.json` | — | ✅ |
| Command | write_change valid remove | `agent_commands/write_change/valid-edge-remove.json` | — | ✅ |
| Command | write_change empty target_files | `agent_commands/write_change/contract-invalid-empty-target-files.json` | `contract_invalid` | ✅ |
| Command | write_change wrong version | `agent_commands/write_change/contract-invalid-wrong-version.json` | `contract_invalid` | ✅ |
| Command | write_change wrong command | `agent_commands/write_change/contract-invalid-wrong-command.json` | `contract_invalid` | ✅ |
| Command | write_change missing change_type | `agent_commands/write_change/contract-invalid-missing-change-type.json` | `contract_invalid` | ✅ |
| Command | write_change invalid change_type | `agent_commands/write_change/contract-invalid-invalid-change-type.json` | `contract_invalid` | ✅ |
| Command | write_change missing locator+target_lines | `agent_commands/write_change/contract-invalid-missing-locator.json` | `contract_invalid` | ✅ |
| Command | validate_change valid success | `agent_commands/validate_change/valid-success.json` | — | ✅ |
| Command | validate_change valid failure | `agent_commands/validate_change/valid-failure.json` | — | ✅ |
| Command | validate_change valid multi-checks | `agent_commands/validate_change/valid-edge-multi-checks.json` | — | ✅ |
| Command | validate_change wrong command | `agent_commands/validate_change/contract-invalid-wrong-command.json` | `contract_invalid` | ✅ |
| Command | validate_change empty checks | `agent_commands/validate_change/contract-invalid-empty-checks.json` | `contract_invalid` | ✅ |
| Command | validate_change duplicate checks | `agent_commands/validate_change/contract-invalid-duplicate-checks.json` | `contract_invalid` | ✅ |
| Command | validate_change success+errors | `agent_commands/validate_change/contract-invalid-success-with-errors.json` | `contract_invalid` | ✅ |
| Command | validate_change failure+empty errors | `agent_commands/validate_change/contract-invalid-failure-empty-errors.json` | `contract_invalid` | ✅ |
| Chain | correct order | `command_chains/valid-minimal.json` | — | ✅ |
| Chain | wrong order | `command_chains/invalid-wrong-order.json` | `command_sequence_invalid` | ✅ |
| Chain | target files mismatch | `command_chains/invalid-target-files-mismatch.json` | `target_files_mismatch` | ✅ |
| Chain | remove+exact_after contradiction | `command_chains/invalid-remove-with-exact-after.json` | `semantic_contradiction` | ✅ |
| Chain | empty asserted state (add+`exact_after=""`) — SEM-EMPTY-ASSERTED | `command_chains/invalid-empty-asserted-state.json` | `semantic_contradiction` | ✅ |
| Chain | empty asserted state (remove+`exact_before=""`) — SEM-EMPTY-ASSERTED | `command_chains/invalid-empty-asserted-state-remove.json` | `semantic_contradiction` | ✅ |
| Chain | empty asserted state (modify+`exact_before=""`) — SEM-EMPTY-ASSERTED | `command_chains/invalid-empty-asserted-state-modify.json` | `semantic_contradiction` | ✅ |
| Chain | mixed versions | `command_chains/invalid-mixed-versions.json` | `command_sequence_invalid`, `contract_invalid` | ✅ |
| Chain | empty/whitespace locator | `command_chains/invalid-empty-locator.json` | `locator_continuity_violation` | ✅ |
| Chain | add+exact_before contradiction | `command_chains/invalid-add-with-exact-before.json` | `semantic_contradiction` | ✅ |
| Chain | errors[] korrekt gebunden (check-Präfix) | `command_chains/valid-errors-with-check-prefix.json` | — | ✅ |
| Chain | errors[] kein Präfix | `command_chains/invalid-error-no-check-prefix.json` | `validate_error_unbindable` | ✅ |
| Chain | errors[] unbekanntes Präfix | `command_chains/invalid-error-unknown-check-prefix.json` | `validate_error_unbindable` | ✅ |
| Chain | errors[] partiell gebunden | `command_chains/invalid-error-partial-binding.json` | `validate_error_unbindable` | ✅ |
| Chain | validate ohne write_change | `command_chains/invalid-validate-without-write.json` | `command_sequence_invalid`, `validate_without_write` | ✅ |
| Chain | validate mit leerem target_files | `command_chains/invalid-validate-empty-targets.json` | `contract_invalid`, `validate_targets_out_of_scope` | ✅ |
| Chain | validate orphaned (kein target_files-Schlüssel) | `command_chains/invalid-validate-orphaned.json` | `contract_invalid`, `validate_targets_out_of_scope` | ✅ |
| Cross-Contract | valid full chain | `cross_contract/valid/minimal_chain.json` | — | ✅ |
| Cross-Contract | handoff schema invalid | `cross_contract/invalid/contract_invalid.json` | `handoff_contract_invalid` | ✅ |
| Cross-Contract | target drift (handoff file missing in chain) | `cross_contract/invalid/target_drift.json` | `handoff_target_drift` | ✅ |
| Cross-Contract | target drift (extra file in chain) | `cross_contract/invalid/target_drift_extra.json` | `handoff_target_drift` | ✅ |
| Cross-Contract | state drift (exact_before/after omitted) | `cross_contract/invalid/state_drift.json` | `handoff_state_drift` | ✅ |
| Cross-Contract | semantic contradiction (remove+exact_after) | `cross_contract/invalid/contradiction.json` | `semantic_contradiction` | ✅ |
| Cross-Contract | empty asserted state (add+`exact_after=""`) | `cross_contract/invalid/empty_change_state.json` | `semantic_contradiction` | ✅ |
| Cross-Contract | empty asserted state — positive contrast (add with non-empty `exact_after`) | `cross_contract/valid/minimal_chain_add.json` | — | ✅ |
| Cross-Contract | intent mismatch (no write_change) | `cross_contract/invalid/semantic_mismatch.json` | `command_sequence_invalid`, `handoff_intent_mismatch`, `validate_without_write` | ✅ |
| Cross-Contract | version conflict | `cross_contract/invalid/version_conflict.json` | `command_sequence_invalid`, `contract_invalid` | ✅ |
| Cross-Contract | locator drift (handoff vs write_change) | `cross_contract/invalid/handoff_locator_drift/locator_drift.json` | `handoff_locator_drift` | ✅ |
