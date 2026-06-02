# Condition Definition: Run-002 (code_first_control)

## Intent

Run-002 is executed under the **`code_first_control`** condition, which differs from Run-001's **`spec_first_baseline`** condition.

## What "Code-First" Means in This Context

**Not** a fundamental difference in implementation approach or execution method (both use deterministic, repo-local scripts).

**Instead**: The condition label reflects the intended control structure:

- **Run-001 (spec_first_baseline)**: Establishes baseline execution against challenge specification (`rest-api-v1.md`) via deterministic `execute-baseline.py` script with fixed `RUN_TIMESTAMP`.
- **Run-002 (code_first_control)**: Control execution under identical specification via deterministic `execute-control.py` script with fixed `RUN_TIMESTAMP`.

## Methodological Isolation

The conditions are isolated by:

1. **Condition name**: Run-001 is labeled `spec_first_baseline` (first reference execution), Run-002 is labeled `code_first_control` (second reference execution for comparability).
2. **Reproducibility contract**: Both `execute-baseline.py` and `execute-control.py` require explicit `RUN_TIMESTAMP`, ensuring deterministic artifact generation.
3. **Same specification scope**: Both produce implementations against the same five-endpoint REST API specification (envelope pattern, error codes, validation). This enables structured comparison of two reference executions under identical specifications.

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
