#!/usr/bin/env python3
"""validate_model_lab_execution_readiness.py — Run-004 v1 readiness preflight validator.

This is a Run-004-v1-specific contract validator, not a generic execution-readiness
framework. It validates a pre-execution bundle that may honestly be blocked or, for
synthetic fixtures/future work, fully bound and authorized. It never executes Run-004.

Exit codes: 0 valid · 1 semantic violation · 2 schema/parse/tool error.
Requires: python3 -m pip install pyyaml jsonschema
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath

try:
    import yaml
    from jsonschema import Draft202012Validator
    from jsonschema.exceptions import SchemaError
except ImportError as exc:
    print(
        "ERROR: Missing dependencies for model-lab-execution-readiness validation "
        "(need PyYAML, jsonschema).",
        file=sys.stderr,
    )
    raise SystemExit(2) from exc


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCHEMA_DIR = REPO_ROOT / "schemas"
SCHEMA_PATH = SCHEMA_DIR / "model-lab-execution-readiness.v1.schema.json"
FREEZE_SCHEMA_PATH = SCHEMA_DIR / "model-lab-execution-readiness-freeze-manifest.v1.schema.json"
EVIDENCE_SCHEMA_PATH = SCHEMA_DIR / "model-lab-execution-readiness-evidence.v1.schema.json"
SEED_SCHEMA_PATH = SCHEMA_DIR / "model-lab-execution-seed-manifest.v1.schema.json"

RUN_004_SERIES_ID = "2026-05-31_model-lab-replication-series"
RUN_004_DESIGN_ID = "run-004-condition-contrast"
RUN_004_CHALLENGE_VERSION = "rest-api-v1"
RUN_004_ARTIFACT_TYPE = "model_lab_execution_readiness"
RUN_004_FREEZE_ARTIFACT_TYPE = "model_lab_execution_readiness_freeze_manifest"
RUN_004_CONTRACT_VERSION = "run-004-execution-readiness.v1"
RUN_004_DISCOVERY_GLOB = "*/artifacts/*/execution-readiness.yml"

DESIGN_CONDITION_PATH = (
    "experiments/2026-05-31_model-lab-replication-series/artifacts/"
    "run-004-condition-contrast-design/condition-design.yml"
)
DESIGN_MEASUREMENT_PATH = (
    "experiments/2026-05-31_model-lab-replication-series/artifacts/"
    "run-004-condition-contrast-design/measurement-protocol.yml"
)
DESIGN_FREEZE_PATH = (
    "experiments/2026-05-31_model-lab-replication-series/artifacts/"
    "run-004-condition-contrast-design/freeze-manifest.yml"
)
DESIGN_BUNDLE_DIR = (
    "experiments/2026-05-31_model-lab-replication-series/artifacts/"
    "run-004-condition-contrast-design"
)
DESIGN_FREEZE_ARTIFACT_TYPE = "model_lab_condition_design_freeze_manifest"
DESIGN_ARTIFACT_TYPE = "model_lab_condition_design"
DESIGN_EXPECTED_HASH_COUNT = 12

EXPECTED_BUNDLE_FILENAMES = {
    "execution-readiness.yml",
    "freeze-manifest.yml",
    "source-snapshots/condition-design.snapshot",
    "source-snapshots/design-freeze-manifest.snapshot",
}
FORBIDDEN_EXECUTION_FILES = frozenset(
    {
        "run.yml",
        "run_meta.json",
        "execution.txt",
        "measurement.yml",
        "auditor-output.yml",
        "comparability.yml",
        "evidence-pack.yml",
    }
)
FORBIDDEN_EXECUTION_DIRS = frozenset({"implementation", "src", "tests"})
MANDATORY_NON_CLAIMS = frozenset(
    {
        "run_004_executed",
        "run_004_result_measured",
        "result_assessment_allowed",
        "comparison_ready",
        "weak_condition_contrast_resolved",
        "model_quality",
        "comparative_superiority",
        "condition_effect",
        "outcome_upgrade",
        "adoption_readiness",
        "promotion_readiness",
        "production_readiness",
        "security_readiness",
        "individual_prompt_component_effect_isolated",
        "execution_artifacts_present",
    }
)
READY_ALLOWED_OPEN_BLOCKERS = {"WEAK_CONDITION_CONTRAST_OPEN"}
READY_REQUIRED_RUNTIME_FIELDS = (
    "provider",
    "exact_model_id",
    "model_revision_or_version",
    "agent_program",
    "agent_version",
    "operating_mode",
    "system_developer_context_identity",
    "network_policy",
    "cache_policy",
    "dependency_resolution_strategy",
)
READY_REQUIRED_PERMISSION_FIELDS = ("filesystem", "shell", "network", "connectors")
READY_REQUIRED_ENV_FIELDS = (
    "os_or_container_identity",
    "architecture",
    "node_version",
    "npm_version",
    "python_version",
)
READY_REQUIRED_SAMPLING_FIELDS = ("temperature", "top_p", "top_k", "max_output_tokens", "seed")
READY_REQUIRED_METRIC_IDS = {
    "functional_test_pass_ratio",
    "error_case_test_pass_ratio",
    "forced_500_check_pass",
    "workflow_protocol_compliance",
    "time_to_validated_change_seconds",
    "time_to_stop_seconds",
    "rework_steps",
    "human_intervention_count",
    "scope_drift_status",
    "contamination_status",
    "timeout_count",
    "abort_status",
    "retry_count",
}
SUPPLEMENTAL_METRIC_RULES = {
    "contamination_status": "none / prompt_metadata_exposure / other_arm_artifact_exposure / shared_context_exposure / operator_intervention / workspace_seed_drift / unknown",
    "timeout_count": "number of predeclared timeout events; never impute a timeout as zero or success",
    "abort_status": "completed / aborted; any abort blocks comparison and preserves incomplete metrics as null",
    "retry_count": "number of predeclared symmetric retries; silent or one-sided retries are invalid",
}
EVIDENCE_CLAIM_KINDS = frozenset({
    "model_identity",
    "agent_identity",
    "access_policy",
    "sampling_config",
    "runtime_environment",
    "workspace_isolation",
    "visibility_boundary",
    "harness",
    "harness_neutrality",
    "forced_500_trigger",
    "first_mutation_trace",
})
PLACEHOLDER_VALUES = {
    "",
    "unknown",
    "not_recorded",
    "not-recorded",
    "not recorded",
    "tbd",
    "todo",
    "pending",
    "n/a",
    "na",
    "none",
    "null",
    "unbound",
    "unresolved",
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
DRIVE_LETTER_RE = re.compile(r"^[A-Za-z]:")
ROLE_LEAK_RE = re.compile(r"control|treatment", re.IGNORECASE)
_SCHEMA_CACHE: dict[str, Draft202012Validator] = {}


class ToolError(Exception):
    """A verification tool/environment failure that must fail closed with exit 2."""


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except (OSError, RuntimeError, ValueError, UnicodeError):
        return str(path)


def display_source_path(raw) -> str:
    if not isinstance(raw, str):
        return str(raw)
    out = []
    lead = len(raw) - len(raw.lstrip())
    trail = len(raw.rstrip())
    for i, c in enumerate(raw):
        cp = ord(c)
        if c == " " and (i < lead or i >= trail):
            out.append(r"\x20")
        elif cp <= 0x1F or cp == 0x7F:
            out.append({"\t": r"\t", "\n": r"\n", "\r": r"\r"}.get(c, f"\\x{cp:02x}"))
        elif 0xD800 <= cp <= 0xDFFF:
            out.append(f"\\u{cp:04x}")
        else:
            out.append(c)
    return "".join(out)


def _has_forbidden_codepoint(text: str) -> bool:
    return any(ord(c) <= 0x1F or ord(c) == 0x7F or 0xD800 <= ord(c) <= 0xDFFF for c in text)


def _inside(candidate: Path, root: Path) -> bool:
    try:
        candidate.relative_to(root)
        return True
    except ValueError:
        return False


def resolve_repo_relative_path(rel_path, repo_root: Path, *, must_exist: bool):
    raw = str(rel_path)
    if _has_forbidden_codepoint(raw) or raw != raw.strip() or not raw:
        return None, "ESCAPE"
    if raw.startswith("/") or DRIVE_LETTER_RE.match(raw) or "\\" in raw:
        return None, "ESCAPE"
    if ".." in PurePosixPath(raw).parts:
        return None, "ESCAPE"
    root = repo_root.resolve()
    candidate = root / raw
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


def load_validator(schema_path: Path) -> Draft202012Validator:
    key = str(schema_path)
    if key in _SCHEMA_CACHE:
        return _SCHEMA_CACHE[key]
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
    except FileNotFoundError as exc:
        raise RuntimeError(f"schema file missing: {display_path(schema_path)}") from exc
    except (json.JSONDecodeError, UnicodeDecodeError, OSError) as exc:
        raise RuntimeError(f"schema unreadable: {display_path(schema_path)}: {exc}") from exc
    except SchemaError as exc:
        raise RuntimeError(f"schema invalid: {display_path(schema_path)}: {exc.message}") from exc
    validator = Draft202012Validator(schema)
    _SCHEMA_CACHE[key] = validator
    return validator


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


def _schema_error_sort_key(error):
    return tuple((type(part).__name__, str(part)) for part in error.absolute_path)


def schema_errors(validator: Draft202012Validator, data: dict, path: Path, *, label: str = "") -> list[str]:
    errors = []
    prefix = f"{label} " if label else ""
    for err in sorted(validator.iter_errors(data), key=_schema_error_sort_key):
        loc = ".".join(str(p) for p in err.absolute_path) or "$"
        errors.append(f"ERROR {prefix}path={display_path(path)} instance_path={loc}: {err.message}")
    return errors


def format_error(rule_id: str, path: Path, message: str) -> str:
    return f"ERROR rule={rule_id} path={display_path(path)}: {message}"


def _sha256_of(path: Path):
    try:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(65536), b""):
                digest.update(chunk)
        return digest.hexdigest()
    except (OSError, ValueError):
        return None


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _bundle_content_hash(entries: list[dict]) -> str:
    digest = hashlib.sha256()
    for entry in sorted(entries, key=lambda item: str(item.get("path", ""))):
        digest.update(str(entry.get("path", "")).encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(entry.get("sha256", "")).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def _parse_rfc3339(value):
    if not isinstance(value, str):
        return None
    text = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        return _dt.datetime.fromisoformat(text)
    except ValueError:
        return None


def _is_placeholder(value) -> bool:
    if value is None:
        return True
    if not isinstance(value, str):
        return False
    return value.strip().lower() in PLACEHOLDER_VALUES


def _evidence_paths_registered(paths, registry: dict[str, set[str]], required_kind: str) -> bool:
    return bool(paths) and all(
        isinstance(item, str)
        and item in registry
        and required_kind in registry[item]
        for item in paths
    )


def _binding_is_bound(field, registry: dict[str, set[str]], required_kind: str) -> bool:
    return (
        isinstance(field, dict)
        and field.get("status") == "bound"
        and not _is_placeholder(field.get("value"))
        and _evidence_paths_registered(field.get("evidence"), registry, required_kind)
    )


def _binding_is_sampling_ready(
    field, unavailable_ids: set[str], field_id: str, registry: dict[str, set[str]]
) -> bool:
    if _binding_is_bound(field, registry, "sampling_config"):
        return True
    return (
        isinstance(field, dict)
        and field.get("status") == "unavailable_documented"
        and field.get("value") is None
        and field_id in unavailable_ids
        and not _is_placeholder(field.get("reason"))
        and _evidence_paths_registered(field.get("evidence"), registry, "sampling_config")
    )


def _has_placeholder_item(values) -> bool:
    return any(_is_placeholder(item) for item in (values or []))


def _is_fixture_candidate(path: Path, repo_root: Path) -> bool:
    try:
        rel = path.resolve().relative_to(repo_root.resolve()).as_posix()
    except (OSError, RuntimeError, ValueError, UnicodeError):
        return False
    return rel.startswith("tests/fixtures/model_lab_execution_readiness/")


def _evidence_registry(data: dict, path: Path, repo_root: Path):
    registry: dict[str, set[str]] = {}
    problems = []
    fixture_candidate = _is_fixture_candidate(path, repo_root)
    evidence_validator = load_validator(EVIDENCE_SCHEMA_PATH)
    root = repo_root.resolve()
    for entry in data.get("evidence_registry") or []:
        if not isinstance(entry, dict):
            continue
        raw = str(entry.get("path", ""))
        if raw in registry:
            problems.append(f"duplicate evidence_registry path: {display_source_path(raw)}")
            continue
        resolved, code = _load_ref(raw, repo_root)
        if code is not None or resolved is None:
            problems.append(f"evidence_registry path is not a safe existing regular file: {display_source_path(raw)}")
            continue
        try:
            rel = resolved.relative_to(root).as_posix()
        except ValueError:
            rel = raw
        if not fixture_candidate and rel.startswith("tests/fixtures/"):
            problems.append(f"fixture evidence is forbidden for a real readiness artifact: {display_source_path(raw)}")
        declared = str(entry.get("sha256", ""))
        if _sha256_of(resolved) != declared:
            problems.append(f"evidence_registry sha256 mismatch: {display_source_path(raw)}")
        kinds = {str(kind) for kind in (entry.get("kinds") or [])}
        unsupported = kinds - EVIDENCE_CLAIM_KINDS - {"synthetic_fixture"}
        if unsupported:
            problems.append(f"unsupported evidence kinds for {display_source_path(raw)}: " + ", ".join(sorted(unsupported)))
        try:
            document = load_yaml(resolved)
        except (FileNotFoundError, ValueError) as exc:
            problems.append(f"evidence document is invalid or unreadable: {display_source_path(raw)}: {exc}")
            registry[raw] = kinds
            continue
        doc_errors = list(evidence_validator.iter_errors(document))
        if doc_errors:
            detail = "; ".join(
                f"{'.'.join(str(p) for p in err.absolute_path) or '$'}: {err.message}"
                for err in sorted(doc_errors, key=_schema_error_sort_key)
            )
            problems.append(f"evidence document schema invalid: {display_source_path(raw)}: {detail}")
            registry[raw] = kinds
            continue
        synthetic = document.get("synthetic_fixture") is True
        if synthetic != ("synthetic_fixture" in kinds):
            problems.append(f"synthetic_fixture registry kind must match evidence document: {display_source_path(raw)}")
        if synthetic and not fixture_candidate:
            problems.append("synthetic_fixture evidence is forbidden outside validator fixtures")
        claims = document.get("claims") or []
        claim_kinds = [str(claim.get("kind", "")) for claim in claims if isinstance(claim, dict)]
        duplicates = sorted({kind for kind in claim_kinds if claim_kinds.count(kind) > 1})
        if duplicates:
            problems.append(f"duplicate evidence claims for {display_source_path(raw)}: " + ", ".join(duplicates))
        declared_claim_kinds = kinds - {"synthetic_fixture"}
        if not fixture_candidate and len(declared_claim_kinds) != 1:
            problems.append(
                f"real readiness evidence must bind exactly one claim kind per file: {display_source_path(raw)}"
            )
        missing = declared_claim_kinds - set(claim_kinds)
        extra = set(claim_kinds) - declared_claim_kinds
        if missing:
            problems.append(f"evidence document lacks declared claims for {display_source_path(raw)}: " + ", ".join(sorted(missing)))
        if extra:
            problems.append(f"evidence document has undeclared claims for {display_source_path(raw)}: " + ", ".join(sorted(extra)))
        registry[raw] = kinds
    return registry, problems


def _general_evidence_errors(data: dict, repo_root: Path) -> list[str]:
    problems = []
    refs = []
    refs.extend(item.get("path") for item in (data.get("evidence") or []) if isinstance(item, dict))
    for blocker in data.get("blockers") or []:
        if isinstance(blocker, dict):
            refs.extend(blocker.get("evidence") or [])
    for raw in refs:
        resolved, code = _load_ref(str(raw), repo_root)
        if code is not None or resolved is None:
            problems.append(f"declared evidence path is not a safe existing regular file: {display_source_path(str(raw))}")
    return problems


def _seed_manifest_errors(raw_ref, declared_hash, repo_root: Path, fixture_candidate: bool) -> list[str]:
    problems = []
    raw = str(raw_ref or "")
    resolved, code = _load_ref(raw, repo_root)
    if code is not None or resolved is None:
        return [f"execution seed manifest is not a safe existing file: {display_source_path(raw)}"]
    try:
        rel = resolved.relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        rel = raw
    if not fixture_candidate and rel.startswith("tests/fixtures/"):
        problems.append("fixture seed manifest is forbidden for a real readiness artifact")
    if _sha256_of(resolved) != declared_hash:
        problems.append("execution seed manifest sha256 mismatch")
    try:
        manifest = load_yaml(resolved)
    except (FileNotFoundError, ValueError) as exc:
        return problems + [f"execution seed manifest is invalid or unreadable: {exc}"]
    schema_problems = list(load_validator(SEED_SCHEMA_PATH).iter_errors(manifest))
    if schema_problems:
        detail = "; ".join(
            f"{'.'.join(str(p) for p in err.absolute_path) or '$'}: {err.message}"
            for err in sorted(schema_problems, key=_schema_error_sort_key)
        )
        return problems + [f"execution seed manifest schema invalid: {detail}"]
    synthetic = manifest.get("synthetic_fixture") is True
    if synthetic and not fixture_candidate:
        problems.append("synthetic execution seed is forbidden outside validator fixtures")
    entries = manifest.get("files") or []
    seed_kind = manifest.get("seed_kind")
    if seed_kind == "empty_directory":
        if manifest.get("root_ref") is not None or entries:
            problems.append("empty_directory seed must have root_ref=null and files=[]")
        if _bundle_content_hash(entries) != manifest.get("content_sha256"):
            problems.append("execution seed manifest content_sha256 mismatch")
        return problems
    if seed_kind != "file_manifest":
        return problems + ["execution seed manifest seed_kind is unsupported"]
    root_raw = str(manifest.get("root_ref", ""))
    root_path, root_code = resolve_repo_relative_path(root_raw, repo_root, must_exist=True)
    if root_code is not None or root_path is None or not root_path.is_dir():
        return problems + [f"execution seed root_ref is not a safe existing directory: {display_source_path(root_raw)}"]
    try:
        root_rel = root_path.relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        root_rel = root_raw
    if not fixture_candidate and root_rel.startswith("tests/fixtures/"):
        problems.append("fixture seed root is forbidden for a real readiness artifact")
    paths = [str(entry.get("path", "")) for entry in entries if isinstance(entry, dict)]
    declared_resolved = set()
    for duplicate in sorted({item for item in paths if paths.count(item) > 1}):
        problems.append(f"duplicate execution seed file path: {display_source_path(duplicate)}")
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        file_raw = str(entry.get("path", ""))
        file_path, file_code = _load_ref(file_raw, repo_root)
        if file_code is not None or file_path is None:
            problems.append(f"execution seed file is not a safe existing regular file: {display_source_path(file_raw)}")
            continue
        if not _inside(file_path, root_path):
            problems.append(f"execution seed file lies outside root_ref: {display_source_path(file_raw)}")
            continue
        declared_resolved.add(file_path)
        if _sha256_of(file_path) != str(entry.get("sha256", "")):
            problems.append(f"execution seed file sha256 mismatch: {display_source_path(file_raw)}")
    actual_resolved = set()
    try:
        root_entries = sorted(root_path.rglob("*"))
    except OSError as exc:
        return problems + [f"cannot walk execution seed root ({exc})"]
    for item in root_entries:
        try:
            item_rel = item.relative_to(root_path).as_posix()
        except ValueError:
            item_rel = str(item)
        if item.is_symlink():
            problems.append(f"symlink not allowed in execution seed root: {item_rel}")
        elif item.is_dir():
            continue
        elif item.is_file():
            actual_resolved.add(item.resolve())
        else:
            problems.append(f"non-regular entry in execution seed root: {item_rel}")
    for missing in sorted(actual_resolved - declared_resolved):
        problems.append(f"execution seed manifest omits root file: {missing.relative_to(root_path).as_posix()}")
    for extra in sorted(declared_resolved - actual_resolved):
        problems.append(f"execution seed manifest declares absent root file: {display_path(extra)}")
    if _bundle_content_hash(entries) != manifest.get("content_sha256"):
        problems.append("execution seed manifest content_sha256 mismatch")
    return problems


def _seed_binding_errors(data: dict, repo_root: Path, path: Path) -> list[str]:
    ws = data.get("workspace_session_isolation") or {}
    arms = ws.get("arms") or {}
    problems = []
    fixture_candidate = _is_fixture_candidate(path, repo_root)
    seed_ids = []
    seed_kinds = []
    seed_refs = []
    seed_hashes = []
    for role in ("control", "treatment"):
        arm = arms.get(role) or {}
        if arm.get("arm_id") != role:
            problems.append(f"workspace arm {role} must have arm_id={role}")
        seed_id = arm.get("execution_seed")
        seed_kind = arm.get("execution_seed_kind")
        seed_ref = arm.get("execution_seed_ref")
        seed_hash = arm.get("seed_hash")
        if _is_placeholder(seed_id):
            problems.append(f"workspace_session_isolation.arms.{role}.execution_seed must be bound")
        else:
            seed_ids.append(str(seed_id))
        if seed_kind not in {"empty_directory", "file_manifest"}:
            problems.append(f"workspace_session_isolation.arms.{role}.execution_seed_kind must be supported")
        else:
            seed_kinds.append(str(seed_kind))
        if _is_placeholder(seed_ref) or _is_placeholder(seed_hash):
            problems.append(f"workspace_session_isolation.arms.{role} must bind execution_seed_ref and seed_hash")
        else:
            seed_refs.append(str(seed_ref))
            seed_hashes.append(str(seed_hash))
            manifest_path, code = _load_ref(str(seed_ref), repo_root)
            manifest_kind = None
            manifest_id = None
            if code is None and manifest_path is not None:
                try:
                    manifest_data = load_yaml(manifest_path)
                    manifest_kind = manifest_data.get("seed_kind")
                    manifest_id = manifest_data.get("seed_id")
                except (FileNotFoundError, ValueError):
                    pass
            if manifest_kind is not None and manifest_kind != seed_kind:
                problems.append(f"workspace_session_isolation.arms.{role}.execution_seed_kind must match seed manifest")
            if manifest_id is not None and manifest_id != seed_id:
                problems.append(f"workspace_session_isolation.arms.{role}.execution_seed must match seed manifest seed_id")
            problems.extend(
                f"workspace_session_isolation.arms.{role}: {problem}"
                for problem in _seed_manifest_errors(seed_ref, seed_hash, repo_root, fixture_candidate)
            )
    if (
        len(seed_ids) != 2
        or len(set(seed_ids)) != 1
        or len(seed_kinds) != 2
        or len(set(seed_kinds)) != 1
        or len(seed_refs) != 2
        or len(set(seed_refs)) != 1
        or len(seed_hashes) != 2
        or len(set(seed_hashes)) != 1
    ):
        problems.append("both arms must use the identical content-bound execution seed manifest")
    return problems


def _session_isolation_errors(data: dict, registry: dict[str, set[str]]) -> list[str]:
    ws = data.get("workspace_session_isolation") or {}
    problems = []
    if ws.get("binding_status") != "bound":
        problems.append("workspace_session_isolation.binding_status must be bound")
    if not _evidence_paths_registered(ws.get("evidence"), registry, "workspace_isolation"):
        problems.append("workspace_session_isolation.evidence must be hash-registered workspace_isolation evidence")
    arms = ws.get("arms") or {}
    values_by_field: dict[str, list[str]] = {}
    for role in ("control", "treatment"):
        arm = arms.get(role) or {}
        for field in ("workspace_path", "session_id", "temp_dir", "cache_dir", "port_assignment", "cleanup_rule"):
            value = arm.get(field)
            if _is_placeholder(value):
                problems.append(f"workspace_session_isolation.arms.{role}.{field} must be bound")
            elif isinstance(value, str):
                values_by_field.setdefault(field, []).append(value)
        if arm.get("clean_start_state") is not True:
            problems.append(f"workspace_session_isolation.arms.{role}.clean_start_state must be true")
        for visible_field in ("workspace_path", "session_id", "temp_dir", "cache_dir"):
            visible_value = arm.get(visible_field)
            if isinstance(visible_value, str) and ROLE_LEAK_RE.search(visible_value):
                problems.append(f"workspace_session_isolation.arms.{role}.{visible_field} leaks an arm role token")
        for visible_path in arm.get("allowed_paths") or []:
            if isinstance(visible_path, str) and ROLE_LEAK_RE.search(visible_path):
                problems.append(f"workspace_session_isolation.arms.{role}.allowed_paths leaks an arm role token")
        if (
            not arm.get("allowed_paths")
            or not arm.get("forbidden_paths")
            or _has_placeholder_item(arm.get("allowed_paths"))
            or _has_placeholder_item(arm.get("forbidden_paths"))
        ):
            problems.append(
                f"workspace_session_isolation.arms.{role} must bind non-placeholder allowed_paths and forbidden_paths"
            )
    for field in ("workspace_path", "session_id", "temp_dir", "cache_dir", "port_assignment"):
        vals = values_by_field.get(field, [])
        if len(vals) == 2 and vals[0] == vals[1]:
            problems.append(f"both arms must not share the same {field}")
    return problems


def _canonical_metric_rules(repo_root: Path) -> tuple[dict[str, str], list[str]]:
    resolved, code = _load_ref(DESIGN_MEASUREMENT_PATH, repo_root)
    if code is not None or resolved is None:
        return {}, ["frozen measurement protocol is missing or unsafe"]
    try:
        protocol = load_yaml(resolved)
    except (FileNotFoundError, ValueError) as exc:
        return {}, [f"frozen measurement protocol is invalid or unreadable: {exc}"]
    problems = []
    if protocol.get("artifact_type") != "model_lab_condition_design_measurement_protocol":
        problems.append("frozen measurement protocol artifact_type mismatch")
    if protocol.get("design_id") != RUN_004_DESIGN_ID or protocol.get("series_id") != RUN_004_SERIES_ID:
        problems.append("frozen measurement protocol identity mismatch")
    if protocol.get("challenge_version") != RUN_004_CHALLENGE_VERSION:
        problems.append("frozen measurement protocol challenge_version mismatch")
    if protocol.get("applies_equally_to_both_arms") is not True or protocol.get("post_hoc_metric_selection_forbidden") is not True:
        problems.append("frozen measurement protocol equality/post-hoc guards are not true")
    rules = {}
    for section in ("primary_metrics", "secondary_metrics"):
        for item in protocol.get(section) or []:
            if not isinstance(item, dict):
                continue
            metric_id = str(item.get("id", ""))
            formula = item.get("formula")
            if not metric_id or not isinstance(formula, str) or not formula.strip():
                problems.append(f"frozen measurement protocol contains invalid {section} entry")
                continue
            if metric_id in rules:
                problems.append(f"duplicate frozen metric id: {metric_id}")
            rules[metric_id] = formula
    rules.update(SUPPLEMENTAL_METRIC_RULES)
    return rules, problems


def _required_blocker_ids(
    data: dict,
    registry: dict[str, set[str]],
    repo_root: Path,
    path: Path,
) -> set[str]:
    required = set()
    runtime = data.get("runtime_binding") or {}
    if any(
        not _binding_is_bound(runtime.get(name), registry, "model_identity")
        for name in ("provider", "exact_model_id", "model_revision_or_version")
    ):
        required.add("MODEL_BINDING_UNRESOLVED")
    if any(
        not _binding_is_bound(runtime.get(name), registry, "agent_identity")
        for name in ("agent_program", "agent_version", "operating_mode", "system_developer_context_identity")
    ):
        required.add("AGENT_BINDING_UNRESOLVED")
    sampling = runtime.get("sampling") or {}
    unavailable = {
        str(item.get("id", ""))
        for item in sampling.get("unavailable_parameters") or []
        if isinstance(item, dict)
    }
    if any(
        not _binding_is_sampling_ready(sampling.get(name), unavailable, name, registry)
        for name in READY_REQUIRED_SAMPLING_FIELDS
    ):
        required.add("SAMPLING_BINDING_UNRESOLVED")
    permissions = runtime.get("permissions") or {}
    if (
        not runtime.get("available_tools")
        or _has_placeholder_item(runtime.get("available_tools"))
        or any(
            not _binding_is_bound(permissions.get(name), registry, "access_policy")
            for name in READY_REQUIRED_PERMISSION_FIELDS
        )
    ):
        required.add("ACCESS_POLICY_UNRESOLVED")
    environment = runtime.get("environment") or {}
    if (
        any(
            not _binding_is_bound(environment.get(name), registry, "runtime_environment")
            for name in READY_REQUIRED_ENV_FIELDS
        )
        or any(
            not _binding_is_bound(runtime.get(name), registry, "runtime_environment")
            for name in ("network_policy", "cache_policy", "dependency_resolution_strategy")
        )
    ):
        required.add("RUNTIME_ENVIRONMENT_UNRESOLVED")
    if _seed_binding_errors(data, repo_root, path):
        required.add("EXECUTION_SEED_UNRESOLVED")
    if _session_isolation_errors(data, registry):
        required.add("SESSION_ISOLATION_UNPROVEN")
    if _ready_visibility_errors(data, registry) or _prompt_delivery_errors(
        data, repo_root, require_delivery_isolation=True
    ):
        required.add("BLINDED_WORKSPACE_UNRESOLVED")
    harness = data.get("harness") or {}
    if _ready_harness_errors(data, repo_root, registry):
        required.add("FRAMEWORK_NEUTRAL_HARNESS_UNRESOLVED")
    forced = harness.get("forced_500_trigger") or {}
    if (
        forced.get("status") != "verified"
        or forced.get("same_for_both_arms") is not True
        or forced.get("framework_neutral") is not True
        or _is_placeholder(forced.get("mechanism"))
        or not _evidence_paths_registered(forced.get("evidence"), registry, "forced_500_trigger")
    ):
        required.add("FORCED_500_TRIGGER_UNRESOLVED")
    metric = data.get("metric_operationalization") or {}
    first = metric.get("first_mutation_trace") or {}
    if (
        first.get("status") != "available"
        or _is_placeholder(first.get("mechanism"))
        or not _evidence_paths_registered(first.get("evidence"), registry, "first_mutation_trace")
    ):
        required.add("FIRST_MUTATION_TRACE_UNRESOLVED")
    canonical_rules, metric_problems = _canonical_metric_rules(repo_root)
    observed = {
        str(item.get("id", "")): item.get("rule")
        for item in metric.get("metrics") or []
        if isinstance(item, dict)
    }
    if metric.get("binding_status") != "bound" or metric_problems or observed != canonical_rules:
        required.add("METRIC_OPERATIONALIZATION_UNRESOLVED")
    order = data.get("execution_order") or {}
    if (
        order.get("binding_status") != "bound"
        or _is_placeholder(order.get("strategy"))
        or (
            order.get("strategy") == "deterministic_randomization"
            and _is_placeholder(order.get("randomization_procedure"))
        )
    ):
        required.add("EXECUTION_ORDER_UNRESOLVED")
    return required

def read_git_source_bytes(repo_root: Path, commit_sha, source_path):
    commit = str(commit_sha).strip()
    spath = str(source_path).strip()
    if not re.match(r"^[0-9a-f]{40}$", commit) or not spath:
        return None, "missing"
    try:
        chk = subprocess.run(
            ["git", "cat-file", "-e", f"{commit}^{{commit}}"],
            cwd=str(repo_root),
            capture_output=True,
            check=False,
        )
        if chk.returncode != 0:
            return None, "tool"
        blob = subprocess.run(
            ["git", "cat-file", "blob", f"{commit}:{spath}"],
            cwd=str(repo_root),
            capture_output=True,
            check=False,
        )
    except (OSError, ValueError):
        return None, "tool"
    if blob.returncode != 0:
        return None, "missing"
    return blob.stdout, None


def _load_ref(ref, repo_root: Path, *, must_exist: bool = True):
    resolved, code = resolve_repo_relative_path(ref, repo_root, must_exist=must_exist)
    if code is not None or resolved is None:
        return None, code
    if must_exist and not resolved.is_file():
        return None, "NOT_FILE"
    return resolved, None


def _read_component_text(path: Path):
    try:
        raw = path.read_bytes()
    except OSError as exc:
        return None, f"could not read ({exc})"
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return None, "is not valid UTF-8"
    if b"\r" in raw:
        return None, "contains CR; LF-only required"
    if not raw.endswith(b"\n"):
        return None, "missing final LF"
    return text[:-1], None


def _recompute_prompt_hash(arm: dict, repo_root: Path):
    parts = []
    for key in ("benchmark_ref", "shared_condition_ref", "overlay_ref"):
        resolved, code = _load_ref(str(arm.get(key, "")), repo_root)
        if code is not None or resolved is None:
            return None, f"{key} {display_source_path(str(arm.get(key, '')))} is not a safe existing file"
        text, problem = _read_component_text(resolved)
        if problem is not None:
            return None, f"{key} {problem}"
        parts.append(text)
    payload = "\n\n".join(parts) + "\n"
    return _sha256_bytes(payload.encode("utf-8")), None


def _actual_bundle_files(bundle_dir: Path) -> tuple[set[Path], list[str]]:
    problems = []
    actual = set()
    try:
        entries = sorted(bundle_dir.rglob("*"))
    except OSError as exc:
        return set(), [f"cannot walk bundle ({exc})"]
    for entry in entries:
        try:
            rel = entry.relative_to(bundle_dir).as_posix()
        except ValueError:
            rel = str(entry)
        if entry.is_symlink():
            problems.append(f"symlink not allowed in bundle: {rel}")
            continue
        if entry.is_dir():
            if entry.name in FORBIDDEN_EXECUTION_DIRS:
                problems.append(f"execution directory forbidden in readiness bundle: {rel}/")
            continue
        if not entry.is_file():
            problems.append(f"not a regular file: {rel}")
            continue
        if entry.name in FORBIDDEN_EXECUTION_FILES:
            problems.append(f"execution artifact forbidden in readiness bundle: {rel}")
            continue
        actual.add(entry.resolve())
    return actual, problems


def _expected_bundle_files(bundle_dir: Path) -> set[Path]:
    return {(bundle_dir / rel).resolve() for rel in EXPECTED_BUNDLE_FILENAMES}


def _check_chronology(data: dict, freeze: dict) -> list[str]:
    problems = []
    source = _parse_rfc3339(data.get("source_captured_at"))
    generated = _parse_rfc3339(data.get("generated_at"))
    frozen = _parse_rfc3339(data.get("readiness_frozen_at"))
    authorized = _parse_rfc3339(data.get("authorized_at")) if data.get("authorized_at") is not None else None
    for label, parsed in (("source_captured_at", source), ("generated_at", generated), ("readiness_frozen_at", frozen)):
        if parsed is None:
            problems.append(f"{label} is not a real RFC-3339 timestamp")
    if source and generated and source > generated:
        problems.append("source_captured_at must be <= generated_at")
    if generated and frozen and generated > frozen:
        problems.append("generated_at must be <= readiness_frozen_at")
    if source and frozen and source > frozen:
        problems.append("source_captured_at must be <= readiness_frozen_at")
    if data.get("authorized_at") is not None and authorized is None:
        problems.append("authorized_at is not a real RFC-3339 timestamp")
    if authorized and frozen and frozen > authorized:
        problems.append("readiness_frozen_at must be <= authorized_at")
    for key in ("source_captured_at", "readiness_frozen_at", "authorized_at"):
        if freeze.get(key) != data.get(key):
            problems.append(f"freeze.{key} must match execution-readiness.{key}")
    return problems


def _state_errors(data: dict, registry: dict[str, set[str]], repo_root: Path, path: Path) -> list[str]:
    problems = []
    state = data.get("state") or {}
    readiness = state.get("readiness_status")
    authorization = state.get("authorization_status")
    blockers = data.get("blockers") or []
    open_blocking = [
        b for b in blockers
        if isinstance(b, dict) and b.get("status") == "open" and b.get("severity") == "blocking"
    ]
    closed = [str(b.get("id", "")) for b in blockers if isinstance(b, dict) and b.get("status") == "closed"]
    if closed:
        problems.append("readiness blockers must not be listed as closed in this preflight bundle: " + ", ".join(closed))
    if authorization == "authorized" and readiness != "ready":
        problems.append("authorization_status=authorized requires readiness_status=ready")
    if authorization == "authorized" and data.get("authorized_at") is None:
        problems.append("authorization_status=authorized requires authorized_at")
    if state.get("run_004_execution_allowed") is True and authorization != "authorized":
        problems.append("run_004_execution_allowed=true requires authorization_status=authorized")
    if readiness == "blocked":
        if authorization != "not_authorized":
            problems.append("blocked readiness must be not_authorized")
        if state.get("run_004_execution_allowed") is not False:
            problems.append("blocked readiness must set run_004_execution_allowed=false")
        if state.get("runtime_values_bound") is not False:
            problems.append("blocked readiness must set runtime_values_bound=false")
        if data.get("authorized_at") is not None:
            problems.append("blocked readiness must not set authorized_at")
        if not open_blocking:
            problems.append("blocked readiness must list at least one open blocking blocker")
        observed_ids = {str(item.get("id", "")) for item in open_blocking}
        missing_blockers = _required_blocker_ids(data, registry, repo_root, path) - observed_ids
        if missing_blockers:
            problems.append("blocked readiness is missing derived blocker ids: " + ", ".join(sorted(missing_blockers)))
    if readiness == "ready":
        if authorization != "authorized":
            problems.append("ready readiness must be authorized in Run-004-v1")
        if state.get("run_004_execution_allowed") is not True:
            problems.append("ready readiness must set run_004_execution_allowed=true")
        if state.get("runtime_values_bound") is not True:
            problems.append("ready readiness must set runtime_values_bound=true")
        unexpected = [str(b.get("id", "")) for b in open_blocking if b.get("id") not in READY_ALLOWED_OPEN_BLOCKERS]
        if unexpected:
            problems.append("ready readiness must not list open blocking blockers: " + ", ".join(unexpected))
    for always_false in ("run_004_executed", "result_assessment_allowed", "comparison_ready"):
        if state.get(always_false) is not False:
            problems.append(f"{always_false} must remain false in this contract")
    if state.get("weak_condition_contrast_status") != "open":
        problems.append("weak_condition_contrast_status must remain open")
    missing_nonclaims = MANDATORY_NON_CLAIMS - {str(x) for x in (data.get("required_non_claims") or [])}
    if missing_nonclaims:
        problems.append("required_non_claims missing: " + ", ".join(sorted(missing_nonclaims)))
    return problems


def _ready_runtime_errors(data: dict, registry: dict[str, set[str]]) -> list[str]:
    runtime = data.get("runtime_binding") or {}
    problems = []
    if runtime.get("binding_status") != "bound":
        problems.append("runtime_binding.binding_status must be bound")
    kind_by_field = {
        "provider": "model_identity",
        "exact_model_id": "model_identity",
        "model_revision_or_version": "model_identity",
        "agent_program": "agent_identity",
        "agent_version": "agent_identity",
        "operating_mode": "agent_identity",
        "system_developer_context_identity": "agent_identity",
        "network_policy": "runtime_environment",
        "cache_policy": "runtime_environment",
        "dependency_resolution_strategy": "runtime_environment",
    }
    for field in READY_REQUIRED_RUNTIME_FIELDS:
        if not _binding_is_bound(runtime.get(field), registry, kind_by_field[field]):
            problems.append(f"runtime_binding.{field} must be bound to a non-placeholder value and registered evidence")
    if not runtime.get("available_tools") or _has_placeholder_item(runtime.get("available_tools")):
        problems.append("runtime_binding.available_tools must be non-empty and contain no placeholders")
    permissions = runtime.get("permissions") or {}
    for field in READY_REQUIRED_PERMISSION_FIELDS:
        if not _binding_is_bound(permissions.get(field), registry, "access_policy"):
            problems.append(f"runtime_binding.permissions.{field} must be bound")
    sampling = runtime.get("sampling") or {}
    unavailable = {str(item.get("id", "")) for item in sampling.get("unavailable_parameters") or [] if isinstance(item, dict)}
    for field in READY_REQUIRED_SAMPLING_FIELDS:
        if not _binding_is_sampling_ready(sampling.get(field), unavailable, field, registry):
            problems.append(f"runtime_binding.sampling.{field} must be bound or explicitly unavailable")
    environment = runtime.get("environment") or {}
    for field in READY_REQUIRED_ENV_FIELDS:
        if not _binding_is_bound(environment.get(field), registry, "runtime_environment"):
            problems.append(f"runtime_binding.environment.{field} must be bound")
    arms = runtime.get("arms") or {}
    profiles = [((arms.get(role) or {}).get("profile_id")) for role in ("control", "treatment")]
    if any(_is_placeholder(p) for p in profiles) or profiles[0] != profiles[1]:
        problems.append("control and treatment must share one concrete runtime profile")
    return problems


def _ready_workspace_errors(
    data: dict,
    registry: dict[str, set[str]],
    repo_root: Path,
    path: Path,
) -> list[str]:
    return _seed_binding_errors(data, repo_root, path) + _session_isolation_errors(data, registry)

def _ready_visibility_errors(data: dict, registry: dict[str, set[str]]) -> list[str]:
    vb = data.get("visibility_boundary") or {}
    problems = []
    if vb.get("boundary_status") != "verified":
        problems.append("visibility_boundary.boundary_status must be verified")
    if not _evidence_paths_registered(vb.get("evidence"), registry, "visibility_boundary"):
        problems.append("visibility_boundary.evidence must be hash-registered visibility_boundary evidence")
    for field in (
        "agent_sees_only_assigned_prompt",
        "other_overlay_hidden",
        "arm_labels_hidden",
        "hypothesis_hidden",
        "other_arm_artifacts_hidden",
        "path_names_role_neutral",
        "repo_metadata_reconstruction_prevented",
    ):
        if vb.get(field) is not True:
            problems.append(f"visibility_boundary.{field} must be true")
    if vb.get("normal_repo_read_access_can_reconstruct_experiment") is not False:
        problems.append("normal repo read access must not reconstruct experiment metadata")
    return problems


def _ready_harness_errors(data: dict, repo_root: Path, registry: dict[str, set[str]]) -> list[str]:
    h = data.get("harness") or {}
    problems = []
    if h.get("binding_status") != "bound":
        problems.append("harness.binding_status must be bound")
    for field in ("harness_id", "harness_version", "install_command", "start_command", "health_ready_signal", "test_command", "port_strategy", "process_termination", "cleanup"):
        if _is_placeholder(h.get(field)):
            problems.append(f"harness.{field} must be bound")
    timeouts = h.get("timeouts") or {}
    for field in ("start_seconds", "test_seconds", "total_seconds"):
        if not isinstance(timeouts.get(field), int):
            problems.append(f"harness.timeouts.{field} must be bound")
    if all(isinstance(timeouts.get(field), int) for field in ("start_seconds", "test_seconds", "total_seconds")):
        if timeouts["total_seconds"] < timeouts["start_seconds"] + timeouts["test_seconds"]:
            problems.append("harness.timeouts.total_seconds must cover start_seconds + test_seconds")
    if h.get("identical_surface_for_both_arms") is not True:
        problems.append("harness.identical_surface_for_both_arms must be true")
    hashes = h.get("file_hashes") or []
    if not hashes:
        problems.append("harness.file_hashes must be non-empty")
    for entry in hashes:
        if not isinstance(entry, dict):
            continue
        resolved, code = _load_ref(str(entry.get("path", "")), repo_root)
        if code is not None or resolved is None:
            problems.append(f"harness file hash path is not safe/existing: {display_source_path(str(entry.get('path', '')))}")
            continue
        declared = str(entry.get("sha256", "")).strip()
        if _sha256_of(resolved) != declared:
            problems.append(f"harness file hash mismatch: {display_source_path(str(entry.get('path', '')))}")
        if not _evidence_paths_registered([str(entry.get("path", ""))], registry, "harness"):
            problems.append(f"harness file is not registered as harness evidence: {display_source_path(str(entry.get('path', '')))}")
    fn = h.get("framework_neutrality") or {}
    if not (fn.get("status") == "verified" and fn.get("fastify_specific_imports_absent") is True and fn.get("express_fastify_neutral") is True):
        problems.append("harness framework neutrality must be verified for Express and Fastify")
    if not _evidence_paths_registered(fn.get("evidence"), registry, "harness_neutrality"):
        problems.append("harness framework neutrality requires hash-registered evidence")
    forced = h.get("forced_500_trigger") or {}
    if not (forced.get("status") == "verified" and forced.get("same_for_both_arms") is True and forced.get("framework_neutral") is True and not _is_placeholder(forced.get("mechanism"))):
        problems.append("forced_500_trigger must be a verified identical framework-neutral mechanism")
    if not _evidence_paths_registered(forced.get("evidence"), registry, "forced_500_trigger"):
        problems.append("forced_500_trigger requires hash-registered evidence")
    return problems


def _ready_misc_errors(
    data: dict,
    registry: dict[str, set[str]],
    repo_root: Path,
) -> list[str]:
    problems = []
    human = data.get("human_intervention") or {}
    for field in ("policy", "count_rule", "agent_question_handling"):
        if _is_placeholder(human.get(field)):
            problems.append(f"human_intervention.{field} must be bound")
    if not human.get("standard_response_texts") or _has_placeholder_item(human.get("standard_response_texts")):
        problems.append("human_intervention.standard_response_texts must be bound")
    if not human.get("abort_conditions") or _has_placeholder_item(human.get("abort_conditions")):
        problems.append("human_intervention.abort_conditions must be bound")
    if human.get("same_policy_across_arms") is not True:
        problems.append("human_intervention.same_policy_across_arms must be true")
    retry = data.get("retry_policy") or {}
    if retry.get("silent_or_one_sided_retries_forbidden") is not True:
        problems.append("retry_policy.silent_or_one_sided_retries_forbidden must be true")
    if retry.get("max_retries", 0) > 0:
        if retry.get("both_arms_restart_after_retry") is not True:
            problems.append("any retry policy must restart both arms symmetrically")
        if not retry.get("allowed_retry_reasons") or _has_placeholder_item(retry.get("allowed_retry_reasons")):
            problems.append("retry_policy.allowed_retry_reasons must be bound when retries are allowed")
    for field in (
        "partial_workspace_behavior",
        "agent_abort_behavior",
        "install_failure_behavior",
        "timeout_behavior",
        "flaky_test_behavior",
    ):
        if _is_placeholder(retry.get(field)):
            problems.append(f"retry_policy.{field} must be bound")
    order = data.get("execution_order") or {}
    if order.get("binding_status") != "bound" or _is_placeholder(order.get("strategy")):
        problems.append("execution_order must be bound before authorization")
    if order.get("strategy") == "deterministic_randomization" and _is_placeholder(order.get("randomization_procedure")):
        problems.append("execution_order.randomization_procedure must be bound for deterministic_randomization")
    metric = data.get("metric_operationalization") or {}
    if metric.get("binding_status") != "bound":
        problems.append("metric_operationalization.binding_status must be bound")
    canonical_rules, canonical_problems = _canonical_metric_rules(repo_root)
    problems.extend(canonical_problems)
    observed = {}
    for item in metric.get("metrics") or []:
        if not isinstance(item, dict):
            continue
        metric_id = str(item.get("id", ""))
        if metric_id in observed:
            problems.append(f"metric_operationalization contains duplicate id: {metric_id}")
        observed[metric_id] = item.get("rule")
    missing = set(canonical_rules) - set(observed)
    extra = set(observed) - set(canonical_rules)
    if missing:
        problems.append("metric_operationalization.metrics missing canonical ids: " + ", ".join(sorted(missing)))
    if extra:
        problems.append("metric_operationalization.metrics contains non-canonical ids: " + ", ".join(sorted(extra)))
    for metric_id in sorted(set(canonical_rules) & set(observed)):
        if observed[metric_id] != canonical_rules[metric_id]:
            problems.append(f"metric_operationalization.metrics.{metric_id} rule differs from the frozen protocol")
    first = metric.get("first_mutation_trace") or {}
    if first.get("status") != "available":
        problems.append("first_mutation_trace must be available before authorization")
    if _is_placeholder(first.get("mechanism")):
        problems.append("first_mutation_trace.mechanism must be bound before authorization")
    if not _evidence_paths_registered(first.get("evidence"), registry, "first_mutation_trace"):
        problems.append("first_mutation_trace requires hash-registered evidence")
    if first.get("agent_report_alone_sufficient") is not False:
        problems.append("agent report alone must not be sufficient for first mutation trace")
    return problems


def _prompt_delivery_errors(data: dict, repo_root: Path, *, require_delivery_isolation: bool) -> list[str]:
    problems = []
    pd = data.get("prompt_delivery") or {}
    if require_delivery_isolation and pd.get("binding_status") != "bound":
        problems.append("prompt_delivery.binding_status must be bound when ready")
    design = None
    design_ref = ((data.get("provenance") or {}).get("condition_design_snapshot_ref"))
    design_resolved, code = _load_ref(str(design_ref), repo_root)
    if code is None and design_resolved is not None:
        try:
            design = load_yaml(design_resolved)
        except (FileNotFoundError, ValueError):
            design = None
    design_assembly = (design or {}).get("condition_input_assembly") or {}
    design_components = design_assembly.get("components") or {}
    design_arms = design_assembly.get("arms") or {}
    for role in ("control", "treatment"):
        arm = (pd.get("arms") or {}).get(role) or {}
        expected_hash, problem = _recompute_prompt_hash(arm, repo_root)
        if problem is not None:
            problems.append(f"prompt_delivery.{role}: {problem}")
            continue
        if expected_hash != arm.get("payload_sha256"):
            problems.append(f"prompt_delivery.{role}.payload_sha256 mismatch")
        if require_delivery_isolation and arm.get("only_assigned_payload_delivered") is not True:
            problems.append(f"prompt_delivery.{role}.only_assigned_payload_delivered must be true when ready")
        if design is not None:
            if arm.get("benchmark_ref") != ((design_components.get("benchmark") or {}).get("ref")):
                problems.append(f"prompt_delivery.{role}.benchmark_ref must match frozen design")
            if arm.get("shared_condition_ref") != ((design_components.get("shared_condition") or {}).get("ref")):
                problems.append(f"prompt_delivery.{role}.shared_condition_ref must match frozen design")
            if arm.get("overlay_ref") != ((design_arms.get(role) or {}).get("overlay_ref")):
                problems.append(f"prompt_delivery.{role}.overlay_ref must match frozen design")
    return problems


def _provenance_errors(data: dict, repo_root: Path) -> list[str]:
    problems = []
    p = data.get("provenance") or {}
    expected = {
        "condition_design_ref": DESIGN_CONDITION_PATH,
        "design_freeze_manifest_ref": DESIGN_FREEZE_PATH,
    }
    for key, expected_path in expected.items():
        if p.get(key) != expected_path:
            problems.append(f"provenance.{key} must be {expected_path!r}")
    for key, hash_key in (
        ("condition_design_ref", "condition_design_sha256"),
        ("design_freeze_manifest_ref", "design_freeze_manifest_sha256"),
        ("condition_design_snapshot_ref", "condition_design_sha256"),
        ("design_freeze_manifest_snapshot_ref", "design_freeze_manifest_sha256"),
    ):
        resolved, code = _load_ref(str(p.get(key, "")), repo_root)
        if code is not None or resolved is None:
            problems.append(f"provenance.{key} is not a safe existing file")
            continue
        if _sha256_of(resolved) != p.get(hash_key):
            problems.append(f"provenance.{key} sha256 mismatch against {hash_key}")
    design_commit = str(p.get("design_source_commit_sha", ""))
    for key, source_path in (
        ("condition_design_snapshot_ref", DESIGN_CONDITION_PATH),
        ("design_freeze_manifest_snapshot_ref", DESIGN_FREEZE_PATH),
    ):
        resolved, code = _load_ref(str(p.get(key, "")), repo_root)
        if code is not None or resolved is None:
            continue
        git_bytes, gprob = read_git_source_bytes(repo_root, design_commit, source_path)
        if gprob == "tool":
            raise ToolError(
                f"cannot verify design source provenance at commit {design_commit[:12]}; "
                "the validate job needs full history"
            )
        if gprob == "missing":
            problems.append(f"{source_path} does not exist at design_source_commit_sha {design_commit[:12]}")
        elif git_bytes != resolved.read_bytes():
            problems.append(f"{key} differs from git {design_commit[:12]}:{source_path}")
    def _load_snapshot_yaml(ref_key: str):
        resolved, code = _load_ref(str(p.get(ref_key, "")), repo_root)
        if code is not None or resolved is None:
            return None
        try:
            return load_yaml(resolved)
        except (FileNotFoundError, ValueError) as exc:
            raise ToolError(f"snapshot for {ref_key} is invalid or unreadable: {exc}") from exc

    design = _load_snapshot_yaml("condition_design_snapshot_ref")
    design_freeze = _load_snapshot_yaml("design_freeze_manifest_snapshot_ref")
    if design is not None:
        if design.get("artifact_type") != DESIGN_ARTIFACT_TYPE:
            problems.append("condition design snapshot artifact_type mismatch")
        if design.get("design_status") != "frozen":
            problems.append("condition design snapshot must remain frozen")
        if design.get("runtime_values_bound") is not False:
            problems.append("condition design snapshot must have runtime_values_bound=false")
        if design.get("run_004_execution_allowed") is not False:
            problems.append("condition design snapshot must have run_004_execution_allowed=false")
    if design_freeze is not None:
        coverage = p.get("design_freeze_hash_coverage") or {}
        if design_freeze.get("artifact_type") != DESIGN_FREEZE_ARTIFACT_TYPE:
            problems.append("design freeze manifest snapshot artifact_type mismatch")
        design_frozen = _parse_rfc3339(design_freeze.get("frozen_at"))
        source_captured = _parse_rfc3339(data.get("source_captured_at"))
        if design_frozen is None:
            problems.append("design freeze manifest snapshot frozen_at is not a real RFC-3339 timestamp")
        elif source_captured is not None and design_frozen > source_captured:
            problems.append("design freeze frozen_at must be <= readiness source_captured_at")
        if design_freeze.get("source_base_commit_sha") != p.get("design_input_source_base_commit_sha"):
            problems.append("design_input_source_base_commit_sha must match design freeze source_base_commit_sha")
        entries = design_freeze.get("hashes") or []
        if coverage.get("expected_hashed_file_count") != len(entries) or len(entries) != DESIGN_EXPECTED_HASH_COUNT:
            problems.append("design freeze hash count does not match expected Run-004 design bundle coverage")
        seen = set()
        design_bundle = (repo_root / DESIGN_BUNDLE_DIR).resolve()
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            raw = str(entry.get("path", ""))
            if raw in seen:
                problems.append(f"duplicate path in design freeze hashes: {display_source_path(raw)}")
            seen.add(raw)
            if raw == DESIGN_FREEZE_PATH:
                problems.append("design freeze manifest must not hash itself")
            resolved, code = _load_ref(raw, repo_root)
            if code is not None or resolved is None:
                problems.append(f"design freeze hash path not safe/existing: {display_source_path(raw)}")
                continue
            if not _inside(resolved, design_bundle):
                problems.append(f"design freeze hash path outside design bundle: {display_source_path(raw)}")
                continue
            if _sha256_of(resolved) != str(entry.get("sha256", "")):
                problems.append(f"design freeze hash mismatch for {display_source_path(raw)}")
        if coverage.get("manifest_excludes_itself") is not True:
            problems.append("design_freeze_hash_coverage.manifest_excludes_itself must be true")
        if coverage.get("hashes_all_declared_design_bundle_files") is not True:
            problems.append("design_freeze_hash_coverage.hashes_all_declared_design_bundle_files must be true")
    return problems


def _freeze_errors(data: dict, freeze: dict, path: Path, repo_root: Path) -> list[str]:
    problems = []
    bundle_dir = path.resolve().parent
    for key in ("artifact_type", "contract_version", "readiness_bundle_id", "series_id", "design_id", "challenge_version"):
        expected = RUN_004_FREEZE_ARTIFACT_TYPE if key == "artifact_type" else data.get(key)
        if key == "contract_version":
            expected = RUN_004_CONTRACT_VERSION
        if freeze.get(key) != expected:
            problems.append(f"freeze.{key} must match expected value {expected!r}")
    for key in ("source_design_commit_sha", "design_input_source_base_commit_sha"):
        expected = (data.get("provenance") or {}).get("design_source_commit_sha" if key == "source_design_commit_sha" else key)
        if freeze.get(key) != expected:
            problems.append(f"freeze.{key} must match provenance")
    problems += _check_chronology(data, freeze)
    actual, actual_problems = _actual_bundle_files(bundle_dir)
    problems += actual_problems
    expected = _expected_bundle_files(bundle_dir)
    for extra in sorted(actual - expected):
        problems.append(f"unexpected file in closed readiness bundle: {extra.relative_to(bundle_dir).as_posix()}")
    for missing in sorted(expected - actual):
        problems.append(f"expected file missing from readiness bundle: {missing.relative_to(bundle_dir).as_posix()}")
    manifest_resolved, code = _load_ref(str((data.get("freeze") or {}).get("freeze_manifest_ref", "")), repo_root)
    if code is not None or manifest_resolved is None or manifest_resolved != (bundle_dir / "freeze-manifest.yml").resolve():
        problems.append("freeze.freeze_manifest_ref must point to the bundle freeze-manifest.yml")
    entries = freeze.get("hashes") or []
    if _bundle_content_hash(entries) != freeze.get("readiness_bundle_content_sha256"):
        problems.append("readiness_bundle_content_sha256 does not match the declared hash entries")
    declared_paths = []
    declared_resolved = set()
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        raw = str(entry.get("path", ""))
        declared_paths.append(raw)
        resolved, rcode = _load_ref(raw, repo_root)
        if rcode is not None or resolved is None:
            problems.append(f"freeze hash path is not safe/existing: {display_source_path(raw)}")
            continue
        if not _inside(resolved, bundle_dir):
            problems.append(f"freeze hash path outside readiness bundle: {display_source_path(raw)}")
            continue
        if resolved == manifest_resolved:
            problems.append("readiness freeze manifest must not hash itself")
        declared_resolved.add(resolved)
        declared = str(entry.get("sha256", ""))
        if not SHA256_RE.match(declared):
            problems.append(f"malformed sha256 for {display_source_path(raw)}")
        elif _sha256_of(resolved) != declared:
            problems.append(f"sha256 mismatch for {display_source_path(raw)}")
    duplicate_paths = sorted({p for p in declared_paths if declared_paths.count(p) > 1})
    for dup in duplicate_paths:
        problems.append(f"duplicate freeze hash path: {display_source_path(dup)}")
    expected_hashed = expected - ({manifest_resolved} if manifest_resolved else set())
    for missing in sorted(expected_hashed - declared_resolved):
        problems.append(f"expected file not covered by readiness freeze: {missing.relative_to(bundle_dir).as_posix()}")
    for extra in sorted(declared_resolved - expected_hashed):
        problems.append(f"readiness freeze hashes outside expected set: {extra.relative_to(bundle_dir).as_posix() if _inside(extra, bundle_dir) else display_path(extra)}")
    if data.get("state", {}).get("authorization_status") == "authorized":
        ws = data.get("workspace_session_isolation", {}).get("arms", {})
        seed_hashes = {((ws.get(role) or {}).get("seed_hash")) for role in ("control", "treatment")}
        if len(seed_hashes) != 1 or freeze.get("future_execution_seed_status") != "bound" or freeze.get("future_execution_seed_sha256") not in seed_hashes:
            problems.append("authorized readiness must bind future_execution_seed_sha256 to the shared arm seed hash")
    else:
        if freeze.get("future_execution_seed_status") != "unresolved" or freeze.get("future_execution_seed_sha256") is not None:
            problems.append("not_authorized readiness must keep the future execution seed unresolved")
    return problems


def semantic_errors(data: dict, path: Path, repo_root: Path) -> list[str]:
    errors = []
    if data.get("series_id") != RUN_004_SERIES_ID:
        errors.append(format_error("EXECUTION_READINESS_REQUIRES_RUN004_IDENTITY", path, "series_id is not the Run-004 series"))
    if data.get("design_id") != RUN_004_DESIGN_ID:
        errors.append(format_error("EXECUTION_READINESS_REQUIRES_RUN004_IDENTITY", path, "design_id is not the Run-004 design"))
    if data.get("challenge_version") != RUN_004_CHALLENGE_VERSION:
        errors.append(format_error("EXECUTION_READINESS_REQUIRES_RUN004_IDENTITY", path, "challenge_version is not rest-api-v1"))
    if data.get("artifact_type") != RUN_004_ARTIFACT_TYPE or data.get("contract_version") != RUN_004_CONTRACT_VERSION:
        errors.append(format_error("EXECUTION_READINESS_REQUIRES_RUN004_IDENTITY", path, "artifact type or contract version mismatch"))
    self_ref = str(data.get("bundle_artifact_path", ""))
    self_resolved, code = _load_ref(self_ref, repo_root)
    if code is not None or self_resolved is None or self_resolved != path.resolve():
        errors.append(format_error("EXECUTION_READINESS_REQUIRES_SELF_IDENTITY", path, "bundle_artifact_path must resolve to the validated file"))
    freeze_ref = str((data.get("freeze") or {}).get("freeze_manifest_ref", ""))
    freeze_resolved, fcode = _load_ref(freeze_ref, repo_root)
    freeze = None
    if fcode is not None or freeze_resolved is None:
        errors.append(format_error("EXECUTION_READINESS_REQUIRES_FREEZE", path, "freeze manifest is missing or unsafe"))
    else:
        try:
            freeze = load_yaml(freeze_resolved)
        except (FileNotFoundError, ValueError) as exc:
            return [format_error("EXECUTION_READINESS_REQUIRES_FREEZE", path, str(exc))]
        freeze_schema_errs = schema_errors(load_validator(FREEZE_SCHEMA_PATH), freeze, freeze_resolved, label="child=freeze")
        if freeze_schema_errs:
            return freeze_schema_errs
    registry, registry_problems = _evidence_registry(data, path, repo_root)
    if registry_problems:
        errors.append(format_error("EXECUTION_READINESS_REQUIRES_EVIDENCE_REGISTRY", path, "; ".join(registry_problems)))
    general_evidence_problems = _general_evidence_errors(data, repo_root)
    if general_evidence_problems:
        errors.append(format_error("EXECUTION_READINESS_REQUIRES_EVIDENCE_PATHS", path, "; ".join(general_evidence_problems)))
    state_problems = _state_errors(data, registry, repo_root, path)
    if state_problems:
        errors.append(format_error("EXECUTION_READINESS_REQUIRES_STATE_MODEL", path, "; ".join(state_problems)))
    try:
        provenance_problems = _provenance_errors(data, repo_root)
    except ToolError as exc:
        raise exc
    if provenance_problems:
        errors.append(format_error("EXECUTION_READINESS_REQUIRES_DESIGN_PROVENANCE", path, "; ".join(provenance_problems)))
    prompt_problems = _prompt_delivery_errors(
        data,
        repo_root,
        require_delivery_isolation=(data.get("state", {}).get("readiness_status") == "ready"),
    )
    if prompt_problems:
        errors.append(format_error("EXECUTION_READINESS_REQUIRES_PROMPT_DELIVERY", path, "; ".join(prompt_problems)))
    if freeze is not None:
        freeze_problems = _freeze_errors(data, freeze, path, repo_root)
        if freeze_problems:
            errors.append(format_error("EXECUTION_READINESS_REQUIRES_VALID_FREEZE", path, "; ".join(freeze_problems)))
    if data.get("state", {}).get("readiness_status") == "ready":
        ready_problems = []
        ready_problems += _ready_runtime_errors(data, registry)
        ready_problems += _ready_workspace_errors(data, registry, repo_root, path)
        ready_problems += _ready_visibility_errors(data, registry)
        ready_problems += _ready_harness_errors(data, repo_root, registry)
        ready_problems += _ready_misc_errors(data, registry, repo_root)
        if ready_problems:
            errors.append(format_error("EXECUTION_READINESS_REQUIRES_FULL_READY_BINDING", path, "; ".join(ready_problems)))
    return errors


def validate_file(path: Path, validator: Draft202012Validator, repo_root: Path | None = None):
    root = repo_root if repo_root is not None else REPO_ROOT
    try:
        data = load_yaml(path)
    except (FileNotFoundError, ValueError) as exc:
        return 2, [f"ERROR path={display_path(path)}: {exc}"]
    errs = schema_errors(validator, data, path)
    if errs:
        return 2, errs
    try:
        sem = semantic_errors(data, path, root)
    except ToolError as exc:
        return 2, [f"ERROR rule=EXECUTION_READINESS_REQUIRES_GIT_SOURCE_PROVENANCE path={display_path(path)}: {exc}"]
    if sem:
        return 1, sem
    return 0, []


def discover_run_004_v1_artifacts(repo_root: Path):
    experiments = repo_root / "experiments"
    if not experiments.is_dir():
        return []
    return sorted(experiments.glob(RUN_004_DISCOVERY_GLOB), key=lambda p: p.as_posix())


def main(argv=None, *, repo_root: Path | None = None):
    root = repo_root if repo_root is not None else REPO_ROOT
    parser = argparse.ArgumentParser(
        description="Validate Run-004-v1 model-lab execution-readiness preflight bundles."
    )
    parser.add_argument("paths", nargs="*")
    args = parser.parse_args(argv)
    try:
        validator = load_validator(SCHEMA_PATH)
        load_validator(FREEZE_SCHEMA_PATH)
        load_validator(EVIDENCE_SCHEMA_PATH)
        load_validator(SEED_SCHEMA_PATH)
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        return 2
    if args.paths:
        paths = [Path(raw) if Path(raw).is_absolute() else (root / raw) for raw in args.paths]
    else:
        paths = discover_run_004_v1_artifacts(root)
        if not paths:
            print(
                "ERROR: no Run-004 v1 model-lab-execution-readiness candidate found; "
                "empty discovery is a failure, not a skip."
            )
            return 2
    highest, passed = 0, 0
    for candidate in paths:
        code, errs = validate_file(candidate, validator, root)
        highest = max(highest, code)
        for err in errs:
            print(err)
        if code == 0:
            passed += 1
            print(f"✅ {display_path(candidate)}")
    print(
        "Run-004 v1 model-lab-execution-readiness artifacts: "
        f"checked={len(paths)}, passed={passed}, failed={len(paths) - passed}"
    )
    return highest


if __name__ == "__main__":
    sys.exit(main())
