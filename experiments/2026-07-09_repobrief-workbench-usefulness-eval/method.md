---
title: "RepoBrief Workbench Usefulness Evaluation — Method"
status: designed
canonicality: operative
---

# Method

## Hypothesis

RepoBrief/Agent Workbench evidence conditions may reduce localization misses,
missing evidence, patch-scope drift, check misses and false-confidence risk in
agent code work. This is unproven until comparable executed runs exist.

## Conditions

The comparison matrix is defined in `measurement-plan.yml` and includes at least:

1. `no_context_no_rlens`
2. `reading_pack`
3. `context_pack`
4. `full_resolved_evidence`
5. `trace_gated`

`full_resolved_evidence` is diagnostic and must not be treated as a safe default
candidate unless executed runs show lower false-confidence risk and acceptable
overhead.

## Run procedure

For each comparable code task:

1. Record task kind, repository, base/head, changed-file count and difficulty.
2. Assign one condition from the matrix.
3. Record allowed and disallowed evidence for the condition before the agent run.
4. Capture the agent's selected files, ranges, citations, checks and claims.
5. Compare against expected evidence from the task profile or review surface.
6. Record external observations: existing tests, CI, reviewer notes, operator
   review, or patch-evaluation artifacts when present.
7. Score metrics and classify misses.
8. Record non-claims and whether any self-proof violation occurred.

## Minimum metrics

The required metrics cover:

- localization;
- evidence completeness;
- patch scope;
- check fit;
- miss taxonomy;
- false-confidence risk;
- effort/overhead;
- no-self-proof violations.

## Success criterion

A condition can only become a promotion candidate if multiple comparable runs
show better or clearer diagnostics than the baseline and no central metric
regresses without an explicit defer/drop decision.

## Non-goals

This method does not execute the run series, promote a default, mutate RepoBrief,
prove agent quality, or treat generated tests as independent proof.
