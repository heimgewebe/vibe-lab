# Outcome-Bound S1 — terminal sampling-integrity closeout

## Status

**REJECT_THIS_REVISION.**

S1 terminates on a sampling-integrity failure before any natural treatment cohort
can be validly enumerated. This is a terminal result for this S1 protocol revision,
not a statement about Outcome Case efficacy.

## Load-bearing defect

The frozen method says that treatment is the first three canonical Bureau
`intakes`/`arrivals` after activation, ordered by canonical event id, and separately
requires a stable `candidate/event identity`. It never specifies whether a
post-activation supersession event for a candidate identity that existed before
activation is itself a new natural S1 arrival.

Two incompatible interpretations were explored during closeout:

1. event-arrival semantics, which assigned `8146/8147/8148`;
2. first-new-candidate-identity semantics, which later selected event `8166`.

Neither interpretation was uniquely frozen at activation. Independent exact-head
review specifically found that the later identity-first obligation postdated the
earlier observed events and therefore cannot retroactively exclude them. The
intermediate T012 interpretation and its timing proof are consequently preserved but
not endorsed and are not part of the terminal gate basis.

## Frozen gate application

Section 11 requires stopping when the sample sequence cannot be proven. Section 10
separately requires `REJECT_THIS_REVISION` for any selection/backfill or other
integrity violation.

Current terminal accounting:

- sample sequence provable from frozen protocol: **no**;
- endorsed natural slot assignments: **0**;
- replacement/backfill performed: **0**;
- S1 productive authority violations: **0**;
- natural-case binding-failure count: **not derived** because the treatment sample
  itself is not validly enumerable;
- result: **REJECT_THIS_REVISION**.

## Preservation and authority

No historical capture or correction was rewritten to manufacture this result.
Earlier event-arrival and identity-first interpretations remain as preserved draft
history, with create-only disposition records and
`results/sampling-integrity-closeout.yml` as the current S1 authority.

Bureau remains authoritative for candidate/task state; Git/GitHub and CI for
technical revision truth; Grabowski for execution receipts. S1 creates no second
technical truth and changes no routing, queue, policy, runtime, merge or deployment
authority.

## Independent review

The independent Grok exact-head review was bound to PR #347 head
`ca7ba0970ce66b6915b8ff32ffa00ffa2e80cbec`; audit SHA-256
`878a6fd4a3328db63a5c89b30a54ad50a43e1556959ded51c9ed7238dc5b197e`.
Its sampling-frame finding is the load-bearing external review result. The separate
review concern about normalized T012 timing is non-load-bearing because the terminal
S1 gate no longer relies on event `8166` or commit/capture ordering.

## Non-claims

This result does not:

- establish Outcome Case efficacy or inefficacy;
- choose Minimal over Full or Full over Minimal;
- reopen P1;
- authorize P2, P3 or a replacement S1 cohort;
- authorize Bureau/Grabowski/Chronik integration;
- reopen or relabel any previously closed technical task.

Any future natural-sampling experiment must freeze its sampling unit before the
first eligible arrival and requires separate justification and review.
