# Outcome-Bound sampling-unit R3 v3 — one-slot invariant with exact-head CI fixpoint

R3 v3 is a separate successor to rejected R3 v2 author head `8fca4c7188792a66c7abdaba9dbe6828b7e7b3eb` / PR #357 and rejected R3 v1 `84ec97c7b76609fa5ef04ccc744de0a030dd8714` / PR #356. Both predecessors remain frozen negative evidence and are not repaired in place.

The one-slot semantics are unchanged from v2 and already survived independent exact-head review: every fully provable post-`A` `candidate_identity_birth` creates exactly one fixed ordinal before naturalness or self-interference; experiment influence consumes that one slot and contributes zero accepted natural evidence. Zero-slot and one-slot-plus-natural-acceptance readings are both forbidden.

R3 v2 was nevertheless rejected because exact-head repository CI exposed revision-specific generated drift in `docs/_generated/promotion-readiness.json` before replay mutation guard. R3 v3 therefore strengthens the freeze discipline: the canonical generated document index and promotion-readiness projection are produced before candidate commit; then the exact candidate commit is checked in a detached worktree with the CI validation prefix `validate-core`, `validate-active`, `validate-legacy`. The candidate is eligible to become the frozen author head only if that prefix succeeds **and leaves the tree clean**, followed by a green replay-mutation guard.

The author revision remains prospective: every counter-hypothesis is `pending` / `not_checked` until an independent reviewer inspects the exact frozen head. A rejected frozen revision is never repaired in place.

This remains paper- and adversarial-only. It chooses neither activation boundary `A` nor target `N`, observes no natural candidate, activates no Natural Pilot, and grants no runtime, routing, queue, policy, deployment, merge-policy, Chronik, Leitstand or product authority. A later Natural-Pilot activation still requires a separate revision-bound, explicitly completeness-reporting Bureau event-journal receipt; a truncated live-register projection is insufficient.
