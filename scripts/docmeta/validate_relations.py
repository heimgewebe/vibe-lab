#!/usr/bin/env python3
"""validate_relations.py — Prüft Frontmatter-Relationen auf Konsistenz.

Scannt alle Markdown-Dateien mit Frontmatter-Relationen und prüft,
ob die Ziel-Pfade (target) tatsächlich existieren.

Benötigt: pip install pyyaml
"""

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: Missing dependency. Run: pip install pyyaml")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

errors = []
warnings = []


def extract_frontmatter(path: Path) -> dict | None:
    """Extract YAML frontmatter from a Markdown file."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    try:
        return yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return None


def resolve_target(source_file: Path, target: str) -> Path:
    """Resolve a relation target relative to the source file's directory."""
    if target.startswith("#"):
        return source_file  # Issue reference, skip
    return (source_file.parent / target).resolve()


def validate_file_relations(md_file: Path):
    fm = extract_frontmatter(md_file)
    if fm is None or "relations" not in fm:
        return

    relations = fm.get("relations", [])
    if not isinstance(relations, list):
        errors.append(f"  ❌ {md_file.relative_to(REPO_ROOT)}: 'relations' must be a list")
        return

    for rel in relations:
        if not isinstance(rel, dict):
            errors.append(f"  ❌ {md_file.relative_to(REPO_ROOT)}: relation entry must be an object")
            continue

        rel_type = rel.get("type")
        target = rel.get("target")

        if not rel_type or not target:
            errors.append(f"  ❌ {md_file.relative_to(REPO_ROOT)}: relation missing 'type' or 'target'")
            continue

        # Skip issue references
        if target.startswith("#"):
            continue

        resolved = resolve_target(md_file, target)
        if not resolved.exists():
            errors.append(
                f"  ❌ {md_file.relative_to(REPO_ROOT)}: "
                f"relation '{rel_type}' target '{target}' does not exist"
            )
        else:
            print(f"  ✅ {md_file.relative_to(REPO_ROOT)} → {rel_type} → {target}")


def main():
    print("🔗 Relations Validation")
    print()

    # Scan all markdown files
    scanned = 0
    for md_file in sorted(REPO_ROOT.rglob("*.md")):
        # Skip hidden dirs, _generated, node_modules, etc.
        rel = md_file.relative_to(REPO_ROOT)
        parts = rel.parts
        if any(p.startswith(".") for p in parts):
            continue
        if "_generated" in parts:
            continue
        if any(p in ("node_modules", "__pycache__") for p in parts):
            continue

        validate_file_relations(md_file)
        scanned += 1

    print()
    print(f"Scanned {scanned} markdown files.")

    if errors:
        print()
        print("❌ Relations validation FAILED:")
        for err in errors:
            print(err)
        sys.exit(1)
    else:
        print("✅ All relations valid.")


if __name__ == "__main__":
    main()
