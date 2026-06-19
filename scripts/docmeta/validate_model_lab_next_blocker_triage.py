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
                                   'readiness_gate' is readable and explicitly confirms
                                   a blocked assessment: readiness_status=blocked,
                                   result_assessment_allowed is literally False, and
                                   comparison_ready is literally False (a missing field
                                   is NOT treated as False). A triage of "what is still
                                   blocking" requires that the assessment is, in fact,
                                   still blocked.
  TRIAGE_REQUIRES_MATCHING_READINESS_GATE_SOURCE
                                   a readiness_gate source loaded but is not a
                                   result_assessment_readiness artifact for the
                                   triage's own series_id (wrong artifact or series).
  TRIAGE_REQUIRES_FALSE_RESULT_ASSESSMENT_ALLOWED
                                   result_assessment_allowed_after_triage is true. A
                                   triage prioritizes blockers; it does not authorize
                                   a result assessment.
  TRIAGE_REQUIRES_FALSE_COMPARISON_READY
                                   comparison_ready_after_triage is true. A triage
                                   does not make the series comparison-ready.
  TRIAGE_REQUIRES_RECOMMENDED_NEXT_TASK
                                   recommended_next_task is missing or lacks a
                                   non-empty id / target_blocker / reason.
  TRIAGE_REQUIRES_RECOMMENDED_TARGET_BLOCKER
                                   recommended_next_task.target_blocker is non-empty
                                   but is not one of the triage's open remaining_blockers
                                   ids.
  TRIAGE_REQUIRES_RECOMMENDED_TASK_SHAPE_MATCH
                                   recommended_next_task.id does not equal the
                                   next_task_shape declared by its (open, listed)
                                   target_blocker.
  TRIAGE_REQUIRES_TOP_PRIORITY_TARGET
                                   the (open, listed) target_blocker does not have
                                   recommended_position == 1; the recommendation must
                                   follow the triage's own ranking.
  TRIAGE_REQUIRES_OPEN_REMAINING_BLOCKERS
                                   a remaining_blockers entry has status != open. A
                                   triage prioritizes unresolved blockers; it must
                                   not mark a blocker resolved.
  TRIAGE_REQUIRES_UNIQUE_BLOCKER_IDS
                                   two remaining_blockers entries share an id
                                   (uniqueItems only blocks identical objects).
  TRIAGE_REQUIRES_UNIQUE_RECOMMENDED_POSITIONS
                                   two remaining_blockers entries share a
                                   recommended_position.
  TRIAGE_REQUIRES_UNIQUE_TRIAGE_CRITERIA_IDS
                                   two triage_criteria entries share an id (only
                                   checked when triage_criteria is present).
  TRIAGE_REQUIRES_DEPENDENCY_RISK_SCOPE_SOURCE
                                   no readable source_evidence of kind
                                   'dependency_risk_scope' was found, so the expected
                                   remaining-blocker set cannot be derived.
  TRIAGE_REQUIRES_SINGLE_READINESS_GATE_SOURCE
                                   source_evidence does not contain exactly one
                                   readiness_gate.
  TRIAGE_REQUIRES_SINGLE_DEPENDENCY_RISK_SCOPE_SOURCE
                                   source_evidence does not contain exactly one
                                   dependency_risk_scope.
  TRIAGE_REQUIRES_VALID_DEPENDENCY_RISK_SCOPE_BLOCKERS
                                   a dependency_risk_scope remaining_blockers is
                                   missing or not a list.
  TRIAGE_REQUIRES_MATCHING_DEPENDENCY_RISK_SCOPE_SOURCE
                                   a dependency_risk_scope source loaded but is not a
                                   dependency_risk_caveat_scope artifact for the
                                   triage's own series_id (wrong artifact or series).
  TRIAGE_REQUIRES_ALL_SCOPE_BLOCKERS
                                   the remaining_blockers id set does not exactly
                                   match the dependency-risk-caveat-scope artifact's
                                   remaining_blockers (reports missing and unexpected).
  SOURCE_EVIDENCE_PATH_NOT_FOUND   a referenced source_evidence path does not exist.
  SOURCE_EVIDENCE_PATH_ESCAPE      a referenced source_evidence path resolves outside the repo.
  MISSING_MANDATORY_DOES_NOT_ESTABLISH
                                   does_not_establish omits a mandatory non-claim.

