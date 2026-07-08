---
title: "Result: Operator Learning Capture — run-003 Repeatability Probe"
status: active
canonicality: operative
updated: "2026-07-08"
---

# Result — run-003 Repeatability Probe (Second Friction-Ledger Snapshot)

## Verdict

repeatability_inconclusive

This is a repeatability probe, not an effectiveness claim and not a status upgrade.

## What was done

- Took a second live snapshot of the Grabowski friction ledger via
  `grabowski_friction_summary`.
- Compared it against the run-002 snapshot: which pattern candidates recur, which are
  new, which dropped.

## Snapshot delta

| | snapshot 1 (run-002) | snapshot 2 (run-003) |
|---|---|---|
| events | 39 | 40 |
| unresolved | 34 | 35 |
| decision_required | 34 | 35 |
| policy_gate (unresolved) | 4 | 5 |

- **Persisted:** all 34 run-002 unresolved events are still present and unresolved.
- **Resolved since run-002:** 0.
- **New unresolved:** 1 — `80ecf623…` (weltgewebe #1370 SMTP gate + an unredacted JWT
  secret exposed in tool output → rotation needed).
- **Dropped:** none.

## Central caveat (anti-overclaiming)

The two snapshots are **minutes apart** and the ledger is **append-only**: unresolved
events do not disappear. So the persistence of the 34 events is **mechanically
trivial** and is **not** independent re-observation. **Persistence ≠ repeatability.**
In particular, the dominant pattern **P1 (clean local → blocked publish/merge/push)
gained zero new instances** — it merely persisted.

## Stability per pattern

- P1–P11 (run-002): `presence = persisted`, `repeatability_verdict = inconclusive`.
  None falsified, none independently re-observed.
- **P12 (new):** `production_secret_gate_and_exposure` — a fail-closed production gate
  plus an accidental unredacted JWT-secret exposure. Security-relevant, single
  observation. Suggested owner: operator/privileged (SMTP injection + JWT rotation).
  Vibe-Lab documents only; it does not rotate secrets or perform privileged injection.

## Decision impact

- **Repeatability is not established.** Do **not** build
  `operator-friction-capture-contract-v0` on this evidence alone.
- Do **not** upgrade usability → effectiveness.
- Next lever: a later snapshot taken after a materially longer interval and/or after
  some events resolve, so that fresh P1 instances and event turnover can be observed
  rather than mere persistence.

## Boundary / non-claims

- Read-only evidence aggregation; owners are suggestions; no steering, no Bureau
  mutation, no publish/merge/deploy automation or bypass.
- No status upgrade, no promotion, no effectiveness claim.
- The new security-relevant event is documented, not acted upon by Vibe-Lab.

## Evidence

- `pattern_stability.yml` — full per-pattern stability, delta, and caveats.
- `snapshot-2-new-events.jsonl` — the one new unresolved event.
- `run_meta.json`, `output.txt` — execution proof.
- run-002 baseline: `../run-002-friction-ledger/`.
