---
title: "No-Vague-Prompts"
type: instruction_block
status: adopted
canonicality: operative
evidence_source: "experiments/2026-04-08_spec-first/"
created: "2026-04-20"
updated: "2026-04-20"
tags:
  - anti-pattern
  - prompting
  - rework-reduction
relations:
  - type: derived_from
    target: ../catalog/anti-patterns/vague-prompt-and-fix.md
---

Never give a vague task description and then iteratively fix the output.

Instead:
1. Define what you need precisely before prompting
2. Include structure, constraints, and expected format upfront
3. Specify error handling and edge cases explicitly

Vague prompts lead to: inconsistent output, missing edge cases, high rework (5-6× more than structured approach), and false confidence in superficially correct results.
