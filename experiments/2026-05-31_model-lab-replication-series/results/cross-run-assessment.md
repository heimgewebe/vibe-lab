---
title: "Cross-Run Assessment: Model-Lab Replication Series Run-001 vs Run-002"
status: draft
canonicality: operative
triggered_by: user-request-2026-06-05-model-lab-next-step-diagnosis
relations:
  - type: references
    target: result.md
  - type: references
    target: decision.yml
  - type: references
    target: ../method.md
  - type: references
    target: ../manifest.yml
  - type: references
    target: ../artifacts/run-001-rest-api-spec-first-baseline/run.yml
  - type: references
    target: ../artifacts/run-002-rest-api-code-first-control/run.yml
  - type: references
    target: ../artifacts/run-001-rest-api-spec-first-baseline/comparability.yml
  - type: references
    target: ../artifacts/run-002-rest-api-code-first-control/comparability.yml
  - type: references
    target: ../artifacts/run-003-plan-stronger-condition-contrast/plan.md
---

# Cross-Run Assessment — Model-Lab Replication Series Run-001 vs Run-002

## 0. Scope und Nicht-Ziele

* Bewertet werden nur Run-001 und Run-002.
* Beide laufen unter `rest-api-v1`.
* Dieses Artefakt ist ein `result_interpretation`-Artefakt, kein Run-Bundle.
* Kein Model-Quality-Verdict.
* Kein Outcome-Upgrade.
* Keine Adoption.
* Keine Promotion.
* Keine Staleness-Reaktivierung.
* Keine Behauptung, dass `spec_first_baseline` oder `code_first_control` besser ist.

## 1. Vergleichsbasis

Run-001:
* id: run-001-rest-api-spec-first-baseline
* condition: spec_first_baseline
* challenge_version: rest-api-v1
* evidence: run.yml, run_meta.json, execution.txt, timing.txt, baseline-output.md, implementation/, targeted-tests.txt, measurement.yml, auditor-output.yml, comparability.yml

Run-002:
* id: run-002-rest-api-code-first-control
* condition: code_first_control
* challenge_version: rest-api-v1
* evidence: run.yml, run_meta.json, execution.txt, timing.txt, control-output.md, implementation/, targeted-tests.txt, measurement.yml, auditor-output.yml, comparability.yml

## 2. Challenge-Konstanz

* Beide adressieren denselben Challenge-Contract: `benchmarks/challenges/rest-api-v1.md`.
* Dadurch ist ein struktureller Vergleich möglich.
* Das beweist noch keine Ergebnisüberlegenheit.

## 3. Condition-Kontrast

* Run-001 ist `spec_first_baseline`.
* Run-002 ist `code_first_control`.
* Der Kontrast ist methodisch schwach, weil beide durch deterministische repo-lokale Scripts erzeugt/archiviert wurden.
* Die Bedingung `code_first_control` ist eine zweite Ausführungsfläche, nicht automatisch ein fundamental anderes Generierungsparadigma.

## 4. Implementierungsvergleich

Beide Implementationen zeigen ein TypeScript/Fastify Shape mit Envelope Pattern. Validierungen für Body/Path/Query, Error Codes und Pagination sind vorhanden. Der 500-Handler ist im Code vorhanden. Die implementation shape appears structurally aligned/similar.

## 5. Verification-Coverage-Vergleich

* Beide haben static verifier scripts.
* Beide haben Vitest specs.
* Diese Specs sind nach aktueller Run-Bundle-Lage executable, aber unrun.
* Bei Run-002 ist forced 500 runtime assertion explizit MISSING_EVIDENCE / code-only/deferred.
* Update (Runtime Validation): The forced 500 runtime assertion has now been validated via an external test artifact (`artifacts/runtime-validation-run-001-run-002`), closing this gap without altering the original bundle.
* Run-001 hat identische Laufzeitbeweislücken bezüglich npm/Vitest und 500 runtime assertions.
* Update (Runtime Validation): Both Vitest specs and 500 assertions for Run-001 and Run-002 have been successfully executed and archived in the separate runtime validation artifact.

## 6. Verhalten / Statuscodes / Error Envelope

The original Run-001 and Run-002 bundles still do not contain in-bundle `npm test`/Vitest output, but a separate post-run runtime-validation artifact now records static verifier execution, Vitest runtime execution, and forced 500 error-envelope runtime assertions for both archived implementations.

This closes the runtime-evidence gap for the archived implementations without mutating the historical run bundles.

## 7. Evidenzlücken

* Runtime execution of Vitest specs is evidenced separately in `artifacts/runtime-validation-run-001-run-002/`.
* Forced 500 path runtime assertion is evidenced separately in `artifacts/runtime-validation-run-001-run-002/`.
* Remaining gap: Condition contrast is weak structural control.
* Remaining gap: No external/independent auditor comparison exists for this pair.
* No model-quality or causal outcome conclusion can be drawn.

## 8. Gegenhypothesen

Gegenhypothese A:
Die sichtbaren Unterschiede zwischen Run-001 und Run-002 sind hauptsächlich Artefakt-/Label-Unterschiede, nicht methodisch relevante Generierungsunterschiede.

Gegenhypothese B:
Die Vergleichbarkeit ist formal hergestellt, aber praktisch noch zu schwach, um einen belastbaren Qualitätsvergleich zu tragen.

## 9. Assessment Verdict

Assessment verdict: comparison_surface_runtime_validated_with_inconclusive_quality_result

## 10. Next Steps

