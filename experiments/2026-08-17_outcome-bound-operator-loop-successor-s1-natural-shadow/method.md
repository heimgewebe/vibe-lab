---
title: "Outcome-Bound S1 — Natural-case external-validity protocol"
status: designed
canonicality: operative
created: "2026-08-17"
updated: "2026-08-17"
triggered_by: "github:heimgewebe/vibe-lab#345"
---

# S1 protocol

## 1. Purpose

Test only whether the already reviewed S0-R3 prospective admission semantics can be
bound on a tiny natural sample before productive mutation, without ambiguity,
selection, delay or new authority.

S1 is not an efficacy experiment. It does not measure whether Outcome Cases improve
decisions and it does not compare the two-question minimal form with the full form.

## 2. Frozen semantic authority

S1 does not rewrite the admission rule. The semantic authority is the S0-R3
`protocol.md` merged in PR #344 at main commit
`66508a215e445c0759826f6c33b14b491dd61960`.

For every treatment case the observer must apply exactly the S0-R3 meanings of:

- **C** — pre-intervention claim snapshot;
- **S** — target subject;
- **B** — contemporaneous authoritative baseline;
- **E** — one independently falsifiable target-effect predicate;
- **T** — minimal ordered authoritative state-transition path from B to E;
- **Q** — non-outcome delivery qualifiers.

No material-sub-effect concept is reintroduced. Source-required effect properties
may not be demoted into Q. Baselines may not be rebased after success. Subject
equivalence must be evidenced or the case fails closed.

## 3. Activation boundary

The experiment becomes eligible to observe natural cases only after the pull request
that introduces this protocol is merged to `main`.

The authoritative activation boundary is that PR's GitHub merge timestamp and merge
commit. Nothing occurring before that boundary may become an S1 treatment case.

This protocol, registration and the initial no-execution decision must therefore be
frozen in the author commit before merge. Post-merge case records are separate,
append-or-create-only artifacts and may not mutate the frozen protocol.

## 4. Natural source universe

Treatment cases come only from canonical Bureau operator-intake candidates that:

1. were independently created outside this experiment after the activation boundary;
2. have a stable Bureau candidate/event identity before S1 capture;
3. were not created, selected, delayed, reprioritized or reshaped for S1;
4. have not had their outcome observed before capture begins.

The Bureau record remains the authority for intake identity. S1 stores references,
not a second copy of Bureau truth.

## 5. Deterministic sample and no cherry-picking

The treatment sample is the first three canonical Bureau intakes, ordered by
ascending canonical Bureau event id, that become visible after activation.

Every one of those first three arrivals permanently consumes its ordinal S1 slot.
There is no replacement, backfill, slot skipping or outcome-based exclusion.

A case that is D0 / `not_applicable`, already under productive mutation, impossible
to bind, or otherwise unusable still consumes its slot and remains evidence. Such a
case may make the final result inconclusive or negative; it may never be replaced by
a more convenient task.

Slots are fixed as `S1-N01`, `S1-N02`, `S1-N03`.

## 6. Capture timing

For each arrival, S1 attempts one shadow capture without extending the time before
productive work would naturally begin.

The capture record must freeze or fail to freeze:

- Bureau candidate/event reference and slot ordinal;
- capture start and stop/freeze timestamps;
- proof/reference for productive-mutation state at capture start;
- C/S/B/E/T/Q bindings under the frozen S0-R3 rule;
- S0-R3 classification: `eligible`, `ineligible`, `indeterminate`, or
  `not_applicable`;
- bounded reason when any binding is unavailable or ambiguous;
- elapsed handling time in seconds;
- authority-violation count, explicitly zero when none occurred.

If productive mutation has already begun before the capture starts, record
`capture_missed_before_mutation`; do not reconstruct C/S/B/E/T/Q retrospectively.
The slot is consumed and productive work continues unchanged.

If the capture cannot finish before productive work would naturally begin, record
`capture_not_frozen_in_time`; do not delay the task. The slot is consumed.

## 7. Fixed paper control

The registration schema requires a bounded comparison. S1 does not invent synthetic
natural controls and does not claim a paired experiment.

Control is exactly three already frozen S0-R3 paper cases from PR #344:

