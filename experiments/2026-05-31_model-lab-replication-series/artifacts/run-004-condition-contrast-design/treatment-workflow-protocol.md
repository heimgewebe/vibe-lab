# Run-004 workflow-instruction overlay — treatment

> Generated deterministically from workflow-instruction-protocol.yml by
> scripts/docmeta/render_condition_overlays.py. Do not edit by hand; the
> validator re-renders and asserts byte equality.

## Shared instruction surface (identical for both arms)
- language: en
- tone: neutral
- tool_hints: none_beyond_shared_benchmark
- permissions: bound_identically_at_execution_readiness
- examples: none
- motivation: none
- quality_rhetoric: none
- common_constraints:
  - Address the shared rest-api-v1 benchmark exactly as given.
  - Use only the tools and permissions bound identically for both arms at execution readiness.
  - Capture the same evidence required by the shared verification and measurement protocols.

## Assigned workflow protocol — treatment (the single primary axis)
- pre_implementation_specification_required: true
- implementation_may_begin_immediately: false
- specification_completeness_check_required: true
- required_specification_sections:
  - endpoint_matrix
  - request_response_schemas
  - validation_rules
  - http_status_codes
  - error_cases
  - edge_cases
  - persistence_assumptions
  - planned_implementation_order
