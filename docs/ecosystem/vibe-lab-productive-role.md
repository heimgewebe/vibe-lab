---
title: "Vibe-Lab Productive Role Boundary"
status: active
canonicality: operative
updated: "2026-07-08"
---

# Vibe-Lab Productive Role Boundary

## Purpose

Vibe-Lab is the ecosystem evidence and learning surface. It records observations from real work, tests whether repeated friction forms a pattern, and turns sufficiently evidenced patterns into proposal-ready follow-up material.

It is not a steering organ.

## Productive role

Vibe-Lab may:

- record observations from real operator work;
- keep evidence references to pull requests, commits, CI checks, run cards, receipts, and cited repository artifacts;
- classify claim boundaries as observed, self-reported, inferred, stale, missing, or unknown;
- aggregate repeated friction into candidate patterns;
- propose follow-up candidates for Bureau review;
- project condensed learning signals for status surfaces after evidence exists.

Vibe-Lab must not:

- choose the next ecosystem task;
- mutate Bureau queues;
- merge pull requests;
- deploy runtime services;
- override GitHub, CI, runtime, or RepoBrief as truth sources;
- promote a rule from a single anecdotal run.

## Cooperation contract

| Organ | Vibe-Lab relation | Boundary |
| --- | --- | --- |
| Grabowski | Primary source of operator-work observations. | Grabowski executes work; Vibe-Lab only records learning evidence. |
| Bureau | Receives proposal-ready follow-up candidates. | Bureau decides whether candidates become tasks. |
| RepoBrief / Lenskit | Supplies cited repository context and freshness information. | Vibe-Lab stores references, not large source dumps. |
| Leitstand | May display condensed learning signals. | Display only; no steering authority. |
| Cabinet | Supplies organ-role context. | Cabinet maps context; it is not a truth source for execution claims. |
| GitHub / CI | Primary truth source for PR, review, merge, and check state. | Vibe-Lab does not reinterpret green/red status without evidence. |

## First productive test

The first productive integration must not start with new export targets or dashboards. It must first test whether recent existing artifacts already contain enough evidence to extract useful learning signals.

The first slice is therefore an operator-learning-capture sample:

1. select a small set of recent real ecosystem work items;
2. bind each observation to named evidence;
3. identify repeated friction candidates;
4. decide whether a capture contract is justified.

## Adoption rule

A Vibe-Lab learning candidate may be promoted only when the evidence states:

- what was observed;
- where it was observed;
- what remains missing;
- which organ should own any follow-up;
- which claims are explicitly not proven.

Single-run observations are usability evidence, not effectiveness evidence.
