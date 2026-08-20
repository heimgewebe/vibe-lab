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

The branch introducing this protocol is pre-activation only. No Bureau identity birth at or below the frozen activation journal watermark becomes eligible.

Before merge, the independent section 8 review must be externally bound to one exact tuple:

```text
review_binding = (reviewed_base, reviewed_head, reviewed_pr_diff_sha256)
```

`reviewed_pr_diff_sha256` is the canonical GitHub PR diff digest for that exact base/head pair. A locally rendered raw `git diff` hash is diagnostic only and cannot substitute for the canonical PR-diff binding used by the merge decision.

Immediately before merge, authoritative PR readback must still prove:

```text
pr_head_at_merge == reviewed_head
pr_base_at_merge == reviewed_base
canonical_pr_diff_sha256_at_merge == reviewed_pr_diff_sha256
```

After integration, authoritative Git readback must prove all of:

```text
main_merge_commit.parents == [reviewed_base, reviewed_head]
reviewed_head is an ancestor of main_merge_commit
tree(main_merge_commit) == tree(reviewed_head)
```

This deliberately requires more than ancestry. A later descendant tip that merely contains the reviewed commit, a changed base, a changed canonical PR diff, a merge commit with different parents, or a merge tree that differs from the reviewed-head tree fails the activation gate. Likewise, PR `MERGED` state, ancestry alone, tree equality alone, squash/rebase/cherry-pick, or conflict-resolution content not already present in the reviewed head does **not** satisfy this gate. Record `activation_integrity_failure`, consume no natural slots and terminally reject this activation attempt rather than reinterpret similar content as reviewed content.

The strict tree condition means that if `main` advances after review, the branch must first incorporate that new base into a new author head and the resulting exact base/head/canonical-diff tuple must be reviewed again. No stale-base merge is allowed to activate the cohort.

### 2.1 External work-blind trigger and single controller orchestration job

The cohort boundary must not depend on when the controller decides to arm or merge after learning about future work. This revision therefore freezes an external work-blind trigger from the material GitHub Codex finding that required this repair:

```text
orchestration_trigger_ref = github:heimgewebe/vibe-lab#353:discussion_r3819573067
orchestration_trigger_at = 2026-08-20T07:42:09Z
orchestration_start_deadline_seconds = 900
```

The trigger timestamp and the deadline are evaluated against GitHub's own HTTP `Date` response, not the Heim-PC clock. If the one controller-owned orchestration job is not started by GitHub-server time `trigger_at + 900 seconds`, this author revision is rejected before publication. The deadline is fail-closed and cannot be reset by a new local timer, empty commit, later review request or Bureau state.

Before the final author head is published to the PR, the controller must start exactly one receipt-bound `activation_orchestration_job` bound to the local author head, the expected current base, PR #353 and the work branch. From that job receipt until the activation snapshot is anchored or activation fails, neither the job nor the controller may inspect Bureau candidate or journal content. The job is controller infrastructure, not the experiment observer: its only allowed writes are publication of this exact work-branch head, request of the required current-head GitHub Codex review, and one exact GitHub merge of PR #353 after every frozen gate passes. It has no Bureau, routing, queue, policy, runtime or deployment write authority.

Once started, the orchestration job owns the whole pre-activation sequence without controller timing choices:

1. verify GitHub-server time is within the frozen trigger deadline, local checkout is clean, `HEAD` is the bound author head, and `origin/main` is the bound expected base;
2. publish exactly that head to the existing work branch without force and require remote readback of the same SHA;
3. immediately read/freeze the canonical GitHub PR diff digest for the exact base/head pair and automatically request the required current-head Codex review; no manual review-request delay is permitted;
4. poll only PR head/base/diff, CI/check state and the Codex settlement while recording a monotonic heartbeat; no Bureau candidate/journal read is allowed;
5. fail terminally on any head/base/diff drift, CI failure, unresolved/material Codex finding, review transport ambiguity, job restart/replacement or heartbeat continuity loss;
6. on the **first** poll where the exact-head self-review evidence, all required CI checks and the required Codex settlement are all PASS, immediately issue exactly one GitHub merge request for PR #353 with expected `sha=reviewed_head` and `merge_method=merge`; there is no separate controller-controlled arming or merge window;
7. verify the resulting merge identity exactly as specified above; on the first successful verification record `cooling_started_monotonic`;
8. continue the same process through the bounded cooling and one-shot Bureau snapshot below.

