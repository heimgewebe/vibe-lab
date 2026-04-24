# Phase 1 Fixtures Specification

> Dieses Dokument ist eine **Spezifikation**.
> Es ist nicht die operative Wahrheit der Ausführung.
> Konkrete JSON-Fixtures entstehen erst im Execution-PR und werden dort
> über `results/evidence.jsonl` belegt.

---

## Struktur

Jede Fallspezifikation enthält:
- `case_id`: Case identifier (A1, A2, B1, etc.)
- `category`: Equivalence class (locator, hash, normalization, etc.)
- `base_fixture`: Which valid fixture is being mutated
- `mutation`: Description of the change
- `expected_validator_behavior`: What should happen
- `artifact`: nur als Platzhalter beschrieben, nicht als ausgeführter Befund

---

## Äquivalenzklasse A: Locator Path Drift

### A1 (negativ): Invalid path segment

**Purpose:** Verify validator rejects structural path changes.

```yaml
case_id: A1
category: locator_drift
base_fixture: tests/fixtures/agent_handoff/pass-minimal.json
mutation:
  field: handoff_target.locator
  change: "contracts/command-semantics.md" → "contracts/command-INVALID.md"
  rationale: "Change path segment; should trigger rejection"
expected_validator_behavior: REJECTED
expected_error_type: "locator_mismatch or similar"
contrast_pair: A2
notes: "Core case: validator must catch structural path changes"
```

### A2 (Kontrast): Path with fragment

**Purpose:** Probe edge case: does validator accept path + fragment?

```yaml
case_id: A2
category: locator_drift
base_fixture: tests/fixtures/agent_handoff/pass-minimal.json
mutation:
  field: handoff_target.locator
  change: "contracts/command-semantics.md" → "contracts/command-semantics.md#L10"
  rationale: "Add fragment; unknown if validator accepts"
expected_validator_behavior: "? (probe — result will determine)"
expected_error_type: null
contrast_pair: A1
notes: "Edge case: tests validator boundary on acceptable locator variants"
```

---

## Äquivalenzklasse B: Hash Value Drift

### B1 (negativ): Hash completely changed

**Purpose:** Verify validator rejects hash mismatches.

```yaml
case_id: B1
category: hash_drift
base_fixture: tests/fixtures/agent_handoff/pass-minimal.json
mutation:
  field: hash
  change: "<original_sha1>" → "ffffffffffffffffffffffffffffffffffffffff"
  rationale: "Completely invalid hash; should always reject"
expected_validator_behavior: REJECTED
expected_error_type: "hash_mismatch or validation_error"
contrast_pair: B2
notes: "Core case: validator must catch hash tampering"
```

### B2 (Kontrast): Hash with single character altered

**Purpose:** Probe edge case: does validator require exact match or fuzzy tolerance?

```yaml
case_id: B2
category: hash_drift
base_fixture: tests/fixtures/agent_handoff/pass-minimal.json
mutation:
  field: hash
  change: "<original_sha1>" → "<modified_by_1_char>"
  rationale: "Minimal hash change; edge case for tolerance"
expected_validator_behavior: "? (probe — will show tolerance level)"
expected_error_type: null
contrast_pair: B1
notes: "Edge case: tests validator tolerance for small hash variations"
```

---

## Äquivalenzklasse C: Path Normalization

### C1 (negativ): Backslash separator (Windows style)

**Purpose:** Probe cross-platform path normalization.

```yaml
case_id: C1
category: path_normalization
base_fixture: tests/fixtures/agent_handoff/pass-minimal.json
mutation:
  field: handoff_target.locator
  change: "contracts/command-semantics.md" → "contracts\\command-semantics.md"
  rationale: "Windows-style backslash; tests normalization logic"
expected_validator_behavior: "? (probe — depends on normalization)"
expected_error_type: null
contrast_pair: C2
notes: "Edge case: tests cross-platform path handling; may be OS-dependent"
```

### C2 (Kontrast): Double forward slash

**Purpose:** Probe path normalization for redundant separators.

```yaml
case_id: C2
category: path_normalization
base_fixture: tests/fixtures/agent_handoff/pass-minimal.json
mutation:
  field: handoff_target.locator
  change: "contracts/command-semantics.md" → "contracts//command-semantics.md"
  rationale: "Redundant separator; edge case for normalization"
expected_validator_behavior: "? (probe — depends on normalization)"
expected_error_type: null
contrast_pair: C1
notes: "Edge case: tests handling of redundant path separators"
```

---

## Äquivalenzklasse D: Unicode/Encoding Edge Case

### D1 (negativ): Soft hyphen in locator

**Purpose:** Probe Unicode handling in path fields.

```yaml
case_id: D1
category: unicode_edge_case
base_fixture: tests/fixtures/agent_handoff/pass-minimal.json
mutation:
  field: handoff_target.locator
  change: "contracts/command-semantics.md" → "contracts/command-semantics\u00AD.md"
  rationale: "Soft hyphen (U+00AD) inserted; tests Unicode normalization"
expected_validator_behavior: REJECTED or normalized_accepted
expected_error_type: "null (if accepted) or schema_error (if rejected)"
contrast_pair: null
notes: "Edge case: tests Unicode handling; may be invisible source of bugs"
```

---

## Äquivalenzklasse E: State Field Mutation

### E1 (negativ): Target file in state changed

**Purpose:** Verify validator catches state drift.

```yaml
case_id: E1
category: state_drift
base_fixture: tests/fixtures/agent_handoff/pass-minimal.json
mutation:
  field: state.target_files[0]
  change: "<original_file>" → "<original_file>.backup"
  rationale: "State target changed; should trigger rejection"
expected_validator_behavior: REJECTED
expected_error_type: "state_mismatch or validation_error"
contrast_pair: null
notes: "Core case: validator must catch state changes"
```

---

## Äquivalenzklasse F: Version Mismatch

### F1 (negativ): Contract version changed

**Purpose:** Verify validator enforces version compatibility.

```yaml
case_id: F1
category: version_mismatch
base_fixture: tests/fixtures/agent_handoff/pass-minimal.json
mutation:
  field: version
  change: "1.0" → "1.1"
  rationale: "Contract version changed; tests compatibility check"
expected_validator_behavior: REJECTED
expected_error_type: "version_mismatch or contract_invalid"
contrast_pair: null
notes: "Core case: validator must enforce version contracts"
```

---

## Übergabe In Den Execution-PR

1. Die 6 Spezifikationen als echte JSON-Fixtures materialisieren.
2. Validator-Ausgaben je Fall erfassen.
3. Ergebnisse ausschließlich im Execution-PR entscheiden (success / patch_needed / inconclusive).

---

## Hinweise

- Dieses Dokument ist absichtlich nicht normativ für Ergebnisbehauptungen.
- Ergebnisclaims entstehen erst durch Laufspuren im Execution-PR.
- Die Kontrastpaar-Struktur dient als Testhärte, nicht als Ausführungsbeweis.
