---
title: "Initial Prompt — rLens Agent Context Conditions"
status: designed
canonicality: operative
---

# Initial Prompt — rLens Agent Context Conditions

Design and later execute a comparison of rLens/RepoBrief agent-context conditions
for real repo and PR tasks.

The comparison must include at least:

- `no_rlens`
- `reading_pack`
- `context_pack`
- `trace_gated`

This experiment also includes `full_dump` as a diagnostic high-context condition,
not as a default candidate.

Measure unsupported claims, hallucinated paths, missing evidence, and rework
count. Do not claim improvement until comparable runs exist.
