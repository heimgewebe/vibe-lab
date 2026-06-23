# Run-004 — Control Arm Workflow Protocol (`direct_implementation`)

> Frozen design artifact. Structurally parallel to the treatment workflow protocol. The
> **only** operative difference between the two protocols is the workflow-protocol
> section (§3). Every other section defers to the shared common condition. No run is
> executed here.

## 1. Scope

This protocol governs the **control** arm of the Run-004 condition contrast. Its role is
`control`; its workflow protocol is `direct_implementation`.

## 2. Inputs

The arm receives the shared task surface defined in `common-condition.md` — the
unmodified `rest-api-v1` challenge and nothing else. See common condition for inputs,
functional requirements, allowed context, and output expectation.

## 3. Workflow protocol (the single operative difference)

- The agent reads the `rest-api-v1` task and **may begin implementation immediately**.
- **No formal upfront specification artifact is required** before implementation.
- `pre_implementation_specification_required: false`
- `implementation_may_begin_immediately: true`
- The agent may, of course, think; the protocol simply imposes **no required
  pre-implementation specification gate**. There is no required specification artifact
  and no required specification structure for this arm.

## 4. Permitted tools and permissions

Identical to the treatment arm. Bound from a single shared source at execution-readiness
time; see `common-condition.md`.

## 5. Intervention and stop rules

Identical to the treatment arm (`intervention_profile:
shared-intervention-and-stop-rules-v1`); see `common-condition.md`.

## 6. Evidence to capture

Identical to the treatment arm; see `common-condition.md` and the shared
`verification-protocol.yml` / `measurement-protocol.yml`.

## 7. What this arm does not decide

- It does not execute a run, bind runtime values, or assert any result.
- It does not claim that direct implementation is better or worse than spec-first.
