#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse

DEFAULT_MARKERS = [
    "docs/doc-freshness-registry.yml",
    "docs/policies/agent-reading-protocol.md",
    "scripts/docmeta/validate_doc_freshness_registry.py",
    "scripts/docmeta/test_validate_doc_freshness_registry.py",
]


def _has_file_section(text: str, marker: str) -> bool:
    """Return true only when the canonical bundle contains marker as a file section.

    The receipt is meant to prove that required source files are present in the
    bundle. Plain substring checks are too weak because one bundled file can
    mention another required path without including that file's content.
    repoLens v2 emits a FILE_START boundary for each included file.
    """

    return f'<!-- FILE_START path="{marker}"' in text


def validate(canonical_md: Path, markers: list[str]) -> list[str]:
    if not canonical_md.is_file():
        return [f"missing canonical markdown: {canonical_md}"]
    text = canonical_md.read_text(encoding="utf-8", errors="replace")
    return [
        f"missing source file section: {marker}"
        for marker in markers
        if not _has_file_section(text, marker)
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--canonical-md", required=True, type=Path)
    parser.add_argument("--require", action="append", dest="markers")
    args = parser.parse_args()
    errors = validate(args.canonical_md, args.markers or DEFAULT_MARKERS)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("bundle freshness receipt passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
