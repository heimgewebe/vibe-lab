---
title: "Context — rLens Agent Context Conditions"
status: designed
canonicality: operative
relations:
  - type: references
    target: "../../docs/playbooks/pr-context-capture.md"
  - type: references
    target: "../2026-06-10_pr-agent-context-comparison-series/method.md"
  - type: references
    target: "../2026-07-01_operator-lab-loop/method.md"
---

# Context — rLens Agent Context Conditions

## Purpose

This experiment records how to compare rLens/RepoBrief access levels for real
agent repo work. It exists because Bureau can now bind rLens context references,
but that does not prove that a given access level improves agent output.

## Decision under test

The experiment informs one narrow decision: which rLens access level, if any,
should become the default for repo/PR agent tasks.

It must not promote a default from design alone.

## In scope

- Real PR-review, PR-rework, small repo-fix, and diagnosis-only tasks.
- rLens conditions that differ only in allowed context surface.
- Evidence quality and rework metrics.
- Preparation and review overhead.

## Out of scope

- Model ranking.
- Runtime/deploy truth claims.
- Automatic promotion of rLens defaults.
- Claims that rLens caused improvement from a single successful run.
- Secret or private-context transfer into lower-trust agents.

## Source-of-truth boundary

rLens is context and navigation evidence. It is not truth. Code, PR diff, CI,
Bureau task state, GitHub comments, runtime probes, and explicit run artifacts
remain the primary evidence for claims.
