# Frozen adversarial sampling-unit cases

These cases are frozen paper inputs. A counter-reviewer must derive every disposition from
`method.md` alone, without adding a rule. `A` is the frozen activation boundary event id from
`method.md` section 3.

Dispositions and slot consumption are frozen **before** any counter-check.

| ID | Class | Frozen situation | Author disposition | Slots consumed | Reason |
| --- | --- | --- | --- | --- | --- |
| U01 | born before A, later supersessions | Identity `candidate-a` has `identity_first_event` at event 40 (`<= A`) carrying `operator_intake`. After `A`, events 900, 905 and 930 supersede and re-enrich it. | `preexisting_identity_no_unit` | 0 | Birth is anchored at event 40, which is at or below `A`. Supersession is not arrival; no post-`A` event of this identity can be reconstructed as a birth. |
| U02 | born after A, later supersessions | Identity `candidate-b` has `identity_first_event` at event 1010 (`> A`) carrying `operator_intake`; events 1011, 1040 and 1200 supersede or correct it. | `one_identity_one_slot_at_event_1010` | 1 | Exactly one unit, anchored at event 1010. Every later event of the same identity is context, never an additional unit. |
| U03 | several new IDs in close succession | Events 1300, 1301 and 1302 are three distinct identity births, each carrying `operator_intake`, all `> A`, within the same second. | `three_units_ordered_1300_1301_1302` | 3 | Ordering is by `event_id` ascending. Temporal closeness is not batching, not a tie, and never a reason to collapse or sample among them. |
| U04 | content-equivalent intake events | Events 1400 and 1401 are two distinct identities whose intake payloads are materially equivalent (same source locator, near-identical title and desired outcome), both `> A`. | `two_units_ordered_1400_1401` | 2 | The unit key is canonical candidate identity, never content. Content similarity is not a dedup rule; introducing one would be a post-observation degree of freedom. |
| U05 | incompletely provable history | For an anchor candidate at event 1500 the journal read reports `history_truncated` and cannot enumerate every `candidate_task` event with `event_id <= 1500` without gaps. | `birth_proof_incomplete_fail_closed_stop` | 0 (sequence stops) | Section 6. The pilot must not widen, re-read with a different rule, or choose grouping semantics after seeing the data. The stop is terminal for the revision, not a skip of this slot. |
| U06 | legacy root before A, explicit successor after A | Event 60 (`<= A`) is a legacy `candidate_task` without stored `candidate_id`; event 1600 (`> A`) carries `candidate_id=candidate-event-60` plus `operator_intake`. | `preexisting_identity_no_unit` | 0 | Canonical normalization joins both events into identity `candidate-event-60`, whose `identity_first_event` is event 60. A later explicit id can never hide an older canonical root. |
| U07 | idempotent replay | A post-`A` intake request is replayed with the same idempotency key and produces no new authoritative event. | `no_event_no_unit` | 0 | A unit is anchored on an authoritative event. No event, no arrival, no unit — regardless of how many client calls occurred. |
| U08 | observer-adjacent operator work | After `A`, the same human/agent identity that will run the pilot records Bureau candidates in unrelated operator work (for example the Bureau bottleneck diagnosis candidates `candidate-ba0a8f5bc6287d310c347f52` and `candidate-0a860a6b490e6e8918fc578a` recorded on 2026-08-20). The next fixed slot lands on one of them. | `slot_fixed_then_independence_must_be_evidenced` | 1 | Section 7. The ordinal is consumed either way. Independence from Outcome-Bound must be shown from pre-existing artefacts; if it cannot be, the case is ambiguous causation and fail-closed rejects the pilot revision. It is never skipped. |
| U09 | supersession observed before birth | A post-`A` identity is born at event 1700; the observer's first sighting is the supersession at event 1705, and only then does it discover event 1700. | `one_unit_anchored_at_event_1700` | 1 | The anchor is fixed by the complete journal, not by observer arrival order. The supersession is context; the birth snapshot remains the claim anchor. |

## Counter-reviewer attacks

The counter-check must additionally try to construct a protocol-conforming result by:

1. treating a post-`A` supersession of a pre-`A` identity as a new arrival;
2. treating a later intake-enrichment event as an identity birth;
3. collapsing several near-simultaneous births into one unit, or sampling among them;
4. deduplicating two content-equivalent identities into one unit;
5. recovering from an incomplete birth proof by widening the read or picking a grouping rule after observation;
6. hiding a legacy no-ID root behind a later explicit candidate id;
7. counting an idempotent replay as an arrival;
8. skipping an observer-adjacent candidate instead of consuming its ordinal;
9. using observer sighting order, wall-clock timestamps or `created_at` instead of authoritative `event_id`;
10. reading "event arrival", "identity birth" and "supersession" as interchangeable anywhere in `method.md`.

Any credible escape is material and rejects this revision.
