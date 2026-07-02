#!/usr/bin/env python3
"""Validate Run-004 runtime-candidate preflight bundles.

This validator is deterministic and offline. It validates schemas, content
hashes, path containment, symlink safety, and blocker semantics. It does not
start Ollama, connect to localhost, call a model, or execute a subprocess.

Exit codes: 0 valid, 1 semantic violation, 2 schema/parse/tool error.
"""

from __future__ import annotations

import argparse
import datetime as _dt
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
        "ERROR: Missing dependencies for model-lab-runtime-candidate validation "
        "(need PyYAML, jsonschema).",
        file=sys.stderr,
    )
    raise SystemExit(2) from exc


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCHEMA_DIR = REPO_ROOT / "schemas"
CANDIDATE_SCHEMA_PATH = SCHEMA_DIR / "model-lab-runtime-candidate.v1.schema.json"
FREEZE_SCHEMA_PATH = SCHEMA_DIR / "model-lab-runtime-candidate-freeze-manifest.v1.schema.json"
EVIDENCE_SCHEMA_PATH = SCHEMA_DIR / "model-lab-execution-readiness-evidence.v1.schema.json"

RUN_004_SERIES_ID = "2026-05-31_model-lab-replication-series"
RUN_004_DESIGN_ID = "run-004-condition-contrast"
RUN_004_CHALLENGE_VERSION = "rest-api-v1"
RUN_004_ARTIFACT_TYPE = "model_lab_runtime_candidate"
RUN_004_CONTRACT_VERSION = "run-004-runtime-candidate.v1"
RUN_004_FREEZE_ARTIFACT_TYPE = "model_lab_runtime_candidate_freeze_manifest"
RUN_004_FREEZE_CONTRACT_VERSION = "run-004-runtime-candidate-freeze.v1"
RUN_004_DISCOVERY_GLOB = "*/artifacts/*/runtime-candidate.yml"

CONDITION_DESIGN_REF = (
    "experiments/2026-05-31_model-lab-replication-series/artifacts/"
    "run-004-condition-contrast-design/condition-design.yml"
)
ACCESS_POLICY_REF = (
    "experiments/2026-05-31_model-lab-replication-series/artifacts/"
    "run-004-access-policy/access-policy.yml"
)
EXPECTED_BUNDLE_FILES = frozenset(
    {
        "runtime-candidate.yml",
        "model-identity-evidence.yml",
        "runtime-environment-evidence.yml",
        "freeze-manifest.yml",
    }
)
EXPECTED_HASHED_FILES = EXPECTED_BUNDLE_FILES - {"freeze-manifest.yml"}
REQUIRED_BLOCKERS = frozenset(
    {
        "AGENT_TOOL_BROKER_UNRESOLVED",
        "AGENT_BINDING_UNRESOLVED",
        "SAMPLING_BINDING_UNRESOLVED",
    }
)
MANDATORY_NON_CLAIMS = frozenset(
    {
        "run_004_executed",
        "run_004_execution_allowed",
        "run_004_model_process_started",
        "run_004_agent_process_started",
        "broker_ready",
        "model_accessible_through_bound_sandbox",
        "codex_bound_for_run004",
        "agent_bound",
        "sampling_bound",
        "result_assessment_allowed",
        "comparison_ready",
        "model_quality",
        "comparative_superiority",
        "condition_effect",
        "outcome_upgrade",
        "adoption_readiness",
        "promotion_readiness",
        "production_readiness",
        "security_readiness",
    }
)
EVIDENCE_KINDS = frozenset({"model_identity", "runtime_environment"})
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
DRIVE_LETTER_RE = re.compile(r"^[A-Za-z]:")
_SCHEMA_CACHE: dict[Path, Draft202012Validator] = {}


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
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


def _has_symlink_component(path: Path, root: Path) -> bool:
    try:
        rel_parts = path.relative_to(root).parts
    except ValueError:
        return True
    current = root
    for part in rel_parts:
        current = current / part
        if current.is_symlink():
            return True
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
    if must_exist and (not resolved.exists() or _has_symlink_component(resolved, root)):
        return None, "SYMLINK_OR_NOT_FOUND"
    return resolved, None


def _safe_repo_file(raw: str, repo_root: Path):
    resolved, code = resolve_repo_relative_path(raw, repo_root, must_exist=True)
    if code is not None or resolved is None or not resolved.is_file():
        return None, code or "NOT_FILE"
    return resolved, None


