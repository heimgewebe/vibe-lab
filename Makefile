# Makefile — Schlanke Routine-Frontdoor
# Siehe: docs/foundations/repo-plan.md → Scaffolding-CLI & Frontdoor

.PHONY: validate validate-schemas validate-execution-proof validate-relations validate-epistemics generate generate-epistemic-state prepare-commit check-generated-clean help

# Minimaler Guard-Stack
validate: validate-schemas validate-execution-proof validate-relations validate-epistemics
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

# Diagnose-Generatoren
generate: generate-doc-index generate-backlinks generate-orphans generate-system-map generate-epistemic-state
	@echo "✅ Generated diagnostics in docs/_generated/."

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

prepare-commit: generate validate check-generated-clean
	@echo "✅ Repo vorbereitet."

check-generated-clean:
	@if ! git diff --quiet -- docs/_generated/ || [ -n "$(git ls-files --others --exclude-standard docs/_generated/)" ]; then \
		echo "❌ docs/_generated/ ist nicht synchron."; \
		echo "Bitte ausführen:"; \
		echo "  make generate"; \
		echo "  git add docs/_generated/"; \
		exit 1; \
	fi

help:
	@echo "Vibe-Lab Makefile"
	@echo ""
	@echo "  make validate                  — Run minimal guard stack (schema + execution-proof + relations + epistemics)"
	@echo "  make validate-schemas          — Validate artifacts against JSON schemas"
	@echo "  make validate-execution-proof  — Validate run_meta.json and adoption_basis coupling"
	@echo "  make validate-relations        — Validate frontmatter relations"
	@echo "  make validate-epistemics       — Validate interpretation_budget for adopted experiments"
	@echo "  make generate           — Generate all diagnostics in docs/_generated/"
	@echo "  make generate-epistemic-state — Generate epistemic state overview"
	@echo "  make prepare-commit     — Run generate + validate + generated-drift check"
	@echo "  make check-generated-clean — Fail if docs/_generated/ has unstaged or untracked drift"
	@echo "  make help               — Show this help"
