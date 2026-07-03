---
title: "Playbook: PR Review Evidence Wait Gate"
status: active
canonicality: operative
schema_version: "0.1.0"
created: "2026-07-03"
updated: "2026-07-03"
author: "heimgewebe"
triggered_by: "user-request-grabowski-vibe-lab-review-evidence-wait-gate-2026-07-03"
tags:
  - playbook
  - pr
  - review
  - evidence
---

# Playbook: PR Review Evidence Wait Gate

Zweck: Review-Signale gehoeren vor die Entscheidung.
Scope: PR work with review evidence.
Before a ready claim, record head_ref, surface, observation, finding state, evidence and decision.
Open findings on an in-scope surface mean: no ready claim yet.
If a surface is unavailable, do not claim review success; record the risk and reason.
Out of scope is allowed with a short reason.

## PR body minimum
surface | head_ref | expected | current_head_observed | finding_state | evidence | decision
Allowed finding_state: none_observed, resolved, unresolved, not_checked, unavailable, out_of_scope.
