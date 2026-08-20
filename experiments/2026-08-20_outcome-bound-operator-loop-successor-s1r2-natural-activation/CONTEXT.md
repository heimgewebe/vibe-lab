# CONTEXT

This directory is the separate prospective natural-activation successor permitted by the terminal S1-R2 paper PASS.

Normative authorities are imported, not rewritten:

- S1-R2 sampling semantics: `../2026-08-18_outcome-bound-operator-loop-successor-s1r2-paper/method.md`, sections 2-5, SHA-256 `19542aae0a473a8a7c63d24e3aa2909a8e115c50561bfeddd07893394d8003ab`.
- S0-R3 Outcome Case semantics: `../2026-08-17_outcome-bound-operator-loop-successor-s0r3/protocol.md`, SHA-256 `f60b26a3bcc0f8f6b55f5b89a8d4dfdd1739017d8b228c5adaa82f5a292a30af`.
- S1-R2 terminal closeout is merged in PR #351 / main commit `21aee3c984b1a774498df1bcf72c459cd28dfcf0`.

The author branch is pre-activation. Only one exact author head on one exact base, bound to the canonical GitHub PR diff digest, may pass the independent pre-activation review gate. The review result stays outside the reviewed branch as a head/base/diff-bound terminal receipt; any content change, PR-head change, base change or canonical-diff change invalidates that review for merge. Before merge dispatch, exactly one read-only activation-checkpoint job must be armed against that reviewed tuple. The same job waits for and verifies the exact merge identity, then maintains a monotonic heartbeat with no gap above 5 seconds while cooling. Its single authoritative Bureau SQLite snapshot must be anchored in the closed 300–305 second post-integration window. If the job is descheduled, blocked or otherwise loses continuity past that bound, activation fails before any journal read; a later snapshot cannot move the cutoff. The job may not inspect Bureau candidate/journal content before the snapshot and may not be restarted or replaced. Only identity births strictly above the resulting immutable event-id watermark are post-activation candidates. GitHub and Bureau wall-clock timestamps are descriptive only and never select a slot. Any merge-identity, checkpoint-continuity, bounded-cooling or journal-watermark failure leaves the cohort inactive, consumes zero slots and terminally rejects the activation attempt. The experiment creates no Bureau, Grabowski runtime, routing, queue, policy, merge-policy, deployment, P2/P3 or Minimal-versus-Full authority.

Case evidence is create-only after activation. No Bureau event at or below the activation watermark can be reused as a slot.