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

For each check below, provide an Evidence Artifact pointing to a repo-local
artifact, CI artifact, or externally verified reference. External verified
evidence must include a stable `source`/`ref` and `sha256` where applicable.
Do not push large logs or raw artifacts into the repo. If a check did not run
or evidence was not archived, mark Evidence Status: `missing_evidence` and
Verdict: `MISSING_EVIDENCE`. Never mark a check PASS without archived evidence.

- [ ] `make validate`
  - Evidence:
  - Evidence Status:
  - Verdict:
- [ ] Relevant targeted tests
  - Evidence:
  - Evidence Status:
  - Verdict:
- [ ] CI result
  - Evidence:
  - Evidence Status:
  - Verdict:
- [ ] Critic/auditor/agent review, if claimed
  - Evidence:
  - Evidence Status:
  - Verdict:

## Claims and Evidence

| Claim | Claim Type | Evidence Artifact | Evidence Status | Verdict |
|-------|------------|-------------------|-----------------|---------|
|       |            |                   |                 |         |

**Evidence Status values** (lowercase): `repo_local`, `ci_artifact`,
`external_verified`, `derived_from_auditor_output`, `missing_evidence`,
`external_unverified`, `self_reported`, `unknown`.

**Verdict values** (uppercase): `PASS`, `MISSING_EVIDENCE`, `CLAIM_NOT_PROVEN`,
`CONTRADICTION`, `OUT_OF_SCOPE`, `NOT_REPRODUCIBLE`. Use the strongest fitting
verdict.

**Claim Type values / examples**: `command_result`, `test_result`, `ci_result`,
`critic_usage`, `auditor_usage`, `agent_usage`.

**Rules:**
- No test-count claim without a test-output evidence artifact.
- No CI-success claim without CI evidence.
- No `make validate` PASS without a captured command-output artifact.
- No critic/auditor/agent-usage claim without an archived reviewer or agent output.
- `missing_evidence`, `external_unverified`, `self_reported`, and `unknown` must
  not support `PASS` for process or result claims.
- Claims without evidence must be `MISSING_EVIDENCE` or `CLAIM_NOT_PROVEN`.

## Agents and Evidence
<!-- If an agent, critic, or auditor was used, record the claim in the Claims and
Evidence table above. Use this section only for a short pointer to the archived
artifact. -->

## Risks / Not Done
<!-- Known limits, follow-ups, or intentionally deferred work -->
