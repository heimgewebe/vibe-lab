#!/usr/bin/env python3
"""validate_model_lab_condition_design.py — Validator for Model-Lab condition-design artifacts.

A condition-design artifact
(``experiments/<series>/artifacts/run-004-condition-contrast-design/condition-design.yml``)
freezes the paired condition contrast a *future* Model-Lab Run-004 must run. v1 has
exactly one honest state: a design frozen before execution (design_status=frozen). It
selects a single primary intervention axis (workflow_protocol) and two future arms
(control=direct_implementation, treatment=spec_first) for the open
weak_condition_contrast blocker. It does NOT execute a run, does NOT bind the execution
environment, does NOT allow a result_assessment, does NOT make the series
comparison-ready, and does NOT resolve weak_condition_contrast.

The fixed v1 status, permissions, primary axis, freeze flag, and decision are pinned in
the JSON schema as const, so this validator only enforces the genuinely semantic,
cross-artifact, completeness, freeze-integrity, path-safety, and isolation rules.

This validator complements — it does not replace — the condition-contrast design gate.
The gate records the criteria a Run-004 design must satisfy; this design selects the
single primary axis and the two concrete conditions and freezes them before execution.

Enforced semantic rules (exit 1):
  CONDITION_DESIGN_REQUIRES_SINGLE_GATE_SOURCE
                                   source_evidence does not contain exactly one
                                   condition_contrast_design_gate source.
  CONDITION_DESIGN_REQUIRES_READABLE_FOUNDATIONAL_SOURCES
                                   a declared foundational source
                                   (condition_contrast_design_gate / readiness_gate) is
                                   not a readable YAML mapping.
  CONDITION_DESIGN_REQUIRES_MATCHING_SOURCE_IDENTITY
                                   a gate source is not a
                                   model_lab_condition_contrast_design_gate for this
                                   series, or a readiness source is not a
                                   result_assessment_readiness for this series and
                                   challenge_version.
  CONDITION_DESIGN_REQUIRES_GATE_AUTHORIZES_DESIGN
                                   the gate source does not authorize a Run-004 design
                                   (gate_status=criteria_defined, run_004_design_allowed
                                   literally True, run_004_execution_allowed literally
                                   False).
  CONDITION_DESIGN_REQUIRES_BLOCKED_READINESS
                                   the gate still permits assessment/comparison, or no
                                   single readiness_gate explicitly confirms a blocked
                                   assessment (readiness_status=blocked,
                                   result_assessment_allowed literally False,
                                   comparison_ready literally False; a missing field is
                                   NOT treated as False).
  CONDITION_DESIGN_REQUIRES_OPEN_TARGET_BLOCKER
                                   the target_blocker is not open in the gate and the
                                   referenced readiness gate.
  CONDITION_DESIGN_REQUIRES_EXACTLY_TWO_ARMS
                                   arms is not exactly one control and one treatment.
  CONDITION_DESIGN_REQUIRES_SINGLE_PRIMARY_AXIS
                                   the primary axis is not workflow_protocol, or the two
                                   arms do not take different workflow_protocol values.
  CONDITION_DESIGN_REQUIRES_MATERIAL_CONTRAST
                                   the workflow_protocol contrast is not the v1 material,
                                   pre-execution-observable one (control=direct
                                   implementation with no required upfront spec;
                                   treatment=spec_first requiring a complete upfront spec).
  CONDITION_DESIGN_REQUIRES_ONLY_PRIMARY_AXIS_DIFFERENCE
                                   the two arms differ in a non-primary (shared) field, so
                                   the design carries a second operative difference.
  CONDITION_DESIGN_REQUIRES_SHARED_VERIFICATION
                                   the two arms do not reference the same verification
                                   protocol.
  CONDITION_DESIGN_REQUIRES_SHARED_MEASUREMENT
                                   the two arms do not reference the same measurement
                                   protocol.
  CONDITION_DESIGN_REQUIRES_SHARED_INTERVENTION_RULES
                                   the two arms do not share the same intervention profile.
  CONDITION_DESIGN_REQUIRES_COMPLETE_CONTROL_BINDINGS
                                   controlled_dimensions omit a mandatory non-primary
                                   dimension id.
  CONDITION_DESIGN_REQUIRES_COMPLETE_CONFOUNDER_CONTROLS
                                   confounder_controls omit a mandatory id or carry an
                                   effect_if_uncontrolled other than the declared one.
  CONDITION_DESIGN_REQUIRES_UNIQUE_SEMANTIC_IDS
                                   two entries within arms, controlled_dimensions, or
                                   confounder_controls share an id.
  CONDITION_DESIGN_REQUIRES_VALID_FREEZE
                                   the freeze manifest is missing/unreadable, not frozen
                                   before execution, lacks a change rule, hashes itself
                                   (cycle), omits the design or a protocol artifact, or
                                   carries a SHA-256 that does not match the file.
  CONDITION_DESIGN_FORBIDS_EXECUTION_ARTIFACTS
                                   the design directory contains a forbidden execution
                                   artifact (run.yml, run_meta.json, implementation/, ...).
  CONDITION_DESIGN_REQUIRES_MANDATORY_NON_CLAIMS
                                   does_not_establish omits a static baseline non-claim,
                                   or lists a now-established selection claim
                                   (primary_intervention_axis_selected /
                                   concrete_condition_selected).
  CONDITION_DESIGN_REQUIRES_SAFE_EXISTING_PATHS
                                   a referenced repo path resolves outside the repo,
                                   does not exist, or is not a regular file.

Exit codes:
  0  valid
  1  semantic violation
  2  schema error / parse error / tool error

Requires: python3 -m pip install pyyaml jsonschema
"""

