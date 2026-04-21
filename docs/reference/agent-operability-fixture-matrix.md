# Agent Operability Fixture Matrix

## 1. Überblick

Diese Matrix macht die vorhandene Fixture-/Validator-Abdeckung explizit sichtbar.

Als **Äquivalenzklasse** gilt hier ausschließlich eine im Repository belegte Klasse über:
- vorhandene Fixture-Familien/-Namen,
- vorhandene Validator-Fehlercodes,
- vorhandene erwartete Outcomes.

Keine neuen Validatoren, keine neuen Contracts, keine neue Semantik.

## 2. Command-Level Coverage

### `read_context`

| Klasse | Fixture(s) | Validator | Error-Code | Status |
|---|---|---|---|---|
| valid-minimal | `tests/fixtures/agent_commands/read_context/valid-minimal.json` | `scripts/docmeta/validate_agent_commands.py` | none | covered |
| valid-edge-complex | `tests/fixtures/agent_commands/read_context/valid-edge-complex.json` | `scripts/docmeta/validate_agent_commands.py` | none | covered |
| contract_invalid-empty-target-files | `tests/fixtures/agent_commands/read_context/contract-invalid-empty-target-files.json` | `scripts/docmeta/validate_agent_commands.py` | `contract_invalid` | covered |
| contract_invalid-wrong-version | `tests/fixtures/agent_commands/read_context/contract-invalid-wrong-version.json` | `scripts/docmeta/validate_agent_commands.py` | `contract_invalid` | covered |
| contract_invalid-wrong-command | `tests/fixtures/agent_commands/read_context/contract-invalid-wrong-command.json` | `scripts/docmeta/validate_agent_commands.py` | `contract_invalid` | covered |
| contract_invalid-empty-fact-string | `tests/fixtures/agent_commands/read_context/contract-invalid-empty-fact-string.json` | `scripts/docmeta/validate_agent_commands.py` | `contract_invalid` | covered |
| contract_invalid-missing-version | `tests/fixtures/agent_commands/read_context/contract-invalid-missing-version.json` | `scripts/docmeta/validate_agent_commands.py` | `contract_invalid` | covered |

### `write_change`

| Klasse | Fixture(s) | Validator | Error-Code | Status |
|---|---|---|---|---|
| valid-minimal | `tests/fixtures/agent_commands/write_change/valid-minimal.json` | `scripts/docmeta/validate_agent_commands.py` | none | covered |
| valid-edge-add-with-target-lines | `tests/fixtures/agent_commands/write_change/valid-edge-add-with-target-lines.json` | `scripts/docmeta/validate_agent_commands.py` | none | covered |
| valid-edge-remove | `tests/fixtures/agent_commands/write_change/valid-edge-remove.json` | `scripts/docmeta/validate_agent_commands.py` | none | covered |
| contract_invalid-empty-target-files | `tests/fixtures/agent_commands/write_change/contract-invalid-empty-target-files.json` | `scripts/docmeta/validate_agent_commands.py` | `contract_invalid` | covered |
| contract_invalid-wrong-version | `tests/fixtures/agent_commands/write_change/contract-invalid-wrong-version.json` | `scripts/docmeta/validate_agent_commands.py` | `contract_invalid` | covered |
| contract_invalid-missing-change-type | `tests/fixtures/agent_commands/write_change/contract-invalid-missing-change-type.json` | `scripts/docmeta/validate_agent_commands.py` | `contract_invalid` | covered |
| contract_invalid-invalid-change-type | `tests/fixtures/agent_commands/write_change/contract-invalid-invalid-change-type.json` | `scripts/docmeta/validate_agent_commands.py` | `contract_invalid` | covered |
| contract_invalid-wrong-command | `tests/fixtures/agent_commands/write_change/contract-invalid-wrong-command.json` | `scripts/docmeta/validate_agent_commands.py` | `contract_invalid` | covered |
| contract_invalid-missing-locator | `tests/fixtures/agent_commands/write_change/contract-invalid-missing-locator.json` | `scripts/docmeta/validate_agent_commands.py` | `contract_invalid` | covered |

### `validate_change`

