#!/usr/bin/env python3
"""replay_minimal.py — Deterministic, non-mutating chain simulation trace generator.

Scope
-----
This tool produces a **deterministic contract-validation trace** for a
predefined command chain. It is **not** an execution engine and does
**not** replay commands in the sense of running them against real files.

What it does:

1. Loads a predefined command chain (JSON array of command records).
2. Validates the chain against structural schemas and semantic contracts
   via ``scripts/docmeta/validate_command_chain.py``.
3. Produces a step-by-step simulation trace by echoing back the declared
   intent from each record — nothing is inferred, planned, or executed.

What it does **not** do:

* No file reads or writes against ``target_files`` content.
* No planning. The chain is consumed verbatim; nothing is inferred or
  reordered.
* No retries. Any validation failure aborts the simulation with exit 1.
* No heuristics. Every rule is explicit and traceable to
  ``contracts/command-semantics.md``.

The term "replay" in the filename refers to the controlled *re-traversal*
of a declared command sequence through a validation pipeline — not to
execution or file mutation. This distinction is explicitly enforced: the
output always contains ``"mutations": []`` and a ``would_mutate: false``
field on any write_change step.

Exit codes
----------
* ``0`` — chain valid, simulation trace emitted.
* ``1`` — chain invalid (validation errors present).
* ``2`` — setup error (missing chain file, invalid JSON).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Import sibling validator module without requiring package plumbing.
_VALIDATOR_DIR = REPO_ROOT / "scripts" / "docmeta"
if str(_VALIDATOR_DIR) not in sys.path:
    sys.path.insert(0, str(_VALIDATOR_DIR))

import validate_command_chain as vcc  # noqa: E402  (path-adjusted import)

_KNOWN_COMMANDS: frozenset[str] = frozenset(
    {"read_context", "validate_change", "write_change"}
)


def display_path(path: Path) -> str:
    resolved = path.resolve(strict=False)
    try:
        return str(resolved.relative_to(REPO_ROOT))
    except ValueError:
        if resolved.name:
            return f"<external>/{resolved.name}"
        return "<external-chain>"


def _simulate_step(index: int, record: dict[str, Any]) -> dict[str, Any]:
    """Return a deterministic trace entry for one command record.

    The trace intentionally contains **only data already in the record**.
    No synthesis, no re-ordering. This is what makes the output
    reproducible bit-for-bit.
    """
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
        step["forbidden_changes_count"] = len(
            record.get("forbidden_changes") or []
        )
        step["would_mutate"] = False
    elif command == "validate_change":
        step["checks"] = list(record.get("checks") or [])
        step["success"] = record.get("success")
        step["errors_count"] = len(record.get("errors") or [])
    return step


def simulate(chain: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Pure function: chain → trace list. No I/O, no globals."""
    return [_simulate_step(i, rec) for i, rec in enumerate(chain)]


# ---------------------------------------------------------------------------
# v0.2 trace builder
# ---------------------------------------------------------------------------


def _build_trace_step_v0_2(
    index: int,
    record: dict[str, Any],
    step_errors: list[str],
    is_contract_valid: bool,
) -> dict[str, Any]:
    """Build one v0.2 step entry. Caller guarantees command is in _KNOWN_COMMANDS."""
    command = record.get("command")
    step: dict[str, Any] = {
        "command": command,
        "errors": step_errors,
        "index": index,
        "valid_contract": is_contract_valid,
        "would_mutate": False,
    }
    # Optional fields — include only when present and applicable.
    target_files = record.get("target_files")
    if isinstance(target_files, list):
        step["target_files"] = [f for f in target_files if isinstance(f, str)]
    if command == "write_change":
        locator = record.get("locator")
        if isinstance(locator, str):
            step["locator"] = locator
    if command == "validate_change":
        checks = record.get("checks")
        if isinstance(checks, list):
            step["checks"] = [c for c in checks if isinstance(c, str)]
    return step


def _build_trace_v0_2(
    chain_label: str,
    chain: list[dict[str, Any]],
    errors: list[Any],
) -> dict[str, Any]:
    """Pure function: (label, chain, errors) → v0.2 trace dict. No I/O."""
    # Partition errors by command_index.
    top_level_msgs: list[str] = []
    step_errors_by_idx: dict[int, list[str]] = {}
    contract_invalid_indices: set[int] = set()

    for err in errors:
        if err.command_index < 0:
            top_level_msgs.append(err.message)
        else:
            step_errors_by_idx.setdefault(err.command_index, []).append(err.message)
            if err.code == "contract_invalid":
                contract_invalid_indices.add(err.command_index)

    # Build steps; unknown/missing-command records are skipped — their errors go top-level.
    steps: list[dict[str, Any]] = []
    skipped_records: list[dict[str, Any]] = []
    skipped_record_count = 0
    for i, record in enumerate(chain):
        command = record.get("command")
        # Distinguish between missing/non-string and unknown string commands.
        if not isinstance(command, str) or command not in _KNOWN_COMMANDS:
            top_level_msgs.extend(step_errors_by_idx.get(i, []))
            skipped_record_count += 1
            # Determine reason and label based on command type.
            if not isinstance(command, str):
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
            "skipped_record_count": skipped_record_count,
            "step_count": len(steps),
        },
        "valid_chain": not bool(errors),
        "version": "v0.2",
        "would_mutate": False,
    }


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------


def run(chain_path: Path, emit_json: bool = False) -> int:
    chain = vcc.load_chain(chain_path)  # exits 2 on missing/invalid
    chain_label = display_path(chain_path)
    errors = vcc.validate_chain(chain, chain_label)

    if emit_json:
        result = _build_trace_v0_2(chain_label, chain, errors)
    else:
        result = {
            "chain": chain_label,
            "validation": {
                "ok": not errors,
                "errors": [err.to_dict() for err in errors],
            },
            "trace": simulate(chain) if not errors else [],
            "mutations": [],
        }
    # Deterministic output: sorted keys, no time-based fields.
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Deterministic, non-mutating chain simulation trace generator. "
            "Validates a command chain and emits a step-by-step trace. "
            "Never reads or writes target_files content — no execution, "
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