The review and merge therefore occur as consequences of the already-started work-blind job, not of a later operator observation. If the job cannot autonomously obtain all gates and issue its one merge effect, the revision fails rather than handing timing control back to the controller.

The post-integration checkpoint timing contract remains frozen as:

```text
checkpoint_poll_interval_target_seconds = 1
checkpoint_max_monotonic_gap_seconds = 5
cooling_threshold_seconds = 300
snapshot_deadline_seconds = 305
```

The same process must record a monotonic heartbeat around every wait/poll iteration. From orchestration-job start until the activation snapshot is anchored, any consecutive observed monotonic heartbeat gap greater than 5 seconds is `activation_integrity_failure`. A blocking external read, process starvation, SIGSTOP/descheduling or other continuity loss therefore cannot silently move the cutoff forward.

After exact merge verification, the same job must:

1. continue the heartbeat loop without Bureau candidate/journal reads;
2. on the first loop in which `monotonic_elapsed_seconds >= 300`, require `monotonic_elapsed_seconds <= 305` and immediately begin exactly one complete read-only SQLite snapshot transaction against the authoritative Bureau StateStore journal;
3. treat the first journal read in that transaction as the snapshot anchor, record `snapshot_anchor_elapsed_seconds`, and require `300 <= snapshot_anchor_elapsed_seconds <= 305`;
4. from that same transaction freeze the journal high-water event id and a digest/receipt binding the complete snapshot read.

If the process first wakes after the cooling threshold with elapsed time above 305 seconds, or if any heartbeat gap exceeded 5 seconds, it must record `activation_integrity_failure` **without opening the Bureau journal**. The job may not inspect Bureau candidate/journal content before the snapshot. The **first snapshot attempt in the closed [300,305]-second window is final**: read failure, incomplete coverage, integrity failure or missing high-water id records `activation_integrity_failure`. A restarted job, later snapshot, manual retry or replacement watermark cannot activate this PR revision.

The checkpoint is valid only when the same job proves:

```text
all_orchestration_heartbeat_gaps_seconds <= 5
300 <= snapshot_anchor_elapsed_seconds <= 305
activation_watermark_event_id = authoritative journal high-water event_id in the single snapshot transaction
activation_snapshot_ref = immutable job/receipt + snapshot digest for that exact transaction
```

Wall-clock timestamps such as GitHub `merged_at`, the job receipt time and Bureau `created_at` remain descriptive evidence only. They are never used to decide whether a Bureau birth is before or after activation.

If the authoritative snapshot exposes no explicit high-water value, use the maximum authoritative Bureau event id present in the complete snapshot transaction. The read must establish complete event coverage through that watermark.

Only identity births whose exact `identity_first_event.event_id > activation_watermark_event_id` are post-activation treatment candidates. Event ids at or below the watermark are permanently pre-activation/cooling history and may never be backfilled.

This event-id watermark is the sole cohort cutoff. It prevents clock skew from changing slot identity, while the external trigger, autonomous publication/review/merge sequence and closed checkpoint window prevent controller or scheduler timing from moving that cutoff without falsifying activation.

If the external-trigger deadline, orchestration-job identity, autonomous publication/review/merge sequence, exact merge parents/tree, heartbeat continuity, closed [300,305]-second snapshot window, single complete authoritative Bureau snapshot, activation snapshot digest/reference or journal high-water event id cannot be established, record `activation_integrity_failure`, leave the cohort inactive and consume zero natural slots. Do not reconstruct the boundary from chat time, controller timing, GitHub `merged_at`, local wall time, Bureau `created_at`, a later retry, a delayed wake or observer first-seen time.

