# Fixed natural slots

No case in this directory exists before the activation boundary.

Only after the exact author base/head/canonical-PR-diff tuple passed repository validation and independent review, every decision-bound review was terminal/reconciled, exactly one read-only activation-checkpoint job was armed before merge, that same job verified the exact resulting merge identity, proved at least 300 seconds of post-integration monotonic cooling and succeeded on its single complete authoritative Bureau SQLite journal snapshot attempt, does the frozen `activation_watermark_event_id` permit the complete S1-R2-normalized journal to fix exactly three ordinals.

The eligible sequence is the first three canonical Operator-Intake identity births whose exact `identity_first_event.event_id > activation_watermark_event_id`, sorted by that event id ascending:

- `S1R2-N01`
- `S1R2-N02`
- `S1R2-N03`

GitHub, local and Bureau wall-clock timestamps are descriptive evidence only. They never select, exclude, replace or reorder a slot. A restarted/replaced checkpoint job or later replacement snapshot cannot supply a valid watermark.

Each slot record is create-only and must preserve the fields required by `../method.md` section 5, including the frozen activation watermark and activation snapshot reference. A non-natural, missed, result-informed, D0 or otherwise inconvenient slot remains consumed. No replacement or backfill is permitted.

Corrections are append-only evidence records; never rewrite an earlier frozen capture to improve the result.