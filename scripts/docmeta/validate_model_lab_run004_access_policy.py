#!/usr/bin/env python3
"""Validate the canonical Run-004 access-policy bundle.

The validator is deliberately Run-004-specific. It never executes a model or
agent and does not rerun the live probe; it verifies the recorded access-policy
bundle semantically and cryptographically. The separate probe script performs
live negative checks.
"""
from __future__ import annotations

import argparse
import ctypes.util
import hashlib
import json
import subprocess
import sys
from pathlib import Path, PurePosixPath

import yaml
from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError

import run_model_lab_run004_sandbox as sandbox

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCHEMA_DIR = REPO_ROOT / "schemas"
POLICY_SCHEMA_PATH = SCHEMA_DIR / "model-lab-access-policy.v1.schema.json"
PROBE_SCHEMA_PATH = SCHEMA_DIR / "model-lab-access-policy-probe.v1.schema.json"
FREEZE_SCHEMA_PATH = SCHEMA_DIR / "model-lab-access-policy-freeze-manifest.v1.schema.json"
EVIDENCE_SCHEMA_PATH = SCHEMA_DIR / "model-lab-execution-readiness-evidence.v1.schema.json"

ACCESS_POLICY_DIR = (
    REPO_ROOT
    / "experiments/2026-05-31_model-lab-replication-series/artifacts/run-004-access-policy"
)
DEFAULT_POLICY = ACCESS_POLICY_DIR / "access-policy.yml"
BOUNDARY_PROBE_NAME = "boundary-probe.json"
ACCESS_EVIDENCE_NAME = "access-policy-evidence.yml"
VISIBILITY_EVIDENCE_NAME = "visibility-boundary-evidence.yml"
FREEZE_NAME = "freeze-manifest.yml"
PROBE_RUNNER_REF = "scripts/docmeta/probe_model_lab_run004_access_policy.py"

RUN_004_SERIES_ID = "2026-05-31_model-lab-replication-series"
RUN_004_DESIGN_ID = "run-004-condition-contrast"
RUN_004_CHALLENGE_VERSION = "rest-api-v1"
MANDATORY_PROBE_NON_CLAIMS = {
    "run_004_executed",
    "model_process_started",
    "agent_process_started",
    "runtime_model_agent_sampling_bound",
    "result_assessment_allowed",
    "comparison_ready",
    "general_container_security",
}
_SCHEMA_CACHE: dict[Path, Draft202012Validator] = {}


class ToolError(Exception):
    """Environment/tooling failure."""


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except (OSError, RuntimeError, ValueError):
        return str(path)


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


def _repo_rel(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()


def _load_validator(schema_path: Path) -> Draft202012Validator:
    if schema_path in _SCHEMA_CACHE:
        return _SCHEMA_CACHE[schema_path]
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
    except FileNotFoundError as exc:
        raise ToolError(f"schema missing: {display_path(schema_path)}") from exc
    except (json.JSONDecodeError, UnicodeDecodeError, OSError, SchemaError) as exc:
        raise ToolError(f"schema invalid or unreadable: {display_path(schema_path)}: {exc}") from exc
    validator = Draft202012Validator(schema)
    _SCHEMA_CACHE[schema_path] = validator
    return validator


def _schema_errors(schema_path: Path, data, path: Path) -> list[str]:
    validator = _load_validator(schema_path)
    errors = []
    for err in sorted(validator.iter_errors(data), key=lambda item: tuple(str(p) for p in item.absolute_path)):
        loc = ".".join(str(part) for part in err.absolute_path) or "$"
        errors.append(f"{display_path(path)} schema {loc}: {err.message}")
    return errors


def _load_yaml(path: Path) -> dict:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"YAML document must be an object: {display_path(path)}")
    return loaded


def _load_json(path: Path) -> dict:
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"JSON document must be an object: {display_path(path)}")
    return loaded


def _safe_repo_file(raw: str) -> Path | None:
    resolved, code = sandbox.workspace_builder.readiness.resolve_repo_relative_path(
        raw,
        REPO_ROOT,
        must_exist=True,
    )
    if code is not None or resolved is None or not resolved.is_file():
        return None
    return resolved


