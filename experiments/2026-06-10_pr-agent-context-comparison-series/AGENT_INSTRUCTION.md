# Agent Instruction — Execute One Run of the PR Agent Context Comparison Series

## Complexity

Task complexity: medium.

Reason: The agent must execute or analyze a real PR task, preserve scope, record
evidence, and fill run-bundle artifacts. Risk is moderate because unsupported
claims or mixed conditions can invalidate the run, but no schema or validator
changes are allowed in the first iteration.

## Assignment

Execute exactly one run of
`experiments/2026-06-10_pr-agent-context-comparison-series`.

Use only the condition assigned by the user or run coordinator. Do not import
artifacts, instructions, dumps, or rubrics from other conditions.

## Hard guardrails

- Do not create or modify schemas.
- Do not create or modify validators.
- Do not promote anything to `catalog/` or `prompts/adopted/`.
- Do not claim a condition effect from a single run.
- Do not treat Lenskit/repoLens navigation as proof.
- Do not patch before diagnosis unless the task is instruction-only.

## Required output artifacts

Create or update only the assigned run folder under `artifacts/` and add:

- `run.yml`
- `run_meta.json`
- `agent-output.md`
- `changed-files.txt` or `no-changes.txt`
- `targeted-tests.txt` or `diagnostic-checks.txt`
- `measurement.yml`
- `comparability.yml`
- `auditor-output.yml`
- `evidence-pack.yml`
- `timing.txt`

Update `results/evidence.jsonl` with one JSON line describing the run.
Do not update `results/result.md` or `results/decision.yml` unless explicitly
asked after review.

## Stop criterion

Stop and report `not_comparable` if the condition boundary was mixed, required
source evidence is missing, or the task cannot be tied to a real PR/review item.
