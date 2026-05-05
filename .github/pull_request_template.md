## Change Summary
<!-- 2-4 lines: what changed and why -->

## Change Type
- [ ] docs
- [ ] guard/validator
- [ ] experiment artifact
- [ ] policy/governance
- [ ] tooling/ci

## Touched Paths
<!-- e.g. docs/, scripts/, .github/workflows/ -->

## Validation

For each check below, provide an Evidence path pointing to a repo-local artifact
(e.g. a captured output file). If a check did not run or the evidence was not
archived, mark it `Evidence Status: missing_evidence` and set Verdict:
`MISSING_EVIDENCE`. Never mark a check PASS without archived evidence.

- [ ] Ran relevant checks locally (list below)
- [ ] CI checks passed or expected deltas explained

Checks run:

- make validate
  - Evidence:
- Relevant targeted tests
  - Evidence:
- CI result
  - Evidence:
- Critic/auditor/agent review, if claimed
  - Evidence:

## Claims and Evidence

| Claim | Claim Type | Evidence Artifact | Evidence Status | Verdict |
|-------|------------|-------------------|-----------------|---------|
|       |            |                   |                 |         |

**Evidence Status values** (lowercase): `repo_local`, `ci_artifact`,
`external_verified`, `derived_from_auditor_output`, `missing_evidence`,
`external_unverified`, `self_reported`.

**Verdict values** (uppercase): `PASS`, `MISSING_EVIDENCE`, `CLAIM_NOT_PROVEN`.

**Rules:**
- No test-count claim without a test-output evidence artifact.
- No CI-success claim without CI evidence.
- No `make validate` PASS without a captured command-output artifact.
- No critic/auditor/agent-usage claim without an archived reviewer or agent output.
- `missing_evidence` documents absence and must never support a PASS verdict.
- `external_unverified` must not support a PASS verdict for process claims.
- Claims without evidence must be `MISSING_EVIDENCE` or `CLAIM_NOT_PROVEN`.

## Agents and Evidence
<!-- If an agent report exists, link it and keep this section brief. -->

## Risks / Not Done
<!-- Known limits, follow-ups, or intentionally deferred work -->
