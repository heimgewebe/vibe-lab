# Makefile — Schlanke Routine-Frontdoor
# Siehe: docs/foundations/repo-plan.md → Scaffolding-CLI & Frontdoor

.PHONY: validate-operator-routing-ml-readiness-audit-tests validate-experiment-registration validate-experiment-registration-tests validate-rlens-agent-context-conditions validate-rlens-agent-context-conditions-tests validate validate-doc-freshness-registry validate-doc-freshness-registry-tests validate-bundle-freshness-receipt-tests validate-operator-lab-run-cards validate-operator-lab-run-cards-tests validate-operator-lab-metrics validate-operator-lab-metrics-tests validate-ecosystem-organ-preflight validate-ecosystem-organ-preflight-tests validate-pr-context-pilot validate-pr-context-pilot-tests validate-schemas validate-schemas-counterevidence-tests validate-execution-proof validate-run-bundle validate-run-bundle-tests validate-model-lab-control-tests validate-model-lab-control validate-challenge-version-tests validate-challenge-versions validate-relations validate-relations-tests validate-backlinks-tests validate-orphans-tests validate-epistemics validate-epistemics-tests validate-agent-handoff validate-agent-handoff-tests validate-agent-commands validate-agent-commands-tests validate-command-chain validate-command-chain-tests validate-command-version-policy-tests validate-fixture-matrix-audit-tests validate-known-gaps-audit validate-cross-contract validate-cross-contract-tests validate-replay-dry-run validate-replay-mutation-guard validate-replay-tests validate-replay-trace-contract validate-phase1c-fixtures validate-phase1c-fixture-tests validate-adoption-completeness validate-adoption-completeness-tests validate-epistemic-state-tests validate-exports-tests validate-export-parity validate-export-parity-tests validate-promotion-readiness validate-promotion-readiness-tests validate-promotion-readiness-ratchet validate-ratchet validate-generated-artifacts-contract validate-generated-artifacts-contract-tests validate-artifact-taxonomy validate-artifact-taxonomy-tests validate-artifact-taxonomy-contract-tests validate-run-evidence-pack-schema-tests validate-claim-evidence validate-claim-evidence-tests validate-runtime-evidence-gate validate-runtime-evidence-gate-tests validate-result-assessment-readiness validate-result-assessment-readiness-tests validate-dependency-risk-caveat-scope validate-dependency-risk-caveat-scope-tests validate-model-lab-next-blocker-triage validate-model-lab-next-blocker-triage-tests validate-model-lab-condition-contrast-design-gate validate-model-lab-condition-contrast-design-gate-tests validate-model-lab-condition-design validate-model-lab-condition-design-tests validate-model-lab-access-policy validate-model-lab-access-policy-tests probe-model-lab-access-policy validate-model-lab-runtime-binding validate-model-lab-runtime-binding-tests validate-model-lab-runtime-candidate validate-model-lab-runtime-candidate-tests validate-model-lab-execution-readiness validate-model-lab-execution-readiness-tests validate-model-lab-execution-seed validate-model-lab-execution-seed-tests validate-model-lab-workspace-isolation validate-model-lab-workspace-isolation-tests validate-pr-scope validate-pr-scope-tests validate-outcome-series validate-outcome-series-tests agent-check agent-check-staged agent-check-tests check-decisions generate generate-blocking generate-generated-diagnostics generate-artifact-only generate-generated-gated generate-projections generate-exports generate-metrics generate-promotion-readiness generate-doc-index generate-system-map generate-backlinks generate-orphans generate-epistemic-state generate-artifact-taxonomy diagnose help validate-active-experiments validate-active-experiments-tests validate-operator-lab-closeout validate-operator-lab-closeout-tests validate-effect-evaluator-tests validate-core validate-active validate-legacy validate-validator-inventory validate-validator-inventory-tests

# Validation frontdoor: complete coverage split by current authority.
validate: validate-core validate-active validate-legacy
	@echo "✅ Validation passed (core + active + legacy)."

