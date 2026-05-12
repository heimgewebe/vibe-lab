---
title: "Review/Rework Artifact Contract (v0.2)"
status: schema-backed
canonicality: canonical
created: "2026-05-11"
updated: "2026-05-12"
author: "evidence-control-plane"
triggered_by: "user-request-2026-05-11-review-rework-outcome-evidence-blocker"
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
  - type: references
    target: "../schemas/review-events.v1.schema.json"
    reason: "JSON Schema für review-events.yml Struktur (v0.2)"
---

# Review/Rework Artifact Contract (v0.2)

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

- **Version**: v0.2 (schema-backed; enforcement active for repo_local metrics)

- **Status**: Schema-backed (schema established; not globally mandatory for all runs)

## Schema

**Schema file**: `schemas/review-events.v1.schema.json`

The schema enforces:
- `schema_version`: string, const `"1.0.0"`
- `contract`: string, const `"review_events"`
- `run_id`: non-empty string
- `pr_ref`: non-empty string
- `review_friction_count`: integer, minimum 0
- `rework_count`: integer, minimum 0
- `captured_at`: string (timezone enforcement via semantic validator)
- `evidence_status`: enum `["repo_local", "ci_artifact", "external_verified"]`
- `review_thread_refs`: optional array of non-empty strings
- `rework_commit_refs`: optional array (string SHAs or objects with `sha`)
- `notes`: optional string
- `additionalProperties: false`

## Artifact Structure

A valid `review-events.yml` artifact MUST contain:

```
review-events.yml
├─ schema_version: "1.0.0"
├─ contract: "review_events"
├─ run_id: <run identifier>
├─ pr_ref: <GitHub PR URL or PR number>
├─ review_friction_count: <integer — number of reviewer rounds before merge>
├─ rework_count: <integer — number of follow-up commits revising prior claims>
├─ captured_at: <ISO 8601 timestamp with timezone>
├─ evidence_status: repo_local | ci_artifact | external_verified
└─ notes: <optional free-text explanation>
```

Additionally, the artifact SHOULD include at least one of the following to make
the review friction count independently verifiable:

```
├─ review_thread_refs: [list of PR comment URLs or API refs]
└─ rework_commit_refs: [list of git commit SHAs with description]
```

`external_verified` evidence_status REQUIRES at least one entry in
`review_thread_refs` or `rework_commit_refs`.

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

A valid `review-events.yml` must pass both:
1. Schema validation against `schemas/review-events.v1.schema.json`
2. Semantic validation in `validate_run_bundle.py` (run_id match, captured_at timezone,
   external_verified refs)

An invalid, missing, or path-escaping `review-events.yml` BLOCKS repo_local
claim for `review_friction_count` and `rework_count`.

### When review-events.yml MAY be null

In any run where review events are not yet archived:

- `review_friction_count.value: null` with `evidence_status: missing_evidence`
  is valid, provided a reason is documented in `notes` or in `missing_evidence`.
- `rework_count.value: null` with `evidence_status: missing_evidence` is valid,
  under the same condition.
- In `comparability.yml`, `review_evidence_artifact` may be omitted or set to
  `null` with no penalty — this is the current baseline for all existing runs.

Historical runs (run-002, run-005, run-006) are grandfathered and remain
unchanged. Retroactive fabrication of `review-events.yml` is explicitly prohibited.

### How Runs Reference This Artifact

In `comparability.yml`, add the optional field:

```yaml
review_evidence_artifact: "review-events.yml"
# or experiment-relative:
review_evidence_artifact: "artifacts/run-007-controlled-agent-skill-run/review-events.yml"
```

The validator (`validate_run_bundle.py`) will:
1. Resolve the path using the same containment rules as `changed_files_artifact`
2. Verify the file exists in the run directory (path escape blocked)
3. Validate against `schemas/review-events.v1.schema.json` (schema-backed)
4. Apply semantic cross-checks (run_id match, captured_at timezone, external_verified refs)
5. Allow `review_friction_count.evidence_status: repo_local` and
   `rework_count.evidence_status: repo_local` only when this field passes all checks

### Null-Value Documentation Discipline (always enforced)

Regardless of whether `review_evidence_artifact` is present, if:

- `review_friction_count.value` is `null` → `evidence_status` MUST be
  `missing_evidence` AND a reason MUST be documented in `notes` or `missing_evidence`
- `rework_count.value` is `null` → same requirement

This prevents silent null accumulation and documents the gap explicitly.

### Operationalization Status

| Enforcement Level | Status        | Details |
| ---               | ---           | ---     |
| **Schema**        | **Active**    | `schemas/review-events.v1.schema.json` — enforces structure, types, additionalProperties:false |
| **Validator**     | **Active**    | `scripts/docmeta/validate_run_bundle.py` — schema + semantic checks |
| **Null-discipline** | Active      | Validator enforces: `null → missing_evidence + reason` |
| **Artifact ref**  | Active        | Validator validates `review_evidence_artifact` when present |
| **Enforcement scope** | repo_local | repo_local Review/Rework-Metriken erfordern valides review-events.yml; nicht global mandatory für alle Runs |
| **CI global**     | Future        | Planned: CI hard-fail for all new runs without review-events.yml (not this PR) |

## Design Rationale

**Why a contract, not optional documentation?**

The pattern of repeatedly documenting `review_friction_count: null (missing_evidence)`
across all 3 comparable runs (run-002, run-005, run-006) shows that review/rework
measurement was never architected as a first-class primitive.

This is the exact structural gap documented in:
- `cross-run-assessment.md §5` (Blocker: review_friction_count fehlt in allen 3 Runs)
- `decision.yml` next_steps (Archivierungsmechanismus als Vorbedingung für Outcome-Evidence)
- `docs/roadmap.md` RM-005 and GAP-003

**Why v0.2 is "schema-backed"?**

v0.1 established the principle; v0.2 adds machine-enforceable structure via
`schemas/review-events.v1.schema.json`. Enforcement is scoped to `repo_local`
Review/Rework-Metriken — not globally mandatory for all runs.

**What this contract explicitly does NOT change:**

- The `insufficient_proof` verdict in `results/decision.yml` remains unchanged
- No promotion, adoption, or usefulness claim is created
- The evaluation in `docs/evaluations/agent-skill-file-fruitfulness.md` is unchanged
- GAP-003 and EP-002 in `docs/roadmap.md` remain open
- Historical runs (run-002, run-005, run-006) are grandfathered and unchanged

## Residual Gaps

The schema-backed mechanism does NOT close these remaining blockers:

1. **Actual Review/Rework Runs**: No run with a real archived `review-events.yml`
   exists yet. The mechanism is ready; the evidence is not.
2. **Independent Auditor**: `review-events.yml` alone does not satisfy the
   independent auditor blocker. Both are required: (a) review events archived,
   and (b) auditor ≠ executor.
3. **Task Diversity**: Single task cluster (file-change tasks) — not addressed here.
4. **Negative Case**: No documented FAIL scenario (Auditor-FAIL) — not addressed here.

---

**Status**: This contract is canonical and SHOULD be followed for all new runs
created after 2026-05-11. Existing runs (run-002, run-005, run-006) are grandfathered;
retrofitting is not required.
