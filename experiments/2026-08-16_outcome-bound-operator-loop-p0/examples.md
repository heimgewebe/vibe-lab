---
title: "Outcome-Bound Operator Loop P0 — Illustrative examples"
status: designed
canonicality: exploratory
created: "2026-08-16"
updated: "2026-08-16"
triggered_by: "conversation:user-request-2026-08-16-outcome-bound-operator-loop"
relations:
  - type: references
    target: contracts/outcome-case-spec.v0.schema.json
  - type: references
    target: contracts/outcome-observation.v0.schema.json
---

# Illustrative examples

These are paper examples, not admitted natural cases, execution records or
evidence, and D1/D2/D3 have no productive authority. Digest values and
authoritative source refs would be sealed only for a real prospectively admitted
record. Every full example requires the canonical `operator_intake_ref` and a
lowercase SHA-256 `source_request_digest`; work-lane and execution-source refs
remain absent until the case actually acquires those identities.

## D1 — one bounded execution

- **identity:** canonical operator-intake and source-request digest are frozen;
  an existing Grabowski work lane and GitHub execution-source identity, when
  acquired, remain two distinct optional refs.
- **distance/risk:** `D1`, moderate risk, no override.
- **problem/actor:** a Grabowski coding task needs a verifiable outcome beyond a
  merely terminal process state; the affected actor is the requesting operator.
- **baseline:** explicit gap: no outcome indicator has yet been frozen.
- **desired change:** the reviewed task outcome is resolvable after one bounded
  execution.
- **hypothesis/intervention:** freezing one indicator and authority before
  mutation is sufficient; add only the Outcome Case spec.
- **alternative path:** if no authoritative outcome exists, append
  `insufficient_evidence` rather than infer from task state.
- **observation:** indicator = reviewed requested change; authority = GitHub/CI
  plus named review; window = technical closeout through review.
- **falsifier:** only lifecycle state or self-report is available.
- **decision rules:** `if_supported` closes only the observation;
  `if_not_supported` stops the intervention; `if_insufficient_evidence` preserves
  the gap without guessing.
- **non-goals:** do not infer correctness, merge readiness or routing quality.

## D2 — one downstream boundary

- **identity:** one canonical intake, one execution-source identity and one
  downstream reviewed CI/review window.
- **distance/risk:** `D2`, moderate risk, no override.
- **problem/actor:** a maintainer needs to know whether a generated-artifact
  contract reduces recurring review ambiguity across several runs.
- **baseline:** observed repeated stale-artifact and schema-friction records,
  referenced rather than copied.
- **desired change:** reviewers can make a clearer handling decision across the
  downstream workflow boundary.
- **hypothesis/intervention:** the full form may expose decision rules missing
  from minimal; use minimal while unproven and compare a full rendering only in
  the separately reviewed shadow protocol.
- **alternative path:** retain minimal if full adds no actionable decision.
- **observation:** indicator = distinct changed review decision; authority =
  referenced run evidence and named reviewer; window = six matched cases.
- **falsifier:** no additional actionable decision or overhead breach.
- **decision rules:** `if_supported` permits a separately reviewed pilot
  proposal; `if_not_supported` retains minimal; `if_insufficient_evidence`
  defers without policy change.
- **non-goals:** do not claim overall friction reduction.

## D3 — multi-step or multi-organ outcome

- **identity:** canonical Bureau intake, separate Grabowski execution receipt and
  separately referenced GitHub/CI closeout.
- **distance/risk:** `D3`, high risk, reviewed override to full because an
  erroneous claim could cross organ boundaries.
- **problem/actor:** a Bureau decision owner needs a bounded outcome assessment
  after multi-step operator work without creating a second control plane.
- **baseline:** explicit gap: causal comparison and completion-time evidence are
  absent.
- **desired change:** the owner receives an honest decision that preserves gaps
  and confounders.
- **hypothesis/intervention:** a full frozen spec plus append-only observation is
  the smallest schema-level intervention.
- **alternative path:** use `insufficient_evidence` when effect authority or the
  observation window cannot be bounded; classify as `L` only when the desired
  outcome is reduction of a named uncertainty or a better bounded decision.
- **observation:** indicator = reviewed decision change; authority = owner plus
  referenced primary sources; window = registered multi-step closeout window.
- **falsifier:** the assessment depends on duplicated truth, retrospective labels
  or unresolved confounding.
- **decision rules:** `if_supported` presents the bounded decision;
  `if_not_supported` stops the intervention; `if_insufficient_evidence` preserves
  uncertainty and may propose a separate reviewed follow-up candidate.
- **non-goals:** do not create tasks, route work, merge, deploy or claim causal
  effectiveness.

## Supported observation

- exact spec binding: case id, spec ref and spec SHA-256 agree;
- technical closeout: references only;
- state: `supported`;
- strength: `direct_primary_evidence`;
- evidence refs: authoritative review and CI refs;
- confounders: none unresolved for the narrow claim;
- established: the frozen desired change occurred in the registered window;
- not established: causality, general efficacy and cross-case superiority;
- reviewed error taxonomy: no class is added (`not_reviewed`, empty list);
- decision/follow-up: close the observation only; the already terminal technical
  task stays closed and authoritative; make no default-policy change.

## Negative observation

- exact spec binding and technical-closeout refs remain intact;
- state: `not_supported`;
- strength: `triangulated_primary_evidence`;
- evidence refs: reviewed diff and CI refs showing the desired change did not
  occur;
- confounders: recorded but not sufficient to reverse the narrow finding;
- established: the registered indicator was absent in the window;
- not established: which alternative intervention would work;
- reviewed error taxonomy: remains `not_reviewed` unless a future named review
  applies the review-bound taxonomy;
- decision/follow-up: stop the intervention and review the alternative path.

## Insufficient observation

- exact spec binding remains intact and the available technical closeout is only
  referenced;
- state: `insufficient_evidence`;
- strength: `insufficient`;
- evidence refs: the gap-bearing closeout or assessment ref, if available;
- confounders: missing comparison, missing completion time or unresolved source
  authority;
- established: only that the case and evidence gap were recorded;
- not established: desired change, contradiction, causality or efficacy;
- reviewed error taxonomy: remains `not_reviewed` unless a future named review
  applies the review-bound taxonomy;
- decision/follow-up: do not guess; append a later correction only if new
  authoritative evidence appears within policy.