validate-core: validate-effect-evaluator-tests validate-doc-freshness-registry-tests validate-doc-freshness-registry validate-bundle-freshness-receipt-tests validate-generated-artifacts-contract validate-generated-artifacts-contract-tests validate-artifact-taxonomy validate-artifact-taxonomy-tests validate-artifact-taxonomy-contract-tests validate-schemas validate-schemas-counterevidence-tests validate-execution-proof validate-run-bundle-tests validate-run-bundle validate-challenge-version-tests validate-challenge-versions validate-relations validate-relations-tests validate-backlinks-tests validate-orphans-tests validate-epistemics validate-epistemics-tests validate-adoption-completeness validate-adoption-completeness-tests validate-epistemic-state-tests validate-export-parity validate-exports-tests validate-export-parity-tests validate-promotion-readiness-tests validate-run-evidence-pack-schema-tests validate-claim-evidence-tests validate-claim-evidence validate-runtime-evidence-gate-tests validate-runtime-evidence-gate validate-result-assessment-readiness-tests validate-result-assessment-readiness validate-dependency-risk-caveat-scope-tests validate-dependency-risk-caveat-scope validate-pr-scope-tests validate-pr-scope agent-check-tests validate-promotion-readiness validate-promotion-readiness-ratchet validate-validator-inventory-tests validate-validator-inventory
	@echo "✅ Core validation passed."

validate-active: validate-operator-routing-ml-readiness-audit-tests validate-active-experiments-tests validate-active-experiments validate-operator-lab-closeout-tests validate-operator-lab-closeout validate-experiment-registration-tests validate-experiment-registration
	@echo "✅ Active experiment validation passed."

validate-legacy: validate-operator-lab-run-cards-tests validate-operator-lab-run-cards validate-operator-lab-metrics-tests validate-operator-lab-metrics validate-ecosystem-organ-preflight-tests validate-ecosystem-organ-preflight validate-model-lab-control-tests validate-model-lab-control validate-agent-handoff validate-agent-handoff-tests validate-agent-commands validate-agent-commands-tests validate-command-chain validate-command-chain-tests validate-command-version-policy-tests validate-fixture-matrix-audit-tests validate-known-gaps-audit validate-cross-contract validate-cross-contract-tests validate-replay-dry-run validate-replay-tests validate-replay-trace-contract validate-phase1c-fixtures validate-phase1c-fixture-tests validate-model-lab-next-blocker-triage-tests validate-model-lab-next-blocker-triage validate-model-lab-condition-contrast-design-gate-tests validate-model-lab-condition-contrast-design-gate validate-model-lab-condition-design-tests validate-model-lab-condition-design validate-model-lab-access-policy-tests validate-model-lab-access-policy validate-model-lab-runtime-binding-tests validate-model-lab-runtime-binding validate-model-lab-runtime-candidate-tests validate-model-lab-runtime-candidate validate-model-lab-execution-readiness-tests validate-model-lab-execution-readiness validate-model-lab-execution-seed-tests validate-model-lab-execution-seed validate-model-lab-workspace-isolation-tests validate-model-lab-workspace-isolation validate-outcome-series-tests validate-outcome-series validate-pr-context-pilot-tests validate-pr-context-pilot validate-rlens-agent-context-conditions-tests validate-rlens-agent-context-conditions
	@echo "✅ Legacy evidence validation passed."


validate-operator-routing-ml-readiness-audit-tests:
	@echo "🧪 Running operator routing ML readiness audit regression tests..."
	@python3 experiments/_archive/2026-07-23_operator-routing-ml-readiness-shadow/tools/test_audit_task_store.py
	@python3 experiments/_archive/2026-07-23_operator-routing-ml-readiness-shadow/tools/test_audit_prospective_cohort.py

validate-experiment-registration:
	@echo "🧭 Validating consumer-bound experiment registrations..."
	@python3 scripts/docmeta/validate_experiment_registration.py

validate-experiment-registration-tests:
	@echo "🧪 Running experiment registration gate tests..."
	@python3 scripts/docmeta/test_validate_experiment_registration.py

validate-doc-freshness-registry:
	@echo "🗂  Validating doc-freshness registry..."
	@python3 scripts/docmeta/validate_doc_freshness_registry.py

validate-doc-freshness-registry-tests:
	@echo "🧪 Running doc-freshness registry regression tests..."
	@python3 scripts/docmeta/test_validate_doc_freshness_registry.py

validate-bundle-freshness-receipt-tests:
	@echo "🧪 Running bundle-freshness receipt regression tests..."
	@python3 scripts/docmeta/test_validate_bundle_freshness_receipt.py

validate-operator-lab-run-cards:
	@echo "🧾 Validating Operator-Lab run-card structure..."
	@python3 scripts/docmeta/validate_operator_lab_run_cards.py

validate-operator-lab-run-cards-tests:
	@echo "🧪 Running Operator-Lab run-card structure regression tests..."
	@python3 scripts/docmeta/test_validate_operator_lab_run_cards.py
validate-operator-lab-metrics:
	@echo "📊 Validating Operator-Lab metrics..."
	@python3 scripts/docmeta/operator_lab_metrics.py
validate-operator-lab-metrics-tests:
	@echo "🧪 Running Operator-Lab metrics regression tests..."
	@python3 scripts/docmeta/test_operator_lab_metrics.py

