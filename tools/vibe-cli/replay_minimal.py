#!/usr/bin/env python3
"""replay_minimal.py - deterministic, non-mutating chain simulation trace generator.

Scope
-----
This tool produces a deterministic contract-validation trace for a predefined
command chain. It does not execute commands against real files.

Output modes:
* Legacy mode (default): historical structure with mutations: [].
* v0.2 mode (--emit-json): schema-validated replay trace with top-level
  would_mutate: false and no legacy mutations field.

Exit codes
----------
* 0 - chain valid, simulation trace emitted.
* 1 - chain invalid (validation errors present).
* 2 - setup error (missing chain file, invalid JSON).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Import sibling validator module without requiring package plumbing.
_VALIDATOR_DIR = REPO_ROOT / "scripts" / "docmeta"
if str(_VALIDATOR_DIR) not in sys.path:
    sys.path.insert(0, str(_VALIDATOR_DIR))

import validate_command_chain as vcc  # noqa: E402

_KNOWN_COMMANDS: frozenset[str] = frozenset(
    {"read_context", "validate_change", "write_change"}
)

_ABS_PATH_PATTERN = re.compile(
    r"(^|[\s:=\[\]\(\)\{\}\"',`])((?<!<external>)/(?:[^\s\"'<>|\[\]{}(),;`]+))"
)


def display_path_legacy(path: Path) -> str:
    """Legacy path display logic used by non-JSON replay output."""
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def display_path_v0_2(path: Path) -> str:
    """v0.2 path display logic with deterministic redaction for externals."""
    resolved = path.resolve(strict=False)
    try:
        return str(resolved.relative_to(REPO_ROOT))
    except ValueError:
        if resolved.name:
            return f"<external>/{resolved.name}"
        return "<external-chain>"


def _simulate_step(index: int, record: dict[str, Any]) -> dict[str, Any]:
    """Return a deterministic trace entry for one command record."""
    command = record.get("command", "<missing>")
    step: dict[str, Any] = {
        "step": index,
        "command": command,
        "version": record.get("version"),
        "action": "simulated",
    }
    if command == "read_context":
        step["target_files"] = list(record.get("target_files") or [])
        step["extracted_facts_count"] = len(record.get("extracted_facts") or [])
    elif command == "write_change":
        step["target_files"] = list(record.get("target_files") or [])
        step["change_type"] = record.get("change_type")
        step["locator_present"] = "locator" in record
        step["target_lines_present"] = "target_lines" in record
        step["forbidden_changes_count"] = len(record.get("forbidden_changes") or [])
        step["would_mutate"] = False
    elif command == "validate_change":
        step["checks"] = list(record.get("checks") or [])
        step["success"] = record.get("success")
        step["errors_count"] = len(record.get("errors") or [])
    return step


def simulate(chain: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Pure function: chain -> trace list. No I/O, no globals."""
    return [_simulate_step(i, rec) for i, rec in enumerate(chain)]


def _build_trace_step_v0_2(
    index: int,
    record: dict[str, Any],
    step_errors: list[str],
    is_contract_valid: bool,
) -> dict[str, Any]:
    """Build one v0.2 step entry. Caller guarantees command is known."""
    command = record.get("command")
    step: dict[str, Any] = {
        "command": command,
        "errors": step_errors,
        "index": index,
        "valid_contract": is_contract_valid,
        "would_mutate": False,
    }
    target_files = record.get("target_files")
    if isinstance(target_files, list) and all(isinstance(f, str) for f in target_files):
        # Redact absolute paths in each target file
        step["target_files"] = [_redact_absolute_paths_in_string(f) for f in target_files]
    if command == "write_change":
        locator = record.get("locator")
        if isinstance(locator, str):
            # Redact absolute paths in locator (both :line and #Lline formats)
            step["locator"] = _redact_absolute_paths_in_string(locator)
    if command == "validate_change":
        checks = record.get("checks")
        if isinstance(checks, list) and all(isinstance(c, str) for c in checks):
            step["checks"] = checks
    return step


def _build_trace_v0_2(
    chain_label: str,
    chain: list[Any],
    errors: list[Any],
    top_level_errors: list[str] | None = None,
) -> dict[str, Any]:
    """Pure function: (label, chain, errors) -> v0.2 trace dict."""
    top_level_msgs: list[str] = list(top_level_errors or [])
    step_errors_by_idx: dict[int, list[str]] = {}
    contract_invalid_indices: set[int] = set()

    for err in errors:
        if err.command_index < 0:
            top_level_msgs.append(err.message)
        else:
            step_errors_by_idx.setdefault(err.command_index, []).append(err.message)
            if err.code == "contract_invalid":
                contract_invalid_indices.add(err.command_index)

    steps: list[dict[str, Any]] = []
    skipped_records: list[dict[str, Any]] = []
    for i, record in enumerate(chain):
        if not isinstance(record, dict):
            top_level_msgs.extend(step_errors_by_idx.get(i, []))
            skipped_records.append(
                {
                    "index": i,
                    "command": "<non_object_record>",
                    "reason": "non_object_record",
                }
            )
            continue

        command = record.get("command")
        if (
            not isinstance(command, str)
            or not command.strip()
            or command not in _KNOWN_COMMANDS
        ):
            top_level_msgs.extend(step_errors_by_idx.get(i, []))
            if not isinstance(command, str) or not command.strip():
                reason = "missing_or_non_string_command"
                command_label = "<missing_or_non_string_command>"
            else:
                reason = "unknown_command"
                command_label = command
            skipped_records.append(
                {
                    "index": i,
                    "command": command_label,
                    "reason": reason,
                }
            )
            continue

        step_errs = step_errors_by_idx.get(i, [])
        is_valid = i not in contract_invalid_indices
        steps.append(_build_trace_step_v0_2(i, record, step_errs, is_valid))

    commands_seen = sorted({s["command"] for s in steps})
    total_error_count = len(top_level_msgs) + sum(len(s["errors"]) for s in steps)

    return {
        "chain_path": chain_label,
        "errors": top_level_msgs,
        "mode": "dry_run",
        "skipped_records": skipped_records,
        "steps": steps,
        "summary": {
            "commands_seen": commands_seen,
            "error_count": total_error_count,
            "non_mutation_guarantee": True,
            "record_count": len(chain),
            "skipped_record_count": len(skipped_records),
            "step_count": len(steps),
        },
        "valid_chain": (
            (not bool(errors))
            and (not bool(skipped_records))
            and (not bool(top_level_msgs))
        ),
        "version": "v0.2",
        "would_mutate": False,
    }


