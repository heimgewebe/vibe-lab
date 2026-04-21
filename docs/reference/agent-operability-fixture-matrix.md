---
title: "Agent Operability — Fixture-Matrix (v0.1)"
status: active
canonicality: reference
created: "2026-04-21"
updated: "2026-04-21"
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

Dieses Dokument ist ein kanonisches Referenzartefakt. Es kartiert alle
vorhandenen Fixtures in explizite Äquivalenzklassen und macht Coverage und
Lücken sichtbar. Es enthält **keine neue Validierungslogik**, keine neuen
Fixtures und keine Schema-Änderungen.

Quellen:
- `tests/fixtures/agent_commands/**`
- `tests/fixtures/command_chains/**`
- `tests/fixtures/cross_contract/**`
- `contracts/command-semantics.md`

---

## 1. Command-Level Coverage

### 1.1 `read_context`

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

**Ungültige Fixtures**

| Fixture | Sidecar | Erwartete Fehler | Was getestet wird |
| ------- | ------- | ---------------- | ----------------- |
| `tests/fixtures/command_chains/invalid-wrong-order.json` | `invalid-wrong-order.expected.json` | `command_sequence_invalid` | `write_change` vor `read_context` — gebrochene Reihenfolge. |
| `tests/fixtures/command_chains/invalid-target-files-mismatch.json` | `invalid-target-files-mismatch.expected.json` | `target_files_mismatch` | `write_change.target_files` enthält `README.md`, das nicht in `read_context.target_files` steht. |
| `tests/fixtures/command_chains/invalid-remove-with-exact-after.json` | `invalid-remove-with-exact-after.expected.json` | `semantic_contradiction` | `change_type: remove` mit gesetztem `exact_after` — semantisch widersprüchlich. |
| `tests/fixtures/command_chains/invalid-mixed-versions.json` | `invalid-mixed-versions.expected.json` | `command_sequence_invalid`, `contract_invalid` | `write_change.version: "v0.2"` in ansonsten v0.1-Kette — gemischte Versionen. |

**Abgedeckte Chain-Prüfkategorien**

| Kategorie | Abgedeckt | Fixture |
| --------- | --------- | ------- |
| Korrekte Reihenfolge | ✅ | `valid-minimal.json` |
| Gebrochene Reihenfolge | ✅ | `invalid-wrong-order.json` |
| Target-Kontinuität (Datei-Ebene) | ✅ | `invalid-target-files-mismatch.json` |
| Semantischer Widerspruch (Record-intern) | ✅ | `invalid-remove-with-exact-after.json` |
| Versionskonsistenz | ✅ | `invalid-mixed-versions.json` |
| Locator-Kontinuität (leerer Locator) | ❌ | Kein dediziertes Chain-Fixture (nur via Cross-Contract `state_drift`) |

---

## 3. Cross-Contract Coverage

Alle Cross-Contract-Fixtures liegen unter `tests/fixtures/cross_contract/`
und binden ein `handoff`-Objekt an eine `chain`. Abgedeckt werden die
Invarianten aus `contracts/command-semantics.md §Cross-Contract`.

**Gültige Fixtures**

| Fixture | Was getestet wird |
| ------- | ----------------- |
| `tests/fixtures/cross_contract/valid/minimal_chain.json` | Handoff (PASS, mit `exact_before/exact_after`) vollständig durch Chain erfüllt. `target_files`, `change_type`, `exact_before/exact_after` übereinstimmend. |

**Ungültige Fixtures**

