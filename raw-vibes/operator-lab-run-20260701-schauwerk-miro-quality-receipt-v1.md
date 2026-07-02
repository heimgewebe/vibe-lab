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

## Follow-up: rich item type correction

Date: 2026-07-01
Target repo: heimgewebe/schauwerk
PR: #24
Commit after merge: 435beb5

### Observation

Live Miro snapshots expose rich items as `doc_format` and `data_table_format`, not only as abstract `doc` and `table` types. The first quality receipt therefore undercounted DOC/TABLE items.

### Correction

Schauwerk PR #24 updated the quality type mapping and tests.

### Evidence

```text
make validate
ruff: passed
registry_validation: passed
pytest: 107 passed
GitHub validate 3.11: success
GitHub validate 3.12: success
```

Live rechecks after local correction:

```text
learn-live-20260701-194620: ok=true, score=92, connectors=5, docs=1, tables=2
nicole-mt-zoom-chunked-20260701-211733: ok=true, score=92, items=96, frames=15, connectors=5, docs=14, tables=13, overlaps=0
```

Remaining boundary: geometry coverage remains low because Miro snapshot reads do not expose full geometry for every item.

## Follow-up: Zoomlandkarte renderer

Date: 2026-07-01
Target repo: heimgewebe/schauwerk
PR: #25
Commit after merge: 76c775f

Schauwerk PR #25 adds `learning-zoomlandkarte-v1` and the CLI option `--template zoomlandkarte` for render, apply and live-test.

Evidence:

```text
make validate
ruff: passed
registry_validation: passed
pytest: 110 passed
GitHub validate 3.11: success
GitHub validate 3.12: success
```

Boundary: render/CLI/test proven; live Miro board creation still needs a separate live run because the long live-test invocation was blocked by the platform tool filter.

## Follow-up: Typed region plan v1

Date: 2026-07-02
Target repo: heimgewebe/schauwerk
PR: #28
Commit after merge: 4773a75

### Intervention

Schauwerk now has a dry-run typed region plan for future managed-region writes:

```text
schauwerk miro region plan <region.yml> --json
```

The plan validates region mode, local surface alias shape, expected snapshot digest, preflight steps, postflight steps, restore requirement, and an explicit no-mutation boundary.

### Evidence

```text
make validate
ruff: passed
registry_validation: passed
pytest: 115 passed
GitHub validate 3.11: success
GitHub validate 3.12: success
```

### Boundary

This is SW-009A planning only. It does not mutate Miro and does not yet apply managed updates.
