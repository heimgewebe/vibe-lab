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
TOMBSTONE_FORMAT_VERSION = "1"
RETIREMENT_DATE = "2026-07-12"
RETIREMENT_DECISION = "decisions/export/README.md"
TOMBSTONE_BODY = (
    "# Tool projection retired\n\n"
    "This file is a compatibility marker only. Vibe-Lab no longer projects "
    "instruction blocks into tool-specific directories.\n\n"
    "Reactivation is handled through the normal experiment registration and "
    "review path; this marker has no operational authority.\n"
)


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
    status = read_source_status(source_file)
    if status != EXPORTABLE_STATUS:
        raise ValueError(
            f"cannot build retirement marker for {source_file}: "
            f"status must be {EXPORTABLE_STATUS!r}, got {status!r}"
        )

    try:
        rel_source = source_file.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        rel_source = f"instruction-blocks/{source_file.name}"
    return (
        "<!-- GENERATED FILE — DO NOT EDIT MANUALLY -->\n"
        f"<!-- source: {rel_source} -->\n"
        f"<!-- target-system: {target_system} -->\n"
        f"<!-- generator: {GENERATOR_ID} -->\n"
        f"<!-- retirement-format: {TOMBSTONE_FORMAT_VERSION} -->\n"
        f"<!-- retired-on: {RETIREMENT_DATE} -->\n"
        f"<!-- decision: {RETIREMENT_DECISION} -->\n\n"
        f"{TOMBSTONE_BODY}"
    )