def _redact_path_like_token(token: str) -> str:
    """Redact one absolute path-like token deterministically.

    Supports both colon line format (path:10) and hash line format (path#L10).
    """
    if token.startswith("//"):
        return token

    line_suffix = ""
    # Match both colon format (:10, :10:5) and hash-L format (#L10)
    match = re.match(r"^(.*?)(:\d+(?::\d+)?|#L\d+)$", token)
    if match:
        core = match.group(1)
        line_suffix = match.group(2)
    else:
        core = token

    repo_root = str(REPO_ROOT.resolve())
    if core == repo_root:
        return "." + line_suffix
    if core.startswith(repo_root + "/"):
        return core[len(repo_root) + 1 :] + line_suffix

    basename = Path(core).name
    if basename:
        return f"<external>/{basename}{line_suffix}"
    return "<external-chain>"


def _redact_absolute_paths_in_string(value: str) -> str:
    """Redact absolute path substrings inside an arbitrary string."""

    def repl(match: re.Match[str]) -> str:
        prefix = match.group(1)
        token = match.group(2)
        return prefix + _redact_path_like_token(token)

    return _ABS_PATH_PATTERN.sub(repl, value)


def _sanitize_v0_2_payload(value: Any) -> Any:
    """Recursively redact absolute paths from the full v0.2 payload."""
    if isinstance(value, dict):
        return {k: _sanitize_v0_2_payload(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_sanitize_v0_2_payload(v) for v in value]
    if isinstance(value, str):
        return _redact_absolute_paths_in_string(value)
    return value


def _load_chain_emit_json_safe(chain_path: Path) -> tuple[list[Any], list[str], int]:
    """Load chain for emit-json mode without exiting or printing plain text."""
    if not chain_path.is_file():
        return [], [f"chain file missing: {display_path_v0_2(chain_path)}"], 2
    try:
        raw = chain_path.read_text(encoding="utf-8")
    except OSError as exc:
        return (
            [],
            [f"chain file could not be read: {display_path_v0_2(chain_path)} ({type(exc).__name__})"],
            2,
        )
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        return (
            [],
            [
                "chain file is not valid JSON: "
                f"{exc.msg} (line {exc.lineno} column {exc.colno})"
            ],
            2,
        )
    if not isinstance(data, list):
        return [], ["chain file must contain a JSON array of command records"], 2
    return data, [], 0


def run(chain_path: Path, emit_json: bool = False) -> int:
    if not emit_json:
        chain = vcc.load_chain(chain_path)  # exits 2 on missing/invalid
        chain_label = display_path_legacy(chain_path)
        errors = vcc.validate_chain(chain, chain_label)
        result = {
            "chain": chain_label,
            "validation": {
                "ok": not errors,
                "errors": [err.to_dict() for err in errors],
            },
            "trace": simulate(chain) if not errors else [],
            "mutations": [],
        }
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if not errors else 1

    chain_label = display_path_v0_2(chain_path)
    chain, setup_errors, setup_exit = _load_chain_emit_json_safe(chain_path)
    if setup_errors:
        result = _build_trace_v0_2(
            chain_label,
            chain=[],
            errors=[],
            top_level_errors=setup_errors,
        )
        result = _sanitize_v0_2_payload(result)
        print(json.dumps(result, indent=2, sort_keys=True))
        return setup_exit

    errors = vcc.validate_chain(chain, chain_label)
    result = _build_trace_v0_2(chain_label, chain, errors)
    result = _sanitize_v0_2_payload(result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["valid_chain"] else 1


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Deterministic, non-mutating chain simulation trace generator. "
            "Validates a command chain and emits a step-by-step trace. "
            "Never reads or writes target_files content - no execution, "
            "no planning, no retries."
        )
    )
    parser.add_argument(
        "chain",
        type=Path,
        nargs="?",
        default=REPO_ROOT
        / "tests"
        / "fixtures"
        / "command_chains"
        / "valid-minimal.json",
        help=(
            "Path to chain JSON (default: "
            "tests/fixtures/command_chains/valid-minimal.json)."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Explicitly mark run as dry-run. The simulator is always a "
            "dry-run; this flag only makes that intent visible in CI."
        ),
    )
    parser.add_argument(
        "--emit-json",
        action="store_true",
        help=(
            "Emit v0.2 replay trace JSON conforming to "
            "schemas/replay.trace.schema.json. "
            "Without this flag the legacy format is produced (unchanged)."
        ),
    )
    args = parser.parse_args()

    chain_path = (
        (REPO_ROOT / args.chain).resolve()
        if not args.chain.is_absolute()
        else args.chain
    )
    if args.dry_run:
        print(
            "# replay_minimal.py: dry-run mode (no mutations by design)",
            file=sys.stderr,
        )
    sys.exit(run(chain_path, emit_json=args.emit_json))


if __name__ == "__main__":
    main()
