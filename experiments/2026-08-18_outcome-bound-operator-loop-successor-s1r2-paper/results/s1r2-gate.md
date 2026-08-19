---
title: "Outcome-Bound S1-R2 — Paper gate"
status: testing
canonicality: operative
created: "2026-08-19"
updated: "2026-08-19"
triggered_by: "grabowski-job:1a00e6999ebc; grabowski-job:f2b7ea92892b; grabowski-job:3742d6127bc5; github:heimgewebe/vibe-lab#350"
---

# S1-R2 paper gate

## Frozen author revision

The frozen author revision is `e62e168bb97a5a70b95dac9585d6bde2833d0b8d`. Its method, registration and P01-P18 author dispositions remain immutable experiment input. The closeout author head `45de7247639edea002e9719c841834d25e2239fc` was separately frozen before the independent closeout judgment; this terminal record appends that result without rewriting either frozen input.

## Reviewer reconciliation

Four decision-bound reviewer attempts from the original paper gate are preserved:

1. Reviewer A initial (`57fb24176513`) failed before analysis with HTTP 529 and produced no semantic verdict.
2. Reviewer B initial (`674203b60055`) failed without substantive review output and produced no semantic verdict.
3. Reviewer B2 (`1a00e6999ebc`) completed successfully at `2026-08-18T16:45:55Z`: `PASS_THIS_REVISION`, 0 material findings.
4. Reviewer A2 (`f2b7ea92892b`) completed successfully at `2026-08-18T16:53:52Z`: `PASS_THIS_REVISION`, 0 material findings.

The two technical failures are not semantic REJECTs and cannot count toward the required reviewer denominator. They were terminally reconciled and replaced by fresh independent jobs rather than resumed or reviewer-shopped after a material finding.

Both valid reviewers were exact-head bound and independently reproduced **P01-P18: 18/18 MATCH, 0 DIFF**. Reviewer A2 could not independently query PR #350 or the pinned Bureau object during an external command outage, but it read the current Bureau source bytes and marked those checks unverified. Reviewer B2 independently verified that PR #350 pointed to the exact author head and that the relevant Bureau source file was byte-identical to the pinned authority commit. This closes the auxiliary binding gap without changing A2's independent semantic verdict.

Both valid reviews were terminal before PR #350 merged at `2026-08-18T17:10:10Z`.

P18's stronger requirement — that every decision-bound reviewer be explicitly read and reconciled by the controller before merge — is bound in `controller-reconciliation-attestation.md`. The contemporaneous controller report at `2026-08-18T17:16:21Z` states that all four reviewer attempts were terminal-read and reconciled before merge. The closeout reread all four archived job artifacts, GitHub merge truth and the lane-bound merge in Grabowski's verified audit chain. These sources are mutually consistent.

There was no dedicated 2026-08-18 machine receipt whose sole semantic was "controller read reviewer X". That limitation was presented unchanged to the independent closeout reviewer. The reviewer concluded that frozen section 7 requires the real reconciliation act, **not a particular receipt type**, and that the contemporaneous attestation corroborated by immutable primary evidence is sufficient under the frozen wording.

## Independent closeout review

The exact closeout author head `45de7247639edea002e9719c841834d25e2239fc` received a separate semantic red-team judgment through `grabowski-job-3742d6127bc5` / Grok `grok-4.5`.

Result: **`PASS_CLOSEOUT`**, material findings **0**.

The reviewer specifically accepted P18, classified the initial A/B attempts as technical no-verdict failures rather than adverse reviews, found no reviewer-shopping, accepted the frozen-semantics and authority boundaries, and identified no overclaim. Its receipt and exact evidence limitation are preserved in `closeout-review.md`.

## Gate result

**PASS_THIS_REVISION — TERMINAL PAPER PASS.**

Material sampling-contract disagreements: **0**.

| Frozen requirement | Finding |
| --- | --- |
| Two independent exact-head semantic reviews | PASS — A2 and B2 terminal on the frozen author head. |
| P01-P18 dispositions reproduced | PASS — 18/18 MATCH by both valid reviewers. |
| Canonical legacy identity escape | PASS — none found. |
| Naturalness/filter/backfill escape | PASS — none found. |
| P18 reviewer reconciliation | PASS — contemporaneous explicit controller attestation corroborated by job/GitHub/audit readback; independent closeout review accepted the missing dedicated read-receipt as non-material under frozen §7. |
| Independent closeout falsification | PASS — `PASS_CLOSEOUT`, 0 material findings on frozen closeout head `45de7247…`. |
| New production/control surface required | PASS — none required. |
| Productive authority effect | PASS — none. |

This establishes only that the corrected sampling contract and its closeout survived the bounded paper attack. It does **not** establish natural-case feasibility, capture timeliness, handling cost, Outcome Case efficacy or decision impact.

## Consequences

- S1 and S1-R1 remain rejected and immutable negative evidence.
- The S0-R3 C/S/B/E/T/Q semantics remain unchanged.
- No natural cohort is activated by this closeout.
- No old Bureau event may be retroactively assigned to a new natural cohort.
- No N01-N03 slot is consumed or backfilled here.
- No validator, Bureau field, service, runtime integration, routing effect, queue effect, policy effect, dashboard, confidence score or new control plane is justified.
- P2/P3 and Minimal-versus-Full remain unauthorized by this result.
- This terminal paper PASS may justify only a **separate prospective natural-activation revision** that freezes its own activation boundary and first-three sequence before any eligible arrival.

The next unresolved question is external validity: can the corrected rule bind the first three genuinely natural fixed slots prospectively and without material friction?