validate-ecosystem-organ-preflight:
	@echo "🧭 Validating Ecosystem-Organ-Preflight run records..."
	@python3 scripts/docmeta/validate_ecosystem_organ_preflight.py

validate-ecosystem-organ-preflight-tests:
	@echo "🧪 Running Ecosystem-Organ-Preflight regression tests..."
	@python3 scripts/docmeta/test_validate_ecosystem_organ_preflight.py

validate-schemas:
	@echo "🔍 Validating schemas..."
	@python3 scripts/docmeta/validate_schema.py

validate-schemas-counterevidence-tests:
	@echo "🧪 Running counterevidence P2-rule regression tests..."
	@python3 scripts/docmeta/test_validate_schema_counterevidence.py

validate-execution-proof:
	@echo "🔍 Validating execution proof..."
	@python3 scripts/docmeta/validate_execution_proof.py

validate-run-bundle:
	@echo "🧷 Validating experiment run bundles..."
	@python3 scripts/docmeta/validate_run_bundle.py

validate-run-bundle-tests:
	@echo "🧪 Running run-bundle validator regression tests..."
	@python3 scripts/docmeta/test_validate_run_bundle.py

validate-pr-context-pilot-tests:
	@echo "🧪 Running PR-context pilot regression tests..."
	@python3 scripts/docmeta/test_validate_pr_context_pilot.py
	@python3 tools/vibe-cli/test_pr_context_capture.py

validate-pr-context-pilot:
	@echo "🧭 Validating PR-context pilot contract..."
	@python3 scripts/docmeta/validate_pr_context_pilot.py

validate-model-lab-control-tests:
	@echo "🧪 Running Model-Lab control minimum regression tests..."
	@python3 scripts/docmeta/test_validate_model_lab_control.py

validate-model-lab-control:
	@echo "🔬 Validating Model-Lab control metadata (opt-in)..."
	@python3 scripts/docmeta/validate_model_lab_control.py

validate-challenge-version-tests:
	@echo "🧪 Running challenge-version validator regression tests..."
	@python3 scripts/docmeta/test_validate_challenge_versions.py

validate-challenge-versions:
	@echo "🏷️  Validating benchmark challenge versions..."
	@python3 scripts/docmeta/validate_challenge_versions.py

validate-relations:
	@echo "🔗 Validating relations..."
	@python3 scripts/docmeta/validate_relations.py

validate-relations-tests:
	@echo "🧪 Running relations validator regression tests..."
	@python3 scripts/docmeta/test_validate_relations.py

validate-backlinks-tests:
	@echo "🧪 Running backlinks generator regression tests..."
	@python3 scripts/docmeta/test_generate_backlinks.py

validate-orphans-tests:
	@echo "🧪 Running orphans generator regression tests..."
	@python3 scripts/docmeta/test_generate_orphans.py

validate-epistemics:
	@echo "🧠 Validating interpretation budget..."
	@python3 scripts/docmeta/validate_interpretation_budget.py

validate-epistemics-tests:
	@echo "🧪 Running interpretation budget regression tests..."
	@python3 scripts/docmeta/test_validate_interpretation_budget.py

validate-agent-handoff:
	@echo "🤝 Validating agent handoff fixtures..."
	@python3 scripts/docmeta/validate_agent_handoff.py

validate-agent-handoff-tests:
	@echo "🧪 Running agent handoff regression tests..."
	@python3 scripts/docmeta/test_validate_agent_handoff.py

validate-known-gaps-audit:
	@echo "🧪 Running known-gaps audit tests..."
	@python3 scripts/docmeta/test_fixture_matrix_known_gaps_audit.py

validate-agent-commands:
	@echo "🤖 Validating agent command fixtures..."
	@python3 scripts/docmeta/validate_agent_commands.py

validate-agent-commands-tests:
	@echo "🧪 Running agent command regression tests..."
	@python3 scripts/docmeta/test_validate_agent_commands.py

validate-command-chain:
	@echo "🔗 Validating command chain fixtures..."
	@python3 scripts/docmeta/validate_command_chain.py

validate-command-chain-tests:
	@echo "🧪 Running command chain regression tests..."
	@python3 scripts/docmeta/test_validate_command_chain.py

validate-command-version-policy-tests:
	@echo "🧪 Running command version policy tests..."
	@python3 scripts/docmeta/test_command_version_policy.py

validate-fixture-matrix-audit-tests:
	@echo "🧪 Running fixture matrix audit tests..."
	@python3 scripts/docmeta/test_fixture_matrix_audit_surface.py

