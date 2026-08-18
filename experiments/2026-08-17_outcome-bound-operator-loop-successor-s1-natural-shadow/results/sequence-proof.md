# S1 identity-arrival sequence correction

## Authority

Activation is fixed at merge commit `5f12ef5bc2a59459ee11b71fd4f8bd434e4386f1` and `2026-08-17T21:07:25Z`. The durable operator preregistration `goo-outcome-bound-s1-n01-first-natural-intake-20260818`, created at `2026-08-18T05:25:06.910865Z`, fixes the watcher rule before the first qualifying identity arrived: only a candidate identity whose **first** canonical `candidate_task` event is after activation can consume S1-N01.

## Excluded supersessions

`SYSTEMKATALOG-DRIFT-CLOSED-LOOP-V1` first entered the canonical live register at event `302` on `2026-07-13T06:19:53.261891Z`. Its post-activation events `8146` through `8153`, plus later `8192` and `8240`, are supersessions of that preexisting identity. They are therefore not new S1 arrivals under the preregistered watcher rule.

The local draft commit `84e5fbd740266a744f7272dfde759c909ae34fc4` assigned events `8146/8147/8148` to S1-N01..N03. Those files remain preserved as draft evidence, but the assignments are not endorsed.

## First qualifying identity

| slot | event | created at | candidate identity | task | result |
| --- | ---: | --- | --- | --- | --- |
| S1-N01 | 8166 | 2026-08-18T05:33:32.623001Z | `candidate-c701b55e34cc9a6a9a6d6752` | `BUREAU-CONTROL-PLANE-V3-T012` | `capture_missed_before_mutation` |

At capture start `2026-08-18T07:43:24Z`, productive T012 work had already begun: coordinated claim intent event `8220` was recorded at `06:17:41Z`, workspace creation event `8223` at `06:17:51Z`, and implementation commit `2fdba02d5e96646831f3dfd35665acfc3239b2c4` existed before capture. Consequently C/S/B/E/T/Q are intentionally left unbound rather than reconstructed.

## Stop rule

S1-N01 permanently consumes the first slot as one natural-case binding failure. The preregistered stop rule applies immediately. N02 and N03 are not assigned in the corrected cohort; there is no replacement or backfill. The frozen gate points to `REJECT_THIS_REVISION`, subject to the required independent exact-revision review.
