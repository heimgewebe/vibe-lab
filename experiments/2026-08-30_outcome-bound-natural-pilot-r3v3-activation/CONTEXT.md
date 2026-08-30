# Context

This experiment is the prospective activation successor to `2026-08-24_outcome-bound-natural-pilot-sampling-unit-r3-v3`. R3 v3 passed paper/adversarial exact-head qualification but explicitly took zero natural cases and authorized no pilot.

The successor keeps R3 v3 sampling semantics unchanged. Before A it is registered in `experiments/active.v1.json` as `testing` with `execution_status: designed` and a `results/decision.yml` verdict of `not_executed`, so lifecycle visibility and review-date enforcement exist without fabricating a natural run. The prospective cohort itself begins only at the separate post-merge Bureau marker whose numeric event id is A.

The frozen protocol adds fixed N=3, exhaustive admission-terminal-state to `binding_failure_count`/verdict mapping, fixed monotonic handling-time boundaries, and the mechanical PASS/REJECT/INCONCLUSIVE decision.

The Bureau activation read must explicitly report `coverage_complete=true` and `projection_source=complete_event_scan`. `history_truncated=true` is permitted only as a presentation property; it must never be misread as complete raw history. Birth proof remains the R3 v3 hard gate.

No pre-A event can become a slot. No Full Outcome Case, validator, routing, queue, runtime, policy, Chronik, Leitstand or product integration is authorized.
