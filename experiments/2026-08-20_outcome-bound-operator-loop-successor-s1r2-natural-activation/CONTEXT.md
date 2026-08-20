# CONTEXT

This directory is the separate prospective natural-activation successor permitted by the terminal S1-R2 paper PASS.

Normative authorities are imported, not rewritten:

- S1-R2 sampling semantics: `../2026-08-18_outcome-bound-operator-loop-successor-s1r2-paper/method.md`, sections 2-5, SHA-256 `19542aae0a473a8a7c63d24e3aa2909a8e115c50561bfeddd07893394d8003ab`.
- S0-R3 Outcome Case semantics: `../2026-08-17_outcome-bound-operator-loop-successor-s0r3/protocol.md`, SHA-256 `f60b26a3bcc0f8f6b55f5b89a8d4dfdd1739017d8b228c5adaa82f5a292a30af`.
- S1-R2 terminal closeout is merged in PR #351 / main commit `21aee3c984b1a774498df1bcf72c459cd28dfcf0`.

The author branch is pre-activation. Only an exact head that first passes the independent pre-activation review gate may be merged. The review result stays outside the reviewed branch as a head-bound terminal receipt; any content change after review invalidates that review for merge. Integration can activate only when authoritative Git commit-graph evidence proves that the exact reviewed author head is an ancestor of the resulting `main` merge commit; PR `MERGED` state or tree equality alone is insufficient. Squash/rebase/cherry-pick integration that loses the reviewed commit leaves `activation_at` undefined and terminally rejects the activation attempt. Only after the ancestry proof and frozen five-minute cooling interval can the experiment-local read-only observer activate. It does not grant Bureau, Grabowski runtime, routing, queue, policy, merge-policy, deployment, P2/P3 or Minimal-versus-Full authority.

Case evidence is create-only after activation. No pre-activation Bureau event can be reused as a slot.