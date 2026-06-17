#!/usr/bin/env python3
"""validate_dependency_risk_caveat_scope.py — Validator for dependency-risk-caveat-scope artifacts.

A dependency-risk-caveat-scope artifact
(``experiments/<series>/results/dependency-risk-caveat-scope.yml``) records, for a
series, how a dependency-risk caveat is *scoped for assessment interpretation*. It
deliberately does NOT remediate the risk and does NOT grant security/production
readiness or a result_assessment. It only records ``scope_status``,
``dependency_risk_remediated``, ``result_assessment_allowed_after_scope``,
``comparison_ready_after_scope``, an audit observation, an assessment
interpretation, and an anti-overclaim ``does_not_establish`` boundary.

This validator complements — it does not replace — the runtime-evidence gate
(``validate_runtime_evidence_gate.py``) and the result-assessment-readiness gate
(``validate_result_assessment_readiness.py``). A runtime gate records that an
implementation *ran*; the readiness gate records whether the series may
*interpret* those runs as a comparison result; this scope artifact records that a
dependency-risk caveat has been *classified* (not solved) for that interpretation.
Scoping a risk is not remediating it.

Enforced semantic rules (exit 1):
  DEPENDENCY_RISK_REMEDIATED_OUT_OF_SCOPE
                                   dependency_risk_remediated is true. v1 models only
                                   not-yet-remediated caveats; remediation belongs in
                                   a future separate contract/PR. Fires for any
                                   scope_status.
  REMEDIATION_PERFORMED_OUT_OF_SCOPE
                                   audit_observation.remediation_performed is true. v1
                                   scopes unresolved caveats only; remediation belongs
                                   in a future separate contract/PR.
  SCOPED_NOT_REMEDIATED_REQUIRES_FALSE_REMEDIATED
                                   scope_status=scoped_not_remediated but
                                   dependency_risk_remediated is true.
  SCOPED_NOT_REMEDIATED_BLOCKS_SECURITY_PRODUCTION
                                   scope_status=scoped_not_remediated but
                                   assessment_interpretation security/production
                                   readiness is not 'blocked'.
  SCOPED_NOT_REMEDIATED_BLOCKS_RESULT_ASSESSMENT
                                   scope_status=scoped_not_remediated but
                                   result_assessment/comparison are allowed (either
                                   the *_after_scope booleans or the
                                   assessment_interpretation strings).
  FUNCTIONAL_RUNTIME_EVIDENCE_MUST_NOT_BE_SECURITY_APPROVAL
                                   functional_runtime_evidence is the
                                   "not_invalidated_by_dev_toolchain_audit" reading
                                   but does_not_establish omits a security disclaimer.
  MISSING_MANDATORY_DOES_NOT_ESTABLISH
                                   does_not_establish omits a mandatory non-claim.
  SOURCE_EVIDENCE_PATH_NOT_FOUND   a referenced source_evidence path does not exist.
  SOURCE_EVIDENCE_PATH_ESCAPE      a referenced source_evidence path resolves outside the repo.
  UNKNOWN_CHALLENGE_VERSION        challenge_version has no benchmarks/challenges/<v>.md file.
  AUDIT_EXIT_NONZERO_REQUIRES_NOT_REMEDIATED
                                   audit_observation.audit_exit_code is a non-zero
                                   integer but the artifact marks the risk remediated,
                                   unblocks security/production, or allows
                                   result_assessment/comparison.

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
        "ERROR: Missing dependencies for dependency-risk-caveat-scope validation. "
        "Install PyYAML and jsonschema.",
        file=sys.stderr,
    )
    raise SystemExit(2) from exc


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCHEMA_PATH = REPO_ROOT / "schemas" / "dependency-risk-caveat-scope.v1.schema.json"

# Baseline anti-overclaim non-claims every scope artifact must carry. Scoping a
# dependency risk is classification, not remediation and not approval: the
# artifact must never imply that the dependency tree is safe, that the audit is
# resolved, or that quality/comparison/outcome/adoption/promotion follow.
MANDATORY_DOES_NOT_ESTABLISH = (
    "security_readiness",
    "production_readiness",
    "absence_of_vulnerabilities",
    "dependency_risk_remediated",
    "dependency_tree_safe",
    "supply_chain_safety",
    "production_dependency_health",
    "security_approval",
    "model_quality",
    "comparative_superiority",
    "condition_effect",
    "outcome_upgrade",
    "adoption_readiness",
    "promotion_readiness",
    "absence_of_regressions",
    "external_model_independence",
    "production_correctness",
    "outcome_assessment",
)

# Subset that the "functional runtime evidence is not invalidated by the
# dev-toolchain audit" reading must explicitly disclaim, so that "the audit does
# not retroactively void the runtime checks" can never be read as a security or
# production approval.
SECURITY_DISCLAIMERS_REQUIRED = (
    "security_readiness",
    "production_readiness",
    "absence_of_vulnerabilities",
    "dependency_risk_remediated",
    "security_approval",
)

FUNCTIONAL_RUNTIME_NOT_INVALIDATED = "not_invalidated_by_dev_toolchain_audit"

SCOPE_GLOB = "*/results/dependency-risk-caveat-scope.yml"
BENCHMARK_CHALLENGES_DIRNAME = ("benchmarks", "challenges")
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

    Mirrors the helper in validate_result_assessment_readiness.py; kept small and
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


def _str_field(container: object, key: str) -> str:
    if isinstance(container, dict):
        return str(container.get(key, ""))
    return ""


def semantic_errors(data: dict, path: Path, repo_root: Path) -> list[str]:
    errors: list[str] = []

    scope_status = str(data.get("scope_status", ""))
    dependency_risk_remediated = bool(data.get("dependency_risk_remediated", False))
    result_assessment_allowed = bool(data.get("result_assessment_allowed_after_scope", False))
    comparison_ready_after_scope = bool(data.get("comparison_ready_after_scope", False))
    does_not_establish = data.get("does_not_establish", []) or []
    source_evidence = data.get("source_evidence", []) or []

    audit = data.get("audit_observation", {}) or {}
    audit_exit_code = audit.get("audit_exit_code") if isinstance(audit, dict) else None
    remediation_performed = bool(audit.get("remediation_performed", False)) if isinstance(audit, dict) else False

    interp = data.get("assessment_interpretation", {}) or {}
    functional_runtime = _str_field(interp, "functional_runtime_evidence")
    security_readiness = _str_field(interp, "security_readiness")
    production_readiness = _str_field(interp, "production_readiness")
    result_assessment = _str_field(interp, "result_assessment")
    comparison_ready = _str_field(interp, "comparison_ready")

    # --- remediation is out of scope for v1 (global, any scope_status) --------
    # v1 models only not-yet-remediated caveats. A remediated state must be
    # represented by a future separate contract/PR, never inside this scope-only
    # artifact.
    if dependency_risk_remediated:
        errors.append(
            format_error(
                "DEPENDENCY_RISK_REMEDIATED_OUT_OF_SCOPE",
                path,
                "dependency_risk_remediated=true is out of scope for "
                "dependency-risk-caveat-scope v1; use a future remediation "
                "contract/PR.",
            )
        )

    # --- remediation_performed is the same claim by the side door -------------
    # audit_observation.remediation_performed=true asserts remediation just like
    # dependency_risk_remediated=true; v1 scopes unresolved caveats only.
    if remediation_performed:
        errors.append(
            format_error(
                "REMEDIATION_PERFORMED_OUT_OF_SCOPE",
                path,
                "audit_observation.remediation_performed=true is out of scope for "
                "dependency-risk-caveat-scope v1; remediation belongs in a future "
                "separate contract/PR.",
            )
        )

    # --- scoped_not_remediated: must stay un-remediated -----------------------
    if scope_status == "scoped_not_remediated":
        if dependency_risk_remediated:
            errors.append(
                format_error(
                    "SCOPED_NOT_REMEDIATED_REQUIRES_FALSE_REMEDIATED",
                    path,
                    "scope_status=scoped_not_remediated requires "
                    "dependency_risk_remediated=false (got true). Scoping a risk is "
                    "not remediating it.",
                )
            )

        # --- scoped_not_remediated: security/production stay blocked ----------
        not_blocked = [
            f"{name}={value!r}"
            for name, value in (
                ("security_readiness", security_readiness),
                ("production_readiness", production_readiness),
            )
            if value != "blocked"
        ]
        if not_blocked:
            errors.append(
                format_error(
                    "SCOPED_NOT_REMEDIATED_BLOCKS_SECURITY_PRODUCTION",
                    path,
                    "scope_status=scoped_not_remediated requires "
                    "assessment_interpretation.security_readiness and "
                    "production_readiness to be 'blocked'; offending: "
                    + ", ".join(not_blocked),
                )
            )

        # --- scoped_not_remediated: result_assessment/comparison stay blocked -
        assessment_violations = []
        if result_assessment_allowed:
            assessment_violations.append("result_assessment_allowed_after_scope=true")
        if comparison_ready_after_scope:
            assessment_violations.append("comparison_ready_after_scope=true")
        if result_assessment != "still_blocked":
            assessment_violations.append(
                f"assessment_interpretation.result_assessment={result_assessment!r} "
                "(expected 'still_blocked')"
            )
        if comparison_ready != "false":
            assessment_violations.append(
                f"assessment_interpretation.comparison_ready={comparison_ready!r} "
                "(expected 'false')"
            )
        if assessment_violations:
            errors.append(
                format_error(
                    "SCOPED_NOT_REMEDIATED_BLOCKS_RESULT_ASSESSMENT",
                    path,
                    "scope_status=scoped_not_remediated must not allow a result "
                    "assessment or comparison; offending: "
                    + ", ".join(assessment_violations),
                )
            )

    # --- functional-runtime reading must not become a security approval -------
    declared = {str(item).strip().lower() for item in does_not_establish}
    if functional_runtime == FUNCTIONAL_RUNTIME_NOT_INVALIDATED:
        missing_security = [d for d in SECURITY_DISCLAIMERS_REQUIRED if d not in declared]
        if missing_security:
            errors.append(
                format_error(
                    "FUNCTIONAL_RUNTIME_EVIDENCE_MUST_NOT_BE_SECURITY_APPROVAL",
                    path,
                    "assessment_interpretation.functional_runtime_evidence="
                    f"'{FUNCTIONAL_RUNTIME_NOT_INVALIDATED}' requires does_not_establish "
                    "to disclaim security/production approval; missing: "
                    + ", ".join(missing_security),
                )
            )

    # --- mandatory anti-overclaim non-claims ----------------------------------
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

    # --- audit exit code coupling --------------------------------------------
    # A non-zero audit exit code is an observed (unremediated) finding: it must
    # not coexist with a remediated flag, an unblocked security/production
    # reading, or any result_assessment / comparison allowance.
    if isinstance(audit_exit_code, int) and not isinstance(audit_exit_code, bool) and audit_exit_code != 0:
        audit_violations = []
        if dependency_risk_remediated:
            audit_violations.append("dependency_risk_remediated=true")
        if security_readiness != "blocked":
            audit_violations.append(f"security_readiness={security_readiness!r}")
        if production_readiness != "blocked":
            audit_violations.append(f"production_readiness={production_readiness!r}")
        if result_assessment_allowed:
            audit_violations.append("result_assessment_allowed_after_scope=true")
        if comparison_ready_after_scope:
            audit_violations.append("comparison_ready_after_scope=true")
        if result_assessment not in ("", "still_blocked"):
            audit_violations.append(
                f"assessment_interpretation.result_assessment={result_assessment!r}"
            )
        if comparison_ready not in ("", "false"):
            audit_violations.append(
                f"assessment_interpretation.comparison_ready={comparison_ready!r}"
            )
        if audit_violations:
            errors.append(
                format_error(
                    "AUDIT_EXIT_NONZERO_REQUIRES_NOT_REMEDIATED",
                    path,
                    f"audit_observation.audit_exit_code={audit_exit_code} (non-zero) "
                    "requires dependency_risk_remediated=false, blocked "
                    "security/production readiness, and no result_assessment/comparison "
                    "allowance; offending: "
                    + ", ".join(audit_violations),
                )
            )

    # --- challenge_version anchored to a real benchmark challenge -------------
    challenge_error = challenge_version_error(data, path, repo_root)
    if challenge_error is not None:
        errors.append(challenge_error)

    # --- source_evidence path escape + existence ------------------------------
    for rel in source_evidence:
        if not isinstance(rel, str) or not rel.strip():
            continue
        _resolved, code = resolve_repo_relative_path(rel.strip(), repo_root, must_exist=True)
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
    return sorted(experiments_dir.glob(SCOPE_GLOB))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate dependency-risk-caveat-scope artifacts."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="dependency-risk-caveat-scope YAML files (default: discover all under experiments/).",
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
                "ℹ️ No dependency-risk-caveat-scope artifacts found; "
                "dependency-risk-caveat-scope validation skipped."
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
        f"Dependency-risk-caveat-scope artifacts: checked={checked}, passed={passed}, "
        f"failed={checked - passed}"
    )
    return highest_exit_code


if __name__ == "__main__":
    sys.exit(main())
