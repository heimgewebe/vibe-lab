---
title: "Outcome-Bound Operator Loop Successor S0-R3 — Fixed adversarial paper cases"
status: designed
canonicality: operative
created: "2026-08-17"
updated: "2026-08-17"
triggered_by: "github:heimgewebe/vibe-lab#343"
---

# Fixed S0-R3 paper cases

These are frozen author assessments for independent review. They are paper probes,
change no predecessor record and provide no natural-cohort or efficacy evidence.

| ID | Case | Frozen C/S/B/E/T/Q summary | Author status |
|---|---|---|---|
| R3-01 | create then preserve | absent config → canonical config already occurred; later work adds regeneration/durability | `ineligible` |
| R3-02 | create then mutate | existing `planned` TaskSpec → same revision `ready`; prior creation only established B | `eligible` |
| R3-03 | repair then durability | unhealthy → healthy repair already succeeded; later work automates/persists same T | `ineligible` |
| R3-04 | pure prerequisite | stale runtime → exact target runtime; prior authority mint is an enabling input on another subject | `eligible` |
| R3-05 | satisfied effect + qualifier padding | blocked pickup → successful ordinary pickup already occurred; later label adds reliability/automation prose | `ineligible` |
| R3-06 | D0 technical acceptance | technical acceptance is the whole effect | `not_applicable` |
| R3-07 | equivalent scratch subject | same failed → healthy T already executed on evidence-supported equivalent subject | `ineligible` |
| R3-08 | ambiguous subject equivalence | same-looking T on a clone, but frozen evidence does not establish equivalence | `indeterminate` |

## R3-01 — create then preserve

**Frozen facts**

1. Baseline before the earlier act: no canonical config artifact exists.
2. An operator manually creates the canonical artifact with the exact target
   payload; authoritative readback confirms it.
3. Only afterwards a candidate proposes automatic regeneration and restart
   durability of that same target artifact.

**C:** before the manual creation, the frozen source claim says the desired change is that the canonical target artifact exists. Regeneration/durability are not independently claimed effects in C.

**S:** canonical config artifact state.

**B:** artifact absent.

**E:** canonical artifact with the target payload exists.

**T:** `absent -> canonical-target-artifact`.

**Q:** automatic regeneration, restart durability.

The earlier act made E true and executed T. Q does not create a new lineage.

**Status:** `ineligible`.

## R3-02 — create then mutate (`planned -> ready`)

**Frozen facts**

1. A prior publication creates revision-1 TaskSpec T033 in authoritative state
   `planned` with a fixed digest.
2. Readback confirms the missing post-merge readiness transition.
3. No `planned -> ready` CAS, implementation or benchmark has occurred.
4. A candidate is then bound to verify exact revision/digest/merge identity and
   perform one `planned -> ready` CAS with readback.

**C:** after authoritative readback of the already-created `planned` TaskSpec exposes the readiness gap and before any readiness CAS, the frozen source claim selects `planned -> ready` as the desired change.

**S:** the existing revision-1 T033 TaskSpec.

**B:** that exact TaskSpec exists in `planned` with the frozen digest.

**E:** that same revision/digest is authoritative in `ready`.

**T:** `planned -> ready` CAS on the same TaskSpec.

**Q:** typed, revision-bound, one-shot verification.

The prior `absent -> planned` publication establishes B but neither makes E true
nor executes T.

**Status:** `eligible`.

This case is intentionally close to rejected R2-02/R2-08 and tests whether R3
avoids both "creation is already a material sub-effect" ambiguity and P1's blanket
prior-mutation prohibition.

## R3-03 — manual repair then automated durable repair

**Frozen facts**

1. A service is unhealthy because state X is missing.
2. An operator manually performs the repair; authoritative readback shows healthy.
3. After observing success, a candidate proposes the same repair automatically and
   persists it across restart.

**C:** before the manual repair, the frozen source claim selects restoration to healthy/X-restored as the desired change; automation and restart persistence are delivery qualifiers, not separate effects in C.

**S:** service recovery state.

**B:** unhealthy/missing-X.

**E:** service is healthy with X restored.

**T:** `unhealthy/missing-X -> healthy/X-restored`.

**Q:** automation, restart persistence, repetition.

The earlier act already made E true and executed T. Later delivery qualifiers do
not create a fresh intervention lineage.

**Status:** `ineligible`.

## R3-04 — pure prerequisite before distinct runtime transition

**Frozen facts**

