#!/usr/bin/env python3
"""generate_system_map.py — Generiert docs/_generated/system-map.md.

Erzeugt eine Systemübersicht: Welche Ordner existieren, wie viele
Dokumente sie enthalten, und welcher Zone sie zugehören.

Ausgabe: docs/_generated/system-map.md
"""

import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT = REPO_ROOT / "docs" / "_generated" / "system-map.md"

ZONE_MAP = {
    "experiments": "🔬 Labor",
    "catalog": "📚 Bibliothek",
    "prompts": "📚 Bibliothek",
    "benchmarks": "📚 Bibliothek",
    "instruction-blocks": "📚 Bibliothek",
    "exports": "⚙️ Generiert",
    "docs/_generated": "⚙️ Generiert",
    ".cursor": "⚙️ Generiert",
    "contracts": "🏛️ Governance",
    "schemas": "🏛️ Governance",
    "decisions": "🏛️ Governance",
    ".vibe": "🏛️ Governance",
    "docs": "📖 Dokumentation",
    "scripts": "🔧 Tooling",
    "tools": "🔧 Tooling",
}

SKIP_DIRS = {".git", ".github", "node_modules", "__pycache__"}


def get_zone(rel_path: str) -> str:
    for prefix, zone in ZONE_MAP.items():
        if rel_path.startswith(prefix):
            return zone
    return "📁 Root"


def main():
    dir_stats: dict[str, dict] = {}

    for item in sorted(REPO_ROOT.rglob("*")):
        if any(p in SKIP_DIRS or (p.startswith(".") and p != ".vibe") for p in item.relative_to(REPO_ROOT).parts):
            continue
        if item.is_file():
            rel = str(item.relative_to(REPO_ROOT))
            top_dir = rel.split("/")[0] if "/" in rel else "."
            if top_dir not in dir_stats:
                dir_stats[top_dir] = {"files": 0, "md_files": 0, "zone": get_zone(top_dir)}
            dir_stats[top_dir]["files"] += 1
            if item.suffix == ".md":
                dir_stats[top_dir]["md_files"] += 1

    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        "<!-- GENERATED FILE — DO NOT EDIT MANUALLY -->",
        f"<!-- Generated: {now} by generate_system_map.py -->",
        "",
        "# System Map",
        "",
        "| Directory | Zone | Files | Markdown |",
        "| --------- | ---- | ----: | -------: |",
    ]

    for dir_name in sorted(dir_stats.keys()):
        stats = dir_stats[dir_name]
        lines.append(f"| `{dir_name}/` | {stats['zone']} | {stats['files']} | {stats['md_files']} |")

    lines.append("")
    lines.append(f"**Total:** {sum(s['files'] for s in dir_stats.values())} files in {len(dir_stats)} directories")
    lines.append("")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ Generated {OUTPUT.relative_to(REPO_ROOT)} ({len(dir_stats)} directories)")


if __name__ == "__main__":
    main()
