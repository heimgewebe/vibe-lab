#!/usr/bin/env python3
"""validate_model_lab_condition_design.py — Validator for Model-Lab condition-design artifacts.

A condition-design artifact
(``experiments/<series>/artifacts/run-004-condition-contrast-design/condition-design.yml``)
freezes, before execution, the paired condition contrast a *future* Model-Lab Run-004
must run. v1 has exactly one honest state: condition semantics frozen
(design_status=frozen, condition_semantics_status=frozen) while the execution binding is
still pending (execution_binding_status=pending, runtime_values_bound=false). The primary
axis is an ASSIGNED workflow-instruction requirement (Spec-First present vs absent), not an
enforced internal thought process. Preconditions are read from a frozen precondition
snapshot, never from mutable live state. It does NOT execute a run, bind runtime values,
allow a result assessment, make the series comparison-ready, or resolve
weak_condition_contrast.

The fixed v1 values are pinned in the JSON schema as const; this validator enforces the
genuinely semantic, cross-artifact, freeze-integrity, isolation, and path-safety rules.

Enforced semantic rules (exit 1) — stable ids:
  CONDITION_DESIGN_REQUIRES_VALID_PRECONDITION_SNAPSHOT
  CONDITION_DESIGN_REQUIRES_GATE_REQUIREMENTS_SUBSET
  CONDITION_DESIGN_REQUIRES_EXACTLY_TWO_ARMS
  CONDITION_DESIGN_REQUIRES_SINGLE_PRIMARY_AXIS
  CONDITION_DESIGN_REQUIRES_MATERIAL_CONTRAST
  CONDITION_DESIGN_REQUIRES_ONLY_PRIMARY_AXIS_DIFFERENCE
  CONDITION_DESIGN_REQUIRES_PRIMARY_AXIS_NOT_CONTROLLED
  CONDITION_DESIGN_REQUIRES_ASSIGNED_VS_OBSERVED_SEPARATION
  CONDITION_DESIGN_REQUIRES_SHARED_VERIFICATION
  CONDITION_DESIGN_REQUIRES_SHARED_MEASUREMENT
  CONDITION_DESIGN_REQUIRES_CHILD_IDENTITY
  CONDITION_DESIGN_REQUIRES_DESIGN_SELF_IDENTITY
  CONDITION_DESIGN_REQUIRES_BUNDLE_BOUNDARY
  CONDITION_DESIGN_REQUIRES_VALID_FREEZE
  CONDITION_DESIGN_FORBIDS_EXECUTION_ARTIFACTS
  CONDITION_DESIGN_REQUIRES_MANDATORY_NON_CLAIMS
  CONDITION_DESIGN_REQUIRES_UNIQUE_SEMANTIC_IDS
  CONDITION_DESIGN_REQUIRES_SAFE_EXISTING_PATHS

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
DESIGN_ARTIFACT_TYPE = "model_lab_condition_design"

SNAPSHOT_ARTIFACT_TYPE = "model_lab_condition_design_precondition_snapshot"
GATE_ARTIFACT_TYPE = "model_lab_condition_contrast_design_gate"
READINESS_ARTIFACT_TYPE = "result_assessment_readiness"
VERIFICATION_ARTIFACT_TYPE = "model_lab_condition_design_verification_protocol"
MEASUREMENT_ARTIFACT_TYPE = "model_lab_condition_design_measurement_protocol"
FREEZE_ARTIFACT_TYPE = "model_lab_condition_design_freeze_manifest"

EXPECTED_TARGET_BLOCKER = "weak_condition_contrast"
EXPECTED_PRIMARY_AXIS = "workflow_protocol"
CONTROL_WORKFLOW_PROTOCOL = "direct_implementation"
TREATMENT_WORKFLOW_PROTOCOL = "spec_first"
COMPLIANCE_METRIC_ID = "workflow_protocol_compliance"

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

# Effect severity (higher = stronger). A design must not WEAKEN a gate-declared effect.
EFFECT_SEVERITY = {"must_be_reported": 1, "blocks_design": 2}

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
    "single_paired_execution_establishes_condition_effect",
)
FORBIDDEN_SELECTION_NON_CLAIMS = (
    "primary_intervention_axis_selected",
    "concrete_condition_selected",
)

# Forbidden execution artifacts, detected RECURSIVELY anywhere in the design bundle.
FORBIDDEN_EXECUTION_FILES = frozenset({
    "run.yml", "run_meta.json", "execution.txt", "measurement.yml", "auditor-output.yml",
    "comparability.yml", "evidence-pack.yml", "timing.txt", "package.json", "package-lock.json",
})
FORBIDDEN_EXECUTION_DIRS = frozenset({"implementation", "src", "tests"})
FORBIDDEN_EXECUTION_GLOBS = ("execute-*.py", "verify-*.py")

# A metric must not pre-bake observed results.
FORBIDDEN_METRIC_VALUE_KEYS = frozenset({"value", "observed", "measured", "result", "score", "values"})

# Freeze manifest must never record a self-containing commit/tree/head SHA.
FORBIDDEN_FREEZE_COMMIT_KEYS = frozenset({"final_commit_sha", "final_tree_sha", "final_pr_head_sha"})

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
RFC3339_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$"
)
DRIVE_LETTER_RE = re.compile(r"^[A-Za-z]:")


def _has_forbidden_path_codepoint(text: str) -> bool:
    return any(
        ord(c) <= 0x1F or ord(c) == 0x7F or 0xD800 <= ord(c) <= 0xDFFF for c in text
    )


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except (OSError, RuntimeError, ValueError, UnicodeError):
        return str(path)


def _escape_source_path_char(char: str) -> str:
    cp = ord(char)
    if cp <= 0x1F or cp == 0x7F:
        return {"\t": r"\t", "\n": r"\n", "\r": r"\r", "\f": r"\f", "\v": r"\v"}.get(char, f"\\x{cp:02x}")
    if 0xD800 <= cp <= 0xDFFF:
        return f"\\u{cp:04x}"
    if char.isspace() and char != " ":
        return f"\\u{cp:04x}" if cp <= 0xFFFF else f"\\U{cp:08x}"
    return char


def display_source_path(raw) -> str:
    if not isinstance(raw, str):
        return str(raw)
    lead = len(raw) - len(raw.lstrip())
    trail = len(raw.rstrip())
    return "".join(
        r"\x20" if (c == " " and (i < lead or i >= trail)) else _escape_source_path_char(c)
        for i, c in enumerate(raw)
    )


def load_schema_validator() -> Draft202012Validator:
    try:
        raw = SCHEMA_PATH.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise RuntimeError(f"schema file missing: {display_path(SCHEMA_PATH)}") from exc
    except UnicodeDecodeError as exc:
        raise RuntimeError(f"schema file is not valid UTF-8: {display_path(SCHEMA_PATH)}") from exc
    except OSError as exc:
        raise RuntimeError(f"schema file could not be read: {display_path(SCHEMA_PATH)}: {exc}") from exc
    try:
        schema = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"schema file invalid JSON: {display_path(SCHEMA_PATH)}: {exc}") from exc
    try:
        Draft202012Validator.check_schema(schema)
        return Draft202012Validator(schema)
    except SchemaError as exc:
        raise RuntimeError(f"schema invalid: {display_path(SCHEMA_PATH)}: {exc.message}") from exc


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
    for error in sorted(validator.iter_errors(data), key=lambda i: list(i.absolute_path)):
        location = ".".join(str(p) for p in error.absolute_path) or "$"
        errors.append(f"ERROR path={display_path(path)} instance_path={location}: {error.message}")
    return errors


def format_error(rule_id: str, path: Path, message: str) -> str:
    return f"ERROR rule={rule_id} path={display_path(path)}: {message}"


def _inside(candidate: Path, root: Path) -> bool:
    try:
        candidate.relative_to(root)
        return True
    except ValueError:
        return False


def resolve_repo_relative_path(rel_path, repo_root: Path, *, must_exist: bool):
    """Resolve a repo-relative POSIX path safely. Returns (resolved|None, code|None)."""
    raw_text = str(rel_path)
    if _has_forbidden_path_codepoint(raw_text):
        return None, "ESCAPE"
    if raw_text != raw_text.strip() or not raw_text:
        return None, "ESCAPE"
    if raw_text.startswith("/") or DRIVE_LETTER_RE.match(raw_text) or "\\" in raw_text:
        return None, "ESCAPE"
    if ".." in PurePosixPath(raw_text).parts:
        return None, "ESCAPE"
    root = repo_root.resolve()
    candidate = root / raw_text
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


def _sha256_of(path: Path):
    try:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(65536), b""):
                digest.update(chunk)
        return digest.hexdigest()
    except (OSError, ValueError):
        return None


def _ids(items) -> list[str]:
    return [
        str(i.get("id", "")).strip()
        for i in (items or [])
        if isinstance(i, dict) and str(i.get("id", "")).strip()
    ]


def _duplicates(values) -> list:
    seen, dups = set(), set()
    for v in values:
        (dups if v in seen else seen).add(v)
    return sorted(dups, key=str)


def _arms_by_role(arms):
    control = [a for a in arms if isinstance(a, dict) and a.get("role") == "control"]
    treatment = [a for a in arms if isinstance(a, dict) and a.get("role") == "treatment"]
    return (control[0] if len(control) == 1 else None,
            treatment[0] if len(treatment) == 1 else None)


def _load_bundle_yaml(ref, bundle_dir: Path, repo_root: Path):
    """Resolve a bundle YAML ref (must be inside the bundle dir) and load it as a mapping.

    Returns (doc|None, problem|None).
    """
    resolved, code = resolve_repo_relative_path(ref, repo_root, must_exist=True)
    if code == "ESCAPE":
        return None, "resolves outside the repo root"
    if code == "NOT_FOUND":
        return None, "does not exist"
    if resolved is None or not resolved.is_file():
        return None, "is not a regular file"
    if not _inside(resolved, bundle_dir):
        return None, "is outside the design bundle"
    try:
        doc = load_yaml(resolved)
    except (FileNotFoundError, ValueError):
        return None, "is not a readable YAML mapping"
    return doc, None


def _child_identity_problems(label, doc, design):
    out = []
    for key in ("design_id", "series_id", "challenge_version"):
        if str(doc.get(key, "")).strip() != str(design.get(key, "")).strip():
            out.append(f"{label}.{key}={doc.get(key)!r} (expected {design.get(key)!r})")
    return out


def _bundle_refs(data: dict):
    """(raw_ref, label) for every ref that must live inside the design bundle."""
    refs = [
        (str(data.get("design_artifact_path", "")), "design_artifact_path"),
        (str(data.get("precondition_snapshot_ref", "")), "precondition_snapshot_ref"),
    ]
    freeze = data.get("freeze") or {}
    if isinstance(freeze, dict) and freeze.get("freeze_manifest_ref"):
        refs.append((str(freeze["freeze_manifest_ref"]), "freeze.freeze_manifest_ref"))
    for block, label in (("verification_surface", "verification_surface.protocol_ref"),
                         ("measurement_surface", "measurement_surface.protocol_ref")):
        b = data.get(block) or {}
        if isinstance(b, dict) and b.get("protocol_ref"):
            refs.append((str(b["protocol_ref"]), label))
    cia = data.get("condition_input_assembly") or {}
    if isinstance(cia, dict) and cia.get("shared_input_ref"):
        refs.append((str(cia["shared_input_ref"]), "condition_input_assembly.shared_input_ref"))
    for arm in data.get("arms") or []:
        if isinstance(arm, dict) and arm.get("overlay_ref"):
            refs.append((str(arm["overlay_ref"]), f"arms[{arm.get('id','?')}].overlay_ref"))
    return refs


def _covered_bundle_files(data: dict):
    """Repo-relative refs that the freeze manifest must cover (design + protocols + snapshot)."""
    out = [str(data.get("design_artifact_path", "")), str(data.get("precondition_snapshot_ref", ""))]
    for block in ("verification_surface", "measurement_surface"):
        b = data.get(block) or {}
        if isinstance(b, dict) and b.get("protocol_ref"):
            out.append(str(b["protocol_ref"]))
    cia = data.get("condition_input_assembly") or {}
    if isinstance(cia, dict) and cia.get("shared_input_ref"):
        out.append(str(cia["shared_input_ref"]))
    for arm in data.get("arms") or []:
        if isinstance(arm, dict) and arm.get("overlay_ref"):
            out.append(str(arm["overlay_ref"]))
    return out


def _execution_artifact_problems(bundle_dir: Path) -> list[str]:
    problems: set[str] = set()
    try:
        if not bundle_dir.is_dir():
            return []
        for entry in bundle_dir.rglob("*"):
            try:
                rel = entry.relative_to(bundle_dir).as_posix()
                if entry.is_dir():
                    if entry.name in FORBIDDEN_EXECUTION_DIRS:
                        problems.add(rel + "/")
                elif entry.is_file():
                    if entry.name in FORBIDDEN_EXECUTION_FILES:
                        problems.add(rel)
                    elif any(entry.match(g) for g in FORBIDDEN_EXECUTION_GLOBS):
                        problems.add(rel)
            except OSError:
                continue
    except OSError:
        return []
    return sorted(problems)


def _freeze_problems(data: dict, bundle_dir: Path, repo_root: Path) -> list[str]:
    problems: list[str] = []
    freeze = data.get("freeze") or {}
    manifest_rel = str(freeze.get("freeze_manifest_ref", ""))
    manifest, prob = _load_bundle_yaml(manifest_rel, bundle_dir, repo_root)
    if manifest is None:
        return [f"freeze manifest {display_source_path(manifest_rel)} {prob}"]
    manifest_path, _ = resolve_repo_relative_path(manifest_rel, repo_root, must_exist=True)

    if str(manifest.get("artifact_type", "")).strip() != FREEZE_ARTIFACT_TYPE:
        problems.append(f"artifact_type={manifest.get('artifact_type')!r} (expected {FREEZE_ARTIFACT_TYPE!r})")
    problems += _child_identity_problems("freeze", manifest, data)
    if manifest.get("frozen_before_execution") is not True:
        problems.append("frozen_before_execution must be literally true")
    if not RFC3339_RE.match(str(manifest.get("frozen_at", ""))):
        problems.append(f"frozen_at must be an RFC-3339 timestamp (got {manifest.get('frozen_at')!r})")
    if not str(manifest.get("change_rule", "")).strip():
        problems.append("change_rule must be non-empty")
    for key in FORBIDDEN_FREEZE_COMMIT_KEYS:
        if key in manifest:
            problems.append(f"must not record a self-referential commit key: {key}")

    entries = manifest.get("hashes")
    if not isinstance(entries, list) or not entries:
        problems.append("hashes must be a non-empty list")
        return problems

    declared_paths: list[str] = []
    hashed_ok: set[Path] = set()
    declared_resolved: set[Path] = set()
    for idx, entry in enumerate(entries):
        if not isinstance(entry, dict):
            problems.append(f"hashes[{idx}] is not a mapping")
            continue
        rel = str(entry.get("path", ""))
        declared = str(entry.get("sha256", "")).strip().lower()
        declared_paths.append(rel)
        resolved, code = resolve_repo_relative_path(rel, repo_root, must_exist=True)
        if code is not None or resolved is None or not resolved.is_file():
            problems.append(f"hashed path {display_source_path(rel)} is not a safe, existing, regular file")
            continue
        if not _inside(resolved, bundle_dir):
            problems.append(f"hashed path {display_source_path(rel)} is outside the design bundle")
            continue
        declared_resolved.add(resolved)
        if not SHA256_RE.match(declared):
            problems.append(f"hashed path {display_source_path(rel)} has a malformed sha256")
            continue
        actual = _sha256_of(resolved)
        if actual != declared:
            problems.append(f"sha256 mismatch for {display_source_path(rel)}")
            continue
        hashed_ok.add(resolved)

    for dup in _duplicates(declared_paths):
        problems.append(f"duplicate hashed path: {display_source_path(dup)}")
    if manifest_path is not None and manifest_path in declared_resolved:
        problems.append("freeze manifest must not hash itself (cycle)")

    for rel in _covered_bundle_files(data):
        resolved, code = resolve_repo_relative_path(rel, repo_root, must_exist=True)
        if code is not None or resolved is None:
            continue  # path safety reported elsewhere
        if resolved not in hashed_ok:
            problems.append(f"bundle file not covered by a valid freeze hash: {display_source_path(rel)}")
    return problems


def _snapshot_problems(data: dict, bundle_dir: Path, repo_root: Path):
    """Returns (problems, gate_block_or_None)."""
    problems: list[str] = []
    ref = str(data.get("precondition_snapshot_ref", ""))
    snap, prob = _load_bundle_yaml(ref, bundle_dir, repo_root)
    if snap is None:
        return [f"precondition snapshot {display_source_path(ref)} {prob}"], None

    if str(snap.get("artifact_type", "")).strip() != SNAPSHOT_ARTIFACT_TYPE:
        problems.append(f"artifact_type={snap.get('artifact_type')!r} (expected {SNAPSHOT_ARTIFACT_TYPE!r})")
    problems += _child_identity_problems("snapshot", snap, data)

    sources = snap.get("captured_sources")
    if not isinstance(sources, dict):
        problems.append("captured_sources missing or malformed")
        return problems, None

    gate = sources.get("gate")
    if not isinstance(gate, dict):
        problems.append("captured_sources.gate missing or malformed")
        gate = None
    else:
        if str(gate.get("artifact_type", "")).strip() != GATE_ARTIFACT_TYPE:
            problems.append(f"gate.artifact_type={gate.get('artifact_type')!r} (expected {GATE_ARTIFACT_TYPE!r})")
        if gate.get("gate_status") != "criteria_defined":
            problems.append(f"gate.gate_status={gate.get('gate_status')!r} (expected 'criteria_defined')")
        if gate.get("run_004_design_allowed") is not True:
            problems.append("gate.run_004_design_allowed must be literally true")
        if gate.get("run_004_execution_allowed") is not False:
            problems.append("gate.run_004_execution_allowed must be literally false")
        if gate.get("result_assessment_allowed_after_gate") is not False:
            problems.append("gate.result_assessment_allowed_after_gate must be literally false")
        if gate.get("comparison_ready_after_gate") is not False:
            problems.append("gate.comparison_ready_after_gate must be literally false")
        if str(gate.get("target_blocker", "")).strip() != str(data.get("target_blocker", "")).strip():
            problems.append(f"gate.target_blocker={gate.get('target_blocker')!r} (expected {data.get('target_blocker')!r})")
        if str(gate.get("blocker_status_after_gate", "")).strip() != "open":
            problems.append("gate.blocker_status_after_gate must be 'open'")
        if not SHA256_RE.match(str(gate.get("source_sha256", "")).strip().lower()):
            problems.append("gate.source_sha256 must be a 64-hex sha256")

    readiness = sources.get("readiness")
    if not isinstance(readiness, dict):
        problems.append("captured_sources.readiness missing or malformed")
    else:
        if str(readiness.get("artifact_type", "")).strip() != READINESS_ARTIFACT_TYPE:
            problems.append(f"readiness.artifact_type={readiness.get('artifact_type')!r} (expected {READINESS_ARTIFACT_TYPE!r})")
        if readiness.get("readiness_status_at_design") != "blocked":
            problems.append("readiness.readiness_status_at_design must be 'blocked'")
        if readiness.get("result_assessment_allowed_at_design") is not False:
            problems.append("readiness.result_assessment_allowed_at_design must be literally false")
        if readiness.get("comparison_ready_at_design") is not False:
            problems.append("readiness.comparison_ready_at_design must be literally false")
        if str(readiness.get("target_blocker_status_at_design", "")).strip() != "open":
            problems.append("readiness.target_blocker_status_at_design must be 'open'")
        if not SHA256_RE.match(str(readiness.get("source_sha256", "")).strip().lower()):
            problems.append("readiness.source_sha256 must be a 64-hex sha256")

    return problems, gate


def _gate_subset_problems(data: dict, gate: dict):
    problems: list[str] = []
    design_dims = set(_ids(data.get("controlled_dimensions")))
    required_dims = gate.get("required_control_dimensions") or []
    if not isinstance(required_dims, list):
        problems.append("snapshot gate.required_control_dimensions is malformed")
        required_dims = []
    missing_dims = [d for d in required_dims if str(d).strip() not in design_dims]
    if missing_dims:
        problems.append("controlled_dimensions missing gate-required: " + ", ".join(map(str, missing_dims)))

    design_conf = {
        str(c.get("id", "")).strip(): str(c.get("effect_if_uncontrolled", "")).strip()
        for c in (data.get("confounder_controls") or [])
        if isinstance(c, dict) and str(c.get("id", "")).strip()
    }
    required_conf = gate.get("required_confounders") or {}
    if not isinstance(required_conf, dict):
        problems.append("snapshot gate.required_confounders is malformed")
        required_conf = {}
    for cid, gate_effect in required_conf.items():
        cid_s = str(cid).strip()
        if cid_s not in design_conf:
            problems.append(f"confounder_controls missing gate-required: {cid_s}")
            continue
        if EFFECT_SEVERITY.get(design_conf[cid_s], 0) < EFFECT_SEVERITY.get(str(gate_effect).strip(), 0):
            problems.append(
                f"confounder {cid_s} weakens gate effect {str(gate_effect)!r} to {design_conf[cid_s]!r}"
            )
    return problems


def _spec_is_no_upfront(spec) -> bool:
    return (
        isinstance(spec, dict)
        and spec.get("pre_implementation_specification_required") is False
        and spec.get("implementation_may_begin_immediately") is True
        and spec.get("specification_completeness_checked_before_implementation") is False
        and not (spec.get("required_specification_sections") or [])
    )


def _spec_is_full_upfront(spec) -> bool:
    if not isinstance(spec, dict):
        return False
    if spec.get("pre_implementation_specification_required") is not True:
        return False
    if spec.get("implementation_may_begin_immediately") is not False:
        return False
    if spec.get("specification_completeness_checked_before_implementation") is not True:
        return False
    sections = {str(s).strip() for s in (spec.get("required_specification_sections") or [])}
    return all(s in sections for s in MANDATORY_TREATMENT_SPEC_SECTIONS)


def _verification_problems(data: dict, bundle_dir: Path, repo_root: Path):
    ref = str((data.get("verification_surface") or {}).get("protocol_ref", ""))
    doc, prob = _load_bundle_yaml(ref, bundle_dir, repo_root)
    if doc is None:
        return [f"verification protocol {display_source_path(ref)} {prob}"]
    problems = _child_identity_problems("verification", doc, data)
    if str(doc.get("artifact_type", "")).strip() != VERIFICATION_ARTIFACT_TYPE:
        problems.append(f"artifact_type={doc.get('artifact_type')!r} (expected {VERIFICATION_ARTIFACT_TYPE!r})")
    if doc.get("applies_equally_to_both_arms") is not True:
        problems.append("applies_equally_to_both_arms must be literally true")
    if doc.get("does_not_execute") is not True:
        problems.append("does_not_execute must be literally true")
    if doc.get("per_arm_test_overrides_forbidden") is not True:
        problems.append("per_arm_test_overrides_forbidden must be literally true")
    if str(doc.get("executable_harness_binding_status", "")).strip() != "deferred_to_execution_readiness":
        problems.append("executable_harness_binding_status must be 'deferred_to_execution_readiness'")
    return problems


def _measurement_problems(data: dict, bundle_dir: Path, repo_root: Path):
    ref = str((data.get("measurement_surface") or {}).get("protocol_ref", ""))
    doc, prob = _load_bundle_yaml(ref, bundle_dir, repo_root)
    if doc is None:
        return [f"measurement protocol {display_source_path(ref)} {prob}"]
    problems = _child_identity_problems("measurement", doc, data)
    if str(doc.get("artifact_type", "")).strip() != MEASUREMENT_ARTIFACT_TYPE:
        problems.append(f"artifact_type={doc.get('artifact_type')!r} (expected {MEASUREMENT_ARTIFACT_TYPE!r})")
    if doc.get("applies_equally_to_both_arms") is not True:
        problems.append("applies_equally_to_both_arms must be literally true")
    if doc.get("post_hoc_metric_selection_forbidden") is not True:
        problems.append("post_hoc_metric_selection_forbidden must be literally true")
    if doc.get("does_not_record_values") is not True:
        problems.append("does_not_record_values must be literally true")
    if doc.get("treatment_only_scoring_forbidden") is not True:
        problems.append("treatment_only_scoring_forbidden must be literally true")
    metrics = []
    for key in ("primary_metrics", "secondary_metrics", "metrics"):
        if isinstance(doc.get(key), list):
            metrics.extend(m for m in doc[key] if isinstance(m, dict))
    metric_ids = {str(m.get("id", "")).strip() for m in metrics}
    if COMPLIANCE_METRIC_ID not in metric_ids:
        problems.append(f"missing mandatory metric '{COMPLIANCE_METRIC_ID}'")
    for m in metrics:
        mid = str(m.get("id", "")).strip() or "<unnamed>"
        for field in ("id", "unit", "formula"):
            if not str(m.get(field, "")).strip():
                problems.append(f"metric {mid} missing {field}")
        if str(m.get("unit", "")).strip() == "ratio" and not isinstance(m.get("range"), dict):
            problems.append(f"ratio metric {mid} must declare a range")
        bad = sorted(FORBIDDEN_METRIC_VALUE_KEYS & set(m.keys()))
        if bad:
            problems.append(f"metric {mid} pre-bakes values: {', '.join(bad)}")
    return problems


def semantic_errors(data: dict, path: Path, repo_root: Path) -> list[str]:
    errors: list[str] = []
    bundle_dir = path.resolve().parent
    arms = data.get("arms") or []
    controlled_dimensions = data.get("controlled_dimensions") or []
    confounder_controls = data.get("confounder_controls") or []
    primary_axis = data.get("primary_intervention_axis") or {}
    control_arm, treatment_arm = _arms_by_role(arms)

    # --- design self-identity ------------------------------------------------
    dpath = str(data.get("design_artifact_path", ""))
    resolved_self, code = resolve_repo_relative_path(dpath, repo_root, must_exist=True)
    if code is not None or resolved_self is None or resolved_self != path.resolve():
        errors.append(format_error(
            "CONDITION_DESIGN_REQUIRES_DESIGN_SELF_IDENTITY", path,
            f"design_artifact_path ({display_source_path(dpath)}) must resolve to the validated file "
            f"({display_path(path)}); a mismatch lets the freeze bind a different file.",
        ))

    # --- precondition snapshot (frozen, not live) ----------------------------
    snap_problems, gate_block = _snapshot_problems(data, bundle_dir, repo_root)
    if snap_problems:
        errors.append(format_error(
            "CONDITION_DESIGN_REQUIRES_VALID_PRECONDITION_SNAPSHOT", path,
            "the frozen precondition snapshot must be a coherent, identity-matched gate+readiness "
            "capture (criteria_defined, design allowed, execution/assessment/comparison blocked, "
            "target open); offending: " + "; ".join(snap_problems),
        ))

    # --- gate requirements are a minimum set (from the snapshot) -------------
    if gate_block is not None:
        subset_problems = _gate_subset_problems(data, gate_block)
        if subset_problems:
            errors.append(format_error(
                "CONDITION_DESIGN_REQUIRES_GATE_REQUIREMENTS_SUBSET", path,
                "the design must control at least the gate-required dimensions and carry at least the "
                "gate-required confounders without weakening their effect; offending: "
                + "; ".join(subset_problems),
            ))

    # --- exactly one control + one treatment ---------------------------------
    roles = sorted(str(a.get("role", "")).strip() for a in arms if isinstance(a, dict))
    if roles != ["control", "treatment"]:
        errors.append(format_error(
            "CONDITION_DESIGN_REQUIRES_EXACTLY_TWO_ARMS", path,
            f"arms must be exactly one 'control' and one 'treatment'; found roles {roles}.",
        ))

    # --- single primary axis (assigned instruction), varied across arms ------
    axis_id = str(primary_axis.get("id", "")).strip() if isinstance(primary_axis, dict) else ""
    if axis_id != EXPECTED_PRIMARY_AXIS:
        errors.append(format_error(
            "CONDITION_DESIGN_REQUIRES_SINGLE_PRIMARY_AXIS", path,
            f"primary_intervention_axis.id must be {EXPECTED_PRIMARY_AXIS!r}; found {axis_id!r}.",
        ))
    elif control_arm is not None and treatment_arm is not None:
        if str(control_arm.get("workflow_protocol", "")).strip() == str(treatment_arm.get("workflow_protocol", "")).strip():
            errors.append(format_error(
                "CONDITION_DESIGN_REQUIRES_SINGLE_PRIMARY_AXIS", path,
                "the two arms must take different workflow_protocol values along the single primary axis.",
            ))

    # --- primary axis must not also be a controlled dimension ----------------
    if EXPECTED_PRIMARY_AXIS in set(_ids(controlled_dimensions)) or axis_id in set(_ids(controlled_dimensions)):
        errors.append(format_error(
            "CONDITION_DESIGN_REQUIRES_PRIMARY_AXIS_NOT_CONTROLLED", path,
            "the selected primary axis must not also appear in controlled_dimensions (it is the one "
            "dimension allowed to vary).",
        ))

    # --- material, pre-execution-observable assigned contrast ----------------
    if control_arm is not None and treatment_arm is not None:
        mat: list[str] = []
        if str(control_arm.get("workflow_protocol", "")).strip() != CONTROL_WORKFLOW_PROTOCOL:
            mat.append(f"control workflow_protocol must be {CONTROL_WORKFLOW_PROTOCOL!r}")
        if not _spec_is_no_upfront(control_arm.get("workflow_protocol_spec", {})):
            mat.append("control must carry no assigned upfront-specification requirement")
        if str(treatment_arm.get("workflow_protocol", "")).strip() != TREATMENT_WORKFLOW_PROTOCOL:
            mat.append(f"treatment workflow_protocol must be {TREATMENT_WORKFLOW_PROTOCOL!r}")
        if not _spec_is_full_upfront(treatment_arm.get("workflow_protocol_spec", {})):
            mat.append("treatment must require a complete, completeness-checked upfront specification "
                       "with sections: " + ", ".join(MANDATORY_TREATMENT_SPEC_SECTIONS))
        if mat:
            errors.append(format_error(
                "CONDITION_DESIGN_REQUIRES_MATERIAL_CONTRAST", path,
                "the assigned workflow-instruction contrast must be material and observable before "
                "execution, not a cosmetic relabel; " + "; ".join(mat),
            ))

        # --- only the primary axis may differ (overlay/condition) ------------
        only: list[str] = []
        if str(control_arm.get("overlay_ref", "")).strip() == str(treatment_arm.get("overlay_ref", "")).strip():
            only.append("both arms share the same overlay_ref")
        cia = data.get("condition_input_assembly") or {}
        cia_arms = cia.get("arms") if isinstance(cia, dict) else None
        if isinstance(cia_arms, dict):
            for role, arm in (("control", control_arm), ("treatment", treatment_arm)):
                entry = cia_arms.get(role) or {}
                if isinstance(entry, dict) and str(entry.get("overlay_ref", "")).strip() != str(arm.get("overlay_ref", "")).strip():
                    only.append(f"condition_input_assembly.arms.{role}.overlay_ref disagrees with arm overlay_ref")
        if only:
            errors.append(format_error(
                "CONDITION_DESIGN_REQUIRES_ONLY_PRIMARY_AXIS_DIFFERENCE", path,
                "arms may differ only along the assigned workflow overlay, and the input assembly must "
                "agree with the arm overlays; " + "; ".join(only),
            ))

    # --- assigned condition vs observed compliance separated -----------------
    aso: list[str] = []
    ccr = data.get("condition_compliance_requirements") or {}
    if not (isinstance(ccr, dict) and (ccr.get("required_future_evidence") or [])):
        aso.append("condition_compliance_requirements.required_future_evidence is empty")
    surfaces = data.get("artifact_surfaces") or {}
    arm_proc = (surfaces.get("arm_specific_process_artifacts") or {}) if isinstance(surfaces, dict) else {}
    if "preimplementation_specification" not in [str(x).strip() for x in (arm_proc.get("treatment") or [])]:
        aso.append("artifact_surfaces.arm_specific_process_artifacts.treatment must include 'preimplementation_specification'")
    if [str(x).strip() for x in (arm_proc.get("control") or [])]:
        aso.append("control must have no arm-specific process artifacts")
    if aso:
        errors.append(format_error(
            "CONDITION_DESIGN_REQUIRES_ASSIGNED_VS_OBSERVED_SEPARATION", path,
            "the assigned condition and the later observed compliance must be separated, and the "
            "treatment process artifact must not be scored as an outcome; " + "; ".join(aso),
        ))

    # --- shared verification / measurement child semantics -------------------
    vproblems = _verification_problems(data, bundle_dir, repo_root)
    if vproblems:
        errors.append(format_error(
            "CONDITION_DESIGN_REQUIRES_SHARED_VERIFICATION", path,
            "the shared verification protocol must apply equally to both arms, not execute, forbid "
            "per-arm overrides, and defer the harness; " + "; ".join(vproblems),
        ))
    mproblems = _measurement_problems(data, bundle_dir, repo_root)
    if mproblems:
        errors.append(format_error(
            "CONDITION_DESIGN_REQUIRES_SHARED_MEASUREMENT", path,
            "the shared measurement protocol must apply equally, forbid post-hoc/treatment-only "
            "scoring, record no values, define units/formulas, and include the compliance metric; "
            + "; ".join(mproblems),
        ))

    # --- child identity (snapshot/freeze covered in their own rules) ---------
    child_id_problems: list[str] = []
    for label, block in (("verification_surface", data.get("verification_surface")),
                         ("measurement_surface", data.get("measurement_surface"))):
        ref = str((block or {}).get("protocol_ref", "")) if isinstance(block, dict) else ""
        doc, prob = _load_bundle_yaml(ref, bundle_dir, repo_root)
        if doc is not None:
            child_id_problems += _child_identity_problems(label, doc, data)
    if child_id_problems:
        errors.append(format_error(
            "CONDITION_DESIGN_REQUIRES_CHILD_IDENTITY", path,
            "every child protocol must carry the design's design_id/series_id/challenge_version; "
            + "; ".join(child_id_problems),
        ))

    # --- bundle boundary -----------------------------------------------------
    boundary: list[str] = []
    for raw_ref, label in _bundle_refs(data):
        resolved, rcode = resolve_repo_relative_path(raw_ref, repo_root, must_exist=True)
        if rcode is not None or resolved is None:
            continue  # path safety reported separately
        if not resolved.is_file():
            boundary.append(f"{label}={display_source_path(raw_ref)}: not a regular file")
        elif not _inside(resolved, bundle_dir):
            boundary.append(f"{label}={display_source_path(raw_ref)}: outside the design bundle")
    if boundary:
        errors.append(format_error(
            "CONDITION_DESIGN_REQUIRES_BUNDLE_BOUNDARY", path,
            "every bundle artifact (overlays, shared input, protocols, snapshot, freeze) must live "
            "inside the design bundle directory; " + "; ".join(boundary),
        ))

    # --- valid, acyclic, complete freeze (no commit self-reference) ----------
    freeze_problems = _freeze_problems(data, bundle_dir, repo_root)
    if freeze_problems:
        errors.append(format_error(
            "CONDITION_DESIGN_REQUIRES_VALID_FREEZE", path,
            "the SHA-256 freeze manifest must be identity-matched, RFC-3339 timestamped, acyclic, "
            "free of commit self-reference, and cover every bundle file; " + "; ".join(freeze_problems),
        ))

    # --- recursive execution-artifact prohibition ----------------------------
    exec_problems = _execution_artifact_problems(bundle_dir)
    if exec_problems:
        errors.append(format_error(
            "CONDITION_DESIGN_FORBIDS_EXECUTION_ARTIFACTS", path,
            "the design bundle must contain no execution artifacts at any depth; offending: "
            + ", ".join(exec_problems),
        ))

    # --- unique semantic ids -------------------------------------------------
    dup_problems: list[str] = []
    for label, items in (("arms", arms), ("controlled_dimensions", controlled_dimensions),
                         ("confounder_controls", confounder_controls)):
        dups = _duplicates(_ids(items))
        if dups:
            dup_problems.append(f"{label}: " + ", ".join(dups))
    if dup_problems:
        errors.append(format_error(
            "CONDITION_DESIGN_REQUIRES_UNIQUE_SEMANTIC_IDS", path,
            "ids must be unique within each list; duplicated — " + "; ".join(dup_problems),
        ))

    # --- mandatory anti-overclaim non-claims ---------------------------------
    declared = {str(x).strip().lower() for x in (data.get("does_not_establish") or [])}
    missing = [x for x in MANDATORY_DOES_NOT_ESTABLISH if x not in declared]
    wrong = [x for x in FORBIDDEN_SELECTION_NON_CLAIMS if x in declared]
    if missing or wrong:
        detail = []
        if missing:
            detail.append("missing: " + ", ".join(missing))
        if wrong:
            detail.append("must not be listed (this design establishes them): " + ", ".join(wrong))
        errors.append(format_error(
            "CONDITION_DESIGN_REQUIRES_MANDATORY_NON_CLAIMS", path,
            "does_not_establish must include all static anti-overclaim non-claims and must not deny "
            "the design's own contribution; " + "; ".join(detail),
        ))

    # --- safe, existing repo paths -------------------------------------------
    safe: list[str] = []
    for raw_ref, label in _bundle_refs(data):
        _, rcode = resolve_repo_relative_path(raw_ref, repo_root, must_exist=True)
        if rcode == "ESCAPE":
            safe.append(f"{label}={display_source_path(raw_ref)}: resolves outside the repo root")
        elif rcode == "NOT_FOUND":
            safe.append(f"{label}={display_source_path(raw_ref)}: does not exist")
    for entry in (data.get("source_evidence") or []):
        if not isinstance(entry, dict):
            continue
        raw_ref = str(entry.get("path", ""))
        resolved, rcode = resolve_repo_relative_path(raw_ref, repo_root, must_exist=True)
        if rcode == "ESCAPE":
            safe.append(f"source_evidence {display_source_path(raw_ref)}: resolves outside the repo root")
        elif rcode == "NOT_FOUND":
            safe.append(f"source_evidence {display_source_path(raw_ref)}: does not exist")
        elif resolved is not None and not resolved.is_file():
            safe.append(f"source_evidence {display_source_path(raw_ref)}: not a regular file")
    if safe:
        errors.append(format_error(
            "CONDITION_DESIGN_REQUIRES_SAFE_EXISTING_PATHS", path,
            "every referenced bundle/context path must be a safe, existing, regular file; offending: "
            + "; ".join(safe),
        ))

    return errors


def validate_file(path: Path, validator: Draft202012Validator, repo_root: Path | None = None):
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
    """Discover only real condition-design artifacts (artifact_type match), so this strongly
    specialized v1 validator never claims unrelated future condition-design.yml files."""
    experiments_dir = repo_root / "experiments"
    if not experiments_dir.is_dir():
        return []
    out = []
    for candidate in sorted(experiments_dir.glob(DESIGN_GLOB)):
        try:
            doc = yaml.safe_load(candidate.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, yaml.YAMLError):
            out.append(candidate)  # surface parse errors during validation
            continue
        if isinstance(doc, dict) and str(doc.get("artifact_type", "")).strip() == DESIGN_ARTIFACT_TYPE:
            out.append(candidate)
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Model-Lab condition-design artifacts.")
    parser.add_argument("paths", nargs="*", help="condition-design YAML files (default: discover under experiments/).")
    args = parser.parse_args(argv)

    try:
        validator = load_schema_validator()
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        return 2

    if args.paths:
        paths = [Path(r) if Path(r).is_absolute() else (REPO_ROOT / r) for r in args.paths]
    else:
        paths = discover_artifacts(REPO_ROOT)
        if not paths:
            print("ℹ️ No model-lab-condition-design artifacts found; model-lab-condition-design validation skipped.")
            return 0

    highest, passed = 0, 0
    for path in paths:
        code, errors = validate_file(path, validator)
        highest = max(highest, code)
        for e in errors:
            print(e)
        if code == 0:
            passed += 1
            print(f"✅ {display_path(path)}")
    checked = len(paths)
    print(f"Model-lab-condition-design artifacts: checked={checked}, passed={passed}, failed={checked - passed}")
    return highest


if __name__ == "__main__":
    sys.exit(main())