## 3. Complete projection before slot naturalness

For every authoritative Bureau `live-register` event with `payload.kind=candidate_task`, first apply S1-R2's frozen `canonical_candidate_id(event)` rule to the complete journal.

Only after normalization:

1. group by canonical candidate identity;
2. compute each identity's minimum-event `identity_first_event`;
3. retain only identities whose exact first event itself carries `operator_intake`;
4. retain only births whose `identity_first_event.event_id > activation_watermark_event_id`;
5. sort by `identity_first_event.event_id` ascending.

Naturalness, repository, risk, distance, outcome, capture state, task state, wall-clock timestamp and source convenience are **not** sequence filters.

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
- frozen `activation_watermark_event_id` plus `activation_snapshot_ref`;
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

Before merge, the exact final author head on the exact current base must receive one independent read-only semantic review bound externally to the exact `(reviewed_base, reviewed_head, reviewed_pr_diff_sha256)` tuple. The reviewer must verify only activation-specific mechanics around the already frozen authorities:

1. the imported S1-R2 sections 2-5 and S0-R3 protocol hashes are exact and no local wording overrides them;
2. the merge gate requires exact pre-merge PR tip/base/canonical-diff identity and exact post-merge parent/tree identity, so ancestry alone, a descendant tip, a changed base, squash/rebase/cherry-pick or unreviewed conflict-resolution content cannot activate;
3. the controller orchestration job is bound before author-head publication to the frozen external Codex-finding trigger, starts within the GitHub-server 900-second deadline, and then owns publication, review request, exact merge and checkpoint without Bureau observation or later controller timing choice;
4. the same job must preserve monotonic heartbeat continuity with no gap above 5 seconds, merge automatically on the first all-gates-PASS poll, and anchor its single Bureau snapshot only in the closed [300,305]-second post-integration window; overshoot or continuity loss fails before any later snapshot can move the cutoff;
5. the complete canonical identity projection fixes the first three births strictly above the frozen event-id watermark before naturalness;
6. source independence is only a slot-consuming gate and never a selector;
7. the prospective capture failure states and PASS/REJECT/INCONCLUSIVE gate cannot backfill, delay productive work or use result knowledge;
8. the revision creates zero Bureau/runtime/routing/queue/policy/merge-policy/deployment authority.

Any material finding rejects this author revision before activation. Do not repair a reviewed head in place; create a new author head and review that exact revision/base/diff tuple again.

Every review job/receipt bound to the merge decision must be terminal and explicitly reconciled before merge. A terminal-but-unread review, a review on another head/base/canonical PR diff, a transport binding mismatch or one material REJECT blocks merge. No majority or last-read shortcut is allowed.

The pre-activation review result is intentionally **not committed back into the reviewed author branch**. Its terminal head/base/canonical-diff-bound job/receipt is external merge evidence. Once a reviewer binds to a tuple, any content change, PR-head change, base change or canonical-diff change invalidates that prior review for merge. `results/decision.yml` therefore remains the prereview design snapshot; it is not live merge-authority state.

For this activation revision, the repository-required current-head GitHub Codex settlement is the independent pre-activation semantic review. Passing it does not return merge timing to the controller: the already-running orchestration job described in section 2.1 must merge on its first all-gates-PASS observation. Natural eligibility begins only if that same job later proves exact integration, bounded monotonic cooling and the single Bureau journal watermark.

## 9. Independent terminal review

After all three fixed slots are recorded, or immediately after an authority/integrity stop, one independent exact-revision reviewer receives the frozen activation protocol and case evidence packet and must independently verify:

