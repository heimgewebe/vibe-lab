# Post-finding orchestration proposal — historical, unexecuted

Date: 2026-08-20

Status: **design artifact only; never activated**

## Provenance

The official prospective registration remains `registration.v2.json` as frozen at author revision `d299357c15457994583e93a8608c7366897e84aa` (`registered_at: 2026-08-20T04:14:35Z`).

After current-head Codex finding `github:heimgewebe/vibe-lab#353:discussion_r3819573067` at `2026-08-20T07:42:09Z` exposed the material pre-arming selection window, later author work explored a repair in which that external finding would act as a work-blind trigger for a single controller-owned orchestration job.

This proposal was created **after** the material finding. It is therefore not part of the preregistered intervention and cannot be used as evidence that the rejected revision was prospectively selection-free.

## Proposed mechanism

The unexecuted design would have required one Bureau-blind orchestration job to:

1. start within a bounded GitHub-server-time window and before final author-head publication;
2. publish and bind one exact head/base/canonical-PR-diff tuple;
3. request and reconcile current-head review plus CI without later controller timing choice;
4. merge only the exact reviewed head with ordered merge-parent and tree identity checks;
5. preserve monotonic heartbeat continuity with no gap above 5 seconds;
6. anchor one and only one Bureau SQLite journal snapshot in the closed 300–305 second post-integration window;
7. use only the resulting immutable event-id watermark for later cohort membership.

## Terminal disposition

The proposal was **not executed**. No orchestration job, activation checkpoint, Bureau watermark or natural slot was created from it.

The experiment is terminally `REJECT_THIS_REVISION` because the preregistered d299 revision itself retained the material pre-arming selection degree of freedom. `results/decision.yml` and `results/preactivation-rejection.md` are the terminal result authority.

Any future attempt to test a work-blind activation mechanism requires a separately registered successor before eligible arrivals; this historical proposal grants no P2/P3, Minimal-versus-Full, routing, runtime, queue, merge-policy or production authority.