| Fixture | Erwartete Fehler | Fehlerklasse | Was getestet wird |
| ------- | ---------------- | ------------ | ----------------- |
| `tests/fixtures/cross_contract/invalid/contract_invalid.json` | `handoff_contract_invalid` | Handoff-Schema-Verletzung | Handoff ohne `status`-Feld — verletzt `agent.handoff.schema.json`. Cross-Contract-Checks werden abgebrochen. |
| `tests/fixtures/cross_contract/invalid/target_drift.json` | `handoff_target_drift` | Target-Drift | `handoff.target_files: ["docs/foundations/vision.md"]`, Chain verwendet `docs/index.md` — Dateien stimmen nicht überein. |
| `tests/fixtures/cross_contract/invalid/target_drift_extra.json` | `handoff_target_drift` | Target-Drift (umgekehrt) | Handoff hat ein File, Chain hat zwei — Chain enthält Dateien außerhalb des Handoff-Scopes. |
| `tests/fixtures/cross_contract/invalid/state_drift.json` | `handoff_state_drift` | State-Drift | Handoff setzt `exact_before/exact_after`, `write_change` lässt beide weg — stille Divergenz. |
| `tests/fixtures/cross_contract/invalid/contradiction.json` | `semantic_contradiction` | Semantischer Widerspruch | `change_type: remove` mit `exact_after` im `write_change` — Record-interne Verletzung innerhalb eines Cross-Contract-Tests. |
| `tests/fixtures/cross_contract/invalid/semantic_mismatch.json` | `command_sequence_invalid`, `handoff_intent_mismatch` | Handoff-Intent + Sequenz | Handoff verlangt `modify`, Chain enthält kein `write_change` (nur `read_context → validate_change`) — Intent nicht erfüllt, Reihenfolge gebrochen. |
| `tests/fixtures/cross_contract/invalid/version_conflict.json` | `command_sequence_invalid`, `contract_invalid` | Versions- + Contract-Verletzung | `write_change.version: "v0.2"` in Cross-Contract-Kontext — gleiche Prüfung wie im reinen Chain-Fall, aber eingebettet in Handoff-Szenario. |

**Abgedeckte Cross-Contract-Prüfkategorien**

| Kategorie | Error-Code | Abgedeckt | Fixture |
| --------- | ---------- | --------- | ------- |
| Handoff-Schema-Validierung | `handoff_contract_invalid` | ✅ | `contract_invalid.json` |
| Target-Drift (Handoff → Chain, fehlende Datei) | `handoff_target_drift` | ✅ | `target_drift.json` |
| Target-Drift (Chain → Handoff, extra Datei) | `handoff_target_drift` | ✅ | `target_drift_extra.json` |
| State-Drift (exact_before/exact_after weggelassen) | `handoff_state_drift` | ✅ | `state_drift.json` |
| Intent-Mismatch (kein write_change für Handoff-change_type) | `handoff_intent_mismatch` | ✅ | `semantic_mismatch.json` |
| Semantischer Widerspruch im Cross-Contract-Kontext | `semantic_contradiction` | ✅ | `contradiction.json` |
| Version-Konflikt im Cross-Contract-Kontext | `command_sequence_invalid` | ✅ | `version_conflict.json` |
| Handoff-Locator-Drift (locator abweichend) | `handoff_locator_drift` | ❌ | Kein Fixture — für v0.2 vorgemerkt |

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

### 4.3 Cross-Step Continuity

Betrifft: Konsistenz zwischen Records innerhalb einer Chain.

| Klasse | Beschreibung | Vertreter |
| ------ | ------------ | --------- |
| CC-OK | `write_change.target_files ⊆ read_context.target_files`. | `command_chains/valid-minimal.json` |
| CC-TARGET-MISMATCH | `write_change.target_files` enthält Dateien außerhalb von `read_context.target_files`. | `command_chains/invalid-target-files-mismatch.json` |
| CC-SEQ-INVALID | Reihenfolge der Commands gebrochen. | `command_chains/invalid-wrong-order.json`, `cross_contract/invalid/semantic_mismatch.json` |

### 4.4 Version Consistency

Betrifft: Einheitlichkeit der `version`-Felder in einer Kette.

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

---

## 5. Known Gaps

Diese Sektion dokumentiert ausschließlich belegbare Lücken — keine
Spekulation.

### 5.1 Validate/Result Seam: MISSING

`validate_change` enthält kein Feld, das das Ergebnis an einen `write_change`-
Kontext zurückbindet. Die Verbindung "dieser validate_change-Record gehört zu
diesem write_change-Record" existiert nicht als maschinell prüfbarer Seam.

**Quelle:** `contracts/command-semantics.md` — Abschnitt "Evolution Constraints (v0.1 → v0.2)" unter `validate_change`
— `errors[]` bleibt in v0.1 ein String-Array ohne Referenz auf konkrete Checks
oder `write_change`-Steps.

**Auswirkung:** Ein Chain-Validator kann nicht prüfen, ob `errors[]`-Einträge
in `validate_change` auf Checks in `checks[]` referenzieren.

**Fixture-Lücke:** Kein Fixture testet einen `validate_change`-Fehler mit
Bezug auf einen spezifischen `write_change`-Schritt.

### 5.2 `locator` ↔ `extracted_facts`: NOT IMPLEMENTED

