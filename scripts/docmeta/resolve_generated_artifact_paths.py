#!/usr/bin/env python3
"""resolve_generated_artifact_paths.py — Liest Pfade aus .vibe/generated-artifacts.yml.

Nutzung:
  python3 scripts/docmeta/resolve_generated_artifact_paths.py canonical
  python3 scripts/docmeta/resolve_generated_artifact_paths.py derived
  python3 scripts/docmeta/resolve_generated_artifact_paths.py gated
  python3 scripts/docmeta/resolve_generated_artifact_paths.py ephemeral
  python3 scripts/docmeta/resolve_generated_artifact_paths.py exports

Ausgabe: Ein Pfad pro Zeile.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print(
        "ERROR: PyYAML is required. Install with: python3 -m pip install PyYAML",
        file=sys.stderr,
    )
    raise SystemExit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONTRACT_FILE = REPO_ROOT / ".vibe" / "generated-artifacts.yml"


def load_paths(group: str) -> list[str]:
    if not CONTRACT_FILE.exists():
        raise FileNotFoundError(f"Missing contract file: {CONTRACT_FILE}")

    data = yaml.safe_load(CONTRACT_FILE.read_text(encoding="utf-8")) or {}
    contract = data.get("generated_artifact_contract") or {}
    bucket = contract.get(group) or {}
    files = bucket.get("files") or []

    if not isinstance(files, list) or any(not isinstance(p, str) for p in files):
        raise ValueError(f"Invalid files list for group '{group}' in {CONTRACT_FILE}")

    return files


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("group", choices=["canonical", "derived", "gated", "ephemeral", "exports"])
    args = parser.parse_args()

    try:
        files = load_paths(args.group)
    except (FileNotFoundError, ValueError, yaml.YAMLError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    for path in files:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
