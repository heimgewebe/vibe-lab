---
title: "Outcome-Bound S1-R2 — Independent Reviewer A2"
status: testing
canonicality: operative
created: "2026-08-19"
updated: "2026-08-19"
triggered_by: "grabowski-job:f2b7ea92892b"
---

# Independent Reviewer A2

## Binding

- frozen author head: `e62e168bb97a5a70b95dac9585d6bde2833d0b8d`
- worktree: clean and exact-head bound
- job: `grabowski-job-f2b7ea92892b`
- finalization receipt SHA-256: `301d488ddf15523e29473e0c9faf3e9d7e52af79e182426b756a501272846012`
- stdout SHA-256: `1b8913b3fd3c53c62bde87a25dca3d316a3a0b28fadeaa083adb11cd55724d21`
- terminal at: `2026-08-18T16:53:52Z`

The reviewer could not independently query PR #350 `headRefOid` or read the pinned Bureau commit because its external command surface was temporarily overloaded. It did verify the exact frozen author head and clean worktree, read the then-current Bureau `live_register.py` bytes directly, and explicitly marked the two external binding checks as unverified rather than assuming them. Reviewer B2 later proved that the same Bureau file was byte-identical to the pinned commit and that PR #350 pointed at this exact author head.

## Verdict

**PASS_THIS_REVISION**

Material findings: **0**.

## Independent P01-P18 classifications

| ID | Derived disposition | Result |
| --- | --- | --- |
| P01 | `preexisting_identity_no_unit` | MATCH |
| P02 | `fixed_slot_requires_naturalness_check` | MATCH |
| P03 | `fixed_slot_requires_naturalness_check` | MATCH |
| P04 | `preexisting_identity_no_unit` | MATCH |
| P05 | `preexisting_identity_no_unit` | MATCH |
| P06 | `one_identity_one_slot` | MATCH |
| P07 | `preexisting_identity_no_unit` | MATCH |
| P08 | `source_independence_failure_reject` | MATCH |
| P09 | `naturalness_established_for_fixed_slot` | MATCH |
| P10 | `source_independence_failure_reject` | MATCH |
| P11 | `integrity_failure_reject` | MATCH |
| P12 | `naturalness_may_still_be_established` | MATCH |
| P13 | `same_fixed_slot_original_claim_anchor` | MATCH |
| P14 | `slot_kept_no_backfill` | MATCH |
| P15 | `slot_kept_capture_failure` | MATCH |
| P16 | `slot_kept_result_informed_failure` | MATCH |
| P17 | `event_700_before_event_701` | MATCH |
| P18 | `merge_blocked_until_reconciled_then_reject` | MATCH |

Total: **18/18 MATCH, 0 DIFF**.

## Adversarial findings

The reviewer found no protocol-conforming escape that hides a legacy no-ID root, turns later intake enrichment into a new identity birth, manufactures and then filters an experiment-caused candidate, skips a causally ambiguous slot, rebases a correction into the claim snapshot, or uses D0/missed/result-known state as a selection filter.

The fixed ordinal sequence is established before naturalness. Experiment-caused or causally unprovable arrivals consume their fixed slot and reject the future natural revision instead of being skipped or backfilled.

P18 is unambiguous: all decision-bound reviewer jobs must be reconciled; one material REJECT wins over any PASS. No majority, last-read or reviewer-shopping escape remains.

## Authority and non-claims

The paper contract needs no production field, validator, service or control plane. It creates no natural activation, no N01-N03, no capture metric, no P2/P3, no Minimal-versus-Full comparison and no Bureau/Grabowski runtime, queue, routing, policy, merge-policy or deployment authority.

This review establishes paper-level semantic stability only. It does not establish natural-case observability, handling feasibility, Outcome Case efficacy or decision impact.