def load_validator(schema_path: Path) -> Draft202012Validator:
    if schema_path in _SCHEMA_CACHE:
        return _SCHEMA_CACHE[schema_path]
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
    _SCHEMA_CACHE[schema_path] = validator
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


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _bundle_hash(entries: list[dict]) -> str:
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


def _is_fixture_candidate(path: Path, repo_root: Path) -> bool:
    try:
        rel = path.resolve().relative_to(repo_root.resolve()).as_posix()
    except (OSError, RuntimeError, ValueError, UnicodeError):
        return False
    return rel.startswith("tests/fixtures/model_lab_runtime_candidate/")


def _validate_provenance(data: dict, path: Path, repo_root: Path) -> list[str]:
    problems = []
    provenance = data.get("provenance") or {}
    expected = {
        "condition_design_ref": CONDITION_DESIGN_REF,
        "access_policy_ref": ACCESS_POLICY_REF,
    }
    for ref_key, expected_ref in expected.items():
        if provenance.get(ref_key) != expected_ref:
            problems.append(f"provenance.{ref_key} must be {expected_ref!r}")
    for ref_key, hash_key in (
        ("condition_design_ref", "condition_design_sha256"),
        ("access_policy_ref", "access_policy_sha256"),
    ):
        resolved, code = _safe_repo_file(str(provenance.get(ref_key, "")), repo_root)
        if code is not None or resolved is None:
            problems.append(f"provenance.{ref_key} is not a safe existing regular file")
            continue
        if _sha256(resolved) != provenance.get(hash_key):
            problems.append(f"provenance.{hash_key} mismatch")
    return problems


def _validate_evidence_registry(data: dict, path: Path, repo_root: Path) -> tuple[dict[str, set[str]], list[str]]:
    problems = []
    registry: dict[str, set[str]] = {}
    fixture_candidate = _is_fixture_candidate(path, repo_root)
    evidence_validator = load_validator(EVIDENCE_SCHEMA_PATH)
    for entry in data.get("evidence_registry") or []:
        if not isinstance(entry, dict):
            continue
        raw = str(entry.get("path", ""))
        if raw in registry:
            problems.append(f"duplicate evidence_registry path: {display_source_path(raw)}")
            continue
        resolved, code = _safe_repo_file(raw, repo_root)
        if code is not None or resolved is None:
            problems.append(f"evidence_registry path is not safe existing regular file: {display_source_path(raw)}")
            continue
        try:
            rel = resolved.relative_to(repo_root.resolve()).as_posix()
        except ValueError:
            rel = raw
        if not fixture_candidate and rel.startswith("tests/fixtures/"):
            problems.append(f"fixture evidence is forbidden for a real runtime candidate: {display_source_path(raw)}")
        declared_hash = str(entry.get("sha256", ""))
        if _sha256(resolved) != declared_hash:
            problems.append(f"evidence_registry sha256 mismatch: {display_source_path(raw)}")
        kinds = {str(kind) for kind in (entry.get("kinds") or [])}
        unsupported = kinds - EVIDENCE_KINDS
        if unsupported:
            problems.append(f"unsupported evidence kinds for {display_source_path(raw)}: " + ", ".join(sorted(unsupported)))
        try:
            document = load_yaml(resolved)
        except (FileNotFoundError, ValueError) as exc:
            problems.append(f"evidence document invalid or unreadable: {display_source_path(raw)}: {exc}")
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
        if document.get("synthetic_fixture") is True and not fixture_candidate:
            problems.append("synthetic_fixture evidence is forbidden outside runtime-candidate fixtures")
        claim_kinds = [
            str(claim.get("kind", ""))
            for claim in (document.get("claims") or [])
            if isinstance(claim, dict)
        ]
        if len(claim_kinds) != 1:
            problems.append(f"runtime candidate evidence must bind exactly one claim kind: {display_source_path(raw)}")
        if set(claim_kinds) != kinds:
            problems.append(f"evidence claim kinds must match registry for {display_source_path(raw)}")
        registry[raw] = kinds
    return registry, problems


def _validate_evidence_paths(data: dict, repo_root: Path) -> list[str]:
    problems = []
    refs = []
    refs.extend(item.get("path") for item in (data.get("evidence") or []) if isinstance(item, dict))
    for blocker in data.get("blockers") or []:
        if isinstance(blocker, dict):
            refs.extend(blocker.get("evidence") or [])
    for raw in refs:
        resolved, code = _safe_repo_file(str(raw), repo_root)
        if code is not None or resolved is None:
            problems.append(f"declared evidence path is not safe existing regular file: {display_source_path(str(raw))}")
    return problems


