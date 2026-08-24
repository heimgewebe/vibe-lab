# Frozen adversarial sampling-unit R3 v3 cases

These are R3 v3 author-side frozen inputs for exact-head review. The reviewer must derive slot construction,
slot consumption and natural-evidence admission from `method.md` alone. `A` is a hypothetical already
frozen activation-boundary event id; R3 v3 does not choose a real `A` or observe a natural case.

| ID | Frozen situation | Assigned slots | Consumed slots | Natural evidence | Expected action |
| --- | --- | ---: | ---: | --- | --- |
| R01 | Identity `candidate-pre` was born at event 90 (`<= A`) with `operator_intake`; event 1200 (`> A`) later supersedes it. | 0 | 0 | none | continue; later event is not a birth |
| R02 | Identity `candidate-natural` has its fully proved first event at 1300 (`> A`) with `operator_intake`; independence is supported by pre-existing evidence. | 1 | 1 | accepted | continue |
| R03 | **Adversarial interference case.** Identity `candidate-induced` has a fully proved first event at 1310 (`> A`) with `operator_intake`. Before birth, the experiment caused the candidate to be delayed and reprioritized. | **1 fixed ordinal** | **1** | **0 accepted; `rejected_interference`** | **fail closed; `REJECT_THIS_REVISION`; zero-slot and one-slot-plus-natural-acceptance readings are both wrong** |
| R04 | Identity `candidate-reshaped` has a fully proved first event at 1320 (`> A`), but the experiment caused its semantics to be reshaped before birth. | 1 fixed ordinal | 1 | 0 accepted; `rejected_interference` | fail closed; semantic influence cannot erase or admit the slot |
| R05 | Identity `candidate-ambiguous` has a fully proved post-`A` birth, but the same operator runs the experiment and no pre-existing evidence establishes independence. | 1 fixed ordinal | 1 | 0 accepted; `rejected_ambiguous_causation` | fail closed; ordinal remains consumed |
| R06 | Fully proved births occur at 1400, 1401 and 1402. The middle birth is experiment-influenced. | ordinals 1, 2, 3 are fixed before gates | evaluation consumes 1 then 2; stop at 2 | slot 1 accepted; slot 2 rejected; slot 3 not evaluated | reject at 2; slot 3 cannot replace or be relabelled as 2 |
| R07 | Candidate-looking event at 1500 cannot be proved to be its identity's first event because the event-journal read reports incomplete coverage. | 0 speculative slots | 0 | none | stop at construction gate; no soft skip, speculative slot or backfill |
| R08 | A fully proved post-`A` birth at 1600 is followed by intake enrichment and supersessions at 1601 and 1700. | 1 | 1 if gate reached | based only on the birth slot gate | later events never create additional slots |
| R09 | Two content-equivalent but canonically distinct identities are fully proved born at 1800 and 1801. | 2 ordered slots | sequential | separately gated | content similarity cannot merge or reorder them |

## Deterministic R03 oracle

The reviewer must treat this tuple as frozen before review:

```text
assigned_slots_for_candidate_induced = 1
consumed_slots_for_candidate_induced = 1
accepted_natural_evidence_for_candidate_induced = 0
disposition = rejected_interference
revision_action = REJECT_THIS_REVISION
```

R03 is intentionally adversarial against both common misreadings:

- **zero-slot error:** interference is incorrectly applied during Phase S and the proved birth disappears;
- **one-slot-plus-natural-acceptance error:** the slot is kept, but slot existence is incorrectly treated as proof of naturalness.

## Required counter-review attacks

The independent exact-head reviewer must explicitly try to recover each forbidden reading:

1. recover the R2 sentence contradiction: "one slot is forbidden" and "one slot is required" for the same interfered birth;
2. `R03 => assigned=0, consumed=0` because interference fails naturalness;
3. `R03 => assigned=1, consumed=1, natural_evidence=accepted` because the birth itself is valid;
4. apply naturalness/self-interference while constructing the Phase-S sequence;
5. drop R03 and renumber the next birth into its ordinal;
6. turn R07's incomplete birth proof into a soft skip or speculative slot and continue;
7. find a `checked`, support/PASS-like, or otherwise favorable counter-hypothesis/result label in the frozen author revision that predates independent review evidence;
8. regenerate all CI-blocking generated artifacts and find any diff or missing commit-required projection at the frozen author head;
9. run the full CI validation prefix and find any tracked mutation or dirty-tree state before replay mutation guard.

Any protocol-conforming path to attacks 1-9 is material and rejects R3 v3. A favorable review is valid
only if all nine attacks fail against the exact frozen author head.
