---
title: "Outcome-Bound S1-R2 Natural Activation — Prospective three-slot protocol"
status: designed
canonicality: operative
created: "2026-08-20"
updated: "2026-08-20"
triggered_by: "conversation:user-request-2026-08-20-continue-outcome-bound"
---

# S1-R2 natural-activation protocol

## 1. Purpose and authority

This experiment asks only whether the terminally paper-passed S1-R2 sampling contract can be applied prospectively to the first three real Bureau Operator-Intake births without selection, backfill, observer interference or material capture friction.

It introduces **no new sampling semantics**.

Normative sampling authority is S1-R2 `method.md` sections 2-5 at SHA-256 `19542aae0a473a8a7c63d24e3aa2909a8e115c50561bfeddd07893394d8003ab`.

Normative Outcome Case semantics are S0-R3 `protocol.md` at SHA-256 `f60b26a3bcc0f8f6b55f5b89a8d4dfdd1739017d8b228c5adaa82f5a292a30af`.

If this activation protocol can be read as changing canonical identity, identity-first birth, fixed-slot ordering, natural-source independence, observer non-interference, C/S/B/E/T/Q, subject equivalence, baseline, target-effect, transition or qualifier semantics, the imported frozen authorities win and this activation revision fails closed.

This is not an efficacy test and does not compare Minimal versus Full.

## 2. Pre-activation state and boundary

The branch introducing this protocol is pre-activation only. No Bureau event observed before the merged author revision becomes eligible.

Before merge, the independent section 8 review must be externally bound to one exact tuple:

```text
review_binding = (reviewed_base, reviewed_head, canonical_pr_diff_sha256)
```

`canonical_pr_diff_sha256` is the canonical GitHub PR diff digest for that exact base/head pair. A locally rendered raw `git diff` hash is diagnostic only and cannot substitute for the canonical PR-diff binding used by the merge decision.

Immediately before merge, authoritative PR readback must still prove:

```text
pr_head_at_merge == reviewed_head
pr_base_at_merge == reviewed_base
canonical_pr_diff_sha256_at_merge == reviewed_diff_sha256
```

After integration, authoritative Git readback must prove all of:

```text
main_merge_commit.parents == [reviewed_base, reviewed_head]
reviewed_head is an ancestor of main_merge_commit
tree(main_merge_commit) == tree(reviewed_head)
```

Only when both the pre-merge review binding and the post-merge integration identity are exact may this experiment define:

```text
activation_at = GitHub PR merged_at + 300 seconds
```

This deliberately requires more than ancestry. A later descendant tip that merely contains the reviewed commit, a changed base, a changed canonical PR diff, a merge commit with different parents, or a merge tree that differs from the reviewed-head tree leaves `activation_at` undefined. Likewise, PR `MERGED` state, ancestry alone, tree equality alone, squash/rebase/cherry-pick, or conflict-resolution content not already present in the reviewed head does **not** satisfy this gate. Record `activation_integrity_failure`, consume no natural slots and terminally reject this activation attempt rather than reinterpret similar content as reviewed content.

The strict tree condition means that if `main` advances after review, the branch must first incorporate that new base into a new author head and the resulting exact base/head/canonical-diff tuple must be reviewed again. No stale-base merge is allowed to activate the cohort.

The five-minute cooling interval is frozen before merge. It prevents merge handling itself from becoming a capture race.

A candidate identity is post-activation only when its canonical `identity_first_event.created_at >= activation_at`.

If the exact GitHub merge timestamp, exact PR head/base/diff binding, exact merge parents/tree, the exact identity-first event timestamp, or the complete authoritative Bureau journal required by S1-R2 cannot be read, fail closed. Do not infer the boundary from chat time, local file time or observer first-seen time.

Nothing before `activation_at` may be backfilled.

## 3. Complete projection before slot naturalness

For every authoritative Bureau `live-register` event with `payload.kind=candidate_task`, first apply S1-R2's frozen `canonical_candidate_id(event)` rule to the complete journal.

Only after normalization:

1. group by canonical candidate identity;
2. compute each identity's minimum-event `identity_first_event`;
3. retain only identities whose exact first event itself carries `operator_intake`;
4. retain only births whose first-event timestamp is post-activation;
5. sort by `identity_first_event.event_id` ascending.

Naturalness, repository, risk, distance, outcome, capture state, task state and source convenience are **not** sequence filters.

