# Operator-Lab Run: Schauwerk Miro Quality Receipt v1

Date: 2026-07-01
Target repo: heimgewebe/schauwerk
Target branch: feat/miro-quality-receipt-v1
Run type: PR / agent implementation

## Trigger check

- PR-/Agentenlauf: yes
- Starker Claim: yes — Miro board quality becomes locally inspectable instead of only visually asserted.
- Run Card nötig: yes

## Hypothesis

A local quality receipt over verified Miro snapshots can reduce layout-regression ambiguity for Schauwerk learning boards without adding unsafe remote Miro cleanup or mutation primitives.

## Intervention

- Add a sanitized local Miro snapshot quality inspector.
- Add CLI dispatch for `schauwerk miro quality`.
- Attach `quality.json` generation to `schauwerk miro learn live-test` after the verified `after.json` snapshot.
- Encode heuristic checks for overlap, readability pressure, connector count, frame structure, DOC/TABLE effect and sticky dominance.

## Evidence

Target repo validation:

```text
make validate
ruff: passed
registry_validation: passed
pytest: 107 passed
```

## Interpretation boundary

This proves local receipt generation and heuristic checks. It does not prove visual beauty, live Miro rendering fidelity, or remote cleanup support.

## Follow-up

Use quality receipts to drive Layout v1.2 changes. Do not patch visual grammar based only on subjective board impressions.
