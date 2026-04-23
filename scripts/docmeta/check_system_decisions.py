#!/usr/bin/env python3
"""check_system_decisions.py - Guard for minimal system_decision contracts.

Validates decisions under decisions/system/ against the minimal schema and
enforces feature gates via effects.enables / effects.disables.
"""

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
    from jsonschema import Draft202012Validator
except ImportError:
    print("ERROR: Missing dependencies. Run: python3 -m pip install pyyaml jsonschema rfc3339-validator")
    sys.exit(1)


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_DECISIONS_DIR = REPO_ROOT / "decisions" / "system"
DEFAULT_SCHEMA_PATH = REPO_ROOT / "contracts" / "system_decision.schema.json"


def _load_yaml(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"expected YAML object, got {type(data).__name__}")
    return data


def _load_validator(schema_path: Path) -> Draft202012Validator:
    with open(schema_path, encoding="utf-8") as f:
        schema = json.load(f)
    return Draft202012Validator(schema, format_checker=Draft202012Validator.FORMAT_CHECKER)


def _has_enabled_feature(decisions: list[dict], feature: str) -> bool:
    for decision in decisions:
        if decision.get("status") != "active":
            continue
        effects = decision.get("effects", {})
        enables = effects.get("enables", []) if isinstance(effects, dict) else []
        if feature in enables:
            return True
    return False


def _display_path(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and enforce system decisions")
    parser.add_argument("--feature", default="metrics", help="Feature that must be enabled by an active system_decision")
    parser.add_argument("--decisions-dir", default=str(DEFAULT_DECISIONS_DIR), help="Directory containing system decision files")
    parser.add_argument("--schema", default=str(DEFAULT_SCHEMA_PATH), help="Path to system decision JSON schema")
    args = parser.parse_args()

    decisions_dir = Path(args.decisions_dir)
    schema_path = Path(args.schema)

    if not schema_path.exists():
        print(f"❌ Missing schema: {schema_path}")
        return 1

    if not decisions_dir.exists():
        print(f"❌ Missing decision directory: {decisions_dir}")
        return 1

    validator = _load_validator(schema_path)
    decision_files = sorted(decisions_dir.glob("*.yml"))
    if not decision_files:
        print(f"❌ No decision files found in {decisions_dir}")
        return 1

    print("🔐 System Decision Guard")
    decisions: list[dict] = []
    has_errors = False

    for path in decision_files:
        rel = _display_path(path)
        try:
            data = _load_yaml(path)
        except Exception as exc:
            print(f"  ❌ {rel}: {exc}")
            has_errors = True
            continue

        validation_errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
        if validation_errors:
            has_errors = True
            for err in validation_errors:
                location = ".".join(str(p) for p in err.path) or "<root>"
                print(f"  ❌ {rel} [{location}]: {err.message}")
            continue

        decisions.append(data)
        print(f"  ✅ {rel} ({data.get('claim')}, status={data.get('status')})")

    if has_errors:
        print("❌ Decision guard failed due to contract violations.")
        return 1

    if not _has_enabled_feature(decisions, args.feature):
        print(
            f"❌ Feature gate blocked: '{args.feature}' is not enabled by any active "
            "system_decision (effects.enables)."
        )
        return 1

    print(f"✅ Feature gate open: '{args.feature}' enabled by active system_decision.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
