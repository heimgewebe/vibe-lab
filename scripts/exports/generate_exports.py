#!/usr/bin/env python3
"""generate_exports.py — Exportiert instruction-blocks/ nach exports/copilot/ und exports/cursor/.

Jeder Export enthält einen maschinenlesbaren Header, der Herkunft, Generator
und Zeitstempel dokumentiert. Die Erzeugung ist deterministisch: gleiche
Eingabe → gleiche Ausgabe (Zeitstempel wird auf Tagesebene fixiert).

Quelle:  instruction-blocks/*.md
Ziele:   exports/copilot/*.md, exports/cursor/*.md
Vertrag: .vibe/generated-artifacts.yml → exports
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

# Repo-Root relativ zu diesem Skript: scripts/exports/ → ../../
REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Gemeinsame Hilfsfunktionen aus docmeta
sys.path.insert(0, str(REPO_ROOT / "scripts" / "docmeta"))
from _paths import write_if_changed, extract_frontmatter  # noqa: E402

SOURCE_DIR = REPO_ROOT / "instruction-blocks"
EXPORT_TARGETS: dict[str, Path] = {
    "copilot": REPO_ROOT / "exports" / "copilot",
    "cursor": REPO_ROOT / "exports" / "cursor",
}

GENERATOR_ID = "scripts/exports/generate_exports.py"


def _strip_frontmatter(text: str) -> str:
    """Entfernt YAML-Frontmatter (---...---) vom Markdown-Text."""
    if not text.startswith("---"):
        return text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return text
    return parts[2].lstrip("\n")


def _build_header(source_path: str, target_system: str, generated_date: str) -> str:
    """Erzeugt einen einheitlichen Export-Header."""
    return (
        f"<!-- GENERATED FILE — DO NOT EDIT MANUALLY -->\n"
        f"<!-- source: {source_path} -->\n"
        f"<!-- target-system: {target_system} -->\n"
        f"<!-- generator: {GENERATOR_ID} -->\n"
        f"<!-- generated: {generated_date} -->\n"
    )


def _build_export(
    source_file: Path,
    target_system: str,
    generated_date: str,
) -> str:
    """Baut den vollständigen Export-Inhalt für eine Quelldatei."""
    text = source_file.read_text(encoding="utf-8")
    fm = extract_frontmatter(source_file)
    body = _strip_frontmatter(text)
    title = fm.get("title", source_file.stem) if fm else source_file.stem
    rel_source = source_file.relative_to(REPO_ROOT)

    header = _build_header(str(rel_source), target_system, generated_date)
    return f"{header}\n# {title}\n{body}"


def generate_exports(generated_date: str | None = None) -> dict[str, int]:
    """Hauptlogik: liest instruction-blocks/, schreibt nach exports/.

    Returns:
        dict mit target_system → Anzahl exportierter Dateien.
    """
    if generated_date is None:
        generated_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    source_files = sorted(SOURCE_DIR.glob("*.md"))

    stats: dict[str, int] = {}

    for target_system, target_dir in sorted(EXPORT_TARGETS.items()):
        target_dir.mkdir(parents=True, exist_ok=True)

        # Entferne .gitkeep falls vorhanden — Exporte ersetzen den Platzhalter.
        # Dieser Seiteneffekt ist durch den Export-Contract in
        # .vibe/generated-artifacts.yml gedeckt (triggered_by: generate-exports).
        gitkeep = target_dir / ".gitkeep"
        if gitkeep.exists():
            gitkeep.unlink()

        exported_names: set[str] = set()

        for src in source_files:
            content = _build_export(src, target_system, generated_date)
            out_file = target_dir / src.name
            write_if_changed(out_file, content)
            exported_names.add(src.name)

        # Entferne veraltete Exporte, die keine Quelle mehr haben
        for existing in target_dir.iterdir():
            if existing.name not in exported_names:
                existing.unlink()

        stats[target_system] = len(source_files)

    return stats


def main() -> int:
    if not SOURCE_DIR.exists():
        print(f"ERROR: Source directory not found: {SOURCE_DIR}", file=sys.stderr)
        return 1

    source_files = sorted(SOURCE_DIR.glob("*.md"))
    if not source_files:
        print(f"WARNING: No *.md files found in {SOURCE_DIR}", file=sys.stderr)
        return 0

    stats = generate_exports()

    for target, count in sorted(stats.items()):
        print(f"✅ Exported {count} instruction-blocks to exports/{target}/")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
