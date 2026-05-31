---
title: "Model-Lab Replication-Series — Failure Modes"
status: designed
canonicality: operative
---

# Model-Lab Replication-Series — Failure Modes

## When does this approach fail or mislead?

- **Pseudo-comparison without a control condition.** A single baseline run with
  no control run cannot support any comparative claim. `control_condition` is
  `future_control_pending` precisely to make this absence explicit.
- **Ambiguous challenge version.** If the challenge version is not pinned, later
  runs may silently target a different task. This series always references the
  exact `challenge_version: rest-api-v1`.
- **Missing evidence artifacts.** A run that claims results without resolvable,
  repo-local evidence artifacts is not trustworthy. Here the evidence pack only
  references artifacts that actually exist.
- **Self-report mistaken for external evidence.** `provenance_level` is
  `self_reported`; this is not independent verification and must not be read as
  external proof.
- **Skeleton mistaken for a result.** The structure existing does not mean a
  comparison happened. The verdict is `CLAIM_NOT_PROVEN` / `not_executed` and
  every artifact states `skeleton only` and `no outcome upgrade`.
- **Retroactive hardening of historical experiments.** AP-1/AP-2 are opt-in.
  This series must not be used as a pretext to make `model_lab_control` or
  `challenge_version` mandatory for existing historical runs or decisions.
