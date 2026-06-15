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
  UNKNOWN_CHALLENGE_VERSION        challenge_version has no benchmarks/challenges/<v>.md file.
  CHALLENGE_VERSION_MISMATCH       the challenge file's frontmatter contradicts the gate.
  RUNTIME_EVIDENCE_PATH_ESCAPE     a referenced path resolves outside the repo.
  IMPLEMENTATION_PATH_NOT_FOUND    implementation_path is not an existing directory.
  COMMAND_OUTPUT_NOT_FOUND         an executed command (exit_code != null) has no archived output.
  COMMAND_EXIT_CODE_MISMATCH       a command's exit_code disagrees with the archived 'Exit Code: N'.
  EVIDENCE_ARTIFACT_NOT_FOUND      a pass/fail/partial check has no existing evidence artifact.
  PASS_WITH_NON_PASS_CHECK         validation_status=pass but a check is not pass.
  PASS_WITH_NONZERO_COMMAND        validation_status=pass but a command exited non-zero.
  PASS_WITH_UNEXECUTED_COMMAND     validation_status=pass but a command was not executed (exit_code null).
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
import re
import sys
from pathlib import Path, PurePosixPath

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
BENCHMARK_CHALLENGES_DIRNAME = ("benchmarks", "challenges")

# Baseline anti-overclaim disclaimers every runtime-evidence gate must carry.
# A runtime-evidence gate records execution; it must never imply quality,
# comparison, outcome, promotion/adoption, production/security readiness, or
# externally attested model independence.
MANDATORY_DISCLAIMERS = (
    "model_quality",
    "comparative_superiority",
    "adoption_readiness",
    "production_correctness",
    "absence_of_regressions",
    "security_readiness",
    "promotion_readiness",
    "outcome_assessment",
    "external_model_independence",
)

# Check statuses for which an evidence artifact must already exist on disk.
EVIDENCE_REQUIRED_STATUSES = {"pass", "fail", "partial"}

GATE_GLOB = "*/artifacts/*/runtime-evidence-gate.yml"
FRONTMATTER_DELIM = "---"
DRIVE_LETTER_RE = re.compile(r"^[A-Za-z]:")
# Matches an archived 'Exit Code: N' line (case-insensitive, whole line).
EXIT_CODE_RE = re.compile(r"^[ \t]*exit code:[ \t]*(-?\d+)[ \t]*$", re.IGNORECASE | re.MULTILINE)


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


def parse_frontmatter(path: Path) -> dict:
    """Return the YAML frontmatter mapping of a Markdown file (``{}`` if absent).

    Mirrors the lightweight frontmatter parsing used by sibling docmeta scripts
    (see ``validate_challenge_versions.py``). Intentionally a simple reader: no
    new dependency, no full Markdown parser.
    """
    text = path.read_text(encoding="utf-8")
    if not text.startswith(FRONTMATTER_DELIM):
        return {}
    end = text.find(f"\n{FRONTMATTER_DELIM}", len(FRONTMATTER_DELIM))
    if end == -1:
        return {}
    raw = text[len(FRONTMATTER_DELIM):end]
    data = yaml.safe_load(raw) or {}
    return data if isinstance(data, dict) else {}


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


def _inside(candidate: Path, root: Path) -> bool:
    try:
        candidate.relative_to(root)
        return True
    except ValueError:
        return False


def resolve_repo_relative_path(
    rel_path: str, repo_root: Path, *, must_exist: bool
) -> tuple[Path | None, str | None]:
    """Resolve a repo-relative POSIX path safely (centralized path handling).

    Returns ``(resolved_path, None)`` when the path is repo-internal (and, when
    ``must_exist`` is True, exists after symlink resolution). On failure returns
    ``(None, code)`` where ``code`` is one of:

      "ESCAPE"     absolute / drive-letter / backslash / lexical ``..`` /
                   symlink leading out of repo / otherwise resolves outside root.
      "NOT_FOUND"  repo-internal but missing (only when ``must_exist`` is True).

    Callers map these generic codes to stable rule ids appropriate to the field
    (e.g. RUNTIME_EVIDENCE_PATH_ESCAPE, IMPLEMENTATION_PATH_NOT_FOUND).
    """
    text = str(rel_path).strip()
    if not text:
        return None, "ESCAPE"
    # Lexical rejections (defense-in-depth; the schema pattern also blocks these).
    if text.startswith("/") or DRIVE_LETTER_RE.match(text) or "\\" in text:
        return None, "ESCAPE"
    if ".." in PurePosixPath(text).parts:
        return None, "ESCAPE"

    root = repo_root.resolve()
    candidate = root / text
    try:
        resolved = candidate.resolve(strict=must_exist)
    except FileNotFoundError:
        # must_exist=True and the path is missing; classify inside vs escape.
        lax = candidate.resolve(strict=False)
        return (None, "NOT_FOUND") if _inside(lax, root) else (None, "ESCAPE")
    except (OSError, RuntimeError):
        return None, "ESCAPE"

    if not _inside(resolved, root):
        return None, "ESCAPE"
    if must_exist and not resolved.exists():
        return None, "NOT_FOUND"
    return resolved, None


