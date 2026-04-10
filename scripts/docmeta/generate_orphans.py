#!/usr/bin/env python3
"""generate_orphans.py — Generiert docs/_generated/orphans.md.

Identifiziert Markdown-Dateien, die von keiner anderen Datei
über Frontmatter-Relationen referenziert werden.

Ausgabe: docs/_generated/orphans.md
"""

import datetime
from pathlib import Path

try:
    import yaml
except ImportError:
    import sys
    print("ERROR: Missing dependency. Run: pip install pyyaml")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT = REPO_ROOT / "docs" / "_generated" / "orphans.md"

SKIP_DIRS = {".git", ".github", "node_modules", "__pycache__", "_archive"}

# Files that are naturally roots (not expected to be referenced by others)
ROOT_FILES = {
    "README.md",
    "CONTRIBUTING.md",
    "AGENTS.md",
    "vision.md",
    "repo-plan.md",
    "docs/index.md",
}


def extract_frontmatter(path: Path) -> dict | None:
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


def should_skip(path: Path) -> bool:
    return any(p in SKIP_DIRS or p.startswith(".") for p in path.relative_to(REPO_ROOT).parts)


def main():
    all_docs: set[str] = set()
    referenced: set[str] = set()

    for md_file in sorted(REPO_ROOT.rglob("*.md")):
        if should_skip(md_file):
            continue
        if "_generated" in md_file.relative_to(REPO_ROOT).parts:
            continue
        if "_template" in md_file.relative_to(REPO_ROOT).parts:
            continue

        rel_path = str(md_file.relative_to(REPO_ROOT))
        all_docs.add(rel_path)

        fm = extract_frontmatter(md_file)
        if fm is None or "relations" not in fm:
            continue

        for rel in fm.get("relations", []):
            if not isinstance(rel, dict):
                continue
            target = rel.get("target", "")
            if target.startswith("#"):
                continue
            resolved = (md_file.parent / target).resolve()
            try:
                ref_path = str(resolved.relative_to(REPO_ROOT))
                referenced.add(ref_path)
            except ValueError:
                pass

    orphans = sorted(all_docs - referenced - ROOT_FILES)

    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        "<!-- GENERATED FILE — DO NOT EDIT MANUALLY -->",
        f"<!-- Generated: {now} by generate_orphans.py -->",
        "",
        "# Orphaned Documents",
        "",
        f"Documents not referenced by any other document via frontmatter relations ({len(orphans)} found):",
        "",
    ]

    if orphans:
        for orphan in orphans:
            lines.append(f"- `{orphan}`")
    else:
        lines.append("*No orphans found.*")

    lines.append("")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ Generated {OUTPUT.relative_to(REPO_ROOT)} ({len(orphans)} orphans)")


if __name__ == "__main__":
    main()
