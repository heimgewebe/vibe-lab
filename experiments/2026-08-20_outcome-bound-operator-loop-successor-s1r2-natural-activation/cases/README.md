# Fixed natural slots

No case in this directory exists before the activation boundary.

Only after the externally triggered controller orchestration job started within its frozen GitHub-server deadline **before author-head publication**, autonomously published the exact head, froze its base/head/canonical-diff tuple, obtained the required current-head Codex PASS and green CI, merged that exact PR on the first all-gates-PASS observation, verified exact merge identity, preserved monotonic heartbeat continuity with no gap above 5 seconds, and anchored its single complete authoritative Bureau SQLite journal snapshot in the closed 300–305 second post-integration window, does the frozen `activation_watermark_event_id` permit the complete S1-R2-normalized journal to fix exactly three ordinals.

The eligible sequence is the first three canonical Operator-Intake identity births whose exact `identity_first_event.event_id > activation_watermark_event_id`, sorted by that event id ascending:

- `S1R2-N01`
- `S1R2-N02`
- `S1R2-N03`

GitHub, local and Bureau wall-clock timestamps are descriptive evidence only. They never select, exclude, replace or reorder a slot. A missed external trigger deadline, any later controller-timed publication/review/merge, a heartbeat gap above 5 seconds, a snapshot anchor after 305 seconds, a restarted/replaced orchestration job or a later replacement snapshot cannot supply a valid watermark.

Each slot record is create-only and must preserve the fields required by `../method.md` section 5, including the frozen activation watermark and activation snapshot reference. A non-natural, missed, result-informed, D0 or otherwise inconvenient slot remains consumed. No replacement or backfill is permitted.

Corrections are append-only evidence records; never rewrite an earlier frozen capture to improve the result.