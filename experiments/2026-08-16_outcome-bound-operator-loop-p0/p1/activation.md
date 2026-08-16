---
title: "Outcome-Bound Operator Loop P1 — Activation receipt"
status: testing
canonicality: operative
created: "2026-08-16"
updated: "2026-08-16"
triggered_by: "github:heimgewebe/vibe-lab#332; codex-review:heimgewebe/vibe-lab#333"
relations:
  - type: references
    target: cohort-protocol.v1.yml
  - type: references
    target: decision.yml
  - type: references
    target: ../method.md
  - type: references
    target: ../contracts/outcome-case-spec.v0.schema.json
  - type: references
    target: ../contracts/outcome-observation.v0.schema.json
---

# P1 activation receipt

P1 protocol revision 1 is frozen in `cohort-protocol.v1.yml`. This receipt
activates only prospective preparation for six natural two-stage full-form shadow
captures. All six slots, `P1-01` through `P1-06`, are **vacant**: **0/6 slots are
assigned**, no screening or form-outcome record exists, no case identity is
present and the activation supplies **zero outcome evidence**. No efficacy run
has occurred. These 0/6 and zero-record statements are the frozen activation
snapshot, not live active state. Mutable Stage A and Stage B progress remains
only in separate append-or-create-only capture records and is not mirrored into
this receipt or the current decision.

For each independently occurring eligible canonical Bureau intake, Stage A first
creates a separate append-or-create-only screening and slot-assignment record.
That record consumes the next ordered vacant slot before any full-form attempt
and binds the intake reference, slot, screening time and proof that productive
mutation had not begun. It neither requires nor contains a full-spec digest.
Successful full-form completion or freeze is not an eligibility condition.

Only after Stage A exists does Stage B attempt the full form in shadow. A complete
spec frozen before productive mutation produces the normal form outcome with its
reference, digest and freeze timing. If the form cannot be completed and frozen
before productive mutation would naturally begin, Stage B records
`form_completion_failed_or_not_frozen`, handling time, unclear or redundant
fields and a bounded reason, then stops P1 capture for that slot. Productive work
proceeds unchanged. The failed slot remains consumed and is never replaced or
backfilled.

The failure outcome is a P1 usability or observability finding only. It is not an
outcome-effect assessment, not minimal-versus-full evidence and not P3 efficacy
evidence. P1’s other observations remain subject to the same no-efficacy
boundary.

The activation and every future P1 artifact have zero authority over task
selection, execution, timing, routing, queues, priority, policy, merge,
deployment, technical closeout or productive integration. Screening and form
handling must never block, delay, reroute, reprioritize or otherwise alter
productive work.

The eventual closeout is a distinct artifact at `p1/closeout.md`; it does not
exist at activation. The current `p1/decision.yml` is an activation decision, not
that closeout. Even an independently reviewed closeout does not execute or
authorize P3: P3 additionally requires a separate execution authorization.
