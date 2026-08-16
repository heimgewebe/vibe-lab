---
title: "Outcome-Bound Operator Loop P0 — Method and future protocols"
status: testing
canonicality: operative
created: "2026-08-16"
updated: "2026-08-16"
triggered_by: "conversation:user-request-2026-08-16-outcome-bound-operator-loop; codex-review:heimgewebe/vibe-lab#329-P2; github:heimgewebe/vibe-lab#332; codex-review:heimgewebe/vibe-lab#333"
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
  - type: references
    target: p1/activation.md
  - type: references
    target: p1/decision.yml
---

# Method and future protocols

## Goal-type separation

P0 combines two declared goal types without crossing their boundaries:

1. **Construction:** define experiment-local paper schemas and examples.
2. **Analysis:** map exactly three existing records for compatibility without
   changing them or making prospective, causal or efficacy claims.

P0 remains complete paper/schema-fit work. P1 is now prepared under the frozen
activation at `p1/activation.md` and the protocol `activation_state`; their 0/6
slots assigned, zero case identities and zero outcome evidence describe only the
frozen activation snapshot, not mutable current live progress or the current
decision contents. `p1/decision.yml` deliberately carries the stable
insufficient-proof assessment for full six-case cohort completion plus its
independently reviewed closeout; mutable Stage A and Stage B progress lives only
in separate append-or-create-only capture records. The historical P0 assessment
remains unchanged at `results/decision.yml`. P3 remains design-only and
prohibited before an independently reviewed P1 closeout plus separate execution
authorization. No downstream system changes.

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

## P1 activation — six prospective two-stage full-form shadow captures

P1 protocol revision 1 is frozen at `p1/cohort-protocol.v1.yml`; its
`activation_state` and the bounded receipt at `p1/activation.md` record the
frozen activation snapshot: 0/6 slots assigned, zero case identities and zero
outcome evidence. Those snapshot values are not mutable current live progress
and are not the current decision contents. `p1/decision.yml` deliberately
carries the stable insufficient-proof assessment for full six-case cohort
completion plus its independently reviewed closeout, while mutable Stage A and
Stage B progress lives only in separate append-or-create-only capture records.
Activation does not execute an efficacy comparison.

Eligibility is determined from the independently occurring canonical Bureau
intake before productive mutation. It does **not** require that the full form can
be completed or frozen. Capture then has two ordered stages:

1. **Stage A — screening and slot assignment.** Before any full-form attempt,
   create a separate append-or-create-only record that consumes the next ordered
   slot and binds the canonical intake reference, screening and assignment time,
   and proof that productive mutation had not begun. The Stage A record neither
   requires nor contains a full-spec digest.
2. **Stage B — full-form attempt.** Attempt the full form in shadow. If a complete
   spec is frozen before productive mutation, record its reference, digest,
   freeze timing and handling time as the normal form outcome. If completion or
   freeze cannot occur before productive mutation would naturally begin, record
   `form_completion_failed_or_not_frozen`, handling time, unclear or redundant
   fields and a bounded reason, then stop P1 capture for that slot while
   productive work proceeds unchanged.

| Slot | Activation state | Stage A transition | Stage B outcomes |
| --- | --- | --- | --- |
| `P1-01` | vacant | first eligible intake consumes slot | normal or explicit failed/not-frozen outcome |
| `P1-02` | vacant | second eligible intake consumes slot | normal or explicit failed/not-frozen outcome |
| `P1-03` | vacant | third eligible intake consumes slot | normal or explicit failed/not-frozen outcome |
| `P1-04` | vacant | fourth eligible intake consumes slot | normal or explicit failed/not-frozen outcome |
| `P1-05` | vacant | fifth eligible intake consumes slot | normal or explicit failed/not-frozen outcome |
| `P1-06` | vacant | sixth eligible intake consumes slot | normal or explicit failed/not-frozen outcome |

Every Stage A assignment permanently consumes its slot. A failed or non-frozen
Stage B attempt stays in the six-slot cohort and cannot be replaced or backfilled.
It is a P1 usability or observability finding, not an outcome-effect assessment
and not P3 efficacy evidence. P1 has no minimal-form comparator and cannot support
minimal-versus-full efficacy. Screening, form handling and findings must never
block, delay, reroute, reprioritize or otherwise alter productive work.

## P3 design — six matched minimal/full pairs

P3 is encoded but not executed. Only after an independently reviewed P1 closeout
and a separate P3 execution authorization may six newly admitted or
prospectively preserved natural cases be used. For each pair
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

Stop cohort assignment or assessment and preserve the current records if any condition
occurs:

- productive mutation had already begun before the applicable Stage A record;
- a spec or observation digest fails to resolve exactly;
- an existing screening, form-outcome or observation record would need mutation
  rather than an appended correction;
- technical closeout truth would need to be copied rather than referenced;
- operator-intake, execution-source identity or authority roles cannot be kept
  distinct;
- evidence authority or observation window is missing;
- a case is synthetic, retrospective, backfilled, replaced or selected after its
  outcome;
- privacy or secrets would require raw transcript or raw response capture;
- any Vibe-Lab artifact attempts Bureau, Grabowski, Chronik, Leitstand, runtime,
  routing, queue, policy, merge-policy or deployment integration;
- any blocking, delay, rerouting, reprioritization, automatic policy, queue,
  merge, deployment or runtime effect occurs;
- P3 starts before an independently reviewed P1 closeout and separate P3
  execution authorization;
- P1 or P3 reaches expiry without the registered reviewed closeout.

A Stage B `form_completion_failed_or_not_frozen` outcome is not a cohort stop: it
stops capture for that consumed slot and productive work continues unchanged. An
authority violation is an immediate cohort failure, not an overhead trade-off.
