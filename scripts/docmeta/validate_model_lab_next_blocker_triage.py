#!/usr/bin/env python3
"""validate_model_lab_next_blocker_triage.py — Validator for Model-Lab next-blocker-triage artifacts.

A next-blocker-triage artifact
(``experiments/<series>/results/next-blocker-triage.yml``) prioritizes the
remaining result-assessment blockers of a Model-Lab series and recommends which
blocker to address next. It is a methodological prioritization only: it does NOT
resolve any blocker, does NOT remediate dependency risk, does NOT start a new
run, does NOT allow a result_assessment, and does NOT make the series
comparison-ready.

This validator complements — it does not replace — the runtime-evidence gate
(``validate_runtime_evidence_gate.py``), the result-assessment-readiness gate
(``validate_result_assessment_readiness.py``), and the dependency-risk-caveat
scope (``validate_dependency_risk_caveat_scope.py``). A runtime gate records that
an implementation *ran*; the readiness gate records whether the series may
*interpret* those runs as a comparison result; the dependency-risk scope records
that a dependency caveat has been *classified* (not solved); this triage records
which still-open blocker should be handled *next*. Prioritizing a blocker is not
resolving it, and a triage never unblocks a result assessment.

Enforced semantic rules (exit 1):
  TRIAGE_REQUIRES_BLOCKED_ASSESSMENT
                                   no referenced source_evidence of kind
                                   'readiness_gate' is readable and confirms a
                                   blocked assessment (readiness_status=blocked and
                                   result_assessment_allowed not true). A triage of
                                   "what is still blocking" requires that the
                                   assessment is, in fact, still blocked.
  TRIAGE_REQUIRES_FALSE_RESULT_ASSESSMENT_ALLOWED
                                   result_assessment_allowed_after_triage is true. A
                                   triage prioritizes blockers; it does not authorize
                                   a result assessment.
  TRIAGE_REQUIRES_FALSE_COMPARISON_READY
                                   comparison_ready_after_triage is true. A triage
                                   does not make the series comparison-ready.
  TRIAGE_REQUIRES_RECOMMENDED_NEXT_TASK
                                   recommended_next_task is missing or lacks a
                                   non-empty id / target_blocker.
  TRIAGE_REQUIRES_ALL_KNOWN_BLOCKERS
                                   remaining_blockers omits a known remaining
                                   blocker id.
  SOURCE_EVIDENCE_PATH_NOT_FOUND   a referenced source_evidence path does not exist.
  SOURCE_EVIDENCE_PATH_ESCAPE      a referenced source_evidence path resolves outside the repo.
  MISSING_MANDATORY_DOES_NOT_ESTABLISH
                                   does_not_establish omits a mandatory non-claim.

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
        "ERROR: Missing dependencies for model-lab-next-blocker-triage validation. "
        "Install PyYAML and jsonschema.",
        file=sys.stderr,
    )
    raise SystemExit(2) from exc


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCHEMA_PATH = REPO_ROOT / "schemas" / "model-lab-next-blocker-triage.v1.schema.json"

# The canonical remaining Model-Lab result-assessment blockers. Source of truth:
# experiments/2026-05-31_model-lab-replication-series/results/dependency-risk-caveat-scope.yml
# (remaining_blockers). A triage must cover every one of them so no open blocker
# silently drops out of the prioritization.
KNOWN_BLOCKERS = (
    "dependency_risk_remediation_not_performed",
    "weak_condition_contrast",
    "external_independence_not_attested",
    "no_external_independent_auditor_comparison",
)

# Baseline anti-overclaim non-claims every triage must carry. A triage prioritizes
# blockers; it must never imply that a result assessment is allowed, that the
# series is comparison-ready, that quality/comparison/condition-effect follow, or
# that external independence / external auditor comparison / dependency-risk
# remediation have been achieved.
MANDATORY_DOES_NOT_ESTABLISH = (
    "result_assessment_allowed",
    "comparison_ready",
    "security_readiness",
    "production_readiness",
    "model_quality",
    "comparative_superiority",
    "condition_effect",
    "external_model_independence",
    "external_auditor_comparison_completed",
    "dependency_risk_remediated",
)

TRIAGE_GLOB = "*/results/next-blocker-triage.yml"
READINESS_GATE_KIND = "readiness_gate"
READINESS_STATUS_KEY = "readiness_status"
RESULT_ASSESSMENT_ALLOWED_KEY = "result_assessment_allowed"
DRIVE_LETTER_RE = re.compile(r"^[A-Za-z]:")


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

    Mirrors the helper in validate_dependency_risk_caveat_scope.py; kept small and
    local rather than shared to avoid coupling the validators.
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


def _source_evidence_entries(data: dict) -> list[dict]:
    return [item for item in (data.get("source_evidence", []) or []) if isinstance(item, dict)]


def _readiness_blocked_confirmed(data: dict, repo_root: Path) -> bool:
    """Return True if a referenced readiness_gate confirms a blocked assessment.

    Reads each source_evidence entry of kind 'readiness_gate' that resolves to an
    existing, readable YAML document and confirms readiness_status=blocked with
    result_assessment_allowed not true. Mirrors the cross-artifact read in
    validate_result_assessment_readiness.py (which inspects a referenced runtime
    gate's validation_status); here we inspect a referenced readiness gate.
    """
    for entry in _source_evidence_entries(data):
        if str(entry.get("kind", "")) != READINESS_GATE_KIND:
            continue
        rel = str(entry.get("path", "")).strip()
        if not rel:
            continue
        resolved, code = resolve_repo_relative_path(rel, repo_root, must_exist=True)
        if code is not None or resolved is None or not resolved.is_file():
            continue
        if resolved.suffix.lower() not in (".yml", ".yaml"):
            continue
        try:
            loaded = yaml.safe_load(resolved.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError):
            continue
        if not isinstance(loaded, dict):
            continue
        allowed = bool(loaded.get(RESULT_ASSESSMENT_ALLOWED_KEY, False))
        status = str(loaded.get(READINESS_STATUS_KEY, ""))
        if not allowed and status == "blocked":
            return True
    return False


def semantic_errors(data: dict, path: Path, repo_root: Path) -> list[str]:
    errors: list[str] = []

    result_assessment_allowed = bool(data.get("result_assessment_allowed_after_triage", False))
    comparison_ready = bool(data.get("comparison_ready_after_triage", False))
    recommended_next_task = data.get("recommended_next_task")
    remaining_blockers = data.get("remaining_blockers", []) or []
    does_not_establish = data.get("does_not_establish", []) or []

    # --- a triage requires a blocked result assessment -----------------------
    if not _readiness_blocked_confirmed(data, repo_root):
        errors.append(
            format_error(
                "TRIAGE_REQUIRES_BLOCKED_ASSESSMENT",
                path,
                "no source_evidence of kind 'readiness_gate' confirms a blocked "
                f"assessment ({READINESS_STATUS_KEY}=blocked and "
                f"{RESULT_ASSESSMENT_ALLOWED_KEY} not true). A next-blocker triage "
                "is only coherent while a formal result assessment is still blocked.",
            )
        )

    # --- triage must not unblock a result assessment -------------------------
    if result_assessment_allowed:
        errors.append(
            format_error(
                "TRIAGE_REQUIRES_FALSE_RESULT_ASSESSMENT_ALLOWED",
                path,
                "result_assessment_allowed_after_triage must be false; a triage "
                "prioritizes blockers, it does not authorize a result assessment.",
            )
        )

    # --- triage must not make the series comparison-ready --------------------
    if comparison_ready:
        errors.append(
            format_error(
                "TRIAGE_REQUIRES_FALSE_COMPARISON_READY",
                path,
                "comparison_ready_after_triage must be false; a triage does not "
                "make the series comparison-ready.",
            )
        )

    # --- triage must name a recommended next task ----------------------------
    task_id = ""
    target_blocker = ""
    if isinstance(recommended_next_task, dict):
        task_id = str(recommended_next_task.get("id", "")).strip()
        target_blocker = str(recommended_next_task.get("target_blocker", "")).strip()
    if not task_id or not target_blocker:
        errors.append(
            format_error(
                "TRIAGE_REQUIRES_RECOMMENDED_NEXT_TASK",
                path,
                "recommended_next_task must be present with a non-empty id and "
                "target_blocker; a triage's purpose is to name the next step.",
            )
        )

    # --- triage must cover every known remaining blocker ---------------------
    declared_blocker_ids = {
        str(b.get("id", "")).strip()
        for b in remaining_blockers
        if isinstance(b, dict)
    }
    missing_blockers = [b for b in KNOWN_BLOCKERS if b not in declared_blocker_ids]
    if missing_blockers:
        errors.append(
            format_error(
                "TRIAGE_REQUIRES_ALL_KNOWN_BLOCKERS",
                path,
                "remaining_blockers must cover every known remaining blocker; "
                "missing: " + ", ".join(missing_blockers),
            )
        )

    # --- mandatory anti-overclaim non-claims ---------------------------------
    declared = {str(item).strip().lower() for item in does_not_establish}
    missing_mandatory = [d for d in MANDATORY_DOES_NOT_ESTABLISH if d not in declared]
    if missing_mandatory:
        errors.append(
            format_error(
                "MISSING_MANDATORY_DOES_NOT_ESTABLISH",
                path,
                "does_not_establish must include the mandatory non-claims; missing: "
                + ", ".join(missing_mandatory),
            )
        )

    # --- source_evidence path escape + existence -----------------------------
    for entry in _source_evidence_entries(data):
        rel = str(entry.get("path", "")).strip()
        if not rel:
            continue
        _resolved, code = resolve_repo_relative_path(rel, repo_root, must_exist=True)
        if code == "ESCAPE":
            errors.append(
                format_error(
                    "SOURCE_EVIDENCE_PATH_ESCAPE",
                    path,
                    f"source_evidence path '{rel}' resolves outside the repo root.",
                )
            )
        elif code == "NOT_FOUND":
            errors.append(
                format_error(
                    "SOURCE_EVIDENCE_PATH_NOT_FOUND",
                    path,
                    f"source_evidence path '{rel}' does not exist.",
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


def discover_artifacts(repo_root: Path) -> list[Path]:
    experiments_dir = repo_root / "experiments"
    if not experiments_dir.is_dir():
        return []
    return sorted(experiments_dir.glob(TRIAGE_GLOB))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Model-Lab next-blocker-triage artifacts."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="next-blocker-triage YAML files (default: discover all under experiments/).",
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
        paths = discover_artifacts(REPO_ROOT)
        if not paths:
            print(
                "ℹ️ No model-lab-next-blocker-triage artifacts found; "
                "model-lab-next-blocker-triage validation skipped."
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
        f"Model-lab-next-blocker-triage artifacts: checked={checked}, passed={passed}, "
        f"failed={checked - passed}"
    )
    return highest_exit_code


if __name__ == "__main__":
    sys.exit(main())
