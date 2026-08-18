---
title: "Outcome-Bound S1-R1 — Fixed sampling-unit adversarial cases"
status: designed
canonicality: operative
created: "2026-08-18"
updated: "2026-08-18"
triggered_by: "conversation:user-request-2026-08-18-continue-outcome-bound"
---

# Fixed sampling cases

These paper cases test only whether the frozen S1-R1 sampling unit has one reproducible interpretation. They provide no natural-case or efficacy evidence.

| ID | Frozen facts | Expected sampling result |
| --- | --- | --- |
| U01 | Candidate A first appeared before activation; after activation event 900 supersedes A. | no unit; event 900 cannot consume a slot |
| U02 | Candidate B first appears after activation at event 901. | one unit anchored to 901 |
| U03 | B then receives events 902 and 905. | no additional units; B remains one unit anchored to 901 |
| U04 | Candidate C first appears after activation at 903, then is corrected before S1-R1 observes it. | one unit anchored to 903; missed/late capture may fail but correction cannot replace C |
| U05 | New candidate D is D0. | D still consumes one natural slot; later gate may become inconclusive but no backfill |
| U06 | New source material is deduplicated by Bureau onto pre-existing candidate A. | no new identity and no unit |
| U07 | Candidate E first appears after activation, but productive mutation began before shadow capture. | E consumes one slot and records `capture_missed_before_mutation` |
| U08 | Two new identities F and G have equal `created_at`; F has lower identity-first event id. | F precedes G |
| U09 | An idempotent replay returns existing candidate/event truth without a new canonical event. | no new unit |
| U10 | Candidate H first appears during the five-minute post-merge cooling interval. | pre-activation; never an S1-R1 unit |
| U11 | Candidate H first appeared during cooling, then receives a post-activation supersession. | still no unit because H's first-ever event is pre-activation |
| U12 | Candidate I first appears after activation, but the target result is already known when capture starts. | I consumes one slot and records `result_informed_binding_failure` |
| U13 | Candidate J has an older canonical `candidate_task` event without `operator_intake`; its first `operator_intake` revision appears only after activation. | no unit; J is a pre-existing identity and cannot become new by later provenance enrichment |

## Frozen aggregate

- sampling unit: candidate identity, not event;
- identity creation event: first-ever canonical `candidate_task` event for that candidate id across all provenance shapes; that exact event must already carry `operator_intake`;
- post-activation eligibility: first-ever event timestamp at or after `merged_at + 300 seconds`;
- ordering: identity-first event id ascending;
- maximum units per candidate id: 1;
- replacement/backfill: forbidden;
- outcome filters: forbidden;
- productive mutations performed for these paper cases: 0.

The independent pre-activation reviewer must reproduce all thirteen results with zero material disagreement. A single defensible alternative sampling interpretation rejects this revision before activation.
