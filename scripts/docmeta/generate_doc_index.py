#!/usr/bin/env python3
"""generate_doc_index.py — Generiert docs/_generated/doc-index.md.

Scannt alle Markdown-Dateien im Repository und erzeugt einen
maschinenlesbaren Dokumenten-Index mit Titel und Status.

Ausgabe: docs/_generated/doc-index.md
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
OUTPUT = REPO_ROOT / "docs" / "_generated" / "doc-index.md"

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
    entries = []

    for md_file in sorted(REPO_ROOT.rglob("*.md")):
        if should_skip(md_file):
            continue
        if "_generated" in md_file.relative_to(REPO_ROOT).parts:
            continue

        rel_path = md_file.relative_to(REPO_ROOT)
        fm = extract_frontmatter(md_file)
        title = fm.get("title", rel_path.stem) if fm else rel_path.stem
        status = fm.get("status", "—") if fm else "—"
        canonicality = fm.get("canonicality", "—") if fm else "—"

        entries.append((str(rel_path), title, status, canonicality))

    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        "<!-- GENERATED FILE — DO NOT EDIT MANUALLY -->",
        f"<!-- Generated: {now} by generate_doc_index.py -->",
        "",
        "# Document Index",
        "",
        "| Path | Title | Status | Canonicality |",
        "| ---- | ----- | ------ | ------------ |",
    ]

    for path, title, status, canonicality in entries:
        lines.append(f"| `{path}` | {title} | {status} | {canonicality} |")

    lines.append("")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ Generated {OUTPUT.relative_to(REPO_ROOT)} ({len(entries)} documents)")


if __name__ == "__main__":
    main()