The expected remaining-blocker set is read from the dependency-risk-caveat-scope
artifact (state lives in artifacts, not in this validator); only the normative
MANDATORY_DOES_NOT_ESTABLISH non-claims stay hardcoded here.

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
from dataclasses import dataclass
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

# The set of remaining blockers a triage must cover is NOT hardcoded here: it is
# state, and state lives in the dependency-risk-caveat-scope artifact. The triage
# must reference that artifact (kind: dependency_risk_scope) and cover exactly its
# remaining_blockers (see TRIAGE_REQUIRES_ALL_SCOPE_BLOCKERS). Only the normative
# non-claims below stay hardcoded.

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
DEPENDENCY_RISK_SCOPE_KIND = "dependency_risk_scope"
READINESS_STATUS_KEY = "readiness_status"
RESULT_ASSESSMENT_ALLOWED_KEY = "result_assessment_allowed"
COMPARISON_READY_KEY = "comparison_ready"
REMAINING_BLOCKERS_KEY = "remaining_blockers"
ARTIFACT_TYPE_KEY = "artifact_type"
SERIES_ID_KEY = "series_id"
# Expected artifact_type for each cross-referenced source kind. A readiness_gate
# source must be a result_assessment_readiness artifact, and a dependency_risk_scope
# source must be a dependency_risk_caveat_scope artifact, both for the triage's own
# series — otherwise the triage is anchored to the wrong (or a stale) artifact.
READINESS_GATE_ARTIFACT_TYPE = "result_assessment_readiness"
DEPENDENCY_RISK_SCOPE_ARTIFACT_TYPE = "dependency_risk_caveat_scope"
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


@dataclass(frozen=True)
class SourceEvidenceResolution:
    """One source_evidence entry, resolved exactly once.

    ``code`` is "ESCAPE" / "NOT_FOUND" / None (ok). ``loaded_yaml`` is the parsed
    document when the resolved file exists and is a YAML mapping, else None. The
    parsed YAML is reused by the readiness-gate and dependency-risk-scope checks so
    each referenced file is read at most once.
    """

    rel_path: str
    kind: str
    resolved: Path | None
    code: str | None
    loaded_yaml: dict | None


def resolve_source_evidence_entries(
    data: dict, repo_root: Path
) -> list[SourceEvidenceResolution]:
    """Resolve every source_evidence entry once (path safety + optional YAML load)."""
    resolutions: list[SourceEvidenceResolution] = []
    for entry in _source_evidence_entries(data):
        rel = str(entry.get("path", "")).strip()
        if not rel:
            continue
        kind = str(entry.get("kind", "")).strip()
        resolved, code = resolve_repo_relative_path(rel, repo_root, must_exist=True)
        loaded: dict | None = None
        if (
            code is None
            and resolved is not None
            and resolved.is_file()
            and resolved.suffix.lower() in (".yml", ".yaml")
        ):
            try:
                doc = yaml.safe_load(resolved.read_text(encoding="utf-8"))
            except (OSError, yaml.YAMLError):
                doc = None
            if isinstance(doc, dict):
                loaded = doc
        resolutions.append(
            SourceEvidenceResolution(
                rel_path=rel, kind=kind, resolved=resolved, code=code, loaded_yaml=loaded
            )
        )
    return resolutions