The first three births in that ordered projection are permanently:

- `S1R2-N01`;
- `S1R2-N02`;
- `S1R2-N03`.

Once an ordinal is determined, no later event may replace it. Corrections and supersessions may be referenced as later context but cannot change the slot's identity-first claim anchor.

## 4. Natural-source gate on the fixed slot

After a slot is fixed, apply S1-R2 section 4 unchanged.

Naturalness passes only when pre-existing evidence supports the frozen S1-R2 counterfactual that the source observation/request and Bureau arrival would have occurred at the same time and with materially the same content if this Outcome-Bound experiment did not exist.

Allowed evidence is read-only reference evidence that already exists independently of this experiment, such as the original operator/source observation plus the canonical Bureau intake event.

If the experiment caused, requested, timed, delayed, reprioritized, duplicated, split, merged or reshaped the arrival, or if source independence cannot be established, record `source_independence_failure`.

That fixed slot remains consumed. It is never skipped or backfilled. The final revision is REJECT once any slot has this failure, although the observer may continue read-only until all three fixed ordinals are recorded unless doing so would itself interfere with work.

## 5. Prospective capture gate

For each fixed slot, the observer attempts one experiment-local shadow capture without delaying productive work.

The slot record must freeze or fail to freeze:

- slot ordinal;
- canonical candidate identity;
- exact identity-first Bureau event id and stable digest/reference;
- source-independence evidence references and gate result;
- capture start and freeze/stop timestamps;
- productive-mutation state at capture start;
- target-effect result-known state at capture start;
- C/S/B/E/T/Q under unchanged S0-R3 when source independence passes and prospective binding is still possible;
- S0-R3 classification: `eligible`, `ineligible`, `indeterminate` or `not_applicable`;
- bounded failure reason;
- elapsed observer handling time in seconds;
- authority-violation count, explicitly zero when none occurred.

Case artifacts are create-only after activation. A correction must be a new append-only evidence record that references the superseded assertion; an existing frozen capture may not be rewritten to improve the result.

If productive mutation already began before capture starts, record `capture_missed_before_mutation`. Do not reconstruct C/S/B/E/T/Q retrospectively.

If the target-effect result is already observable before capture starts, record `result_informed_binding_failure`. Do not infer a favourable pre-result contract from the result.

If capture cannot freeze before productive work would naturally begin, record `capture_not_frozen_in_time`; productive work must not wait.

A non-D0 natural slot whose C/S/B/E/T cannot be frozen prospectively records `prospective_binding_failure`.

## 6. Observer non-interference

The observer may only:

- read existing Bureau, Git, GitHub, Grabowski and independently produced source evidence;
- create experiment-local prospective capture/evidence artifacts;
- run repository validation and independent read-only review of those artifacts.

The observer may not create or mutate Bureau candidates, publish intake, claim tasks, alter priority, routing, queue, timing, execution, merge, deployment or technical closeout, nor ask another actor to manufacture a treatment arrival.

Any such experiment-attributable productive effect is an `authority_violation`, consumes the implicated fixed slot if one exists, and rejects the revision.

## 7. Measures

Primary metric: `natural_source_binding_failure_count`.

Count one failure for each fixed slot with any of:

- `source_independence_failure`;
- `capture_missed_before_mutation`;
- `capture_not_frozen_in_time`;
- `result_informed_binding_failure`;
- `prospective_binding_failure` for a non-D0 natural slot;
- material independent-review disagreement;
- authority violation;
- sequence, replacement or backfill violation.

Cost metric: `natural_case_binding_effort_seconds`, measured from capture start to freeze/stop and excluding productive implementation and reviewer time.

Guard measures:

- D0 / `not_applicable` count;
- definitive non-D0 complete C/S/B/E/T bindings;
- agreed `indeterminate` count and reason class;
- source-independence failures;
- material reviewer disagreements;
- authority violations;
- replacements/backfills, which must remain zero.

## 8. Pre-activation exact-head review gate

Before merge, the exact final author head on the exact current base must receive one independent read-only semantic review bound externally to the exact `(reviewed_base, reviewed_head, canonical_pr_diff_sha256)` tuple. The reviewer must verify only activation-specific mechanics around the already frozen authorities:

1. the imported S1-R2 sections 2-5 and S0-R3 protocol hashes are exact and no local wording overrides them;
2. the merge gate requires exact pre-merge PR tip/base/canonical-diff identity and exact post-merge parent/tree identity, so ancestry alone, a descendant tip, a changed base, squash/rebase/cherry-pick or unreviewed conflict-resolution content cannot activate;
3. the merge-plus-300-second boundary is unambiguous and no pre-boundary event can enter;
4. the complete canonical identity projection fixes the first three ordinals before naturalness;
5. source independence is only a slot-consuming gate and never a selector;
6. the prospective capture failure states and PASS/REJECT/INCONCLUSIVE gate cannot backfill, delay productive work or use result knowledge;
7. the revision creates zero Bureau/runtime/routing/queue/policy/merge-policy/deployment authority.

Any material finding rejects this author revision before activation. Do not repair a reviewed head in place; create a new author head and review that exact revision/base/diff tuple again.

Every review job/receipt bound to the merge decision must be terminal and explicitly reconciled before merge. A terminal-but-unread review, a review on another head/base/canonical PR diff, a transport binding mismatch or one material REJECT blocks merge. No majority or last-read shortcut is allowed.

The pre-activation review result is intentionally **not committed back into the reviewed author branch**. Its terminal head/base/canonical-diff-bound job/receipt is external merge evidence. Once a reviewer binds to a tuple, any content change, PR-head change, base change or canonical-diff change invalidates that prior review for merge. `results/decision.yml` therefore remains the prereview design snapshot; it is not live merge-authority state.

Passing this gate authorizes only merge of the experiment protocol. Natural eligibility still begins only after the exact integration proof and the frozen post-merge `activation_at`.

## 9. Independent terminal review

After all three fixed slots are recorded, or immediately after an authority/integrity stop, one independent exact-revision reviewer receives the frozen activation protocol and case evidence packet and must independently verify:

1. exact pre-merge reviewed base/head/canonical-diff binding, exact merge parent/tree identity, exact PR merge timestamp and `activation_at`;
2. complete S1-R2 canonical identity projection;
3. exact first three post-activation Operator-Intake births by identity-first event id;
4. source-independence gate for each fixed slot;
5. zero replacement/backfill;
6. prospective timing and result-known state;
7. C/S/B/E/T/Q and S0-R3 classification wherever attempted;
8. capture effort;
9. zero productive authority effects.

A changed slot identity, changed source-independence disposition, changed S0-R3 classification, required retrospective reconstruction, sequence/backfill mismatch or unrecorded authority effect is material.

## 10. Preregistered decision gate

### PASS_THIS_REVISION

PASS only when:

- exactly `S1R2-N01..N03` are consumed in canonical post-activation order;
- source independence passes for all three fixed slots;
- `natural_source_binding_failure_count == 0`;
- zero material independent-review disagreements;
- zero authority violations;
- zero replacements/backfills;
- median treatment capture effort is at most 600 seconds;
- at least two of the three slots are non-D0 with definitive complete C/S/B/E/T bindings.

PASS establishes only tiny-sample prospective natural handling feasibility for the frozen S1-R2 + S0-R3 contracts.

### REJECT_THIS_REVISION

Reject on any pre-activation `activation_integrity_failure`, source-independence failure, binding/capture failure, material review disagreement, authority/integrity violation, sequence/backfill violation, or median effort above 600 seconds.

### INCONCLUSIVE

Use only when all three fixed slots and source-independence gates are valid with zero failures, zero disagreements, zero authority/integrity violations, zero replacement/backfill and median effort at most 600 seconds, but fewer than two informative non-D0 definitive C/S/B/E/T cases occur.

Never backfill an inconclusive cohort.

## 11. Stop and non-promotion rules

Stop rather than widen the experiment if:

- the complete normalized sequence cannot be proven;
- a frozen capture would need in-place rewriting;
- productive work would need to wait;
- technical truth would need to be copied instead of referenced;
- a new validator, production field, service or control plane is required;
- the observer would need productive authority to continue.

No result here can authorize P1 reopening, P2, P3, Minimal-versus-Full, automatic learning, Bureau schema changes, Grabowski runtime changes, routing, queue, policy, merge-policy or deployment changes.

Only a terminal PASS may justify a **separate small decision-impact pilot**. A REJECT or INCONCLUSIVE result remains terminal negative/limited evidence for this natural-activation revision.