validate-cross-contract:
	@echo "🪢 Validating cross-contract (Handoff ↔ Chain) fixtures..."
	@python3 scripts/docmeta/validate_command_chain.py --cross-contract-fixtures tests/fixtures/cross_contract

validate-cross-contract-tests:
	@echo "🧪 Running cross-contract regression tests..."
	@python3 tests/contracts/test_cross_contract_chain.py

validate-replay-dry-run:
	@echo "♻️  Replay dry-run (no mutations by design)..."
	@python3 tools/vibe-cli/replay_minimal.py --dry-run >/dev/null
	@# Non-mutation guarantee: enforced at three levels:
	@# 1. By design: replay_minimal.py contains no file-write calls.
	@# 2. By test: test_replay_minimal.py::test_simulate_is_pure asserts no
	@#    input mutation; test_write_change_trace_marks_would_mutate_false
	@#    asserts would_mutate=false in every trace.
	@# 3. By CI: the "Guard — replay must not mutate the repo" step in
	@#    .github/workflows/validate.yml runs git diff in a clean checkout.
	@#    For an equivalent local guard, use: make validate-replay-mutation-guard
	@#    (only conclusive in a clean working tree).
	@echo "✅ Replay trace generator completed (non-mutation enforced by design + tests + CI)."
validate-run-evidence-pack-schema-tests:
	@echo "🧪 Running run-evidence-pack schema regression tests..."
	@python3 scripts/docmeta/test_run_evidence_pack_schema.py

validate-claim-evidence:
	@echo "🔎 Validating claim-evidence semantic rules..."
	@files="$$( { find experiments -path '*/artifacts/*/evidence-pack.yml' -o -path '*/artifacts/*/evidence-pack.yaml' 2>/dev/null; find artifacts -path '*/evidence-pack.yml' -o -path '*/evidence-pack.yaml' 2>/dev/null; } | tr '\n' ' ' )"; \
	if [ -z "$$files" ]; then \
		echo "ℹ️ No run evidence packs found; semantic claim-evidence validation skipped."; \
	else \
		python3 scripts/docmeta/validate_claim_evidence.py $$files; \
	fi

validate-claim-evidence-tests:
	@echo "🧪 Running claim-evidence semantic validator tests..."
	@python3 scripts/docmeta/test_validate_claim_evidence.py

validate-runtime-evidence-gate:
	@echo "⏱  Validating runtime-evidence gates..."
	@python3 scripts/docmeta/validate_runtime_evidence_gate.py

validate-runtime-evidence-gate-tests:
	@echo "🧪 Running runtime-evidence-gate validator tests..."
	@python3 scripts/docmeta/test_validate_runtime_evidence_gate.py

validate-result-assessment-readiness:
	@echo "🚦 Validating result-assessment-readiness gates..."
	@python3 scripts/docmeta/validate_result_assessment_readiness.py

validate-result-assessment-readiness-tests:
	@echo "🧪 Running result-assessment-readiness validator tests..."
	@python3 scripts/docmeta/test_validate_result_assessment_readiness.py

validate-dependency-risk-caveat-scope:
	@echo "🚦 Validating dependency-risk-caveat-scope artifacts..."
	@python3 scripts/docmeta/validate_dependency_risk_caveat_scope.py

validate-dependency-risk-caveat-scope-tests:
	@echo "🧪 Running dependency-risk-caveat-scope validator tests..."
	@python3 scripts/docmeta/test_validate_dependency_risk_caveat_scope.py

validate-model-lab-next-blocker-triage:
	@echo "🧭 Validating model-lab-next-blocker-triage artifacts..."
	@python3 scripts/docmeta/validate_model_lab_next_blocker_triage.py

validate-model-lab-next-blocker-triage-tests:
	@echo "🧪 Running model-lab-next-blocker-triage validator tests..."
	@python3 scripts/docmeta/test_validate_model_lab_next_blocker_triage.py

validate-model-lab-condition-contrast-design-gate-tests:
	@echo "🧪 Running model-lab condition-contrast-design-gate validator tests..."
	@python3 scripts/docmeta/test_validate_model_lab_condition_contrast_design_gate.py

validate-model-lab-condition-contrast-design-gate:
	@echo "🧭 Validating model-lab condition-contrast-design-gate artifacts..."
	@python3 scripts/docmeta/validate_model_lab_condition_contrast_design_gate.py

validate-model-lab-condition-design-tests:
	@echo "🧪 Running model-lab condition-design validator tests..."
	@python3 scripts/docmeta/test_validate_model_lab_condition_design.py

validate-model-lab-condition-design:
	@echo "🧭 Validating model-lab condition-design artifacts..."
	@python3 scripts/docmeta/validate_model_lab_condition_design.py

