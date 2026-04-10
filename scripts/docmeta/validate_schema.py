#!/usr/bin/env python3
"""validate_schema.py — Validiert Artefakte gegen JSON-Schemas.

Prüft:
- experiments/*/manifest.yml gegen schemas/experiment.manifest.schema.json
- catalog/**/*.md Frontmatter gegen schemas/catalog.entry.schema.json
- catalog/combos/**/*.md Frontmatter gegen schemas/combo.schema.json
- experiments/*/results/evidence.jsonl auf Struktur und Taxonomie

Benötigt: pip install pyyaml jsonschema
"""

import json
import sys
from pathlib import Path

# Gemeinsame Pfad-Logik aus _paths.py
sys.path.insert(0, str(Path(__file__).parent))
from _paths import extract_frontmatter  # noqa: E402

try:
    import yaml
    from jsonschema import validate, ValidationError, SchemaError
except ImportError:
    print("ERROR: Missing dependencies. Run: pip install pyyaml jsonschema")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

SCHEMA_MAP = {
    "experiment_manifest": REPO_ROOT / "schemas" / "experiment.manifest.schema.json",
    "catalog_entry": REPO_ROOT / "schemas" / "catalog.entry.schema.json",
    "combo": REPO_ROOT / "schemas" / "combo.schema.json",
}

# Pflichtfelder für jede Zeile in evidence.jsonl
EVIDENCE_REQUIRED_KEYS: frozenset[str] = frozenset({
    "event_type", "timestamp", "iteration", "metric", "value", "context"
})

# Erlaubte Werte für event_type
EVIDENCE_EVENT_TYPES: frozenset[str] = frozenset({"observation", "measurement", "decision"})

errors = []


def load_schema(schema_path: Path) -> dict:
    with open(schema_path) as f:
        return json.load(f)


def load_yaml(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f) or {}


def validate_experiment_manifests():
    schema_path = SCHEMA_MAP["experiment_manifest"]
    if not schema_path.exists():
        errors.append(f"  Schema not found: {schema_path}")
        return

    schema = load_schema(schema_path)
    experiments_dir = REPO_ROOT / "experiments"

    for manifest in experiments_dir.glob("*/manifest.yml"):
        if manifest.parent.name.startswith("_"):
            continue  # Skip _template, _archive
        try:
            data = load_yaml(manifest)
            validate(instance=data, schema=schema)
            print(f"  ✅ {manifest.relative_to(REPO_ROOT)}")
        except ValidationError as e:
            errors.append(f"  ❌ {manifest.relative_to(REPO_ROOT)}: {e.message}")
        except SchemaError as e:
            errors.append(f"  ❌ Schema error: {e.message}")


def validate_catalog_entries():
    schema_path = SCHEMA_MAP["catalog_entry"]
    combo_schema_path = SCHEMA_MAP["combo"]
    if not schema_path.exists():
        errors.append(f"  Schema not found: {schema_path}")
        return

    schema = load_schema(schema_path)
    combo_schema = load_schema(combo_schema_path) if combo_schema_path.exists() else None

    catalog_dir = REPO_ROOT / "catalog"
    for md_file in catalog_dir.rglob("*.md"):
        fm = extract_frontmatter(md_file)
        if fm is None:
            continue  # No frontmatter, skip

        # Use combo schema for combos/ entries
        is_combo = "combos" in md_file.relative_to(catalog_dir).parts
        active_schema = combo_schema if (is_combo and combo_schema) else schema

        try:
            validate(instance=fm, schema=active_schema)
            print(f"  ✅ {md_file.relative_to(REPO_ROOT)}")
        except ValidationError as e:
            errors.append(f"  ❌ {md_file.relative_to(REPO_ROOT)}: {e.message}")


def validate_evidence_files():
    """Minimaler struktureller Check für evidence.jsonl Dateien.

    Prüft:
    - Jede Zeile ist gültiges JSON
    - Pflichtfelder (event_type, timestamp, iteration, metric, value, context) vorhanden
    - event_type ist in der erlaubten Taxonomie (observation, measurement, decision)
    """
    experiments_dir = REPO_ROOT / "experiments"
    found = 0
    for evidence_file in experiments_dir.glob("*/results/evidence.jsonl"):
        if evidence_file.parent.parent.name.startswith("_"):
            continue  # Skip _template, _archive
        found += 1
        lines = evidence_file.read_text(encoding="utf-8").strip().splitlines()
        for lineno, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError as e:
                errors.append(
                    f"  ❌ {evidence_file.relative_to(REPO_ROOT)}:{lineno}: invalid JSON — {e}"
                )
                continue

            missing = EVIDENCE_REQUIRED_KEYS - entry.keys()
            if missing:
                errors.append(
                    f"  ❌ {evidence_file.relative_to(REPO_ROOT)}:{lineno}: "
                    f"missing required keys: {sorted(missing)}"
                )
                continue

            event_type = entry.get("event_type")
            if event_type not in EVIDENCE_EVENT_TYPES:
                errors.append(
                    f"  ❌ {evidence_file.relative_to(REPO_ROOT)}:{lineno}: "
                    f"event_type '{event_type}' not in allowlist {sorted(EVIDENCE_EVENT_TYPES)}"
                )
                continue

            print(f"  ✅ {evidence_file.relative_to(REPO_ROOT)}:{lineno} ({event_type})")

    if found == 0:
        print("  (no evidence.jsonl files found outside _template/_archive)")


def main():
    print("🔍 Schema Validation")
    print()
    print("Experiment Manifests:")
    validate_experiment_manifests()
    print()
    print("Catalog Entries:")
    validate_catalog_entries()
    print()
    print("Evidence Files:")
    validate_evidence_files()
    print()

    if errors:
        print("❌ Validation FAILED:")
        for err in errors:
            print(err)
        sys.exit(1)
    else:
        print("✅ All schema validations passed.")


if __name__ == "__main__":
    main()
