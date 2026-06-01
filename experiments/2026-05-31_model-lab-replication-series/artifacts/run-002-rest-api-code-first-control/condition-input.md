# Condition Definition: Run-002 (code_first_control)

## Intent

Run-002 is executed under the **`code_first_control`** condition, which differs from Run-001's **`spec_first_baseline`** condition.

## What "Code-First" Means in This Context

**Not** a fundamental difference in implementation approach (both are template-generated code).

**Instead**: The execution generation differs:

- **Run-001 (spec_first_baseline)**: Agent receives challenge specification (`rest-api-v1.md`), interprets specification, generates implementation.
- **Run-002 (code_first_control)**: Agent receives the same challenge specification, then generates code via a deterministic script (`execute-control.py`) with fixed parameters (`RUN_TIMESTAMP`).

## Methodological Isolation

The conditions are isolated by:

1. **Execution path**: Run-001 uses open-ended agent interpretation; Run-002 uses deterministic parametric generation.
2. **Reproducibility contract**: Run-002's `execute-control.py` requires explicit `RUN_TIMESTAMP`, ensuring deterministic artifact generation.
3. **Same result surface**: Both produce the same five-endpoint REST API, envelope pattern, error codes, validation. This enables comparison of execution strategies without confounding factors.

## What This Does NOT Claim

- Run-002 is "better" or "worse" than Run-001
- "Code-first" means a fundamentally different software-engineering paradigm
- The condition difference automatically predicts implementation quality or maintainability

## What This ENABLES

- Structured comparison of two execution strategies under identical specifications
- Assessment of whether condition affects implementation completeness, consistency, or artifact fidelity
- Comparison surface infrastructure (not comparison result)

## Actual Comparison

Comparison is deferred to a separate `decision_type=result_assessment` artifact to be created later.
