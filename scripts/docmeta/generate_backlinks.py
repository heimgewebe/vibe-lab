#!/usr/bin/env python3
"""generate_backlinks.py — Generiert docs/_generated/backlinks.md.

Scannt alle Markdown-Dateien und erzeugt eine Rückverlinkungsmatrix:
Welche Dateien verweisen auf welche anderen Dateien (über Frontmatter-Relationen)?

Ausgabe: docs/_generated/backlinks.md
"""

import datetime
from collections import defaultdict
from pathlib import Path

try:
    import yaml
except ImportError:
    import sys
    print("ERROR: Missing dependency. Run: pip install pyyaml")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT = REPO_ROOT / "docs" / "_generated" / "backlinks.md"

SKIP_DIRS = {".git", ".github", "node_modules", "__pycache__", "_archive"}


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
    # backlinks[target] = [(source, relation_type)]
    backlinks: dict[str, list[tuple[str, str]]] = defaultdict(list)

    for md_file in sorted(REPO_ROOT.rglob("*.md")):
        if should_skip(md_file):
            continue
        if "_generated" in md_file.relative_to(REPO_ROOT).parts:
            continue

        fm = extract_frontmatter(md_file)
        if fm is None or "relations" not in fm:
            continue

        source = str(md_file.relative_to(REPO_ROOT))
        for rel in fm.get("relations", []):
            if not isinstance(rel, dict):
                continue
            target = rel.get("target", "")
            rel_type = rel.get("type", "unknown")
            if target.startswith("#"):
                continue
            # Resolve to repo-relative path
            resolved = (md_file.parent / target).resolve()
            try:
                rel_target = str(resolved.relative_to(REPO_ROOT))
            except ValueError:
                rel_target = target
            backlinks[rel_target].append((source, rel_type))

    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        "<!-- GENERATED FILE — DO NOT EDIT MANUALLY -->",
        f"<!-- Generated: {now} by generate_backlinks.py -->",
        "",
        "# Backlinks",
        "",
    ]

    if backlinks:
        for target in sorted(backlinks.keys()):
            lines.append(f"## `{target}`")
            lines.append("")
            for source, rel_type in sorted(backlinks[target]):
                lines.append(f"- ← `{source}` ({rel_type})")
            lines.append("")
    else:
        lines.append("*No backlinks found.*")
        lines.append("")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ Generated {OUTPUT.relative_to(REPO_ROOT)} ({len(backlinks)} targets)")


if __name__ == "__main__":
    main()