from __future__ import annotations

import argparse
import hashlib
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
        "ERROR: Missing dependencies for model-lab-condition-design validation. "
        "Install PyYAML and jsonschema.",
        file=sys.stderr,
    )
    raise SystemExit(2) from exc


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCHEMA_PATH = REPO_ROOT / "schemas" / "model-lab-condition-design.v1.schema.json"

DESIGN_GLOB = "*/artifacts/*/condition-design.yml"

# Source kinds. Exactly one of each foundational kind is required and must be a readable
# YAML mapping; the context kinds are checked only for existence as safe regular files.
GATE_KIND = "condition_contrast_design_gate"
READINESS_KIND = "readiness_gate"
FOUNDATIONAL_KINDS = (GATE_KIND, READINESS_KIND)

# Cross-referenced artifact identities.
GATE_ARTIFACT_TYPE = "model_lab_condition_contrast_design_gate"
READINESS_ARTIFACT_TYPE = "result_assessment_readiness"

EXPECTED_TARGET_BLOCKER = "weak_condition_contrast"
EXPECTED_PRIMARY_AXIS = "workflow_protocol"
CONTROL_WORKFLOW_PROTOCOL = "direct_implementation"
TREATMENT_WORKFLOW_PROTOCOL = "spec_first"

ARTIFACT_TYPE_KEY = "artifact_type"
SERIES_ID_KEY = "series_id"
CHALLENGE_VERSION_KEY = "challenge_version"

# The mandatory upfront-specification sections the treatment (spec_first) arm requires.
MANDATORY_TREATMENT_SPEC_SECTIONS = (
    "endpoint_matrix",
    "request_response_schemas",
    "validation_rules",
    "http_status_codes",
    "error_cases",
    "edge_cases",
    "persistence_assumptions",
    "planned_implementation_order",
)

# Every non-primary experimentally relevant dimension that must be bound identically
# across arms (the canonical set comes from the condition-contrast design gate; the
# primary axis workflow_protocol is deliberately NOT in this set).
MANDATORY_CONTROLLED_DIMENSIONS = (
    "challenge_contract",
    "acceptance_surface",
    "evaluation_criteria",
    "verification_surface",
    "evidence_capture",
    "model_identity_and_version",
    "tool_and_agent_mode",
    "sampling_configuration",
    "human_intervention",
    "dependency_and_runtime_environment",
    "test_harness",
)

# Minimum confounder controls and the effect each must declare (mirrors the gate).
EXPECTED_CONFOUNDER_EFFECTS = {
    "multi_axis_drift": "blocks_design",
    "acceptance_or_test_drift": "blocks_design",
    "unequal_human_intervention": "blocks_design",
    "dependency_or_runtime_drift": "must_be_reported",
    "post_hoc_condition_rework": "blocks_design",
    "self_reported_independence_as_external_proof": "must_be_reported",
}

# Static baseline anti-overclaim non-claims every condition-design artifact must carry.
MANDATORY_DOES_NOT_ESTABLISH = (
    "weak_condition_contrast_resolved",
    "run_004_execution_allowed",
    "run_004_executed",
    "execution_environment_bound",
    "result_assessment_allowed",
    "comparison_ready",
    "condition_effect",
    "model_quality",
    "comparative_superiority",
    "external_model_independence",
    "external_auditor_comparison_completed",
    "dependency_risk_remediated",
    "security_readiness",
    "production_readiness",
)

# These two states are ESTABLISHED by this PR, so they must not be listed as
# not-established. Listing them would deny the design's own contribution.
FORBIDDEN_SELECTION_NON_CLAIMS = (
    "primary_intervention_axis_selected",
    "concrete_condition_selected",
)

# Forbidden execution artifacts in the real design directory. Names are exact; the
# design's own measurement-protocol.yml / verification-protocol.yml are deliberately not
# in this list.
FORBIDDEN_EXECUTION_FILES = (
    "run.yml",
    "run_meta.json",
    "execution.txt",
    "measurement.yml",
    "auditor-output.yml",
    "comparability.yml",
    "evidence-pack.yml",
    "timing.txt",
    "package.json",
    "package-lock.json",
)
FORBIDDEN_EXECUTION_DIRS = ("implementation", "src", "tests")
FORBIDDEN_EXECUTION_GLOBS = ("execute-*.py", "verify-*.py")

