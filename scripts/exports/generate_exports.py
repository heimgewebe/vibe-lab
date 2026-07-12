#!/usr/bin/env python3
"""Generate deterministic retirement tombstones for legacy tool projections."""

from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
from export_contract import (  # noqa: E402
    EXPORT_TARGETS,
    SOURCE_DIR,
    build_tombstone,
    expected_export_name,
    exportable_source_files,
)


def generate_exports(
    source_dir: Path = SOURCE_DIR,
    export_targets: dict[str, Path] | None = None,
) -> dict[str, int]:
    """Write only bounded retirement markers; never copy instruction content."""
    if export_targets is None:
        export_targets = EXPORT_TARGETS
    sources = exportable_source_files(source_dir)
    expected = {expected_export_name(src): src for src in sources}
    stats: dict[str, int] = {}

    for target_system, target_dir in sorted(export_targets.items()):
        target_dir.mkdir(parents=True, exist_ok=True)
        for stale in target_dir.rglob("*.md"):
            relative_name = stale.relative_to(target_dir).as_posix()
            if relative_name not in expected:
                stale.unlink()
        for name, src in expected.items():
            content = build_tombstone(src, target_system)
            out = target_dir / name
            if not out.exists() or out.read_text(encoding="utf-8") != content:
                out.write_text(content, encoding="utf-8")
        stats[target_system] = len(expected)
    return stats


def main() -> int:
    if not SOURCE_DIR.exists():
        print(f"ERROR: Source directory not found: {SOURCE_DIR}", file=sys.stderr)
        return 1
    stats = generate_exports()
    for target, count in sorted(stats.items()):
        print(f"retired projection markers: {target}={count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
