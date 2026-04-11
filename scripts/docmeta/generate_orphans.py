#!/usr/bin/env python3
import json
from pathlib import Path
import re

REPO_ROOT = Path(__file__).parent.parent.parent
DOC_INDEX_PATH = REPO_ROOT / "docs" / "_generated" / "doc-index.md"
ORPHANS_OUT_PATH = REPO_ROOT / "docs" / "_generated" / "orphans.md"

# Directories/files to exclude from scan
EXCLUDES = [
    "venv", ".venv", "node_modules", ".git", ".github",
    "_template", "README.md", "CONTRIBUTING.md", "pull_request_template.md"
]

# Legitimate root nodes or entry points that shouldn't be flagged as orphans
LEGITIMATE_ORPHANS = {
    "docs/index.md",
    "docs/masterplan.md",
    "docs/policies/privacy-and-ethics.md",
    "benchmarks/challenges/rest-api-v1.md",
    "benchmarks/challenges/kanban-board-v1.md",
    "benchmarks/challenges/legacy-refactoring-v1.md",
}


def should_skip(path: Path, root: Path, skip_generated: bool = False) -> bool:
    rel = str(path.relative_to(root))
    if any(excl in rel for excl in EXCLUDES):
        return True
    if skip_generated and "docs/_generated" in rel:
        return True
    return False

def extract_links(markdown_content: str) -> set[str]:
    # Extract markdown links [text](url)
    links = set()
    pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    for match in pattern.finditer(markdown_content):
        url = match.group(2)
        # simplistic clean up (remove hash fragments)
        if "#" in url:
            url = url.split("#")[0]
        if url.endswith(".md"):
            links.add(url)
    return links

def main():
    all_docs: set[str] = set()
    referenced: set[str] = set()

    for md_file in sorted(REPO_ROOT.rglob("*.md")):
        if should_skip(md_file, REPO_ROOT, skip_generated=True):
            continue
        rel_path = str(md_file.relative_to(REPO_ROOT))
        all_docs.add(rel_path)

        try:
            content = md_file.read_text(encoding="utf-8")
            links = extract_links(content)
            for link in links:
                # Resolve relative link
                try:
                    target = (md_file.parent / link).resolve().relative_to(REPO_ROOT.resolve())
                    referenced.add(str(target))
                except ValueError:
                    pass # External or invalid link
        except Exception as e:
            print(f"Error parsing {rel_path}: {e}")

    orphans = all_docs - referenced - LEGITIMATE_ORPHANS

    # Group by directory for better output
    grouped = {}
    for orphan in orphans:
        parts = orphan.split("/")
        if len(parts) > 1:
            group = parts[0]
        else:
            group = "root"
        if group not in grouped:
            grouped[group] = []
        grouped[group].append(orphan)

    with open(ORPHANS_OUT_PATH, "w", encoding="utf-8") as f:
        f.write("# 🏝️ Unreferenzierte Dokumente (Orphans)\n\n")
        f.write("> **Diagnose:** Diese Dokumente werden von keinem anderen Markdown-Dokument im Repository verlinkt.\n")
        f.write("> Sie sind entweder veraltet, isolierte Entwürfe oder es fehlen Backlinks in der Navigation.\n")
        f.write("> System-Root-Dokumente (`docs/index.md` etc.) sind hiervon ausgenommen.\n\n")

        if not orphans:
            f.write("🎉 **Keine Orphan-Dokumente gefunden!** Die Informationsarchitektur ist lückenlos.\n")
        else:
            for group, items in sorted(grouped.items()):
                f.write(f"## {group}\n\n")
                for item in sorted(items):
                    f.write(f"- [`{item}`](../../{item})\n")
                f.write("\n")

    print(f"✅ Generated {ORPHANS_OUT_PATH.relative_to(REPO_ROOT)} ({len(orphans)} unreferenced)")


if __name__ == "__main__":
    main()
