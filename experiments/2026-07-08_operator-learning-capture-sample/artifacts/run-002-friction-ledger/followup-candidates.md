---
title: "Follow-up Candidates — run-002 Friction Ledger"
status: active
canonicality: operative
updated: "2026-07-08"
---

# Follow-up Candidates (Proposal-Ready, Not Bureau Writes)

Per `docs/ecosystem/vibe-lab-productive-role.md`, Vibe-Lab **proposes** candidates and
**must not mutate Bureau queues**. This file is the proposal surface. Actual
registration into Bureau is a human/Operator decision. No Bureau write was performed
from Vibe-Lab in this run (deliberate boundary choice; see the closing note).

Each candidate carries: target repo/organ, suggested owner, evidence ref, and the
explicit claim boundary.

| # | Candidate | Suggested owner | Target repo/organ | Evidence ref | Boundary |
|---|-----------|-----------------|-------------------|--------------|----------|
| FUP-1 | Evaluate a narrower, typed, receipt-bound publish/merge surface so completed clean work can be landed without raw git/gh command strings that trip the safety filter. **Policy scope (if any auto-merge is ever allowed) stays a human decision.** | grabowski (+ human policy) | heimgewebe/grabowski | ledger P1: 15eac059, 267cf730, c6ebcdc7, b76fda53, 61654db6, f25644c5, 6a536fc8, ec080824 | belegt (pattern); owner = suggestion |
| FUP-2 | Reconcile the capability contract: enable `file_delete` or change `remove_path`/`restore_removed_path` so reversible-remove does not depend on an unavailable capability. Deterministic quick win. | grabowski | heimgewebe/grabowski | ledger P4: 8ad7833a, bdcbdb70 | belegt |
| FUP-3 | Restore the recovery/backup gate: reconnect rclone gdrive OAuth (stale backup) and stand up heimserver or the wg-prod-1 rest-server as a recovery target. Highest operational damage (silent backup loss). | operator / infra | heim-pc + heimserver + wg-prod-1 | ledger P5: 344a3108, e4623d1f, 309cb40a, 3b600b77 | belegt |
| FUP-4 | Fix rLens/RepoBrief context availability: run auth 401 and bundle discovery/registry path mismatch. | lenskit / rLens | (rLens/lenskit) | ledger P6: b312e8da, 9a4e4f4e | belegt |
| FUP-5 | Investigate platform-filter non-determinism on read-only inspection; prefer typed read tools meanwhile. | grabowski / operator | heimgewebe/grabowski | ledger P2: 8729a6c8, 64d7c608, 01aac3d3, f24796c5, c0b1809b, 098fae3d | belegt (blocked); root cause spekulativ |

## Deliberate boundary note

The task permitted registering Bureau follow-ups for non-implemented sensible points.
This run intentionally stops at **proposal-ready candidates in-repo** rather than
writing into Bureau, because:

1. `vibe-lab-productive-role.md` states Vibe-Lab must not mutate Bureau queues; it
   supplies candidates for Bureau to decide.
2. No Bureau write tool is available to Vibe-Lab in this role, and the ledger itself
   shows Bureau/queue writes are a friction surface — inventing one here would be both
   out-of-boundary and unreliable.

If Bureau registration is desired, the Operator can take these five rows as the input
set; each already has repo, suggested owner, and evidence ref.
