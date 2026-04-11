# Makefile — Schlanke Routine-Frontdoor
# Siehe: repo-plan.md → Scaffolding-CLI & Frontdoor

.PHONY: validate validate-schemas validate-relations validate-execution-proof generate help

# Minimaler Guard-Stack
validate: validate-schemas validate-relations validate-execution-proof
	@echo "✅ Validation passed."

validate-schemas:
	@echo "🔍 Validating schemas..."
	@python3 scripts/docmeta/validate_schema.py

validate-relations:
	@echo "🔗 Validating relations..."
	@python3 scripts/docmeta/validate_relations.py

validate-execution-proof:
	@echo "📜 Validating execution proof..."
	@python3 scripts/docmeta/validate_execution_proof.py

# Diagnose-Generatoren
generate: generate-doc-index generate-backlinks generate-orphans generate-system-map
	@echo "✅ Generated diagnostics in docs/_generated/."

generate-doc-index:
	@python3 scripts/docmeta/generate_doc_index.py

generate-backlinks:
	@python3 scripts/docmeta/generate_backlinks.py

generate-orphans:
	@python3 scripts/docmeta/generate_orphans.py

generate-system-map:
	@python3 scripts/docmeta/generate_system_map.py

help:
	@echo "Vibe-Lab Makefile"
	@echo ""
	@echo "  make validate           — Run minimal guard stack (schema + relations)"
	@echo "  make validate-schemas   — Validate artifacts against JSON schemas"
	@echo "  make validate-relations — Validate frontmatter relations
	@echo "  make validate-execution-proof — Validate execution proof""
	@echo "  make generate           — Generate all diagnostics in docs/_generated/"
	@echo "  make help               — Show this help"
