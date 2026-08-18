---
title: "Outcome-Bound S1-R2 — Canonical identity and natural-source paper protocol"
status: designed
canonicality: operative
created: "2026-08-18"
updated: "2026-08-18"
triggered_by: "conversation:user-request-2026-08-18-continue-outcome-bound"
---

# S1-R2 paper protocol

## 1. Purpose and limit

S1-R2 tests only whether the natural-sampling contract can close the two material defects that rejected S1-R1:

- M1: experiment-caused candidates were not excluded by a frozen source-independence rule;
- M2: legacy candidate events without stored `candidate_id` were not normalized through Bureau's canonical identity rule before grouping.

A third predecessor incident was review-process level: PR #348 was merged while a material exact-head REJECT was terminal but unreconciled. S1-R2 freezes that failure only as P18 and the pre-merge paper gate in section 7; it does not implement a new merge-policy or runtime control surface.

S1-R2 is paper-only. Merging this protocol does **not** activate a natural cohort, define an activation timestamp, consume a Bureau candidate, reopen P1, authorize P2/P3, or compare Minimal versus Full.

The admission semantics remain exactly S0-R3. C/S/B/E/T/Q, subject equivalence, baseline rules and prior-act classification are outside this revision.

## 2. Canonical event identity — frozen before grouping

For every authoritative Bureau StateStore `live-register` event whose payload is `kind=candidate_task`, define:

```text
canonical_candidate_id(event) =
  payload.candidate_id                           if it is present and non-empty
  "candidate-event-" + decimal(event.event_id) otherwise
```

This is the existing deployed Bureau identity rule; S1-R2 does not introduce a new identity namespace.

Only after every candidate event is normalized by this function may events be grouped by candidate identity.

For each canonical identity, define:

```text
identity_first_event = event with minimum authoritative event_id
                       among all candidate_task events whose
                       canonical_candidate_id(event) is that identity
```

An identity has an Operator-Intake birth only when **that exact `identity_first_event` itself carries `operator_intake`**. If the first event lacks `operator_intake`, later enrichment never turns the pre-existing identity into a new sampling unit.

Consequences:

- a legacy no-ID root and a later explicit successor `candidate-event-<root_event_id>` are one identity;
- a later explicit `candidate_id` can never hide an older canonical legacy root;
- an identity whose first event lacked `operator_intake` is pre-existing forever for this sampling contract, even if later events add intake metadata;
- supersessions, corrections, enrichment, repeated observations and status changes never create another identity unit;
- an idempotent replay that creates no new event creates no new unit;
- the identity-first event is fixed by the complete journal, not by the first event visible to the observer.

If the complete normalized history cannot be proven, fail closed. No fallback grouping rule may be selected after observation.

## 3. Sequence before naturalness — no filtering escape

A future natural successor must first build the complete normalized identity projection, retain only identities whose `identity_first_event` itself carries `operator_intake`, and order post-activation Operator-Intake births by `identity_first_event.event_id` ascending.

No source, repository, risk, distance, outcome, capture state, task state or naturalness criterion may reorder, skip or replace an identity after that sequence is fixed.

Natural-source evidence is therefore a **gate on a fixed slot**, never a selector for which candidate gets a slot.

An inconvenient or non-natural first identity cannot be skipped in favour of a later candidate. It consumes the fixed ordinal and falsifies the natural-source requirement.

## 4. Natural-source independence

For a fixed identity slot, naturalness is established only when the candidate arrival is independently caused outside the Outcome-Bound experiment.

The counterfactual rule is:

> The source observation/request and its Bureau candidate arrival would have occurred at the same time and with materially the same content if S1-R2 and any later natural Outcome-Bound observer did not exist.

A future natural successor must bind this claim to pre-existing evidence available without rewriting Bureau truth, for example an independently produced source observation/reference plus the canonical Bureau intake event.

The experiment itself must not create, request, time, delay, reprioritize, duplicate, split, merge, reshape or otherwise cause candidate arrivals to populate its sample.

If a fixed slot is experiment-caused, source causation is ambiguous, or the required independence evidence is unavailable, record `source_independence_failure`. The slot remains consumed and the natural revision rejects. It is never filtered out or backfilled.

Creating an easy candidate for the experiment therefore makes PASS harder, never easier.

## 5. Observer non-interference

A later natural observer may only:

- read existing Bureau/Git/GitHub/Grabowski evidence;
- create experiment-local prospective capture/evidence artifacts;
- perform independent read-only review.

It may not use Bureau candidate mutation/publication, queue/claim/priority/routing/deployment effects, or ask another actor to produce a treatment candidate for the experiment.

Any observed treatment-generation effect attributable to the experiment is an integrity failure, not a removable confounder.

Normal candidates created by unrelated operator work remain in sequence. Their source independence is judged from their pre-existing source evidence and experiment non-interference, not from whether they are convenient.

## 6. Paper cases

`sampling-cases.md` freezes the adversarial cases P01-P18.

The cases must cover at least:

- legacy no-ID root followed by explicit canonical successor;
- new explicit and new legacy identities;
- first event without operator-intake followed by later intake enrichment;
- repeated supersessions and deduplication;
- experiment-manufactured post-boundary candidate;
- independently produced candidate;
- causally ambiguous candidate;
- experiment-induced versus unrelated timing/reprioritization;
- correction before capture;
- D0, missed capture, result-known capture and event-id tie handling.

Paper review evaluates only whether each case has one unique disposition under sections 2-5. It does not simulate a real natural cohort.

## 7. Two-reviewer pre-merge gate

The exact author head must receive **two independent read-only exact-head reviews**.

Each reviewer independently derives P01-P18 and attacks both predecessor defects plus any new selection, causation, legacy-identity, timing or authority escape.

The author revision passes only when:

- both reviewers classify all P01-P18 identically to the frozen author dispositions;
- neither reviewer reports a material sampling-contract finding;
- neither review requires a new production field, validator, service or control surface;
- all reviewer jobs/receipts bound to the merge decision are terminal and explicitly reconciled by the controller before merge.

There is no majority vote. One material REJECT is sufficient to reject the author revision even if another reviewer passes it.

A reviewer still running, terminal but unread, bound to another head, or materially contradicting another review blocks merge.

## 8. Paper gate result

Primary metric: `material_sampling_contract_disagreement_count`.

### PASS_THIS_REVISION

Only if both exact-head reviewers reproduce all paper cases and the material disagreement count is zero.

PASS establishes only that the corrected sampling contract survived a bounded paper attack. It does not activate sampling and does not establish natural handling feasibility or Outcome Case efficacy.

### REJECT_THIS_REVISION

Reject on any material disagreement, unresolved causal/source-independence degree of freedom, canonical-identity mismatch, selection/backfill escape, review-reconciliation failure, or need for a new production/control surface.

The frozen author revision remains negative evidence; do not repair it in place after a material review finding.

## 9. Successor rule

Only a terminal paper PASS may justify a **separate natural-activation revision**. That later revision must freeze its own activation boundary, first-three sequence and capture gate before any eligible arrival.

The natural revision must use sections 2-5 unchanged unless a new paper review explicitly authorizes a different contract.

No paper result can authorize P2/P3, Minimal-versus-Full, automatic learning, routing, queue, Bureau schema, runtime, policy, merge-policy or deployment changes.
