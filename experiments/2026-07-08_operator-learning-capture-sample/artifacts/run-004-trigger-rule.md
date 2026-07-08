---
title: "run-004 Trigger Rule — Friction-Ledger Repeatability"
status: active
canonicality: operative
updated: "2026-07-08"
---

# run-004 Trigger Rule

run-004 is a **scheduled-but-not-yet-executed** repeatability run. This file is the
gate. run-004 **must not** start immediately after run-003, because a near-immediate
second snapshot only re-observes append-only persistence, not genuine recurrence
(see `run-003-friction-ledger-snapshot-2/pattern_stability.yml` → interval caveat).

## Baseline (from run-003, snapshot 2)

- `run-003 generated_at`: **2026-07-08T17:25Z**
- `unresolved_count` baseline: **35**
- run-003 unresolved event-id set: the 34 run-002 events
  (`run-002-friction-ledger/friction-events.jsonl`) **plus** `80ecf62307a54392aab8c7c5411ba331`.
- P1 (`clean_local_then_blocked_publish`) instance count baseline: **8**
  (member ids in `run-002-friction-ledger/pattern_candidates.yml` → P1).

## Start condition (run-004 may start if AT LEAST ONE holds)

Evaluate against a fresh `grabowski_friction_summary` snapshot.

1. **Interval** — `now − 2026-07-08T17:25Z ≥ 24h`
   (earliest: **2026-07-09T17:25Z**; better: after several real operator cycles).
2. **Ledger turnover** — any of:
   - **≥1** baseline unresolved event has become `resolved: true`; or
   - **≥3** new `decision_required` events beyond the baseline
     (i.e. `unresolved_count ≥ 38`, or ≥3 event-ids not in the run-003 set); or
   - **≥1 new P1 instance** — a new unresolved event with publish/merge/push/commit
     semantics beyond the baseline 8.
3. **Live recurrence** — a relevant publish/merge/push block occurs **live again**
   (a fresh `platform_filter` event on a push/merge/publish surface).

If none holds, **do not run run-004**; re-check later.

## run-004 goal (when triggered)

- Test **genuine re-observation**, not append-only persistence.
- **P1 upgrade only** if new independent instances appear (condition 2c or 3).
  Persistence alone never upgrades P1.
- Keep the verdict honest: persistence ≠ repeatability ≠ effectiveness.

## Explicit non-goals / boundaries

- No status upgrade, no usability → effectiveness upgrade.
- Do **not** build `operator-friction-capture-contract-v0` until real repeatability
  (condition 2 or 3) is observed across the run.
- No Bureau queue mutation; owners remain suggestions.
- **P12 is tracked separately** as a security follow-up
  (`heimgewebe/weltgewebe#1375`, JWT rotation). It is **not** a Vibe-Lab task and is
  **not** advanced or resolved by any run-004. Security rotation is Operator/privileged.
