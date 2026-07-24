---
title: "Vibe-Lab Productive Role Boundary"
status: active
canonicality: operative
updated: "2026-07-24"
---

# Vibe-Lab Productive Role Boundary

## Purpose

Vibe-Lab is the ecosystem experiment and evidence surface. It registers bounded comparisons for named consumers, binds observations to evidence and closes experiments with reviewed decisions.

It is not a steering organ.

## Productive role

Vibe-Lab may:

- register a bounded prospective comparison for a named consumer and decision target;
- keep evidence references to pull requests, commits, CI checks, run cards, receipts, and cited repository artifacts;
- classify claim boundaries as observed, self-reported, inferred, stale, missing, or unknown;
- evaluate comparability and uncertainty without inventing causal proof;
- close an experiment with a reviewed disposition;
- propose evidence-bound follow-up candidates for Bureau review.

Vibe-Lab must not:

- choose the next ecosystem task;
- mutate Bureau queues;
- merge pull requests;
- deploy runtime services;
- override GitHub, CI, runtime, or RepoGround as truth sources;
- promote a rule from a single anecdotal run.

## Cooperation contract

| Organ | Vibe-Lab relation | Boundary |
| --- | --- | --- |
| Grabowski | Primary source of operator-work observations. | Grabowski executes work; Vibe-Lab only binds experiment observations to evidence. |
| Bureau | Receives proposal-ready follow-up candidates. | Bureau decides whether candidates become tasks. |
| RepoGround | Supplies cited, commit-bound repository context and freshness information. | Vibe-Lab stores references, not large source dumps and does not grant RepoGround mutation authority. |
| Leitstand | May display condensed learning signals. | Display only; no steering authority. |
| Systemkatalog | Supplies stable organ-role and authority context. | Systemkatalog is read-only catalog truth; it does not own runtime status or execution claims. |
| GitHub / CI | Primary truth source for PR, review, merge, and check state. | Vibe-Lab does not reinterpret green/red status without evidence. |

## Current productive gate

`experiments/active.v1.json` is the only current experiment truth. New work enters Vibe-Lab only when a named external consumer, a decision target, a prospective comparison and an expiry are explicit. Historical captures and archived experiments remain evidence, but they do not justify a new active surface by themselves.

## Adoption rule

A Vibe-Lab learning candidate may be promoted only when the evidence states:

- what was observed;
- where it was observed;
- what remains missing;
- which organ should own any follow-up;
- which claims are explicitly not proven.

Single-run observations are usability evidence, not effectiveness evidence.
