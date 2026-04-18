#!/usr/bin/env python3
"""validate_agent_handoff.py — Validates HANDOFF_BLOCK fixtures.

Checks:
1. Fixture JSON validates against schemas/agent.handoff.schema.json
2. critic_signature is supported (experiment-critic/v1)
3. For status == PASS: handoff hash is recomputed using canon v1 and must match

Canonicalization (canon v1):
- field order: status, target_files, locator, change_type, scope, normalized_task
- target_files: strip entries, deduplicate, lexicographically sort
- scope and normalized_task: trim + collapse internal whitespace + normalize newlines to \n
- locator: trim + normalize newlines to \n (no internal whitespace collapse)
- compact JSON UTF-8 bytes, sha256
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

try:
    from jsonschema import Draft202012Validator, SchemaError, ValidationError
    from jsonschema.validators import validator_for
except ImportError:
    print("ERROR: Missing dependencies. Run: python3 -m pip install jsonschema")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCHEMA_PATH = REPO_ROOT / "schemas" / "agent.handoff.schema.json"
DEFAULT_FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "agent_handoff"

CANON_FIELDS = (
    "status",
    "target_files",
    "locator",
    "change_type",
    "scope",
    "normalized_task",
)

WS_RE = re.compile(r"\s+")


def _normalize_newlines(value: str) -> str:
    return value.replace("\r\n", "\n").replace("\r", "\n")


def _normalize_scope_or_task(value: str) -> str:
    text = _normalize_newlines(value).strip()
    return WS_RE.sub(" ", text)


def _normalize_locator(value: str) -> str:
    return _normalize_newlines(value).strip()


def canonical_payload_v1(handoff: dict) -> dict:
    target_files = handoff.get("target_files", [])
    cleaned_targets = sorted({str(item).strip() for item in target_files if str(item).strip()})

    payload = {
        "status": str(handoff.get("status", "")).strip(),
        "target_files": cleaned_targets,
        "locator": _normalize_locator(str(handoff.get("locator", ""))),
        "change_type": str(handoff.get("change_type", "")).strip(),
        "scope": _normalize_scope_or_task(str(handoff.get("scope", ""))),
        "normalized_task": _normalize_scope_or_task(str(handoff.get("normalized_task", ""))),
    }

    # Keep order deterministic.
    return {k: payload[k] for k in CANON_FIELDS}


def compute_sha256_hex(payload: dict) -> str:
    compact = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(compact.encode("utf-8")).hexdigest()


def load_validator(schema_path: Path) -> Draft202012Validator:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator_cls = validator_for(schema, default=Draft202012Validator)
    validator_cls.check_schema(schema)
    return validator_cls(schema, format_checker=validator_cls.FORMAT_CHECKER)


def validate_one(path: Path, validator: Draft202012Validator) -> list[str]:
    local_errors: list[str] = []

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{path.relative_to(REPO_ROOT)}: invalid JSON — {exc}"]

    try:
        validator.validate(data)
    except ValidationError as exc:
        return [f"{path.relative_to(REPO_ROOT)}: schema validation failed — {exc.message}"]

    status = data.get("status")
    sig = data.get("critic_signature")
    if sig != "experiment-critic/v1":
        local_errors.append(
            f"{path.relative_to(REPO_ROOT)}: unsupported_signature '{sig}' (expected experiment-critic/v1)"
        )

    if status == "PASS":
        handoff_meta = data.get("handoff", {})
        algo = handoff_meta.get("algo")
        canon = handoff_meta.get("canon")
        expected_hash = handoff_meta.get("hash")

        if algo != "sha256":
            local_errors.append(
                f"{path.relative_to(REPO_ROOT)}: unsupported algo '{algo}' (expected sha256)"
            )
        if canon != "v1":
            local_errors.append(
                f"{path.relative_to(REPO_ROOT)}: unsupported canon '{canon}' (expected v1)"
            )

        if not local_errors:
            actual_payload = canonical_payload_v1(data)
            actual_hash = compute_sha256_hex(actual_payload)
            if expected_hash != actual_hash:
                local_errors.append(
                    f"{path.relative_to(REPO_ROOT)}: hash_mismatch expected={expected_hash} actual={actual_hash}"
                )

    return local_errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate agent handoff fixtures")
    parser.add_argument(
        "--fixtures",
        type=Path,
        default=DEFAULT_FIXTURE_DIR,
        help="Directory containing handoff JSON fixtures (default: tests/fixtures/agent_handoff)",
    )
    args = parser.parse_args()

    if not SCHEMA_PATH.is_file():
        print(f"ERROR: schema missing: {SCHEMA_PATH}")
        sys.exit(2)

    try:
        validator = load_validator(SCHEMA_PATH)
    except SchemaError as exc:
        print(f"ERROR: schema invalid ({SCHEMA_PATH.relative_to(REPO_ROOT)}): {exc.message}")
        sys.exit(2)

    fixtures_dir = (REPO_ROOT / args.fixtures).resolve() if not args.fixtures.is_absolute() else args.fixtures
    if not fixtures_dir.is_dir():
        print(f"ERROR: fixtures directory missing: {fixtures_dir}")
        sys.exit(2)

    fixture_files = sorted(fixtures_dir.rglob("*.json"))
    if not fixture_files:
        print(f"ERROR: no handoff fixtures found in {fixtures_dir}")
        sys.exit(2)

    print("🔍 Agent Handoff Validation")
    errs: list[str] = []
    for fixture in fixture_files:
        local = validate_one(fixture, validator)
        if local:
            errs.extend(local)
        else:
            print(f"  ✅ {fixture.relative_to(REPO_ROOT)}")

    if errs:
        print("\n❌ Agent handoff validation failed:")
        for err in errs:
            print(f"  - {err}")
        sys.exit(1)

    print("\n✅ Agent handoff validation passed.")


if __name__ == "__main__":
    main()