validate-model-lab-access-policy-tests:
	@echo "🧪 Running Run-004 access-policy sandbox regression tests..."
	@python3 scripts/docmeta/test_validate_model_lab_run004_access_policy.py

validate-model-lab-access-policy:
	@echo "🧭 Validating canonical Run-004 access-policy bundle..."
	@python3 scripts/docmeta/validate_model_lab_run004_access_policy.py

probe-model-lab-access-policy:
	@echo "🧪 Running Run-004 access-policy live negative probe..."
	@python3 scripts/docmeta/probe_model_lab_run004_access_policy.py

validate-model-lab-runtime-binding-tests:
	@echo "🧪 Running Run-004 runtime-binding broker and validator tests..."
	@python3 scripts/docmeta/test_run_model_lab_run004_agent.py
	@python3 scripts/docmeta/test_validate_model_lab_run004_runtime_binding.py

validate-model-lab-runtime-binding:
	@echo "🧭 Validating canonical Run-004 runtime-binding bundle..."
	@python3 scripts/docmeta/validate_model_lab_run004_runtime_binding.py

validate-model-lab-execution-readiness-tests:
	@echo "🧪 Running model-lab execution-readiness validator tests..."
	@python3 scripts/docmeta/test_validate_model_lab_execution_readiness.py

validate-model-lab-execution-readiness:
	@echo "🧭 Validating model-lab execution-readiness artifacts..."
	@python3 scripts/docmeta/validate_model_lab_execution_readiness.py

validate-model-lab-execution-seed-tests:
	@echo "🧪 Running model-lab execution-seed builder tests..."
	@python3 scripts/docmeta/test_build_model_lab_execution_seed.py

validate-model-lab-execution-seed:
	@echo "🌱 Validating canonical Run-004 execution seed..."
	@python3 scripts/docmeta/build_model_lab_execution_seed.py

validate-model-lab-workspace-isolation-tests:
	@echo "🧪 Running Run-004 workspace-isolation materializer tests..."
	@python3 scripts/docmeta/test_prepare_model_lab_run004_workspaces.py

validate-model-lab-workspace-isolation:
	@echo "🧱 Validating canonical Run-004 workspace-isolation plan..."
	@python3 scripts/docmeta/prepare_model_lab_run004_workspaces.py

validate-pr-scope:
	@echo "🔎 Validating PR scope / artifact boundary..."
	@python3 scripts/docmeta/validate_pr_scope.py

validate-pr-scope-tests:
	@echo "🧪 Running PR scope validator tests..."
	@python3 scripts/docmeta/test_validate_pr_scope.py

validate-outcome-series:
	@echo "🔒 Validating outcome-evidence-replication-series gate..."
	@python3 scripts/docmeta/validate_outcome_evidence_replication_series.py

validate-outcome-series-tests:
	@echo "🧪 Running outcome-evidence-replication-series gate tests..."
	@python3 scripts/docmeta/test_validate_outcome_evidence_replication_series.py

validate-replay-tests:
	@echo "🧪 Running replay runner regression tests..."
	@python3 tools/vibe-cli/test_replay_minimal.py

validate-replay-trace-contract:
	@echo "🧪 Running replay trace contract tests (v0.2)..."
	@python3 tools/vibe-cli/test_replay_trace_contract.py

validate-replay-mutation-guard:
	@echo "🔒 Replay mutation guard (requires clean working tree)..."
	@# This target mirrors the CI step "Guard — replay must not mutate the repo".
	@# It is only conclusive in a clean working tree (i.e., no uncommitted changes).
	@# In CI this runs after every checkout; locally, call it explicitly when needed.
	@if [ -n "$$(git status --porcelain)" ]; then \
	    echo "⚠️  Working tree is dirty — guard would produce a false positive."; \
	    echo "   Commit or stash your changes, then re-run this target."; \
	    exit 1; \
	fi
	@python3 tools/vibe-cli/replay_minimal.py --dry-run >/dev/null
	@if [ -n "$$(git status --porcelain)" ]; then \
	    echo "❌ Replay produced filesystem changes (tracked or untracked) — non-mutation contract violated."; \
	    git status --porcelain; \
	    exit 1; \
	fi
	@echo "✅ Replay mutation guard passed (clean tree, no changes after run)."

validate-phase1c-fixtures:
	@echo "🧭 Validating Phase-1c fixture corpus..."
	@python3 scripts/docmeta/validate_experiment_structure_phase1c_fixtures.py

validate-phase1c-fixture-tests:
	@echo "🧪 Running Phase-1c fixture checker regression tests..."
	@python3 scripts/docmeta/test_validate_experiment_structure_phase1c_fixtures.py

