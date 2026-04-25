---
status: derived
canonicality: derived
authority: historical_record
note: "Reconciliation note for the v1→v2 generated-artifact contract concept break. Does not modify historical evidence."
---

# Generated-Artifact Contract — v1 → v2 Reconciliation

This note explains how to interpret the legacy bucket labels used by the
historical experiment runs in this folder against the current object-based
generated-artifact contract (`schema_version: "2.0.0"` in
`.vibe/generated-artifacts.yml`).

## Historical labels (v1)

The original experiment validated the **bucket-based** generated-artifact
contract. It used these top-level groups:

- `canonical`
- `derived`
- `gated`
- `exports`
- `ephemeral`

Each group was a list of paths plus group-level `commit_policy` and
`ci_policy` attributes. The historical evidence captured by the runs in
this experiment (`evidence.jsonl`, `result.md`, `decision.yml`, run logs)
references these labels.

## Current model (v2)

The bucket grouping has been replaced by **explicit per-artifact objects**
with the following fields:

- `path`, `class`, `authority`, `origin`, `lifecycle`
- `enforcement` (list, must include `no_manual_edit` unless explicitly justified)
- `activation`, `commit_policy`, `ci_policy`
- For `class: generated_projection`: `generator`, `derives_from`,
  `target_surface`, `deterministic: true`, `regenerable: true`

Approximate v1 → v2 mapping (descriptive, not normative):

| v1 bucket   | v2 class(es)                                | v2 ci_policy / activation         |
| ----------- | ------------------------------------------- | --------------------------------- |
| canonical   | `generated_index`                           | `ci_policy: blocking`             |
| derived     | `diagnostic_report`, `diagnostic_dry_run`   | `ci_policy: non_blocking`         |
| gated       | `metric_report`                             | `ci_policy: best_effort`, `activation: gated` |
| exports     | `generated_projection`                      | `ci_policy: blocking`             |
| ephemeral   | `ephemeral_trace`                           | `ci_policy: non_blocking`         |

This mapping is approximate and is provided only to help readers understand
historical artefacts. It is **not** a substitute for the v2 contract.

## What this means for evidence

- **Historical metrics remain valid for their original contract version.**
  The evidence captured under the v1 bucket model continues to describe
  what was true at the time of those runs. It is not retroactively
  recomputed against v2.
- **Historical claims are not rewritten.** Existing entries in
  `results/evidence.jsonl`, `results/result.md`,
  `results/cross-run-assessment.md`, `results/decision.yml`, and the
  per-run artifact directories under `artifacts/run-*/` continue to refer
  to the v1 bucket labels they were captured against. No evidence files
  have been edited as part of the v1→v2 migration.
- **New diagnostics must use v2 fields.** Any newly captured evidence,
  new decisions, or new diagnostic reports that touch the
  generated-artifact contract must reference v2 attributes (class,
  ci_policy, commit_policy, activation, enforcement) and not the legacy
  bucket names.
- **Reconciliation, not rewrite.** This note is the canonical place to
  explain the concept break. If a future reader encounters the legacy
  labels in this experiment’s evidence, they should land here.

## See also

- `.vibe/generated-artifacts.yml` — current v2 contract
- `scripts/docmeta/validate_generated_artifacts_contract.py` — v2 validator
- `scripts/docmeta/resolve_generated_artifact_paths.py` — v2 resolver (filter-based)
- `.vibe/artifact-taxonomy.yml` — global artifact taxonomy (diagnostic)
