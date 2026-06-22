#!/usr/bin/env python3
"""validate_model_lab_condition_contrast_design_gate.py — Validator for Model-Lab condition-contrast design-gate artifacts.

A condition-contrast design-gate artifact
(``experiments/<series>/results/condition-contrast-design-gate.yml``) defines the
machine-readable criteria a *future* Run-004 condition-contrast design must
satisfy. v1 has exactly one honest state: a fully defined criteria gate
(gate_status=criteria_defined). It is a design-criteria gate only: it does NOT
select a primary intervention axis, does NOT select a concrete condition, does
NOT execute Run-004, does NOT allow a result_assessment, does NOT make the series
comparison-ready, and does NOT resolve weak_condition_contrast.

The fixed v1 status, permissions, contrast policy, source kinds, control
vocabulary, and structural materiality evidence are pinned in the JSON schema as
const / enum / required, so this validator only enforces the genuinely semantic,
cross-artifact and completeness rules.

This validator complements — it does not replace — the runtime-evidence gate,
the result-assessment-readiness gate, the dependency-risk-caveat scope, and the
next-blocker triage. The triage records which still-open blocker to handle next;
this gate records what a future design for the top-ranked blocker
(weak_condition_contrast) must satisfy.

Enforced semantic rules (exit 1):
  CONTRAST_GATE_REQUIRES_SINGLE_TRIAGE_SOURCE
                                   source_evidence does not contain exactly one
                                   next_blocker_triage source.
  CONTRAST_GATE_REQUIRES_SINGLE_READINESS_SOURCE
                                   source_evidence does not contain exactly one
                                   readiness_gate source.
  CONTRAST_GATE_REQUIRES_READABLE_FOUNDATIONAL_SOURCES
                                   a declared foundational source (next_blocker_triage
                                   or readiness_gate) is not a readable YAML mapping
                                   (not a regular file, wrong extension, unreadable,
                                   invalid YAML, or not a mapping). The gate must never
                                   pass while a declared foundational source could not
                                   be read.
  CONTRAST_GATE_REQUIRES_MATCHING_SOURCE_IDENTITY
                                   a triage source is not a
                                   model_lab_next_blocker_triage for this gate's
                                   series, or a readiness source is not a
                                   result_assessment_readiness for this gate's
                                   series and challenge_version.
  CONTRAST_GATE_REQUIRES_TRIAGE_RECOMMENDATION
                                   the readable triage does not recommend this gate
                                   (recommended_next_task.id == the design-gate task
                                   id) for the gate's own target_blocker.
  CONTRAST_GATE_REQUIRES_BLOCKED_READINESS
                                   no readable readiness_gate explicitly confirms a
                                   blocked assessment (readiness_status=blocked,
                                   result_assessment_allowed is literally False,
                                   comparison_ready is literally False; a missing
                                   field is NOT treated as False).
  CONTRAST_GATE_REQUIRES_OPEN_TARGET_BLOCKER
                                   the gate's target_blocker is not listed as open
                                   in the referenced triage's remaining_blockers
                                   and/or the referenced readiness gate's blockers.
  CONTRAST_GATE_REQUIRES_COMPLETE_CRITERIA
                                   invariant_dimensions, dimensions_to_control_when_not_primary,
                                   or materiality_criteria omit a mandatory id.
  CONTRAST_GATE_REQUIRES_UNIQUE_SEMANTIC_IDS
                                   two entries within invariant_dimensions,
                                   dimensions_to_control_when_not_primary,
                                   materiality_criteria, or confounder_controls
                                   share an id (uniqueItems only blocks identical
                                   objects).
  CONTRAST_GATE_REQUIRES_COMPLETE_CONFOUNDER_CONTROLS
                                   confounder_controls omit a mandatory id or carry
                                   an effect_if_uncontrolled other than the declared
                                   one for that id.
  CONTRAST_GATE_REQUIRES_MANDATORY_NON_CLAIMS
                                   does_not_establish omits a static baseline
                                   non-claim (including weak_condition_contrast_resolved).
  CONTRAST_GATE_REQUIRES_SAFE_EXISTING_SOURCE_PATHS
                                   a referenced source_evidence path resolves
                                   outside the repo (escape), does not exist, or
                                   exists but is not a regular file.

v1 is the condition-contrast design gate for weak_condition_contrast.
The schema form fixes this contract identity.
Triage and readiness confirm the recommendation and open status.
Readiness state continues to live in the source artifacts.
weak_condition_contrast_resolved is a static mandatory non-claim.

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

# Source kinds. Exactly one of each foundational kind is required and must be a
# readable YAML mapping; the context kinds are checked only for existence as safe
# regular files, never for prose content.
TRIAGE_KIND = "next_blocker_triage"
READINESS_KIND = "readiness_gate"
FOUNDATIONAL_KINDS = (TRIAGE_KIND, READINESS_KIND)

# Cross-referenced artifact identities. A next_blocker_triage source must be a
# model_lab_next_blocker_triage artifact, and a readiness_gate source must be a
# result_assessment_readiness artifact, both for this gate's own series.
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

# Outcome surfaces a future design must keep fixed.
MANDATORY_INVARIANT_DIMENSIONS = (
    "challenge_contract",
    "acceptance_surface",
    "evaluation_criteria",
    "verification_surface",
    "evidence_capture",
)

# Dimensions a future design must control or document whenever they are not the
# single primary intervention axis. This gate does not select the axis or decide
# eligibility; it only fixes the control treatment for the non-primary case.
MANDATORY_DIMENSIONS_TO_CONTROL_WHEN_NOT_PRIMARY = (
    "model_identity_and_version",
    "tool_and_agent_mode",
    "sampling_configuration",
    "human_intervention",
    "dependency_and_runtime_environment",
    "test_harness",
)

# Minimum materiality criteria a future design must satisfy.
MANDATORY_MATERIALITY_CRITERIA = (
    "single_primary_intervention_axis",
    "operationally_verifiable_difference",
    "no_cosmetic_relabeling",
    "fixed_outcome_surface",
    "provenance_before_execution",
)

# Minimum confounder controls and the effect each is required to declare. The
# effect describes the future design's reaction to the confounder, not a confounder
# that has already occurred, so a 'blocks_design' entry does not block this gate.
EXPECTED_CONFOUNDER_EFFECTS = {
    "multi_axis_drift": "blocks_design",
    "acceptance_or_test_drift": "blocks_design",
    "unequal_human_intervention": "blocks_design",
    "dependency_or_runtime_drift": "must_be_reported",
    "post_hoc_condition_rework": "blocks_design",
    "self_reported_independence_as_external_proof": "must_be_reported",
}

# Static baseline anti-overclaim non-claims every condition-contrast gate must carry.
# The gate defines criteria only: it never selects a primary axis or a concrete
# condition, so those are mandatory non-claims too.
MANDATORY_DOES_NOT_ESTABLISH = (
    "weak_condition_contrast_resolved",
    "primary_intervention_axis_selected",
    "concrete_condition_selected",
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

# Human-readable descriptions for foundational-source readability failures.
READABILITY_MESSAGES = {
    "NOT_FILE": "is not a regular file",
    "UNSUPPORTED_YAML_EXTENSION": "is not a .yml/.yaml file",
    "READ_ERROR": "could not be read as UTF-8 text",
    "YAML_PARSE_ERROR": "is not valid YAML",
    "YAML_NOT_MAPPING": "is not a YAML mapping",
}

DRIVE_LETTER_RE = re.compile(r"^[A-Za-z]:")


def _has_forbidden_path_codepoint(text: str) -> bool:
    """True if text contains a C0 control char, DEL, or a lone UTF-16 surrogate.

    These are rejected as form errors (the repoRelativePath schema pattern blocks
    them too) and keep the resolver fail-closed before pathlib: NUL raises
    ValueError and lone surrogates raise UnicodeError during filesystem resolution.
    This is a narrow crash-surface guard, not a general Unicode/Bidi naming policy.
    """
    return any(
        ord(char) <= 0x1F or ord(char) == 0x7F or 0xD800 <= ord(char) <= 0xDFFF
        for char in text
    )


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def load_schema_validator() -> Draft202012Validator:
    try:
        raw = SCHEMA_PATH.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise RuntimeError(f"schema file missing: {display_path(SCHEMA_PATH)}") from exc
    except UnicodeDecodeError as exc:
        raise RuntimeError(
            f"schema file is not valid UTF-8: {display_path(SCHEMA_PATH)}"
        ) from exc
    except OSError as exc:
        raise RuntimeError(
            f"schema file could not be read: {display_path(SCHEMA_PATH)}: {exc}"
        ) from exc

    try:
        schema = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"schema file invalid JSON: {display_path(SCHEMA_PATH)}: {exc}"
        ) from exc

    try:
        Draft202012Validator.check_schema(schema)
        return Draft202012Validator(schema)
    except SchemaError as exc:
        raise RuntimeError(
            f"schema invalid: {display_path(SCHEMA_PATH)}: {exc.message}"
        ) from exc


def load_yaml(path: Path) -> dict:
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"file missing: {display_path(path)}") from exc
    except UnicodeDecodeError as exc:
        raise ValueError(f"file is not valid UTF-8: {display_path(path)}") from exc
    except OSError as exc:
        raise ValueError(f"file could not be read: {display_path(path)}: {exc}") from exc

    try:
        loaded = yaml.safe_load(raw)
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
    ``(None, code)`` where ``code`` is "ESCAPE" (forbidden C0/DEL/surrogate
    codepoint / absolute / drive-letter / backslash / lexical ``..`` / symlink
    leading out of repo / a value pathlib cannot safely resolve / otherwise
    resolves outside root) or "NOT_FOUND" (repo-internal but missing).

    Mirrors the helper in validate_model_lab_next_blocker_triage.py; kept small and
    local rather than shared to avoid coupling the validators.
    """
    raw_text = str(rel_path)
    # Reject forbidden codepoints on the raw value (before strip) so an edge tab or
    # control character cannot be normalized away; the schema pattern also blocks these.
    if _has_forbidden_path_codepoint(raw_text):
        return None, "ESCAPE"
    if raw_text != raw_text.strip():
        return None, "ESCAPE"
    text = raw_text
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
        try:
            lax = candidate.resolve(strict=False)
        except (OSError, RuntimeError, ValueError, UnicodeError):
            return None, "ESCAPE"
        return (None, "NOT_FOUND") if _inside(lax, root) else (None, "ESCAPE")
    except (OSError, RuntimeError, ValueError, UnicodeError):
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
    """One source_evidence entry, resolved (path safety + content) exactly once.

    ``code`` is "ESCAPE" / "NOT_FOUND" / None (path safety + existence).
    ``readability_error`` is one of NOT_FILE / UNSUPPORTED_YAML_EXTENSION /
    READ_ERROR / YAML_PARSE_ERROR / YAML_NOT_MAPPING / None and captures the
    content-level outcome (YAML extension/parse/mapping checks run only for
    foundational kinds; NOT_FILE can apply to any kind). ``loaded_yaml`` is the
    parsed mapping for a readable foundational source, else None. Parse failures
    are recorded explicitly, never swallowed into loaded_yaml=None.
    """

    rel_path: str
    kind: str
    resolved: Path | None
    code: str | None
    readability_error: str | None
    loaded_yaml: dict | None


