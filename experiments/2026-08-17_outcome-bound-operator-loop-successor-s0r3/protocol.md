---
title: "Outcome-Bound Operator Loop Successor S0-R3 — Atomic target-effect protocol"
status: designed
canonicality: operative
created: "2026-08-17"
updated: "2026-08-17"
triggered_by: "github:heimgewebe/vibe-lab#343"
---

# S0-R3 protocol

## Purpose

Test whether a smaller, explicitly frozen target-effect contract makes prospective
Outcome Case admission reviewer-reproducible after S0-R2 failed on effect-lineage
ambiguity.

The rule is paper-only and has no authority outside this experiment.

## What R3 removes

S0-R3 deliberately removes **material sub-effect** as an admission concept. A
reviewer must not decide whether some arbitrary fragment of a later benefit was
"material". That degree of freedom was the main ambiguity in S0-R2.

Instead each case first freezes a **claim snapshot C**: the latest source request,
problem statement or reviewed desired-change/falsifier record that exists before
the candidate intervention begins and is not rewritten for admission. From C and
its contemporaneous authoritative state, the case freezes exactly these semantic
bindings before author classification:

1. **Subject S** — the state-bearing system/object/actor whose change is claimed.
2. **Baseline B** — the authoritative state of S at C. A later successful act may
   not be used to rebase B.
3. **Target-effect predicate E** — one independently falsifiable target-state
   assertion on S whose truth is sufficient for the declared positive effect claim.
4. **Transition signature T** — the minimal ordered authoritative state-transition
   path on S from B to E; it may contain one or more state edges but no unrelated
   implementation steps.
5. **Delivery qualifiers Q** — descriptors such as repetition, packaging or
   execution mode that are not independently claimed outcomes in C. A property
   directly required by the desired change or falsifier in C is not Q; it must be
   represented in E and, where applicable, T.

C/S/B/E/T/Q are experiment-local review objects, not proposed Bureau or runtime
fields.

## Atomic target-effect rule

`E` must be one independently falsifiable target-state assertion. If C contains
multiple separable outcome claims and no single primary effect is already selected
there, R3 does not let the author choose the favourable conjunct after the fact;
the case is `indeterminate` for this rule revision.

The author may not change C, S, B, E, T or Q after inspecting whether a prior act
would become eligible or ineligible. If the frozen evidence cannot support a
single reasonable binding, the case is `indeterminate`.

The desired-change, falsifier and decision-rule wording in C constrain E.
Implementation inputs, intermediate artifacts and prerequisites do not become
effect claims merely because the candidate cannot execute without them. Conversely,
a source-required property such as restart survival or zero-manual-intervention may
not be demoted into Q merely to make prior success look like a complete effect.

## Baseline rule

B is the authoritative state of S at C. Work completed before C may therefore be
part of the honest baseline for a genuinely later claim. Work after C may not be
used to move B forward. Earlier work that already made E true at C means there is
no unresolved target change under this contract; the case is `ineligible`.

This is the create-versus-mutate boundary:

- `absent -> planned` may establish the baseline for a later `planned -> ready`
  intervention;
- it does not thereby execute `planned -> ready`;
- if the later claim instead freezes `absent -> ready` as T, then prior creation
  cannot be laundered into a mere prerequisite.

## Same-transition and delivery-qualifier rule

A productive act after C is lineage-positive when it executed any edge of the
frozen T path on the same subject, or on a subject whose equivalence is explicitly
supported by frozen evidence, even if the later proposal adds only Q such as:

- automation;
- durability or restart persistence;
- repetition or scheduling;
- packaging or productisation;
- broader deployment of the same demonstrated transition.

Thus qualifier padding cannot turn an already demonstrated transition into a new
prospective intervention.

## Subject-equivalence rule

Same labels do not prove subject equivalence, and different labels do not disprove
it. Equivalence must be supported by frozen primary or contemporaneous evidence
showing that the earlier act exercised the same state semantics and transition
contract relevant to the later claim.

If that evidence is sufficient, the earlier T counts. If it is insufficient, the
classification is `indeterminate`; the author may not choose the favourable side.

## Prior-act decision procedure

For each productive act relevant to the case, evaluate in order:

1. Did it occur before C and is its result honestly represented in B? If yes, it
   is baseline evidence unless E was already true at C.
