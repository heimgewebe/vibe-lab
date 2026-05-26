---
title: "Playbook — Outcome-Evidence-Replication-Series Gate"
status: draft
canonicality: exploratory
relations:
  - type: references
    target: ../roadmap.md
  - type: references
    target: ../../experiments/2026-05-25_outcome-evidence-replication-series/manifest.yml
---

# Playbook — Outcome-Evidence-Replication-Series Gate

## Purpose
This gate blocks any Outcome-Upgrade until the series has enough comparable runs and evidence.

## Minimum Criteria Before Outcome-Upgrade
- at least 4 comparable runs in the series
- at least 3 distinct task classes
- at least 2 runs with independent review
- at least 1 run with full independence
- `full_independence` means a Human Reviewer or another AI system / different model family
- same model family plus different session counts only as `partial_independence`
- at least 1 negative control with an expected and stable `CLAIM_NOT_PROVEN`

## Comparable Run Definition
- same claim/outcome relation
- consistent required artifacts
- explicitly declared task class
- no mixing of scaffold, execution, and outcome claims

## Required Artifacts Per Run
- `run.yml`
- `measurement.yml`
- `auditor-output.yml`
- `evidence-pack.yml`
- `comparability.yml`
- `review-events.yml` when review/rework claims are made
- a timing artifact when duration or friction is claimed
- `make-validate.txt` or CI evidence when validity is claimed

## Hard Rules
- No Outcome-Upgrade with only run-local, self-reported, or partially independent evidence.
- No Outcome-Upgrade without a stable negative case.
- No adoption or promotion claim from series planning alone.

## Notes
This playbook is a gate, not a validator. It creates no runs and changes no status.