# Arm fields allowed to differ between the two arms (the primary-axis surface). Every
# other arm field must be identical, or the design carries a second operative difference.
PRIMARY_AXIS_ARM_KEYS = frozenset(
    {"id", "role", "workflow_protocol", "workflow_protocol_ref", "workflow_protocol_spec"}
)

READABILITY_MESSAGES = {
    "NOT_FILE": "is not a regular file",
    "UNSUPPORTED_YAML_EXTENSION": "is not a .yml/.yaml file",
    "READ_ERROR": "could not be read as UTF-8 text",
    "YAML_PARSE_ERROR": "is not valid YAML",
    "YAML_NOT_MAPPING": "is not a YAML mapping",
}

DRIVE_LETTER_RE = re.compile(r"^[A-Za-z]:")


def _has_forbidden_path_codepoint(text: str) -> bool:
    """True if text contains a C0 control char, DEL, or a lone UTF-16 surrogate."""
    return any(
        ord(char) <= 0x1F or ord(char) == 0x7F or 0xD800 <= ord(char) <= 0xDFFF
        for char in text
    )


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except (OSError, RuntimeError, ValueError, UnicodeError):
        return str(path)


def _escape_source_path_char(char: str) -> str:
    codepoint = ord(char)
    if codepoint <= 0x1F or codepoint == 0x7F:
        if char == '\t': return r'\t'
        if char == '\n': return r'\n'
        if char == '\r': return r'\r'
        if char == '\f': return r'\f'
        if char == '\v': return r'\v'
        return f"\\x{codepoint:02x}"
    if 0xD800 <= codepoint <= 0xDFFF:
        return f"\\u{codepoint:04x}"
    if char.isspace() and char != ' ':
        if codepoint <= 0xFFFF:
            return f"\\u{codepoint:04x}"
        return f"\\U{codepoint:08x}"
    return char


