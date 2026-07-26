---
title: "Operator Routing ML Readiness Shadow — Method"
status: active
canonicality: operative
triggered_by: "user-request-operator-learning-ml-2026-07-23"
---

# Method

## Phase A — readiness baseline

1. Read the Grabowski task SQLite store strictly read-only.
2. Read Agent Workspace manifests strictly read-only and aggregate validated `route_evidence` coverage separately from task-table coverage.
3. Do not pretend `route_evidence` is a task-table column or that workspace manifests are directly joinable to task rows without an explicit versioned capture binding.
4. Count task lifecycle states and direct structured fields relevant to routing and outcomes.
5. Treat `state` only as process lifecycle evidence; never relabel it as semantic task correctness.
6. Treat model or harness values inferred from `argv` only as diagnostic lower-bound coverage, not canonical routing truth.
7. Store aggregates only. Do not export raw argv, prompts, transcripts, notes, workspace ids, recommendation ids or private payloads.

## Phase B — shadow capture

1. Select naturally occurring eligible coding-agent tasks prospectively.
2. Freeze task class, risk band and repository-context band before outcome review.
3. Record the actual route identity from the authoritative routing decision source, not by post-hoc argv guessing.
4. Execute normally. The experiment does not select or modify the route.
5. After execution, bind an independent semantic outcome assessment to primary evidence such as CI, diff-bound review or explicit operator decision.
6. Preserve failures and null outcomes. For an eligible case with no defensible semantic outcome, record an explicit abstention; keep it in the cohort denominator and do not count it as complete.
7. Compare completeness and capture cost only after at least 20 control and 20 treatment cases.
8. Only if the readiness threshold passes may a separate offline model-comparison task evaluate scikit-learn baselines. No model receives production authority from this experiment.

## Phase C — prospective cohort readiness gate

1. Bind the audit to `readiness-gate.v1.json`; thresholds are fixed before any comparative model performance is inspected and must not be relaxed after seeing results.
2. Read the create-only `prospective`, `eligibility`, `records` and `attempts` cohort directories strictly read-only.
3. Recompute content identities, deterministic workspace/task case ids, prospective-to-bound-eligibility-to-record links and freeze/outcome/capture ordering. Any integrity or no-effect violation fails closed.
4. Resolve the Agent Workspace manifest read-only from each prospective workspace identity, verify workspace and plan identity plus the canonical route-evidence hash, and derive the frozen bounded feature vector again from that verified route. A feature mismatch blocks PASS. The frozen manifest hash remains receipt-bound snapshot identity; it is not compared to the later mutable manifest after task binding.
5. Verify every bound eligibility reference against the exact prospective workspace/plan/case/freeze tuple and every sealed record against the exact eligibility, route and feature binding. The preregistered comparison unit is the natural coding-agent task, so each bound eligibility is one treatment case even when several tasks share one prospective workspace; each eligibility can count as complete at most once, and multiple records for the same eligibility fail closed.
6. Count created, duplicate, rejected and error capture attempts explicitly. Unsealed and unbound cases remain visible instead of being silently discarded.
7. Report task kind, risk tier, repository context, actual route, recommended route and route schema v1/v2 separately. No representativeness claim is made for unobserved or under-covered strata.
8. A reviewed semantic outcome counts as complete only with primary evidence. Abstentions remain in the eligible treatment-case denominator; lifecycle state is never promoted into a semantic label.
9. Read legacy v1/v2 receipts without rewriting them. For new v3 receipts, validate bounded case provenance, execution provenance and zero or two-to-four independently attributable semantic assessments. Legacy missing fields remain unknown and never become pass-quality evidence by inference.
10. Resolve `agent-workspace-manifest` routes from immutable workspace bindings. For `direct-task-start`, validate the create-only binding structure, but do not treat its self-reported creation time as prospective evidence. Current prospective v2 receipts do not commit the later binding bytes or an independent creation receipt, so those bindings are excluded from route/repository coverage and route-plus-outcome completeness. A future producer contract must commit the binding identity at freeze time or supply durable external creation evidence before direct-task cases can support `PASS`. Raw argv remains excluded. Coverage-relevant accepted source bindings remain part of the aggregate cohort identity.
11. Count only `production` v3 eligibility in the treatment denominator. Test, synthetic and quarantined cases are reported and excluded. A reviewed record counts as complete only when it has primary evidence, observed execution provenance, a resolved prospectively bound route and at least two distinct reviewer pseudonyms assessing the same outcome kind. Unknown execution or unresolved route provenance blocks `PASS` for the treatment cohort.
12. Preserve assessment disagreement explicitly. The deterministic top-level adjudication keeps a unanimous label and uses `partial` when reviewers disagree; any contradictory optimistic or pessimistic top-level label is an integrity error. Pseudonym distinction makes disagreement measurable but is not a cryptographic proof of reviewer independence.
13. Require the complete canonical route reference—including source and manifest identity field—to remain exact across prospective, eligibility and record receipts. Both legacy and current reference shapes remain readable, but no unsafe cross-shape equivalence is invented.
14. Emit exactly `PASS`, `FAIL` or `CONTINUE-COLLECTING`, bound to the criteria SHA-256, raw cohort hashes and coverage-source binding hashes. Only `PASS` may unblock a separate offline model-comparison task.
15. The 2026-07-26 live audit returned `CONTINUE-COLLECTING`: one prospectively frozen production case, one eligibility, one sealed abstention and two capture attempts were read with zero integrity errors and zero no-effect violations. The current direct-task binding is structurally valid but is not retrospectively promoted to prospective route evidence, so it contributes neither route coverage nor route-plus-outcome completeness.

## Stop rules

Stop before model training if completeness is below 80 percent, if more than 30 percent of non-abstaining outcomes lack primary evidence, if semantic outcomes cannot be separated from process lifecycle, if canonical route identity cannot be bound to the eligible case, if privacy requires raw transcript export, or if any component attempts automatic routing, queue, policy, merge or runtime mutation. A result from 80.0 percent up to but below 90.0 percent completeness is inconclusive: extend the frozen cohort or defer; do not train.

## Interpretation

A pass establishes only dataset readiness for an offline shadow model comparison. It does not establish that ML improves routing and does not authorize deployment.
