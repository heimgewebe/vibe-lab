# S1-R2 fixed adversarial sampling cases

These cases are frozen paper inputs. Reviewers must derive each disposition from `method.md` without adding a new sampling rule.

| ID | Frozen situation | Author disposition | Reason |
| --- | --- | --- | --- |
| P01 | Event 25 is a pre-boundary legacy `candidate_task` with no stored `candidate_id`; post-boundary event 900 explicitly uses `candidate_id=candidate-event-25` and carries `operator_intake`. | `preexisting_identity_no_unit` | Normalize event 25 to `candidate-event-25` before grouping. Event 25 is the identity-first event and lacks the required post-boundary Operator-Intake birth. |
| P02 | Post-boundary event 500 is a legacy no-ID `candidate_task` and itself carries `operator_intake`; there is no older event for its canonical identity. | `fixed_slot_requires_naturalness_check` | Normalize to `candidate-event-500`; the identity-first event itself carries intake and is a genuine identity birth for sequencing. |
| P03 | Post-boundary event 510 has explicit `candidate_id=candidate-new`, carries `operator_intake`, and has no older normalized event for that identity. | `fixed_slot_requires_naturalness_check` | New explicit identity; naturalness is checked only after its ordinal is fixed. |
| P04 | Event 520 creates explicit `candidate-x` without `operator_intake`; event 530 later adds `operator_intake` to the same identity. | `preexisting_identity_no_unit` | Identity-first event lacks intake; later enrichment cannot create a new Operator-Intake birth. |
| P05 | Legacy event 540 has no stored ID and no `operator_intake`; event 550 uses `candidate_id=candidate-event-540` and adds intake. | `preexisting_identity_no_unit` | Canonical normalization joins both events before the intake-birth test. |
| P06 | Event 560 is a new intake birth for `candidate-y`; events 561 and 562 supersede/refine it. | `one_identity_one_slot` | All three normalize to one identity; only the first event can establish the slot. |
| P07 | A post-boundary intake request deduplicates onto an identity whose normalized root predates the boundary. | `preexisting_identity_no_unit` | Deduplication cannot manufacture a new identity birth. |
| P08 | After a future natural experiment activates, its observer deliberately calls candidate intake to manufacture an easy candidate that becomes the next fixed ordinal. | `source_independence_failure_reject` | Sequence is fixed before naturalness; the manufactured candidate is not skipped and therefore falsifies the natural revision. |
| P09 | An always-on watchdog independently creates the next candidate from a source observation already produced without any Outcome-Bound action; the candidate would exist unchanged without the experiment. | `naturalness_established_for_fixed_slot` | Existing source evidence supports the counterfactual and observer non-interference. |
| P10 | The next fixed candidate has a plausible source locator but evidence cannot establish whether the experiment prompted or materially shaped its creation. | `source_independence_failure_reject` | Ambiguous causation is fail-closed and never a reason to skip the ordinal. |
| P11 | The experiment delays, reprioritizes or asks another actor to time a candidate so a preferred identity lands in the first three. | `integrity_failure_reject` | Treatment-generation/timing effects attributable to the experiment violate non-interference even if the resulting candidate content is otherwise valid. |
| P12 | Unrelated operator work reprioritizes a candidate for its own independently evidenced operational reason; the Outcome-Bound experiment neither requested nor influenced the change. | `naturalness_may_still_be_established` | The counterfactual is relative to the experiment, not to every external cause. The fixed slot still needs evidence of independence from Outcome-Bound. |
| P13 | A natural new identity is fixed as a slot; a correction/supersession arrives before the observer starts its capture. | `same_fixed_slot_original_claim_anchor` | Correction timing does not create or replace an identity. Later evidence may be context but cannot replace the identity-first claim snapshot. |
| P14 | A source-independent fixed slot is D0 / `not_applicable` under S0-R3. | `slot_kept_no_backfill` | D0 is downstream of fixed sequence and naturalness; it is never a selection filter. |
| P15 | A source-independent fixed slot is first observed only after productive mutation began. | `slot_kept_capture_failure` | Missed capture is downstream evidence; the ordinal remains fixed and a natural pilot would reject under its capture gate rather than backfill. |
| P16 | A source-independent fixed slot is first observed after its target-effect result is already known. | `slot_kept_result_informed_failure` | Result knowledge cannot remove or replace the slot and cannot authorize retrospective shaping. |
| P17 | Two independently natural Operator-Intake births have identical timestamps but authoritative event IDs 700 and 701. | `event_700_before_event_701` | Event ID, not timestamp or observer arrival order, is the deterministic tie-breaker. |

| P18 | Two exact-head reviewer jobs are both terminal before merge: reviewer A reports one material `REJECT_THIS_REVISION`; reviewer B reports `PASS_THIS_REVISION`. The controller has read only reviewer B so far. | `merge_blocked_until_reconciled_then_reject` | Every decision-bound review must be terminal and explicitly reconciled. One material REJECT is sufficient; PASS is never decided by majority or last-read result. |

## Reviewer attacks

Each reviewer must additionally try to construct a protocol-conforming PASS by:

1. hiding a legacy no-ID root behind a later explicit candidate ID;
2. treating later intake enrichment as identity birth;
3. manufacturing a candidate and then excluding it as non-natural;
4. relabelling experiment-induced timing as ordinary operator work;
5. skipping a causally ambiguous candidate;
6. using a later correction as the claim snapshot;
7. using D0, missed capture or result knowledge as a selection filter;
8. choosing timestamp/observer order instead of authoritative event ID;
9. merging after reading one PASS while another already-terminal decision-bound review remains unread or materially rejects.

Any credible escape is material and rejects the author revision.
