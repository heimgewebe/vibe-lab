---
title: "Operator Routing ML Readiness Shadow — Method"
status: active
canonicality: operative
triggered_by: "user-request-operator-learning-ml-2026-07-23"
---

# Method

## Phase A — readiness baseline

1. Read the Grabowski task SQLite store strictly read-only.
2. Count task lifecycle states and direct structured fields relevant to routing and outcomes.
3. Treat `state` only as process lifecycle evidence; never relabel it as semantic task correctness.
4. Treat model or harness values inferred from `argv` only as diagnostic lower-bound coverage, not canonical routing truth.
5. Store aggregates only. Do not export raw argv, prompts, transcripts, notes or private payloads.

## Phase B — shadow capture

1. Select naturally occurring eligible coding-agent tasks prospectively.
2. Freeze task class, risk band and repository-context band before outcome review.
3. Record the actual route identity from the authoritative routing decision source, not by post-hoc argv guessing.
4. Execute normally. The experiment does not select or modify the route.
5. After execution, bind an independent semantic outcome assessment to primary evidence such as CI, diff-bound review or explicit operator decision.
6. Preserve failures, null outcomes and abstentions.
7. Compare completeness and capture cost only after at least 20 control and 20 treatment cases.
8. Only if the readiness threshold passes may a separate offline model-comparison task evaluate scikit-learn baselines. No model receives production authority from this experiment.

## Stop rules

Stop before model training if semantic outcomes cannot be separated from process lifecycle, canonical route identity is unavailable, privacy requires raw transcript export, or any component attempts automatic routing, queue, policy, merge or runtime mutation.

## Interpretation

A pass establishes only dataset readiness for an offline shadow model comparison. It does not establish that ML improves routing and does not authorize deployment.