def _readiness_blocked_confirmed(resolutions: list[SourceEvidenceResolution]) -> bool:
    """True if a referenced readiness_gate explicitly confirms a blocked assessment.

    Inspects each kind 'readiness_gate' resolution that loaded as a YAML mapping and
    requires all three signals to be present and explicit: readiness_status=blocked,
    result_assessment_allowed is literally False, and comparison_ready is literally
    False. A missing field is NOT treated as False — an under-specified gate must not
    pass for a blocked assessment. Mirrors the cross-artifact read in
    validate_result_assessment_readiness.py.
    """
    for res in resolutions:
        if res.kind != READINESS_GATE_KIND or res.loaded_yaml is None:
            continue
        status = res.loaded_yaml.get(READINESS_STATUS_KEY)
        allowed = res.loaded_yaml.get(RESULT_ASSESSMENT_ALLOWED_KEY)
        comparison = res.loaded_yaml.get(COMPARISON_READY_KEY)
        if status == "blocked" and allowed is False and comparison is False:
            return True
    return False


def _scope_blocker_ids(
    resolutions: list[SourceEvidenceResolution],
) -> tuple[set[str], bool, list[str]]:
    """Return (expected_blocker_ids, scope_source_found, problems).

    ``scope_source_found`` is True if at least one kind 'dependency_risk_scope'
    resolution loaded as a YAML mapping. The ids are read tolerantly: each
    remaining_blockers item may be a plain string (the canonical
    dependency-risk-caveat-scope.v1 form) or a mapping with an 'id' field. Empty
    ids are ignored.
    """
    found = False
    ids: set[str] = set()
    problems: list[str] = []
    for res in resolutions:
        if res.kind != DEPENDENCY_RISK_SCOPE_KIND or res.loaded_yaml is None:
            continue
        found = True
        if REMAINING_BLOCKERS_KEY not in res.loaded_yaml:
            problems.append(f"{res.rel_path}: '{REMAINING_BLOCKERS_KEY}' is missing")
            continue
        raw_blockers = res.loaded_yaml[REMAINING_BLOCKERS_KEY]
        if not isinstance(raw_blockers, list):
            problems.append(f"{res.rel_path}: '{REMAINING_BLOCKERS_KEY}' must be a list")
            continue
        for item in raw_blockers:
            if isinstance(item, str):
                blocker_id = item.strip()
            elif isinstance(item, dict):
                blocker_id = str(item.get("id", "")).strip()
            else:
                blocker_id = ""
            if blocker_id:
                ids.add(blocker_id)
    return ids, found, problems


def _source_type_series_mismatches(
    resolutions: list[SourceEvidenceResolution],
    kind: str,
    expected_artifact_type: str,
    expected_series_id: str,
) -> list[str]:
    """Describe each loaded source of ``kind`` whose artifact_type/series_id is wrong.

    Only inspects resolutions of the given kind that loaded as a YAML mapping (a
    missing/unreadable source is handled by the kind-specific presence rules). A
    source must be the expected artifact_type and carry the triage's own series_id,
    so the triage cannot anchor to the wrong artifact or a different series.
    """
    problems: list[str] = []
    for res in resolutions:
        if res.kind != kind or res.loaded_yaml is None:
            continue
        actual_type = str(res.loaded_yaml.get(ARTIFACT_TYPE_KEY, "")).strip()
        actual_series = str(res.loaded_yaml.get(SERIES_ID_KEY, "")).strip()
        issues: list[str] = []
        if actual_type != expected_artifact_type:
            issues.append(
                f"artifact_type={actual_type!r} (expected {expected_artifact_type!r})"
            )
        if not expected_series_id or actual_series != expected_series_id:
            issues.append(
                f"series_id={actual_series!r} (expected {expected_series_id!r})"
            )
        if issues:
            problems.append(f"{res.rel_path}: " + ", ".join(issues))
    return problems


def _duplicates(values: list) -> list:
    """Return the distinct values that appear more than once, ordered by str()."""
    seen: set = set()
    dups: set = set()
    for value in values:
        if value in seen:
            dups.add(value)
        else:
            seen.add(value)
    return sorted(dups, key=str)


