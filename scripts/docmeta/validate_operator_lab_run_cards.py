#!/usr/bin/env python3
"""Validate Operator-Lab raw-note to structured run-card linkage.

This guard is intentionally narrow. It does not try to validate every historic
Operator-Lab artifact shape. It only prevents the failure mode observed after
introducing the Operator-Lab loop: a raw-vibes operator-lab note being used as
final PR evidence without a structured run-card follow-up.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "experiments/2026-07-01_operator-lab-loop/artifacts"
RAW_VIBES = ROOT / "raw-vibes"
RAW_PATTERN = "operator-lab-run-*.md"


def _repo_rel(path: Path, *, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _source_note_paths(card: dict[str, Any]) -> set[str]:
    paths: set[str] = set()
    source_note = card.get("source_note")
    if isinstance(source_note, dict) and isinstance(source_note.get("path"), str):
        paths.add(source_note["path"])
    source_notes = card.get("source_notes")
    if isinstance(source_notes, list):
        for item in source_notes:
            if isinstance(item, dict) and isinstance(item.get("path"), str):
                paths.add(item["path"])
    return paths


def validate_operator_lab_run_cards(repo_root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    raw_dir = repo_root / "raw-vibes"
    artifacts_dir = repo_root / "experiments/2026-07-01_operator-lab-loop/artifacts"

    raw_notes = sorted(raw_dir.glob(RAW_PATTERN)) if raw_dir.exists() else []
    run_cards = sorted(artifacts_dir.glob("run-*/run-card.yml")) if artifacts_dir.exists() else []

    source_index: dict[str, list[Path]] = {}
    for run_card in run_cards:
        card = _load_yaml(run_card)
        for raw_path in _source_note_paths(card):
            source_index.setdefault(raw_path, []).append(run_card)
            if raw_path.startswith("raw-vibes/") and not (repo_root / raw_path).is_file():
                errors.append(f"{_repo_rel(run_card, root=repo_root)} references missing source_note.path: {raw_path}")

    for raw_note in raw_notes:
        rel = _repo_rel(raw_note, root=repo_root)
        cards = source_index.get(rel, [])
        if not cards:
            errors.append(
                f"{rel} has no structured Operator-Lab run-card source_note.path reference"
            )
            continue
        for card_path in cards:
            run_meta = card_path.parent / "run_meta.json"
            if not run_meta.is_file():
                errors.append(
                    f"{_repo_rel(card_path, root=repo_root)} references {rel} but sibling run_meta.json is missing"
                )

    return errors


def main() -> int:
    errors = validate_operator_lab_run_cards()
    print("🧾 Validating Operator-Lab run-card structure...")
    if errors:
        print("❌ Operator-Lab run-card validation FAILED:")
        for error in errors:
            print(f"  ❌ {error}")
        return 1
    print("✅ Operator-Lab raw notes have structured run-card follow-up.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