def read_archived_exit_code(path: Path) -> int | None:
    """Return the integer from the last archived 'Exit Code: N' line, or None.

    When the captured output does not carry such a line, no mismatch check is
    applied (returns None).
    """
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    matches = EXIT_CODE_RE.findall(text)
    if not matches:
        return None
    try:
        return int(matches[-1])
    except ValueError:
        return None


def challenge_version_errors(data: dict, path: Path, repo_root: Path) -> list[str]:
    """Validate challenge_version against benchmarks/challenges/<version>.md."""
    errors: list[str] = []
    challenge_version = str(data.get("challenge_version", "")).strip()
    challenge_id = str(data.get("challenge_id", "")).strip()
    if not challenge_version:
        return errors  # schema already requires a non-empty value

    challenges_dir = (repo_root / Path(*BENCHMARK_CHALLENGES_DIRNAME)).resolve()
    candidate = challenges_dir / f"{challenge_version}.md"
    try:
        inside = _inside(candidate.resolve(strict=False), challenges_dir)
    except (OSError, RuntimeError):
        inside = False
    if not inside or not candidate.is_file():
        errors.append(
            format_error(
                "UNKNOWN_CHALLENGE_VERSION",
                path,
                f"challenge_version '{challenge_version}' has no challenge file at "
                f"benchmarks/challenges/{challenge_version}.md.",
            )
        )
        return errors

    try:
        front = parse_frontmatter(candidate)
    except (OSError, yaml.YAMLError) as exc:
        errors.append(
            format_error(
                "UNKNOWN_CHALLENGE_VERSION",
                path,
                f"challenge file for '{challenge_version}' could not be parsed: {exc}.",
            )
        )
        return errors

    fm_challenge_id = front.get("challenge_id")
    if (
        challenge_id
        and isinstance(fm_challenge_id, str)
        and fm_challenge_id.strip()
        and fm_challenge_id.strip() != challenge_id
    ):
        errors.append(
            format_error(
                "CHALLENGE_VERSION_MISMATCH",
                path,
                f"challenge_id '{challenge_id}' does not match the challenge file's "
                f"challenge_id '{fm_challenge_id.strip()}' "
                f"(benchmarks/challenges/{challenge_version}.md).",
            )
        )
        return errors

    fm_challenge_version = front.get("challenge_version")
    if (
        isinstance(fm_challenge_version, str)
        and fm_challenge_version.strip()
        and fm_challenge_version.strip() != challenge_version
    ):
        errors.append(
            format_error(
                "CHALLENGE_VERSION_MISMATCH",
                path,
                f"challenge_version '{challenge_version}' does not match the challenge "
                f"file's challenge_version '{fm_challenge_version.strip()}'.",
            )
        )
        return errors

    fm_version = front.get("version")
    if isinstance(fm_version, str) and fm_version.strip():
        version = fm_version.strip()
        combined = f"{challenge_id}-{version}" if challenge_id else None
        if version != challenge_version and combined != challenge_version:
            errors.append(
                format_error(
                    "CHALLENGE_VERSION_MISMATCH",
                    path,
                    f"challenge_version '{challenge_version}' is not reconcilable with the "
                    f"challenge file's version '{version}' "
                    f"(expected '{version}' or '{combined}').",
                )
            )

    return errors


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

    # --- challenge version is anchored to a real benchmark challenge ----------
    errors.extend(challenge_version_errors(data, path, repo_root))

    # --- path escape + existence (implementation_path) -----------------------
    impl_path = str(data.get("implementation_path", "")).strip()
    if impl_path:
        resolved, code = resolve_repo_relative_path(impl_path, repo_root, must_exist=False)
        if code == "ESCAPE":
            errors.append(
                format_error(
                    "RUNTIME_EVIDENCE_PATH_ESCAPE",
                    path,
                    f"implementation_path '{impl_path}' resolves outside the repo root.",
                )
            )
        elif resolved is None or not resolved.is_dir():
            errors.append(
                format_error(
                    "IMPLEMENTATION_PATH_NOT_FOUND",
                    path,
                    f"implementation_path '{impl_path}' is not an existing directory.",
                )
            )

    # --- commands: path escape + output existence + exit-code agreement ------
    for command in commands:
        if not isinstance(command, dict):
            continue
        cmd_id = str(command.get("id", "<missing>"))
        exit_code = command.get("exit_code")
        out = str(command.get("output_artifact", "")).strip()
        if not out:
            continue
        executed = exit_code is not None
        resolved, code = resolve_repo_relative_path(out, repo_root, must_exist=executed)
        if code == "ESCAPE":
            errors.append(
                format_error(
                    "RUNTIME_EVIDENCE_PATH_ESCAPE",
                    path,
                    f"command '{cmd_id}' output_artifact '{out}' resolves outside the repo root.",
                )
            )
            continue
        if code == "NOT_FOUND":
            # Only reached when executed (must_exist=True): a command that ran
            # must have archived output.
            errors.append(
                format_error(
                    "COMMAND_OUTPUT_NOT_FOUND",
                    path,
                    f"command '{cmd_id}' ran (exit_code != null) but output_artifact "
                    f"'{out}' does not exist.",
                )
            )
            continue
        # Cross-check the YAML exit_code against the archived 'Exit Code: N' line.
        if executed and resolved is not None:
            archived = read_archived_exit_code(resolved)
            if archived is not None and archived != exit_code:
                errors.append(
                    format_error(
                        "COMMAND_EXIT_CODE_MISMATCH",
                        path,
                        f"command '{cmd_id}' declares exit_code {exit_code} but its archived "
                        f"output '{out}' records 'Exit Code: {archived}'.",
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
        evidence_required = status in EVIDENCE_REQUIRED_STATUSES
        _resolved, code = resolve_repo_relative_path(ev, repo_root, must_exist=evidence_required)
        if code == "ESCAPE":
            errors.append(
                format_error(
                    "RUNTIME_EVIDENCE_PATH_ESCAPE",
                    path,
                    f"check '{check_id}' evidence_artifact '{ev}' resolves outside the repo root.",
                )
            )
            continue
        if code == "NOT_FOUND":
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
                continue
            resolved, code = resolve_repo_relative_path(ev, repo_root, must_exist=False)
            if code is None and resolved is not None and resolved.is_file():
                evidenced_pass_checks += 1

        for command in commands:
            if not isinstance(command, dict):
                continue
            cmd_id = str(command.get("id", "<missing>"))
            exit_code = command.get("exit_code")
            out = str(command.get("output_artifact", "")).strip()
            if exit_code is None:
                errors.append(
                    format_error(
                        "PASS_WITH_UNEXECUTED_COMMAND",
                        path,
                        f"validation_status=pass but command '{cmd_id}' was not executed "
                        f"(exit_code is null).",
                    )
                )
            elif exit_code != 0:
                errors.append(
                    format_error(
                        "PASS_WITH_NONZERO_COMMAND",
                        path,
                        f"validation_status=pass but command '{cmd_id}' exited {exit_code} "
                        f"(non-zero).",
                    )
                )
            if not out:
                continue
            resolved, code = resolve_repo_relative_path(out, repo_root, must_exist=False)
            if code == "ESCAPE":
                continue  # already reported in the commands loop
            if resolved is None or not resolved.is_file():
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
    passed = 0
    for path in paths:
        exit_code, errors = validate_file(path, validator)
        highest_exit_code = max(highest_exit_code, exit_code)
        for error in errors:
            print(error)
        if exit_code == 0:
            passed += 1
            print(f"✅ {display_path(path)}")

    checked = len(paths)
    print(
        f"Runtime-evidence gates: checked={checked}, passed={passed}, "
        f"errors={checked - passed}"
    )
    return highest_exit_code


if __name__ == "__main__":
    sys.exit(main())
