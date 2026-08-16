---
title: "Outcome-Bound Operator Loop Successor S0-R2 — Fixed adversarial paper cases"
status: designed
canonicality: operative
created: "2026-08-16"
updated: "2026-08-16"
triggered_by: "github:heimgewebe/vibe-lab#341"
---

# Fixed S0-R2 paper cases

These classifications are frozen author assessments for independent review. They
change no predecessor record and provide no prospective cohort or efficacy evidence.

| ID | Case | Author status | Decisive R2 reason |
|---|---|---|---|
| R2-01 | P1-01 runtime-refresh authority | `eligible` | stale runtime/PR state does not execute the fresh single-use authority |
| R2-02 | P1-02 merge-bound readiness promotion | `eligible` | task publication creates the precondition but does not execute planned→ready CAS |
| R2-03 | `candidate-05002…` post-merge convergence | `ineligible` | prior seed already produced the convergence and is the productive subset later residualised as automation/durability |
| R2-04 | `candidate-a91b…` companion post-seed intake | `indeterminate` | bound evidence cannot establish lineage distinctness |
| R2-05 | `candidate-8145…` scratch patch + benchmark | `ineligible` | same mechanism was implemented and exercised before intake |
| R2-06 | D0 technical-acceptance control | `not_applicable` | technical acceptance is the complete desired effect |
| R2-07 | synthetic manual-success → durable automation relabel | `ineligible` | residualisation is explicitly lineage-positive |
| R2-08 | synthetic productive setup → distinct state-transition intervention | `eligible` | setup exposes the gap but neither produces nor exercises the later transition |

## R2-01 — P1-01 runtime-refresh authority

**Prior productive state:** CI-green main, stale immutable runtime and prior PR work
already exist.

**Candidate intervention:** mint exactly one fresh single-use refresh authority bound
to the exact runtime target and use the already authorised refresh mechanism.

**Lineage assessment:** the prior PR/runtime state does not create, exercise or
package the fresh authority. It is the state to which the authority applies.

**Status:** `eligible`.

Refs:

- `../../2026-08-16_outcome-bound-operator-loop-p0/p1/cases/P1-01/stage-a-screening.yml`
- `../../2026-08-16_outcome-bound-operator-loop-p0/p1/cases/P1-01/full-spec.json`

## R2-02 — P1-02 merge-bound readiness promotion

**Prior productive act:** PR #2014/#2015 merged and T033/T034 were published as
revision-1 `planned` TaskSpecs.

**Candidate intervention:** a typed post-merge path verifies exact merge/spec/state
bindings and performs a single `planned`→`ready` CAS with revision-bound readback.

**Lineage assessment:** publication creates the object and exposes its readiness
gap, but does not produce the desired readiness change, does not execute the CAS
transition and is not a manual/temporary version of that transition.

**Status:** `eligible`.

This does not change P1-02's permanent ineligibility under P1 revision 1.

Refs:

- `../../2026-08-16_outcome-bound-operator-loop-p0/p1/cases/P1-02/stage-a-screening.yml`
- `../../2026-08-16_outcome-bound-operator-loop-p0/p1/cases/P1-02/full-spec.json`
- `../../2026-08-16_outcome-bound-operator-loop-p0/p1/cases/P1-02/eligibility-correction.yml`

## R2-03 — candidate-05002 post-merge convergence

**Prior productive act:** `seed_missing_registry` changed authoritative StateStore
ready-task state from 136 to 140 and that convergence was observed before the
candidate intake.

**Later proposed intervention:** protected post-merge publication should perform
that conservative convergence automatically and durably.

**Lineage assessment:** the prior seed already produced the material target
convergence. The later proposal primarily residualises that observed success into
an automatic/durable path. Trigger or durability differences do not break lineage.
The favourable later prose that called the seed merely diagnostic is insufficient
to establish distinctness under the R2 evidence hierarchy.

**Status:** `ineligible`.

Refs:

- `../../2026-08-16_outcome-bound-operator-loop-successor-s0/results/reviewer-b.md`
- `github:heimgewebe/vibe-lab#336`
- `bureau-candidate:candidate-05002ab2a02663d844bbbc43`

## R2-04 — candidate-a91b companion post-seed intake

The candidate exists in the same post-seed family, but the frozen evidence does not
bind a sufficiently precise candidate intervention or primary prior-act record to
prove whether the seed is lineage-positive or distinct antecedent work.

**Status:** `indeterminate`.

Fail closed; similarity alone is not evidence, but favourable later prose cannot
prove distinctness either.

Refs:

- `bureau-candidate:candidate-a91b4d18a6c9db7e617c13ce`
- `../../2026-08-16_outcome-bound-operator-loop-successor-s0/results/reviewer-b.md`

## R2-05 — candidate-8145 already-started mechanism

The candidate's own intake stated that a scratch patch and a successful long-lived
benchmark already existed. Those acts implemented and exercised the mechanism to
be assessed.

**Status:** `ineligible` by transition overlap.

Refs:

- `github:heimgewebe/vibe-lab#336`
- `bureau-candidate:candidate-8145cd731e6a7d1163b4ed0f`

## R2-06 — D0 technical-acceptance control

A docs-only change has the complete desired effect "the changed files satisfy the
registered schema and authoritative repository validation". No downstream effect
is claimed.

**Status:** `not_applicable`.

## R2-07 — synthetic residual-durability relabel

**Frozen synthetic facts:**

1. an operator manually performs state transition A→B;
2. authoritative readback confirms B, the desired operational state;
3. after observing success, a proposal is written to make A→B automatic,
   repeatable and durable;
4. no automation code has begun yet.

Under S0 the later author could attempt to call the manual success T0 and define
only durability as the intervention.

Under R2 the manual success is lineage-positive by effect overlap and
residualisation.

**Status:** `ineligible`.

## R2-08 — synthetic distinct-transition control

**Frozen synthetic facts:**

1. a productive import creates revision-1 records in `planned` state;
2. readback exposes that the system has no reviewed transition from `planned` to
   `ready`;
3. no code, mutation or benchmark for such a transition exists;
4. a candidate intervention is then bound to add exact digest verification and a
   `planned`→`ready` CAS.

The import creates the precondition but neither produces the desired readiness
change nor exercises/packages the later CAS transition.

**Status:** `eligible`.

This control prevents R2 from degenerating into P1 revision 1's rule that every
prior productive act is disqualifying.

## Frozen aggregate

- `eligible`: 3
- `ineligible`: 3
- `indeterminate`: 1
- `not_applicable`: 1
- productive mutations performed for S0-R2 classification: 0
- predecessor records rewritten: 0
- natural cases admitted: 0
- efficacy claims: 0

Reviewer B must independently classify all eight cases and separately attempt to
construct a lineage-renaming escape. Any material disagreement rejects this rule
revision for pilot use.
