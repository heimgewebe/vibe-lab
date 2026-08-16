---
title: "Outcome-Bound Operator Loop P0 — Method and future protocols"
status: designed
canonicality: operative
created: "2026-08-16"
updated: "2026-08-16"
triggered_by: "conversation:user-request-2026-08-16-outcome-bound-operator-loop; codex-review:heimgewebe/vibe-lab#329-P2"
relations:
  - type: references
    target: contracts/outcome-case-spec.v0.schema.json
  - type: references
    target: contracts/outcome-observation.v0.schema.json
  - type: references
    target: examples.md
  - type: references
    target: schema-fit.md
  - type: references
    target: results/p0-gate.md
---

# Method and future protocols

## Goal-type separation

P0 combines two declared goal types without crossing their boundaries:

1. **Construction:** define experiment-local paper schemas and examples.
2. **Analysis:** map exactly three existing records for compatibility without
   changing them or making prospective, causal or efficacy claims.

P1 and P3 below are designs only. No natural case is admitted, no spec is frozen
for productive use, no observation is appended and no downstream system changes.

## One logical Outcome Case

An Outcome Case has two distinct records:

1. `outcome-case-spec.v0` freezes intent before productive mutation. Its
   `/case_spec` payload is canonicalized with RFC 8785 and SHA-256 bound.
2. `outcome-observation.v0` is appended after the observation window. It binds the
   exact case id, spec reference and spec digest; references technical closeout;
   records support, evidence quality, limitations and reviewed follow-up; and
   carries a SHA-256 over the complete record after removing only the current
   `digest_binding.record_sha256` value. RFC 8785 canonicalization therefore
   covers the digest algorithm, canonicalization mode, scope and predecessor.

The observation ledger is create/append-only. A correction is a new observation
whose `previous_record_sha256` points to the prior record; that predecessor link
is inside the new record's protected payload. Existing bytes are not rewritten.
The top-level observation `case_id` MUST equal
`spec_binding.case_id`; `spec_binding.spec_sha256` MUST equal the frozen
`spec_digest.value`; and the referenced spec MUST resolve to that digest. These
cross-record equalities are reviewed P0 rules, not a new repository validator.

The full identity binds the case to the canonical operator-intake reference and
a lowercase SHA-256 `source_request_digest`. This supplies end-to-end request
binding without storing the request or transcript. `work_lane_ref` and
`execution_source_identity_refs` are added only after those identities exist;
they are optional so the spec can freeze before productive mutation without
inventing a lane or execution-source identity.

`technical_closeout_refs` holds references only. Outcome Observations MUST NOT
copy CI state, merge state, execution receipt content, deployment state, diff
content or other technical-closeout truth. The owning source remains authoritative.

### Lifecycle separation

Technical task closeout is terminal and remains authoritative in its owning
source. A later effect observation MUST NOT reopen, relabel or revise the closed
technical task. If the observation warrants more work, it may produce a separate
reviewed follow-up candidate; that candidate does not alter the original
closeout and gains no automatic routing, queue or execution authority.

## Forms

The minimal `/case_spec` contains exactly:

- `desired_change`;
- `falsifier`;
- optional `evidence_ref`.

The full form contains request-bound identity; distance and risk; problem; affected actor;
observed baseline or an explicit gap; desired change; hypothesis; smallest
testable intervention; an alternative path where applicable; observation
indicator, authority and window; falsifier; decision rules; and non-goals.

The full form's `decision_rules` object must state separate nonblank actions for
`if_supported`, `if_not_supported` and `if_insufficient_evidence`. Form choice
follows outcome distance below. A reviewed risk override may require full even
at a shorter distance. More prose or more filled fields is not an actionable
decision.

## Distance classes and risk override

| Class | Outcome distance | Intake consequence |
| --- | --- | --- |
| `D0` | Technical acceptance itself is the desired effect. | No Outcome Case by default; technical closeout is sufficient. |
| `D1` | The desired effect is direct behavior observable across one bounded work or repository boundary. | Outcome Case normally uses the minimal form. |
| `D2` | The desired effect occurs across one downstream workflow or authority boundary beyond technical closeout. | Outcome Case is a pilot candidate and remains minimal while the form is unproven. |
| `D3` | The desired effect is delayed, multi-step or strategic, often across multiple organs and with material confounding exposure. | Full-form candidate; P0 grants no productive authority. |
| `L` | Learning work whose desired outcome is reduction of a named uncertainty or a better bounded decision. | Use the full form with an explicit decision boundary; learning is not a synonym for “no actor, do not execute.” |

Distance describes where an outcome can be observed, not severity. A reviewed
risk override applies when reversibility, safety, security, privacy, legal impact
or blast radius requires the full form despite a shorter distance. It can raise
the minimum form to `full`; it cannot reduce distance, weaken evidence, authorize
execution or manufacture an outcome. The override requires a named review ref.

