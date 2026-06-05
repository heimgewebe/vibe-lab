---
title: "Cross-Run Assessment: Model-Lab Replication Series Run-001 vs Run-002"
status: draft
canonicality: operative
triggered_by: user-request-2026-06-04-cross-run-assessment
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

Kein tatsächliches Runtime-Verhalten kann aus diesen Bundles abgeleitet werden, da keine `npm test`-/Vitest-Ausgabe im Run-Bundle archiviert ist.

## 7. Evidenzlücken

* Runtime execution of Vitest specs is not evidenced in the run bundles.
* Forced 500 path runtime assertion is not evidenced.
* Update: The runtime behavior of the 500 path has been evidenced separately in `runtime-validation-run-001-run-002`.
* Condition contrast is weak structural control.
* No external/independent auditor comparison exists for this pair.
* No model-quality or causal outcome conclusion can be drawn.

## 8. Gegenhypothesen

Gegenhypothese A:
Die sichtbaren Unterschiede zwischen Run-001 und Run-002 sind hauptsächlich Artefakt-/Label-Unterschiede, nicht methodisch relevante Generierungsunterschiede.

Gegenhypothese B:
Die Vergleichbarkeit ist formal hergestellt, aber praktisch noch zu schwach, um einen belastbaren Qualitätsvergleich zu tragen.

## 9. Assessment Verdict

Assessment verdict: comparison_surface_assessed_with_inconclusive_quality_result

## 10. Next Steps

1. ~~Optional runtime validation run for both implementations, including forced 500 assertion.~~ (Completed: `artifacts/runtime-validation-run-001-run-002`)
2. Optional Run-003 with genuinely stronger condition contrast.
3. Only after that: consider a formal `decision_type=result_assessment`.
4. Continue to block model-quality/adoption/promotion claims until stronger evidence exists.
