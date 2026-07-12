"""Compatibility contract for retired tool-specific instruction exports.

The Cursor and Copilot surfaces are kept only as generated tombstones so old
links remain deterministic. They intentionally contain no executable guidance.
Reactivation requires a named consumer, a decision target, measurement and an
expiry/review date through the normal Vibe-Lab experiment gate.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SOURCE_DIR = REPO_ROOT / "instruction-blocks"
EXPORT_TARGETS: dict[str, Path] = {
    "copilot": REPO_ROOT / "exports" / "copilot",
    "cursor": REPO_ROOT / "exports" / "cursor",
}
EXPORTABLE_STATUS = "adopted"
GENERATOR_ID = "scripts/exports/generate_exports.py"


def expected_export_name(src: Path) -> str:
    return src.name


def read_source_status(src: Path) -> str | None:
    text = src.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    for raw_line in parts[1].splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        if key.strip() == "status":
            return value.strip().strip('"').strip("'")
    return None


def is_exportable_source(src: Path) -> bool:
    return read_source_status(src) == EXPORTABLE_STATUS


def exportable_source_files(source_dir: Path = SOURCE_DIR) -> list[Path]:
    return [src for src in sorted(source_dir.glob("*.md")) if is_exportable_source(src)]


def build_tombstone(source_file: Path, target_system: str) -> str:
    try:
        rel_source = source_file.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        rel_source = f"instruction-blocks/{source_file.name}"
    return (
        "<!-- GENERATED FILE — DO NOT EDIT MANUALLY -->\n"
        f"<!-- source: {rel_source} -->\n"
        f"<!-- target-system: {target_system} -->\n"
        f"<!-- generator: {GENERATOR_ID} -->\n\n"
        "# Tool projection retired\n\n"
        "This compatibility file intentionally contains no instruction text. "
        "Vibe-Lab no longer publishes default Cursor or Copilot projections.\n\n"
        "Reactivation requires a named downstream consumer, a reviewed decision "
        "target, measurable success and falsification criteria, and an expiry date.\n"
    )
