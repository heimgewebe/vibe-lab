#!/usr/bin/env python3
"""replay_minimal.py — Deterministic, non-mutating chain simulator.

Scope
-----
This is the *minimal* replay corridor described in Phase F-light of the
Phase-1c blueprint. It is **not** an execution engine. It:

1. Loads a predefined command chain (JSON array of command records).
2. Validates the chain via ``scripts.docmeta.validate_command_chain``.
3. Simulates the chain step-by-step and emits a deterministic trace.

Hard limits (enforced by design)
--------------------------------
* No file writes. The simulator never opens any target file for writing
  and never touches ``target_files`` content.
* No planning. The chain is consumed verbatim; nothing is inferred or
  reordered.
* No retries. Any validation failure aborts the simulation with exit 1.
* No heuristics. Every rule is explicit and traceable to
  ``contracts/command-semantics.md``.

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


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


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


def run(chain_path: Path) -> int:
    chain = vcc.load_chain(chain_path)  # exits 2 on missing/invalid
    chain_label = display_path(chain_path)
    errors = vcc.validate_chain(chain, chain_label)

    result: dict[str, Any] = {
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
            "Deterministic replay simulator for validated command chains. "
            "Never mutates files."
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
    args = parser.parse_args()

    chain_path = (
        (REPO_ROOT / args.chain).resolve()
        if not args.chain.is_absolute()
        else args.chain
    )
    if args.dry_run:
        print("# replay_minimal.py: dry-run mode (no mutations by design)")
    sys.exit(run(chain_path))


if __name__ == "__main__":
    main()