def _check_environment_tools(policy: dict) -> list[str]:
    problems = []
    executable = Path(policy["backend"]["executable"])
    if not executable.is_file() or executable.is_symlink():
        problems.append("bubblewrap executable is missing or unsafe")
    else:
        try:
            version = subprocess.run(
                [str(executable), "--version"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="strict",
                check=False,
                timeout=10,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            raise ToolError(f"cannot check bubblewrap version: {exc}") from exc
        if version.returncode != 0:
            problems.append("bubblewrap --version failed")
        elif sandbox._version_tuple(version.stdout) < sandbox._version_tuple(policy["backend"]["minimum_version"]):
            problems.append("bubblewrap version is below the policy minimum")
    if ctypes.util.find_library("seccomp") is None:
        problems.append("libseccomp is unavailable")
    return problems


def _validate_probe_result(probe: dict, probe_path: Path, policy: dict, policy_path: Path) -> list[str]:
    problems = _schema_errors(PROBE_SCHEMA_PATH, probe, probe_path)
    if problems:
        return problems
    if probe.get("synthetic_fixture") is True:
        problems.append("canonical boundary probe must not be synthetic")
    expected_paths = {
        "policy_ref": _repo_rel(policy_path),
        "launcher_ref": policy["launcher_ref"],
        "isolation_plan_ref": policy["isolation_plan_ref"],
    }
    for field, expected in expected_paths.items():
        if probe.get(field) != expected:
            problems.append(f"boundary probe {field} must be {expected}")
    for ref_field, hash_field in (
        ("policy_ref", "policy_sha256"),
        ("launcher_ref", "launcher_sha256"),
        ("isolation_plan_ref", "isolation_plan_sha256"),
    ):
        target = _safe_repo_file(str(probe.get(ref_field, "")))
        if target is None:
            problems.append(f"boundary probe {ref_field} is not a safe existing file")
        elif _sha256(target) != probe.get(hash_field):
            problems.append(f"boundary probe {hash_field} mismatch")
    if set(probe.get("non_claims") or []) < MANDATORY_PROBE_NON_CLAIMS:
        problems.append("boundary probe is missing mandatory non-claims")
    policy_arms = policy.get("arms") or {}
    for role in ("control", "treatment"):
        arm = (probe.get("arms") or {}).get(role) or {}
        expected_hash = (policy_arms.get(role) or {}).get("payload_sha256")
        if arm.get("expected_prompt_sha256") != expected_hash:
            problems.append(f"boundary probe {role} expected prompt hash must match policy")
        if arm.get("observed_prompt_sha256") != expected_hash:
            problems.append(f"boundary probe {role} observed prompt hash must match policy")
        checks = arm.get("checks") or {}
        failed = sorted(name for name, value in checks.items() if value is not True)
        if failed:
            problems.append(f"boundary probe {role} has failed checks: {', '.join(failed)}")
    return problems


def _validate_evidence(path: Path, expected_kind: str) -> list[str]:
    problems = []
    try:
        data = _load_yaml(path)
    except (OSError, UnicodeError, ValueError, yaml.YAMLError) as exc:
        return [f"{display_path(path)} is invalid or unreadable: {exc}"]
    problems.extend(_schema_errors(EVIDENCE_SCHEMA_PATH, data, path))
    if problems:
        return problems
    if data.get("synthetic_fixture") is True:
        problems.append(f"{display_path(path)} must not be synthetic")
    claims = data.get("claims") or []
    if len(claims) != 1 or claims[0].get("kind") != expected_kind:
        problems.append(f"{display_path(path)} must contain exactly one {expected_kind} claim")
    return problems


def _expected_freeze_paths(policy_path: Path, bundle_dir: Path, policy: dict) -> set[str]:
    return {
        _repo_rel(policy_path),
        policy["launcher_ref"],
        PROBE_RUNNER_REF,
        policy["isolation_plan_ref"],
        _repo_rel(bundle_dir / BOUNDARY_PROBE_NAME),
        _repo_rel(bundle_dir / ACCESS_EVIDENCE_NAME),
        _repo_rel(bundle_dir / VISIBILITY_EVIDENCE_NAME),
    }


def _validate_freeze(freeze: dict, freeze_path: Path, policy_path: Path, policy: dict) -> list[str]:
    problems = _schema_errors(FREEZE_SCHEMA_PATH, freeze, freeze_path)
    if problems:
        return problems
    bundle_dir = policy_path.resolve().parent
    for field, expected in (
        ("policy_id", policy["policy_id"]),
        ("series_id", RUN_004_SERIES_ID),
        ("design_id", RUN_004_DESIGN_ID),
        ("challenge_version", RUN_004_CHALLENGE_VERSION),
    ):
        if freeze.get(field) != expected:
            problems.append(f"freeze {field} must be {expected}")
    if freeze.get("manifest_excludes_itself") is not True:
        problems.append("freeze manifest_excludes_itself must be true")
    entries = freeze.get("hashes") or []
    if _bundle_hash(entries) != freeze.get("content_sha256"):
        problems.append("freeze content_sha256 mismatch")
    seen: set[str] = set()
    expected_paths = _expected_freeze_paths(policy_path, bundle_dir, policy)
    observed_paths: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        raw = str(entry.get("path", ""))
        if raw in seen:
            problems.append(f"duplicate freeze hash path: {raw}")
        seen.add(raw)
        if raw == _repo_rel(freeze_path):
            problems.append("access-policy freeze manifest must not hash itself")
        path = _safe_repo_file(raw)
        if path is None:
            problems.append(f"freeze hash path is not safe/existing: {raw}")
            continue
        observed_paths.add(raw)
        if _sha256(path) != entry.get("sha256"):
            problems.append(f"freeze hash mismatch: {raw}")
    missing = expected_paths - observed_paths
    extra = observed_paths - expected_paths
    if missing:
        problems.append("freeze missing expected paths: " + ", ".join(sorted(missing)))
    if extra:
        problems.append("freeze contains unexpected paths: " + ", ".join(sorted(extra)))
    return problems


def validate_bundle(policy_path: Path = DEFAULT_POLICY) -> list[str]:
    problems: list[str] = []
    policy_path = policy_path if policy_path.is_absolute() else REPO_ROOT / policy_path
    policy, policy_problems = sandbox.validate_policy(policy_path, REPO_ROOT)
    problems.extend(policy_problems)
    if policy is None:
        return problems
    try:
        policy_data = _load_yaml(policy_path)
    except (OSError, UnicodeError, ValueError, yaml.YAMLError) as exc:
        return [f"{display_path(policy_path)} is invalid or unreadable: {exc}"]
    problems.extend(_schema_errors(POLICY_SCHEMA_PATH, policy_data, policy_path))
    if policy_data.get("synthetic_fixture") is True:
        problems.append("canonical access policy must not be synthetic")
    problems.extend(_check_environment_tools(policy_data))

    bundle_dir = policy_path.resolve().parent
    probe_path = bundle_dir / BOUNDARY_PROBE_NAME
    freeze_path = bundle_dir / FREEZE_NAME
    for required in (probe_path, freeze_path, bundle_dir / ACCESS_EVIDENCE_NAME, bundle_dir / VISIBILITY_EVIDENCE_NAME):
        if not required.is_file() or required.is_symlink():
            problems.append(f"required bundle file missing or unsafe: {display_path(required)}")
    if problems:
        return problems

    try:
        probe = _load_json(probe_path)
        freeze = _load_yaml(freeze_path)
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError, yaml.YAMLError) as exc:
        return problems + [f"bundle child invalid or unreadable: {exc}"]
    problems.extend(_validate_probe_result(probe, probe_path, policy_data, policy_path))
    problems.extend(_validate_evidence(bundle_dir / ACCESS_EVIDENCE_NAME, "access_policy"))
    problems.extend(_validate_evidence(bundle_dir / VISIBILITY_EVIDENCE_NAME, "visibility_boundary"))
    problems.extend(_validate_freeze(freeze, freeze_path, policy_path, policy_data))
    return problems


def readiness_binding(policy_path: Path = DEFAULT_POLICY) -> dict:
    policy_path = policy_path if policy_path.is_absolute() else REPO_ROOT / policy_path
    bundle_dir = policy_path.resolve().parent
    policy = _load_yaml(policy_path)
    paths = {
        "policy_ref": _repo_rel(policy_path),
        "launcher_ref": policy["launcher_ref"],
        "probe_runner_ref": PROBE_RUNNER_REF,
        "boundary_probe_ref": _repo_rel(bundle_dir / BOUNDARY_PROBE_NAME),
        "freeze_manifest_ref": _repo_rel(bundle_dir / FREEZE_NAME),
    }
    out: dict[str, str] = {}
    for ref_key, ref in paths.items():
        out[ref_key] = ref
        hash_key = ref_key.removesuffix("_ref") + "_sha256"
        out[hash_key] = _sha256(REPO_ROOT / ref)
    return out


def _looks_repo_relative(raw: str) -> bool:
    path = PurePosixPath(raw)
    return bool(raw) and not raw.startswith("/") and ".." not in path.parts and "\\" not in raw


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Validate the Run-004 access-policy bundle.")
    parser.add_argument("policy", nargs="?", type=Path, default=DEFAULT_POLICY)
    args = parser.parse_args(argv)
    try:
        problems = validate_bundle(args.policy)
    except ToolError as exc:
        print(f"ERROR: {exc}")
        return 2
    except (OSError, UnicodeError, ValueError, yaml.YAMLError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 2
    if problems:
        for problem in problems:
            print(f"ERROR: {problem}")
        return 1
    print(f"OK access_policy={display_path(args.policy if args.policy.is_absolute() else REPO_ROOT / args.policy)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
