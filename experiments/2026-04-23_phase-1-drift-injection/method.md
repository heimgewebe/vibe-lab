# Phase 1: Drift Injection — Systematic Testing

> **Duration:** Minimal (6 test cases)  
> **Scope:** Agent handoff validator coverage under locator/hash drift  
> **Constraint:** Phase 1 only; no Phase 2+ pre-emptive logic  

## Overview

Phase 1 **injects locator drifts** into known-valid agent handoff fixtures and measures whether existing validators catch them. The goal is to detect coverage gaps or confirm existing validator robustness.

This is the most concrete, operationally tight phase of the series. It requires:
1. Real fixtures from tests/fixtures/agent_handoff/
2. Real validator runs (make validate or direct invocation)
3. Concrete evidence (validator output, acceptance/rejection status)
4. No speculation

---

## Definitions

### Baseline Fixture

A valid agent handoff record that:
- Matches `contracts/command-semantics.md` handoff schema
- Passes the current agent_handoff validator
- Has all required fields (command, version, handoff_target, intent, hash, state, etc.)

**Source:** `tests/fixtures/agent_handoff/pass-minimal.json`, `valid-edge-complex.json`, etc.

### Drift Injection

A **minimal, single-field mutation** of a baseline fixture:
- Change the `handoff_target.locator` path
- Change the `hash` value
- Normalize path separators (/ vs \\ vs variations)
- Add/remove path segments

**Definition:** Exactly one field mutated; all else identical.

### Equivalence Class

A set of mutations that should **all trigger the same validator behavior** (all accept or all reject).

Example: "All mutations that shift the locator path by 1-2 segments should be rejected."

### Contrast Pair (Kontrastpaar)

For **each** equivalence class, we define:
- **Negative case:** A drift that **should be rejected** (the equivalence class baseline)
- **Near-valid contrast:** A similar drift that **might be accepted** (edge case)

Example:
- Negative: `locator: "contracts/foo/invalid-deep"` (should reject)
- Contrast: `locator: "contracts/invalid-deep"` (should accept, if normalization is lenient)

This prevents **alibi fixtures** (single trivial test cases).

---

## Test Cases (6 Minimal)

### Case A: Locator Path Drift

**Equivalence class:** Structural path changes

#### A1 (Negative): Invalid path segment
```json
{
  "fixture": "pass-minimal.json",
  "mutation": {
    "field": "handoff_target.locator",
    "old_value": "contracts/command-semantics.md",
    "new_value": "contracts/command-INVALID.md"
  },
  "expected": "REJECTED",
  "reason": "Path segment changed; should not match"
}
```

#### A2 (Contrast): Path normalization variant
```json
{
  "fixture": "pass-minimal.json",
  "mutation": {
    "field": "handoff_target.locator",
    "old_value": "contracts/command-semantics.md",
    "new_value": "contracts/command-semantics.md#L10"
  },
  "expected": "? (probe)",
  "reason": "Fragment added; validator behavior unknown (edge case)"
}
```

---

### Case B: Hash Value Drift

**Equivalence class:** Hash mutations

#### B1 (Negative): Hash completely changed
```json
{
  "fixture": "pass-minimal.json",
  "mutation": {
    "field": "hash",
    "old_value": "<original_hash>",
    "new_value": "ffffffffffffffffffffffffffffffffffffffff"
  },
  "expected": "REJECTED",
  "reason": "Hash mismatch; validator should catch"
}
```

#### B2 (Contrast): Hash off-by-one bit
```json
{
  "fixture": "pass-minimal.json",
  "mutation": {
    "field": "hash",
    "old_value": "<original_hash>",
    "new_value": "<original_hash_with_1_char_changed>"
  },
  "expected": "? (probe)",
  "reason": "Minimal hash change; edge case"
}
```

---

### Case C: Path Normalization

**Equivalence class:** Windows vs. Unix path separators

#### C1 (Negative): Mixed separator style
```json
{
  "fixture": "pass-minimal.json",
  "mutation": {
    "field": "handoff_target.locator",
    "old_value": "contracts/command-semantics.md",
    "new_value": "contracts\\command-semantics.md"
  },
  "expected": "? (probe)",
  "reason": "Backslash separator; depends on path normalization logic"
}
```

#### C2 (Contrast): Double slash
```json
{
  "fixture": "pass-minimal.json",
  "mutation": {
    "field": "handoff_target.locator",
    "old_value": "contracts/command-semantics.md",
    "new_value": "contracts//command-semantics.md"
  },
  "expected": "? (probe)",
  "reason": "Redundant separator; edge case for normalization"
}
```

---

### Case D–F: Token/Encoding Edge Cases

