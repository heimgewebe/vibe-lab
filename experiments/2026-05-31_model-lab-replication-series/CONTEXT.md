---
title: "Model-Lab Replication-Series — Context"
status: designed
canonicality: operative
---

# Model-Lab Replication-Series — Context

## Why this series exists

RM-008 (Model-Lab Control Plane, Welle 1) introduced two opt-in guards:

- **AP-1** — `scripts/docmeta/validate_model_lab_control.py`: an opt-in
  Lab-Control-Minimum check that only enforces `run_meta.json` files which set
  `model_lab_control: true`.
- **AP-2** — `scripts/docmeta/validate_challenge_versions.py`: a challenge-version
  validator pre-stage that only enforces decisions which explicitly opt in as
  Model-Lab / comparative.

Until now both have been validator infrastructure without a real, activated
Model-Lab series to act on. This series closes that gap: it is the first
experiment that **activates** the opt-in surface (`model_lab_control: true` in a
`run_meta.json`, and a comparative `decision.yml` against a known
`challenge_version`).

## Why start with REST-API v1

`benchmarks/challenges/rest-api-v1.md` already exists as a versioned benchmark
challenge (`challenge_id: rest-api`, `version: v1`). Starting here gives:

- an existing, versioned challenge to reference (low scope, nothing new invented);
- simple comparability semantics for later runs;
- a clean anchor that AP-2 can resolve against the challenge registry.

## What is explicitly NOT done here

- No model ranking and no "Model X is better" claim.
- No adoption, no promotion, no catalog move.
- No dashboard, no metrics aggregation, no staleness reactivation.
- No global schema hardening and no global `challenge_version` requirement for
  historical decisions.

This is a laboratory anchor, not an oracle.
