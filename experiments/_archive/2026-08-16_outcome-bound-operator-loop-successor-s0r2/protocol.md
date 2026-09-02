---
title: "Outcome-Bound Operator Loop Successor S0-R2 — Effect-lineage admission protocol"
status: designed
canonicality: operative
created: "2026-08-16"
updated: "2026-08-16"
triggered_by: "github:heimgewebe/vibe-lab#341"
---

# S0-R2 protocol

## Purpose

Test whether prospective Outcome Case admission can distinguish genuinely new
interventions from renamed residual work without returning to P1 revision 1's
blanket prohibition on all prior productive mutation.

The paper rule has no authority outside this experiment.

## Core object: effect lineage

A prospective case is not defined only by the latest intervention label. The
reviewer must first decide whether any earlier productive act belongs to the same
**effect lineage** as the proposed intervention.

An earlier productive act is lineage-positive when the available evidence shows
at least one of these conditions:

1. **Effect overlap** — it already produced the desired change or a material
   sub-effect that the later intervention preserves, operationalises or scales.
2. **Transition overlap** — it implemented, executed, benchmarked or authoritatively
   exercised the same productive state transition or operative mechanism.
3. **Residualisation** — the later intervention is primarily automation,
   durability, hardening, generalisation, repetition or packaging of an already
   observed productive success.

Different names, triggers, durability levels or implementation surfaces do not by
themselves break lineage.

## Distinct antecedent rule

Earlier productive work may remain antecedent only when the evidence supports all
of the following:

- it did **not** produce the desired change or a material sub-effect of it;
- it did **not** exercise the same operative transition or mechanism;
- the later intervention is not merely a residualisation of that earlier act.

Creating or exposing the state that a later intervention addresses can therefore
be antecedent. Merely being chronologically earlier is not enough.

## Evidence hierarchy and anti-post-hoc rule

The distinction must be supported by evidence that exists independently of the
admitting author's later favourable wording. Use, in descending order:

1. primary receipts, authoritative state/readback, code or execution evidence;
2. contemporaneous intake/issue/request records;
3. later reviewed summaries that bind the above evidence.

Later author prose may explain evidence but may not by itself establish that a
prior productive act was distinct. If distinctness depends on such prose, the
classification is `indeterminate`.

## Prospective boundary

After lineage is determined, the candidate intervention still must be bound before
its own first productive effect. A future conceptual admission condition is:

```text
no lineage-positive productive act already occurred
AND no unresolved lineage ambiguity exists
AND candidate intervention identity is evidence-bound before its first effect
AND case/intervention selection is not informed by that intervention's result
```

## Classifications

- `eligible` — prior productive acts are evidence-supported as distinct antecedent
  work, and the candidate intervention is bound before its first productive effect.
- `ineligible` — a lineage-positive productive act already occurred, the candidate
  intervention itself already started, or result-informed relabelling is required.
- `indeterminate` — evidence cannot establish whether prior productive work is in
  or out of the same effect lineage.
- `not_applicable` — D0 control where technical acceptance is itself the complete
  desired effect and an Outcome Case would duplicate technical closeout.

`indeterminate` is fail-closed.

## Fixed adversarial set

Freeze exactly eight paper cases before independent review:

1. P1-01 runtime-refresh authority — clean eligible control.
2. P1-02 merge-bound readiness promotion — productive antecedent but distinct
   state transition.
3. `candidate-05002…` — the prior seed produced the convergence later proposed for
   durable automation.
4. `candidate-a91b…` — same post-seed family with insufficient intervention-specific
   evidence.
5. `candidate-8145…` — scratch implementation and successful benchmark already
   exercised the mechanism.
6. D0 technical-acceptance control.
7. synthetic residual-durability relabel — manual success followed only by
   automation/durability packaging.
8. synthetic distinct-transition control — earlier productive setup exposes a gap,
   while a later intervention performs a different state transition and is not a
   residualisation of the setup.

The synthetic cases exist only to adversarially test the semantic rule and may
never count as natural cohort evidence.

## Review gate

Reviewer A is the frozen author assessment. Reviewer B must independently classify
all eight cases from the frozen evidence and separately attempt to construct a
credible renaming/residualisation escape.

A material disagreement exists when Reviewer B:

- changes any classification;
- says a definitive classification should be `indeterminate`;
- finds a credible way to make lineage-positive work appear antecedent under the
  written rule;
- finds that the rule collapses back to "any prior productive act means
  ineligible" on the distinct-transition controls.

S0-R2 passes only with **zero material disagreements**, zero credible renaming
escapes and zero productive authority effects.

## Stop and non-promotion rules

Stop/reject this revision if classification requires rewriting predecessor records,
productive mutation, a new validator/registry/control surface, silently upgraded
evidence authority, or production authority changes.

Even a clean review does not start S1. It can support only a separate reviewed
proposal for a natural admission-only shadow pilot.