#### D1 (Negative): UTF-8 normalization
```json
{
  "fixture": "pass-minimal.json",
  "mutation": {
    "field": "handoff_target.locator",
    "old_value": "contracts/command-semantics.md",
    "new_value": "contracts/command-semantics.md\u00AD"
  },
  "expected": "? (probe)",
  "reason": "Soft hyphen added; Unicode edge case"
}
```

#### E1 (Negative): State field mutation
```json
{
  "fixture": "pass-minimal.json",
  "mutation": {
    "field": "state.target_files[0]",
    "old_value": "<original_file>",
    "new_value": "<original_file>.backup"
  },
  "expected": "REJECTED",
  "reason": "State target changed; should trigger validator"
}
```

#### F1 (Negative): Version mismatch
```json
{
  "fixture": "pass-minimal.json",
  "mutation": {
    "field": "version",
    "old_value": "1.0",
    "new_value": "1.1"
  },
  "expected": "REJECTED",
  "reason": "Contract version changed; validator enforces compatibility"
}
```

---

## Execution Steps

1. **Baseline Verification**
   ```bash
   make validate  # confirm existing tests pass
   ```

2. **Fixture Generation**
   - Create 6 fixture files in a temporary staging directory
   - Each fixture is a standalone JSON file
   - Name: `phase-1-drift-A1.json`, `phase-1-drift-A2.json`, etc.

3. **Validator Invocation**
   For each fixture:
   ```bash
   python tests/validators/agent_handoff.py < phase-1-drift-X.json
   ```
   Record:
   - Exit code (0 = accepted, 1 = rejected, etc.)
   - Stdout/stderr
   - Error messages (if any)

4. **Evidence Recording**
   Each test case recorded in `results/evidence.jsonl`:
   ```json
   {
     "timestamp": "2026-04-23T...",
     "fixture": "phase-1-drift-A1",
     "expected": "REJECTED",
     "actual": "REJECTED",
     "validator_output": "...",
     "status": "✅ PASS",
     "hypothesis_support": "confirmed"
   }
   ```

5. **Stop Condition**
   - If all 6 cases behave as expected: Phase 1 complete ✓
   - If 1+ case diverges from expectation:
     - Document in decision.yml
     - If false-positive (should reject but accepted):
       - Draft patch with contrastpair rule
       - Create new PR from this work
     - If false-negative (should accept but rejected):
       - Document as accepted limitation or re-evaluate hypothesis

---

## Stop Conditions

### Success (no patch needed)
- All 6 test cases produce expected validator behavior
- Evidence.jsonl is complete
- No gaps discovered
- Decision: **Phase 1 complete; Phase 2 candidate decision**

### Gap Found (patch needed)
- At least one case behaves unexpectedly
- False-positive detected: drift slipped through validator
- Decision: **Phase 1 pivots to patch**
  1. Draft minimal patch
  2. Ensure contrastpair rule: include negative + contrast case
  3. Validate patch with make validate
  4. Create separate PR for patch (do not commit to Phase 1)

---

## Constraints & Boundaries

| Boundary | Inside Scope | Outside Scope |
| -------- | ----------- | ------------ |
| Fixture scope | agent_handoff validator only | Command chains, cross-contract |
| Mutation scope | Locator, hash, state, version | Semantic meaning, logic |
| Validator scope | Schema compliance, structure | Quality judgment, "intelligence" |
| Outcome scope | Evidence + patch proposal | Phase 2 execution |

---

## Kontrastpaar Rule (Patch Gate)

If Phase 1 discovers a validator gap and proposes a patch:

**Mandatory:**
1. Negative case: a drift that should be rejected (was falsely accepted)
2. Contrast case: a near-valid alternative that should still be accepted

**Example:**
- Negative: `locator: "contracts/invalid-path"` (should reject)
- Contrast: `locator: "contracts/valid-path"` (should accept)

**Prevents:** Alibi patches that only fix one edge case without probing related cases.

---

## Success Metrics

| Metric | Target |
| ------ | ------ |
| Evidence completeness | 6/6 fixtures tested |
| False-positive rate | 0 (or explicitly documented) |
| False-negative rate | 0 (or explicitly documented) |
| Patch adherence | If needed, contrastpair rule enforced |
| CI status | make validate green |

---

## Notes & Assumptions

### Known Uncertainties
- Exact validator implementation details not yet probed
- "Acceptable" path variations not yet characterized
- Stop condition depends on real-world validator behavior

### Mitigations
- Evidence.jsonl provides full audit trail
- Contrastpair rule prevents under-testing
- Phase 1 is deliberately small to stay focused

### Handoff to Phase 2
- If successful: Phase 1 evidence becomes baseline for Phase 2
- If patch needed: Patch PR created separately; Phase 2 waits for patch merge
