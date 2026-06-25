---
title: "Model-Lab Replication-Series — Method"
status: designed
triggered_by: "user-request-2026-06-06-run-003-semantic-rework"
canonicality: operative
relations:
  - type: references
    target: "artifacts/run-003-rest-api-independent-model-or-tool-condition/condition-input.md"
  - type: references
    target: "artifacts/run-003-rest-api-independent-model-or-tool-condition/run-output.md"
---

# Model-Lab Replication-Series — Method

## Shape of the series

The series grows one run at a time under the fixed challenge `rest-api-v1`.

- Run-001 is the executed `spec_first_baseline`.
- Run-002 is the executed `code_first_control`.
- Run-003 is executed under the retained label `independent_model_or_tool_condition`; its independence is only `self_reported_different_agent_tool_context`, with `external_attestation: false`.
- All three have separate runtime-validation artifacts. Run-003 has `validation_status: partial`.

These surfaces support structural comparison work only. They do not establish model quality, comparative superiority, a condition effect, outcome upgrade, adoption, promotion, production readiness, or security readiness. Formal assessment remains separate and blocked.

## Historical execution surfaces

### Run-001

Run-001 executes the baseline challenge repo-locally and archives its implementation, verification specification, execution output, changed files, and timing. `run_meta.json` opts into Model-Lab control semantics; `results/decision.yml` references `rest-api-v1`.

### Run-002

Run-002 executes the same challenge under `code_first_control`. Its `comparability.yml` references Run-001 and records `comparable_surface_available`, but comparison remains deferred.

### Run-003

Run-003 executes the same challenge in a separately reported agent/tool/session context. Its concrete boundary is recorded in `artifacts/run-003-rest-api-independent-model-or-tool-condition/condition-input.md`. The label does not prove model independence. Runtime validation is archived separately under `artifacts/runtime-validation-run-003/`.

## Measurement status

The series records execution completeness, artifact locators, verification evidence, and the availability of a comparison surface. It does not perform model comparison inside the run bundles.

Current status:

```text
executed_three_surface_run003_runtime_validation_partial
```

Runtime validation is a prerequisite for later assessment, not an assessment result.

## Methodological strength

The existing three-run surface provides weak structural control. Run-001 and Run-002 differ in more than a fully isolated experimental treatment, and Run-003 adds only self-reported context separation. Comparative claims therefore remain blocked.

## Condition-contrast design gate

`results/condition-contrast-design-gate.yml` defines the criteria for a stronger future contrast. It permits a separate Run-004 design task but does not authorize execution or assessment and does not close `weak_condition_contrast`.

## Run-004 condition design

A frozen, not-executed condition design exists under `artifacts/run-004-condition-contrast-design/`.

### Primary axis and arms

The single primary axis is `workflow_protocol` with semantics `assigned_instruction_requirement`.

- Control receives the neutral baseline without an assigned upfront-specification requirement.
- Treatment receives the same baseline plus a positive Spec-First workflow requirement grounded in the frozen snapshot of `instruction-blocks/spec-first.md`.

The design varies an assigned instruction, not an inaccessible internal thought process. Assigned condition and later observed compliance remain separate; contamination and ordering evidence must be collected in a future execution.

### Blinded deterministic delivery

The delivered prompt consists of the frozen benchmark, shared condition, and arm overlay in the same fixed order for both arms. Role names, axis names, hypotheses, and experiment framing remain outside the delivered text.

`common-condition.md` and both overlays are rendered from `workflow-instruction-protocol.yml` and byte-checked. The treatment grounding is re-derived from the frozen Spec-First snapshot. Delivered files must be UTF-8 with LF line endings and a final newline.

### Honest bundled prompt scope

The intervention is the complete treatment-only workflow-instruction bundle, not an isolated sentence. It includes:

- the preimplementation specification requirement;
- implementation ordering and completeness review;
- formal specification-format and explicit constraint examples;
- prompt length and internal structure;
- directive strength and motivational or efficacy framing;
- required specification sections.

A later observation may be attributed only to this complete bundle. It may not be attributed to an individual component or to the canonical Spec-First text alone.

Only these prompt surfaces are declared constant across arms:

- language;
- permissions;
- composition order;
- benchmark;
- shared condition.

Runtime dimensions such as model identity, tooling, sampling, dependency/runtime environment, harness, session isolation, and human-intervention rules remain unbound until a separate execution-readiness step and must then be bound equivalently across arms.

### Permanent historical provenance

Gate, readiness, challenge, and Spec-First preconditions are frozen as byte snapshots. On every validation, the validator reads the historical Git object at each declared `source_commit_sha:source_path` and requires byte equality with the snapshot.

A missing commit, unavailable object store, missing historical path, or byte mismatch fails closed. Full Git history is therefore part of the CI verification surface. Mutable working-tree files are not treated as provenance.

The validator also derives required dimensions and confounders from the frozen full gate rather than trusting an editable reduced list.

### Freeze and current boundary

The design bundle is closed and frozen with SHA-256 values before execution. The manifest excludes itself and contains no final commit, tree, or head identity.

No Run-004 arm has been executed. Runtime is unbound. No measurements, compliance observations, result assessment, model judgment, or condition effect exist. `weak_condition_contrast` remains open and `comparison_ready` remains false.

The only permitted next step is a separate execution-readiness and authorization check.

## Next extension

Later work may assess execution readiness, bind identical runtime values, and declare execution order. It must remain separate from the design and must not infer assessment readiness from the existence of the frozen bundle.
