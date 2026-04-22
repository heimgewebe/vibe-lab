---
title: "Edge-Case-Enumeration"
type: instruction_block
status: adopted
canonicality: operative
evidence_source: "experiments/2026-04-14_prompt-length-control/"
created: "2026-04-20"
updated: "2026-04-20"
tags:
  - edge-cases
  - completeness
  - prompting
relations:
  - type: derived_from
    target: ../catalog/techniques/spec-first-prompting.md
  - type: references
    target: ../catalog/techniques/prompt-length-control.md
---

Before implementation, enumerate edge cases explicitly:
1. Empty/null inputs
2. Maximum/minimum values and boundary conditions
3. Special characters and encoding edge cases
4. Concurrent or repeated operations
5. Invalid or malformed input data

For each edge case, define the expected behavior. This is not optional padding — explicit edge case enumeration is part of the constraint structure that drives code quality.

Missing edge cases in the specification = missing edge cases in the output.