def resolve_source_evidence_entries(
    data: dict, repo_root: Path
) -> list[SourceEvidenceResolution]:
    """Resolve every source_evidence entry once (path safety + content readability).

    Each source entry is resolved once, and each foundational YAML document is read
    and parsed once. The resulting resolution object is reused by later checks.
    """
    resolutions: list[SourceEvidenceResolution] = []
    for entry in _source_evidence_entries(data):
        raw_rel = str(entry.get("path", ""))
        rel = raw_rel.strip()
        kind = str(entry.get("kind", "")).strip()
        # Pass the raw (unstripped) path so the resolver can independently reject edge
        # control characters; rel stays the normalized display form for diagnostics.
        resolved, code = resolve_repo_relative_path(raw_rel, repo_root, must_exist=True)
        readability_error: str | None = None
        loaded: dict | None = None
        if code is None and resolved is not None:
            if not resolved.is_file():
                readability_error = "NOT_FILE"
            elif kind in FOUNDATIONAL_KINDS:
                if resolved.suffix.lower() not in (".yml", ".yaml"):
                    readability_error = "UNSUPPORTED_YAML_EXTENSION"
                else:
                    try:
                        raw = resolved.read_text(encoding="utf-8")
                    except (OSError, UnicodeError):
                        readability_error = "READ_ERROR"
                    else:
                        try:
                            doc = yaml.safe_load(raw)
                        except yaml.YAMLError:
                            readability_error = "YAML_PARSE_ERROR"
                        else:
                            if not isinstance(doc, dict):
                                readability_error = "YAML_NOT_MAPPING"
                            else:
                                loaded = doc
        resolutions.append(
            SourceEvidenceResolution(
                rel_path=rel,
                kind=kind,
                resolved=resolved,
                code=code,
                readability_error=readability_error,
                loaded_yaml=loaded,
            )
        )
    return resolutions


