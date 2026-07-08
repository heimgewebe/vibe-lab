---
title: "Result: Operator Learning Capture — run-002 Friction Ledger"
status: active
canonicality: operative
updated: "2026-07-08"
---

# Result — run-002 Friction Ledger

## Verdict

inconclusive_for_effectiveness / usability_signal_confirmed

This is a second run of the Operator Learning Capture Sample experiment. It does
**not** upgrade the experiment status, does not promote anything, and does not make
an effectiveness claim. It confirms that the Grabowski friction ledger is a usable,
higher-density evidence source than the PR-history sample of run-001.

## What was done

- Read the **live** ledger via `grabowski_friction_summary` (not the task summary).
- Verified the claimed numbers against the ledger's own aggregates: 39 events,
  **34 unresolved = 34 decision_required**; `failure_class` split
  platform_filter 20 / environment_tooling 6 / actionable_failure 4 / policy_gate 4.
  Self-consistent.
- Mapped all 34 unresolved decision_required events to evidence-bound rows
  (`friction-events.jsonl`) and aggregated them into 11 pattern candidates
  (`pattern_candidates.yml`).

## Strongest pattern (confirmed by live ledger)

**P1 — clean local work → publish/merge/push/land step blocked by the platform
safety filter.** 8 events: pushes (15eac059, 267cf730, c6ebcdc7, b76fda53),
merges (61654db6, f25644c5), a commit+push (6a536fc8), and a PR review-trigger
write (ec080824). Highest on frequency, repeatability, operational damage, owner
clarity, and in-boundary actionability. The task's expected top pattern is therefore
**adopted because the live ledger carries it**, not because the summary asserted it.

## Priority order (axes: frequency → repeatability → damage → owner clarity → actionability)

1. P1 clean-local → blocked publish/merge/push (8)
2. P2 read-only inspection intermittently blocked (6)
3. P3 write/edit + checkout-lifecycle blocked (5)
4. P4 capability mismatch: file_delete missing → remove_path unusable (2) — **quick win**
5. P5 recovery/backup gate fail-closed (4) — **highest operational damage**
6. P6 rLens context unavailable (2)
7. P7 connector tool snapshot lag (2)
8. P8 unbounded crash/core artifacts (2)
9. P9 task-reconcile credential false positive (1)
10. P10 runtime bootstrap gap (1)
11. P11 build/clean ownership + PATH (1)

Note: P4 and P5 rank below P1–P3 on the frequency axis but are called out because P4
is a deterministic, single-owner quick win and P5 is the highest operational-damage
cluster (silent loss of backups).

## Decision impact

The candidate next step named in the run-001 experiment result —
`operator-friction-capture-contract-v0` — is **reinforced, not yet adopted**. This run
shows the ledger already contains the structured signal such a contract would consume,
so a contract would formalize an existing feed rather than invent one.

Do **not** proceed yet with: pattern promotion, Bureau queue mutation, Leitstand
signals, Grabowski receipt implementation, or any publish/merge/deploy automation.

## Boundary / non-claims

- Read-only evidence aggregation. The ledger explicitly `does_not_establish` root
  cause, merge readiness, or policy exception; this run inherits that boundary.
- All suggested owners are **suggestions**, not directives. Vibe-Lab does not steer,
  merge, deploy, or mutate Bureau queues.
- No status upgrade, no promotion, no effectiveness claim. A single ledger snapshot is
  usability evidence, not effectiveness evidence.
- P1 does **not** claim the safety filter mis-fires, and this run builds **no** bypass
  of any publish/merge/deploy block. Blocks are documented as friction only.

## Evidence

- `friction-events.jsonl` — 34 unresolved events, one row each.
- `pattern_candidates.yml` — 11 aggregated patterns with priority axes and owners.
- `followup-candidates.md` — proposal-ready follow-up candidates (not Bureau writes).
- `run_meta.json`, `output.txt` — execution proof.
