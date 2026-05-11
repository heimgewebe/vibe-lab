---
title: "Review/Rework Artifact Contract (v0.1)"
status: defining
canonicality: canonical
created: "2026-05-11"
author: "evidence-control-plane"
relations:
  - type: references
    target: "../experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/results/cross-run-assessment.md"
    reason: "§5 Blocker: review_friction_count und rework_count persistent unmessbar"
  - type: references
    target: "../experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/results/decision.yml"
    reason: "verdict=insufficient_proof; next_steps nennen Archivierungsmechanismus als Blocker"
  - type: references
    target: "changed-files-artifact.contract.md"
    reason: "Analoges Muster: first-class primitive für fehlende Metrik-Klasse"
  - type: references
    target: "../docs/evaluations/agent-skill-file-fruitfulness.md"
    reason: "Evaluation-Metriken review_friction_count und rework_count definiert"
---

# Review/Rework Artifact Contract (v0.1)

## Purpose

Define the minimal structure and semantics of a `review-events.yml` artifact that
can be archived as part of any run bundle when `review_friction_count` or
`rework_count` measurement is claimed or attempted.

This contract exists to break the pattern of repeatedly documenting
`review_friction_count: null` and `rework_count: null` with `missing_evidence` across
multiple runs. Instead, it establishes review and rework evidence as **first-class
primitives** that either exist (and enable friction/rework measurement) or are
explicitly absent (with documented reason).

**This contract does NOT:**
- claim that the Agent/Skill layer reduces review friction or rework
- enable a `result_assessment` or `adoption_assessment`
- create a usefulness claim of any kind
- override the `insufficient_proof` verdict in `results/decision.yml`

It only enables future runs to move from `missing_evidence` to `repo_local` for
these two metrics — once external review events are actually archived.

## Contract Scope

- **Applies to**: Run bundles in `experiments/*/artifacts/run-*/` where:
  - `measurement.yml` includes `review_friction_count` or `rework_count` metrics
    (whether measured or null), OR
  - `comparability.yml` includes a `review_evidence_artifact` field

- **Version**: v0.1 (establishing the primitive; subsequent revisions may formalize
  structure and add CI enforcement)

- **Status**: Defining (canonical for new runs; not yet enforced by schema)

## Artifact Structure

A valid `review-events.yml` artifact MUST contain:

```
review-events.yml
├─ run_id: <run identifier>
├─ pr_ref: <GitHub PR URL or PR number>
├─ review_friction_count: <integer — number of reviewer rounds before merge>
├─ rework_count: <integer — number of follow-up commits revising prior claims>
├─ captured_at: <ISO 8601 timestamp>
├─ evidence_status: repo_local | ci_artifact | external_verified
└─ notes: <optional free-text explanation>
```

Additionally, the artifact SHOULD include at least one of the following to make
the review friction count independently verifiable:

```
├─ review_thread_refs: [list of PR comment URLs or API refs]
└─ rework_commit_refs: [list of git commit SHAs with description]
```

### Minimal Example (review-events.yml)

```yaml
schema_version: "1.0.0"
contract: "review_events"
run_id: "run-007-controlled-agent-skill-run"
pr_ref: "github:heimgewebe/vibe-lab/pull/42"
review_friction_count: 2
rework_count: 1
captured_at: "2026-05-20T14:30:00Z"
evidence_status: "external_verified"
review_thread_refs:
  - "https://github.com/heimgewebe/vibe-lab/pull/42#issuecomment-1001"
  - "https://github.com/heimgewebe/vibe-lab/pull/42#issuecomment-1002"
rework_commit_refs:
  - sha: "abc123def456"
    description: "Fix: address reviewer comment about missing rationale in decision.yml"
notes: "2 reviewer rounds before merge. 1 rework commit."
```

## Semantics

### When review-events.yml MUST exist (enabling repo_local evidence_status)

If `measurement.yml` declares `review_friction_count` or `rework_count` with
`evidence_status: repo_local`, then `comparability.yml` MUST reference a
`review_evidence_artifact` pointing to a valid `review-events.yml` in the same
run directory.