def _readiness_blocked_confirmed(readiness_docs: list[dict]) -> bool:
    """True if a referenced readiness_gate explicitly confirms a blocked assessment.

    Requires all three signals to be present and explicit: readiness_status=blocked,
    result_assessment_allowed is literally False, and comparison_ready is literally
    False. A missing field is NOT treated as False. Mirrors the cross-artifact read
    in validate_model_lab_next_blocker_triage.py.
    """
    for doc in readiness_docs:
        status = doc.get(READINESS_STATUS_KEY)
        allowed = doc.get(RESULT_ASSESSMENT_ALLOWED_KEY)
        comparison = doc.get(COMPARISON_READY_KEY)
        if status == "blocked" and allowed is False and comparison is False:
            return True
    return False


def _triage_recommends_gate(triage_docs: list[dict], target_blocker: str) -> bool:
    """True if a referenced triage recommends this design gate for the target blocker."""
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
    invariant_dimensions = data.get("invariant_dimensions", []) or []
    dimensions_to_control = data.get("dimensions_to_control_when_not_primary", []) or []
    materiality_criteria = data.get("materiality_criteria", []) or []
    confounder_controls = data.get("confounder_controls", []) or []
    does_not_establish = data.get("does_not_establish", []) or []

    # Resolve every source_evidence path (and read foundational YAML) exactly once;
    # the triage, readiness, identity, and path checks all reuse this list.
    resolutions = resolve_source_evidence_entries(data, repo_root)
    triage_paths = [
        (r.rel_path, r.loaded_yaml)
        for r in resolutions
        if r.kind == TRIAGE_KIND and r.loaded_yaml is not None
    ]
    readiness_paths = [
        (r.rel_path, r.loaded_yaml)
        for r in resolutions
        if r.kind == READINESS_KIND and r.loaded_yaml is not None
    ]
    triage_docs = [doc for _, doc in triage_paths]
    readiness_docs = [doc for _, doc in readiness_paths]

    # --- exactly one foundational triage / readiness source ------------------
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

    # --- foundational sources must be readable YAML mappings -----------------
    # A declared foundational source that is unsafe/missing is reported by the path
    # rule; one that exists but is not a readable YAML mapping is reported here, so
    # the gate can never pass while its foundational evidence could not be read.
    readable_problems = [
        f"{r.rel_path} ({r.kind}) {READABILITY_MESSAGES.get(r.readability_error, r.readability_error)}"
        for r in resolutions
        if r.kind in FOUNDATIONAL_KINDS and r.code is None and r.readability_error is not None
    ]
    if readable_problems:
        errors.append(
            format_error(
                "CONTRAST_GATE_REQUIRES_READABLE_FOUNDATIONAL_SOURCES",
                path,
                "each foundational source (next_blocker_triage, readiness_gate) must be a "
                "readable YAML mapping; offending: " + "; ".join(readable_problems),
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
    if readiness_docs and not _readiness_blocked_confirmed(readiness_docs):
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

    # --- invariant + controlled-secondary + materiality criteria complete ----
    criteria_problems: list[str] = []
    for label, mandatory, items in (
        ("invariant_dimensions", MANDATORY_INVARIANT_DIMENSIONS, invariant_dimensions),
        ("dimensions_to_control_when_not_primary", MANDATORY_DIMENSIONS_TO_CONTROL_WHEN_NOT_PRIMARY, dimensions_to_control),
        ("materiality_criteria", MANDATORY_MATERIALITY_CRITERIA, materiality_criteria),
    ):
        present = set(_ids(items))
        missing = [m for m in mandatory if m not in present]
        if missing:
            criteria_problems.append(f"{label}: " + ", ".join(missing))
    if criteria_problems:
        errors.append(
            format_error(
                "CONTRAST_GATE_REQUIRES_COMPLETE_CRITERIA",
                path,
                "invariant_dimensions, dimensions_to_control_when_not_primary and "
                "materiality_criteria must each cover their mandatory id set; missing — "
                + "; ".join(criteria_problems),
            )
        )

    # --- semantic ids must be unique within each list ------------------------
    duplicate_id_problems: list[str] = []
    for label, items in (
        ("invariant_dimensions", invariant_dimensions),
        ("dimensions_to_control_when_not_primary", dimensions_to_control),
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

    # --- confounder controls must be complete with their declared effects ----
    confounder_effects = {
        str(c.get("id", "")).strip(): str(c.get("effect_if_uncontrolled", "")).strip()
        for c in confounder_controls
        if isinstance(c, dict) and str(c.get("id", "")).strip()
    }
    confounder_problems: list[str] = []
    for cid, expected_effect in EXPECTED_CONFOUNDER_EFFECTS.items():
        if cid not in confounder_effects:
            confounder_problems.append(f"missing: {cid}")
        elif confounder_effects[cid] != expected_effect:
            confounder_problems.append(
                f"{cid}: effect_if_uncontrolled={confounder_effects[cid]!r} (expected {expected_effect!r})"
            )
    if confounder_problems:
        errors.append(
            format_error(
                "CONTRAST_GATE_REQUIRES_COMPLETE_CONFOUNDER_CONTROLS",
                path,
                "confounder_controls must cover the mandatory set, each with its declared "
                "effect_if_uncontrolled; " + "; ".join(confounder_problems),
            )
        )

    # --- mandatory anti-overclaim non-claims ---------------------------------
    declared = {str(item).strip().lower() for item in does_not_establish}
    missing_mandatory = [
        item for item in MANDATORY_DOES_NOT_ESTABLISH
        if item not in declared
    ]
    if missing_mandatory:
        errors.append(
            format_error(
                "CONTRAST_GATE_REQUIRES_MANDATORY_NON_CLAIMS",
                path,
                "does_not_establish must include all static anti-overclaim non-claims; "
                "missing: " + ", ".join(missing_mandatory),
            )
        )

    # --- source_evidence path escape / existence / regular-file --------------
    # ESCAPE and NOT_FOUND are path-safety problems for any source kind. A
    # non-regular-file target is reported here for context sources; for foundational
    # sources it is a readability failure (reported above), so it is not duplicated.
    safe_problems: list[str] = []
    for res in resolutions:
        if res.code == "ESCAPE":
            safe_problems.append(f"{res.rel_path}: resolves outside the repo root")
        elif res.code == "NOT_FOUND":
            safe_problems.append(f"{res.rel_path}: does not exist")
        elif res.readability_error == "NOT_FILE" and res.kind not in FOUNDATIONAL_KINDS:
            safe_problems.append(f"{res.rel_path}: exists but is not a regular file")
    if safe_problems:
        errors.append(
            format_error(
                "CONTRAST_GATE_REQUIRES_SAFE_EXISTING_SOURCE_PATHS",
                path,
                "every source_evidence path must be a safe, existing, regular repo file; "
                "offending: " + "; ".join(safe_problems),
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
