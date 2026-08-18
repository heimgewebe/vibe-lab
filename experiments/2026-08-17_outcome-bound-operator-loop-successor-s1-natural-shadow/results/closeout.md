# Outcome-Bound S1 — corrected pre-review closeout

## Status

This is an author/controller closeout packet, not the required independent exact-revision review. The corrected sequence consumes **S1-N01 only** and immediately hits the frozen reject threshold.

## What changed

A prior local draft treated Bureau events `8146`, `8147` and `8148` as three natural arrivals. That is not compatible with the preregistered watcher rule fixed before the qualifying arrival: all three belong to `SYSTEMKATALOG-DRIFT-CLOSED-LOOP-V1`, whose first canonical event is `302` from 13 July 2026. The prior files are preserved; their cohort assignments are superseded by `cases/S1-N01/identity-arrival-correction.yml` and the adjacent create-only draft-disposition records.

## Correct S1-N01

The first candidate identity whose first canonical `candidate_task` event occurs after activation is:

- Bureau event: `8166`
- created: `2026-08-18T05:33:32.623001Z`
- candidate: `candidate-c701b55e34cc9a6a9a6d6752`
- task: `BUREAU-CONTROL-PLANE-V3-T012`

Capture began at `2026-08-18T07:43:24Z`. Productive T012 activity predates capture:

- coordinated claim intent event `8220`: `2026-08-18T06:17:41.356320Z`;
- workspace created event `8223`: `2026-08-18T06:17:51.014271Z`;
- implementation commit `2fdba02d5e96646831f3dfd35665acfc3239b2c4`: `2026-08-18T06:49:24Z`.

Therefore S1-N01 is `capture_missed_before_mutation`. C/S/B/E/T/Q are not reconstructed. The slot is consumed, replacements/backfills remain zero, and S1 caused zero productive authority effects.

## Gate

`natural_case_binding_failure_count = 1`. Section 10 of the frozen S1 protocol therefore points mechanically to `REJECT_THIS_REVISION`. Section 11 stops further assignment immediately; N02 and N03 remain unassigned in the corrected cohort.

## Independent review still required

Before terminal result publication, an independent exact-revision reviewer must verify:

1. activation commit and timestamp;
2. first-event identity ordering and exclusion of old-identity supersessions;
3. that event `8166` is the first qualifying identity;
4. that productive T012 work predates capture;
5. that no C/S/B/E/T/Q reconstruction, replacement or backfill occurred;
6. zero S1 production-authority effects;
7. the mechanical reject threshold.

No P1 reopening, P2/P3, Minimal-versus-Full comparison, Bureau/Grabowski runtime change, routing, queue, policy, merge-policy or deployment authority follows from this result.