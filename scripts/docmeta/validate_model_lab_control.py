#!/usr/bin/env python3
"""validate_model_lab_control.py — opt-in Lab-Control-Minimum check.

This validator is deliberately additive: it validates only run_meta.json files
that explicitly opt in with ``"model_lab_control": true``. Historical run
metadata without that flag is ignored so AP-1 can introduce machine-readable
comparability checks without globally hardening schemas or breaking legacy runs.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

REQUIRED_STRING_FIELDS: tuple[str, ...] = (
    "model_id",
    "model_provider",
    "model_version_or_date",
    "tooling",
    "agent_mode",
    "challenge_id",
    "challenge_version",
    "condition",
    "control_condition",
    "temperature_or_sampling",
    "run_started_at",
    "run_finished_at",
    "human_intervention_level",
)

REQUIRED_LIST_FIELDS: tuple[str, ...] = (
    "evidence_artifacts",
)


@dataclass(frozen=True)
class ValidationResult:
    checked: int
    activated: int
    errors: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.errors


def _validate_activated_run(path: Path, data: dict[str, object]) -> list[str]:
    errors: list[str] = []

    for field in REQUIRED_STRING_FIELDS:
        value = data.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(
                f"{path}: missing or invalid required Model-Lab string field: {field}"
            )

    for field in REQUIRED_LIST_FIELDS:
        value = data.get(field)
        if not isinstance(value, list) or not value:
            errors.append(f"{path}: {field} must be a non-empty array of strings")
        elif any(not isinstance(item, str) or not item.strip() for item in value):
            errors.append(f"{path}: {field} entries must be non-empty strings")

    return errors


def iter_run_meta_files(paths: Iterable[Path]) -> Iterable[Path]:
    for path in paths:
        if path.is_dir():
            candidates = set(path.rglob("run_meta.json"))
            candidates.update(path.rglob("*run-meta.json"))
            yield from sorted(candidates)
        else:
            # Direct file arguments are yielded as-is so tests and ad-hoc checks can
            # validate scenario-named fixtures such as missing-model-id.json.
            yield path


def validate_files(paths: Iterable[Path]) -> ValidationResult:
    checked = 0
    activated = 0
    errors: list[str] = []

    for path in iter_run_meta_files(paths):
        checked += 1
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{path}: invalid JSON: {exc}")
            continue
        except OSError as exc:
            errors.append(f"{path}: cannot read file: {exc}")
            continue

        if not isinstance(data, dict):
            errors.append(f"{path}: run_meta.json must contain a JSON object")
            continue

        if data.get("model_lab_control") is not True:
            continue

        activated += 1
        errors.extend(_validate_activated_run(path, data))

    return ValidationResult(checked=checked, activated=activated, errors=tuple(errors))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate opt-in Model-Lab control metadata. Only run_meta.json files "
            "with model_lab_control=true are enforced."
        )
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        default=[REPO_ROOT / "experiments"],
        help="run_meta.json files or directories to scan (default: experiments/)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = validate_files(args.paths)

    for error in result.errors:
        print(f"ERROR: {error}", file=sys.stderr)

    print(
        "Model-Lab control check: "
        f"checked={result.checked}, activated={result.activated}, errors={len(result.errors)}"
    )
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
