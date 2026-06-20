#!/usr/bin/env python3
"""validate_model_lab_condition_contrast_design_gate.py — Validator for Model-Lab condition-contrast design-gate artifacts.

A condition-contrast design-gate artifact
(``experiments/<series>/results/condition-contrast-design-gate.yml``) defines the
machine-readable criteria a *future* Run-004 condition-contrast design must
satisfy. It is a design-criteria gate only: it does NOT select a primary
intervention axis, does NOT select a concrete condition, does NOT execute
Run-004, does NOT allow a result_assessment, does NOT make the series
comparison-ready, and does NOT resolve weak_condition_contrast.

This validator complements — it does not replace — the runtime-evidence gate
(``validate_runtime_evidence_gate.py``), the result-assessment-readiness gate
(``validate_result_assessment_readiness.py``), the dependency-risk-caveat scope
(``validate_dependency_risk_caveat_scope.py``), and the next-blocker triage
(``validate_model_lab_next_blocker_triage.py``). The triage records which
still-open blocker to handle next; this gate records what a future design for the
top-ranked blocker (weak_condition_contrast) must satisfy. Defining criteria is
not selecting an axis, not selecting a condition, and never authorizes execution
or assessment.

Enforced semantic rules (exit 1):
  CONTRAST_GATE_REQUIRES_SINGLE_TRIAGE_SOURCE
                                   source_evidence does not contain exactly one
                                   next_blocker_triage source.
  CONTRAST_GATE_REQUIRES_SINGLE_READINESS_SOURCE
                                   source_evidence does not contain exactly one
                                   readiness_gate source.
  CONTRAST_GATE_REQUIRES_MATCHING_SOURCE_IDENTITY
                                   a triage source is not a
                                   model_lab_next_blocker_triage for this gate's
                                   series, or a readiness source is not a
                                   result_assessment_readiness for this gate's
                                   series and challenge_version (wrong artifact,
                                   series, or challenge).
  CONTRAST_GATE_REQUIRES_TRIAGE_RECOMMENDATION
                                   no readable triage recommends this gate
                                   (recommended_next_task.id == the design-gate
                                   task id) for the gate's own target_blocker.
  CONTRAST_GATE_REQUIRES_BLOCKED_READINESS
                                   no readable readiness_gate explicitly confirms
                                   a blocked assessment (readiness_status=blocked,
                                   result_assessment_allowed is literally False,
                                   comparison_ready is literally False; a missing
                                   field is NOT treated as False).
  CONTRAST_GATE_REQUIRES_OPEN_TARGET_BLOCKER
                                   the gate's target_blocker is not listed as open
                                   in a referenced triage's remaining_blockers
                                   and/or in a referenced readiness gate's
                                   blockers. Defining criteria for an already-closed
                                   blocker would be incoherent.
  CONTRAST_GATE_REQUIRES_SINGLE_PRIMARY_AXIS_POLICY
                                   contrast_policy does not require exactly one
                                   primary intervention axis
                                   (primary_intervention_axis_required != true or
                                   required_primary_intervention_axis_count != 1).
  CONTRAST_GATE_REQUIRES_COMPLETE_CRITERIA
                                   invariant_dimensions or materiality_criteria
                                   omit a mandatory id, materiality evidence is not
                                   required, or a materiality criterion lacks a
                                   non-empty evidence_required list.
  CONTRAST_GATE_REQUIRES_UNIQUE_SEMANTIC_IDS
                                   two entries within invariant_dimensions,
                                   controlled_secondary_dimensions,
                                   materiality_criteria, or confounder_controls
                                   share an id (uniqueItems only blocks identical
                                   objects).
  CONTRAST_GATE_REQUIRES_COMPLETE_CONFOUNDER_CONTROLS
                                   confounder_controls omit a mandatory id.
  CONTRAST_GATE_REQUIRES_STATUS_PERMISSION_CONSISTENCY
                                   gate_status and run_004_design_allowed disagree
                                   (criteria_defined => true, blocked => false), or
                                   decision.status != gate_status.
  CONTRAST_GATE_FORBIDS_EXECUTION_AND_ASSESSMENT
                                   run_004_execution_allowed,
                                   result_assessment_allowed_after_gate, or
                                   comparison_ready_after_gate is true. A
                                   design-criteria gate never authorizes execution,
                                   result assessment, or comparison.
  CONTRAST_GATE_REQUIRES_MANDATORY_NON_CLAIMS
                                   does_not_establish omits a mandatory non-claim.
  CONTRAST_GATE_REQUIRES_SAFE_EXISTING_SOURCE_PATHS
                                   a referenced source_evidence path resolves
                                   outside the repo (escape) or does not exist.

The mandatory invariant/materiality/confounder ids and the mandatory non-claims
stay hardcoded here as the normative minimum; the expected target_blocker, the
blocked readiness state, and the recommendation are read from the source
artifacts (state lives in artifacts, not in this validator).

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
        "ERROR: Missing dependencies for model-lab-condition-contrast-design-gate "
        "validation. Install PyYAML and jsonschema.",
        file=sys.stderr,
    )
    raise SystemExit(2) from exc


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCHEMA_PATH = (
    REPO_ROOT / "schemas" / "model-lab-condition-contrast-design-gate.v1.schema.json"
)

GATE_GLOB = "*/results/condition-contrast-design-gate.yml"

# Source kinds. Exactly one of each foundational kind is required; the context
# kinds are checked only for existence and path safety, never for prose content.
TRIAGE_KIND = "next_blocker_triage"
READINESS_KIND = "readiness_gate"

# Cross-referenced artifact identities. A next_blocker_triage source must be a
# model_lab_next_blocker_triage artifact, and a readiness_gate source must be a
# result_assessment_readiness artifact, both for this gate's own series — otherwise
# the gate is anchored to the wrong (or a stale) artifact.
TRIAGE_ARTIFACT_TYPE = "model_lab_next_blocker_triage"
READINESS_ARTIFACT_TYPE = "result_assessment_readiness"

# The triage must recommend *this* design gate. The recommended task id is the
# Model-Lab task id (not this artifact's artifact_type, which is intentionally
# the longer model_lab_condition_contrast_design_gate).
EXPECTED_TRIAGE_TASK_ID = "condition_contrast_design_gate"

ARTIFACT_TYPE_KEY = "artifact_type"
SERIES_ID_KEY = "series_id"
CHALLENGE_VERSION_KEY = "challenge_version"
READINESS_STATUS_KEY = "readiness_status"
RESULT_ASSESSMENT_ALLOWED_KEY = "result_assessment_allowed"
COMPARISON_READY_KEY = "comparison_ready"

# Outcome surfaces a future design must keep fixed. The whole point of the gate is
# that these stay constant across conditions, so all must be declared.
MANDATORY_INVARIANT_DIMENSIONS = (
    "challenge_contract",
    "acceptance_surface",
    "evaluation_criteria",
    "verification_surface",
    "evidence_capture",
)

# Minimum materiality criteria a future design must satisfy. Each must carry
# concrete pre-execution evidence requirements (materiality must be observable
# before any run, never asserted after the fact).
MANDATORY_MATERIALITY_CRITERIA = (
    "single_primary_intervention_axis",
    "operationally_verifiable_difference",
    "no_cosmetic_relabeling",
    "fixed_outcome_surface",
    "provenance_before_execution",
)

# Minimum confounder controls. A future design must classify each of these as
# controlled or reported before it can claim a material contrast.
MANDATORY_CONFOUNDER_CONTROLS = (
    "multi_axis_drift",
    "acceptance_or_test_drift",
    "unequal_human_intervention",
    "dependency_or_runtime_drift",
    "post_hoc_condition_rework",
    "self_reported_independence_as_external_proof",
)

# Baseline anti-overclaim non-claims every gate must carry. Defining criteria must
# never imply the blocker is resolved, a run was executed, a result assessment is
# allowed, the series is comparison-ready, or that quality/comparison/condition
# effect/external independence/auditor comparison/security/production/dependency
# remediation have been achieved.
MANDATORY_DOES_NOT_ESTABLISH = (
    "weak_condition_contrast_resolved",
    "run_004_execution_allowed",
    "run_004_executed",
    "result_assessment_allowed",
    "comparison_ready",
    "model_quality",
    "comparative_superiority",
    "condition_effect",
    "external_model_independence",
    "external_auditor_comparison_completed",
    "security_readiness",
    "production_readiness",
    "dependency_risk_remediated",
)

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
        raise RuntimeError(
            f"schema invalid: {display_path(SCHEMA_PATH)}: {exc.message}"
        ) from exc


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

    Mirrors the helper in validate_model_lab_next_blocker_triage.py; kept small and
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
    parsed YAML is reused by the triage and readiness checks so each referenced
    file is read at most once.
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


def _loaded_docs_of_kind(
    resolutions: list[SourceEvidenceResolution], kind: str
) -> list[dict]:
    return [r.loaded_yaml for r in resolutions if r.kind == kind and r.loaded_yaml is not None]


def _readiness_blocked_confirmed(readiness_docs: list[dict]) -> bool:
    """True if a referenced readiness_gate explicitly confirms a blocked assessment.

    Requires all three signals to be present and explicit: readiness_status=blocked,
    result_assessment_allowed is literally False, and comparison_ready is literally
    False. A missing field is NOT treated as False — an under-specified gate must not
    pass for a blocked assessment. Mirrors the cross-artifact read in
    validate_model_lab_next_blocker_triage.py.
    """
    for doc in readiness_docs:
        status = doc.get(READINESS_STATUS_KEY)
        allowed = doc.get(RESULT_ASSESSMENT_ALLOWED_KEY)
        comparison = doc.get(COMPARISON_READY_KEY)
        if status == "blocked" and allowed is False and comparison is False:
            return True
    return False


def _triage_recommends_gate(triage_docs: list[dict], target_blocker: str) -> bool:
    """True if a referenced triage recommends this design gate for the target blocker.

    The recommended_next_task.id must equal the design-gate task id and its
    target_blocker must equal the gate's own target_blocker.
    """
    for doc in triage_docs:
        task = doc.get("recommended_next_task")
        if not isinstance(task, dict):
            continue
        task_id = str(task.get("id", "")).strip()
        task_target = str(task.get("target_blocker", "")).strip()
        if task_id == EXPECTED_TRIAGE_TASK_ID and target_blocker and task_target == target_blocker:
            return True
    return False


def _blocker_open_in(doc: dict, key: str, target: str) -> bool:
    """True if doc[key] lists an entry with id==target and status=='open'."""
    for item in doc.get(key, []) or []:
        if not isinstance(item, dict):
            continue
        if str(item.get("id", "")).strip() == target and str(item.get("status", "")).strip() == "open":
            return True
    return False


def _source_identity_mismatches(
    docs_with_paths: list[tuple[str, dict]],
    *,
    expected_artifact_type: str,
    expected_series_id: str,
    expected_challenge_version: str | None = None,
) -> list[str]:
    """Describe each loaded source whose artifact_type/series_id/challenge differs."""
    problems: list[str] = []
    for rel_path, doc in docs_with_paths:
        actual_type = str(doc.get(ARTIFACT_TYPE_KEY, "")).strip()
        actual_series = str(doc.get(SERIES_ID_KEY, "")).strip()
        issues: list[str] = []
        if actual_type != expected_artifact_type:
            issues.append(f"artifact_type={actual_type!r} (expected {expected_artifact_type!r})")
        if not expected_series_id or actual_series != expected_series_id:
            issues.append(f"series_id={actual_series!r} (expected {expected_series_id!r})")
        if expected_challenge_version is not None:
            actual_challenge = str(doc.get(CHALLENGE_VERSION_KEY, "")).strip()
            if actual_challenge != expected_challenge_version:
                issues.append(
                    f"challenge_version={actual_challenge!r} (expected {expected_challenge_version!r})"
                )
        if issues:
            problems.append(f"{rel_path}: " + ", ".join(issues))
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


def _ids(items: list) -> list[str]:
    return [
        str(item.get("id", "")).strip()
        for item in items
        if isinstance(item, dict) and str(item.get("id", "")).strip()
    ]


def semantic_errors(data: dict, path: Path, repo_root: Path) -> list[str]:
    errors: list[str] = []

    gate_series_id = str(data.get("series_id", "")).strip()
    gate_challenge = str(data.get("challenge_version", "")).strip()
    target_blocker = str(data.get("target_blocker", "")).strip()
    gate_status = str(data.get("gate_status", "")).strip()
    design_allowed = data.get("run_004_design_allowed")
    execution_allowed = bool(data.get("run_004_execution_allowed", False))
    assessment_allowed = bool(data.get("result_assessment_allowed_after_gate", False))
    comparison_ready = bool(data.get("comparison_ready_after_gate", False))
    contrast_policy = data.get("contrast_policy") or {}
    invariant_dimensions = data.get("invariant_dimensions", []) or []
    controlled_dimensions = data.get("controlled_secondary_dimensions", []) or []
    materiality_criteria = data.get("materiality_criteria", []) or []
    confounder_controls = data.get("confounder_controls", []) or []
    decision = data.get("decision") or {}
    does_not_establish = data.get("does_not_establish", []) or []

    # Resolve every source_evidence path (and load referenced YAML) exactly once;
    # the triage, readiness, and path checks all reuse this list.
    resolutions = resolve_source_evidence_entries(data, repo_root)
    triage_paths = [(r.rel_path, r.loaded_yaml) for r in resolutions if r.kind == TRIAGE_KIND and r.loaded_yaml is not None]
    readiness_paths = [(r.rel_path, r.loaded_yaml) for r in resolutions if r.kind == READINESS_KIND and r.loaded_yaml is not None]
    triage_docs = [doc for _, doc in triage_paths]
    readiness_docs = [doc for _, doc in readiness_paths]

    # --- exactly one foundational triage source ------------------------------
    triage_count = sum(1 for r in resolutions if r.kind == TRIAGE_KIND)
    if triage_count != 1:
        errors.append(
            format_error(
                "CONTRAST_GATE_REQUIRES_SINGLE_TRIAGE_SOURCE",
                path,
                "source_evidence must contain exactly one next_blocker_triage source; "
                f"foundational triage evidence must be unambiguous (found {triage_count}).",
            )
        )

    # --- exactly one foundational readiness source ---------------------------
    readiness_count = sum(1 for r in resolutions if r.kind == READINESS_KIND)
    if readiness_count != 1:
        errors.append(
            format_error(
                "CONTRAST_GATE_REQUIRES_SINGLE_READINESS_SOURCE",
                path,
                "source_evidence must contain exactly one readiness_gate source; "
                f"foundational readiness evidence must be unambiguous (found {readiness_count}).",
            )
        )

    # --- foundational sources must be the right artifact for this series -----
    identity_problems = _source_identity_mismatches(
        triage_paths,
        expected_artifact_type=TRIAGE_ARTIFACT_TYPE,
        expected_series_id=gate_series_id,
    )
    identity_problems += _source_identity_mismatches(
        readiness_paths,
        expected_artifact_type=READINESS_ARTIFACT_TYPE,
        expected_series_id=gate_series_id,
        expected_challenge_version=gate_challenge,
    )
    if identity_problems:
        errors.append(
            format_error(
                "CONTRAST_GATE_REQUIRES_MATCHING_SOURCE_IDENTITY",
                path,
                "each foundational source must match this gate's identity "
                f"(series_id={gate_series_id!r}, challenge_version={gate_challenge!r}); "
                "offending: " + "; ".join(identity_problems),
            )
        )

    # --- triage must recommend this design gate for the target blocker -------
    if triage_docs and not _triage_recommends_gate(triage_docs, target_blocker):
        errors.append(
            format_error(
                "CONTRAST_GATE_REQUIRES_TRIAGE_RECOMMENDATION",
                path,
                "no referenced next_blocker_triage recommends this gate: "
                f"recommended_next_task.id must equal {EXPECTED_TRIAGE_TASK_ID!r} and "
                f"recommended_next_task.target_blocker must equal this gate's "
                f"target_blocker ({target_blocker!r}).",
            )
        )

    # --- readiness must remain blocked ---------------------------------------
    if not _readiness_blocked_confirmed(readiness_docs):
        errors.append(
            format_error(
                "CONTRAST_GATE_REQUIRES_BLOCKED_READINESS",
                path,
                "no source_evidence of kind 'readiness_gate' explicitly confirms a "
                "blocked assessment (readiness_status=blocked, "
                "result_assessment_allowed=false, and comparison_ready=false; missing "
                "fields do not count as false). A design-criteria gate is only coherent "
                "while a formal result assessment is still blocked.",
            )
        )

    # --- target blocker must stay open in both foundational sources ----------
    open_problems: list[str] = []
    for rel_path, doc in triage_paths:
        if target_blocker and not _blocker_open_in(doc, "remaining_blockers", target_blocker):
            open_problems.append(f"{rel_path}: not open in triage remaining_blockers")
    for rel_path, doc in readiness_paths:
        if target_blocker and not _blocker_open_in(doc, "blockers", target_blocker):
            open_problems.append(f"{rel_path}: not open in readiness blockers")
    if open_problems:
        errors.append(
            format_error(
                "CONTRAST_GATE_REQUIRES_OPEN_TARGET_BLOCKER",
                path,
                f"target_blocker {target_blocker!r} must be listed as open in both the "
                "referenced triage and readiness gate; defining criteria for a closed "
                "blocker is incoherent. Offending: " + "; ".join(open_problems),
            )
        )

    # --- contrast policy must require exactly one primary intervention axis ---
    axis_required = contrast_policy.get("primary_intervention_axis_required")
    axis_count = contrast_policy.get("required_primary_intervention_axis_count")
    axis_count_ok = isinstance(axis_count, int) and not isinstance(axis_count, bool) and axis_count == 1
    if axis_required is not True or not axis_count_ok:
        errors.append(
            format_error(
                "CONTRAST_GATE_REQUIRES_SINGLE_PRIMARY_AXIS_POLICY",
                path,
                "contrast_policy must require exactly one primary intervention axis "
                "(primary_intervention_axis_required=true and "
                "required_primary_intervention_axis_count=1); got "
                f"primary_intervention_axis_required={axis_required!r}, "
                f"required_primary_intervention_axis_count={axis_count!r}.",
            )
        )

    # --- invariant + materiality criteria must be complete -------------------
    criteria_problems: list[str] = []
    invariant_ids = set(_ids(invariant_dimensions))
    missing_invariants = [d for d in MANDATORY_INVARIANT_DIMENSIONS if d not in invariant_ids]
    if missing_invariants:
        criteria_problems.append("missing invariant_dimensions: " + ", ".join(missing_invariants))

    materiality_ids = set(_ids(materiality_criteria))
    missing_materiality = [m for m in MANDATORY_MATERIALITY_CRITERIA if m not in materiality_ids]
    if missing_materiality:
        criteria_problems.append("missing materiality_criteria: " + ", ".join(missing_materiality))

    if contrast_policy.get("materiality_evidence_required") is not True:
        criteria_problems.append("contrast_policy.materiality_evidence_required must be true")
    else:
        for crit in materiality_criteria:
            if not isinstance(crit, dict):
                continue
            crit_id = str(crit.get("id", "")).strip() or "<missing-id>"
            evidence = crit.get("evidence_required")
            if not isinstance(evidence, list) or not [e for e in evidence if str(e).strip()]:
                criteria_problems.append(
                    f"materiality criterion {crit_id!r} lacks a non-empty evidence_required list"
                )
    if criteria_problems:
        errors.append(
            format_error(
                "CONTRAST_GATE_REQUIRES_COMPLETE_CRITERIA",
                path,
                "invariant_dimensions and materiality_criteria must be complete and "
                "evidence-bound; " + "; ".join(criteria_problems),
            )
        )

    # --- semantic ids must be unique within each list ------------------------
    # uniqueItems in the schema only blocks fully identical objects; two entries
    # with the same id but different prose would slip through, so check ids here.
    duplicate_id_problems: list[str] = []
    for label, items in (
        ("invariant_dimensions", invariant_dimensions),
        ("controlled_secondary_dimensions", controlled_dimensions),
        ("materiality_criteria", materiality_criteria),
        ("confounder_controls", confounder_controls),
    ):
        dups = _duplicates(_ids(items))
        if dups:
            duplicate_id_problems.append(f"{label}: " + ", ".join(dups))
    if duplicate_id_problems:
        errors.append(
            format_error(
                "CONTRAST_GATE_REQUIRES_UNIQUE_SEMANTIC_IDS",
                path,
                "ids must be unique within each criteria list; duplicated — "
                + "; ".join(duplicate_id_problems),
            )
        )

    # --- confounder controls must be complete --------------------------------
    confounder_ids = set(_ids(confounder_controls))
    missing_confounders = [c for c in MANDATORY_CONFOUNDER_CONTROLS if c not in confounder_ids]
    if missing_confounders:
        errors.append(
            format_error(
                "CONTRAST_GATE_REQUIRES_COMPLETE_CONFOUNDER_CONTROLS",
                path,
                "confounder_controls must cover the mandatory set; missing: "
                + ", ".join(missing_confounders),
            )
        )

    # --- gate_status / permission / decision consistency ---------------------
    consistency_problems: list[str] = []
    if gate_status == "criteria_defined" and design_allowed is not True:
        consistency_problems.append(
            f"gate_status=criteria_defined requires run_004_design_allowed=true (got {design_allowed!r})"
        )
    if gate_status == "blocked" and design_allowed is not False:
        consistency_problems.append(
            f"gate_status=blocked requires run_004_design_allowed=false (got {design_allowed!r})"
        )
    decision_status = str(decision.get("status", "")).strip()
    if decision_status != gate_status:
        consistency_problems.append(
            f"decision.status={decision_status!r} must equal gate_status={gate_status!r}"
        )
    if consistency_problems:
        errors.append(
            format_error(
                "CONTRAST_GATE_REQUIRES_STATUS_PERMISSION_CONSISTENCY",
                path,
                "gate status, design permission, and decision must be consistent; "
                + "; ".join(consistency_problems),
            )
        )

    # --- gate must forbid execution, result assessment, and comparison -------
    forbidden_problems: list[str] = []
    if execution_allowed:
        forbidden_problems.append("run_004_execution_allowed must be false")
    if assessment_allowed:
        forbidden_problems.append("result_assessment_allowed_after_gate must be false")
    if comparison_ready:
        forbidden_problems.append("comparison_ready_after_gate must be false")
    if forbidden_problems:
        errors.append(
            format_error(
                "CONTRAST_GATE_FORBIDS_EXECUTION_AND_ASSESSMENT",
                path,
                "a design-criteria gate must not authorize execution, result "
                "assessment, or comparison; " + "; ".join(forbidden_problems),
            )
        )

    # --- mandatory anti-overclaim non-claims ---------------------------------
    declared = {str(item).strip().lower() for item in does_not_establish}
    missing_mandatory = [d for d in MANDATORY_DOES_NOT_ESTABLISH if d not in declared]
    if missing_mandatory:
        errors.append(
            format_error(
                "CONTRAST_GATE_REQUIRES_MANDATORY_NON_CLAIMS",
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
                    "CONTRAST_GATE_REQUIRES_SAFE_EXISTING_SOURCE_PATHS",
                    path,
                    f"source_evidence path '{res.rel_path}' resolves outside the repo root.",
                )
            )
        elif res.code == "NOT_FOUND":
            errors.append(
                format_error(
                    "CONTRAST_GATE_REQUIRES_SAFE_EXISTING_SOURCE_PATHS",
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
    return sorted(experiments_dir.glob(GATE_GLOB))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Model-Lab condition-contrast design-gate artifacts."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="condition-contrast-design-gate YAML files (default: discover all under experiments/).",
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
                "ℹ️ No model-lab-condition-contrast-design-gate artifacts found; "
                "model-lab-condition-contrast-design-gate validation skipped."
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
        f"Model-lab-condition-contrast-design-gate artifacts: checked={checked}, "
        f"passed={passed}, failed={checked - passed}"
    )
    return highest_exit_code


if __name__ == "__main__":
    sys.exit(main())
