---
title: "Model-Lab Replication-Series — Failure Modes"
status: designed
canonicality: operative
---

# Model-Lab Replication-Series — Failure Modes

## When does this approach fail or mislead?

- **Cosmetic condition relabeling.** A changed label or minor prose variation is
  not a material condition difference and must not be read as a stronger contrast.
- **Multi-axis condition drift.** Changing more than one primary experimental
  difference at once confounds any later effect; a compliant design selects exactly
  one primary axis and classifies every other difference as controlled or reported.
- **Challenge or acceptance-surface drift.** Differing challenge, acceptance
  criteria, or evaluation surface between conditions breaks comparability; these
  surfaces stay fixed.
- **Test or verifier drift.** Manufacturing contrast through different tests or
  runtime checks is not a real difference; verification stays functionally
  equivalent.
- **Unequal human intervention.** One condition receiving different manual
  correction or rework confounds the contrast; intervention rules are defined
  equivalently before execution.
- **Dependency or runtime-environment drift.** Unrecorded dependency or runtime
  differences must be held constant or documented and justified, never silently
  introduced.
- **Post-hoc single-condition rework.** Altering a condition after observing its
  result invalidates the contrast; each condition is frozen before execution.
- **Self-reported independence mistaken for external proof.** Self-reported context
  separation is not external attestation; external independence stays a separate
  later evidence track.
- **Design gate mistaken for execution permission.** Defining contrast criteria
  does not authorize Run-004 execution, a result assessment, or a comparison;
  `weak_condition_contrast` stays open.
- **Historical run-bundle rewrite.** The archived Run-001/Run-002/Run-003 bundles
  and historical evidence must not be rewritten to manufacture a stronger contrast.
- **Ambiguous challenge version.** Every future design must stay pinned to
  `rest-api-v1`; silent task drift destroys comparability.
- **Missing evidence artifacts.** A declared contrast or run without resolvable,
  repo-local evidence cannot support later assessment.
- **Retroactive hardening of historical experiments.** This gate must not be used
  to rewrite historical Run-001/Run-002/Run-003 bundles or to make opt-in AP-1/AP-2
  controls retroactively mandatory for unrelated historical experiments.
- **Pseudo-comparison without a materially distinct control condition.**
  Multiple run surfaces do not by themselves create a meaningful comparison.
  Without a predeclared, materially distinct and controlled intervention axis,
  no condition-effect or comparative-quality claim is supported.
- **Skeleton or design gate mistaken for a result.**
  A schema-valid gate, design artifact, execution scaffold, or green validator
  establishes structural compliance only. It does not establish an executed
  comparison, empirical result, condition effect, or outcome upgrade.
- **Frozen condition design mistaken for execution-readiness or a result.**
  A frozen, validated condition design (one primary axis, two arms, controlled
  bindings, SHA-256 freeze) selects and freezes a contrast before execution only.
  It does not bind the runtime environment, authorize Run-004 execution, perform a
  measurement, or assess a result; runtime values stay deferred to a separate
  execution-readiness check and `weak_condition_contrast` stays open.
