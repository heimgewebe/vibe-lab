---
title: "Outcome-Bound Operator Loop Successor S0-R2 — Paper gate"
status: rejected
canonicality: operative
created: "2026-08-17"
updated: "2026-08-17"
triggered_by: "github:heimgewebe/vibe-lab#342; github-review:4947056280"
---

# S0-R2 paper gate

## Frozen author assessment

The frozen author revision is
`5ecaa9d8eaae6d767c51605f9a0f5c07614a9fb5`. Its eight classifications remain
unchanged as historical experiment input:

- R2-01 `eligible`
- R2-02 `eligible`
- R2-03 `ineligible`
- R2-04 `indeterminate`
- R2-05 `ineligible`
- R2-06 `not_applicable`
- R2-07 `ineligible`
- R2-08 `eligible`

They are not repaired after review.

## Exact-head review result

GitHub review `4947056280`, bound to the frozen author head, found a material
semantic ambiguity in the effect-lineage rule. The protocol does not determine
whether an earlier act that creates the exact object later preserved and mutated
is a lineage-positive material sub-effect or merely the antecedent state addressed
by a distinct transition.

That ambiguity directly affects R2-02 and R2-08. Their frozen `eligible` outcomes
can reasonably become `indeterminate` without violating the written rule. The
preregistered success condition required zero material disagreement, so this alone
rejects the revision.

The review also found a separate registration/procedure mismatch: the registration
requires eight paired S0/R2 observations, but rejected S0 has six fixed cases and
the R2 procedure asks for eight R2-only reviewer classifications. The registered
comparison therefore cannot be executed from the frozen inputs as written.

## Gate result

**REJECT_THIS_REVISION.**

The frozen S0-R2 semantic boundary is not stable enough for a natural
admission-only shadow proposal. The exact revision is terminal negative evidence,
not a draft to be repaired into a pass.

## Consequences

- P1 revision 1 remains closed and unchanged.
- Rejected S0 remains closed and unchanged.
- The frozen S0-R2 protocol, registration and author classifications are not
  rewritten after review.
- No S1 or natural cohort starts.
- No validator or new metadata/control surface is justified.
- S2, P2 and P3 remain unauthorized.
- No Bureau, Grabowski runtime/routing, Chronik, Leitstand, queue, policy,
  deployment or merge-policy authority changes.
- A future successor must be a new revision with a prospectively frozen rule and
  a registration that matches its actual review procedure.

## Future design hypothesis, not part of R2

One plausible next rule would bind the candidate intervention to an explicit target
state delta or target predicate before classification: creating the subject/input
would be antecedent unless it already satisfies a non-trivial part of that target
predicate. This could distinguish R2-02/R2-08 from candidate-05002 without relying
on object identity alone.

That idea is deliberately not inserted into R2 after the fatal review.