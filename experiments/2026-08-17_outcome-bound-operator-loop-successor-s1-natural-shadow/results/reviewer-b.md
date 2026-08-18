---
title: "Outcome-Bound S1 — Independent sampling-integrity review"
status: rejected
canonicality: operative
created: "2026-08-18"
updated: "2026-08-18"
triggered_by: "github:heimgewebe/vibe-lab#347"
---

# Independent sampling-integrity review

## Review binding

- PR: `heimgewebe/vibe-lab#347`
- independently reviewed head: `ca7ba0970ce66b6915b8ff32ffa00ffa2e80cbec`
- provider: Grok
- requested model: `grok-4.5`
- exact-head external-review audit SHA-256: `878a6fd4a3328db63a5c89b30a54ad50a43e1556959ded51c9ed7238dc5b197e`
- frozen S1 method SHA-256: `3f8868f02d41c126911e7e13748ea844eb944acb9012e1cf558ce3ca2f03f852`

The review was read-only and advisory. It received the exact PR head and diff and
returned `NEEDS_CHANGE` with two findings. One finding is load-bearing for the S1
result; the other concerned a timing proof that is no longer part of the terminal
gate basis.

## Load-bearing finding: sampling frame was resolved too late

The reviewer found that the identity-first interpretation used to exclude Bureau
events `8146` through `8148` relied on an operator obligation created after those
events had already occurred. The reviewed diff did not demonstrate that
first-new-candidate-identity sampling was already frozen in the activation revision.
The later obligation therefore cannot retroactively choose that sampling unit.

Independent reread of the unchanged activation method confirms the underlying
problem: it speaks of the first three canonical Bureau `intakes` and `arrivals`,
ordered by event id, and separately requires a stable `candidate/event identity`,
but does not define whether successive events for one pre-existing candidate
identity are separate S1 arrivals. Choosing either event-arrival or unique-candidate
semantics after the arrivals is result-adjacent protocol completion rather than
application of a fully frozen sampling rule.

**Reviewer-B consequence:** the deterministic natural sample sequence is not
provable from the frozen S1 protocol. Section 11 therefore requires an integrity
stop, and section 10 requires `REJECT_THIS_REVISION` for the resulting integrity
violation.

## Non-load-bearing timing finding

The same review challenged a normalized implementation-commit timestamp used by the
later identity-first T012 interpretation. The terminal S1 result no longer depends
on T012, event `8166`, or any commit-before-capture ordering. Those artifacts remain
preserved as a non-endorsed intermediate interpretation and provide no current slot,
binding-failure or gate count.

## Review conclusion

- material findings relevant to terminal S1 result: **1**
- sample sequence reproducible from frozen protocol: **no**
- post-observation sampling completion permitted: **no**
- replacement/backfill performed: **no**
- S1 productive authority effect observed: **0**
- terminal gate: **`REJECT_THIS_REVISION`**

This rejects only the S1 natural-sampling revision. It does not establish Outcome
Case efficacy or inefficacy, does not reopen P1, and does not authorize P2, P3,
Minimal-versus-Full comparison or any production integration.
