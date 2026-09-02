---
title: "Outcome-Bound S1 — Natural-sampling gate"
status: rejected
canonicality: operative
created: "2026-08-18"
updated: "2026-08-18"
triggered_by: "github:heimgewebe/vibe-lab#347"
---

# S1 natural-sampling gate

Gate result: **REJECT_THIS_REVISION**.

| Frozen requirement | Finding |
| --- | --- |
| Deterministic natural sequence can be proved | **FAIL** — the activation protocol does not define whether supersession events for one pre-existing candidate identity are distinct S1 `intakes/arrivals`. |
| No post-observation sample selection | **FAIL as protocol integrity** — a later identity-first obligation cannot retroactively resolve already observed arrivals. |
| Replacement/backfill | PASS — none performed. |
| Productive authority effects caused by S1 | PASS — none established. |
| Technical truth remains in owning sources | PASS — S1 references Bureau/Git/Grabowski evidence and creates no second technical authority. |

The reject follows without choosing either the event-arrival interpretation
(`8146/8147/8148`) or the later first-new-candidate interpretation (`8166`). Section
11 of the frozen method says to stop when the sample sequence cannot be proven;
section 10 separately rejects any selection/backfill or other integrity violation.

No `natural_case_binding_failure_count` is needed for this terminal decision. The
sample itself is not validly enumerable under the frozen semantics, so deriving a
natural-case denominator or median handling cost would add false precision.

This gate does **not** establish that Outcome Cases fail, that the Minimal form wins,
or that the Full form loses. It rejects only this S1 natural-sampling protocol and
authorizes no P1/P2/P3, routing, queue, policy, runtime, merge or deployment change.
