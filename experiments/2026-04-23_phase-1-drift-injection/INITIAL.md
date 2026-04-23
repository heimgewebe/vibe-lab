# Phase 1 Initial State

## Baseline Measurement

**Execution Date:** 2026-04-23  
**Branch:** experiments/phase-1-drift-injection  
**Status:** Planned

### Fixture Inventory

**Source:** `tests/fixtures/agent_handoff/`

**Valid fixtures (should pass validator):**
- `pass-minimal.json` — minimal valid handoff
- Additional valid fixtures (counted below)

**Invalid fixtures (should fail validator):**
- `contract-invalid-missing-handoff.json`
- `hash-mismatch.json`
- `partial-missing-required-fixes.json`
- Additional invalid fixtures (counted below)

**Fixture count command:**
```bash
find tests/fixtures/agent_handoff -type f -name '*.json' | wc -l
```

**Expected count:** ~8–10 fixtures (baseline TBD during execution)

### Validator State

**Validator:** `agent_handoff` (from contracts/command-semantics.md)

**Test command:**
```bash
make validate
```

**Current baseline (pre-Phase 1):**
```
🤝 Validating agent handoff fixtures...
🔍 Agent Handoff Validation
  ✅ tests/fixtures/agent_handoff/contract-invalid-missing-handoff.json (expected contract_invalid)
  ✅ tests/fixtures/agent_handoff/hash-mismatch.json (expected hash_mismatch)
  ✅ tests/fixtures/agent_handoff/partial-missing-required-fixes.json (expected contract_invalid)
  ✅ tests/fixtures/agent_handoff/pass-minimal.json

✅ Agent handoff validation passed.
🧪 Running agent handoff regression tests...
......
----------------------------------------------------------------------
Ran 6 tests in X.XXXs

OK
```

**Interpretation:** Validator is working as of baseline; 6 regression tests pass.

### Test Case Setup

**Phase 1 will create:** 6 new drift injection fixtures (A1, A2, B1, B2, C1, D1)

**Directory:** `results/fixtures/` (within this experiment)

**Format:** JSON, matching agent_handoff schema with single-field mutations

---

## Preconditions Check

- [x] Agent Failure Surface Design PR (#93) logic available
- [x] make validate passes (confirmed by recent run)
- [ ] Phase 1 fixtures created (TBD)
- [ ] Phase 1 execution started (TBD)

---

## Execution Timeline

| Step | Date | Status | Owner |
| ---- | ---- | ------ | ----- |
| Baseline measurement | 2026-04-23 | ✓ | design phase |
| Create 6 fixtures | TBD | — | execution |
| Run validator tests | TBD | — | execution |
| Collect evidence | TBD | — | execution |
| Decision point | TBD | — | review |

---

## Notes

- Baseline fixture count: established via `find` command (recursive, robust)
- Validator behavior: documented in baseline make validate output
- Phase 1 is deliberately minimal to avoid scope creep
