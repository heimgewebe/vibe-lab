---
title: "Method — rLens Agent Context Conditions"
status: designed
canonicality: operative
relations:
  - type: references
    target: "measurement-plan.yml"
  - type: references
    target: "CONTEXT.md"
---

# Method — rLens Agent Context Conditions

## Series design

Each run applies exactly one condition to one real ecosystem task. Conditions may
not be mixed inside a run. A run is comparable only if the task class, task size,
allowed context, disallowed context, output request, validation possibility, and
review source are recorded.

## Conditions

### A — `no_rlens`

The agent receives the normal user request, live repo/PR information available in
the conversation, and ordinary tool access. No rLens bundle, RepoBrief reading
pack, context pack, or trace gate is provided.

Purpose: baseline for ordinary operator work.

### B — `reading_pack`

The agent receives a bounded rLens/RepoBrief reading pack: required reading,
relevant paths, and freshness metadata. The agent may use the pack for navigation
but must verify claims against live repo/PR evidence before acting.

Purpose: test whether small curated reading improves locator and evidence quality.

### C — `context_pack`

The agent receives a task-profiled context pack with exact artifact refs,
source freshness, relevant paths, non-claims, and expected evidence fields. The
pack is narrower than a full dump and is bound to the task class.

Purpose: test whether task-profiled context reduces unsupported claims and rework.

### D — `full_dump`

The agent receives a broad rLens/RepoBrief dump or large repository context slice.
The dump must carry freshness and non-truth warnings. The run is diagnostic only;
this condition is not eligible as a default without separate privacy and token-cost
review.

Purpose: test whether more context improves output or merely increases fluent but
ungrounded claims.

### E — `trace_gated`

The agent receives a context pack and must produce a compact proof-of-reading
trace before final answer or patch. Each nontrivial claim must cite a live file,
PR, CI/log, Bureau task, or rLens context reference, and stale/derived context
must be explicitly downgraded.

Purpose: test whether trace gating lowers unsupported claims, hallucinated paths,
missing evidence, and rework enough to justify the extra ceremony.

## Task classes

Allowed task classes:

1. `pr_review`: review a PR or review comment.
2. `pr_rework`: implement or plan a response to a review comment.
3. `small_repo_fix`: make a small repository change with tests.
4. `diagnosis_only`: diagnose a repo issue without mutation.

Excluded tasks:

- secret-bearing work;
- live deploy/runtime mutation;
- tasks too broad to validate in one run;
- tasks where condition exposure cannot be separated.

## Required run artifacts

A completed run must include:

- `run.yml`
- `condition-input.md`
- `agent-output.md`
- `measurement.yml`
- `comparability.yml`
- `review-notes.md` or `auditor-output.yml`
- `validation-output.txt` or `diagnostic-checks.txt`
- `timing.yml`

Patch runs must also include the actual diff or PR reference and targeted test
output.

## Assessment rule

No default rLens access level can be promoted until either:

- at least three comparable task pairs support the same directional finding; or
- the result is explicitly recorded as inconclusive and no promotion occurs.

The first run under a condition is only an observation. A clean single PR is not a
condition-effect claim.
