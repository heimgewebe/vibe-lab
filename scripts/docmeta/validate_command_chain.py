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
        "validate_error_unbindable",
        "handoff_contract_invalid",
        "handoff_target_drift",
        "handoff_intent_mismatch",
        "handoff_state_drift",
        "validate_without_write",
        "validate_targets_out_of_scope",
        "handoff_locator_drift",
    }
)

HANDOFF_SCHEMA_PATH = Path(__file__).resolve().parent.parent.parent / "schemas" / "agent.handoff.schema.json"


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


def load_chain(chain_path: Path) -> list[Any]:
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
    return data


# ---------------------------------------------------------------------------
# Validation stages
# ---------------------------------------------------------------------------


def _validate_individual(
    chain: list[Any],
    validators: dict[str, Draft202012Validator],
    chain_label: str,
) -> list[ChainError]:
    errors: list[ChainError] = []
    for idx, record in enumerate(chain):
        if not isinstance(record, dict):
            errors.append(
                ChainError(
                    code="contract_invalid",
                    message=(
                        f"chain[{idx}] must be a JSON object, got "
                        f"{type(record).__name__}"
                    ),
                    command_index=idx,
                    path=chain_label,
                )
            )
            continue
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
    chain: list[Any], chain_label: str
) -> list[ChainError]:
    """Only accept the exact canonical sequence in v0.1.

    Rationale (contracts/command-semantics.md, §Chain Invariants):
    the v0.1 chain is fixed to read_context → write_change → validate_change.
    No prefix/partial chains are considered valid.
    """
    actual = tuple(
        r.get("command") if isinstance(r, dict) else "<non_object_record>"
        for r in chain
    )
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
    chain: list[Any], chain_label: str
) -> list[ChainError]:
    errors: list[ChainError] = []
    versions: set[Any] = set()
    for r in chain:
        if not isinstance(r, dict):
            continue
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
    chain: list[Any], chain_label: str
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
        (
            i
            for i, r in enumerate(chain)
            if isinstance(r, dict) and r.get("command") == "write_change"
        ),
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
    chain: list[Any], chain_label: str
) -> list[ChainError]:
    """Validate locator fields in write_change records.

    **v0.1 scope (partial operationalization):**
    Only the following is checked in v0.1:

    * ``write_change.locator``, when present, must not be empty or
      whitespace-only. This is belt-and-suspenders over the schema
      ``minLength: 1`` constraint.

    **Not checked here (📋 separate invariant):**

    * Coupling between ``write_change.locator`` and
      ``read_context.extracted_facts``: verifying that the locator
      actually refers to a location that was read would require either
      file I/O (excluded by design) or structured extracted_facts
      (not yet defined in v0.1). Triggering ``locator_continuity_violation``
      on that basis is **deferred**.
    * ``handoff.locator`` ↔ ``write_change.locator`` consistency is checked
      separately by ``_validate_handoff_locator_drift``.

    See ``contracts/command-semantics.md`` §Chain Invariants for the
    full documented intent.
    """
    errors: list[ChainError] = []
    for idx, record in enumerate(chain):
        if not isinstance(record, dict):
            continue
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
    chain: list[Any], chain_label: str
) -> list[ChainError]:
    """Encodes single-record anti-invariants from command-semantics.md."""
    errors: list[ChainError] = []
    for idx, record in enumerate(chain):
        if not isinstance(record, dict):
            continue
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
            # Empty-asserted-state contradictions: when an exact_* field is
            # present, the side that the change_type semantically asserts must
            # not be empty. The forbidden-side rules above already cover the
            # case where the wrong side is set; this rule covers the
            # complementary case where the right side is set but vacuous.
            #
            # Asserted side per change_type (only checked when present):
            #   add      -> exact_after  must be non-empty (post-state asserted)
            #   remove   -> exact_before must be non-empty (pre-state asserted)
            #   modify   -> both sides, when present, must be non-empty
            #   replace  -> both sides, when present, must be non-empty
            asserted_fields: tuple[str, ...] = ()
            if change_type == "add":
                asserted_fields = ("exact_after",)
            elif change_type == "remove":
                asserted_fields = ("exact_before",)
            elif change_type in ("modify", "replace"):
                asserted_fields = ("exact_before", "exact_after")
            for field in asserted_fields:
                value = record.get(field)
                if isinstance(value, str) and value == "":
                    errors.append(
                        ChainError(
                            code="semantic_contradiction",
                            message=(
                                f"change_type={change_type} with empty {field}; "
                                "asserted state is vacuous"
                            ),
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


def _validate_error_check_binding(
    chain: list[Any], chain_label: str
) -> list[ChainError]:
    """Each errors[] entry in validate_change must be bindable to a checks[].

    **v0.1 rule:** an error string is considered bound when it starts with
    ``<check>:`` where ``<check>`` is a value from ``checks[]``.  A bare
    colon immediately following the check name is sufficient; surrounding
    whitespace in the error string is not normalised (the prefix must be
    exact).

    Only applies when ``success == False``; ``success == True`` implies
    ``errors == []`` by schema, so there is nothing to check.

    Violations produce ``validate_error_unbindable`` — one error per
    unbound entry.

    **Scope discipline (v0.1):**
    * String errors only.  No structured error objects.
    * No heuristic inference; only literal prefix matching.
    * Does not restrict which check names appear in checks[]; those remain
      an open list (see Tolerated Ambiguity in command-semantics.md).

    See ``contracts/command-semantics.md`` §Command: validate_change
    (Invariants) and §Chain Anti-Invariants.
    """
    errors: list[ChainError] = []
    for idx, record in enumerate(chain):
        if not isinstance(record, dict):
            continue
        if record.get("command") != "validate_change":
            continue
        if record.get("success") is not False:
            continue
        checks = record.get("checks") or []
        if not isinstance(checks, list):
            continue
        check_names = {c for c in checks if isinstance(c, str)}
        if not check_names:
            continue
        error_entries = record.get("errors") or []
        if not isinstance(error_entries, list):
            continue
        for entry in error_entries:
            if not isinstance(entry, str):
                continue
            bound = any(entry.startswith(check + ":") for check in check_names)
            if not bound:
                errors.append(
                    ChainError(
                        code="validate_error_unbindable",
                        message=(
                            f"errors[] entry not bindable to any check: {entry!r}; "
                            f"expected prefix from {sorted(check_names)}"
                        ),
                        command_index=idx,
                        path=chain_label,
                    )
                )
    return errors


def _validate_validate_result_seam(
    chain: list[Any], chain_label: str
) -> list[ChainError]:
    """Validate→Result seam: plausibility checks between validate_change and write_change.

    **v0.1 minimal invariants (cross-record):**

    1. ``validate_without_write``: a ``validate_change`` record must be preceded
       by at least one ``write_change`` in the same chain. A ``validate_change``
       that exists without a prior ``write_change`` is semantically ungrounded.

    2. ``validate_targets_out_of_scope``: when ``validate_change.checks`` is
       non-empty, the most recent preceding ``write_change`` in the same chain
       must carry a non-empty ``target_files`` list. Without concrete target
       files there is no plausible scope for the validation to act on.

    **Note on double-reporting:** when the preceding ``write_change`` is already
    schema-invalid (``contract_invalid``), this check still fires and produces
    ``validate_targets_out_of_scope`` in addition. This is intentional: schema
    invalidity and semantic-plausibility loss are distinct concerns and both are
    reported independently (v0.1 scope).

    **Scope discipline (v0.1):**
    * Purely structural plausibility — no semantic analysis of check names.
    * Only the emptiness / absence of ``write_change.target_files`` is tested;
      content of checks[] is not inspected further.
    * No new result-schema semantics; no ``errors[]`` structure.

    See ``contracts/command-semantics.md`` §Command: validate_change and
    §Chain Anti-Invariants.
    """
    errors: list[ChainError] = []
    for idx, record in enumerate(chain):
        if not isinstance(record, dict):
            continue
        if record.get("command") != "validate_change":
            continue

        # Find the most recent write_change that precedes this validate_change.
        preceding_write: dict[str, Any] | None = None
        for j in range(idx - 1, -1, -1):
            if (
                isinstance(chain[j], dict)
                and chain[j].get("command") == "write_change"
            ):
                preceding_write = chain[j]
                break

        if preceding_write is None:
            errors.append(
                ChainError(
                    code="validate_without_write",
                    message=(
                        "validate_change has no preceding write_change in chain; "
                        "validation cannot be plausibly grounded"
                    ),
                    command_index=idx,
                    path=chain_label,
                )
            )
            continue

        # Only check target_files scope when validate_change.checks is non-empty.
        checks = record.get("checks")
        if not isinstance(checks, list) or len(checks) == 0:
            continue

        target_files = preceding_write.get("target_files")
        if not isinstance(target_files, list) or len(target_files) == 0:
            errors.append(
                ChainError(
                    code="validate_targets_out_of_scope",
                    message=(
                        "validate_change.checks is non-empty but the preceding "
                        "write_change has no target_files to bind the validation against"
                    ),
                    command_index=idx,
                    path=chain_label,
                )
            )
    return errors


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def validate_chain(
    chain: list[Any],
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
    errors.extend(_validate_error_check_binding(chain, chain_label))
    errors.extend(_validate_validate_result_seam(chain, chain_label))
    return errors


# ---------------------------------------------------------------------------
# Cross-contract validation (Handoff ↔ Chain)
# ---------------------------------------------------------------------------


def _load_handoff_validator() -> Draft202012Validator | None:
    if not HANDOFF_SCHEMA_PATH.is_file():
        return None
    try:
        return load_validator(HANDOFF_SCHEMA_PATH)
    except SchemaError:
        return None


def _validate_handoff_contract(
    handoff: dict[str, Any], label: str
) -> list[ChainError]:
    validator = _load_handoff_validator()
    if validator is None:
        return [
            ChainError(
                code="handoff_contract_invalid",
                message=(
                    "agent.handoff schema missing or invalid at "
                    f"{display_path(HANDOFF_SCHEMA_PATH)}"
                ),
                command_index=-1,
                path=label,
            )
        ]
    try:
        validator.validate(handoff)
    except ValidationError as exc:
        return [
            ChainError(
                code="handoff_contract_invalid",
                message=f"handoff schema validation failed: {exc.message}",
                command_index=-1,
                path=label,
            )
        ]
    return []


def _handoff_target_files(handoff: dict[str, Any]) -> list[str]:
    tf = handoff.get("target_files")
    if not isinstance(tf, list):
        return []
    return [f for f in tf if isinstance(f, str)]


def _first_record(
    chain: list[dict[str, Any]], command: str
) -> tuple[int, dict[str, Any]] | None:
    for idx, record in enumerate(chain):
        if isinstance(record, dict) and record.get("command") == command:
            return idx, record
    return None


def _validate_handoff_target_drift(
    handoff: dict[str, Any], chain: list[dict[str, Any]], label: str
) -> list[ChainError]:
    """Symmetric scope-binding: handoff.target_files and every chain record
    with a ``target_files`` field (``read_context``, ``write_change``) must
    name exactly the same set of files.

    Two drift directions are detected and reported with the same code:

    a) A handoff file is absent from a chain record's ``target_files``
       (chain covers less than the handoff scope).
    b) A chain record's ``target_files`` contains a file not listed in
       ``handoff.target_files`` (chain reaches outside the handoff scope).

    Rationale: the handoff is the authoritative scope declaration. Silent
    additions and silent omissions are equally unacceptable drifts.
    """
    handoff_files = _handoff_target_files(handoff)
    if not handoff_files:
        return []
    handoff_set = set(handoff_files)
    errors: list[ChainError] = []
    for idx, record in enumerate(chain):
        if not isinstance(record, dict):
            continue
        command = record.get("command")
        if command not in ("read_context", "write_change"):
            continue
        rec_files = record.get("target_files")
        if not isinstance(rec_files, list):
            continue
        rec_set = {f for f in rec_files if isinstance(f, str)}
        missing = sorted(handoff_set - rec_set)
        extra = sorted(rec_set - handoff_set)
        if missing:
            errors.append(
                ChainError(
                    code="handoff_target_drift",
                    message=(
                        f"{command}.target_files does not cover "
                        f"handoff.target_files; missing={missing}"
                    ),
                    command_index=idx,
                    path=label,
                )
            )
        if extra:
            errors.append(
                ChainError(
                    code="handoff_target_drift",
                    message=(
                        f"{command}.target_files contains files outside "
                        f"handoff.target_files; extra={extra}"
                    ),
                    command_index=idx,
                    path=label,
                )
            )
    return errors


_MUTATING_CHANGE_TYPES: frozenset[str] = frozenset(
    {"add", "modify", "remove", "replace"}
)


def _validate_handoff_intent(
    handoff: dict[str, Any], chain: list[dict[str, Any]], label: str
) -> list[ChainError]:
    """Handoff intent (``change_type``) must be fulfillable by the chain.

    v0.1 rules (no heuristic interpretation):

    * If ``handoff.change_type`` is one of the mutating types, the chain
      MUST contain a ``write_change`` record.
    * If such a ``write_change`` exists, its ``change_type`` MUST equal
      the handoff's ``change_type`` exactly. No promotion, no aliasing.
    """
    change_type = handoff.get("change_type")
    if not isinstance(change_type, str) or change_type not in _MUTATING_CHANGE_TYPES:
        return []

    found = _first_record(chain, "write_change")
    if found is None:
        return [
            ChainError(
                code="handoff_intent_mismatch",
                message=(
                    f"handoff.change_type='{change_type}' requires a "
                    "write_change command; chain has none"
                ),
                command_index=-1,
                path=label,
            )
        ]
    idx, write_rec = found
    wc_change = write_rec.get("change_type")
    if wc_change != change_type:
        return [
            ChainError(
                code="handoff_intent_mismatch",
                message=(
                    f"handoff.change_type='{change_type}' but "
                    f"write_change.change_type='{wc_change}'"
                ),
                command_index=idx,
                path=label,
            )
        ]
    return []


def _validate_handoff_state_continuity(
    handoff: dict[str, Any], chain: list[dict[str, Any]], label: str
) -> list[ChainError]:
    """No implicit state derivation.

    If the handoff pins ``exact_before`` or ``exact_after``, the
    ``write_change`` record MUST carry the same string verbatim. Silent
    omission or silent divergence is a drift.

    If the handoff does not pin these fields, the chain may set them
    freely — absence in handoff is not an assertion.
    """
    found = _first_record(chain, "write_change")
    if found is None:
        return []
    idx, write_rec = found
    errors: list[ChainError] = []
    for field in ("exact_before", "exact_after"):
        if field not in handoff:
            continue
        handoff_val = handoff.get(field)
        write_val = write_rec.get(field)
        if field not in write_rec:
            errors.append(
                ChainError(
                    code="handoff_state_drift",
                    message=(
                        f"handoff.{field} set but write_change.{field} "
                        "missing (silent omission)"
                    ),
                    command_index=idx,
                    path=label,
                )
            )
            continue
        if handoff_val != write_val:
            errors.append(
                ChainError(
                    code="handoff_state_drift",
                    message=(
                        f"handoff.{field} and write_change.{field} "
                        "differ (silent divergence)"
                    ),
                    command_index=idx,
                    path=label,
                )
            )
    return errors


def _validate_handoff_locator_drift(
    handoff: dict[str, Any], chain: list[dict[str, Any]], label: str
) -> list[ChainError]:
    """Handoff locator and write_change locator must remain consistent.

    If both ``handoff.locator`` and ``write_change.locator`` are present
    and non-empty, they must be equal. Divergence means the chain
    targets a different location than the handoff intended.

    Scope (v0.1):
    * Plain string equality only; no fuzzy matching.
    * Only fires when both sides carry a non-empty locator string.
    * No coupling to ``read_context.extracted_facts``.
    """
    handoff_locator = handoff.get("locator")
    if not isinstance(handoff_locator, str) or not handoff_locator.strip():
        return []
    found = _first_record(chain, "write_change")
    if found is None:
        return []
    idx, write_rec = found
    write_locator = write_rec.get("locator")
    if not isinstance(write_locator, str) or not write_locator.strip():
        return []
    if handoff_locator == write_locator:
        return []
    return [
        ChainError(
            code="handoff_locator_drift",
            message=(
                f"handoff.locator={handoff_locator!r} and "
                f"write_change.locator={write_locator!r} diverge"
            ),
            command_index=idx,
            path=label,
        )
    ]


def validate_cross_contract(
    handoff: dict[str, Any],
    chain: list[dict[str, Any]],
    label: str,
    validators: dict[str, Draft202012Validator] | None = None,
) -> list[ChainError]:
    """Validate a ``{handoff, chain}`` pair end-to-end.

    Order:
    1. Individual chain-level checks (schema, sequence, target subset,
       semantic contradictions).
    2. Handoff schema conformance.
    3. Cross-contract invariants (target drift, intent, state drift).

    Chain errors and cross-contract errors are reported together; the
    caller decides how to act. No implicit defaults are injected.
    """
    errors: list[ChainError] = []
    errors.extend(validate_chain(chain, label, validators))
    errors.extend(_validate_handoff_contract(handoff, label))
    # Cross-contract checks are only meaningful when the handoff is
    # structurally valid; otherwise we'd read fields that the schema has
    # not blessed. Short-circuit after contract failure.
    if any(e.code == "handoff_contract_invalid" for e in errors):
        return errors
    errors.extend(_validate_handoff_target_drift(handoff, chain, label))
    errors.extend(_validate_handoff_intent(handoff, chain, label))
    errors.extend(_validate_handoff_state_continuity(handoff, chain, label))
    errors.extend(_validate_handoff_locator_drift(handoff, chain, label))
    return errors


def load_cross_contract_fixture(
    path: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[str]]:
    """Load a cross-contract fixture file.

    Format::

        {
          "handoff": {...},
          "chain":   [...],
          "expected_errors": ["code", ...]   // optional
        }

    ``expected_errors`` is the set of distinct error codes the fixture
    must produce; omission means "must validate cleanly".
    """
    if not path.is_file():
        print(f"ERROR: cross-contract fixture missing: {display_path(path)}")
        sys.exit(2)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: fixture is not valid JSON: {exc}")
        sys.exit(2)
    if not isinstance(data, dict):
        print(f"ERROR: fixture {display_path(path)} must be a JSON object")
        sys.exit(2)
    handoff = data.get("handoff")
    chain = data.get("chain")
    if not isinstance(handoff, dict):
        print(f"ERROR: fixture {display_path(path)} is missing object 'handoff'")
        sys.exit(2)
    if not isinstance(chain, list):
        print(f"ERROR: fixture {display_path(path)} is missing array 'chain'")
        sys.exit(2)
    for i, item in enumerate(chain):
        if not isinstance(item, dict):
            print(
                f"ERROR: fixture {display_path(path)}: "
                f"chain[{i}] must be a JSON object, got {type(item).__name__}"
            )
            sys.exit(2)
    expected = data.get("expected_errors", [])
    if not isinstance(expected, list) or not all(isinstance(c, str) for c in expected):
        print(
            f"ERROR: fixture {display_path(path)} has invalid 'expected_errors'"
        )
        sys.exit(2)
    return handoff, chain, expected


def _run_cross_contract_fixture_dir(fixtures_root: Path) -> int:
    if not fixtures_root.is_dir():
        print(
            f"ERROR: cross-contract fixtures root missing: "
            f"{display_path(fixtures_root)}"
        )
        return 2
    fixture_files = sorted(fixtures_root.rglob("*.json"))
    if not fixture_files:
        print(
            f"ERROR: no cross-contract fixtures under "
            f"{display_path(fixtures_root)}"
        )
        return 2

    validators = _validators_by_command()
    failed = 0
    print("🔍 Cross-Contract Validation (Handoff ↔ Chain)")
    for fixture_path in fixture_files:
        label = display_path(fixture_path)
        handoff, chain, expected = load_cross_contract_fixture(fixture_path)
        observed = validate_cross_contract(handoff, chain, label, validators)
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
        print(f"\n❌ Cross-contract validation failed ({failed} case(s)).")
        return 1
    print("\n✅ Cross-contract validation passed.")
    return 0


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
        "--handoff",
        type=Path,
        default=None,
        help=(
            "Path to a HANDOFF_BLOCK JSON file. When given with --chain, "
            "runs cross-contract validation (Handoff ↔ Chain)."
        ),
    )
    parser.add_argument(
        "--cross-contract-fixtures",
        type=Path,
        default=None,
        help=(
            "Directory containing cross-contract fixtures (each file is "
            "a JSON object with 'handoff', 'chain', and optional "
            "'expected_errors'). Overrides --fixtures/--chain."
        ),
    )
    parser.add_argument(
        "--format",
        choices=("human", "json"),
        default="human",
        help="Output format for single-chain mode (--chain).",
    )
    args = parser.parse_args()

    if args.cross_contract_fixtures is not None:
        root = (
            (REPO_ROOT / args.cross_contract_fixtures).resolve()
            if not args.cross_contract_fixtures.is_absolute()
            else args.cross_contract_fixtures
        )
        sys.exit(_run_cross_contract_fixture_dir(root))

    if args.chain is not None:
        chain_path = (
            (REPO_ROOT / args.chain).resolve()
            if not args.chain.is_absolute()
            else args.chain
        )
        chain = load_chain(chain_path)

        if args.handoff is not None:
            handoff_path = (
                (REPO_ROOT / args.handoff).resolve()
                if not args.handoff.is_absolute()
                else args.handoff
            )
            if not handoff_path.is_file():
                print(f"ERROR: handoff file missing: {display_path(handoff_path)}")
                sys.exit(2)
            try:
                handoff = json.loads(handoff_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                print(f"ERROR: handoff file is not valid JSON: {exc}")
                sys.exit(2)
            if not isinstance(handoff, dict):
                print("ERROR: handoff file must contain a JSON object")
                sys.exit(2)
            label = display_path(chain_path)
            errors = validate_cross_contract(handoff, chain, label)
            if not errors:
                if args.format == "human":
                    print(f"✅ Cross-contract valid: {label}")
                sys.exit(0)
            if args.format == "json":
                print(_format_json(errors))
            else:
                print(_format_human(label, errors))
            sys.exit(1)

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
