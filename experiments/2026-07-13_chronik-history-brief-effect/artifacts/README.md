# Experiment artifacts

Store frozen Chronik cohort receipts, immutable task evidence references and independent scorecards here. Do not store raw logs, prompts, secrets or mutable live-state dumps.

`artifacts/admissions/<case-id>/admission.json` is reserved for create-only records written by `tools/vibe-cli/admit_natural_case.py`. The directory is intentionally absent until the first real natural case is admitted. A record freezes eligibility attestations, comparability/confounder metadata, an explicit pre-planning condition, evidence digests and the independent-review handoff. It is not a run, observation, fairness proof or effect result.

Triggered by: `user-request-chronik-natural-case-admission-2026-08-09`.
