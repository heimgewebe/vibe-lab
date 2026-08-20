# CONTEXT

This directory is the separate prospective natural-activation successor permitted by the terminal S1-R2 paper PASS.

Normative authorities are imported, not rewritten:

- S1-R2 sampling semantics: `../2026-08-18_outcome-bound-operator-loop-successor-s1r2-paper/method.md`, sections 2-5, SHA-256 `19542aae0a473a8a7c63d24e3aa2909a8e115c50561bfeddd07893394d8003ab`.
- S0-R3 Outcome Case semantics: `../2026-08-17_outcome-bound-operator-loop-successor-s0r3/protocol.md`, SHA-256 `f60b26a3bcc0f8f6b55f5b89a8d4dfdd1739017d8b228c5adaa82f5a292a30af`.
- S1-R2 terminal closeout is merged in PR #351 / main commit `21aee3c984b1a774498df1bcf72c459cd28dfcf0`.

The author branch is pre-activation. Only one exact author head on one exact base, bound to the canonical GitHub PR diff digest, may pass the independent pre-activation review gate. The review result stays outside the reviewed branch as a head/base/diff-bound terminal receipt; any content change, PR-head change, base change or canonical-diff change invalidates that review for merge. Integration can activate only when authoritative PR and Git evidence proves all of the following without substitution: the PR tip at merge is exactly the reviewed head, the PR base commit is exactly the reviewed base, the resulting `main` commit is a true merge commit whose first parent is that reviewed base and whose second parent is that reviewed head, the reviewed head is an ancestor of the merge commit, and the merge commit tree is exactly the reviewed-head tree. PR `MERGED` state, ancestry alone, tree equality alone, a later descendant tip, a changed base, or squash/rebase/cherry-pick/conflict-resolution content does not satisfy this gate. Any mismatch leaves `activation_at` undefined and terminally rejects the activation attempt. Only after that exact integration proof and the frozen five-minute cooling interval can the experiment-local read-only observer activate. It does not grant Bureau, Grabowski runtime, routing, queue, policy, merge-policy, deployment, P2/P3 or Minimal-versus-Full authority.

Case evidence is create-only after activation. No pre-activation Bureau event can be reused as a slot.