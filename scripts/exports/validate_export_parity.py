#!/usr/bin/env python3
"""Validate that legacy Cursor/Copilot surfaces contain tombstones only."""

from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
from export_contract import (  # noqa: E402
    EXPORT_TARGETS,
    SOURCE_DIR,
    build_tombstone,
    exportable_source_files,
)


def validate(
    source_dir: Path = SOURCE_DIR,
    export_targets: dict[str, Path] | None = None,
) -> list[str]:
    if export_targets is None:
        export_targets = EXPORT_TARGETS
    if not source_dir.is_dir():
        return [f"missing instruction source directory: {source_dir}"]

    sources = exportable_source_files(source_dir)
    expected = {src.name: src for src in sources}
    errors: list[str] = []

    for target_system, target_dir in sorted(export_targets.items()):
        actual = (
            {
                path.relative_to(target_dir).as_posix(): path
                for path in target_dir.rglob("*")
                if path.is_file()
            }
            if target_dir.exists()
            else {}
        )
        missing = sorted(set(expected) - set(actual))
        orphaned = sorted(set(actual) - set(expected))
        errors.extend(f"missing retirement marker: exports/{target_system}/{name}" for name in missing)
        errors.extend(f"unexpected file in retired surface: exports/{target_system}/{name}" for name in orphaned)
        for name in sorted(set(expected) & set(actual)):
            wanted = build_tombstone(expected[name], target_system)
            if actual[name].read_text(encoding="utf-8") != wanted:
                errors.append(f"active or drifted instruction export: exports/{target_system}/{name}")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("retired export boundary violated:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("retired export boundary OK: no tool-specific instruction content published")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
