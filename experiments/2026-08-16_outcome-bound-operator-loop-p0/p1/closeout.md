# P1 Early-Stop Closeout

## Status

P1 is closed early under `p1/cohort-protocol.v1.yml` revision 1. The cohort stop was triggered at P1-02 because independent review established that productive mutation had already begun before the applicable Stage A record was created.

This closeout is process and usability/observability evidence only. It is not an efficacy assessment of the Outcome Case method, does not compare Minimal versus Full form, does not authorize P2 or P3, and grants no productive authority to Vibe-Lab.

## Publication order

The required successor current decision and coherent active-registry removal were published first in commit `48fb4a87aec37bc6acc77f0b989b2a4f4ef2599e` on PR #338. That revision contains no `p1/closeout.md`. This closeout was created only after that first state had been pushed and the PR opened.

## Cohort accounting

| Item | Count | Interpretation |
|---|---:|---|
| Slots registered | 6 | P1-01 through P1-06 |
| Assigned and consumed | 2 | P1-01 and P1-02 |
| Protocol-valid prospective normal cases | 1 | P1-01 only |
| Preserved stop-triggering consumed cases | 1 | P1-02; original prospective classification is not endorsed after review |
| Preserved vacant slots after stop | 4 | P1-03 through P1-06; no later assignment allowed |
| Recorded Stage-B `full_spec_frozen_before_productive_mutation` records | 2 | P1-01 plus the preserved P1-02 record; this count is historical-record count, not valid-case count |
| Protocol-valid prospective normal Stage-B outcomes | 1 | P1-01 |
| `form_completion_failed_or_not_frozen` records | 0 | None |
| Authority violations | 0 | The P1-02 admission error is a protocol-eligibility failure, not a productive authority violation |

P1-02 remains permanently consumed. It is not replaced or backfilled. P1-03 through P1-06 remain vacant because the cohort stop terminates further assignment and assessment.

## Stop-rule evidence

The stop condition is exactly:

`Productive mutation had already begun before the applicable Stage A record was created.`

For P1-02, PR #2014 and PR #2015 had already merged and T033/T034 had already been productively published into the authoritative Bureau StateStore before the candidate and before Stage A. Protocol revision 1 contains no exception limiting `productive mutation` to the newly proposed repair implementation.

Independent eligibility review:

- reviewer: Codex architecture, read-only eligibility audit
- job: `grabowski-job:8e1b296f1a7b`
- receipt: `d2a145c94ef647ec2873c119e5eed420c4ac701f5d9d1a3ed5ce835e4825977c`
- payload: `5c5e28403f2a608a5f7a575858d60a4c72f0c712ccd69ce90fc9019da5e9e896`
- append-only correction: `p1/cases/P1-02/eligibility-correction.yml`

The original P1-02 Stage A, Full Spec, Stage B, trigger-provenance and run-meta records are preserved unchanged. The correction changes cohort interpretation only; it does not rewrite history.

## P1 usability and observability measurements

### P1-01 — valid prospective normal case

- Full-form handling time: **82.660682 s**
- Time through persistent materialization: **107.365738 s**
- Full spec schema validation: PASS
- Digest validation: PASS
- Scope change identified before mutation: no
- Intervention change identified before mutation: no
- Verifier distinction surfaced: yes, experiment-only and not applied to productive work
- Fields with handling friction:
  - `distance_and_risk.distance` — unclear boundary
  - `distance_and_risk.risk` — context-sensitive
  - `alternative_path` — possibly redundant for this D2 case
- Effect observation in the preserved case record: `pending`
- Authority violations: 0

### P1-02 — preserved stop-triggering capture, not a valid prospective case

The following numbers are retained as historical handling evidence only and are **excluded from any prospective efficacy or valid-cohort aggregate**:

- Recorded Full-form handling time: **63.0 s**
- Recorded time through persistent materialization: **146.150419 s**
- Full spec schema validation: PASS
- Digest validation: PASS
- Fields with handling friction recorded before the eligibility correction:
  - `distance_and_risk.distance` — D1/D2 boundary
  - `alternative_path` — possibly redundant for this D2 case
  - `observation_plan.indicator` — technical CAS versus downstream claimability verifier boundary
- Preserved effect state: `pending`; it is not interpreted as a cohort-valid effect observation after the eligibility correction
- Authority violations: 0

The P1-02 data demonstrate that technically consistent and hash-bound capture can still be epistemically invalid for a prospective cohort when admission timing is wrong. Technical schema validity did not rescue eligibility.

## No replacement or backfill

No failed, excluded or stop-triggering slot was replaced. P1-02 remains the second consumed slot. The later vacant slots were not searched for substitute cases after the stop.

## Authority assessment

No P1 artifact promoted a Bureau candidate, created a Bureau task, changed task readiness, claimed work, altered routing or queue state, changed priority, merged or deployed productive code, or relabeled a technical closeout. Bureau, GitHub/CI, Grabowski and runtime authorities remained separate.

The P1-02 error was narrower but important: the controller initially interpreted `productive mutation` as if it meant implementation of the newly proposed repair. Independent review showed that the frozen protocol text is broader. That is a cohort-admission semantics failure, not an authority violation.

## Limitations and non-claims

- Only P1-01 is a genuinely prospective, protocol-valid normal case.
- P1-02 is retained because immutable evidence must not be rewritten, but it cannot count as a valid prospective efficacy case.
- Four registered slots remain vacant because the stop rule terminates the cohort early.
- P1-01, the single protocol-valid prospective case, has no completed domain-effect observation in P1. Both preserved Stage-B case records carry historical `pending` effect states, but P1-02's state is not interpreted as cohort-valid after the eligibility correction.
- P1 contains no Minimal-form control arm.
- There is no six-case valid sample and no matched Minimal-versus-Full comparison.
- P1 therefore cannot estimate Decision Impact, relative overhead, false-completion prevention, or whether Full form beats Minimal form.
- No conclusion is supported about which semantic distance should use which form.
- `status: inconclusive` means the planned efficacy question remains unanswered, not that the technical artifacts failed.

## P2 and P3

P2 is **not justified automatically** by this closeout. One preventable problem was observed here in cohort-admission semantics (`productive mutation` scope); recurrence is not established, and the problem is not missing case-schema syntax or digest validation. Building a validator merely because P2 appeared in the original plan would add the kind of meta-infrastructure this experiment is meant to avoid. Any validator proposal needs separate evidence that a small mechanical check can prevent this class of error without inventing a new authority.

P3 is **not authorized**. The registered matched Minimal-versus-Full comparison cannot be inferred from or launched by this early-stopped P1. A future comparison would require a separately reviewed successor protocol or experiment and separate execution authorization.

## Independent closeout review

- required reviewer identity: Codex architecture exact-head semantic reviewer
- review reference: PR #338 (`github:heimgewebe/vibe-lab#338`)
- review scope: frozen protocol compliance; commit-order proof; P1-02 preservation and append-only correction; cohort counts; no replacement/backfill; usability/observability claims; authority boundaries; explicit Minimal-versus-Full, P2 and P3 non-claims
- review status at closeout creation: **pending exact-head review**

Acceptance of this closeout remains contingent on the independent exact-head review and hosted CI for the revision containing this file. The review result is external revision-bound evidence and does not require rewriting the immutable P1-02 capture records.