## Outcome Observation

Each observation records exactly one of:

- `supported`;
- `partially_supported`;
- `not_supported`;
- `contradicted`;
- `pending`;
- `insufficient_evidence`.

Evidence strength is qualitative and limited to
`direct_primary_evidence`, `triangulated_primary_evidence`, `bounded_proxy`,
`named_human_assessment`, `self_report` or `insufficient`. It is not a numeric
confidence score. Each record separates established claims from
not-established claims, retains confounders, and states the reviewed or pending
decision plus follow-up.

The terminal substantive states `supported`, `partially_supported`,
`not_supported` and `contradicted` require at least one evidence reference, a
qualitative strength other than `insufficient`, and at least one established
claim. `pending` requires `insufficient` strength and no established claim;
preliminary evidence references may still be retained. `insufficient_evidence`
also requires `insufficient` strength but may cite limitation evidence and keep
narrow established facts that do not conclude the desired effect.

When `decision.review_status` is `reviewed`, `decision_ref` is required. When it
is `pending`, `decision_ref` is omitted so an unmade decision is never assigned a
fabricated authority reference.

## Reviewed-only error taxonomy

The producer does not assign an error class. Only a named review, with review
time and reference, may add one or more of:

- `shaping_error`: the frozen problem, desired change, boundary or decision rule
  was materially wrong or incomplete before execution;
- `execution_error`: productive work did not follow the frozen intervention or
  failed independently of the hypothesis;
- `observation_error`: evidence binding, observation authority, window or digest
  prevents a sound assessment;
- `hypothesis_failure`: shaping, execution and observation are adequate, but the
  predicted desired change is not supported or is contradicted;
- `external_or_confounded`: an external event or unresolved confounder prevents
  attribution.

`not_reviewed` requires an empty classification list. Error classes explain a
reviewed assessment; they do not change technical closeout or external authority.

## P1 design — six natural full-form shadow cases

P1 is encoded but not executed. Slots are not cases or evidence until a naturally
occurring canonical Bureau intake is admitted prospectively. Each slot uses the
full form in shadow only and has zero effect on execution.

| Slot | Admission requirement | Frozen output | Shadow observation |
| --- | --- | --- | --- |
| `P1-01` | first eligible natural intake | one full spec before mutation | append after registered window |
| `P1-02` | second eligible natural intake | one full spec before mutation | append after registered window |
| `P1-03` | third eligible natural intake | one full spec before mutation | append after registered window |
| `P1-04` | fourth eligible natural intake | one full spec before mutation | append after registered window |
| `P1-05` | fifth eligible natural intake | one full spec before mutation | append after registered window |
| `P1-06` | sixth eligible natural intake | one full spec before mutation | append after registered window |

Admission order cannot be backfilled with synthetic or retrospective cases.
Distance and risk are assessed from the admitted intake, not pre-assigned to make
the sample look balanced. P1 may assess usability and missing fields only; it
cannot support minimal-versus-full efficacy.

## P3 design — six matched minimal/full pairs

P3 is encoded but not executed. After an independently reviewed P1 closeout, use
six newly admitted or prospectively preserved natural cases. For each pair
`P3-01` through `P3-06`, render the same intake, desired change and falsifier in
minimal and full form before outcome review. Freeze both digests and measure form
handling time separately. Neither rendering may influence route, queue, runtime,
policy, merge, deployment or technical closeout.

Minimal wins by default. Full may be proposed for a later reviewed pilot only if
all conditions hold across the six pairs:

1. full yields at least two additional distinct actionable decisions;
2. median full-form handling overhead is no more than `2x` median minimal-form
   handling overhead;
3. median full-form handling overhead is no more than `10 minutes`;
4. authority violations equal zero.

One additional actionable decision is inconclusive. Field completeness, prose
volume and reviewer preference are not actionable decisions.

## Stop conditions

Stop admission or assessment and preserve the current records if any condition
occurs:

- productive mutation begins before the applicable spec is frozen;
- a spec or observation digest fails to resolve exactly;
- an existing observation would need mutation rather than an appended correction;
- technical closeout truth would need to be copied rather than referenced;
- operator-intake, execution-source identity or authority roles cannot be kept
  distinct;
- evidence authority or observation window is missing;
- a case is synthetic, retrospective, backfilled or selected after its outcome;
- privacy or secrets would require raw transcript or raw response capture;
- any Vibe-Lab artifact attempts Bureau, Grabowski, Chronik, Leitstand, runtime,
  routing, queue, policy, merge-policy or deployment integration;
- any automatic policy, routing, queue, merge, deployment or runtime effect occurs;
- P1 or P3 reaches expiry without the registered reviewed closeout.

An authority violation is an immediate failure, not an overhead trade-off.
