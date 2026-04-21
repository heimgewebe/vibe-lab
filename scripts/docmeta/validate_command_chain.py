#!/usr/bin/env python3
"""validate_command_chain.py — Cross-contract validator for command chains.

Purpose
-------
Validate a chain of agent commands against:

1. Each individual command's JSON schema (reuse of existing validators).
2. Cross-command semantic invariants defined in
   ``contracts/command-semantics.md``:

   - Sequence: ``read_context → write_change → validate_change``
   - Locator continuity: ``write_change.target_files`` ⊆
     ``read_context.target_files``.
   - Internal semantic contradictions (e.g. ``change_type == "remove"``
     with ``exact_after`` set) that pass the schema but violate the
     semantic contract.

Error model
-----------
Unlike ``validate_agent_commands.py`` (string-based), this validator
emits **structured** ``ChainError`` objects. Both a machine-readable
JSON-Lines stream (stdout when ``--format json``) and a human summary
are produced. Exit codes follow the established convention:

* ``0`` — chain valid
* ``1`` — validation failure (contract / semantic / sequence)
* ``2`` — setup failure (missing schema, missing chain file)

The semantic checks are intentionally minimal. They only encode
invariants that are already written in the semantics contract.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator, SchemaError, ValidationError
    from jsonschema.validators import validator_for
except ImportError:
    print("ERROR: Missing dependencies. Run: python3 -m pip install jsonschema")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCHEMA_DIR = REPO_ROOT / "schemas"

EXPECTED_SEQUENCE: tuple[str, ...] = (
    "read_context",
    "write_change",
    "validate_change",
)

ERROR_CODES: frozenset[str] = frozenset(
    {
        "contract_invalid",
        "command_sequence_invalid",
        "target_files_mismatch",
        "locator_continuity_violation",
        "semantic_contradiction",
    }
)


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


@dataclasses.dataclass(frozen=True)
class ChainError:
    """Structured error for chain validation.

    Attributes mirror the error model documented in
    ``contracts/command-semantics.md``.
    """

    code: str
    message: str
    command_index: int
    path: str

    def __post_init__(self) -> None:  # pragma: no cover — defensive guard
        if self.code not in ERROR_CODES:
            raise ValueError(f"unknown chain error code: {self.code}")

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


def schema_path_for(command: str) -> Path:
    return SCHEMA_DIR / f"command.{command}.schema.json"


def load_validator(schema_path: Path) -> Draft202012Validator:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator_cls = validator_for(schema, default=Draft202012Validator)
    validator_cls.check_schema(schema)
    return validator_cls(schema, format_checker=validator_cls.FORMAT_CHECKER)


def _validators_by_command() -> dict[str, Draft202012Validator]:
    out: dict[str, Draft202012Validator] = {}
    for command in EXPECTED_SEQUENCE:
        spath = schema_path_for(command)
        if not spath.is_file():
            print(f"ERROR: schema missing: {display_path(spath)}")
            sys.exit(2)
        try:
            out[command] = load_validator(spath)
        except SchemaError as exc:
            print(
                f"ERROR: schema invalid ({display_path(spath)}): {exc.message}"
            )
            sys.exit(2)
    return out


def load_chain(chain_path: Path) -> list[dict[str, Any]]:
    """Load a chain JSON file; exits with code 2 on any setup error.

    Public because ``tools/vibe-cli/replay_minimal.py`` reuses it.
    """
    if not chain_path.is_file():
        print(f"ERROR: chain file missing: {display_path(chain_path)}")
        sys.exit(2)
    try:
        data = json.loads(chain_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: chain file is not valid JSON: {exc}")
        sys.exit(2)
    if not isinstance(data, list):
        print("ERROR: chain file must contain a JSON array of command records")
        sys.exit(2)
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            print(f"ERROR: chain[{i}] must be an object")
            sys.exit(2)
    return data


# ---------------------------------------------------------------------------
# Validation stages
# ---------------------------------------------------------------------------


def _validate_individual(
    chain: list[dict[str, Any]],
    validators: dict[str, Draft202012Validator],
    chain_label: str,
) -> list[ChainError]:
    errors: list[ChainError] = []
    for idx, record in enumerate(chain):
        command = record.get("command")
        # Guard against unhashable command values (e.g. dict, list): an
        # unhashable value can never match a key in `validators`, so treat
        # it as an unknown command and emit contract_invalid rather than
        # letting the hash-based `in` test raise TypeError.
        try:
            command_known = isinstance(command, str) and command in validators
        except TypeError:
            command_known = False
        if not command_known:
            errors.append(
                ChainError(
                    code="contract_invalid",
                    message=(
                        f"unknown or missing command '{command}'; "
                        f"expected one of {sorted(validators)}"
                    ),
                    command_index=idx,
                    path=chain_label,
                )
            )
            continue
        try:
            validators[command].validate(record)
        except ValidationError as exc:
            errors.append(
                ChainError(
                    code="contract_invalid",
                    message=f"schema validation failed: {exc.message}",
                    command_index=idx,
                    path=chain_label,
                )
            )
    return errors


def _validate_sequence(
    chain: list[dict[str, Any]], chain_label: str
) -> list[ChainError]:
    """Only accept the exact canonical sequence in v0.1.

    Rationale (contracts/command-semantics.md, §Chain Invariants):
    the v0.1 chain is fixed to read_context → write_change → validate_change.
    No prefix/partial chains are considered valid.
    """
    actual = tuple(r.get("command") for r in chain)
    if actual == EXPECTED_SEQUENCE:
        return []
    return [
        ChainError(
            code="command_sequence_invalid",
            message=(
                "chain sequence "
                f"{list(actual)} does not match expected "
                f"{list(EXPECTED_SEQUENCE)}"
            ),
            command_index=-1,
            path=chain_label,
        )
    ]


def _validate_version_consistency(
    chain: list[dict[str, Any]], chain_label: str
) -> list[ChainError]:
    errors: list[ChainError] = []
    versions: set[Any] = set()
    for r in chain:
        if "version" in r:
            v = r.get("version")
            try:
                versions.add(v)
            except TypeError:
                # Unhashable version value (e.g. dict or list). Schema
                # validation will already emit contract_invalid for this
                # record. Represent the value as its string form so we
                # can still detect cross-record version inconsistency.
                versions.add(repr(v))
    if len(versions) > 1:
        errors.append(
            ChainError(
                code="command_sequence_invalid",
                message=(
                    "mixed command versions in chain: "
                    f"{sorted(str(v) for v in versions)}"
                ),
                command_index=-1,
                path=chain_label,
            )
        )
    return errors


def _validate_target_files_continuity(
    chain: list[dict[str, Any]], chain_label: str
) -> list[ChainError]:
    # Only meaningful if chain matches the expected shape.
    # Build command→record map safely: skip records whose command value is
    # unhashable (they are already flagged as contract_invalid).
    by_cmd: dict[str, dict[str, Any]] = {}
    for r in chain:
        if not isinstance(r, dict):
            continue
        cmd = r.get("command")
        if isinstance(cmd, str):
            by_cmd[cmd] = r
    read_ctx = by_cmd.get("read_context")
    write_chg = by_cmd.get("write_change")
    if read_ctx is None or write_chg is None:
        return []

    read_files = read_ctx.get("target_files") or []
    write_files = write_chg.get("target_files") or []
    if not isinstance(read_files, list) or not isinstance(write_files, list):
        return []

    read_set = {f for f in read_files if isinstance(f, str)}
    missing = [f for f in write_files if isinstance(f, str) and f not in read_set]
    if not missing:
        return []

    write_idx = next(
        (i for i, r in enumerate(chain) if r.get("command") == "write_change"),
        -1,
    )
    return [
        ChainError(
            code="target_files_mismatch",
            message=(
                "write_change.target_files not subset of "
                f"read_context.target_files; missing={sorted(missing)}"
            ),
            command_index=write_idx,
            path=chain_label,
        )
    ]


def _validate_locator_continuity(
    chain: list[dict[str, Any]], chain_label: str
) -> list[ChainError]:
    """Validate locator fields in write_change records.

    **v0.1 scope (partial operationalization):**
    Only the following is checked in v0.1:

    * ``write_change.locator``, when present, must not be empty or
      whitespace-only. This is belt-and-suspenders over the schema
      ``minLength: 1`` constraint.

    **Not checked in v0.1 (📋 documented for v0.2):**

    * Coupling between ``write_change.locator`` and
      ``read_context.extracted_facts``: verifying that the locator
      actually refers to a location that was read would require either
      file I/O (excluded by design) or structured extracted_facts
      (not yet defined in v0.1). Triggering ``locator_continuity_violation``
      on that basis is **deferred**.

    See ``contracts/command-semantics.md`` §Chain Invariants for the
    full documented intent.
    """
    errors: list[ChainError] = []
    for idx, record in enumerate(chain):
        if record.get("command") != "write_change":
            continue
        locator = record.get("locator")
        if locator is not None and isinstance(locator, str) and not locator.strip():
            errors.append(
                ChainError(
                    code="locator_continuity_violation",
                    message="write_change.locator is empty or whitespace",
                    command_index=idx,
                    path=chain_label,
                )
            )
    return errors


def _validate_semantic_anti_invariants(
    chain: list[dict[str, Any]], chain_label: str
) -> list[ChainError]:
    """Encodes single-record anti-invariants from command-semantics.md."""
    errors: list[ChainError] = []
    for idx, record in enumerate(chain):
        command = record.get("command")
        if command == "write_change":
            change_type = record.get("change_type")
            exact_before = record.get("exact_before")
            exact_after = record.get("exact_after")
            if change_type == "remove" and exact_after is not None:
                errors.append(
                    ChainError(
                        code="semantic_contradiction",
                        message=(
                            "change_type=remove with exact_after set; "
                            "a removal has no post-state"
                        ),
                        command_index=idx,
                        path=chain_label,
                    )
                )
            if change_type == "add" and exact_before is not None:
                errors.append(
                    ChainError(
                        code="semantic_contradiction",
                        message=(
                            "change_type=add with exact_before set; "
                            "an addition has no pre-state at the locator"
                        ),
                        command_index=idx,
                        path=chain_label,
                    )
                )
            if (
                exact_before is not None
                and exact_after is not None
                and exact_before == exact_after
            ):
                errors.append(
                    ChainError(
                        code="semantic_contradiction",
                        message="exact_before == exact_after; no effective change",
                        command_index=idx,
                        path=chain_label,
                    )
                )
            tf = record.get("target_files") or []
            if isinstance(tf, list) and len(tf) != len(set(tf)):
                errors.append(
                    ChainError(
                        code="semantic_contradiction",
                        message="write_change.target_files contains duplicates",
                        command_index=idx,
                        path=chain_label,
                    )
                )
        elif command == "read_context":
            tf = record.get("target_files") or []
            if isinstance(tf, list) and len(tf) != len(set(tf)):
                errors.append(
                    ChainError(
                        code="semantic_contradiction",
                        message="read_context.target_files contains duplicates",
                        command_index=idx,
                        path=chain_label,
                    )
                )
    return errors


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def validate_chain(
    chain: list[dict[str, Any]],
    chain_label: str,
    validators: dict[str, Draft202012Validator] | None = None,
) -> list[ChainError]:
    """Run all chain-level checks; returns aggregated ``ChainError`` list."""
    if validators is None:
        validators = _validators_by_command()

    errors: list[ChainError] = []
    errors.extend(_validate_individual(chain, validators, chain_label))
    # Sequence/version checks are meaningful only if individual records
    # carry a recognizable shape, but we still run them: they catch
    # the "wrong order" class even when each command is well-formed.
    errors.extend(_validate_sequence(chain, chain_label))
    errors.extend(_validate_version_consistency(chain, chain_label))
    errors.extend(_validate_target_files_continuity(chain, chain_label))
    errors.extend(_validate_locator_continuity(chain, chain_label))
    errors.extend(_validate_semantic_anti_invariants(chain, chain_label))
    return errors


def _format_human(chain_label: str, errors: Iterable[ChainError]) -> str:
    lines = [f"❌ Chain validation failed: {chain_label}"]
    for err in errors:
        lines.append(
            f"  - [{err.code}] (command_index={err.command_index}) {err.message}"
        )
    return "\n".join(lines)


def _format_json(errors: Iterable[ChainError]) -> str:
    return "\n".join(json.dumps(err.to_dict(), sort_keys=True) for err in errors)


def _detect_expected_errors(chain_file: Path) -> list[str]:
    """Chain fixtures may declare `expected_errors: [...]` (top-level sibling).

    Because the chain file itself is a JSON array, we use a sidecar:
    ``<stem>.expected.json`` containing ``{"expected_errors": [codes]}``.
    Missing sidecar means "chain must validate cleanly".
    """
    sidecar = chain_file.with_suffix(".expected.json")
    if not sidecar.is_file():
        return []
    try:
        data = json.loads(sidecar.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    if not isinstance(data, dict):
        return []
    codes = data.get("expected_errors")
    if not isinstance(codes, list):
        return []
    return [c for c in codes if isinstance(c, str)]


def _run_fixture_dir(fixtures_root: Path) -> int:
    if not fixtures_root.is_dir():
        print(f"ERROR: fixtures root missing: {display_path(fixtures_root)}")
        return 2
    chain_files = sorted(fixtures_root.glob("*.json"))
    chain_files = [p for p in chain_files if not p.name.endswith(".expected.json")]
    if not chain_files:
        print(f"ERROR: no chain fixtures under {display_path(fixtures_root)}")
        return 2

    validators = _validators_by_command()
    failed = 0
    print("🔍 Command Chain Validation")
    for chain_path in chain_files:
        label = display_path(chain_path)
        chain = load_chain(chain_path)
        observed = validate_chain(chain, label, validators)
        expected = _detect_expected_errors(chain_path)

        observed_codes = sorted({e.code for e in observed})
        expected_codes = sorted(set(expected))

        if expected_codes:
            if observed_codes == expected_codes:
                print(f"  ✅ {label} (expected errors: {expected_codes})")
            else:
                failed += 1
                print(
                    f"  ❌ {label}: "
                    f"expected={expected_codes} observed={observed_codes}"
                )
                for err in observed:
                    print(
                        f"      - [{err.code}] "
                        f"(command_index={err.command_index}) {err.message}"
                    )
        else:
            if observed:
                failed += 1
                print(f"  ❌ {label}: unexpected failures")
                for err in observed:
                    print(
                        f"      - [{err.code}] "
                        f"(command_index={err.command_index}) {err.message}"
                    )
            else:
                print(f"  ✅ {label}")

    if failed:
        print(f"\n❌ Command chain validation failed ({failed} case(s)).")
        return 1
    print("\n✅ Command chain validation passed.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate command chains against semantic contracts"
    )
    parser.add_argument(
        "--fixtures",
        type=Path,
        default=REPO_ROOT / "tests" / "fixtures" / "command_chains",
        help=(
            "Directory containing chain fixtures (default: "
            "tests/fixtures/command_chains). Each *.json is a chain; "
            "<stem>.expected.json may declare expected_errors codes."
        ),
    )
    parser.add_argument(
        "--chain",
        type=Path,
        default=None,
        help="Validate a single chain file (overrides --fixtures).",
    )
    parser.add_argument(
        "--format",
        choices=("human", "json"),
        default="human",
        help="Output format for single-chain mode (--chain).",
    )
    args = parser.parse_args()

    if args.chain is not None:
        chain_path = (
            (REPO_ROOT / args.chain).resolve()
            if not args.chain.is_absolute()
            else args.chain
        )
        chain = load_chain(chain_path)
        errors = validate_chain(chain, display_path(chain_path))
        if not errors:
            if args.format == "human":
                print(f"✅ Chain valid: {display_path(chain_path)}")
            sys.exit(0)
        if args.format == "json":
            print(_format_json(errors))
        else:
            print(_format_human(display_path(chain_path), errors))
        sys.exit(1)

    fixtures_root = (
        (REPO_ROOT / args.fixtures).resolve()
        if not args.fixtures.is_absolute()
        else args.fixtures
    )
    sys.exit(_run_fixture_dir(fixtures_root))


if __name__ == "__main__":
    main()
