#!/usr/bin/env python3
"""Guard the archived Phase-1c fixture inventory.

The former checker reimplemented manifest, decision, evidence, confidence, and
status semantics for three historical fixtures. That duplicate semantic layer
was retired together with the Phase-1c custom agent. Current experiment truth
continues to be protected by the generic schema, run-bundle, relation, and
claim/evidence validators.

This script now protects only archival integrity:

- the fixed three-case inventory remains complete;
- each case points to its own directory inside the archive root;
- the historical expected verdict metadata does not drift silently;
- referenced fixture directories exist and are non-empty.

It does not interpret fixture content or authorize current experiment outcomes.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "experiment_structure_phase1c"
INDEX_FILE = FIXTURE_ROOT / "expected-outcomes.json"

EXPECTED_CASES: dict[str, tuple[str, str, float]] = {
    "valid": ("VALID", "adopted", 1.0),
    "inconsistent": ("INCONSISTENT", "inconclusive", 0.5),
    "insufficient_input": ("ERROR", "blocked", 0.0),
}


def _load_index(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"missing archive index: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"archive index is invalid JSON: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("archive index root must be an object")
    return data


def archive_errors(
    index_path: Path = INDEX_FILE,
    fixture_root: Path = FIXTURE_ROOT,
    repo_root: Path = REPO_ROOT,
) -> list[str]:
    try:
        data = _load_index(index_path)
    except ValueError as exc:
        return [str(exc)]

    cases = data.get("cases")
    if not isinstance(cases, dict):
        return ["archive index must contain a cases object"]

    errors: list[str] = []
    actual_names = set(cases)
    expected_names = set(EXPECTED_CASES)
    for name in sorted(expected_names - actual_names):
        errors.append(f"missing archived case: {name}")
    for name in sorted(actual_names - expected_names):
        errors.append(f"unexpected archived case: {name}")

    resolved_repo = repo_root.resolve()
    resolved_fixture_root = fixture_root.resolve()

    for name in sorted(expected_names & actual_names):
        case = cases.get(name)
        if not isinstance(case, dict):
            errors.append(f"case {name} must be an object")
            continue

        raw_path = case.get("fixture_path")
        if not isinstance(raw_path, str) or not raw_path.strip():
            errors.append(f"case {name} needs a fixture_path")
            continue

        candidate = (repo_root / raw_path).resolve()
        expected_dir = (fixture_root / name).resolve()
        try:
            candidate.relative_to(resolved_repo)
            candidate.relative_to(resolved_fixture_root)
        except ValueError:
            errors.append(f"case {name} fixture_path escapes the archive root: {raw_path}")
            continue

        if candidate != expected_dir:
            errors.append(
                f"case {name} fixture_path must be {expected_dir.relative_to(resolved_repo).as_posix()}"
            )
        elif not candidate.is_dir():
            errors.append(f"case {name} fixture directory is missing: {raw_path}")
        elif not any(path.is_file() for path in candidate.rglob("*")):
            errors.append(f"case {name} fixture directory is empty: {raw_path}")

        expected_verdict, expected_status, expected_confidence = EXPECTED_CASES[name]
        if case.get("expected_verdict") != expected_verdict:
            errors.append(f"case {name} expected_verdict drifted")
        if case.get("expected_status_assessment") != expected_status:
            errors.append(f"case {name} expected_status_assessment drifted")
        if case.get("expected_confidence") != expected_confidence:
            errors.append(f"case {name} expected_confidence drifted")

        notes = case.get("notes")
        if not isinstance(notes, list) or not notes or not all(
            isinstance(note, str) and note.strip() for note in notes
        ):
            errors.append(f"case {name} must retain non-empty historical notes")

    return errors


def main() -> int:
    errors = archive_errors()
    if errors:
        print("Phase-1c fixture archive guard failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Phase-1c fixture archive intact: 3 historical cases, no semantic re-evaluation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
