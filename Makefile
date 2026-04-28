# Makefile — Schlanke Routine-Frontdoor
# Siehe: docs/foundations/repo-plan.md → Scaffolding-CLI & Frontdoor

.PHONY: validate validate-schemas validate-schemas-counterevidence-tests validate-execution-proof validate-relations validate-epistemics validate-epistemics-tests validate-agent-handoff validate-agent-handoff-tests validate-agent-commands validate-agent-commands-tests validate-command-chain validate-command-chain-tests validate-command-version-policy-tests validate-fixture-matrix-audit-tests validate-known-gaps-audit validate-cross-contract validate-cross-contract-tests validate-replay-dry-run validate-replay-mutation-guard validate-replay-tests validate-replay-trace-contract validate-phase1c-fixtures validate-phase1c-fixture-tests validate-adoption-completeness validate-adoption-completeness-tests validate-epistemic-state-tests validate-exports-tests validate-export-parity validate-export-parity-tests validate-promotion-readiness validate-promotion-readiness-tests validate-promotion-readiness-ratchet validate-ratchet validate-generated-artifacts-contract validate-generated-artifacts-contract-tests validate-artifact-taxonomy validate-artifact-taxonomy-tests validate-artifact-taxonomy-contract-tests check-decisions generate generate-blocking generate-generated-diagnostics generate-artifact-only generate-generated-gated generate-projections generate-exports generate-metrics generate-promotion-readiness generate-doc-index generate-system-map generate-backlinks generate-orphans generate-epistemic-state generate-artifact-taxonomy diagnose help

# Minimaler Guard-Stack
validate: validate-generated-artifacts-contract validate-generated-artifacts-contract-tests validate-artifact-taxonomy validate-artifact-taxonomy-tests validate-artifact-taxonomy-contract-tests validate-schemas validate-schemas-counterevidence-tests validate-execution-proof validate-relations validate-epistemics validate-epistemics-tests validate-agent-handoff validate-agent-handoff-tests validate-agent-commands validate-agent-commands-tests validate-command-chain validate-command-chain-tests validate-command-version-policy-tests validate-fixture-matrix-audit-tests validate-known-gaps-audit validate-cross-contract validate-cross-contract-tests validate-replay-dry-run validate-replay-tests validate-replay-trace-contract validate-phase1c-fixtures validate-phase1c-fixture-tests validate-adoption-completeness validate-adoption-completeness-tests validate-epistemic-state-tests validate-export-parity validate-exports-tests validate-export-parity-tests validate-promotion-readiness-tests
	@# Promotion-Readiness als Dry-Run (Phase 1): inhaltliche not_ready-Befunde
	@# sind non-blocking, weil das Skript dafür exit=0 liefert. Echte Crashes
	@# (ImportError, RuntimeError, fehlende Dateien) sollen make validate brechen.
	@$(MAKE) validate-promotion-readiness
	@# Ratchet (Phase 2): blockiert neue nicht eingefrorene Verstöße.
	@# Historische not_ready-Fälle aus .vibe/promotion-readiness-freeze.yml bleiben sichtbar,
	@# blockieren aber nicht. Stale/over-permissive Freeze-Einträge blockieren.
	@$(MAKE) validate-promotion-readiness-ratchet
	@echo "✅ Validation passed."

validate-schemas:
	@echo "🔍 Validating schemas..."
	@python3 scripts/docmeta/validate_schema.py

validate-schemas-counterevidence-tests:
	@echo "🧪 Running counterevidence P2-rule regression tests..."
	@python3 scripts/docmeta/test_validate_schema_counterevidence.py

validate-execution-proof:
	@echo "🔍 Validating execution proof..."
	@python3 scripts/docmeta/validate_execution_proof.py

validate-relations:
	@echo "🔗 Validating relations..."
	@python3 scripts/docmeta/validate_relations.py

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
	@echo "  make validate-generated-artifacts-contract — Validate .vibe/generated-artifacts.yml against v2 contract"
	@echo "  make validate-generated-artifacts-contract-tests — Run generated-artifact contract regression tests"
	@echo "  make validate-artifact-taxonomy-tests — Run artifact taxonomy generator regression tests"
	@echo "  make validate-schemas                  — Validate artifacts against JSON schemas"
	@echo "  make validate-schemas-counterevidence-tests — Run P2 counterevidence rule regression tests"
	@echo "  make validate-execution-proof  — Validate run_meta.json and adoption_basis coupling"
	@echo "  make validate-relations        — Validate frontmatter relations"
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