| Klasse | Fixture(s) | Validator | Error-Code | Status |
|---|---|---|---|---|
| valid-success | `tests/fixtures/agent_commands/validate_change/valid-success.json` | `scripts/docmeta/validate_agent_commands.py` | none | covered |
| valid-failure | `tests/fixtures/agent_commands/validate_change/valid-failure.json` | `scripts/docmeta/validate_agent_commands.py` | none | covered |
| valid-edge-multi-checks | `tests/fixtures/agent_commands/validate_change/valid-edge-multi-checks.json` | `scripts/docmeta/validate_agent_commands.py` | none | covered |
| contract_invalid-success-with-errors | `tests/fixtures/agent_commands/validate_change/contract-invalid-success-with-errors.json` | `scripts/docmeta/validate_agent_commands.py` | `contract_invalid` | covered |
| contract_invalid-failure-empty-errors | `tests/fixtures/agent_commands/validate_change/contract-invalid-failure-empty-errors.json` | `scripts/docmeta/validate_agent_commands.py` | `contract_invalid` | covered |
| contract_invalid-empty-checks | `tests/fixtures/agent_commands/validate_change/contract-invalid-empty-checks.json` | `scripts/docmeta/validate_agent_commands.py` | `contract_invalid` | covered |
| contract_invalid-duplicate-checks | `tests/fixtures/agent_commands/validate_change/contract-invalid-duplicate-checks.json` | `scripts/docmeta/validate_agent_commands.py` | `contract_invalid` | covered |
| contract_invalid-wrong-command | `tests/fixtures/agent_commands/validate_change/contract-invalid-wrong-command.json` | `scripts/docmeta/validate_agent_commands.py` | `contract_invalid` | covered |

## 3. Chain-Level Coverage

| Klasse | Fixture(s) | Validator | Error-Code | Status |
|---|---|---|---|---|
| sequence_valid | `tests/fixtures/command_chains/valid-minimal.json` | `scripts/docmeta/validate_command_chain.py` | none | covered |
| sequence_invalid | `tests/fixtures/command_chains/invalid-wrong-order.json`, `tests/fixtures/command_chains/invalid-wrong-order.expected.json` | `scripts/docmeta/validate_command_chain.py` | `command_sequence_invalid` | covered |
| version_mismatch | `tests/fixtures/command_chains/invalid-mixed-versions.json`, `tests/fixtures/command_chains/invalid-mixed-versions.expected.json` | `scripts/docmeta/validate_command_chain.py` | `command_sequence_invalid`, `contract_invalid` | covered |
| target_continuity | `tests/fixtures/command_chains/invalid-target-files-mismatch.json`, `tests/fixtures/command_chains/invalid-target-files-mismatch.expected.json` | `scripts/docmeta/validate_command_chain.py` | `target_files_mismatch` | covered |
| semantic_contradiction | `tests/fixtures/command_chains/invalid-remove-with-exact-after.json`, `tests/fixtures/command_chains/invalid-remove-with-exact-after.expected.json` | `scripts/docmeta/validate_command_chain.py` | `semantic_contradiction` | covered |
| locator_continuity_violation | keine dedizierte Datei in `tests/fixtures/command_chains/` | `scripts/docmeta/validate_command_chain.py` | `locator_continuity_violation` | missing |
| extracted_facts↔locator coupling | in `contracts/command-semantics.md` explizit für v0.2 dokumentiert, in v0.1 nicht operationalisiert | `scripts/docmeta/validate_command_chain.py` | `locator_continuity_violation` (v0.1 eingeschränkt) | intentionally_deferred_v0.2 |

## 4. Cross-Contract Coverage

### Handoff → Commands

| Klasse | Fixture(s) | Error-Code | Status |
|---|---|---|---|
| handoff_pass | `tests/fixtures/agent_handoff/pass-minimal.json` | none | unclear |
| handoff_contract_invalid | `tests/fixtures/agent_handoff/contract-invalid-missing-handoff.json`, `tests/fixtures/agent_handoff/partial-missing-required-fixes.json` | `contract_invalid` | covered |
| handoff_hash_mismatch | `tests/fixtures/agent_handoff/hash-mismatch.json` | `hash_mismatch` | covered |
| handoff_to_command_chain seam fixture | keine Fixture mit kombiniertem Handoff+Command-Chain Payload im Scope | unknown | missing |

### Commands → Validate/Result