def _actual_bundle_files(bundle_dir: Path) -> tuple[set[str], list[str]]:
    problems = []
    actual: set[str] = set()
    try:
        entries = sorted(bundle_dir.rglob("*"))
    except OSError as exc:
        return set(), [f"cannot walk runtime-candidate bundle ({exc})"]
    for entry in entries:
        try:
            rel = entry.relative_to(bundle_dir).as_posix()
        except ValueError:
            rel = str(entry)
        if entry.is_symlink():
            problems.append(f"symlink not allowed in runtime-candidate bundle: {rel}")
            continue
        if entry.is_dir():
            continue
        if not entry.is_file():
            problems.append(f"not a regular file in runtime-candidate bundle: {rel}")
            continue
        actual.add(rel)
    return actual, problems


def _validate_freeze(data: dict, freeze: dict, path: Path, freeze_path: Path, repo_root: Path) -> list[str]:
    problems = []
    bundle_dir = path.resolve().parent
    for key, expected in (
        ("artifact_type", RUN_004_FREEZE_ARTIFACT_TYPE),
        ("contract_version", RUN_004_FREEZE_CONTRACT_VERSION),
        ("candidate_id", data.get("candidate_id")),
        ("series_id", RUN_004_SERIES_ID),
        ("design_id", RUN_004_DESIGN_ID),
        ("challenge_version", RUN_004_CHALLENGE_VERSION),
    ):
        if freeze.get(key) != expected:
            problems.append(f"freeze.{key} must be {expected!r}")
    if freeze.get("manifest_excludes_itself") is not True:
        problems.append("freeze.manifest_excludes_itself must be true")
    generated = _parse_rfc3339(data.get("generated_at"))
    frozen = _parse_rfc3339(freeze.get("frozen_at"))
    if generated is None:
        problems.append("runtime-candidate.generated_at is not a real RFC-3339 timestamp")
    if frozen is None:
        problems.append("freeze.frozen_at is not a real RFC-3339 timestamp")
    if generated is not None and frozen is not None and generated > frozen:
        problems.append("runtime-candidate.generated_at must be <= freeze.frozen_at")
    actual, actual_problems = _actual_bundle_files(bundle_dir)
    problems.extend(actual_problems)
    extra = actual - EXPECTED_BUNDLE_FILES
    missing = EXPECTED_BUNDLE_FILES - actual
    if extra:
        problems.append("unexpected file in closed runtime-candidate bundle: " + ", ".join(sorted(extra)))
    if missing:
        problems.append("expected file missing from runtime-candidate bundle: " + ", ".join(sorted(missing)))
    freeze_ref = str((data.get("freeze") or {}).get("freeze_manifest_ref", ""))
    resolved_freeze, code = _safe_repo_file(freeze_ref, repo_root)
    if code is not None or resolved_freeze is None or resolved_freeze != freeze_path.resolve():
        problems.append("freeze.freeze_manifest_ref must point to this bundle freeze-manifest.yml")
    entries = freeze.get("hashes") or []
    if _bundle_hash(entries) != freeze.get("content_sha256"):
        problems.append("freeze.content_sha256 mismatch")
    declared_paths: list[str] = []
    declared_rel: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        raw = str(entry.get("path", ""))
        declared_paths.append(raw)
        resolved, ref_code = _safe_repo_file(raw, repo_root)
        if ref_code is not None or resolved is None:
            problems.append(f"freeze hash path is not safe existing regular file: {display_source_path(raw)}")
            continue
        if not _inside(resolved, bundle_dir):
            problems.append(f"freeze hash path outside runtime-candidate bundle: {display_source_path(raw)}")
            continue
        rel = resolved.relative_to(bundle_dir).as_posix()
        if rel == "freeze-manifest.yml":
            problems.append("runtime-candidate freeze manifest must not hash itself")
        declared_rel.add(rel)
        declared_hash = str(entry.get("sha256", ""))
        if not SHA256_RE.match(declared_hash):
            problems.append(f"malformed sha256 in freeze hash entry: {display_source_path(raw)}")
        elif _sha256(resolved) != declared_hash:
            problems.append(f"sha256 mismatch for {display_source_path(raw)}")
    duplicates = sorted({raw for raw in declared_paths if declared_paths.count(raw) > 1})
    for duplicate in duplicates:
        problems.append(f"duplicate freeze hash path: {display_source_path(duplicate)}")
    if declared_rel != EXPECTED_HASHED_FILES:
        problems.append(
            "runtime-candidate freeze must hash exactly: " + ", ".join(sorted(EXPECTED_HASHED_FILES))
        )
    return problems