def semantic_errors(data: dict, path: Path, repo_root: Path) -> list[str]:
    errors: list[str] = []

    result_assessment_allowed = bool(data.get("result_assessment_allowed_after_triage", False))
    comparison_ready = bool(data.get("comparison_ready_after_triage", False))
    recommended_next_task = data.get("recommended_next_task")
    remaining_blockers = data.get("remaining_blockers", []) or []
    does_not_establish = data.get("does_not_establish", []) or []
    triage_series_id = str(data.get("series_id", "")).strip()

    # Resolve every source_evidence path (and load referenced YAML) exactly once;
    # the readiness, dependency-risk-scope, and path checks all reuse this list.
    resolutions = resolve_source_evidence_entries(data, repo_root)

    readiness_count = sum(1 for r in resolutions if r.kind == READINESS_GATE_KIND)
    if readiness_count != 1:
        errors.append(
            format_error(
                "TRIAGE_REQUIRES_SINGLE_READINESS_GATE_SOURCE",
                path,
                "source_evidence must contain exactly one readiness_gate source; foundational readiness evidence must be unambiguous."
            )
        )

    scope_count = sum(1 for r in resolutions if r.kind == DEPENDENCY_RISK_SCOPE_KIND)
    if scope_count != 1:
        errors.append(
            format_error(
                "TRIAGE_REQUIRES_SINGLE_DEPENDENCY_RISK_SCOPE_SOURCE",
                path,
                "source_evidence must contain exactly one dependency_risk_scope source; foundational dependency-risk scope evidence must be unambiguous."
            )
        )

    # --- a triage requires a blocked result assessment -----------------------
    if not _readiness_blocked_confirmed(resolutions):
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

    # --- readiness_gate source must be the right artifact for this series -----
    readiness_mismatches = _source_type_series_mismatches(
        resolutions, READINESS_GATE_KIND, READINESS_GATE_ARTIFACT_TYPE, triage_series_id
    )
    if readiness_mismatches:
        errors.append(
            format_error(
                "TRIAGE_REQUIRES_MATCHING_READINESS_GATE_SOURCE",
                path,
                "a source_evidence of kind 'readiness_gate' must be a "
                f"'{READINESS_GATE_ARTIFACT_TYPE}' artifact for this triage's series "
                f"(series_id={triage_series_id!r}); offending: "
                + "; ".join(readiness_mismatches),
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
    reason = ""
    if isinstance(recommended_next_task, dict):
        task_id = str(recommended_next_task.get("id", "")).strip()
        target_blocker = str(recommended_next_task.get("target_blocker", "")).strip()
        reason = str(recommended_next_task.get("reason", "")).strip()
    if not task_id or not target_blocker or not reason:
        errors.append(
            format_error(
                "TRIAGE_REQUIRES_RECOMMENDED_NEXT_TASK",
                path,
                "recommended_next_task must be present with non-empty id, target_blocker, and reason; a triage must name and justify the next step.",
            )
        )

    # --- remaining_blockers must stay open -----------------------------------
    non_open = [
        (str(b.get("id", "")).strip() or "<missing-id>")
        for b in remaining_blockers
        if isinstance(b, dict) and str(b.get("status", "")).strip() != "open"
    ]
    if non_open:
        errors.append(
            format_error(
                "TRIAGE_REQUIRES_OPEN_REMAINING_BLOCKERS",
                path,
                "remaining_blockers entries must stay open; a next-blocker triage "
                "prioritizes unresolved blockers and must not mark any blocker as "
                "resolved. Offending: " + ", ".join(non_open),
            )
        )

    # --- blocker ids must be semantically unique ------------------------------
    # uniqueItems in the schema only blocks fully identical objects; two entries
    # with the same id but different metadata would slip through, so check ids here.
    duplicate_blocker_ids = _duplicates(
        [
            str(b.get("id", "")).strip()
            for b in remaining_blockers
            if isinstance(b, dict) and str(b.get("id", "")).strip()
        ]
    )
    if duplicate_blocker_ids:
        errors.append(
            format_error(
                "TRIAGE_REQUIRES_UNIQUE_BLOCKER_IDS",
                path,
                "remaining_blockers ids must be unique; duplicated: "
                + ", ".join(duplicate_blocker_ids),
            )
        )

    # --- recommended_position values must be unique ---------------------------
    duplicate_positions = _duplicates(
        [
            b.get("recommended_position")
            for b in remaining_blockers
            if isinstance(b, dict)
            and isinstance(b.get("recommended_position"), int)
            and not isinstance(b.get("recommended_position"), bool)
        ]
    )
    if duplicate_positions:
        errors.append(
            format_error(
                "TRIAGE_REQUIRES_UNIQUE_RECOMMENDED_POSITIONS",
                path,
                "remaining_blockers recommended_position values must be unique; "
                "duplicated: " + ", ".join(str(p) for p in duplicate_positions),
            )
        )

    # --- triage_criteria ids must be unique (only when criteria are present) --
    # Presence of triage_criteria is NOT required here (an open contract decision);
    # this only constrains uniqueness when the optional block is supplied.
    triage_criteria = data.get("triage_criteria")
    if isinstance(triage_criteria, list):
        duplicate_criteria_ids = _duplicates(
            [
                str(c.get("id", "")).strip()
                for c in triage_criteria
                if isinstance(c, dict) and str(c.get("id", "")).strip()
            ]
        )
        if duplicate_criteria_ids:
            errors.append(
                format_error(
                    "TRIAGE_REQUIRES_UNIQUE_TRIAGE_CRITERIA_IDS",
                    path,
                    "triage_criteria ids must be unique; duplicated: "
                    + ", ".join(duplicate_criteria_ids),
                )
            )

    # --- recommended target_blocker must be a listed, open blocker ------------
    # Non-empty target_blocker only (an empty one is already reported by
    # TRIAGE_REQUIRES_RECOMMENDED_NEXT_TASK); it must point at a blocker the triage
    # itself lists as still open.
    open_blocker_ids = {
        str(b.get("id", "")).strip()
        for b in remaining_blockers
        if isinstance(b, dict)
        and str(b.get("status", "")).strip() == "open"
        and str(b.get("id", "")).strip()
    }
    if target_blocker and target_blocker not in open_blocker_ids:
        errors.append(
            format_error(
                "TRIAGE_REQUIRES_RECOMMENDED_TARGET_BLOCKER",
                path,
                "recommended_next_task.target_blocker must reference one of the open "
                f"remaining_blockers ids; got {target_blocker!r}, open ids: "
                + (", ".join(sorted(open_blocker_ids)) or "<none>") + ".",
            )
        )

    # The next two checks only apply when target_blocker is an otherwise-valid
    # open, listed blocker (an invalid target is already reported above), so they
    # stay isolated to genuine task/priority inconsistencies.
    target_block = next(
        (
            b
            for b in remaining_blockers
            if isinstance(b, dict) and str(b.get("id", "")).strip() == target_blocker
        ),
        None,
    )
    if target_blocker in open_blocker_ids and target_block is not None:
        # --- recommended task must match the target blocker's next_task_shape -
        target_shape = str(target_block.get("next_task_shape", "")).strip()
        if task_id and target_shape and task_id != target_shape:
            errors.append(
                format_error(
                    "TRIAGE_REQUIRES_RECOMMENDED_TASK_SHAPE_MATCH",
                    path,
                    "recommended_next_task.id must match the next_task_shape declared "
                    f"by its target_blocker; got id={task_id!r}, target_blocker "
                    f"{target_blocker!r} next_task_shape={target_shape!r}.",
                )
            )

        # --- target blocker must be the top priority (recommended_position 1) -
        position = target_block.get("recommended_position")
        if not (isinstance(position, int) and not isinstance(position, bool) and position == 1):
            errors.append(
                format_error(
                    "TRIAGE_REQUIRES_TOP_PRIORITY_TARGET",
                    path,
                    "recommended_next_task.target_blocker must reference the "
                    "top-priority open blocker (recommended_position == 1); "
                    f"target_blocker {target_blocker!r} has recommended_position="
                    f"{position!r}.",
                )
            )

    # --- remaining_blockers must match the dependency-risk-scope artifact -----
    # The expected set is read from the dependency-risk-caveat-scope artifact (state
    # in artifacts, not in this validator), so a future blocker change there does not
    # require editing the validator.
    declared_blocker_ids = {
        str(b.get("id", "")).strip()
        for b in remaining_blockers
        if isinstance(b, dict) and str(b.get("id", "")).strip()
    }
    expected_blocker_ids, scope_source_found, scope_blocker_problems = _scope_blocker_ids(resolutions)
    if not scope_source_found:
        errors.append(
            format_error(
                "TRIAGE_REQUIRES_DEPENDENCY_RISK_SCOPE_SOURCE",
                path,
                "no readable source_evidence of kind 'dependency_risk_scope' was "
                "found; the expected remaining-blocker set is derived from the "
                "dependency-risk-caveat-scope artifact and cannot be checked without it.",
            )
        )
    elif scope_blocker_problems:
        for problem in scope_blocker_problems:
            errors.append(
                format_error(
                    "TRIAGE_REQUIRES_VALID_DEPENDENCY_RISK_SCOPE_BLOCKERS",
                    path,
                    f"dependency_risk_scope artifact must have a valid remaining_blockers list; {problem}",
                )
            )
    else:
        missing = sorted(expected_blocker_ids - declared_blocker_ids)
        unexpected = sorted(declared_blocker_ids - expected_blocker_ids)
        if missing or unexpected:
            detail = []
            if missing:
                detail.append("missing: " + ", ".join(missing))
            if unexpected:
                detail.append("unexpected: " + ", ".join(unexpected))
            errors.append(
                format_error(
                    "TRIAGE_REQUIRES_ALL_SCOPE_BLOCKERS",
                    path,
                    "remaining_blockers ids must exactly match the "
                    "dependency-risk-caveat-scope remaining_blockers; "
                    + "; ".join(detail),
                )
            )

    # --- dependency_risk_scope source must be the right artifact for this series
    scope_mismatches = _source_type_series_mismatches(
        resolutions,
        DEPENDENCY_RISK_SCOPE_KIND,
        DEPENDENCY_RISK_SCOPE_ARTIFACT_TYPE,
        triage_series_id,
    )
    if scope_mismatches:
        errors.append(
            format_error(
                "TRIAGE_REQUIRES_MATCHING_DEPENDENCY_RISK_SCOPE_SOURCE",
                path,
                "a source_evidence of kind 'dependency_risk_scope' must be a "
                f"'{DEPENDENCY_RISK_SCOPE_ARTIFACT_TYPE}' artifact for this triage's "
                f"series (series_id={triage_series_id!r}); offending: "
                + "; ".join(scope_mismatches),
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

    # --- source_evidence path escape + existence (reuses the single pass) -----
    for res in resolutions:
        if res.code == "ESCAPE":
            errors.append(
                format_error(
                    "SOURCE_EVIDENCE_PATH_ESCAPE",
                    path,
                    f"source_evidence path '{res.rel_path}' resolves outside the repo root.",
                )
            )
        elif res.code == "NOT_FOUND":
            errors.append(
                format_error(
                    "SOURCE_EVIDENCE_PATH_NOT_FOUND",
                    path,
                    f"source_evidence path '{res.rel_path}' does not exist.",
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