validate-adoption-completeness:
	@echo "📦 Validating adoption completeness..."
	@python3 scripts/adoption/validate_adoption_completeness.py

validate-adoption-completeness-tests:
	@echo "🧪 Running adoption completeness regression tests..."
	@python3 scripts/adoption/test_validate_adoption_completeness.py

validate-epistemic-state-tests:
	@echo "🧪 Running epistemic state regression tests..."
	@python3 scripts/docmeta/test_generate_epistemic_state.py

validate-exports-tests:
	@echo "🧪 Running export generator regression tests..."
	@python3 scripts/exports/test_generate_exports.py

validate-export-parity:
	@echo "🔎 Validating export parity (collision / orphan / missing)..."
	@python3 scripts/exports/validate_export_parity.py

validate-export-parity-tests:
	@echo "🧪 Running export parity validator regression tests..."
	@python3 scripts/exports/test_validate_export_parity.py

validate-promotion-readiness:
	@echo "🔎 Running promotion-readiness dry-run (Phase 1, non-blocking)..."
	@python3 scripts/docmeta/validate_promotion_readiness.py

validate-promotion-readiness-tests:
	@echo "🧪 Running promotion-readiness regression tests..."
	@python3 scripts/docmeta/test_promotion_readiness.py

validate-promotion-readiness-ratchet:
	@echo "🔒 Running promotion-readiness ratchet (Phase 2, blocking for new violations)..."
	@# Reads .vibe/promotion-readiness-freeze.yml for the historical baseline.
	@# Passes only if all not_ready experiments are in the freeze and no freeze entry is stale.
	@# New experiments without falsifiability will fail here; add a freeze entry only with
	@# an explicit reason (not as a blanket bypass).
	@python3 scripts/docmeta/validate_promotion_readiness.py --ratchet

validate-ratchet: validate-promotion-readiness-ratchet

validate-generated-artifacts-contract:
	@echo "📜 Validating generated-artifact contract (v2)..."
	@python3 scripts/docmeta/validate_generated_artifacts_contract.py

validate-generated-artifacts-contract-tests:
	@echo "🧪 Running generated-artifact contract regression tests..."
	@python3 scripts/docmeta/test_validate_generated_artifacts_contract.py

validate-artifact-taxonomy:
	@echo "📋 Validating artifact taxonomy contract..."
	@python3 scripts/docmeta/validate_artifact_taxonomy.py

validate-artifact-taxonomy-tests:
	@echo "🧪 Running artifact taxonomy generator regression tests..."
	@python3 scripts/docmeta/test_generate_artifact_taxonomy.py

validate-artifact-taxonomy-contract-tests:
	@echo "🧪 Running artifact taxonomy contract validator regression tests..."
	@python3 scripts/docmeta/test_validate_artifact_taxonomy.py

agent-check:
	@echo "🛡  Running fast agent compliance guard (canonical + generated paths)..."
	@python3 scripts/agents/check_agent_compliance.py

agent-check-staged:
	@echo "🛡  Running fast agent compliance guard on staged paths..."
	@python3 scripts/agents/check_agent_compliance.py --staged --quiet

agent-check-tests:
	@echo "🧪 Running agent compliance guard regression tests..."
	@python3 scripts/agents/test_check_agent_compliance.py

check-decisions:
	@echo "🔐 Validating system decision guard..."
	@python3 scripts/docmeta/check_system_decisions.py

# Diagnose-Generatoren (v2 contract: filter-driven)
generate: generate-blocking generate-generated-diagnostics
	@$(MAKE) generate-generated-gated || true
	@echo "✅ Generated diagnostics in docs/_generated/."

# Blocking artifacts: ci_policy=blocking (generated index + projections)
generate-blocking: generate-doc-index generate-projections
	@echo "✅ Generated blocking artifacts (doc-index, projections)."

# Non-blocking diagnostic artifacts: ci_policy=non_blocking
generate-generated-diagnostics: generate-system-map generate-backlinks generate-orphans generate-promotion-readiness generate-artifact-taxonomy
	@echo "✅ Generated non-blocking diagnostics in docs/_generated/."

# artifact_only runtime artifacts: ci_policy=artifact_only, commit_policy=do_not_commit
# These are NOT committed and NOT part of the normal generate flow.
# Run explicitly for local inspection or in the ephemeral-diagnostics CI job.
generate-artifact-only: generate-epistemic-state
	@echo "✅ Generated artifact-only runtime diagnostics (not committed)."

# Gated/best-effort artifacts: activation=gated or ci_policy=best_effort
generate-generated-gated: generate-metrics
	@echo "✅ Generated gated diagnostics in docs/_generated/."

