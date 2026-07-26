---
title: "Operator Routing Shadow — Independent Semantic Review Protocol"
status: active
canonicality: operative
updated: "2026-07-26"
---

# Independent semantic review protocol

## Purpose

This protocol defines how a naturally captured routing-shadow case receives a
semantic outcome without turning task lifecycle state, CI success or operator
confidence into an automatic correctness label.

## For non-programmers

A task saying “finished” only proves that the process stopped normally. It does
not prove that the code or decision was good. Vibe-Lab therefore requires two
separate judgements about the result before a case counts as complete.

## Roles

1. **Primary reviewer:** the operator or integrator performs an evidence-bound
   assessment of the result after execution.
2. **Independent reviewer:** a different human reviewer or a separately invoked
   advisory reviewer from an independent model/provider family assesses the same
   outcome kind without receiving the primary reviewer’s label.

The two assessments must use distinct privacy-preserving reviewer pseudonym
SHA-256 values. Distinct pseudonyms make disagreement measurable; they do not by
themselves cryptographically prove organisational independence.

## Review input

Reviewers may use bounded primary evidence references only:

- `github-ci:` for existing CI evidence;
- `diff-review:` for a revision-bound diff review;
- `operator-decision:` for an explicit operator decision;
- `chronik:` for a frozen historical evidence reference;
- `artifact:` for an immutable receipt or result artifact.

Raw prompts, transcripts, private notes, unrestricted command lines and secrets
must not enter the cohort record.

## Allowed labels

Both reviewers assess the same outcome kind:

- `task_correctness`; or
- `decision_quality`.

Each reviewer chooses exactly one label: `success`, `partial` or `failure`.
Disagreement is preserved and measured; it is never averaged away or silently
converted to success.

## Seal rule

A new reviewed v3 record counts as complete only when:

- execution and semantic outcome remain separate;
- at least two distinct reviewer assessments are present;
- every assessment has primary evidence;
- the top-level reviewed outcome has primary evidence;
- freeze, execution observation, semantic observation and capture times are valid;
- case provenance is `production` for inclusion in the treatment denominator;
- the no-effect boundary remains unchanged.

If two defensible independent assessments are unavailable, seal an explicit
abstention such as `no_semantic_review` or `insufficient_primary_evidence`.
The case remains in the denominator and does not count as complete.

## Existing records

Create-only cohort history is immutable. The existing 2026-07-24 production
record remains an abstention and is not backfilled with later reviews. This
prevents outcome-aware rewriting of the prospective cohort.

## Authority boundary

Review results are experiment evidence only. They cannot select routes, change
policy, mutate Bureau queues, merge pull requests, deploy services, train models
or authorize online learning.
