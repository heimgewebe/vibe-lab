#!/usr/bin/env python3
"""validate_agent_commands.py — Validates command.* fixtures against their schemas.

Covers Phase D of docs/blueprints/blueprint-agent-operability-phase-1c.md
(Deliverables D4–D6). Intentionally minimal:

- Validates JSON fixtures under tests/fixtures/agent_commands/<command>/ against
  schemas/command.<command>.schema.json.
- Fixtures may declare `expected_error: "contract_invalid"` to assert a negative
  case (mirrors the pattern from validate_agent_handoff.py).
- Does NOT execute any command. Replay/execution is Phase F (deferred).
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
SCHEMA_DIR = REPO_ROOT / "schemas"
DEFAULT_FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "agent_commands"

COMMANDS: tuple[str, ...] = ("read_context", "write_change", "validate_change")

SUPPORTED_EXPECTED_ERRORS = frozenset({"contract_invalid"})


def display_path(path: Path) -> str:
    """Return repo-relative path where possible, otherwise absolute path."""
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def schema_path_for(command: str) -> Path:
    return SCHEMA_DIR / f"command.{command}.schema.json"


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

    try:
        validator.validate(data)
    except ValidationError as exc:
        return [f"{label}: contract_invalid: schema validation failed — {exc.message}"]

    return local_errors


def detect_expected_error(path: Path) -> str | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    marker = data.get("expected_error") if isinstance(data, dict) else None
    if isinstance(marker, str) and marker in SUPPORTED_EXPECTED_ERRORS:
        return marker
    return None


def classify_error(local_errors: list[str]) -> str | None:
    return "contract_invalid" if local_errors else None


def run_for_command(
    command: str,
    validator: Draft202012Validator,
    fixture_files: list[Path],
    mode: str,
) -> list[str]:
    print(f"🔍 Command: {command}")
    errs: list[str] = []
    for fixture in fixture_files:
        expected_error = detect_expected_error(fixture)
        local = validate_one(fixture, validator)
        observed_error = classify_error(local)

        if mode == "strict":
            if local:
                errs.extend(local)
            else:
                print(f"  ✅ {display_path(fixture)}")
            continue

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

    return errs


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate agent command fixtures")
    parser.add_argument(
        "--fixtures",
        type=Path,
        default=DEFAULT_FIXTURE_DIR,
        help="Root directory containing command fixtures (default: tests/fixtures/agent_commands)",
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

    fixtures_root = (
        (REPO_ROOT / args.fixtures).resolve()
        if not args.fixtures.is_absolute()
        else args.fixtures
    )
    if not fixtures_root.is_dir():
        print(f"ERROR: fixtures root missing: {display_path(fixtures_root)}")
        sys.exit(2)

    # Pre-flight: verify all schemas and fixture dirs exist (setup errors → exit 2)
    validators: dict[str, Draft202012Validator] = {}
    fixture_lists: dict[str, list[Path]] = {}
    for command in COMMANDS:
        schema_path = schema_path_for(command)
        if not schema_path.is_file():
            print(f"ERROR: schema missing: {display_path(schema_path)}")
            sys.exit(2)
        try:
            validators[command] = load_validator(schema_path)
        except SchemaError as exc:
            print(f"ERROR: schema invalid ({display_path(schema_path)}): {exc.message}")
            sys.exit(2)
        fixture_dir = fixtures_root / command
        if not fixture_dir.is_dir():
            print(f"ERROR: fixtures directory missing: {display_path(fixture_dir)}")
            sys.exit(2)
        files = sorted(fixture_dir.rglob("*.json"))
        if not files:
            print(f"ERROR: no command fixtures found in {display_path(fixture_dir)}")
            sys.exit(2)
        fixture_lists[command] = files

    print("🔍 Agent Command Validation")
    all_errs: list[str] = []
    for command in COMMANDS:
        all_errs.extend(
            run_for_command(command, validators[command], fixture_lists[command], args.mode)
        )

    if all_errs:
        print("\n❌ Agent command validation failed:")
        for err in all_errs:
            print(f"  - {err}")
        sys.exit(1)

    print("\n✅ Agent command validation passed.")


if __name__ == "__main__":
    main()
