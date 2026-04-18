#!/usr/bin/env python3
"""validate_experiment_validation.py — Validates Phase-1c experiment validation fixtures.

Checks:
1. Fixture JSON validates against schemas/experiment.validation.schema.json
2. For validation_result: experiment_id must be non-empty
3. For validation_error: missing array must have at least one entry

Supports expected_error markers for negative fixtures (same pattern as
validate_agent_handoff.py).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from jsonschema import Draft202012Validator, SchemaError, ValidationError
    from jsonschema.validators import validator_for
except ImportError:
    print("ERROR: Missing dependencies. Run: python3 -m pip install jsonschema")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCHEMA_PATH = REPO_ROOT / "schemas" / "experiment.validation.schema.json"
DEFAULT_FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "experiment_validation"


def display_path(path: Path) -> str:
    """Return repo-relative path where possible, otherwise absolute path."""
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def load_validator(schema_path: Path) -> Draft202012Validator:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator_cls = validator_for(schema, default=Draft202012Validator)
    validator_cls.check_schema(schema)
    return validator_cls(schema, format_checker=validator_cls.FORMAT_CHECKER)


def validate_one(path: Path, validator: Draft202012Validator) -> list[str]:
    local_errors: list[str] = []
    label = display_path(path)

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{label}: contract_invalid: invalid JSON — {exc}"]

    # Strip expected_error marker before validation
    clean = {k: v for k, v in data.items() if k != "expected_error"} if isinstance(data, dict) else data

    try:
        validator.validate(clean)
    except ValidationError as exc:
        return [f"{label}: contract_invalid: schema validation failed — {exc.message}"]

    return local_errors


def detect_expected_error(path: Path) -> str | None:
    """Read optional expected_error marker from fixture JSON.

    Supported classes: contract_invalid.
    """
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    marker = data.get("expected_error") if isinstance(data, dict) else None
    if isinstance(marker, str) and marker in {"contract_invalid"}:
        return marker
    return None


def classify_error(local_errors: list[str]) -> str | None:
    if not local_errors:
        return None
    first = local_errors[0]
    if "contract_invalid" in first:
        return "contract_invalid"
    return "contract_invalid"


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate experiment validation fixtures")
    parser.add_argument(
        "--fixtures",
        type=Path,
        default=DEFAULT_FIXTURE_DIR,
        help="Directory containing validation JSON fixtures (default: tests/fixtures/experiment_validation)",
    )
    parser.add_argument(
        "--mode",
        choices=("assert-fixtures", "strict"),
        default="assert-fixtures",
        help=(
            "assert-fixtures: pass when expected_error markers match observed failures; "
            "strict: fail on any real validation error"
        ),
    )
    args = parser.parse_args()

    if not SCHEMA_PATH.is_file():
        print(f"ERROR: schema missing: {display_path(SCHEMA_PATH)}")
        sys.exit(2)

    try:
        validator = load_validator(SCHEMA_PATH)
    except SchemaError as exc:
        print(f"ERROR: schema invalid ({display_path(SCHEMA_PATH)}): {exc.message}")
        sys.exit(2)

    fixtures_dir = (REPO_ROOT / args.fixtures).resolve() if not args.fixtures.is_absolute() else args.fixtures
    if not fixtures_dir.is_dir():
        print(f"ERROR: fixtures directory missing: {display_path(fixtures_dir)}")
        sys.exit(2)

    fixture_files = sorted(fixtures_dir.rglob("*.json"))
    if not fixture_files:
        print(f"ERROR: no validation fixtures found in {display_path(fixtures_dir)}")
        sys.exit(2)

    print("🔍 Experiment Validation Fixtures")
    errs: list[str] = []
    for fixture in fixture_files:
        expected_error = detect_expected_error(fixture)
        local = validate_one(fixture, validator)
        observed_error = classify_error(local)

        if args.mode == "strict":
            if local:
                errs.extend(local)
            else:
                print(f"  ✅ {display_path(fixture)}")
            continue

        # Default mode: mixed fixture assertions (positive + expected negatives)
        if expected_error is None:
            if local:
                errs.append(
                    f"{display_path(fixture)}: unexpected_failure expected=none observed={observed_error}"
                )
                errs.extend(local)
            else:
                print(f"  ✅ {display_path(fixture)}")
            continue

        if observed_error == expected_error:
            print(f"  ✅ {display_path(fixture)} (expected {expected_error})")
        elif observed_error is None:
            errs.append(
                f"{display_path(fixture)}: expected_failure_missing expected={expected_error} observed=none"
            )
        else:
            errs.append(
                f"{display_path(fixture)}: wrong_failure_class expected={expected_error} observed={observed_error}"
            )
            errs.extend(local)

    if errs:
        print("\n❌ Experiment validation fixture check failed:")
        for err in errs:
            print(f"  - {err}")
        sys.exit(1)

    print("\n✅ Experiment validation fixture check passed.")


if __name__ == "__main__":
    main()
