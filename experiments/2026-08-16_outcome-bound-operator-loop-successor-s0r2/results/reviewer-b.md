---
title: "Outcome-Bound Operator Loop Successor S0-R2 — Independent exact-head PR review"
status: rejected
canonicality: operative
created: "2026-08-16"
updated: "2026-08-17"
triggered_by: "github:heimgewebe/vibe-lab#342; github-review:4947056280"
---

# Independent exact-head review

## Binding

- Frozen author head: `5ecaa9d8eaae6d767c51605f9a0f5c07614a9fb5`
- Base head: `8d7f764620ec06fa6bc84fe6ae02ba61f002c4b2`
- GitHub review: `4947056280`
- Review comments: `3792553284`, `3792553287`
- Review timestamp: `2026-08-16T18:46:09Z`
- Reviewer: `chatgpt-codex-connector`
- Reviewer role: independent exact-head pull-request reviewer; the review changed no repository content.

The review was bound to the same frozen author head named by the PR. It found two
P1 defects before a complete eight-case classification pass was necessary. Because
the frozen protocol says a material disagreement rejects the revision and the
frozen author inputs must not be repaired after review, the remaining case pass is
not manufactured after the fatal finding.

## Fatal finding 1 — precondition versus material sub-effect remains ambiguous

The frozen R2 rule says earlier work is lineage-positive when it already produced
the desired change or a material sub-effect, while the distinct-antecedent rule
allows earlier work that merely creates or exposes the state addressed by the
later intervention.

The reviewer found that these clauses do not decide what happens when the earlier
setup creates the exact object that the later intervention preserves and mutates.
That ambiguity reaches both positive distinct-transition controls:

- **R2-02**: publication creates the `planned` TaskSpec later promoted by the CAS;
- **R2-08**: the synthetic import creates the `planned` records later promoted by
  the distinct CAS.

Under the written rule, a reviewer can treat the created object as a material
sub-effect and therefore lineage-positive, or as only the state addressed by the
later transition. The frozen author `eligible` classifications are therefore not
semantically forced by the protocol and can reasonably be downgraded to
`indeterminate`.

This is material under the preregistered zero-disagreement gate. It also means the
rule has not yet solved the granularity problem: `effect overlap` is still
underspecified at the boundary between producing the intervention subject and
producing part of the intervention's target effect.

## Fatal finding 2 — the registered comparison cannot be executed as written

The registration declares a paired comparison with eight control and eight
treatment observations, where each fixed case is evaluated against rejected S0 and
S0-R2. The frozen procedure does not provide that experiment:

- rejected S0 contains only six fixed cases;
- R2 adds two synthetic controls that have no frozen S0 partner;
- the R2 protocol asks the independent reviewer to classify all eight only under
  R2, then compare against the frozen R2 author table.

A completed review under the written procedure would therefore measure
**author/reviewer agreement under R2**, not the registered eight-pair
**S0-versus-R2 comparison**. Repairing either the registration or procedure after
the exact-head review would rewrite preregistered experiment input and is not
permitted for this frozen revision.

This is a registration/procedure integrity failure. It is kept separate from the
semantic falsification above because the semantic ambiguity already rejects R2 on
its own.

## Authority and scope review

No finding requires or authorizes a validator, new registry/control surface,
Bureau mutation, Grabowski runtime/routing change, Chronik or Leitstand change,
queue/policy/deployment change, P1 reopening, S1 cohort, S2, P2 or P3.

The frozen P1 and rejected S0 records remain historical truth. No predecessor
classification is rewritten.

## Gate recommendation

**REJECT_THIS_REVISION.**

The frozen S0-R2 rule fails its paper-level semantic-stability gate because its two
positive distinct-transition controls are not deterministically classifiable under
the written effect-lineage definition. Separately, the preregistered comparison and
the written review procedure do not describe the same measurement.

A future successor may explicitly define the target-effect predicate so that
creating the intervention subject is distinct from satisfying a material part of
the target effect, and it must preregister the actual author/reviewer replication
or provide truly paired S0/R2 cases. Those are future design candidates only; they
are not silently retrofitted into this frozen revision.