| Klasse | Fixture(s) | Error-Code | Status |
|---|---|---|---|
| command_chain_with_validate_change | `tests/fixtures/command_chains/valid-minimal.json` und `invalid-*.json` | chain codes (`command_sequence_invalid`, `target_files_mismatch`, `semantic_contradiction`, `contract_invalid`) | covered |
| phase1c_valid | `tests/fixtures/experiment_structure_phase1c/valid/manifest.yml`, `tests/fixtures/experiment_structure_phase1c/valid/INITIAL.md`, `tests/fixtures/experiment_structure_phase1c/valid/CONTEXT.md`, `tests/fixtures/experiment_structure_phase1c/valid/results/decision.yml`, `tests/fixtures/experiment_structure_phase1c/valid/results/evidence.jsonl`, `tests/fixtures/experiment_structure_phase1c/valid/results/result.md` | verdict `VALID`, status_assessment `adopted` | covered |
| phase1c_inconsistent | `tests/fixtures/experiment_structure_phase1c/inconsistent/manifest.yml`, `tests/fixtures/experiment_structure_phase1c/inconsistent/INITIAL.md`, `tests/fixtures/experiment_structure_phase1c/inconsistent/CONTEXT.md`, `tests/fixtures/experiment_structure_phase1c/inconsistent/results/decision.yml`, `tests/fixtures/experiment_structure_phase1c/inconsistent/results/evidence.jsonl`, `tests/fixtures/experiment_structure_phase1c/inconsistent/results/result.md` | verdict `INCONSISTENT`, status_assessment `inconclusive` | covered |
| phase1c_insufficient_input | `tests/fixtures/experiment_structure_phase1c/insufficient_input/manifest.yml`, `tests/fixtures/experiment_structure_phase1c/insufficient_input/INITIAL.md`, `tests/fixtures/experiment_structure_phase1c/insufficient_input/CONTEXT.md`, `tests/fixtures/experiment_structure_phase1c/insufficient_input/results/decision.yml`, `tests/fixtures/experiment_structure_phase1c/insufficient_input/results/evidence.jsonl` | verdict `ERROR`, status_assessment `blocked` | covered |
| phase1c_expected_cases_spec | `tests/fixtures/experiment_structure_phase1c/expected-outcomes.json` | expected cases spec | covered |
| direct command→phase1c linkage fixture | keine direkte Fixture, die Command-Records und Result-Artefakte in einem gemeinsamen Prüffall verbindet | unknown | missing |

Zusatz (Scope-Sichtbarkeit): `tests/contracts/**` fehlt, nötig für explizite Contract-Test-Klassen.

## 5. Coverage-Bewertung

| Klasse | Bewertung |
|---|---|
| Command-Schema-Klassen (`agent_commands/*`) | covered |
| Chain-Klassen: `sequence_valid`, `sequence_invalid`, `version_mismatch`, `target_continuity`, `semantic_contradiction` | covered |
| Chain-Klasse: `locator_continuity_violation` (als dedizierte Fixture-Datei) | missing |
| Handoff-Klassen (`pass`, `contract_invalid`, `hash_mismatch`) | covered/unclear (siehe Seams) |
| Seam `handoff_to_command_chain` | missing |
| Seam `command_to_result` (direkte gemeinsame Fixture) | missing |
| `extracted_facts`↔`locator` inhaltliche Kopplung | intentionally_deferred_v0.2 |
| `tests/contracts/**`-basierte Klassen | missing |

## 6. Identifizierte Lücken

### Gap: Handoff → Command seam
Status: missing
Benötigt für: explizite End-to-End-Übergangsvalidierung von Handoff-Daten in Command-Ketten
Aktuelle Abdeckung: getrennte Fixture-Familien (`agent_handoff/*` vs. `command_chains/*`), keine gemeinsame Seam-Fixture

### Gap: Command → Result seam
Status: missing
Benötigt für: vollständige End-to-End-Validierung von Command-Kette bis Result-Artefakten
Aktuelle Abdeckung: Command-Chains und Phase-1c-Result-Fälle existieren separat, aber ohne direkte Verknüpfungsfixture

### Gap: locator_continuity_violation als Datei-Fixture
Status: missing
Benötigt für: explizite dateibasierte Regressionsabdeckung des Fehlercodes `locator_continuity_violation`
Aktuelle Abdeckung: Verhalten über Logik und Unit-Test mit synthetischen In-Memory-Chains, keine dedizierte Datei unter `tests/fixtures/command_chains/`

### Gap: tests/contracts Fixture-Korpus
Status: missing
Benötigt für: explizite Vertrags-Testklassen im Pfad `tests/contracts/**` (im Scope genannt)
Aktuelle Abdeckung: Pfad enthält keine Dateien

## Optional: Priorisierung fehlender Klassen

1. `handoff_to_command_chain` seam
2. `command_to_result` seam
3. `locator_continuity_violation` als dedizierte Chain-Datei
