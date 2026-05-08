---
title: "Changed-Files Artifact Contract (v0.1)"
status: defining
canonicality: canonical
created: "2026-05-08"
author: "evidence-control-plane"
relations:
  - type: references
    target: "../experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/artifacts/run-003-controlled-agent-skill-run/measurement.yml"
    reason: "scope_drift_count metric requires changed-files artifact"
  - type: references
    target: "../experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/artifacts/run-004-controlled-agent-skill-run/measurement.yml"
    reason: "scope_drift_count metric requires changed-files artifact"
---

# Changed-Files Artifact Contract (v0.1)

## Purpose

Define the minimal structure and semantics of a `changed-files.txt` artifact that must be archived
as part of any run bundle when scope-drift measurement is claimed or attempted.

This contract exists to prevent the pattern of repeatedly documenting `scope_drift_count: null`
with `missing_evidence` across multiple runs. Instead, it establishes changed-files as a **first-class
primitive** that either exists (and enables drift measurement) or is explicitly absent (with documented reason).

## Contract Scope

- **Applies to**: Run bundles in `experiments/*/artifacts/run-*/` where:
  - `measurement.yml` includes a `scope_drift_count` metric (whether measured or null), OR
  - `comparability.yml` includes a `changed_files_artifact` field

- **Version**: v0.1 (establishing the primitive; subsequent revisions may formalize structure)

- **Status**: Defining (not yet enforced by schema, but canonical for new runs)

## Artifact Structure

A valid changed-files artifact MUST contain:

```
changed-files.txt (or changed-files.jsonl, or changed-files.md)
├─ File List: repo-relative paths affected by the run
├─ Change Type: Add/Modify/Delete per file (minimal classification)
└─ Scope Boundary: explicit statement of what was in/out of scope
```

### Minimal Example (changed-files.txt)

```
# Changed-Files Artifact for run-002-controlled-agent-skill-run
# Generated: 2026-05-06T12:00:00Z
# Scope: Experiment artifact creation + measurement.yml updates only

artifacts/run-002-controlled-agent-skill-run/measurement.yml        [add]
artifacts/run-002-controlled-agent-skill-run/auditor-output.yml     [add]
artifacts/run-002-controlled-agent-skill-run/evidence-pack.yml      [add]
artifacts/run-002-controlled-agent-skill-run/run.yml                [add]
artifacts/run-002-controlled-agent-skill-run/run_meta.json          [add]
experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/manifest.yml  [modify]

Scope Boundary
==============
INCLUDED:
- Experiment artifact directory (run-002-controlled-agent-skill-run/)
- Manifest updates to reference new artifacts
- Generated metrics in .vibe/

EXCLUDED:
- Source code changes
- Test modifications
- Documentation outside experiment context
```

## Semantics

### When changed-files.txt MUST exist

1. **In archived run bundles**: When a run bundle is archived in `artifacts/run-*/`, a changed-files artifact
   MUST be created and referenced in `comparability.yml` via the `changed_files_artifact` field.

2. **When scope_drift_count is claimed**: If `measurement.yml` declares `scope_drift_count` with
   `evidence_status: repo_local`, the changed-files artifact MUST be present and repo-locatable.

### When changed-files.txt MAY be null

- In candidate/rehearsal runs (verdict: not_comparable) where scope containment is self-evident or deliberately
  not measured, `changed_files_artifact: null` is acceptable with explicit notes in `measurement.yml`
  explaining why drift measurement was skipped.

- Example: "No changed-files artifact archived. Scope appears contained to run-004 artifact directory plus
  manifest/index updates, but without a repo-local changed-files record this cannot be claimed as repo_local."

### Operationalization Status

| Enforcement Level | Status | Details |
| --- | --- | --- |
| **Schema** | Not yet | JSON schema for changed-files structure is pending; currently documented only |
| **Manual** | Active | Run creators MUST archive or explicitly justify absence |
| **CI** | Future | Planned: CI check to enforce presence/justification in run bundles |

## Design Rationale

**Why a contract, not optional documentation?**

The pattern of repeatedly documenting `scope_drift_count: missing_evidence` across runs suggests that
scope measurement was never architected as a first-class primitive. Without a contract:

- Teams document absence industrially (= bureaucratic evidence growth)
- Subsequent runs repeat the same gap
- The system institutionalizes incompleteness instead of fixing it

**Why v0.1 is "defining"?**

This contract is intentionally minimal to:
1. Establish the principle that changed-files MUST be a first-class artifact
2. Not prescribe exact format (txt, jsonl, md all acceptable in v0.1)
3. Leave structure details for v0.2 (possibly JSON schema formalization)

## Next Steps

1. **For future runs**: Archive changed-files as part of run-bundle creation. Reference it in
   `comparability.yml` via `changed_files_artifact: artifacts/run-*/changed-files.txt`.

2. **For run-003/004**: These runs lack changed-files artifacts (retroactive capture not feasible).
   This is documented in their `measurement.yml` as `missing_evidence`. These runs correctly
   remain `not_comparable` until true comparable runs with proper artifacts are created.

3. **For v0.2**: Formalize changed-files structure in JSON schema; add CI enforcement.

---

**Status**: This contract is canonical and MUST be followed for all new runs created after 2026-05-08.
Existing runs (run-002, run-003, run-004) are grandfathered; retrofitting is not required.
