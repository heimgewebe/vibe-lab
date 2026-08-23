---
title: "Outcome-Bound natural pilot — sampling-unit R3 (unambiguous one-slot invariant)"
status: designed
canonicality: exploratory
created: "2026-08-23"
updated: "2026-08-23"
triggered_by: "bureau-task:OPERATOR-INTEGRATION-LOOP-V1-T037; rejected-predecessor:OPERATOR-INTEGRATION-LOOP-V1-T036"
---

# Sampling-unit R3 protocol

## 1. Purpose and frozen predecessor

This is a separate successor to the rejected T036 author revision at
`c654a3c707fc4e6aafdc0034b26e2e622e1e1054`. The predecessor R2 `method.md`, R01-R09 and result are
negative evidence and MUST NOT be repaired in place.

R3 changes one semantic seam only: **slot construction happens before naturalness and
self-interference gates**. It does not test efficacy, choose a natural-pilot activation boundary or
sample size, observe natural cases, or create any production/control-plane surface.

## 2. Canonical birth identity

The inherited identity rule is unchanged:

```text
canonical_candidate_id(event) =
  payload.candidate_id                           if present and non-empty
  "candidate-event-" + decimal(event.event_id)  otherwise

identity_first_event(identity) =
  the candidate_task event with the minimum authoritative event_id
  among all candidate_task events whose canonical_candidate_id is that identity
```

A **birth-qualified identity** is an identity whose exact `identity_first_event`:

1. exists in the authoritative Bureau event journal;
2. itself carries `operator_intake`;
3. has `event_id > A`; and
4. satisfies the complete birth proof in section 4.

Neither a supersession, later intake enrichment, observer first-sighting, replay nor content
similarity can create another birth.

## 3. Two-phase slot semantics

R3 uses two different objects and never collapses them:

```text
birth_slot = (ordinal, canonical_candidate_id, anchor_event_id)
natural_evidence = admission result for an already-created birth_slot
```

### Phase S — construct and ordinal slots

For a completeness-bounded journal projection, enumerate every birth-qualified identity in
`identity_first_event.event_id` ascending order. Assign ordinals `1..K` in that order:

```text
slot_k = (
  ordinal = k,
  canonical_candidate_id(identity_first_event_k),
  anchor_event_id = identity_first_event_k.event_id
)
```

The slot exists **before** any question is asked about naturalness, experiment causation,
self-interference, source quality, capture success, task state or outcome. Once assigned, its
ordinal cannot be erased, renumbered, skipped, replaced or backfilled within this revision.

### Phase G — gate evidence for each already-created slot

Only after `slot_k` exists may the protocol evaluate whether its birth is natural and independent
of the Outcome-Bound experiment.

| Gate result | Slot exists? | Slot consumed? | Natural evidence accepted? | Revision action |
| --- | --- | --- | --- | --- |
| natural and independently evidenced | yes | yes | yes | continue under the future pilot's stop rule |
| experiment-influenced | yes | yes | no | fail closed at `k`; reject that pilot revision |
| causation ambiguous / independence unproved | yes | yes | no | fail closed at `k`; reject that pilot revision |

Thus an interfered post-`A` birth has exactly one permissible slot interpretation: **one already-created and consumed slot**. The forbidden interpretation is **zero slots**. Slot existence does not imply evidence admission: the same interfered birth contributes **zero accepted natural-evidence cases**.

`assigned` and `consumed` are also distinct. A completeness-bounded projection may assign later
ordinals, but if gate evaluation stops at `k`, later assigned slots are not evaluated or consumed
by that stopped revision. They cannot be used as replacements for `k`.

## 4. Birth proof — hard construction gate

Slot construction is permitted only from an explicitly completeness-reporting Bureau event-journal
read that can prove the identity birth without post-observation rule choice. For each proposed
anchor it must establish:

1. all relevant `candidate_task` events through the anchor are enumerable without silent
   truncation;
2. canonical identity resolution is deterministic for those events; and
3. no relevant earlier event of that identity is hidden by an unreported gap.

If completeness is not established, **no speculative slot is constructed** and the sequence stops
fail-closed at the construction gate. This is not a naturalness exclusion and does not authorize a
skip or backfill. A later revision may try again only with a newly frozen completeness proof.

The default `live-register` projection is explicitly insufficient as birth proof when its history
is truncated. A future activation requires a separate, revision-bound event-journal completeness
receipt before Phase S.

## 5. Self-interference and naturalness

The experiment must not create, request, time, accelerate, delay, reprioritize, split, merge or
semantically reshape a candidate birth. It also must not cause another actor to do so.

Crucially, these facts are **not slot-construction predicates**. They are Phase-G evidence gates on
an immutable slot. If a post-`A` birth was influenced by the experiment — including delayed,
prioritized or semantically transformed to fit the study — its fixed ordinal is consumed, its
natural-evidence disposition is `rejected_interference`, and the revision stops fail-closed.

When observer and candidate-producing operator are the same identity, independence must be
supported by evidence that pre-existed the slot's gate decision. Missing or post-hoc independence
evidence is `rejected_ambiguous_causation`, consumes the slot and stops the revision.

## 6. Ordering and no-backfill invariant

The only ordering key is `identity_first_event.event_id` ascending. Wall-clock timestamps,
first-sighting time, repository, risk, source, outcome, task state and convenience are forbidden
ordering or replacement keys.

For any assigned ordinal `k`:

```text
slot_k cannot become absent because Phase G rejects its evidence.
slot_(k+1) cannot be relabelled slot_k.
```

This invariant is the direct R3 correction of T036's zero-versus-one ambiguity.

## 7. Prospective review rule

At the frozen **author head**, every counter-hypothesis assessment in `manifest.yml` must remain
`status: pending` and `outcome: not_checked`. No PASS, support, favorable confidence increase or
terminal result may be written before independent review evidence exists.

An independent reviewer must inspect that exact author commit and attempt at least:

1. deriving zero slots for a post-`A` experiment-influenced birth;
2. deriving one accepted natural case from the same interfered birth;
3. skipping that birth and shifting the next ordinal down;
4. using naturalness as a selector during Phase S;
5. converting incomplete birth proof into a soft skip;
6. finding any counter-hypothesis assessment that was already marked checked or favorable before
   review evidence existed.

Any material escape or prospective-label violation returns `REJECT_THIS_REVISION`. The frozen
author method/cases are not repaired after review.

## 8. Future activation hard gate

This paper revision does not activate a pilot. Before any later natural-pilot activation, a
separate revision-bound Bureau observation must demonstrate an explicitly completeness-reporting
event-journal read adequate for section 4. A truncated live-register summary, even if otherwise
healthy, cannot satisfy that gate and cannot be used to invent a birth proof.

## 9. Non-claims

This revision chooses no `A` or `N`, takes no natural cases, activates no pilot and does not reopen
P1. It authorizes neither P2/P3, Minimal-versus-Full, a validator, routing, queue, claim policy,
Bureau/Grabowski runtime integration, deployment, merge-policy, Chronik, Leitstand nor product
integration.
