# Phase 1 Failure Modes & Risk Assessment

> **Status:** Designed phase; risks are design risks, not execution risks yet.

---

## Known False Assumptions

### A. "All validator behavior is deterministic across OS/encoding"

**Risk:** Path normalization, encoding handling may differ on Windows vs. Linux.

**Mitigation:**
- Phase 1 runs on Linux; results may not transfer
- Document platform-specific behavior explicitly
- Mark cross-platform testing as Phase 2+ scope

### B. "Drift injection alone is sufficient to find coverage gaps"

**Risk:** Some validator gaps are latent (require specific sequences or context).

**Mitigation:**
- Phase 1 is deliberately narrow (single-field mutations)
- Cross-contract gaps are Phase 3 scope
- Sequence gaps are Phase 2/3 scope

### C. "Absence of error means absence of problem"

**Risk:** Validator may silently accept invalid state without explicit error.

**Mitigation:**
- Phase 1 fixture evaluation is pass/fail only
- Do not interpret silence as correctness
- Evidence.jsonl must explicitly record "no error output but result unclear"

### D. "Contrastpair rule prevents alibi patches"

**Risk:** Even with contrastpair, patch may be too narrow (fixes case but not class).

**Mitigation:**
- Contrastpair rule is necessary but not sufficient
- Decision gate requires manual review of patch scope
- Phase 1 should not auto-merge patches

---

## Anti-Patterns to Avoid

### 1. Alibi Fixtures
**Definition:** Single minimal test case that appears to satisfy a requirement but doesn't.

**Example:**
```json
{
  "mutation": "change locator by 1 char",
  "expected": "rejected",
  "result": "rejected",
  "conclusion": "✓ locator validation works"
}
```

**Problem:** Only one variation tested; doesn't probe nearby cases.

**Prevention:** Contrastpair rule (negative + near-valid contrast).

### 2. Premature Validator Overhardening
**Definition:** Adding new validator logic for Phase 1 gaps before Phase 2 context.

**Example:**
```
Gap found: hash mutation not caught
→ Add new validator: hash format stricter
→ But Phase 2 might show hash isn't the real issue; locator order is
```

**Problem:** Early patch may be wrong direction.

**Prevention:**
- Phase 1 only collects evidence
- Patch proposal is separate decision gate
- Patch must have contrastpair (not just "make it stricter")

### 3. "Nice to know" Creep
**Definition:** Phase 1 starts testing things outside scope ("what if we add Unicode?").

**Example:**
```
Phase 1 is locator drift only.
But someone adds: "let's test emoji in locator"
```

**Problem:** Scope explosion.

**Prevention:**
- Phase 1 fixtures are pre-defined (6 cases)
- New ideas → Phase 2+ backlog
- Strictly reject new cases mid-Phase 1

### 4. Validator Scope Bleed
**Definition:** Validator used for quality judgment instead of structure check.

**Example:**
```
Validator rejects handoff because "locator looks suspicious"
(not because structure is wrong)
```

**Problem:** Conflates structure with semantics.

**Prevention:**
- Validator scope: schema compliance, structure validity, continuity
- Validator does NOT judge: quality, wisdom, intent

### 5. Single-Case False Confidence
**Definition:** Phase 1 finds no gaps; concludes validators are perfect.

**Example:**
```
All 6 test cases pass.
→ "We're done; validators are solid"
→ Phase 2 immediately finds cross-contract gaps
```

**Problem:** Phase 1 scope is narrow; absence of gap is not presence of completeness.

**Prevention:**
- Decision is not "validators are perfect"
- Decision is "Phase 1 found no drift-specific gaps within scope"
- Phase 2/3 may find different gap classes

---

## Negativ-Evidenz: What Counts as Valid Absence

### Valid Null Result
```
Executed Phase 1 with all 6 fixtures.
All behaved as expected.
No false positives found.
No new gap candidates.
Decision: Phase 1 complete; evidence supports Phase 2 readiness.
```

**Logged as:** evidence.jsonl complete, decision: "proceed"

### Invalid Null Result (No Conclusion)
```
Phase 1 created 2 fixtures out of 6.
Didn't get to cases C/D/E/F.
"No gaps found" (incomplete).
```

**Problem:** Missing evidence.
**Logged as:** evidence.jsonl incomplete, decision: "blocked pending full Phase 1"

### Ambiguous Null Result
```
All 6 fixtures tested.
5 behaved as expected.
1 is unclear (validator output neither error nor success).
"No gaps found" (because unclear case was ignored).
```

**Problem:** Unresolved edge case.
**Logged as:** evidence.jsonl marked "uncertain", decision: "Phase 1 requires clarification"

---

## Risk Matrix

| Risk | Likelihood | Impact | Mitigation |
| ---- | ---------- | ------ | ---------- |
| Validator behavior differs by platform | Medium | Low | Document platform; mark as Phase 2 scope |
| Alibi fixtures slip through | High | Medium | Enforce contrastpair rule; manual review |
| Phase 1 discovers gap; patch is wrong | Medium | High | Patch requires decision gate + evidence |
| Scope creep (add new test cases mid-Phase) | High | High | Pre-define 6 cases; reject additions |
| Null result misinterpreted as "perfect" | High | Medium | Explicitly state scope limits in decision |
| Validator overhardening (too strict) | Medium | High | Contrastpair rule ensures contrast cases |

---

## Stop Conditions Revisited

### SUCCESS: No patch needed
- [x] All 6 fixtures tested
- [x] Evidence.jsonl complete (6 entries)
- [x] All results match expected behavior
- [x] No false positives or ambiguous cases
- Decision: **Phase 1 complete; Phase 2 entry approved**

### BLOCKED: Patch needed
- [x] At least one false positive detected
- [x] Patch drafted with contrastpair rule (negative + contrast)
- [x] make validate still passes with patch
- [x] Patch is NOT merged to main (separate PR)
- Decision: **Phase 1 paused; patch PR in review**

### INCONCLUSIVE: Ambiguity unresolved
- [x] At least one unclear result
- [x] Cannot determine if expected or unexpected
- [x] Evidence.jsonl marked "uncertain"
- Decision: **Phase 1 paused; clarification required**

---

## Boundary Enforcement

**These are OUT of scope:**

| Out of Scope | Why | Where it goes |
| ------------ | --- | ------------- |
| Cross-contract validation | Phase 1 is handoff-only | Phase 3 |
| Command chain sequences | Phase 1 is single-fixture mutations | Phase 2 |
| Semantic meaning of locator | Phase 1 is structure only | Decision review |
| Validator performance/speed | Not a failure surface | Orthogonal work |
| "What if we add X?" | Speculative; freeze Phase 1 | Phase 2+ backlog |

---

## Success Definition

**Phase 1 is successful if:**

1. All 6 test cases produce concrete evidence (validator accept/reject)
2. Evidence matches pre-defined expectations (or documented why not)
3. No alibi fixtures (each has contrast pair)
4. Contrastpair rule enforced for any patch proposal
5. CI remains green (make validate passes)
6. Decision is documented (success, patch needed, or inconclusive)
7. If patch needed: separate PR created, Phase 1 not auto-merged

**Phase 1 is failed if:**

1. Execution stops mid-way without evidence justification
2. Alibi fixtures treated as sufficient test coverage
3. Patch created without contrastpair rule
4. make validate fails after Phase 1 work
5. Null result interpreted as "validators are perfect"
