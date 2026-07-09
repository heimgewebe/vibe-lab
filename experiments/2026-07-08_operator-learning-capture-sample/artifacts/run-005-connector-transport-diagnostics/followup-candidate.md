---
title: "Follow-up Candidate — P13 Connector Transport Diagnostics"
status: active
canonicality: operative
triggered_by: "run-005-connector-transport-diagnostics"
updated: "2026-07-09"
---

# Follow-up Candidate — P13 Connector Transport Diagnostics

## Candidate

Add a narrow Grabowski-side connector transport diagnostics grip or runbook step.

## Evidence

- `transport-events.jsonl` lists six recent connector-transport-relevant ledger events.
- Four of those six are unresolved.
- The live friction summary classifies connector transport as recurring and decision-required.

## Intended owner

Grabowski / Operator surface.

## Proposed behavior

1. Capture bounded runtime and tunnel status.
2. Capture a bounded recent journal excerpt or structured count for `/mcp`, stream exceptions, timeout and 502 markers.
3. Require target-state re-read before retrying any mutating operation after a connector failure.
4. For read-only work, allow at most one retry after splitting the call into smaller typed or single-purpose calls.
5. Record friction when the connector failure changes the operator path.

## Boundary

This is a proposal-ready candidate, not a Bureau queue mutation and not an implementation claim.
