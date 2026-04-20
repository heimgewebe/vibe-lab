# Makefile — Schlanke Routine-Frontdoor
# Siehe: docs/foundations/repo-plan.md → Scaffolding-CLI & Frontdoor

.PHONY: validate validate-schemas validate-execution-proof validate-relations validate-epistemics validate-epistemics-tests validate-agent-handoff validate-agent-handoff-tests validate-agent-commands validate-agent-commands-tests validate-phase1c-fixtures validate-phase1c-fixture-tests validate-adoption-completeness validate-adoption-completeness-tests validate-epistemic-state-tests validate-exports-tests generate generate-canonical generate-derived generate-ephemeral generate-exports generate-stable generate-volatile diagnose generate-epistemic-state help

# Minimaler Guard-Stack
validate: validate-schemas validate-execution-proof validate-relations validate-epistemics validate-epistemics-tests validate-agent-handoff validate-agent-handoff-tests validate-agent-commands validate-agent-commands-tests validate-phase1c-fixtures validate-phase1c-fixture-tests validate-adoption-completeness validate-adoption-completeness-tests validate-epistemic-state-tests validate-exports-tests
	@echo "✅ Validation passed."

validate-schemas:
	@echo "🔍 Validating schemas..."
	@python3 scripts/docmeta/validate_schema.py

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

validate-agent-commands:
	@echo "🤖 Validating agent command fixtures..."
	@python3 scripts/docmeta/validate_agent_commands.py

validate-agent-commands-tests:
	@echo "🧪 Running agent command regression tests..."
	@python3 scripts/docmeta/test_validate_agent_commands.py

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

# Diagnose-Generatoren
generate: generate-canonical generate-derived generate-ephemeral
	@echo "✅ Generated diagnostics in docs/_generated/."

generate-canonical: generate-doc-index generate-system-map generate-exports
	@echo "✅ Generated canonical diagnostics in docs/_generated/."

generate-derived: generate-backlinks generate-orphans
	@echo "✅ Generated derived diagnostics in docs/_generated/."

generate-ephemeral: generate-epistemic-state
	@echo "✅ Generated ephemeral diagnostics in docs/_generated/."

# Backward-compatible aliases
generate-stable: generate-canonical
generate-volatile: generate-derived generate-ephemeral

diagnose: generate-derived generate-ephemeral
	@echo "✅ Generated non-blocking diagnostics for local inspection."

generate-doc-index:
	@python3 scripts/docmeta/generate_doc_index.py

generate-backlinks:
	@python3 scripts/docmeta/generate_backlinks.py

generate-orphans:
	@python3 scripts/docmeta/generate_orphans.py

generate-system-map:
	@python3 scripts/docmeta/generate_system_map.py

generate-epistemic-state:
	@python3 scripts/docmeta/generate_epistemic_state.py

generate-exports:
	@python3 scripts/exports/generate_exports.py

help:
	@echo "Vibe-Lab Makefile"
	@echo ""
	@echo "  make validate                  — Run schema, execution-proof, relations, interpretation-budget, handoff, and regression-test guards"
	@echo "  make validate-schemas          — Validate artifacts against JSON schemas"
	@echo "  make validate-execution-proof  — Validate run_meta.json and adoption_basis coupling"
	@echo "  make validate-relations        — Validate frontmatter relations"
	@echo "  make validate-epistemics       — Validate interpretation_budget for adopted experiments"
	@echo "  make validate-epistemics-tests — Run interpretation_budget unit regression tests"
	@echo "  make validate-agent-handoff    — Validate HANDOFF_BLOCK schema/hash fixtures"
	@echo "  make validate-agent-handoff-tests — Run HANDOFF_BLOCK unit regression tests"
	@echo "  make validate-agent-commands   — Validate agent command fixtures against command.*.schema.json"
	@echo "  make validate-agent-commands-tests — Run agent command unit regression tests"
	@echo "  make validate-phase1c-fixtures — Validate Phase-1c fixture corpus against expected outcomes"
	@echo "  make validate-phase1c-fixture-tests — Run Phase-1c fixture checker unit regression tests"
	@echo "  make validate-adoption-completeness — Validate adopted experiments have catalog extractions"
	@echo "  make validate-adoption-completeness-tests — Run adoption completeness regression tests (path-match)"
	@echo "  make validate-epistemic-state-tests — Run interpretation risk regression tests"
	@echo "  make validate-exports-tests — Run export generator regression tests"
	@echo "  make generate           — Generate canonical, derived, and ephemeral diagnostics"
	@echo "  make generate-canonical — Generate contract-relevant diagnostics (blocking in CI)"
	@echo "  make generate-derived   — Generate reconstructable diagnostics (non-blocking in CI)"
	@echo "  make generate-ephemeral — Generate runtime-only diagnostics (artifact-first)"
	@echo "  make generate-stable    — Alias for make generate-canonical"
	@echo "  make generate-volatile  — Alias for make generate-derived + make generate-ephemeral"
	@echo "  make diagnose           — Alias for non-blocking diagnostics"
	@echo "  make generate-epistemic-state — Generate epistemic state overview"
	@echo "  make generate-exports   — Generate exports from instruction-blocks"
	@echo "  make help               — Show this help"
