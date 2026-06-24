# Run-004 — Shared Condition (one assembly component)

> Frozen design artifact. This is the **shared_condition** component of the input assembly.
> It is NOT the only input: the assembled input for each arm is, in order, the frozen
> benchmark text, then this shared condition, then the arm's workflow-instruction overlay
> (see `condition-design.yml -> condition_input_assembly`). Both arms receive the same
> benchmark and the same shared condition; they differ only in the assigned workflow overlay.
> This describes a paired design only; no run is executed and no result is asserted.

## Identical inputs (both arms)

- The same frozen `rest-api-v1` benchmark text (`source-snapshots/rest-api-v1.md`).
- This same shared condition text.
- They differ only in the assigned workflow-instruction overlay (the single primary axis).

## Identical functional requirements and acceptance

- The functional API surface and acceptance surface required by `rest-api-v1` are identical
  for both arms and are held unchanged.

## Identical tools, permissions, interventions

- Tooling, agent mode, and permissions are identical for both arms and are bound from a
  single shared source at execution-readiness time (not in this design).
- Human-intervention, retry, and stop rules are **not bound in this design**. They must be
  bound once, from one shared execution-readiness source, and applied identically to both
  arms before any execution authorization. No asymmetric intervention is permitted.

## Output artifacts (not all identical)

- **Common outcome artifacts** (both arms): the implementation plus the shared verification
  and measurement evidence.
- **Arm-specific process artifacts**: the treatment arm additionally produces a
  pre-implementation specification. This specification is part of the intervention and is
  **not** scored as an outcome.

## Identical evidence requirements

- Both arms capture the same provenance and evidence per the shared verification and
  measurement protocols. Contrast is never manufactured through different evidence handling.

## What this file does not decide

- It does not execute either arm, bind concrete runtime values, or authorize a result
  assessment.