2. After C, did it make the frozen E true on S? If yes: **lineage-positive**.
3. After C, did it execute any edge of the frozen T path on S or an
   evidence-supported equivalent subject? If yes: **lineage-positive**.
4. Does the later candidate require changing C/S/B/E/T after observing success, or
   demoting a source-required effect property into Q? If yes:
   **lineage-positive / result-informed relabel**.
5. After C, did the act only establish an enabling input on another subject while E
   stayed false and no T edge was executed on S? If yes: **distinct antecedent**.
6. Can any of C/S/B/E/T or required subject equivalence not be established from the
   frozen evidence? **indeterminate**.

No `material sub-effect` judgement is allowed.

## Prospective candidate boundary

After prior acts are classified, the candidate itself must still be bound before
its first execution of T and before its result is known:

```text
no prior lineage-positive act
AND no unresolved C/S/B/E/T/equivalence ambiguity
AND candidate C/S/B/E/T/Q are frozen before candidate T begins
AND candidate selection/identity is not informed by candidate result
```

## Classifications

- `eligible` — all prior productive acts are distinct antecedents and the candidate
  contract is bound before T begins.
- `ineligible` — E or T was already satisfied/executed in the same lineage, the
  candidate already began, or favourable result-informed relabelling is required.
- `indeterminate` — frozen evidence cannot establish a unique contract or subject
  equivalence.
- `not_applicable` — D0 control where technical acceptance is itself the complete
  desired effect and an Outcome Case would duplicate technical closeout.

`indeterminate` is fail-closed.

## Fixed adversarial set

Freeze exactly eight R3 treatment cases before independent review:

1. create-then-preserve / durable regeneration;
2. create-then-mutate / `planned -> ready`;
3. manual repair followed by automation/durability of the same repair;
4. pure prerequisite creation followed by a distinct runtime transition;
5. already-satisfied effect with qualifier-padding relabel;
6. D0 technical-acceptance control;
7. same transition on an explicitly equivalent scratch subject followed by
   production packaging;
8. same-looking transition on a subject whose equivalence is not established.

Synthetic cases are paper probes only and may never count as natural cohort
evidence.

## Comparison contract — no fake pairs

S0-R3 fixes S0-R2's registration/procedure mismatch prospectively.

The registration uses an **unpaired** comparison:

- control count = exactly **3 predecessor falsification probes**:
  create-vs-mutate ambiguity, residual/qualifier renaming, and the prior
  registration/procedure mismatch;
- treatment count = exactly **8 R3 paper cases**;
- only the eight treatment cases are independently classified under R3;
- the three controls are failure-context checks, not invented S0/R2 case pairs and
  not part of the treatment agreement denominator.

The review must report these counts explicitly. A mismatch rejects the revision.

## Independent review gate

Reviewer A is the frozen author assessment. Reviewer B receives the exact frozen
S0-R3 author head and must independently:

1. restate C, S, B, E, T and Q for all eight cases from the frozen case facts;
2. classify all eight without using the author's classification as authority;
3. attack qualifier padding, baseline laundering and subject splitting;
4. verify that R3-02 and R3-04 remain genuinely eligible rather than collapsing
   to P1's blanket prior-mutation rule;
5. verify that R3-08 fails closed instead of choosing favourable equivalence;
6. verify the registered 3-control/8-treatment procedure exactly.

A material disagreement exists when Reviewer B:

- changes any classification;
- says a definitive classification should be `indeterminate`;
- cannot reproduce a unique C/S/B/E/T binding from the frozen facts;
- finds a credible qualifier-, baseline- or subject-renaming escape;
- finds blanket prior-mutation exclusion on the eligible controls;
- finds any count/procedure mismatch;
- finds that classification needs new production fields, validator logic or
  authority effects.

S0-R3 passes only with **zero material disagreements**, zero credible renaming
escapes, exact 3/8 procedure coherence and zero productive authority effects.

## Stop and non-promotion rules

Stop/reject this revision if classification requires rewriting predecessor
records, productive mutation, a new validator/registry/control surface, silently
upgraded evidence authority, or production authority changes.

Even a clean paper review does not reopen P1 or start a natural cohort. At most it
can support a separate reviewed proposal for another bounded admission-only shadow
step. P2, P3 and product/runtime integration remain outside this experiment.
