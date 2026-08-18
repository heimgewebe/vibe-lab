---
title: "Outcome-Bound S1 — Canonical natural-arrival sequence proof"
status: testing
canonicality: operative
created: "2026-08-18"
updated: "2026-08-18"
triggered_by: "conversation:user-request-2026-08-18-outcome-bound-restplan-implementation"
---

# Canonical natural-arrival sequence proof

## Activation boundary

S1 became eligible to observe natural cases only after PR #346 merged at
`2026-08-17T21:07:25Z`, merge commit
`5f12ef5bc2a59459ee11b71fd4f8bd434e4386f1`.

## Authoritative ordering read

The canonical Bureau StateStore database
`/home/alex/.local/state/bureau/bureau.sqlite3` was read without mutation. The
`events` table was scanned for `live-register` records whose payload kind is
`candidate_task` and contains the canonical `operator_intake` binding, strictly
after the activation timestamp and in ascending numeric StateStore event id.

The first three matching arrivals are:

| Slot | StateStore event | Created at | Candidate identity | Supersedes |
| --- | ---: | --- | --- | ---: |
| `S1-N01` | `8146` | `2026-08-17T21:31:57.378731Z` | `SYSTEMKATALOG-DRIFT-CLOSED-LOOP-V1` | `8109` |
| `S1-N02` | `8147` | `2026-08-17T22:32:43.503381Z` | `SYSTEMKATALOG-DRIFT-CLOSED-LOOP-V1` | `8146` |
| `S1-N03` | `8148` | `2026-08-17T23:37:56.183230Z` | `SYSTEMKATALOG-DRIFT-CLOSED-LOOP-V1` | `8147` |

All three are distinct canonical arrival events even though they are successive
revisions of the same candidate identity. S1 section 5 freezes the sample as the
first three arrivals and states that every arrival consumes its ordinal slot.
Therefore later distinct candidates may not replace these three events.

## Event-bound source evidence

The three events bind different exact drift-report digests:

- event `8146`: `8d86c385a399d5a072e06a7b5597e6d2b6683c940fe173efce5f541321b918ce`;
- event `8147`: `5e05f6be5811f7ba3b7ccfeb3510dd2cb9f9c3abce1d6dadd03b0e6d35b5b986`;
- event `8148`: `65d7f562d5807285a980931c24309d90575a212e9fe1cc3c0c72532ff756cee6`.

Each event names the same rolling source locator:
`/home/alex/.local/state/heim-pc/systemkatalog-drift-watch/drift-report.json`.
At the S1 closeout capture that locator had advanced to digest
`70e8eecfb9c7c566ece248ef93befeb6bb8918e7f083efd01b1e82278e831471`.
A bounded search of the normal Heim-PC and Bureau state surfaces did not resolve an
immutable file containing any of the three historical event-bound digests. This
establishes only that the registered rolling locator and bounded state search no
longer supply those historical report bytes; it does not prove that no copy exists
anywhere else.

## Present-state readback is not historical baseline

A fresh canonical assessment of candidate
`SYSTEMKATALOG-DRIFT-CLOSED-LOOP-V1` resolves current event `8240`, status
`observed`, with advisory decision `promote`; publication approval remains absent.
That present-state readback is useful only to prove that the candidate lineage has
continued. It must not be used to reconstruct or rebase B for events 8146–8148.

## Integrity conclusion

- treatment slots consumed: **3/3**;
- replacements/backfills: **0**;
- arrival-order ambiguity: **0**;
- distinct candidate identities required by the protocol: **no**;
- technical/Bureau truth copied into S1 as a second authority: **no** — the capture
  records retain identifiers and bounded findings only.

This sequence proof does not establish timely prospective capture, productive
mutation absence, target-effect success, Outcome Case efficacy, or any production
authority.
