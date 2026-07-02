#!/usr/bin/env python3
"""Validate Operator-Lab raw-note to structured run-card linkage.

This guard is intentionally narrow. It does not try to validate every historic
Operator-Lab artifact shape. It only prevents the failure mode observed after
introducing the Operator-Lab loop: a raw-vibes operator-lab note being used as
final PR evidence without a structured run-card follow-up.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "experiments/2026-07-01_operator-lab-loop/artifacts"
RAW_VIBES = ROOT / "raw-vibes"
RAW_PATTERN = "operator-lab-run-*.md"
RECENT_RUN_SLOT_MIN = 15
RUN_SLOT_RE = re.compile(r"^run-(\d{3})-")


def _repo_rel(path: Path, *, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}



def _run_slot(path):
    match = RUN_SLOT_RE.match(path.parent.name)
    if match is None:
        return None
    return int(match.group(1))


def _manifest_execution_refs(repo_root):
    manifest = repo_root / "experiments/2026-07-01_operator-lab-loop/manifest.yml"
    data = _load_yaml(manifest) if manifest.is_file() else {}
    experiment = data.get("experiment")
    refs = experiment.get("execution_refs") if isinstance(experiment, dict) else None
    return {item for item in refs if isinstance(item, str)} if isinstance(refs, list) else set()

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


    manifest_refs = _manifest_execution_refs(repo_root)
    recent_by_slot = {}
    experiment_dir = repo_root / "experiments/2026-07-01_operator-lab-loop"
    for run_card in run_cards:
        slot = _run_slot(run_card)
        if slot is None or slot < RECENT_RUN_SLOT_MIN:
            continue
        recent_by_slot.setdefault(slot, []).append(run_card)
        rel_to_experiment = run_card.resolve().relative_to(experiment_dir.resolve()).as_posix()
        if rel_to_experiment not in manifest_refs:
            errors.append(
                f"{_repo_rel(run_card, root=repo_root)} is not registered in operator-lab manifest execution_refs"
            )

    for slot, cards in sorted(recent_by_slot.items()):
        if len(cards) > 1:
            joined = ", ".join(_repo_rel(card, root=repo_root) for card in cards)
            errors.append(f"operator-lab run slot run-{slot:03d} is used by multiple run-cards: {joined}")

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