Die inhaltliche Kopplung zwischen `write_change.locator` und
`read_context.extracted_facts` ist in v0.1 nicht maschinell erzwungen.

**Quelle:** `contracts/command-semantics.md` — Abschnitt "Error-Klassen (strukturiertes Modell)", Eintrag `locator_continuity_violation`
— explizit als v0.2-Scope markiert. Der Error-Code `locator_continuity_violation`
prüft in v0.1 nur leeren/whitespace-Locator, nicht die Kopplung an Facts.

**Fixture-Lücke:** Kein Fixture testet einen nicht-leeren, aber in
`extracted_facts` nicht referenzierten Locator.

### 5.3 Strukturiertes `errors[]`: NOT IMPLEMENTED

`validate_change.errors[]` ist in v0.1 ein String-Array. Es gibt keine
Struktur (`{check, code, message}`), die eine maschinelle Auswertung
ermöglicht.

**Quelle:** `contracts/command-semantics.md` — Abschnitt "Evolution Constraints (v0.1 → v0.2)" unter `validate_change`
— Breaking Change explizit auf v0.2 verschoben.

**Fixture-Lücke:** Alle `errors[]`-Einträge in Fixtures sind Freitext-Strings
(z. B. `"lint: E501 line too long"`). Kein Fixture definiert strukturierte
Fehler.

### 5.4 Handoff-Locator-Drift: KEIN FIXTURE

Die Prüfung `handoff.locator ↔ write_change.locator` ist in der
Invariantenliste von `contracts/command-semantics.md` — Abschnitt "Evolution
Constraints (v0.1 → v0.2)" unter "Cross-Contract" — explizit als
v0.2-Evolution benannt (`handoff_locator_drift`). Der Error-Code existiert
noch nicht im Validator.

**Fixture-Lücke:** Kein Cross-Contract-Fixture testet einen abweichenden
Locator zwischen Handoff und `write_change`.

### 5.5 Dediziertes Chain-Fixture für leeren Locator: FEHLT

`locator_continuity_violation` (leerer/whitespace Locator) ist als Chain-
Error-Code definiert, aber es existiert kein dediziertes `command_chains/`-
Fixture, das diesen Code isoliert auslöst. Die einzige Abdeckung erfolgt
indirekt über `cross_contract/invalid/state_drift.json`.

### 5.6 `add` mit `exact_before`: KEIN CHAIN-FIXTURE

Die Anti-Invariante "change_type: add mit gesetztem exact_before" ist in
`contracts/command-semantics.md` — Abschnitt "Anti-Invariants" unter "Command: write_change" — als ⚙️ Chain-Check
definiert, aber kein `command_chains/`-Fixture testet diesen Fall.

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
| Chain | mixed versions | `command_chains/invalid-mixed-versions.json` | `command_sequence_invalid`, `contract_invalid` | ✅ |
| Chain | empty locator (isolated) | — | `locator_continuity_violation` | ❌ MISSING |
| Chain | add+exact_before contradiction | — | `semantic_contradiction` | ❌ MISSING |
| Cross-Contract | valid full chain | `cross_contract/valid/minimal_chain.json` | — | ✅ |
| Cross-Contract | handoff schema invalid | `cross_contract/invalid/contract_invalid.json` | `handoff_contract_invalid` | ✅ |
| Cross-Contract | target drift (handoff file missing in chain) | `cross_contract/invalid/target_drift.json` | `handoff_target_drift` | ✅ |
| Cross-Contract | target drift (extra file in chain) | `cross_contract/invalid/target_drift_extra.json` | `handoff_target_drift` | ✅ |
| Cross-Contract | state drift (exact_before/after omitted) | `cross_contract/invalid/state_drift.json` | `handoff_state_drift` | ✅ |
| Cross-Contract | semantic contradiction (remove+exact_after) | `cross_contract/invalid/contradiction.json` | `semantic_contradiction` | ✅ |
| Cross-Contract | intent mismatch (no write_change) | `cross_contract/invalid/semantic_mismatch.json` | `command_sequence_invalid`, `handoff_intent_mismatch` | ✅ |
| Cross-Contract | version conflict | `cross_contract/invalid/version_conflict.json` | `command_sequence_invalid`, `contract_invalid` | ✅ |
| Cross-Contract | locator drift (handoff vs write_change) | — | `handoff_locator_drift` | ❌ MISSING (v0.2) |
