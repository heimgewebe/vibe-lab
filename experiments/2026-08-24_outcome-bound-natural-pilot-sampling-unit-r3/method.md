---
title: "Outcome-Bound natural pilot — sampling-unit R3 (one-slot invariant)"
status: designed
canonicality: exploratory
created: "2026-08-24"
updated: "2026-08-24"
triggered_by: "bureau-task:OPERATOR-INTEGRATION-LOOP-V1-T037; predecessor:OPERATOR-INTEGRATION-LOOP-V1-T036; github:heimgewebe/vibe-lab#355"
---

# Sampling-unit R3 protocol

## 1. Purpose and frozen predecessor

R3 is a separate successor to the rejected T036/R2 author revision at
`c654a3c707fc4e6aafdc0034b26e2e622e1e1054`. The predecessor's method,
registration, R01-R09 cases and terminal decision are frozen negative evidence and MUST NOT be
repaired or rewritten by this revision.

R3 corrects one falsified semantic seam only: the one-slot invariant is stated without the R2
sentence-level contradiction. It does not test Outcome Case efficacy, choose an activation boundary
or sample size, observe natural cases, or create a production/control-plane surface.

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

A supersession, later intake enrichment, observer first-sighting, replay or content similarity never
creates another birth.

## 3. One-slot invariant and two-phase semantics

R3 keeps slot construction and evidence admission as different objects:

```text
birth_slot = (ordinal, canonical_candidate_id, anchor_event_id)
natural_evidence = admission result for an already-created birth_slot
```

### Phase S — construct and freeze slots

From a completeness-bounded journal projection, enumerate every birth-qualified identity in
`identity_first_event.event_id` ascending order and assign ordinals `1..K` in that order:

```text
slot_k = (
  ordinal = k,
  canonical_candidate_id(identity_first_event_k),
  anchor_event_id = identity_first_event_k.event_id
)
```

For every **fully provable** post-`A` birth, slot creation is unconditional with respect to
naturalness and experiment causation. The slot is fully constructed and its ordinal is frozen before
naturalness, self-interference, source quality, capture success, task state or outcome is evaluated.
Once assigned, its ordinal cannot be erased, renumbered, skipped, replaced or backfilled within this
revision.

### Phase G — gate evidence for an already-created slot

Only after `slot_k` exists may the protocol evaluate naturalness and independence from the
Outcome-Bound experiment.

| Gate result | Assigned slots for this birth | Consumed slots for this birth | Natural evidence accepted | Revision action |
| --- | ---: | ---: | ---: | --- |
| natural and independently evidenced | 1 | 1 | 1 | continue under a future pilot stop rule |
| experiment-influenced | **1** | **1** | **0** | fail closed at `k`; reject that pilot revision |
| causation ambiguous / independence unproved | **1** | **1** | **0** | fail closed at `k`; reject that pilot revision |

The invariant for an experiment-influenced, fully proved post-`A` birth is therefore exactly:

```text
assigned_slots = 1
consumed_slots = 1
accepted_natural_evidence = 0
```

**Only the zero-slot interpretation is excluded by the slot invariant.** Exactly one slot is
required. Separately, Phase G forbids treating that consumed slot as accepted natural evidence.
Thus both of these readings are protocol violations:

```text
assigned=0, consumed=0, natural=0      # wrong: gate erased a proved birth slot
assigned=1, consumed=1, natural=1      # wrong: slot existence was mistaken for natural admission
```

`assigned` and `consumed` remain distinct for later slots. A completeness-bounded projection may
assign later ordinals before gate evaluation reaches them; if evaluation fails at `k`, later assigned
slots are not consumed by that stopped revision and can never replace `k`.

## 4. Birth proof — construction hard gate

The one-slot invariant applies only after the identity birth is fully provable. Slot construction is
permitted only from an explicitly completeness-reporting Bureau event-journal read that establishes,
for each proposed anchor:

1. all relevant `candidate_task` events through the anchor are enumerable without silent truncation;
2. canonical identity resolution is deterministic for those events; and
3. no relevant earlier event of that identity is hidden by an unreported gap.

If completeness is not established, the protocol stops at the construction gate. It creates **no
speculative slot**, performs no naturalness decision for that candidate-looking event, and cannot
skip forward or backfill from later births. This is not a zero-slot interpretation of a fully proved
birth; the precondition for a birth-qualified identity was never established.

A default or truncated `live-register` projection is insufficient. Any later pilot activation needs
its own revision-bound, explicitly completeness-reporting event-journal receipt before Phase S.

## 5. Self-interference and naturalness

The experiment must not create, request, time, accelerate, delay, reprioritize, split, merge or
semantically reshape a candidate birth, and must not cause another actor to do so.

These facts are Phase-G evidence gates, never Phase-S slot selectors. If a fully proved post-`A`
birth was delayed, prioritized, semantically transformed or otherwise influenced by the experiment,
its already-fixed ordinal is consumed exactly once, its natural-evidence disposition is
`rejected_interference`, and the revision stops fail-closed.

When observer and candidate-producing operator are the same identity, independence must be supported
by evidence that pre-existed the slot's gate decision. Missing or post-hoc independence evidence is
`rejected_ambiguous_causation`; it consumes the one fixed slot and stops the revision.

## 6. Ordering and no-backfill invariant

The only ordering key is `identity_first_event.event_id` ascending. Wall-clock timestamps,
first-sighting time, repository, risk, source, outcome, task state and convenience are forbidden
ordering or replacement keys.

For any assigned ordinal `k`:

```text
Phase G rejection cannot make slot_k absent.
slot_(k+1) cannot be relabelled slot_k.
```

This preserves exactly one consumed ordinal for an interfered proved birth while preventing later
births from replacing it.

## 7. Prospective author-head rule

At the frozen **R3 author head**, every counter-hypothesis assessment in `manifest.yml` MUST be
`status: pending` and `outcome: not_checked`. No PASS-like result, support label, favorable confidence
increase or terminal verdict may exist before independent review evidence is produced.

The author head is immutable review input. If independent review later finds a material defect, the
review result is `REJECT_THIS_REVISION`; the frozen author files are not repaired after the review.
Any successor must be a new revision.

## 8. Required independent exact-head attacks

An independent reviewer of the exact frozen author commit must attempt at least:

1. recover the R2 contradiction by deriving both "one slot forbidden" and "one slot required";
2. derive zero slots for the adversarial experiment-influenced post-`A` birth;
3. derive accepted natural evidence from that same one-slot birth;
4. apply naturalness or self-interference while constructing the Phase-S sequence;
5. skip an interfered birth and shift a later ordinal down;
6. convert incomplete birth proof into a soft skip or speculative slot;
7. find any counter-hypothesis assessment or result label already marked checked/favorable before review evidence exists.

Any protocol-conforming escape is material and rejects this revision. A favorable review is valid only
when all attacks fail against the exact author head.

## 9. Future activation hard gate

R3 does not activate a pilot. Before any later activation, a separate revision-bound Bureau
observation must demonstrate an explicitly completeness-reporting event-journal read adequate for
section 4. A truncated summary cannot satisfy that gate and cannot be used to infer a birth proof.

## 10. Non-claims

This revision chooses no `A` or `N`, takes no natural cases, activates no pilot and does not reopen
P1. It authorizes neither P2/P3, Minimal-versus-Full, a validator, routing, queue, claim policy,
Bureau/Grabowski runtime integration, deployment, merge policy, Chronik, Leitstand nor product
integration.