# Tool projections: class=generated_projection
generate-projections: generate-exports
	@echo "✅ Generated tool projections in exports/."

diagnose: generate-generated-diagnostics
	@$(MAKE) generate-generated-gated || true
	@echo "✅ Generated non-blocking diagnostics for local inspection."

generate-doc-index:
	@python3 scripts/docmeta/generate_doc_index.py

generate-backlinks:
	@python3 scripts/docmeta/generate_backlinks.py

generate-orphans:
	@python3 scripts/docmeta/generate_orphans.py

generate-promotion-readiness:
	@# Writes docs/_generated/promotion-readiness.json via write_if_changed.
	@# Dry-run: exit=0 unless the script itself crashes.
	@python3 scripts/docmeta/validate_promotion_readiness.py

generate-system-map:
	@python3 scripts/docmeta/generate_system_map.py

generate-epistemic-state:
	@python3 scripts/docmeta/generate_epistemic_state.py

generate-exports:
	@python3 scripts/exports/generate_exports.py

generate-metrics: check-decisions
	@python3 scripts/docmeta/generate_metrics.py

generate-artifact-taxonomy:
	@python3 scripts/docmeta/generate_artifact_taxonomy.py

help:
	@echo "Vibe-Lab Makefile"
	@echo ""
	@echo "  make validate                  — Run schema, execution-proof, relations, interpretation-budget, handoff, generated-artifact contract, and regression-test guards"
	@echo "  make validate-core             — Run generic repository, schema, evidence, relation, and generated-artifact guards"
	@echo "  make validate-active           — Run only validators owned by active experiments and the frozen Operator-Lab closeout"
	@echo "  make validate-legacy           — Run grandfathered historical experiment and agent-operability guards"
	@echo "  make validate-validator-inventory — Prove every validator target is classified and CI uses the grouped frontdoor"
	@echo "  make agent-check               — Fast guard: blocks edits to canonical control documents and generated artifacts (~2 s)"
	@echo "  make agent-check-tests         — Run agent compliance guard regression tests"
	@echo "  make validate-generated-artifacts-contract — Validate .vibe/generated-artifacts.yml against v2 contract"
	@echo "  make validate-generated-artifacts-contract-tests — Run generated-artifact contract regression tests"
	@echo "  make validate-artifact-taxonomy-tests — Run artifact taxonomy generator regression tests"
	@echo "  make validate-doc-freshness-registry — Validate docs/doc-freshness-registry.yml (mirrors CI workflow)"
	@echo "  make validate-doc-freshness-registry-tests — Run doc-freshness registry regression tests"
	@echo "  make validate-bundle-freshness-receipt-tests — Run bundle-freshness receipt regression tests (mirrors CI workflow)"
	@echo "  make validate-schemas                  — Validate artifacts against JSON schemas"
	@echo "  make validate-schemas-counterevidence-tests — Run P2 counterevidence rule regression tests"
	@echo "  make validate-execution-proof  — Validate run_meta.json and adoption_basis coupling"
	@echo "  make validate-run-bundle       — Cross-validate experiment run bundles (run.yml, auditor-output.yml, measurement.yml)"
	@echo "  make validate-run-bundle-tests — Run run-bundle validator regression tests"
	@echo "  make validate-model-lab-runtime-binding — Validate Run-004 runtime-binding bundle"
	@echo "  make validate-model-lab-runtime-binding-tests — Run Run-004 runtime-binding broker/validator tests"
	@echo "  make validate-model-lab-execution-readiness — Validate Run-004 execution-readiness preflight artifacts"
	@echo "  make validate-model-lab-execution-readiness-tests — Run Run-004 execution-readiness validator regression tests"
	@echo "  make validate-relations        — Validate frontmatter relations"
	@echo "  make validate-relations-tests  — Run relations validator regression tests"
	@echo "  make validate-backlinks-tests  — Run backlinks generator regression tests"
	@echo "  make validate-orphans-tests    — Run orphans generator regression tests"
	@echo "  make validate-epistemics       — Validate interpretation_budget for adopted experiments"
	@echo "  make validate-epistemics-tests — Run interpretation_budget unit regression tests"
	@echo "  make validate-agent-handoff    — Validate HANDOFF_BLOCK schema/hash fixtures"
	@echo "  make validate-agent-handoff-tests — Run HANDOFF_BLOCK unit regression tests"
	@echo "  make validate-agent-commands   — Validate agent command fixtures against command.*.schema.json"
	@echo "  make validate-agent-commands-tests — Run agent command unit regression tests"
	@echo "  make validate-command-chain    — Validate command chain fixtures"
	@echo "  make validate-command-chain-tests — Run command chain regression tests"
	@echo "  make validate-cross-contract   — Validate Handoff ↔ Chain cross-contract fixtures"
	@echo "  make validate-cross-contract-tests — Run cross-contract regression tests"
	@echo "  make validate-replay-dry-run   — Simulate a validated chain without mutations"
	@echo "  make validate-replay-tests     — Run replay runner regression tests"
	@echo "  make validate-replay-trace-contract — Run replay trace contract tests (v0.2, schema-validated)"
	@echo "  make validate-phase1c-fixtures — Validate Phase-1c fixture corpus against expected outcomes"
	@echo "  make validate-phase1c-fixture-tests — Run Phase-1c fixture checker unit regression tests"
	@echo "  make validate-adoption-completeness — Validate adopted experiments have catalog extractions"
	@echo "  make validate-adoption-completeness-tests — Run adoption completeness regression tests (path-match)"
	@echo "  make validate-epistemic-state-tests — Run interpretation risk regression tests"
	@echo "  make validate-exports-tests — Run export generator regression tests"
	@echo "  make validate-export-parity — Validate export parity: collision / orphan / missing (blocking)"
	@echo "  make validate-export-parity-tests — Run export parity validator regression tests"
	@echo "  make validate-promotion-readiness — Dry-run Phase-1 promotion-readiness gate (non-blocking)"
	@echo "  make validate-promotion-readiness-tests — Run promotion-readiness regression tests"
	@echo "  make validate-promotion-readiness-ratchet — Phase-2 ratchet: blocks new violations (requires .vibe/promotion-readiness-freeze.yml)"
	@echo "  make validate-ratchet — Alias for validate-promotion-readiness-ratchet"
	@echo "  make check-decisions         — Validate system decisions and gate required features"
	@echo "  make generate           — Generate all committable v2 artifacts (blocking + diagnostics + gated; excludes ci_policy=artifact_only)"
	@echo "  make generate-blocking  — Generate blocking artifacts (doc-index, projections)"
	@echo "  make generate-generated-diagnostics — Generate non-blocking diagnostic artifacts (ci_policy=non_blocking)"
	@echo "  make generate-artifact-only         — Generate artifact-only runtime diagnostics (not committed; ci_policy=artifact_only)"
	@echo "  make generate-generated-gated       — Generate gated/best-effort diagnostic artifacts"
	@echo "  make generate-projections           — Generate tool projections (exports/)"
	@echo "  make diagnose           — Alias for non-blocking diagnostics"
	@echo "  make generate-epistemic-state — Generate epistemic state overview (artifact-only, not committed)"
	@echo "  make generate-exports   — Generate exports from instruction-blocks"
	@echo "  make generate-metrics   — Generate decision-gated metrics trend report"
	@echo "  make generate-artifact-taxonomy — Generate artifact taxonomy report (diagnostic)"
	@echo "  make help               — Show this help"

