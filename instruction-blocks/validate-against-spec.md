---
title: "Validate-Against-Spec"
type: instruction_block
status: adopted
canonicality: operative
evidence_source: "experiments/2026-04-08_spec-first/"
created: "2026-04-20"
updated: "2026-04-20"
tags:
  - validation
  - spec-first
  - quality-assurance
relations:
  - type: derived_from
    target: ../catalog/techniques/spec-first-prompting.md
---

After generating code from a specification:
1. Check every endpoint/function against the spec — are all cases covered?
2. Verify error handling matches the defined error codes
3. Confirm response structures match the schema exactly
4. Test edge cases that were explicitly defined in the spec

If the code deviates from the spec: fix the code, not the spec (unless the spec has a genuine error).