1. ~~Optional runtime validation run for both implementations, including forced 500 assertion.~~ (Completed: `artifacts/runtime-validation-run-001-run-002`)
2. Run-003 execution exists under the retained condition label, calibrated as `self_reported_different_agent_tool_context` with `external_attestation: false`.
3. Runtime-validate Run-003 in a separate artifact.
4. Only after Run-003 runtime-validation evidence exists: consider a formal `decision_type=result_assessment`.
5. Continue to block model-quality/adoption/promotion/readiness claims until stronger evidence exists.

## 11. Run-003 execution follow-up (addendum)

Scope note: This addendum records a third executed surface for the series, calibrated as a self-reported different agent/tool/session boundary, and explicitly does not extend the Run-001-vs-Run-002 verdict from section 9. The Run-001-vs-Run-002 verdict in section 9 remains `comparison_surface_runtime_validated_with_inconclusive_quality_result` and is not modified by this addendum.

### 11.1 What Run-003 is

- Run id: `run-003-rest-api-independent-model-or-tool-condition`
- Condition label: `independent_model_or_tool_condition`
- Challenge: `rest-api-v1` (unchanged from Run-001/Run-002)
- Executor: `agent:gpt-5.5-api-assistant` (self-reported)
- `independence_status`: `self_reported_different_agent_tool_context`
- `external_attestation`: `false` - no provider-side model-independence attestation is claimed.

### 11.2 What Run-003 establishes

- A third executed implementation surface under the same `rest-api-v1` challenge.
- A static verifier output archived at `artifacts/run-003-rest-api-independent-model-or-tool-condition/static-verify-run-003.txt` (exit code 0, run 2026-06-07). The static verifier asserts presence of required implementation tokens only; it is not a runtime validation.
- Bundle artifacts (run.yml, run_meta.json, condition-input.md, comparability.yml, measurement.yml, evidence-pack.yml, auditor-output.yml, execution.txt, provenance.txt, changed-files.txt, timing.txt, run-output.md, targeted-tests.txt, implementation/+) consistent with the prior run-bundle pattern.

### 11.3 What Run-003 does NOT establish

Vitest runtime execution, the forced-500 error-handler assertion, and dependency-risk
observation are no longer deferred: they are now evidenced separately in
`artifacts/runtime-validation-run-003/` (see section 11.6; gate `validation_status: partial`).
The following remain explicitly NOT established, by either the Run-003 bundle or the
runtime-validation artifact:

- A `decision_type=result_assessment` for Run-003 or for the series.
- A comparative outcome claim between Run-003 and any prior run.
- A model-quality verdict, condition-effect verdict, or comparative-superiority claim.
- An adoption, promotion, production-readiness, or security-readiness claim.
- An externally attested model independence.
- A security or production dependency-health approval (the dependency audit observed
  unremediated high-severity dev-toolchain advisories).

### 11.4 Series-level comparability semantics

To prevent silent drift between `current_comparable_runs` and the run-bundle interpretation, this addendum records the series-level reading now used by Run-003:

- `min_comparable_runs_required` and `current_comparable_runs` are series-level thresholds for *result-assessment-ready comparable runs*, not for raw executed surfaces.
- The series currently has 0 result-assessment-ready comparable runs, regardless of how many executed surfaces exist.
- The series-level minimum is 3, reflecting that any comparative condition-effect claim involving the self-reported different agent/tool boundary would require at least 3 independent comparable runs. The older Run-001/Run-002 run-bundles retain their pre-Run-003 run-local `min_comparable_runs_required: 2` as a historical snapshot, not as a current series-level threshold. This avoids rewriting historical run-bundles while keeping the series-level meaning explicit.
- Concrete machine-readable surface counts on Run-003's run.yml/measurement.yml/comparability.yml are intentionally **not** back-written by this runtime-validation pass (mirroring the non-mutating `runtime-validation-run-001-run-002` pattern, which also left the original bundles untouched):
  - `current_executed_surfaces: 3`
  - `current_runtime_validated_surfaces: 2` — retained as a pre-Run-003 snapshot in `measurement.yml` and `comparability.yml`. Run-003 now also has functional runtime evidence, but it is archived separately in `artifacts/runtime-validation-run-003/` (gate `validation_status: partial`; see section 11.6) rather than written back into the historical Run-003 metadata. The historical count therefore stays at 2 by design; it is not a comparison-readiness signal.
  - `current_result_assessment_ready_surfaces: 0`

### 11.5 Next concrete step

Run-003 runtime validation is archived in `artifacts/runtime-validation-run-003/` (gate `validation_status: partial`; see section 11.6). A formal `decision_type=result_assessment` remains deferred until the dependency-risk caveat and the methodological weaknesses in sections 3, 7, and 8 are explicitly handled. Runtime contact across three surfaces is a prerequisite for stronger assessment, not a comparison result; `comparison_ready` remains false.

### 11.6 Run-003 runtime-validation closure

A separate runtime-validation artifact now closes the Run-003 runtime-evidence gap without rewriting the historical Run-003 bundle:

- Artifact: `artifacts/runtime-validation-run-003/` (mirrors `runtime-validation-run-001-run-002`).
- Machine-readable gate: `runtime-evidence-gate.yml` (`runtime-evidence-gate.v1`), validated by `scripts/docmeta/validate_runtime_evidence_gate.py` in `make validate`.
- Reused evidence ledger: `evidence-pack.yml` (`run-evidence-pack.v1`), validated by the existing `validate_claim_evidence.py`.
- Result: `validation_status: partial`. Static verifier, Vitest suite, and forced-500 error-envelope assertion passed (exit code 0); `npm audit --audit-level=moderate` exited 1 with 5 high-severity dev-toolchain advisories (esbuild/vite/vitest), observed and not remediated.
- This closure is runtime evidence only and changes none of the non-claims in section 11.3.