validate-model-lab-runtime-candidate-tests:
	@echo "Running Run-004 runtime-candidate validator regression tests..."
	@python3 scripts/docmeta/test_validate_model_lab_runtime_candidate.py

validate-model-lab-runtime-candidate:
	@echo "Validating Run-004 runtime-candidate preflight artifacts..."
	@python3 scripts/docmeta/validate_model_lab_runtime_candidate.py


validate-rlens-agent-context-conditions:
	@python3 scripts/docmeta/validate_rlens_agent_context_conditions.py

validate-rlens-agent-context-conditions-tests:
	@PYTHONPATH=scripts/docmeta python3 scripts/docmeta/test_validate_rlens_agent_context_conditions.py

validate-active-experiments:
	python3 scripts/docmeta/validate_active_experiments.py

validate-active-experiments-tests:
	python3 scripts/docmeta/test_validate_active_experiments.py

validate-operator-lab-closeout:
	python3 scripts/docmeta/operator_lab_closeout.py --check

validate-operator-lab-closeout-tests:
	python3 scripts/docmeta/test_operator_lab_closeout.py

validate-effect-evaluator-tests:
	python3 tools/vibe-cli/test_admit_natural_case.py
	python3 tools/vibe-cli/test_capture_effect_observation.py
	python3 tools/vibe-cli/test_evaluate_effect.py

validate-validator-inventory:
	@echo "🗂  Validating validator inventory and group coverage..."
	@python3 scripts/docmeta/validate_validator_inventory.py

validate-validator-inventory-tests:
	@echo "🧪 Running validator inventory regression tests..."
	@python3 scripts/docmeta/test_validate_validator_inventory.py
