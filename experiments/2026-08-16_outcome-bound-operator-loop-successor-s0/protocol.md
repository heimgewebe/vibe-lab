---
title: "Outcome-Bound Operator Loop Successor S0 — Intervention-relative admission protocol"
status: designed
canonicality: operative
created: "2026-08-16"
updated: "2026-08-16"
triggered_by: "github:heimgewebe/vibe-lab#339"
---

# S0 protocol

## Purpose

Test only whether a narrower prospective-admission boundary is understandable on
fixed historical calibration cases. This protocol creates no productive gate and
has no authority outside this experiment.

## Three boundaries

### T0 — `situation_exists`

The problem, gap, diagnosis, prior merge, prior task publication, registry seed,
runtime state or other antecedent production state may already exist. T0 does not
by itself make a later case retrospective.

### T1 — `intervention_identified`

The concrete intervention-under-test is identifiable as a bounded productive
change. Exact second-level reconstruction is not required. The case needs a stable
intervention description and at least one evidence reference showing that the
intervention identity was not invented after its outcome became known.

### T2 — `intervention_effect_begins`

T2 is the first productive act materially belonging to execution of that concrete
intervention. It includes, when they are part of the intervention:

- implementation or scratch code intended to realize it;
- an authoritative state mutation made to realize it;
- execution or benchmarking of the proposed mechanism;
- routing, queue, priority, policy, deployment or runtime mutation made to realize it.

Observation, diagnosis and antecedent state do not count as T2 unless they are
materially part of the intervention itself.

## Intervention identity guard

The successor rule may not be used to rename work after it has started. A reviewer
must treat earlier productive work as part of the intervention when it materially
implements, exercises or validates the same proposed mechanism, even if a later
record gives the mechanism a narrower name.

Conversely, an antecedent productive action may remain part of T0 when it merely
creates, reveals or diagnoses the state to which a distinct later intervention is
addressed. The distinction must be supported by the available case evidence; the
experiment does not infer it from convenient wording.

If the evidence cannot establish whether earlier productive work belongs to the
intervention-under-test, the correct status is `indeterminate`, not `eligible`.

## Successor classification

Each calibration case receives exactly one status:

- `eligible` — the concrete intervention is stably identifiable before T2, its
  productive effect had not begun at the prospective freeze boundary, and the
  case was not selected after observing the intervention outcome;
- `ineligible` — the intervention's productive effect had already begun, the
  intervention identity is result-selected/retrofitted, or the case otherwise
  requires retrospective outcome knowledge;
- `not_applicable` — no Outcome Case is warranted by default because technical
  acceptance itself is the complete desired effect (D0 calibration);
- `indeterminate` — available evidence cannot reliably separate antecedent state
  from execution of the intervention-under-test.

Only `eligible` would be admissible to a future prospective cohort. `indeterminate`
is fail-closed and cannot be counted as eligible.

## Prospective condition

For a future case, the conceptual condition is:

```text
intervention identity bound before T2
AND intervention effect not yet begun at freeze
AND no result-informed case or intervention selection
```

A future Admission Record would need only the situation, intervention description,
`effect_started: false`, one intervention evidence reference and the reviewed
classification. S0 does not create that production or cohort contract.

## Fixed S0 calibration set

S0 freezes exactly six cases before independent review:

1. P1-01 — fresh single-use Bureau runtime-refresh authority;
2. P1-02 — merge-bound readiness promotion for standalone Operator-Intake tasks;
3. candidate `candidate-05002ab2a02663d844bbbc43` — post-merge StateStore convergence;
4. candidate `candidate-a91b4d18a6c9db7e617c13ce` — companion post-seed natural intake with incomplete intervention-specific evidence;
5. candidate `candidate-8145cd731e6a7d1163b4ed0f` — scratch patch and benchmark already existed before intake;
6. one explicit D0 paper-only calibration where technical acceptance is the desired effect.

The detailed frozen author classifications live in `s0/paper-cases.md` and are
retrospective calibration records, never prospective cohort or efficacy evidence.

## Review gate

Reviewer A is the frozen author assessment in this revision. Reviewer B must be an
independent exact-head semantic reviewer that has not authored these case
classifications.

A **material disagreement** exists if Reviewer B:

- changes any case among `eligible`, `ineligible`, `not_applicable` or
  `indeterminate`;
- finds that a case given a definitive classification should instead be
  `indeterminate`;
- identifies a credible intervention-renaming path that would make already-started
  work appear prospective under this rule.

S0 passes only with zero material disagreements across all six fixed cases and zero
productive authority effects. Any material disagreement yields `defer` and no S1.

## S0 stop and non-promotion rules

Stop or defer if:

- a historical P1 record would need rewriting;
- a productive system would need mutation to classify a paper case;
- case evidence is silently upgraded from self-report to primary authority;
- a reviewer cannot distinguish antecedent state from intervention execution;
- the rule needs a validator, registry field or production gate to be understandable;
- any Vibe-Lab artifact changes Bureau, Grabowski, Chronik, Leitstand, GitHub/CI or runtime authority.

Even a clean S0 review authorizes only a **separate proposal/review** for S1. It does
not start S1, S2, P2 or P3 and does not change the predecessor P1 verdict.
