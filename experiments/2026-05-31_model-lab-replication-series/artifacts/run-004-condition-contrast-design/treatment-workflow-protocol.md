# Run-004 — Treatment Arm Workflow Protocol (`spec_first`)

> Frozen design artifact. Structurally parallel to the control workflow protocol. The
> **only** operative difference between the two protocols is the workflow-protocol
> section (§3). Every other section defers to the shared common condition. No run is
> executed here.

## 1. Scope

This protocol governs the **treatment** arm of the Run-004 condition contrast. Its role
is `treatment`; its workflow protocol is `spec_first`.

## 2. Inputs

The arm receives the shared task surface defined in `common-condition.md` — the
unmodified `rest-api-v1` challenge and nothing else. See common condition for inputs,
functional requirements, allowed context, and output expectation.

## 3. Workflow protocol (the single operative difference)

- The agent reads the `rest-api-v1` task and **must produce a complete structured
  specification before any implementation change**.
- **Implementation is forbidden until the specification artifact is complete.**
- `pre_implementation_specification_required: true`
- `implementation_may_begin_immediately: false`
- The required specification artifact must contain, at minimum, these verifiable
  sections (`required_specification_sections`):
  - `endpoint_matrix`
  - `request_response_schemas`
  - `validation_rules`
  - `http_status_codes`
  - `error_cases`
  - `edge_cases`
  - `persistence_assumptions`
  - `planned_implementation_order`
- Only after this artifact is complete may implementation begin in the later run.

## 4. Permitted tools and permissions

Identical to the control arm. Bound from a single shared source at execution-readiness
time; see `common-condition.md`.

## 5. Intervention and stop rules

Identical to the control arm (`intervention_profile:
shared-intervention-and-stop-rules-v1`); see `common-condition.md`.

## 6. Evidence to capture

Identical to the control arm; see `common-condition.md` and the shared
`verification-protocol.yml` / `measurement-protocol.yml`.

## 7. What this arm does not decide

- It does not execute a run, bind runtime values, or assert any result.
- It does not claim that spec-first is better or worse than direct implementation.
