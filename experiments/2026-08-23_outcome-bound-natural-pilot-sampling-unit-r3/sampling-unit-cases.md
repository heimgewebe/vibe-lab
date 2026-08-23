# Frozen adversarial sampling-unit R3 cases

These cases are author-side frozen inputs for exact-head review. The reviewer must derive the
slot assignment, slot consumption and natural-evidence disposition from `method.md` alone. `A` is
a hypothetical already-frozen activation-boundary event id; this paper revision does not choose a
real `A`.

| ID | Frozen situation | Assigned slots | Consumed slots | Natural evidence | Expected action |
| --- | --- | ---: | ---: | --- | --- |
| R01 | Identity `candidate-pre` was born at event 90 (`<= A`) with `operator_intake`; event 1200 (`> A`) later supersedes it. | 0 | 0 | none | continue; the later event is not a birth |
| R02 | Identity `candidate-natural` has its proven first event at 1300 (`> A`) with `operator_intake`; independence from the experiment is supported by pre-existing evidence. | 1 | 1 | accepted | continue |
| R03 | **Adversarial interference case.** Identity `candidate-induced` has its proven first event at 1310 (`> A`) with `operator_intake`, but the experiment caused the candidate to be delayed and reprioritized before birth. | 1 (next fixed ordinal) | **1** | **rejected_interference** | **fail closed; REJECT_THIS_REVISION; never reinterpret as zero slots** |
| R04 | Identity `candidate-ambiguous` has a proven post-`A` birth, but the same operator runs the experiment and no pre-existing evidence establishes independence. | 1 (next fixed ordinal) | 1 | rejected_ambiguous_causation | fail closed; ordinal remains consumed |
| R05 | Proven births occur at 1400, 1401 and 1402. The middle birth is experiment-influenced. | ordinals 1, 2, 3 are fixed before gates | evaluation consumes 1 then 2; stop at 2 | slot 1 accepted; slot 2 rejected; slot 3 not evaluated | reject at 2; slot 3 cannot replace or be relabelled as 2 |
| R06 | Candidate-looking event at 1500 cannot be proven to be its identity's first event because the event-journal read reports incomplete coverage. | 0 speculative slots | 0 | none | stop at construction gate; no soft skip/backfill |
| R07 | A proven post-`A` birth at 1600 is followed by intake enrichment and supersessions at 1601 and 1700. | 1 | 1 if gate reached | based only on the birth slot gate | later events never create additional slots |
| R08 | A replay uses the same idempotency key and creates no authoritative event. | 0 | 0 | none | no event, no birth, no slot |
| R09 | Two content-equivalent but canonically distinct identities are proven born at 1800 and 1801. | 2 ordered slots | sequential | separately gated | content similarity cannot merge or reorder them |

## Required counter-review attacks

The independent exact-head reviewer must explicitly try to recover each forbidden reading:

1. `R03 => assigned=0, consumed=0` because interference fails naturalness;
2. `R03 => assigned=1, consumed=1, natural_evidence=accepted` because the birth itself is valid;
3. drop R03 and renumber the next birth into its ordinal;
4. apply the naturalness/self-interference predicate while building the Phase-S sequence;
5. turn R06's incomplete birth proof into a skip and continue with a later birth;
6. find a `checked`, `supports_primary`, PASS-like, or otherwise favorable counter-hypothesis label
   in the frozen author revision that predates independent review evidence.

Any protocol-conforming path to attacks 1-6 is material and rejects the revision. A review PASS is
valid only if all six attacks fail and the reviewer is bound to the exact frozen author head.
