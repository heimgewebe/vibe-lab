#!/usr/bin/env python3
"""validate_relations.py — Prüft Frontmatter-Relationen auf Konsistenz.

Scannt alle Markdown-Dateien mit Frontmatter-Relationen und prüft,
ob die Ziel-Pfade (target) tatsächlich existieren.

Benötigt: pip install pyyaml
"""

import sys
from pathlib import Path

# Gemeinsame Pfad-Logik aus _paths.py
sys.path.insert(0, str(Path(__file__).parent))
from _paths import should_skip, extract_frontmatter  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def resolve_target(source_file: Path, target: str, repo_root: Path = REPO_ROOT) -> Path | None:
    """Resolve a relation target relative to the source file's directory.

    Returns None if the target resolves outside ``repo_root`` (path-escape guard).
    """
    if target.startswith("#"):
        return source_file  # Issue reference, skip
    resolved = (source_file.parent / target).resolve()
    try:
        resolved.relative_to(repo_root)
    except ValueError:
        return None  # target escapes repository root
    return resolved


def validate_file_relations(
    md_file: Path,
    errors: list[str],
    repo_root: Path = REPO_ROOT,
    *,
    quiet: bool = False,
) -> None:
    """Validiert die Relationen einer einzelnen Markdown-Datei.

    Schreibt Fehler in die übergebene ``errors``-Liste statt in einen globalen
    Modul-State. Das gibt sauberer Test-Isolation und macht die Funktion
    direkt aufrufbar.
    """
    fm = extract_frontmatter(md_file)
    if fm is None or "relations" not in fm:
        return

    rel_path = md_file.relative_to(repo_root)

    relations = fm.get("relations", [])
    if not isinstance(relations, list):
        errors.append(f"  ❌ {rel_path}: 'relations' must be a list")
        return

    for rel in relations:
        if not isinstance(rel, dict):
            errors.append(f"  ❌ {rel_path}: relation entry must be an object")
            continue

        rel_type = rel.get("type")
        target = rel.get("target")

        if not rel_type or not target:
            errors.append(f"  ❌ {rel_path}: relation missing 'type' or 'target'")
            continue

        # Skip issue references
        if target.startswith("#"):
            continue

        resolved = resolve_target(md_file, target, repo_root=repo_root)
        if resolved is None:
            errors.append(
                f"  ❌ {rel_path}: "
                f"relation '{rel_type}' target '{target}' escapes repository root"
            )
        elif not resolved.exists():
            errors.append(
                f"  ❌ {rel_path}: "
                f"relation '{rel_type}' target '{target}' does not exist"
            )
        elif not quiet:
            print(f"  ✅ {rel_path} → {rel_type} → {target}")


def collect_errors(repo_root: Path = REPO_ROOT, *, quiet: bool = False) -> list[str]:
    """Scannt alle Markdown-Dateien und gibt eine Fehlerliste zurück."""
    errors: list[str] = []
    for md_file in sorted(repo_root.rglob("*.md")):
        if should_skip(md_file, repo_root, skip_generated=True):
            continue
        validate_file_relations(md_file, errors, repo_root=repo_root, quiet=quiet)
    return errors


def main() -> int:
    print("🔗 Relations Validation")
    print()

    scanned = 0
    errors: list[str] = []
    for md_file in sorted(REPO_ROOT.rglob("*.md")):
        if should_skip(md_file, REPO_ROOT, skip_generated=True):
            continue
        validate_file_relations(md_file, errors, repo_root=REPO_ROOT)
        scanned += 1

    print()
    print(f"Scanned {scanned} markdown files.")

    if errors:
        print()
        print("❌ Relations validation FAILED:")
        for err in errors:
            print(err)
        return 1
    print("✅ All relations valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
