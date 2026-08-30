# Context

This experiment is the prospective activation successor to `2026-08-24_outcome-bound-natural-pilot-sampling-unit-r3-v3`. R3 v3 passed paper/adversarial exact-head qualification but explicitly took zero natural cases and authorized no pilot.

The activation keeps R3 v3 semantics unchanged and adds only: a post-merge Bureau marker whose numeric event id is A, fixed N=3, admission terminal states, the <=10 minute handling gate, and the mechanical PASS/REJECT/INCONCLUSIVE decision.

The Bureau activation read must explicitly report `coverage_complete=true` and `projection_source=complete_event_scan`. `history_truncated=true` is permitted only as a presentation property; it must never be misread as complete raw history. Birth proof remains the R3 v3 hard gate.

No pre-A event can become a slot. No Full Outcome Case, validator, routing, queue, runtime, policy, Chronik, Leitstand or product integration is authorized.
