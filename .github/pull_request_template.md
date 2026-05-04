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
- [ ] `make validate`
  - Evidence:
- [ ] Relevant targeted tests
  - Evidence:
- [ ] CI result
  - Evidence:
- [ ] Critic/auditor/agent review, if claimed
  - Evidence:

Checks run:
<!-- e.g. make validate, make generate-stable -->

If a check was not run or evidence was not archived, mark it explicitly as `MISSING_EVIDENCE`.
Do not write success claims without evidence.

## Claims and Evidence
List every process or result claim made by this PR.

| Claim | Claim Type | Evidence Artifact | Evidence Status | Verdict |
| --- | --- | --- | --- | --- |
| <!-- e.g. make validate passed --> | <!-- command_result / test_result / ci_result / critic_usage / auditor_usage / agent_usage --> | <!-- repo-local path or external reference --> | <!-- repo_local / ci_artifact / external_verified / external_unverified / derived_from_auditor_output / missing_evidence / self_reported --> | <!-- PASS / MISSING_EVIDENCE / CLAIM_NOT_PROVEN --> |

Field semantics:
- `Evidence Status` uses lowercase evidence-state values, e.g. `repo_local`, `ci_artifact`, `missing_evidence`.
- `Verdict` uses uppercase claim verdicts, e.g. `PASS`, `MISSING_EVIDENCE`, `CLAIM_NOT_PROVEN`.

Rules:
- No test-count claim without test-output evidence.
- No CI-success claim without CI evidence.
- No `make validate` claim without command-output evidence.
- No critic/auditor/agent-usage claim without archived reviewer or agent output.
- `missing_evidence` documents absence only and must not support `PASS`.
- `external_unverified` must not support `PASS` for process claims.
- Claims without evidence must be marked as `MISSING_EVIDENCE` or `CLAIM_NOT_PROVEN`.

## Risks / Not Done
<!-- Known limits, follow-ups, or intentionally deferred work -->
