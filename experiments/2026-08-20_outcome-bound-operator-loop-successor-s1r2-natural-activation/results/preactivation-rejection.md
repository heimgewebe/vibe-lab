# S1-R2 natural activation — pre-activation rejection

Date: 2026-08-20

## Result

**REJECT_THIS_REVISION before activation.**

No natural slot was assigned or consumed. No Bureau activation watermark was created. P2, P3, Minimal-versus-Full and production integration remain unauthorized.

## Frozen author revision

- PR: `heimgewebe/vibe-lab#353`
- reviewed author head: `d299357c15457994583e93a8608c7366897e84aa`
- base: `5e49c38f522df43ca550ba0c908bec5d8a2c4418`
- canonical PR diff SHA-256: `11b83b92bb17b8e213bee8e3db375921808eeb9e0cc24a5dbd51d462ff6aa4bf`
- parent protocol head: `2435f70524190e2996febc033db10566e3ce60b0`
- `tree(d299357c…) == tree(2435f705…) == 2614fdf5898d224e86d6415bb1fce82784f6fa0f`
- S1-R2 imported method SHA-256: `19542aae0a473a8a7c63d24e3aa2909a8e115c50561bfeddd07893394d8003ab`
- S0-R3 imported protocol SHA-256: `f60b26a3bcc0f8f6b55f5b89a8d4dfdd1739017d8b228c5adaa82f5a292a30af`

The empty `d299357c…` rebind changed review identity but not protocol content.

## Material finding — pre-arming selection window

Current-head Codex review opened `PRRT_kwDOR8ZYIc6aujIL` / `discussion_r3819573067` with a P1 finding: the protocol forbids work-informed merge timing only **after** the activation checkpoint is armed. It does not freeze a work-blind trigger or bounded automatic deadline between final review completion, checkpoint arming and merge.

That is material under the preregistered rule. An independently planned Operator-Intake arrival can satisfy S1-R2 source independence while the controller still has advance knowledge of its timing. By delaying review finalization, arming or merge, the controller can change whether that arrival falls below or above the later activation watermark and therefore can change `S1R2-N01..N03` without changing the arrival itself.

This is a remaining activation/selection degree of freedom. The experiment's own falsification criterion says such a degree of freedom rejects before activation.

## Why this is not repaired again

A further protocol repair could add an external work-blind coordinator, absolute rendezvous, automatic review/arming/merge deadline, or a new timing-control surface. Doing that now would complete another part of the sampling contract after a material exact-head finding and would turn the feasibility test into another design-hardening loop.

S1-R2 section 4 already requires that the experiment must not time or delay candidate arrivals, and section 9 requires the natural successor to freeze its activation boundary before any eligible arrival. The present revision has not shown that the existing operator/controller arrangement can do this without a remaining selection degree of freedom.

The scientifically conservative result is therefore rejection, not another in-place activation repair.

## Scope of the conclusion

The rejection establishes only that this natural-activation revision did not achieve selection-free prospective admission. It does **not** refute S0-R3 Outcome Case semantics, the S1-R2 canonical identity rule, the natural-source counterfactual itself, or any Minimal-versus-Full efficacy hypothesis.

The following remain untested because activation never occurred:

- live natural-source evidence availability;
- prospective C/S/B/E/T/Q capture success;
- handling effort for three natural slots;
- informativeness of a three-slot cohort;
- decision impact of Outcome Case metadata.

## Required closeout

1. Preserve `d299357c…` and the Codex P1 as negative pre-activation evidence.
2. Consume zero natural slots and do not backfill anything.
3. Obtain one independent read-only closeout review of this rejection packet.
4. Merge only the negative experiment closeout; the merge must not be interpreted as activation authority.
5. Do not start P2/P3, Minimal-versus-Full or productive Bureau/Grabowski integration from this result.
6. A future natural-sampling successor, if ever justified, must be separately registered and must freeze a genuinely work-blind activation boundary before any eligible arrival rather than repairing this revision in place.
