#!/usr/bin/env python3
"""Validate the closed Run-004 runtime-binding bundle.

This validator is intentionally static: it verifies the recorded local Ollama
model identity, local broker/protocol identity, sampling config, execution order,
partial environment observations, kind-separated evidence, and freeze hashes. It
does not contact Ollama and does not execute Run-004.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import sys
from pathlib import Path, PurePosixPath

import yaml
from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCHEMA_DIR = REPO_ROOT / "schemas"
CONTRACT_SCHEMA = SCHEMA_DIR / "model-lab-runtime-binding.v1.schema.json"
PROBE_SCHEMA = SCHEMA_DIR / "model-lab-runtime-binding-neutral-probe.v1.schema.json"
FREEZE_SCHEMA = SCHEMA_DIR / "model-lab-runtime-binding-freeze-manifest.v1.schema.json"
EVIDENCE_SCHEMA = SCHEMA_DIR / "model-lab-execution-readiness-evidence.v1.schema.json"

RUNTIME_DIR = (
    REPO_ROOT
    / "experiments/2026-05-31_model-lab-replication-series/artifacts/run-004-runtime-binding"
)
DEFAULT_CONTRACT = RUNTIME_DIR / "runtime-contract.yml"
FREEZE_NAME = "freeze-manifest.yml"
EXPECTED_FILES = {
    "agent-protocol.md",
    "runtime-contract.yml",
    "neutral-probe.yml",
    "model-identity-evidence.yml",
    "agent-identity-evidence.yml",
    "sampling-config-evidence.yml",
    "execution-order-evidence.yml",
    "runtime-environment-evidence.yml",
    FREEZE_NAME,
}
EXPECTED_EVIDENCE = {
    "model-identity-evidence.yml": "model_identity",
    "agent-identity-evidence.yml": "agent_identity",
    "sampling-config-evidence.yml": "sampling_config",
    "execution-order-evidence.yml": "execution_order",
    "runtime-environment-evidence.yml": "runtime_environment",
}
RUN_004_SERIES_ID = "2026-05-31_model-lab-replication-series"
RUN_004_DESIGN_ID = "run-004-condition-contrast"
RUN_004_CHALLENGE_VERSION = "rest-api-v1"
MANDATORY_NON_CLAIMS = {
    "run_004_executed",
    "run_004_result_measured",
    "result_assessment_allowed",
    "comparison_ready",
    "model_quality",
    "comparative_superiority",
    "condition_effect",
    "production_readiness",
    "security_readiness",
    "run_004_arm_workspace_materialized",
}
MANDATORY_PROBE_NON_CLAIMS = {
    "run_004_executed",
    "challenge_prompt_used",
    "arm_output_produced",
    "result_assessment_allowed",
    "comparison_ready",
    "live_ollama_required_for_ci",
}
MODEL_BLOCKER = "MODEL_BINDING_UNRESOLVED"
AGENT_BLOCKER = "AGENT_BINDING_UNRESOLVED"
SAMPLING_BLOCKER = "SAMPLING_BINDING_UNRESOLVED"
ORDER_BLOCKER = "EXECUTION_ORDER_UNRESOLVED"
RUNTIME_ENV_BLOCKER = "RUNTIME_ENVIRONMENT_UNRESOLVED"

_SCHEMA_CACHE: dict[Path, Draft202012Validator] = {}


class ToolError(Exception):
    """Validator setup/parsing failure."""


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except (OSError, RuntimeError, ValueError):
        return str(path)


def _sha(path: Path) -> str:
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


def _load_validator(path: Path) -> Draft202012Validator:
    if path in _SCHEMA_CACHE:
        return _SCHEMA_CACHE[path]
    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
    except (OSError, UnicodeError, json.JSONDecodeError, SchemaError) as exc:
        raise ToolError(f"schema invalid or unreadable: {display_path(path)}: {exc}") from exc
    validator = Draft202012Validator(schema)
    _SCHEMA_CACHE[path] = validator
    return validator


def _schema_errors(schema_path: Path, data, path: Path) -> list[str]:
    validator = _load_validator(schema_path)
    errors = []
    for err in sorted(validator.iter_errors(data), key=lambda item: tuple(str(p) for p in item.absolute_path)):
        loc = ".".join(str(part) for part in err.absolute_path) or "$"
        errors.append(f"{display_path(path)} schema {loc}: {err.message}")
    return errors


def _load_yaml(path: Path) -> dict:
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise ToolError(f"YAML invalid or unreadable: {display_path(path)}: {exc}") from exc
    if not isinstance(loaded, dict):
        raise ToolError(f"YAML document must be an object: {display_path(path)}")
    return loaded


def _has_symlink_component(path: Path, root: Path) -> bool:
    try:
        root_resolved = root.resolve(strict=True)
        resolved = path.resolve(strict=True)
        relative = resolved.relative_to(root_resolved)
    except (OSError, RuntimeError, ValueError):
        return True
    current = root_resolved
    for component in relative.parts:
        if component in ("", ".", ".."):
            return True
        current = current / component
        try:
            if current.is_symlink():
                return True
        except OSError:
            return True
    return False


def _safe_repo_file(raw: str) -> Path | None:
    if not raw or raw.startswith("/") or "\\" in raw or ".." in PurePosixPath(raw).parts:
        return None
    try:
        root = REPO_ROOT.resolve(strict=True)
        candidate = (root / raw).resolve(strict=True)
        candidate.relative_to(root)
    except (OSError, RuntimeError, ValueError):
        return None
    if _has_symlink_component(candidate, root) or not candidate.is_file():
        return None
    return candidate


def _program_binding_errors(path: Path, contract: dict) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, UnicodeError, SyntaxError) as exc:
        return [f"agent program constants are unreadable: {exc}"]
    names = {"MODEL_ALIAS", "OLLAMA_ENDPOINT", "OLLAMA_KEEP_ALIVE", "AGENT_VERSION", "PROTOCOL_SHA256", "SAMPLING"}
    values: dict[str, object] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name) or target.id not in names:
            continue
        try:
            values[target.id] = ast.literal_eval(node.value)
        except (TypeError, ValueError):
            return [f"agent program constant {target.id} must be literal"]
    missing = names - values.keys()
    if missing:
        return ["agent program missing bound constants: " + ", ".join(sorted(missing))]
    problems: list[str] = []
    if values["MODEL_ALIAS"] != (contract.get("model") or {}).get("alias"):
        problems.append("agent MODEL_ALIAS must match runtime contract model.alias")
    if values["OLLAMA_ENDPOINT"] != (contract.get("ollama") or {}).get("endpoint"):
        problems.append("agent OLLAMA_ENDPOINT must match runtime contract ollama.endpoint")
    if values["AGENT_VERSION"] != (contract.get("agent") or {}).get("agent_version"):
        problems.append("agent AGENT_VERSION must match runtime contract agent.agent_version")
    if values["PROTOCOL_SHA256"] != (contract.get("agent") or {}).get("protocol_sha256"):
        problems.append("agent PROTOCOL_SHA256 must match runtime contract agent.protocol_sha256")
    contract_sampling = contract.get("sampling") or {}
    program_sampling = values["SAMPLING"]
    if not isinstance(program_sampling, dict):
        problems.append("agent SAMPLING must be a literal mapping")
    else:
        for field, value in program_sampling.items():
            if contract_sampling.get(field) != value:
                problems.append(f"agent SAMPLING.{field} must match runtime contract sampling.{field}")
    if contract_sampling.get("same_across_arms") is not True:
        problems.append("runtime contract sampling.same_across_arms must be true")
    if contract_sampling.get("stream") is not False:
        problems.append("runtime contract sampling.stream must be false")
    if values["OLLAMA_KEEP_ALIVE"] != contract_sampling.get("keep_alive"):
        problems.append("agent OLLAMA_KEEP_ALIVE must match runtime contract sampling.keep_alive")
    return problems


def _bundle_file_errors(bundle_dir: Path) -> list[str]:
    problems = []
    if not bundle_dir.is_dir() or bundle_dir.is_symlink():
        return [f"runtime binding bundle directory missing or unsafe: {display_path(bundle_dir)}"]
    observed: set[str] = set()
    for item in sorted(bundle_dir.rglob("*")):
        rel = item.relative_to(bundle_dir).as_posix()
        if item.is_symlink():
            problems.append(f"symlink not allowed in runtime bundle: {rel}")
            continue
        if item.is_dir():
            continue
        if not item.is_file():
            problems.append(f"non-regular path in runtime bundle: {rel}")
            continue
        observed.add(rel)
    missing = EXPECTED_FILES - observed
    extra = observed - EXPECTED_FILES
    if missing:
        problems.append("runtime bundle missing expected files: " + ", ".join(sorted(missing)))
    if extra:
        problems.append("runtime bundle contains unexpected files: " + ", ".join(sorted(extra)))
    return problems


def _validate_evidence(path: Path, expected_kind: str) -> tuple[list[str], set[str]]:
    problems: list[str] = []
    affected = {RUNTIME_ENV_BLOCKER}
    if expected_kind == "model_identity":
        affected = {MODEL_BLOCKER}
    elif expected_kind == "agent_identity":
        affected = {AGENT_BLOCKER}
    elif expected_kind == "sampling_config":
        affected = {SAMPLING_BLOCKER}
    elif expected_kind == "execution_order":
        affected = {ORDER_BLOCKER}
    data = _load_yaml(path)
    problems.extend(_schema_errors(EVIDENCE_SCHEMA, data, path))
    if problems:
        return problems, affected
    if data.get("synthetic_fixture") is True:
        problems.append(f"{display_path(path)} must not be synthetic")
    claims = data.get("claims") or []
    if len(claims) != 1 or claims[0].get("kind") != expected_kind:
        problems.append(f"{display_path(path)} must contain exactly one {expected_kind} claim")
    return problems, affected


def _validate_freeze(freeze: dict, freeze_path: Path, bundle_dir: Path, contract: dict) -> list[str]:
    problems = _schema_errors(FREEZE_SCHEMA, freeze, freeze_path)
    if problems:
        return problems
    expected_identity = {
        "binding_id": contract["binding_id"],
        "series_id": RUN_004_SERIES_ID,
        "design_id": RUN_004_DESIGN_ID,
        "challenge_version": RUN_004_CHALLENGE_VERSION,
    }
    for field, expected in expected_identity.items():
        if freeze.get(field) != expected:
            problems.append(f"freeze {field} must be {expected}")
    entries = freeze.get("hashes") or []
    if _bundle_hash(entries) != freeze.get("content_sha256"):
        problems.append("freeze content_sha256 mismatch")
    seen: set[str] = set()
    expected_hashed = {
        _repo_rel(bundle_dir / name)
        for name in EXPECTED_FILES
        if name != FREEZE_NAME
    }
    observed: set[str] = set()
    for entry in entries:
        raw = str(entry.get("path", ""))
        if raw in seen:
            problems.append(f"duplicate freeze hash path: {raw}")
        seen.add(raw)
        if raw == _repo_rel(freeze_path):
            problems.append("runtime freeze manifest must not hash itself")
        target = _safe_repo_file(raw)
        if target is None:
            problems.append(f"freeze hash path is not safe/existing: {raw}")
            continue
        observed.add(raw)
        if _sha(target) != entry.get("sha256"):
            problems.append(f"freeze hash mismatch: {raw}")
    missing = expected_hashed - observed
    extra = observed - expected_hashed
    if missing:
        problems.append("freeze missing expected paths: " + ", ".join(sorted(missing)))
    if extra:
        problems.append("freeze contains unexpected paths: " + ", ".join(sorted(extra)))
    return problems


def validate_bundle_with_blockers(contract_path: Path = DEFAULT_CONTRACT) -> tuple[list[str], set[str]]:
    problems: list[str] = []
    affected: set[str] = set()
    contract_path = contract_path if contract_path.is_absolute() else REPO_ROOT / contract_path
    bundle_dir = contract_path.resolve().parent
    problems.extend(_bundle_file_errors(bundle_dir))
    if problems:
        return problems, {MODEL_BLOCKER, AGENT_BLOCKER, SAMPLING_BLOCKER, ORDER_BLOCKER}

    contract = _load_yaml(contract_path)
    problems.extend(_schema_errors(CONTRACT_SCHEMA, contract, contract_path))
    if problems:
        return problems, {MODEL_BLOCKER, AGENT_BLOCKER, SAMPLING_BLOCKER, ORDER_BLOCKER}

    freeze_path = bundle_dir / FREEZE_NAME
    neutral_path = bundle_dir / "neutral-probe.yml"
    freeze = _load_yaml(freeze_path)
    neutral = _load_yaml(neutral_path)
    neutral_errors = _schema_errors(PROBE_SCHEMA, neutral, neutral_path)
    if neutral_errors:
        problems.extend(neutral_errors)
        affected.update({MODEL_BLOCKER, AGENT_BLOCKER})

    for name, kind in EXPECTED_EVIDENCE.items():
        child_errors, child_affected = _validate_evidence(bundle_dir / name, kind)
        if child_errors:
            problems.extend(child_errors)
            affected.update(child_affected)

    agent = contract.get("agent") or {}
    program = _safe_repo_file(str(agent.get("program_ref", "")))
    protocol = _safe_repo_file(str(agent.get("protocol_ref", "")))
    if program is None or _sha(program) != agent.get("program_sha256"):
        problems.append("agent program_ref/program_sha256 mismatch")
        affected.add(AGENT_BLOCKER)
    elif program_errors := _program_binding_errors(program, contract):
        problems.extend(program_errors)
        affected.update({MODEL_BLOCKER, AGENT_BLOCKER, SAMPLING_BLOCKER})
    if protocol is None or _sha(protocol) != agent.get("protocol_sha256"):
        problems.append("agent protocol_ref/protocol_sha256 mismatch")
        affected.add(AGENT_BLOCKER)
    elif agent.get("system_developer_identity_sha256") != agent.get("protocol_sha256"):
        problems.append("system_developer_identity_sha256 must equal protocol_sha256")
        affected.add(AGENT_BLOCKER)

    neutral_ref = _safe_repo_file(str(((contract.get("neutral_probe") or {}).get("ref", ""))))
    if neutral_ref is None or _sha(neutral_ref) != (contract.get("neutral_probe") or {}).get("sha256"):
        problems.append("neutral probe ref/sha256 mismatch")
        affected.update({MODEL_BLOCKER, AGENT_BLOCKER})
    if neutral.get("model_file_identity_verified") is not True:
        problems.append("neutral probe must verify local model file identity")
        affected.add(MODEL_BLOCKER)
    if neutral.get("ollama_client_version_verified") is not True:
        problems.append("neutral probe must verify Ollama client version")
        affected.add(MODEL_BLOCKER)
    ollama = contract.get("ollama") or {}
    if ollama.get("live_chat_status") != "verified":
        problems.append("runtime contract must record verified live Ollama loopback chat")
        affected.update({MODEL_BLOCKER, AGENT_BLOCKER})
    if neutral.get("ollama_loopback_chat_completed") is not True:
        problems.append("neutral probe must complete live Ollama loopback chat")
        affected.update({MODEL_BLOCKER, AGENT_BLOCKER})
    if neutral.get("textual_json_tool_action_verified") is not True:
        problems.append("neutral probe must verify the bound textual JSON tool-action format")
        affected.add(AGENT_BLOCKER)
    if neutral.get("multi_turn_tool_round_trip_verified") is not True:
        problems.append("neutral probe must verify a multi-turn tool-result round trip")
        affected.add(AGENT_BLOCKER)
    if neutral.get("structured_tool_action_verified") is not True:
        problems.append("neutral probe must verify one harmless structured tool action")
        affected.add(AGENT_BLOCKER)
    observations = neutral.get("observations") or {}
    expected_probe_observations = {
        "configured_num_ctx": 16384,
        "configured_num_predict": 4096,
        "keep_alive": "10m",
        "first_tool_name": "list_files",
        "first_tool_path": "",
        "follow_up_content": "DONE",
    }
    for field, expected in expected_probe_observations.items():
        if observations.get(field) != expected:
            problems.append(f"neutral probe observation {field} must equal {expected!r}")
            affected.update({MODEL_BLOCKER, AGENT_BLOCKER})
    if neutral.get("synthetic_workspace_removed") is not True:
        problems.append("neutral probe must remove its synthetic workspace")
        affected.add(AGENT_BLOCKER)
    if set(neutral.get("non_claims") or []) < MANDATORY_PROBE_NON_CLAIMS:
        problems.append("neutral probe is missing mandatory non-claims")
        affected.update({MODEL_BLOCKER, AGENT_BLOCKER})

    runtime_profile = contract.get("runtime_profile") or {}
    if runtime_profile.get("control_profile_id") != runtime_profile.get("treatment_profile_id"):
        problems.append("runtime profile must be identical across arms")
        affected.update({MODEL_BLOCKER, AGENT_BLOCKER, SAMPLING_BLOCKER})
    runtime_env = contract.get("runtime_environment") or {}
    unresolved = set(runtime_env.get("unresolved_fields") or [])
    required_unresolved = {
        "dependency_resolution_strategy",
        "cache_policy",
        "full_execution_environment",
        "node_jitless_command_binding",
    }
    if not required_unresolved.issubset(unresolved):
        problems.append("runtime_environment must preserve dependency/cache/full-environment/node-jitless unresolved fields")
        affected.add(RUNTIME_ENV_BLOCKER)
    if "live_ollama_loopback_chat" in unresolved:
        problems.append("verified live Ollama loopback chat must not remain listed as unresolved")
        affected.update({MODEL_BLOCKER, AGENT_BLOCKER, RUNTIME_ENV_BLOCKER})
    if set(contract.get("non_claims") or []) < MANDATORY_NON_CLAIMS:
        problems.append("runtime contract is missing mandatory non-claims")
        affected.update({MODEL_BLOCKER, AGENT_BLOCKER, SAMPLING_BLOCKER, ORDER_BLOCKER})
    problems.extend(_validate_freeze(freeze, freeze_path, bundle_dir, contract))
    if any("freeze" in problem for problem in problems):
        affected.update({MODEL_BLOCKER, AGENT_BLOCKER, SAMPLING_BLOCKER, ORDER_BLOCKER})
    return problems, affected


def validate_bundle(contract_path: Path = DEFAULT_CONTRACT) -> list[str]:
    problems, _ = validate_bundle_with_blockers(contract_path)
    return problems


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Validate the Run-004 runtime-binding bundle.")
    parser.add_argument("contract", nargs="?", type=Path, default=DEFAULT_CONTRACT)
    args = parser.parse_args(argv)
    try:
        problems = validate_bundle(args.contract)
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
    path = args.contract if args.contract.is_absolute() else REPO_ROOT / args.contract
    print(f"OK runtime_binding={display_path(path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