1. exact pre-merge reviewed base/head/canonical-diff binding and exact merge parent/tree identity;
2. exact external trigger, GitHub-server deadline and pre-publication orchestration-job identity plus its uninterrupted binding to the author head/base/PR and later frozen canonical diff;
3. all recorded monotonic heartbeat gaps are at most 5 seconds and the immutable single-attempt Bureau snapshot anchor lies in the closed [300,305]-second post-integration window;
4. immutable authoritative Bureau activation-snapshot reference and high-water event id;
5. complete S1-R2 canonical identity projection;
6. exact first three Operator-Intake births whose identity-first event ids are strictly above the activation watermark;
7. source-independence gate for each fixed slot;
8. zero replacement/backfill;
9. prospective timing and result-known state;
10. C/S/B/E/T/Q and S0-R3 classification wherever attempted;
11. capture effort;
12. zero productive authority effects.

A heartbeat continuity gap above 5 seconds, snapshot-anchor overshoot above 305 seconds, restarted/replaced checkpoint job, later activation snapshot, changed activation watermark, cross-system wall-clock substitution, changed slot identity, changed source-independence disposition, changed S0-R3 classification, required retrospective reconstruction, sequence/backfill mismatch or unrecorded authority effect is material.

## 10. Preregistered decision gate

### PASS_THIS_REVISION

PASS only when:

- exactly one externally triggered pre-publication orchestration job started within the frozen GitHub-server deadline, autonomously published/reviewed/merged the exact head and produced the activation receipt;
- every recorded checkpoint heartbeat gap is at most 5 seconds;
- the activation snapshot anchor elapsed time is in the closed [300,305]-second window;
- the activation snapshot/watermark is valid, immutable and from that job's single post-threshold snapshot attempt;
- exactly `S1R2-N01..N03` are consumed in canonical event-id order strictly above that watermark;
- source independence passes for all three fixed slots;
- `natural_source_binding_failure_count == 0`;
- zero material independent-review disagreements;
- zero authority violations;
- zero replacements/backfills;
- median treatment capture effort is at most 600 seconds;
- at least two of the three slots are non-D0 with definitive complete C/S/B/E/T bindings.

PASS establishes only tiny-sample prospective natural handling feasibility for the frozen S1-R2 + S0-R3 contracts.

### REJECT_THIS_REVISION

Reject on any pre-activation `activation_integrity_failure`, missed external-trigger deadline, controller-timed publication/review/merge after orchestration start, orchestration heartbeat gap above 5 seconds, snapshot-anchor elapsed time above 305 seconds, missing/restarted/replaced orchestration job, failed or repeated activation snapshot attempt, invalid/changed activation watermark, cross-system wall-clock substitution for the watermark, source-independence failure, binding/capture failure, material review disagreement, authority/integrity violation, sequence/backfill violation, or median effort above 600 seconds.

### INCONCLUSIVE

Use only when the activation checkpoint/watermark and all three fixed slots/source-independence gates are valid with zero failures, zero disagreements, zero authority/integrity violations, zero replacement/backfill and median effort at most 600 seconds, but fewer than two informative non-D0 definitive C/S/B/E/T cases occur.

Never backfill an inconclusive cohort.

## 11. Stop and non-promotion rules

Stop rather than widen the experiment if:

- the externally triggered orchestration job is not started within its frozen GitHub-server deadline and before author-head publication;
- the orchestration job cannot autonomously publish, request/reconcile review, merge the exact PR, or later terminates, loses monotonic heartbeat continuity or must be restarted before freezing its one allowed activation snapshot;
- the job reaches the post-integration snapshot anchor later than 305 monotonic seconds;
- the exact activation snapshot/high-water event id cannot be frozen from its single complete authoritative Bureau journal read;
- the complete normalized sequence cannot be proven;
- a frozen capture would need in-place rewriting;
- productive work would need to wait;
- technical truth would need to be copied instead of referenced;
- a new validator, production field, service or control plane is required;
- the observer would need productive authority to continue.

No result here can authorize P1 reopening, P2, P3, Minimal-versus-Full, automatic learning, Bureau schema changes, Grabowski runtime changes, routing, queue, policy, merge-policy or deployment changes.

Only a terminal PASS may justify a **separate small decision-impact pilot**. A REJECT or INCONCLUSIVE result remains terminal negative/limited evidence for this natural-activation revision.