def display_source_path(raw: str) -> str:
    if not isinstance(raw, str):
        return str(raw)

    leading_count = len(raw) - len(raw.lstrip())
    trailing_start = len(raw.rstrip())

    res = []
    for i, char in enumerate(raw):
        if char == ' ' and (i < leading_count or i >= trailing_start):
            res.append(r'\x20')
        else:
            res.append(_escape_source_path_char(char))

    return "".join(res)


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
    ``(None, code)`` where ``code`` is "ESCAPE" (forbidden codepoint / absolute /
    drive-letter / backslash / lexical ``..`` / symlink leading out of repo / a value
    pathlib cannot safely resolve / otherwise resolves outside root) or "NOT_FOUND"
    (repo-internal but missing). Mirrors the helper in the neighbouring Model-Lab
    validators; kept small and local rather than shared to avoid coupling them.
    """
    raw_text = str(rel_path)
    if _has_forbidden_path_codepoint(raw_text):
        return None, "ESCAPE"
    if raw_text != raw_text.strip():
        return None, "ESCAPE"
    text = raw_text
    if not text:
        return None, "ESCAPE"
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


def _sha256_of(path: Path) -> str | None:
    try:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(65536), b""):
                digest.update(chunk)
        return digest.hexdigest()
    except (OSError, ValueError):
        return None


def _source_evidence_entries(data: dict) -> list[dict]:
    return [item for item in (data.get("source_evidence", []) or []) if isinstance(item, dict)]


@dataclass(frozen=True)
class SourceEvidenceResolution:
    """One source_evidence entry, resolved (path safety + content) exactly once."""

    raw_rel_path: str
    rel_path: str
    kind: str
    resolved: Path | None
    code: str | None
    readability_error: str | None
    loaded_yaml: dict | None


def resolve_source_evidence_entries(
    data: dict, repo_root: Path
) -> list[SourceEvidenceResolution]:
    """Resolve every source_evidence entry once (path safety + content readability)."""
    resolutions: list[SourceEvidenceResolution] = []
    for entry in _source_evidence_entries(data):
        raw_rel = str(entry.get("path", ""))
        rel = raw_rel.strip()
        kind = str(entry.get("kind", "")).strip()
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
                raw_rel_path=raw_rel,
                rel_path=rel,
                kind=kind,
                resolved=resolved,
                code=code,
                readability_error=readability_error,
                loaded_yaml=loaded,
            )
        )
    return resolutions


def _source_identity_mismatches(
    docs_with_paths: list[tuple[str, dict]],
    *,
    expected_artifact_type: str,
    expected_series_id: str,
    expected_challenge_version: str | None = None,
) -> list[str]:
    problems: list[str] = []
    for raw_rel_path, doc in docs_with_paths:
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
            problems.append(f"{display_source_path(raw_rel_path)}: " + ", ".join(issues))
    return problems


def _gate_authorizes_design(gate_docs: list[dict]) -> bool:
    """True if a referenced gate explicitly authorizes a Run-004 design."""
    for doc in gate_docs:
        if (
            doc.get("gate_status") == "criteria_defined"
            and doc.get("run_004_design_allowed") is True
            and doc.get("run_004_execution_allowed") is False
        ):
            return True
    return False


def _gate_keeps_assessment_blocked(gate_docs: list[dict]) -> bool:
    """True if a referenced gate keeps assessment and comparison blocked after the gate."""
    for doc in gate_docs:
        if (
            doc.get("result_assessment_allowed_after_gate") is False
            and doc.get("comparison_ready_after_gate") is False
        ):
            return True
    return False


def _readiness_blocked_confirmed(readiness_docs: list[dict]) -> bool:
    """True if a referenced readiness_gate explicitly confirms a blocked assessment."""
    for doc in readiness_docs:
        if (
            doc.get("readiness_status") == "blocked"
            and doc.get("result_assessment_allowed") is False
            and doc.get("comparison_ready") is False
        ):
            return True
    return False


def _gate_target_open(gate_docs: list[dict], target_blocker: str) -> bool:
    for doc in gate_docs:
        if (
            str(doc.get("target_blocker", "")).strip() == target_blocker
            and str(doc.get("blocker_status_after_gate", "")).strip() == "open"
        ):
            return True
    return False


def _blocker_open_in(doc: dict, key: str, target: str) -> bool:
    for item in doc.get(key, []) or []:
        if not isinstance(item, dict):
            continue
        if str(item.get("id", "")).strip() == target and str(item.get("status", "")).strip() == "open":
            return True
    return False


def _duplicates(values: list) -> list:
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


def _arms_by_role(arms: list) -> tuple[dict | None, dict | None]:
    control = [a for a in arms if isinstance(a, dict) and a.get("role") == "control"]
    treatment = [a for a in arms if isinstance(a, dict) and a.get("role") == "treatment"]
    control_arm = control[0] if len(control) == 1 else None
    treatment_arm = treatment[0] if len(treatment) == 1 else None
    return control_arm, treatment_arm


def _spec_is_no_upfront_spec(spec: dict) -> bool:
    return (
        isinstance(spec, dict)
        and spec.get("pre_implementation_specification_required") is False
        and spec.get("implementation_may_begin_immediately") is True
        and not (spec.get("required_specification_sections") or [])
    )


def _spec_is_full_upfront_spec(spec: dict) -> bool:
    if not isinstance(spec, dict):
        return False
    if spec.get("pre_implementation_specification_required") is not True:
        return False
    if spec.get("implementation_may_begin_immediately") is not False:
        return False
    sections = {str(s).strip() for s in (spec.get("required_specification_sections") or [])}
    return all(section in sections for section in MANDATORY_TREATMENT_SPEC_SECTIONS)


def _execution_artifact_problems(design_dir: Path) -> list[str]:
    """Forbidden execution artifacts directly inside the design directory."""
    problems: list[str] = []
    try:
        if not design_dir.is_dir():
            return problems
    except OSError:
        return problems
    for name in FORBIDDEN_EXECUTION_FILES:
        try:
            if (design_dir / name).is_file():
                problems.append(name)
        except OSError:
            continue
    for name in FORBIDDEN_EXECUTION_DIRS:
        try:
            if (design_dir / name).is_dir():
                problems.append(name + "/")
        except OSError:
            continue
    for pattern in FORBIDDEN_EXECUTION_GLOBS:
        try:
            for match in sorted(design_dir.glob(pattern)):
                if match.is_file():
                    problems.append(match.name)
        except OSError:
            continue
    return sorted(set(problems))


def _freeze_problems(data: dict, repo_root: Path) -> list[str]:
    """Validate the SHA-256 freeze manifest: integrity, no cycle, complete coverage."""
    problems: list[str] = []
    freeze = data.get("freeze")
    if not isinstance(freeze, dict):
        return ["freeze block missing or malformed"]

    if freeze.get("frozen_before_execution") is not True:
        problems.append("freeze.frozen_before_execution must be literally true")

    manifest_rel = str(freeze.get("freeze_manifest_ref", ""))
    manifest_path, code = resolve_repo_relative_path(manifest_rel, repo_root, must_exist=True)
    if code is not None or manifest_path is None or not manifest_path.is_file():
        problems.append(
            f"freeze_manifest_ref {display_source_path(manifest_rel)} is not a safe, existing, regular file"
        )
        return problems

    try:
        manifest = load_yaml(manifest_path)
    except (FileNotFoundError, ValueError):
        problems.append(f"freeze manifest {display_path(manifest_path)} is not a readable YAML mapping")
        return problems

    if manifest.get("frozen_before_execution") is not True:
        problems.append("freeze manifest frozen_before_execution must be literally true")
    if not str(manifest.get("change_rule", "")).strip():
        problems.append("freeze manifest must declare a non-empty change_rule")

    entries = manifest.get("hashes")
    if not isinstance(entries, list) or not entries:
        problems.append("freeze manifest hashes must be a non-empty list")
        return problems

    hashed_resolved: set[Path] = set()
    declared_resolved: set[Path] = set()
    for idx, entry in enumerate(entries):
        if not isinstance(entry, dict):
            problems.append(f"hashes[{idx}] is not a mapping")
            continue
        entry_rel = str(entry.get("path", ""))
        declared = str(entry.get("sha256", "")).strip().lower()
        resolved, ecode = resolve_repo_relative_path(entry_rel, repo_root, must_exist=True)
        if ecode is not None or resolved is None or not resolved.is_file():
            problems.append(f"hashed path {display_source_path(entry_rel)} is not a safe, existing, regular file")
            continue
        # Track every declared (resolvable) path so a self-reference is caught by path
        # presence, independent of whether its (circular) hash happens to match.
        declared_resolved.add(resolved)
        if not re.fullmatch(r"[0-9a-f]{64}", declared):
            problems.append(f"hashed path {display_source_path(entry_rel)} has a malformed sha256")
            continue
        actual = _sha256_of(resolved)
        if actual is None:
            problems.append(f"hashed path {display_source_path(entry_rel)} could not be hashed")
            continue
        if actual != declared:
            problems.append(f"sha256 mismatch for {display_source_path(entry_rel)}")
            continue
        hashed_resolved.add(resolved)

    # No self-hash: the manifest must not list itself (would be a cycle).
    if manifest_path in declared_resolved:
        problems.append("freeze manifest must not hash itself (cycle)")

    # The design artifact and every protocol artifact it references must be frozen.
    required_refs: dict[str, str] = {}
    design_self = str(data.get("design_artifact_path", ""))
    if design_self:
        required_refs[design_self] = "design_artifact_path"
    for arm in data.get("arms", []) or []:
        if not isinstance(arm, dict):
            continue
        for key in (
            "workflow_protocol_ref",
            "common_condition_ref",
            "verification_protocol_ref",
            "measurement_protocol_ref",
        ):
            ref = str(arm.get(key, ""))
            if ref:
                required_refs.setdefault(ref, key)

    for ref, label in sorted(required_refs.items()):
        resolved, ecode = resolve_repo_relative_path(ref, repo_root, must_exist=True)
        if ecode is not None or resolved is None:
            # Path safety/existence of these refs is also reported by SAFE_EXISTING_PATHS;
            # here we only assert freeze coverage, so skip unresolvable refs.
            continue
        if resolved not in hashed_resolved:
            problems.append(f"{label} {display_source_path(ref)} is not covered by the freeze manifest")

    return problems


def _collect_repo_refs(data: dict) -> list[tuple[str, str]]:
    """(raw_path, label) for every repo path the design references and must keep safe."""
    refs: list[tuple[str, str]] = []
    design_self = str(data.get("design_artifact_path", ""))
    if design_self:
        refs.append((design_self, "design_artifact_path"))
    freeze = data.get("freeze")
    if isinstance(freeze, dict) and freeze.get("freeze_manifest_ref"):
        refs.append((str(freeze.get("freeze_manifest_ref")), "freeze.freeze_manifest_ref"))
    for arm in data.get("arms", []) or []:
        if not isinstance(arm, dict):
            continue
        arm_id = str(arm.get("id", "?"))
        for key in (
            "workflow_protocol_ref",
            "common_condition_ref",
            "verification_protocol_ref",
            "measurement_protocol_ref",
        ):
            if arm.get(key):
                refs.append((str(arm.get(key)), f"arms[{arm_id}].{key}"))
    return refs


def semantic_errors(data: dict, path: Path, repo_root: Path) -> list[str]:
    errors: list[str] = []

    design_series_id = str(data.get("series_id", "")).strip()
    design_challenge = str(data.get("challenge_version", "")).strip()
    target_blocker = str(data.get("target_blocker", "")).strip()
    arms = data.get("arms", []) or []
    controlled_dimensions = data.get("controlled_dimensions", []) or []
    confounder_controls = data.get("confounder_controls", []) or []
    does_not_establish = data.get("does_not_establish", []) or []
    primary_axis = data.get("primary_intervention_axis") or {}

    resolutions = resolve_source_evidence_entries(data, repo_root)
    gate_paths = [
        (r.raw_rel_path, r.loaded_yaml)
        for r in resolutions
        if r.kind == GATE_KIND and r.loaded_yaml is not None
    ]
    readiness_paths = [
        (r.raw_rel_path, r.loaded_yaml)
        for r in resolutions
        if r.kind == READINESS_KIND and r.loaded_yaml is not None
    ]
    gate_docs = [doc for _, doc in gate_paths]
    readiness_docs = [doc for _, doc in readiness_paths]

    # --- exactly one foundational gate source --------------------------------
    gate_count = sum(1 for r in resolutions if r.kind == GATE_KIND)
    if gate_count != 1:
        errors.append(
            format_error(
                "CONDITION_DESIGN_REQUIRES_SINGLE_GATE_SOURCE",
                path,
                "source_evidence must contain exactly one condition_contrast_design_gate "
                f"source; foundational gate evidence must be unambiguous (found {gate_count}).",
            )
        )

    readiness_count = sum(1 for r in resolutions if r.kind == READINESS_KIND)

    # --- foundational sources must be readable YAML mappings -----------------
    readable_problems = [
        f"{display_source_path(r.raw_rel_path)} ({r.kind}) "
        f"{READABILITY_MESSAGES.get(r.readability_error, r.readability_error)}"
        for r in resolutions
        if r.kind in FOUNDATIONAL_KINDS and r.code is None and r.readability_error is not None
    ]
    if readable_problems:
        errors.append(
            format_error(
                "CONDITION_DESIGN_REQUIRES_READABLE_FOUNDATIONAL_SOURCES",
                path,
                "each foundational source (condition_contrast_design_gate, readiness_gate) "
                "must be a readable YAML mapping; offending: " + "; ".join(readable_problems),
            )
        )

    # --- foundational sources must be the right artifact for this series -----
    identity_problems = _source_identity_mismatches(
        gate_paths,
        expected_artifact_type=GATE_ARTIFACT_TYPE,
        expected_series_id=design_series_id,
    )
    identity_problems += _source_identity_mismatches(
        readiness_paths,
        expected_artifact_type=READINESS_ARTIFACT_TYPE,
        expected_series_id=design_series_id,
        expected_challenge_version=design_challenge,
    )
    if identity_problems:
        errors.append(
            format_error(
                "CONDITION_DESIGN_REQUIRES_MATCHING_SOURCE_IDENTITY",
                path,
                "each foundational source must match this design's identity "
                f"(series_id={design_series_id!r}, challenge_version={design_challenge!r}); "
                "offending: " + "; ".join(identity_problems),
            )
        )

    # --- gate must authorize a Run-004 design --------------------------------
    if gate_docs and not _gate_authorizes_design(gate_docs):
        errors.append(
            format_error(
                "CONDITION_DESIGN_REQUIRES_GATE_AUTHORIZES_DESIGN",
                path,
                "no referenced condition_contrast_design_gate authorizes a Run-004 design "
                "(needs gate_status=criteria_defined, run_004_design_allowed=true, "
                "run_004_execution_allowed=false).",
            )
        )

    # --- assessment / comparison must remain blocked -------------------------
    blocked = True
    if gate_docs and not _gate_keeps_assessment_blocked(gate_docs):
        blocked = False
    if readiness_count != 1 or not readiness_docs or not _readiness_blocked_confirmed(readiness_docs):
        blocked = False
    if not blocked:
        errors.append(
            format_error(
                "CONDITION_DESIGN_REQUIRES_BLOCKED_READINESS",
                path,
                "the gate must keep result_assessment_allowed_after_gate=false and "
                "comparison_ready_after_gate=false, and exactly one readiness_gate source "
                "must explicitly confirm a blocked assessment (readiness_status=blocked, "
                "result_assessment_allowed=false, comparison_ready=false; missing fields do "
                "not count as false). A frozen design is only coherent while a formal result "
                "assessment is still blocked.",
            )
        )

    # --- target blocker must stay open in gate and readiness -----------------
    open_problems: list[str] = []
    if gate_docs and target_blocker and not _gate_target_open(gate_docs, target_blocker):
        open_problems.append("not open in the gate (blocker_status_after_gate)")
    for raw_rel_path, doc in readiness_paths:
        if target_blocker and not _blocker_open_in(doc, "blockers", target_blocker):
            open_problems.append(f"{display_source_path(raw_rel_path)}: not open in readiness blockers")
    if open_problems:
        errors.append(
            format_error(
                "CONDITION_DESIGN_REQUIRES_OPEN_TARGET_BLOCKER",
                path,
                f"target_blocker {target_blocker!r} must stay open in both the gate and the "
                "referenced readiness gate; designing a contrast for a closed blocker is "
                "incoherent. Offending: " + "; ".join(open_problems),
            )
        )

    # --- exactly one control and one treatment arm ---------------------------
    roles = sorted(str(a.get("role", "")).strip() for a in arms if isinstance(a, dict))
    control_arm, treatment_arm = _arms_by_role(arms)
    if roles != ["control", "treatment"]:
        errors.append(
            format_error(
                "CONDITION_DESIGN_REQUIRES_EXACTLY_TWO_ARMS",
                path,
                "arms must be exactly one 'control' and one 'treatment'; "
                f"found roles {roles}.",
            )
        )

    # --- single primary axis: workflow_protocol, varied across arms ----------
    axis_id = str(primary_axis.get("id", "")).strip() if isinstance(primary_axis, dict) else ""
    if axis_id != EXPECTED_PRIMARY_AXIS:
        errors.append(
            format_error(
                "CONDITION_DESIGN_REQUIRES_SINGLE_PRIMARY_AXIS",
                path,
                f"primary_intervention_axis.id must be {EXPECTED_PRIMARY_AXIS!r}; found {axis_id!r}.",
            )
        )
    elif control_arm is not None and treatment_arm is not None:
        if str(control_arm.get("workflow_protocol", "")).strip() == str(
            treatment_arm.get("workflow_protocol", "")
        ).strip():
            errors.append(
                format_error(
                    "CONDITION_DESIGN_REQUIRES_SINGLE_PRIMARY_AXIS",
                    path,
                    "the two arms must take different workflow_protocol values along the "
                    "single primary axis; both arms share the same value.",
                )
            )

    # --- material, pre-execution-observable contrast -------------------------
    if control_arm is not None and treatment_arm is not None:
        material_problems: list[str] = []
        if str(control_arm.get("workflow_protocol", "")).strip() != CONTROL_WORKFLOW_PROTOCOL:
            material_problems.append(
                f"control workflow_protocol must be {CONTROL_WORKFLOW_PROTOCOL!r}"
            )
        if not _spec_is_no_upfront_spec(control_arm.get("workflow_protocol_spec", {})):
            material_problems.append(
                "control must allow immediate implementation with no required upfront specification"
            )
        if str(treatment_arm.get("workflow_protocol", "")).strip() != TREATMENT_WORKFLOW_PROTOCOL:
            material_problems.append(
                f"treatment workflow_protocol must be {TREATMENT_WORKFLOW_PROTOCOL!r}"
            )
        if not _spec_is_full_upfront_spec(treatment_arm.get("workflow_protocol_spec", {})):
            material_problems.append(
                "treatment must forbid implementation before a complete upfront specification "
                "carrying the mandatory sections: " + ", ".join(MANDATORY_TREATMENT_SPEC_SECTIONS)
            )
        if material_problems:
            errors.append(
                format_error(
                    "CONDITION_DESIGN_REQUIRES_MATERIAL_CONTRAST",
                    path,
                    "the workflow_protocol contrast must be material and observable before "
                    "execution, not a cosmetic relabel; " + "; ".join(material_problems),
                )
            )

    # --- only the primary axis may differ between arms -----------------------
    if control_arm is not None and treatment_arm is not None:
        differing_non_primary = sorted(
            key
            for key in set(control_arm) | set(treatment_arm)
            if key not in PRIMARY_AXIS_ARM_KEYS
            and control_arm.get(key) != treatment_arm.get(key)
        )
        if differing_non_primary:
            errors.append(
                format_error(
                    "CONDITION_DESIGN_REQUIRES_ONLY_PRIMARY_AXIS_DIFFERENCE",
                    path,
                    "the two arms may differ only along the primary axis (workflow_protocol); "
                    "these non-primary arm fields differ: " + ", ".join(differing_non_primary),
                )
            )

        # --- shared verification / measurement / intervention ----------------
        if control_arm.get("verification_protocol_ref") != treatment_arm.get("verification_protocol_ref"):
            errors.append(
                format_error(
                    "CONDITION_DESIGN_REQUIRES_SHARED_VERIFICATION",
                    path,
                    "both arms must reference the same verification protocol.",
                )
            )
        if control_arm.get("measurement_protocol_ref") != treatment_arm.get("measurement_protocol_ref"):
            errors.append(
                format_error(
                    "CONDITION_DESIGN_REQUIRES_SHARED_MEASUREMENT",
                    path,
                    "both arms must reference the same measurement protocol.",
                )
            )
        if control_arm.get("intervention_profile") != treatment_arm.get("intervention_profile"):
            errors.append(
                format_error(
                    "CONDITION_DESIGN_REQUIRES_SHARED_INTERVENTION_RULES",
                    path,
                    "both arms must share the same intervention_profile (intervention and "
                    "stop rules).",
                )
            )

    # --- complete control bindings for every non-primary dimension ----------
    present_dimensions = set(_ids(controlled_dimensions))
    missing_dimensions = [d for d in MANDATORY_CONTROLLED_DIMENSIONS if d not in present_dimensions]
    if missing_dimensions:
        errors.append(
            format_error(
                "CONDITION_DESIGN_REQUIRES_COMPLETE_CONTROL_BINDINGS",
                path,
                "controlled_dimensions must bind every mandatory non-primary dimension; "
                "missing: " + ", ".join(missing_dimensions),
            )
        )

    # --- complete confounder controls with declared effects ------------------
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
                "CONDITION_DESIGN_REQUIRES_COMPLETE_CONFOUNDER_CONTROLS",
                path,
                "confounder_controls must cover the mandatory set, each with its declared "
                "effect_if_uncontrolled; " + "; ".join(confounder_problems),
            )
        )

    # --- unique semantic ids within each list --------------------------------
    duplicate_id_problems: list[str] = []
    for label, items in (
        ("arms", arms),
        ("controlled_dimensions", controlled_dimensions),
        ("confounder_controls", confounder_controls),
    ):
        dups = _duplicates(_ids(items))
        if dups:
            duplicate_id_problems.append(f"{label}: " + ", ".join(dups))
    if duplicate_id_problems:
        errors.append(
            format_error(
                "CONDITION_DESIGN_REQUIRES_UNIQUE_SEMANTIC_IDS",
                path,
                "ids must be unique within each list; duplicated — " + "; ".join(duplicate_id_problems),
            )
        )

    # --- valid, acyclic, complete freeze -------------------------------------
    freeze_problems = _freeze_problems(data, repo_root)
    if freeze_problems:
        errors.append(
            format_error(
                "CONDITION_DESIGN_REQUIRES_VALID_FREEZE",
                path,
                "the SHA-256 freeze manifest must be internally consistent, acyclic, and "
                "cover the design and every protocol artifact; " + "; ".join(freeze_problems),
            )
        )

    # --- no execution artifacts in the design path ---------------------------
    execution_problems = _execution_artifact_problems(path.resolve().parent)
    if execution_problems:
        errors.append(
            format_error(
                "CONDITION_DESIGN_FORBIDS_EXECUTION_ARTIFACTS",
                path,
                "the design directory must not contain execution artifacts; offending: "
                + ", ".join(execution_problems),
            )
        )

    # --- mandatory anti-overclaim non-claims ---------------------------------
    declared = {str(item).strip().lower() for item in does_not_establish}
    missing_mandatory = [item for item in MANDATORY_DOES_NOT_ESTABLISH if item not in declared]
    wrongly_listed = [item for item in FORBIDDEN_SELECTION_NON_CLAIMS if item in declared]
    if missing_mandatory or wrongly_listed:
        detail: list[str] = []
        if missing_mandatory:
            detail.append("missing: " + ", ".join(missing_mandatory))
        if wrongly_listed:
            detail.append(
                "must not be listed (this design establishes them): " + ", ".join(wrongly_listed)
            )
        errors.append(
            format_error(
                "CONDITION_DESIGN_REQUIRES_MANDATORY_NON_CLAIMS",
                path,
                "does_not_establish must include all static anti-overclaim non-claims and must "
                "not deny the design's own contribution; " + "; ".join(detail),
            )
        )

    # --- every referenced repo path safe, existing, regular ------------------
    safe_problems: list[str] = []
    for res in resolutions:
        if res.code == "ESCAPE":
            safe_problems.append(f"{display_source_path(res.raw_rel_path)}: resolves outside the repo root")
        elif res.code == "NOT_FOUND":
            safe_problems.append(f"{display_source_path(res.raw_rel_path)}: does not exist")
        elif res.readability_error == "NOT_FILE" and res.kind not in FOUNDATIONAL_KINDS:
            # A foundational non-regular-file is already reported by the readability rule.
            safe_problems.append(f"{display_source_path(res.raw_rel_path)}: exists but is not a regular file")
    for raw_ref, label in _collect_repo_refs(data):
        resolved, code = resolve_repo_relative_path(raw_ref, repo_root, must_exist=True)
        if code == "ESCAPE":
            safe_problems.append(f"{label}={display_source_path(raw_ref)}: resolves outside the repo root")
        elif code == "NOT_FOUND":
            safe_problems.append(f"{label}={display_source_path(raw_ref)}: does not exist")
        elif resolved is not None and not resolved.is_file():
            safe_problems.append(f"{label}={display_source_path(raw_ref)}: exists but is not a regular file")
    if safe_problems:
        errors.append(
            format_error(
                "CONDITION_DESIGN_REQUIRES_SAFE_EXISTING_PATHS",
                path,
                "every referenced repo path must be a safe, existing, regular file; offending: "
                + "; ".join(safe_problems),
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
    return sorted(experiments_dir.glob(DESIGN_GLOB))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Model-Lab condition-design artifacts."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="condition-design YAML files (default: discover all under experiments/).",
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
                "ℹ️ No model-lab-condition-design artifacts found; "
                "model-lab-condition-design validation skipped."
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
        f"Model-lab-condition-design artifacts: checked={checked}, "
        f"passed={passed}, failed={checked - passed}"
    )
    return highest_exit_code


if __name__ == "__main__":
    sys.exit(main())
