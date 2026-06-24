# Run-004 — Common Condition (shared task surface)

> Frozen design artifact. This file defines the task surface that is **identical for
> both future arms** (control and treatment). It describes a paired design only; no run
> is executed, no runtime environment is bound, and no result is asserted. Both arms
> read this same file; nothing here is arm-dependent.

## Challenge

- Challenge: `rest-api` at `challenge_version: rest-api-v1`.
- The challenge contract is the existing `rest-api-v1` surface used by Run-001/002/003.
  It is held unchanged; no requirement is added, removed, or reworded for either arm.

## Identical input

- Both arms receive the unmodified `rest-api-v1` challenge text as their only task input.
- No arm receives extra hints, examples, encouragement, quality rhetoric, or additional
  background. Any such addition would be a confounder and is forbidden.

## Identical functional requirements

- The functional API surface required by `rest-api-v1` (endpoints, validation, status
  codes, error envelope, pagination, persistence behaviour) is identical for both arms.
- The acceptance surface is identical for both arms.

## Identical allowed context

- The repository start state, available files, and reference material are identical.
- The allowed working context (what the agent may read and edit) is identical.

## Identical output expectation

- Each arm must produce a working `rest-api-v1` implementation in the same target shape
  expected by the shared verification protocol.
- The expected output artifacts (implementation plus whatever the verification protocol
  consumes) are the same for both arms.

## Identical tool and permission limits

- Tooling, agent mode, and permissions are identical for both arms and are bound from a
  single shared source at execution-readiness time (not in this design).
- No arm may use a tool or permission the other arm cannot.

## Identical intervention rules

- Human intervention, correction, and rework rules are identical for both arms
  (`intervention_profile: shared-intervention-and-stop-rules-v1`).
- The same retry and abort rules apply to both arms.

## Identical stop rules

- The same stop conditions apply to both arms (e.g. time/resource limits bound from a
  single shared source at execution-readiness time, identical for both arms).
- An arm that hits a stop rule is recorded as such by the shared measurement protocol;
  the stop rules themselves do not differ between arms.

## Identical evidence requirements

- Both arms capture the same provenance and evidence (run metadata, command, exit
  status, produced artifacts) per the shared verification and measurement protocols.
- Evidence capture is equivalent across arms; contrast is never manufactured through
  different evidence handling.

## What this file does not decide

- It does not execute either arm.
- It does not bind concrete runtime values (model, tool, sampling, dependencies,
  environment, time/resource limits); those are deferred to a separate
  execution-readiness step and must be bound identically across arms from a single
  source.
- It does not authorize a result assessment or a comparison.