- R3-02 — create then mutate, author/reviewer classification reproduced;
- R3-04 — pure prerequisite then distinct runtime transition, reproduced;
- R3-08 — unresolved subject equivalence, correctly fail-closed as indeterminate.

These three controls establish only the known paper-semantic benchmark. They are
never counted as natural evidence and are not paired to treatment cases.

Treatment is exactly the three natural slots above. Comparison mode is unpaired.

## 8. Independent review

After all three slots are consumed, or immediately after an integrity/authority stop,
an independent exact-revision reviewer receives the frozen protocol plus the
case evidence packet and must independently:

1. verify the activation boundary and deterministic three-arrival sequence;
2. verify that no replacement/backfill or outcome selection occurred;
3. restate C/S/B/E/T/Q for every case where prospective binding was attempted;
4. reproduce or challenge the S0-R3 classification;
5. distinguish honest source-evidence insufficiency from semantic-rule ambiguity;
6. verify capture timing and elapsed handling time;
7. attack baseline, qualifier, subject and result-informed renaming;
8. verify that S1 caused zero productive authority effects.

A material disagreement is any changed classification, required downgrade to
`indeterminate`, non-reproducible C/S/B/E/T/Q binding, credible renaming escape,
sequence/backfill mismatch, retroactive capture, or unrecorded authority effect.

## 9. Measures

### Primary: natural_case_binding_failure_count

Count one failure for each treatment slot with any of:

- `capture_missed_before_mutation`;
- `capture_not_frozen_in_time`;
- a material independent-review disagreement;
- retroactive or result-informed binding;
- an authority violation;
- a non-D0 case whose C/S/B/E/T cannot be frozen prospectively.

Lower is better.

### Cost: natural_case_binding_effort_seconds

Measure elapsed shadow handling time from capture start to freeze/stop for each slot.
No productive implementation or reviewer time is included in this metric.

### Guard measures

Record separately:

- number of D0 / `not_applicable` arrivals;
- definitive non-D0 bindings;
- agreed `indeterminate` cases and whether caused by source-evidence insufficiency
  or rule ambiguity;
- material reviewer disagreements;
- authority violations;
- replacements/backfills (must remain zero).

## 10. Preregistered gate

### PASS_THIS_REVISION

Only if all of the following hold:

- all three natural slots were consumed in canonical arrival order;
- all three captures began before productive mutation and froze before productive
  work would naturally begin;
- `natural_case_binding_failure_count == 0`;
- zero material independent-review disagreements;
- zero authority violations and zero replacements/backfills;
- median treatment binding effort is at most 600 seconds;
- at least two of the three treatment cases are non-D0 and have definitive complete
  C/S/B/E/T bindings (`eligible` or `ineligible`).

PASS establishes only tiny-sample natural handling feasibility for the frozen R3
rule. It does not establish efficacy or adoption readiness.

### REJECT_THIS_REVISION

If any integrity violation, retroactive reconstruction, selection/backfill,
productive authority effect or independently confirmed semantic-rule failure occurs.

A binding-effort median above 600 seconds also rejects this revision as too costly
for the intended lightweight shadow use.

### INCONCLUSIVE

Use when the sequence was preserved and no integrity/authority violation occurred,
but the three natural arrivals do not contain at least two definitive non-D0 cases,
or the evidence is otherwise too sparse to evaluate external validity honestly.

Do not backfill an inconclusive sample.

## 11. Stop rules

Stop assignment immediately and preserve all records if:

- any case would need retrospective reconstruction after productive mutation;
- an existing case record would need rewriting rather than append-only correction;
- task selection, execution, routing, queue, priority, timing, merge, deployment or
  technical closeout is changed for the experiment;
- Bureau/GitHub/CI/runtime technical truth would need duplication rather than a
  reference;
- raw chat, secrets or private payloads would need to be stored;
- the sample sequence cannot be proven;
- a validator, new runtime field or production authority is required to continue.

## 12. Non-claims and successor rule

S1 cannot authorize P1 reopening, P2, P3, the Minimal-vs-Full comparison, automatic
learning, routing changes, Bureau schema changes or any production integration.

A PASS can support only a separately reviewed future proposal that asks whether the
Outcome Case structure changes enough real decisions to justify its cost. A reject
or inconclusive result remains negative/limited evidence and does not reopen or
rewrite prior technical tasks.