1. Installed runtime is stale relative to exact current `main`.
2. A fresh single-use authority object is minted but not consumed.
3. Minting the authority does not modify the installed runtime.
4. A candidate is then bound to consume that authority through the existing
   refresh mechanism and converge the runtime to exact `main`.

**C:** before the authority is minted, the frozen source claim selects convergence of the installed runtime to exact target `main` as the desired change.

**S:** installed runtime revision.

**B:** stale installed runtime plus a valid unused authority.

**E:** installed runtime revision equals the exact target `main` revision.

**T:** `stale-runtime -> exact-target-runtime` refresh.

**Q:** single-use authority, exact revision verification.

The authority mint is an enabling input on a different state-bearing object. It
neither makes E true nor executes T on S.

**Status:** `eligible`.

## R3-05 — already satisfied effect with qualifier-padding relabel

**Frozen facts**

1. Ordinary atomic pickup is blocked.
2. A productive intervention restores ordinary atomic pickup and authoritative
   readback confirms success.
3. After that result is known, a candidate is worded as "make pickup reliable and
   automatic" without identifying a distinct state transition beyond the same
   successful pickup path.

**C:** before the first successful restoration, the frozen source claim selects successful ordinary canonical pickup as the desired change. The later reliability/automation wording does not replace C for this same case.

**S:** ordinary atomic pickup capability.

**B:** blocked pickup.

**E:** ordinary atomic pickup succeeds through the canonical path.

**T:** `blocked -> successful-canonical-pickup`.

**Q:** reliability/automatic-operation wording only; no distinct T is evidenced.

The earlier act already made E true and executed T. Post-success qualifier padding
cannot establish a new prospective case.

**Status:** `ineligible`.

## R3-06 — D0 technical-acceptance control

A docs-only change has the complete desired effect "the changed files satisfy the
registered schema and authoritative repository validation". There is no claimed
downstream product/operator effect.

**Status:** `not_applicable`.

No S/B/E/T admission contract is required because an Outcome Case would duplicate
the technical closeout.

## R3-07 — same transition on explicitly equivalent scratch subject

**Frozen facts**

1. A scratch fixture uses the same implementation function, state schema and
   transition contract as the later production target; these equivalence facts are
   bound before the candidate wording.
2. A scratch patch executes `failed -> healthy` and a benchmark/readback confirms
   success.
3. Only afterwards a candidate proposes to package and deploy that same transition
   to production.

**C:** before the scratch execution, the frozen source claim selects the recovery subject reaching healthy state; the frozen evidence also declares the scratch subject transition-equivalent for that claim.

**S:** production recovery subject; the scratch subject is frozen as transition-
equivalent for this claim.

**B:** failed recovery state.

**E:** recovery subject reaches healthy state.

**T:** `failed -> healthy` through the same recovery function/contract.

**Q:** production packaging/deployment.

The earlier act executed T on an evidence-supported equivalent subject. Packaging
and deployment do not create a fresh lineage for this paper boundary.

**Status:** `ineligible`.

## R3-08 — same-looking transition with unproven subject equivalence

**Frozen facts**

1. A simulation clone reports a successful `failed -> healthy` transition.
2. The clone uses a similar label and API shape, but frozen evidence does not show
   that it shares the authoritative state schema, implementation function or
   transition semantics of the production target.
3. A production candidate is then proposed before any production mutation.

**C:** before the clone execution, the frozen source claim selects the production recovery subject reaching healthy state; it does not establish clone/production equivalence.

**S:** production recovery subject.

**B:** production subject is failed.

**E:** production subject reaches healthy authoritative state.

**T:** `failed -> healthy` on production semantics.

**Q:** none material.

Whether the clone already executed the same T depends on subject equivalence that
is not established by the frozen evidence. The author may not choose the favourable
side merely because the labels look similar.

**Status:** `indeterminate`.

## Frozen aggregate

- treatment cases: **8**
- `eligible`: 2
- `ineligible`: 4
- `indeterminate`: 1
- `not_applicable`: 1
- predecessor control probes: **3** and explicitly unpaired
- productive mutations performed for S0-R3 classification: 0
- predecessor records rewritten: 0
- natural cases admitted: 0
- efficacy claims: 0

Reviewer B must independently reproduce C/S/B/E/T/Q and all eight treatment
classifications, attack baseline/qualifier/subject renaming, and verify the exact
3-control/8-treatment procedure. Any material disagreement rejects this revision for pilot use.
