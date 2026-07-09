---
title: "Result: Operator Learning Capture — run-005 Connector Transport Diagnostics"
status: active
canonicality: operative
triggered_by: "user-request-grabowski-p13-connector-transport-2026-07-09"
updated: "2026-07-09"
---

# Result — run-005 Connector Transport Diagnostics

## Verdict

`proposal_ready_connector_transport_diagnostics`

P13 is stronger than a one-off anecdote: the live Grabowski friction ledger reports six connector-transport-relevant events, four still unresolved. The useful next action is not another broad retry and not a direct runtime fix from Vibe-Lab. The useful next action is a narrow Grabowski-side diagnostic grip or runbook step.

## What this run checked

| Check | Result |
|---|---:|
| Friction snapshot size | 50 events |
| Unresolved events | 41 |
| Decision-required events | 41 |
| Connector-transport-relevant events | 6 |
| Connector-transport unresolved | 4 |
| Adjacent runtime contract | valid |
| `grabowski-operator.service` | active/running |
| `tunnel-client-grabowski.service` | active/running |

## Interpretation

The pattern is: broad, long-running or multi-step connector calls sometimes return `502 upstream/external service error`; smaller typed calls often succeed immediately after. That means the failed connector response must not be treated as proof that the underlying host command failed, succeeded, or did nothing.

## Recommended policy shape

- Read-only retry: at most one retry, split into smaller typed or single-purpose calls.
- Mutation retry: no blind retry. First re-read target state, locks, process state, PR state, or file state.
- Evidence: capture runtime/tunnel status plus bounded journal markers before deciding whether the failure is still active.
- False-green guard: a successful small retry does not prove the original broad call was harmless.

## Boundary

- Belegt: ledger counts, event ids, unresolved count, runtime/tunnel service status.
- Plausibel: broad or long connector calls increase 502 risk.
- Spekulativ: exact root cause in connector, tunnel, MCP stream handling, output size, concurrency, or platform edge.

## Non-claims

- No root-cause proof.
- No connector vendor fix.
- No runtime policy change.
- No proof of command success or failure when the connector failed.
- No safe mutation retry from a 502 alone.
- No Bureau mutation.

## Next lever

Turn `followup-candidate.md` into a Grabowski-owned implementation task: add a narrow connector-transport diagnostic grip or equivalent operator runbook primitive.
