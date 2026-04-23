# Phase 1 Fixtures — Drift Injection Test Cases

> These are **template/specification** files showing what Phase 1 will test.
> Actual execution fixtures will be generated during Phase 1 run.
> 
> Format: Each file documents one test case (negative case or contrast pair).

---

## Structure

Each test case fixture contains:
- `case_id`: Case identifier (A1, A2, B1, etc.)
- `category`: Equivalence class (locator, hash, normalization, etc.)
- `base_fixture`: Which valid fixture is being mutated
- `mutation`: Description of the change
- `expected_validator_behavior`: What should happen
- `artifact`: The actual mutated handoff JSON (inline or reference)

---

## Case A: Locator Path Drift

### A1 (Negative): Invalid path segment

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

### A2 (Contrast): Path with fragment

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

## Case B: Hash Value Drift

### B1 (Negative): Hash completely changed

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

### B2 (Contrast): Hash with single character altered

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

## Case C: Path Normalization

### C1 (Negative): Backslash separator (Windows style)

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

### C2 (Contrast): Double forward slash

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

## Case D: Unicode/Encoding Edge Case

### D1 (Negative): Soft hyphen in locator

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

## Case E: State Field Mutation

### E1 (Negative): Target file in state changed

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

## Case F: Version Mismatch

### F1 (Negative): Contract version changed

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

## Execution Plan

1. **Baseline:** Run existing agent_handoff validator on these 6 cases
2. **Evidence:** Record validator output (accept/reject + error messages)
3. **Decision:**
   - If all pass as expected: **Phase 1 complete**
   - If gap found: **Propose patch with contrastpair rule**
   - If ambiguous: **Document and escalate**

---

## Notes

- These fixtures are **not yet created** (design phase)
- Actual JSON content will be generated during Phase 1 execution
- Each test case includes both the specification and the expected validator behavior
- Contrastpair structure ensures both negative cases and edge-case probes
