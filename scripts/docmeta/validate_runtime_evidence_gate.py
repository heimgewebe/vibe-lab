#!/usr/bin/env python3
"""validate_runtime_evidence_gate.py — Validator for runtime-evidence gates.

A runtime-evidence gate (``artifacts/<id>/runtime-evidence-gate.yml``) records,
for a single experiment run, which runtime commands were executed, where their
outputs are archived, and a per-check rollup status. It deliberately does NOT
assert model quality; the mandatory ``does_not_establish`` list keeps the
artifact bounded.

This validator complements — it does not replace — the existing evidence
layer (``validate_claim_evidence.py`` / ``run-evidence-pack.v1``). The
run-evidence-pack contract is reused for the per-claim runtime evidence ledger;
this validator only enforces the gate-level semantics that contract cannot
express (a top-level ``validation_status`` rollup and a mandatory anti-overclaim
``does_not_establish`` list).

Enforced semantic rules (exit 1):
  MISSING_DOES_NOT_ESTABLISH       does_not_establish omits a mandatory disclaimer.
  RUNTIME_EVIDENCE_PATH_ESCAPE     a referenced path resolves outside the repo.
  IMPLEMENTATION_PATH_NOT_FOUND    implementation_path is not an existing directory.
  COMMAND_OUTPUT_NOT_FOUND         an executed command (exit_code != null) has no archived output.
  EVIDENCE_ARTIFACT_NOT_FOUND      a pass/fail/partial check has no existing evidence artifact.
  PASS_WITH_NON_PASS_CHECK         validation_status=pass but a check is not pass.
  PASS_WITH_MISSING_COMMAND_OUTPUT validation_status=pass but a command output is missing.
  STRONG_CLAIM_WITHOUT_RUNTIME_EVIDENCE
                                   validation_status=pass without any evidenced passing check.
  NON_PASS_REQUIRES_LIMITATIONS    non-pass status without an explicit known_limitations entry.

Exit codes:
  0  valid
  1  semantic violation
  2  schema error / parse error / tool error

Requires: python3 -m pip install pyyaml jsonschema
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
    from jsonschema import Draft202012Validator
    from jsonschema.exceptions import SchemaError
except ImportError as exc:
    print(
        "ERROR: Missing dependencies for runtime-evidence-gate validation. "
        "Install PyYAML and jsonschema.",
        file=sys.stderr,
    )
    raise SystemExit(2) from exc


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCHEMA_PATH = REPO_ROOT / "schemas" / "runtime-evidence-gate.v1.schema.json"

# Baseline anti-overclaim disclaimers every runtime-evidence gate must carry.
MANDATORY_DISCLAIMERS = (
    "model_quality",
    "comparative_superiority",
    "adoption_readiness",
    "production_correctness",
    "absence_of_regressions",
)

# Check statuses for which an evidence artifact must already exist on disk.
EVIDENCE_REQUIRED_STATUSES = {"pass", "fail", "partial"}

GATE_GLOB = "*/artifacts/*/runtime-evidence-gate.yml"


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def load_schema_validator() -> Draft202012Validator:
    try:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeError(f"schema file missing: {display_path(SCHEMA_PATH)}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"schema file invalid JSON: {display_path(SCHEMA_PATH)}: {exc}"
        ) from exc

    try:
        return Draft202012Validator(schema)
    except SchemaError as exc:
        raise RuntimeError(f"schema invalid: {display_path(SCHEMA_PATH)}: {exc.message}") from exc


def load_yaml(path: Path) -> dict:
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"file missing: {display_path(path)}") from exc
    except yaml.YAMLError as exc:
        raise ValueError(f"YAML parse error in {display_path(path)}: {exc}") from exc

    if not isinstance(loaded, dict):
        raise ValueError(f"YAML document must be an object: {display_path(path)}")
    return loaded


def schema_errors(validator: Draft202012Validator, data: dict, path: Path) -> list[str]:
    errors: list[str] = []
    for error in sorted(validator.iter_errors(data), key=lambda item: list(item.absolute_path)):
        location = ".".join(str(part) for part in error.absolute_path) or "$"
        errors.append(
            f"ERROR path={display_path(path)} instance_path={location}: {error.message}"
        )
    return errors


def format_error(rule_id: str, path: Path, message: str) -> str:
    return f"ERROR rule={rule_id} path={display_path(path)}: {message}"


def _resolves_outside_repo(rel_path: str, repo_root: Path) -> bool:
    """True when rel_path (repo-relative) resolves outside repo_root."""
    try:
        candidate = (repo_root / rel_path).resolve()
        candidate.relative_to(repo_root.resolve())
        return False
    except (ValueError, OSError):
        return True


def _exists(rel_path: str, repo_root: Path) -> bool:
    return (repo_root / rel_path).is_file()


def semantic_errors(data: dict, path: Path, repo_root: Path) -> list[str]:
    errors: list[str] = []

    validation_status = str(data.get("validation_status", ""))
    commands = data.get("commands", []) or []
    checks = data.get("checks", []) or []
    does_not_establish = data.get("does_not_establish", []) or []
    known_limitations = data.get("known_limitations", []) or []

    # --- mandatory anti-overclaim disclaimers --------------------------------
    declared = {str(item).strip().lower() for item in does_not_establish}
    missing_disclaimers = [d for d in MANDATORY_DISCLAIMERS if d not in declared]
    if missing_disclaimers:
        errors.append(
            format_error(
                "MISSING_DOES_NOT_ESTABLISH",
                path,
                "does_not_establish must include the mandatory disclaimers; missing: "
                + ", ".join(missing_disclaimers),
            )
        )

    # --- path escape + existence (implementation_path) -----------------------
    impl_path = str(data.get("implementation_path", "")).strip()
    if impl_path:
        if _resolves_outside_repo(impl_path, repo_root):
            errors.append(
                format_error(
                    "RUNTIME_EVIDENCE_PATH_ESCAPE",
                    path,
                    f"implementation_path '{impl_path}' resolves outside the repo root.",
                )
            )
        elif not (repo_root / impl_path).is_dir():
            errors.append(
                format_error(
                    "IMPLEMENTATION_PATH_NOT_FOUND",
                    path,
                    f"implementation_path '{impl_path}' is not an existing directory.",
                )
            )

    # --- commands: path escape + output existence ----------------------------
    for command in commands:
        if not isinstance(command, dict):
            continue
        cmd_id = str(command.get("id", "<missing>"))
        out = str(command.get("output_artifact", "")).strip()
        if not out:
            continue
        if _resolves_outside_repo(out, repo_root):
            errors.append(
                format_error(
                    "RUNTIME_EVIDENCE_PATH_ESCAPE",
                    path,
                    f"command '{cmd_id}' output_artifact '{out}' resolves outside the repo root.",
                )
            )
            continue
        # A command that actually ran (exit_code != null) must have archived output.
        if command.get("exit_code") is not None and not _exists(out, repo_root):
            errors.append(
                format_error(
                    "COMMAND_OUTPUT_NOT_FOUND",
                    path,
                    f"command '{cmd_id}' ran (exit_code != null) but output_artifact "
                    f"'{out}' does not exist.",
                )
            )

    # --- checks: path escape + evidence existence ----------------------------
    for check in checks:
        if not isinstance(check, dict):
            continue
        check_id = str(check.get("id", "<missing>"))
        status = str(check.get("status", ""))
        ev = str(check.get("evidence_artifact", "")).strip()
        if not ev:
            continue
        if _resolves_outside_repo(ev, repo_root):
            errors.append(
                format_error(
                    "RUNTIME_EVIDENCE_PATH_ESCAPE",
                    path,
                    f"check '{check_id}' evidence_artifact '{ev}' resolves outside the repo root.",
                )
            )
            continue
        if status in EVIDENCE_REQUIRED_STATUSES and not _exists(ev, repo_root):
            errors.append(
                format_error(
                    "EVIDENCE_ARTIFACT_NOT_FOUND",
                    path,
                    f"check '{check_id}' (status={status}) evidence_artifact "
                    f"'{ev}' does not exist.",
                )
            )

    # --- pass consistency ----------------------------------------------------
    if validation_status == "pass":
        evidenced_pass_checks = 0
        for check in checks:
            if not isinstance(check, dict):
                continue
            check_id = str(check.get("id", "<missing>"))
            status = str(check.get("status", ""))
            ev = str(check.get("evidence_artifact", "")).strip()
            if status != "pass":
                errors.append(
                    format_error(
                        "PASS_WITH_NON_PASS_CHECK",
                        path,
                        f"validation_status=pass but check '{check_id}' has status '{status}'.",
                    )
                )
            elif ev and not _resolves_outside_repo(ev, repo_root) and _exists(ev, repo_root):
                evidenced_pass_checks += 1

        for command in commands:
            if not isinstance(command, dict):
                continue
            cmd_id = str(command.get("id", "<missing>"))
            out = str(command.get("output_artifact", "")).strip()
            if not out or _resolves_outside_repo(out, repo_root):
                continue
            if not _exists(out, repo_root):
                errors.append(
                    format_error(
                        "PASS_WITH_MISSING_COMMAND_OUTPUT",
                        path,
                        f"validation_status=pass but command '{cmd_id}' output_artifact "
                        f"'{out}' is missing.",
                    )
                )

        if evidenced_pass_checks == 0:
            errors.append(
                format_error(
                    "STRONG_CLAIM_WITHOUT_RUNTIME_EVIDENCE",
                    path,
                    "validation_status=pass requires at least one passing check with an "
                    "existing evidence artifact.",
                )
            )
    else:
        # --- non-pass requires explicit limitations --------------------------
        if not [item for item in known_limitations if str(item).strip()]:
            errors.append(
                format_error(
                    "NON_PASS_REQUIRES_LIMITATIONS",
                    path,
                    f"validation_status='{validation_status}' requires at least one "
                    f"explicit known_limitations entry.",
                )
            )

    return errors


def validate_file(
    path: Path,
    validator: Draft202012Validator,
    repo_root: Path | None = None,
) -> tuple[int, list[str]]:
    effective_root = repo_root if repo_root is not None else REPO_ROOT
    try:
        data = load_yaml(path)
    except (FileNotFoundError, ValueError) as exc:
        return 2, [f"ERROR path={display_path(path)}: {exc}"]

    errors = schema_errors(validator, data, path)
    if errors:
        return 2, errors

    semantic = semantic_errors(data, path, effective_root)
    if semantic:
        return 1, semantic
    return 0, []


def discover_gates(repo_root: Path) -> list[Path]:
    experiments_dir = repo_root / "experiments"
    if not experiments_dir.is_dir():
        return []
    return sorted(experiments_dir.glob(GATE_GLOB))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate runtime-evidence gate artifacts."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="runtime-evidence-gate YAML files (default: discover all under experiments/).",
    )
    args = parser.parse_args(argv)

    try:
        validator = load_schema_validator()
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        return 2

    if args.paths:
        paths = [
            Path(raw) if Path(raw).is_absolute() else (REPO_ROOT / raw)
            for raw in args.paths
        ]
    else:
        paths = discover_gates(REPO_ROOT)
        if not paths:
            print("ℹ️ No runtime-evidence gates found; runtime-evidence-gate validation skipped.")
            return 0

    highest_exit_code = 0
    for path in paths:
        exit_code, errors = validate_file(path, validator)
        highest_exit_code = max(highest_exit_code, exit_code)
        for error in errors:
            print(error)
        if exit_code == 0:
            print(f"✅ {display_path(path)}")

    return highest_exit_code


if __name__ == "__main__":
    sys.exit(main())