def _validate_state_and_blockers(data: dict, registry: dict[str, set[str]], path: Path) -> list[str]:
    problems = []
    blockers = data.get("blockers") or []
    blocking_open = {
        str(item.get("id", ""))
        for item in blockers
        if isinstance(item, dict) and item.get("status") == "open" and item.get("severity") == "blocking"
    }
    missing = REQUIRED_BLOCKERS - blocking_open
    if missing:
        problems.append("missing mandatory open blocking runtime-candidate blockers: " + ", ".join(sorted(missing)))
    broker = data.get("broker") or {}
    sandbox = data.get("sandbox_access") or {}
    if broker.get("blocker_id") != "AGENT_TOOL_BROKER_UNRESOLVED":
        problems.append("broker.blocker_id must be AGENT_TOOL_BROKER_UNRESOLVED")
    if broker.get("broker_ready") is not False:
        problems.append("broker_ready must be false for the real runtime candidate")
    if broker.get("parent_model_controller_implemented") is not False:
        problems.append("parent_model_controller_implemented must be false")
    if broker.get("sandboxed_structured_tool_broker_implemented") is not False:
        problems.append("sandboxed_structured_tool_broker_implemented must be false")
    if sandbox.get("model_accessible_through_bound_sandbox") is not False:
        problems.append("model_accessible_through_bound_sandbox must be false")
    if sandbox.get("sockets_denied") is not True:
        problems.append("sandbox_access.sockets_denied must be true")
    if sandbox.get("allowed_command_roots") != ["/usr/bin", "/bin"]:
        problems.append("sandbox_access.allowed_command_roots must remain /usr/bin and /bin only")
    if str(sandbox.get("ollama_executable", "")).startswith(("/usr/bin/", "/bin/")):
        problems.append("ollama_executable must not be represented as sandbox-executable")
    state = data.get("state") or {}
    if any(
        state.get(field) is not False
        for field in (
            "run_004_execution_allowed",
            "run_004_executed",
            "result_assessment_allowed",
            "comparison_ready",
            "ordinary_validation_calls_model",
            "run_004_model_process_started",
            "run_004_agent_process_started",
        )
    ):
        problems.append("runtime candidate must not claim execution, assessment, model contact, or agent contact")
    if data.get("agent_binding", {}).get("binding_status") != "unresolved":
        problems.append("agent_binding must remain unresolved")
    if data.get("agent_binding", {}).get("codex_bound_for_run004") is not False:
        problems.append("Codex must not be bound for Run-004")
    if data.get("sampling_binding", {}).get("binding_status") != "unresolved":
        problems.append("sampling_binding must remain unresolved")
    missing_nonclaims = MANDATORY_NON_CLAIMS - {str(item) for item in (data.get("required_non_claims") or [])}
    if missing_nonclaims:
        problems.append("required_non_claims missing: " + ", ".join(sorted(missing_nonclaims)))
    for required_path, kind in (
        ("model-identity-evidence.yml", "model_identity"),
        ("runtime-environment-evidence.yml", "runtime_environment"),
    ):
        match = [
            path_ref
            for path_ref, kinds in registry.items()
            if path_ref.endswith("/" + required_path) and kind in kinds
        ]
        if not match:
            problems.append(f"runtime candidate must registry-bind {required_path} as {kind}")
    return problems


