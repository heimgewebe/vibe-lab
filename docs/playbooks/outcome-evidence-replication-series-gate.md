---
title: "Playbook — Outcome-Evidence-Replication-Series Gate"
status: active
canonicality: operative
relations:
  - type: references
    target: ../roadmap.md
  - type: references
    target: ../../experiments/2026-05-25_outcome-evidence-replication-series/manifest.yml
---

# Playbook — Outcome-Evidence-Replication-Series Gate

## Purpose
This gate blocks any Outcome-Upgrade until the series has enough comparable runs and evidence.
The gate is enforced by `validate_outcome_evidence_replication_series.py` in the `make validate` pipeline.

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
- `changed-files.txt`
- `timing.txt`
- `make-validate.txt`
- `review-events.yml` only when review/rework claims are made

For contract-/documentation-alignment runs in this series:
- `outcome_upgrade_allowed` must be `false`
- no promotion, adoption, or validator-architecture claim

## Hard Rules
- No Outcome-Upgrade with only run-local, self-reported, or partially independent evidence.
- No Outcome-Upgrade without a stable negative case.
- No adoption or promotion claim from series planning alone.
- Any upgrade-flag (outcome/effect/promotion) requires the series to meet all minimum criteria.

## Gate Rules (Enforced by Validator)
- **G1**: All 8 required artifacts must be present per run
- **G2**: A `verdict=not_comparable` run cannot claim any upgrade-flags
- **G3**: `task_class=validator_test_hardening` requires real code paths to claim outcome upgrades
- **G4**: No upgrade-flags allowed if series has fewer than 4 comparable runs
- **G5**: A `negative_control` run requires `verdict.outcome=CLAIM_NOT_PROVEN`
- **G6**: Self-reported provenance cannot claim full-independence variants
- **G7**: Any upgrade-flag requires the series to meet all playbook minimum criteria (4 comparable runs with 3+ distinct task classes, 2+ with independent review, 1+ with full independence, 1+ negative control)

## Notes
This playbook is a gate enforced by automated validation. It creates no runs and changes no status.

