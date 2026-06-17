#!/usr/bin/env python3
"""validate_result_assessment_readiness.py — Validator for result-assessment-readiness gates.

A result-assessment-readiness gate
(``experiments/<series>/results/result-assessment-readiness.yml``) records, for a
series, whether a formal ``result_assessment`` is currently allowed. It does NOT
decide which model or approach is better; it only records ``readiness_status``,
``result_assessment_allowed``, ``comparison_ready``, the open blockers, and an
anti-overclaim allowed/disallowed claim boundary.

This validator complements — it does not replace — the runtime-evidence gate
(``validate_runtime_evidence_gate.py``). A runtime-evidence gate records that an
implementation *ran*; this gate records whether the series may *interpret* those
runs as a comparison result. Runtime evidence is a prerequisite, not a verdict.

Enforced semantic rules (exit 1):
  READINESS_BLOCKED_REQUIRES_FALSE_ALLOWED
                                   readiness_status=blocked but result_assessment_allowed
                                   or comparison_ready is true.
  READINESS_READY_REQUIRES_NO_OPEN_BLOCKERS
                                   readiness_status=ready but a blocker is open / blocking.
  BLOCKED_REQUIRES_OPEN_BLOCKER    readiness_status=blocked but no blocker has status=open.
  ALLOWED_DISALLOWED_CLAIM_OVERLAP allowed_claims and disallowed_claims overlap.
  MISSING_MANDATORY_DISALLOWED_CLAIM
                                   disallowed_claims omits a mandatory non-claim.
  EVIDENCE_PATH_NOT_FOUND          a referenced evidence path does not exist.
  EVIDENCE_PATH_ESCAPE             a referenced evidence path resolves outside the repo.
  PARTIAL_RUNTIME_GATE_BLOCKS_READY
                                   a referenced runtime gate is not pass (e.g. partial),
                                   but this artifact claims ready / result_assessment_allowed.
  ASSESSMENT_ALLOWED_REQUIRES_READY
                                   result_assessment_allowed=true but readiness_status != ready.
  READINESS_READY_REQUIRES_ASSESSMENT_ALLOWED
                                   readiness_status=ready but result_assessment_allowed != true.
  COMPARISON_READY_REQUIRES_ASSESSMENT_ALLOWED
                                   comparison_ready=true but readiness is not ready + allowed.
  OPEN_OR_BLOCKING_BLOCKER_REQUIRES_EVIDENCE
                                   an open or blocking blocker carries no evidence.
  UNKNOWN_CHALLENGE_VERSION        challenge_version has no benchmarks/challenges/<v>.md file.

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
        "ERROR: Missing dependencies for result-assessment-readiness validation. "
        "Install PyYAML and jsonschema.",
        file=sys.stderr,
    )
    raise SystemExit(2) from exc


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCHEMA_PATH = REPO_ROOT / "schemas" / "result-assessment-readiness.v1.schema.json"

# Baseline anti-overclaim non-claims every readiness gate must carry. A readiness
# gate records whether interpretation is allowed; it must never imply quality,
# comparison, condition effect, outcome/adoption/promotion, production/security
# readiness, or externally attested model independence.
MANDATORY_DISALLOWED_CLAIMS = (
    "model_quality",
    "comparative_superiority",
    "condition_effect",
    "outcome_upgrade",
    "adoption_readiness",
    "promotion_readiness",
    "production_readiness",
    "security_readiness",
    "absence_of_regressions",
    "external_model_independence",
)

READINESS_GLOB = "*/results/result-assessment-readiness.yml"
BENCHMARK_CHALLENGES_DIRNAME = ("benchmarks", "challenges")
DRIVE_LETTER_RE = re.compile(r"^[A-Za-z]:")
RUNTIME_GATE_STATUS_KEY = "validation_status"


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
    ``(None, code)`` where ``code`` is "ESCAPE" (absolute / drive-letter /
    backslash / lexical ``..`` / symlink leading out of repo / otherwise resolves
    outside root) or "NOT_FOUND" (repo-internal but missing).

    Mirrors the helper in validate_runtime_evidence_gate.py; kept small and local
    rather than shared to avoid coupling the two validators.
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
        lax = candidate.resolve(strict=False)
        return (None, "NOT_FOUND") if _inside(lax, root) else (None, "ESCAPE")
    except (OSError, RuntimeError):
        return None, "ESCAPE"

    if not _inside(resolved, root):
        return None, "ESCAPE"
    if must_exist and not resolved.exists():
        return None, "NOT_FOUND"
    return resolved, None


def _iter_evidence_refs(data: dict) -> list[tuple[str, str]]:
    """Yield (location_label, path) for every referenced evidence path.

    Covers the top-level ``evidence`` list and each ``blockers[].evidence`` list.
    """
    refs: list[tuple[str, str]] = []
    for item in data.get("evidence", []) or []:
        if isinstance(item, str) and item.strip():
            refs.append(("evidence", item.strip()))
    for blocker in data.get("blockers", []) or []:
        if not isinstance(blocker, dict):
            continue
        blocker_id = str(blocker.get("id", "<missing>"))
        for item in blocker.get("evidence", []) or []:
            if isinstance(item, str) and item.strip():
                refs.append((f"blocker '{blocker_id}' evidence", item.strip()))
    return refs


def _runtime_gate_status(resolved: Path) -> str | None:
    """Return the validation_status of a referenced runtime-evidence gate, or None.

    A referenced file is treated as a runtime gate when it is a YAML document that
    carries a top-level ``validation_status`` field. Anything else (markdown,
    plain text, YAML without that field) is not a runtime gate and returns None.
    """
    if resolved.suffix.lower() not in (".yml", ".yaml"):
        return None
    try:
        loaded = yaml.safe_load(resolved.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return None
    if not isinstance(loaded, dict):
        return None
    status = loaded.get(RUNTIME_GATE_STATUS_KEY)
    return status if isinstance(status, str) else None


def challenge_version_error(data: dict, path: Path, repo_root: Path) -> str | None:
    """Return an UNKNOWN_CHALLENGE_VERSION error string, or None.

    Existence check only: ``benchmarks/challenges/<challenge_version>.md`` must
    exist (no frontmatter matching in this contract). A path-escape guard keeps a
    crafted challenge_version from pointing outside benchmarks/challenges/.
    """
    challenge_version = str(data.get("challenge_version", "")).strip()
    if not challenge_version:
        return None  # schema already requires a non-empty value
    challenges_dir = (repo_root / Path(*BENCHMARK_CHALLENGES_DIRNAME)).resolve()
    candidate = challenges_dir / f"{challenge_version}.md"
    try:
        inside = _inside(candidate.resolve(strict=False), challenges_dir)
    except (OSError, RuntimeError):
        inside = False
    if not inside or not candidate.is_file():
        return format_error(
            "UNKNOWN_CHALLENGE_VERSION",
            path,
            f"challenge_version '{challenge_version}' has no challenge file at "
            f"benchmarks/challenges/{challenge_version}.md.",
        )
    return None


def semantic_errors(data: dict, path: Path, repo_root: Path) -> list[str]:
    errors: list[str] = []

    readiness_status = str(data.get("readiness_status", ""))
    result_assessment_allowed = bool(data.get("result_assessment_allowed", False))
    comparison_ready = bool(data.get("comparison_ready", False))
    blockers = data.get("blockers", []) or []
    allowed_claims = data.get("allowed_claims", []) or []
    disallowed_claims = data.get("disallowed_claims", []) or []

    # --- blocked consistency -------------------------------------------------
    if readiness_status == "blocked":
        if result_assessment_allowed or comparison_ready:
            errors.append(
                format_error(
                    "READINESS_BLOCKED_REQUIRES_FALSE_ALLOWED",
                    path,
                    "readiness_status=blocked requires result_assessment_allowed=false and "
                    f"comparison_ready=false (got result_assessment_allowed="
                    f"{str(result_assessment_allowed).lower()}, comparison_ready="
                    f"{str(comparison_ready).lower()}).",
                )
            )
        has_open_blocker = any(
            isinstance(b, dict) and str(b.get("status", "")) == "open" for b in blockers
        )
        if not has_open_blocker:
            errors.append(
                format_error(
                    "BLOCKED_REQUIRES_OPEN_BLOCKER",
                    path,
                    "readiness_status=blocked requires at least one blocker with status=open.",
                )
            )

    # --- ready consistency ---------------------------------------------------
    if readiness_status == "ready":
        for blocker in blockers:
            if not isinstance(blocker, dict):
                continue
            blocker_id = str(blocker.get("id", "<missing>"))
            status = str(blocker.get("status", ""))
            severity = str(blocker.get("severity", ""))
            if status == "open" or severity == "blocking":
                errors.append(
                    format_error(
                        "READINESS_READY_REQUIRES_NO_OPEN_BLOCKERS",
                        path,
                        f"readiness_status=ready but blocker '{blocker_id}' is still "
                        f"status={status or '<missing>'} / severity={severity or '<missing>'}.",
                    )
                )

    # --- boolean coupling: the three readiness flags must not contradict ------
    if result_assessment_allowed and readiness_status != "ready":
        errors.append(
            format_error(
                "ASSESSMENT_ALLOWED_REQUIRES_READY",
                path,
                "result_assessment_allowed=true requires readiness_status=ready "
                f"(got readiness_status={readiness_status!r}).",
            )
        )
    if readiness_status == "ready" and not result_assessment_allowed:
        errors.append(
            format_error(
                "READINESS_READY_REQUIRES_ASSESSMENT_ALLOWED",
                path,
                "readiness_status=ready requires result_assessment_allowed=true.",
            )
        )
    if comparison_ready and not (readiness_status == "ready" and result_assessment_allowed):
        errors.append(
            format_error(
                "COMPARISON_READY_REQUIRES_ASSESSMENT_ALLOWED",
                path,
                "comparison_ready=true requires readiness_status=ready and "
                f"result_assessment_allowed=true (got readiness_status={readiness_status!r}, "
                f"result_assessment_allowed={str(result_assessment_allowed).lower()}).",
            )
        )

    # --- open / blocking blockers must carry evidence ------------------------
    for blocker in blockers:
        if not isinstance(blocker, dict):
            continue
        status = str(blocker.get("status", ""))
        severity = str(blocker.get("severity", ""))
        if status != "open" and severity != "blocking":
            continue
        blocker_id = str(blocker.get("id", "<missing>"))
        blocker_evidence = blocker.get("evidence", []) or []
        has_evidence = any(
            isinstance(item, str) and item.strip() for item in blocker_evidence
        )
        if not has_evidence:
            errors.append(
                format_error(
                    "OPEN_OR_BLOCKING_BLOCKER_REQUIRES_EVIDENCE",
                    path,
                    f"blocker '{blocker_id}' is open/blocking "
                    f"(status={status or '<missing>'}, severity={severity or '<missing>'}) "
                    "but carries no evidence.",
                )
            )

    # --- challenge_version is anchored to a real benchmark challenge ----------
    challenge_error = challenge_version_error(data, path, repo_root)
    if challenge_error is not None:
        errors.append(challenge_error)

    # --- mandatory disallowed claims -----------------------------------------
    declared_disallowed = {str(item).strip().lower() for item in disallowed_claims}
    missing_disallowed = [d for d in MANDATORY_DISALLOWED_CLAIMS if d not in declared_disallowed]
    if missing_disallowed:
        errors.append(
            format_error(
                "MISSING_MANDATORY_DISALLOWED_CLAIM",
                path,
                "disallowed_claims must include the mandatory non-claims; missing: "
                + ", ".join(missing_disallowed),
            )
        )

    # --- allowed / disallowed overlap ----------------------------------------
    declared_allowed = {str(item).strip().lower() for item in allowed_claims}
    overlap = sorted(declared_allowed & declared_disallowed)
    if overlap:
        errors.append(
            format_error(
                "ALLOWED_DISALLOWED_CLAIM_OVERLAP",
                path,
                "allowed_claims and disallowed_claims must not overlap; overlapping: "
                + ", ".join(overlap),
            )
        )

    # --- evidence path escape + existence (resolved once, reused below) -------
    resolved_refs: list[tuple[str, str, Path | None, str | None]] = []
    for label, rel in _iter_evidence_refs(data):
        resolved, code = resolve_repo_relative_path(rel, repo_root, must_exist=True)
        resolved_refs.append((label, rel, resolved, code))
        if code == "ESCAPE":
            errors.append(
                format_error(
                    "EVIDENCE_PATH_ESCAPE",
                    path,
                    f"{label} path '{rel}' resolves outside the repo root.",
                )
            )
        elif code == "NOT_FOUND":
            errors.append(
                format_error(
                    "EVIDENCE_PATH_NOT_FOUND",
                    path,
                    f"{label} path '{rel}' does not exist.",
                )
            )

    # --- partial runtime gate must not be read as ready ----------------------
    # A referenced runtime-evidence gate that is not 'pass' (e.g. partial) cannot
    # back a ready / result_assessment_allowed=true claim. Runtime contact is a
    # prerequisite, not a comparison result. Reuses the resolution above; only
    # already-resolved, existing files are inspected.
    if readiness_status == "ready" or result_assessment_allowed:
        for label, rel, resolved, code in resolved_refs:
            if code is not None or resolved is None or not resolved.is_file():
                continue
            gate_status = _runtime_gate_status(resolved)
            if gate_status is not None and gate_status != "pass":
                errors.append(
                    format_error(
                        "PARTIAL_RUNTIME_GATE_BLOCKS_READY",
                        path,
                        f"{label} references runtime gate '{rel}' with "
                        f"validation_status={gate_status!r}; this artifact must not set "
                        f"readiness_status=ready or result_assessment_allowed=true while a "
                        f"referenced runtime gate is not 'pass'.",
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
    return sorted(experiments_dir.glob(READINESS_GLOB))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate result-assessment-readiness gate artifacts."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="readiness YAML files (default: discover all under experiments/).",
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
            print(
                "ℹ️ No result-assessment-readiness gates found; "
                "result-assessment-readiness validation skipped."
            )
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
        f"Result-assessment-readiness gates: checked={checked}, passed={passed}, "
        f"errors={checked - passed}"
    )
    return highest_exit_code


if __name__ == "__main__":
    sys.exit(main())
