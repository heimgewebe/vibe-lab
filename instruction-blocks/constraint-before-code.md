---
title: "Constraint-Before-Code"
type: instruction_block
status: adopted
canonicality: operative
evidence_source: "experiments/2026-04-14_prompt-length-control/"
created: "2026-04-20"
updated: "2026-04-20"
tags:
  - constraints
  - cognitive-modes
  - prompting
relations:
  - type: derived_from
    target: ../catalog/techniques/prompt-length-control.md
---

Before writing any implementation:
1. List all input constraints (types, ranges, formats, required fields)
2. List all output constraints (structure, edge case behavior)
3. Define error handling (what happens on invalid input?)
4. Identify edge cases explicitly

Do NOT substitute this with verbose explanations or essays — only structured constraints activate the right cognitive mode. Token volume without constraint structure has no quality effect.