### When review-events.yml MAY be null

In any run where review events are not yet archived:

- `review_friction_count.value: null` with `evidence_status: missing_evidence`
  is valid, provided a reason is documented in `notes` or in `missing_evidence`.
- `rework_count.value: null` with `evidence_status: missing_evidence` is valid,
  under the same condition.
- In `comparability.yml`, `review_evidence_artifact` may be omitted or set to
  `null` with no penalty — this is the current baseline for all existing runs.

### How Runs Reference This Artifact

In `comparability.yml`, add the optional field:

```yaml
review_evidence_artifact: "review-events.yml"
# or experiment-relative:
review_evidence_artifact: "artifacts/run-007-controlled-agent-skill-run/review-events.yml"
```

The validator (`validate_run_bundle.py`) will:
1. Resolve the path using the same containment rules as `changed_files_artifact`
2. Verify the file exists in the run directory
3. Allow `review_friction_count.evidence_status: repo_local` and
   `rework_count.evidence_status: repo_local` only when this field is valid

### Null-Value Documentation Discipline (always enforced)

Regardless of whether `review_evidence_artifact` is present, if:

- `review_friction_count.value` is `null` → `evidence_status` MUST be
  `missing_evidence` AND a reason MUST be documented in `notes` or `missing_evidence`
- `rework_count.value` is `null` → same requirement

This prevents silent null accumulation and documents the gap explicitly.

### Operationalization Status

| Enforcement Level | Status   | Details |
| ---               | ---      | ---     |
| **Schema**        | Not yet  | JSON schema for review-events.yml structure is pending |
| **Null-discipline** | Active | Validator enforces: `null → missing_evidence + reason` |
| **Artifact ref**  | Active   | Validator validates `review_evidence_artifact` when present |
| **CI**            | Future   | Planned: CI check for mandatory archiving |

## Design Rationale

**Why a contract, not optional documentation?**

The pattern of repeatedly documenting `review_friction_count: null (missing_evidence)`
across all 3 comparable runs (run-002, run-005, run-006) shows that review/rework
measurement was never architected as a first-class primitive.

This is the exact structural gap documented in:
- `cross-run-assessment.md §5` (Blocker: review_friction_count fehlt in allen 3 Runs)
- `decision.yml` next_steps (Archivierungsmechanismus als Vorbedingung für Outcome-Evidence)
- `docs/roadmap.md` RM-005 and GAP-003

**Why v0.1 is "defining"?**

This contract is intentionally minimal to:
1. Establish the principle that review/rework events MUST be archivable as first-class artifacts
2. Not prescribe a mandatory timeline or enforcement date
3. Leave schema formalization for v0.2
4. Not block existing runs (run-002, run-005, run-006 are grandfathered — they document
   absence with reason, satisfying null-discipline)

**What this contract explicitly does NOT change:**

- The `insufficient_proof` verdict in `results/decision.yml` remains unchanged
- No promotion, adoption, or usefulness claim is created
- The evaluation in `docs/evaluations/agent-skill-file-fruitfulness.md` is unchanged
- GAP-003 and EP-002 in `docs/roadmap.md` remain open

## Next Steps

1. **For future runs**: Archive `review-events.yml` as part of run-bundle creation.
   Reference it in `comparability.yml` via `review_evidence_artifact`.

2. **For existing runs (run-002, run-005, run-006)**: These runs lack
   `review-events.yml` (retroactive capture is not feasible for already-closed PRs).
   They correctly remain with `null + missing_evidence + reason`. No change required.

3. **For independent auditor requirement**: `review-events.yml` alone does not satisfy
   the independent auditor blocker from `cross-run-assessment.md §5.C`. Both are
   required: (a) review events archived, and (b) auditor ≠ executor.

4. **For v0.2**: Formalize `review-events.yml` in a JSON schema; add CI enforcement.

---

**Status**: This contract is canonical and SHOULD be followed for all new runs
created after 2026-05-11. Existing runs (run-002, run-005, run-006) are grandfathered;
retrofitting is not required.