def semantic_errors(data: dict, path: Path, repo_root: Path) -> list[str]:
    errors = []
    if data.get("series_id") != RUN_004_SERIES_ID:
        errors.append(format_error("RUNTIME_CANDIDATE_REQUIRES_RUN004_IDENTITY", path, "series_id is not the Run-004 series"))
    if data.get("design_id") != RUN_004_DESIGN_ID:
        errors.append(format_error("RUNTIME_CANDIDATE_REQUIRES_RUN004_IDENTITY", path, "design_id is not the Run-004 design"))
    if data.get("challenge_version") != RUN_004_CHALLENGE_VERSION:
        errors.append(format_error("RUNTIME_CANDIDATE_REQUIRES_RUN004_IDENTITY", path, "challenge_version is not rest-api-v1"))
    if data.get("artifact_type") != RUN_004_ARTIFACT_TYPE or data.get("contract_version") != RUN_004_CONTRACT_VERSION:
        errors.append(format_error("RUNTIME_CANDIDATE_REQUIRES_RUN004_IDENTITY", path, "artifact type or contract version mismatch"))
    self_ref = str(data.get("candidate_artifact_path", ""))
    self_resolved, self_code = _safe_repo_file(self_ref, repo_root)
    if self_code is not None or self_resolved is None or self_resolved != path.resolve():
        errors.append(format_error("RUNTIME_CANDIDATE_REQUIRES_SELF_IDENTITY", path, "candidate_artifact_path must resolve to the validated file"))
    provenance_problems = _validate_provenance(data, path, repo_root)
    if provenance_problems:
        errors.append(format_error("RUNTIME_CANDIDATE_REQUIRES_PROVENANCE", path, "; ".join(provenance_problems)))
    registry, registry_problems = _validate_evidence_registry(data, path, repo_root)
    if registry_problems:
        errors.append(format_error("RUNTIME_CANDIDATE_REQUIRES_EVIDENCE_REGISTRY", path, "; ".join(registry_problems)))
    evidence_path_problems = _validate_evidence_paths(data, repo_root)
    if evidence_path_problems:
        errors.append(format_error("RUNTIME_CANDIDATE_REQUIRES_EVIDENCE_PATHS", path, "; ".join(evidence_path_problems)))
    state_problems = _validate_state_and_blockers(data, registry, path)
    if state_problems:
        errors.append(format_error("RUNTIME_CANDIDATE_REQUIRES_BLOCKED_STATE", path, "; ".join(state_problems)))
    freeze_ref = str((data.get("freeze") or {}).get("freeze_manifest_ref", ""))
    freeze_path, freeze_code = _safe_repo_file(freeze_ref, repo_root)
    if freeze_code is not None or freeze_path is None:
        errors.append(format_error("RUNTIME_CANDIDATE_REQUIRES_FREEZE", path, "freeze manifest is missing or unsafe"))
        return errors
    try:
        freeze = load_yaml(freeze_path)
    except (FileNotFoundError, ValueError) as exc:
        return [format_error("RUNTIME_CANDIDATE_REQUIRES_FREEZE", path, str(exc))]
    freeze_schema_errors = schema_errors(load_validator(FREEZE_SCHEMA_PATH), freeze, freeze_path, label="child=freeze")
    if freeze_schema_errors:
        return freeze_schema_errors
    freeze_problems = _validate_freeze(data, freeze, path, freeze_path, repo_root)
    if freeze_problems:
        errors.append(format_error("RUNTIME_CANDIDATE_REQUIRES_VALID_FREEZE", path, "; ".join(freeze_problems)))
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
    sem = semantic_errors(data, path, root)
    if sem:
        return 1, sem
    return 0, []


def discover_run_004_runtime_candidates(repo_root: Path):
    experiments = repo_root / "experiments"
    if not experiments.is_dir():
        return []
    return sorted(experiments.glob(RUN_004_DISCOVERY_GLOB), key=lambda p: p.as_posix())


def main(argv=None, *, repo_root: Path | None = None):
    root = repo_root if repo_root is not None else REPO_ROOT
    parser = argparse.ArgumentParser(description="Validate Run-004 runtime-candidate preflight bundles.")
    parser.add_argument("paths", nargs="*")
    args = parser.parse_args(argv)
    try:
        validator = load_validator(CANDIDATE_SCHEMA_PATH)
        load_validator(FREEZE_SCHEMA_PATH)
        load_validator(EVIDENCE_SCHEMA_PATH)
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        return 2
    if args.paths:
        paths = [Path(raw) if Path(raw).is_absolute() else (root / raw) for raw in args.paths]
    else:
        paths = discover_run_004_runtime_candidates(root)
        if not paths:
            print("ERROR: no Run-004 runtime-candidate bundle found; empty discovery is a failure, not a skip.")
            return 2
    highest, passed = 0, 0
    for candidate in paths:
        code, errs = validate_file(candidate, validator, root)
        highest = max(highest, code)
        for err in errs:
            print(err)
        if code == 0:
            passed += 1
            print(f"OK runtime_candidate={display_path(candidate)}")
    print(f"Run-004 runtime-candidate bundles: checked={len(paths)}, passed={passed}, failed={len(paths) - passed}")
    return highest


if __name__ == "__main__":
    sys.exit(main())
