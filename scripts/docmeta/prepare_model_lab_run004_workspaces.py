#!/usr/bin/env python3
"""Validate and materialize the canonical Run-004 isolated workspace plan."""
from __future__ import annotations

import argparse
import ctypes
import errno
import hashlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

import build_model_lab_execution_seed as seed_builder
import validate_model_lab_execution_readiness as readiness

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_PLAN = (
    REPO_ROOT
    / "experiments/2026-05-31_model-lab-replication-series/artifacts/"
    / "run-004-workspace-isolation/workspace-isolation-plan.yml"
)
SCHEMA_PATH = REPO_ROOT / "schemas/model-lab-workspace-isolation-plan.v1.schema.json"
DESIGN_SNAPSHOT = (
    REPO_ROOT
    / "experiments/2026-05-31_model-lab-replication-series/artifacts/"
    / "run-004-execution-readiness/source-snapshots/condition-design.snapshot"
)
ROLES = ("control", "treatment")
ROLE_LEAK_RE = readiness.ROLE_LEAK_RE


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _schema_error_sort_key(error):
    return tuple(str(part) for part in error.absolute_path), error.message


def _load_repo_file(raw: str, repo_root: Path) -> Path | None:
    resolved, code = readiness.resolve_repo_relative_path(raw, repo_root, must_exist=True)
    if code is not None or resolved is None or not resolved.is_file() or resolved.is_symlink():
        return None
    return resolved


def _component_text(path: Path) -> str:
    raw = path.read_bytes()
    if b"\r" in raw:
        raise ValueError(f"component contains CR: {path}")
    if not raw.endswith(b"\n"):
        raise ValueError(f"component lacks final LF: {path}")
    return raw[:-1].decode("utf-8")


def prompt_bytes(slot: dict, repo_root: Path) -> bytes:
    parts = []
    for key in ("benchmark_ref", "shared_condition_ref", "overlay_ref"):
        path = _load_repo_file(str(slot.get(key, "")), repo_root)
        if path is None:
            raise ValueError(f"unsafe or missing {key}")
        parts.append(_component_text(path))
    return ("\n\n".join(parts) + "\n").encode("utf-8")


def _under(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def _canonical_absolute(raw) -> bool:
    if not isinstance(raw, str) or not raw.startswith("/"):
        return False
    path = Path(raw)
    return path.is_absolute() and "." not in path.parts and ".." not in path.parts and path.as_posix() == raw


def _rename_noreplace(source: Path, destination: Path) -> None:
    """Atomically publish a directory without replacing an existing destination."""
    libc = ctypes.CDLL(None, use_errno=True)
    renameat2 = getattr(libc, "renameat2", None)
    if renameat2 is None:
        raise OSError(errno.ENOSYS, "renameat2(RENAME_NOREPLACE) is required")
    renameat2.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
    renameat2.restype = ctypes.c_int
    at_fdcwd = -100
    rename_noreplace = 1
    result = renameat2(
        at_fdcwd,
        os.fsencode(source),
        at_fdcwd,
        os.fsencode(destination),
        rename_noreplace,
    )
    if result != 0:
        error_number = ctypes.get_errno()
        if error_number == errno.EEXIST:
            raise FileExistsError(error_number, os.strerror(error_number), destination)
        raise OSError(error_number, os.strerror(error_number), destination)


def validate_plan(plan_path: Path, repo_root: Path) -> tuple[dict | None, list[str]]:
    problems: list[str] = []
    try:
        resolved_plan = plan_path.resolve(strict=True)
        resolved_plan.relative_to(repo_root.resolve())
    except (OSError, RuntimeError, ValueError):
        return None, ["plan must be a safe existing repository file"]
    if resolved_plan.is_symlink() or not resolved_plan.is_file():
        return None, ["plan must be a regular non-symlink file"]
    try:
        data = yaml.safe_load(resolved_plan.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        return None, [f"plan is invalid or unreadable: {exc}"]
    try:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        return None, [f"plan schema is invalid or unreadable: {exc}"]
    for error in sorted(Draft202012Validator(schema).iter_errors(data), key=_schema_error_sort_key):
        where = ".".join(str(part) for part in error.absolute_path) or "$"
        problems.append(f"schema {where}: {error.message}")
    if not isinstance(data, dict):
        return None, problems or ["plan must be a mapping"]
    if data.get("synthetic_fixture") is True and not resolved_plan.relative_to(repo_root.resolve()).as_posix().startswith("tests/fixtures/"):
        problems.append("synthetic plan is forbidden outside fixtures")
    runtime_root = Path(str(data.get("runtime_root", "")))
    if not runtime_root.is_absolute():
        problems.append("runtime_root must be absolute")
    if _under(runtime_root, repo_root.resolve()) or runtime_root == repo_root.resolve():
        problems.append("runtime_root must be outside the repository")
    seed_ref = str(data.get("seed_manifest_ref", ""))
    seed_path = _load_repo_file(seed_ref, repo_root)
    if seed_path is None:
        problems.append("seed_manifest_ref must be a safe existing repository file")
    else:
        if _sha256(seed_path) != data.get("seed_manifest_sha256"):
            problems.append("seed_manifest_sha256 mismatch")
        _, seed_problems = seed_builder.validate_manifest(seed_path, repo_root)
        problems.extend(f"seed: {problem}" for problem in seed_problems)
    materializer_ref = str(data.get("materializer_ref", ""))
    materializer_path = _load_repo_file(materializer_ref, repo_root)
    if materializer_path is None:
        problems.append("materializer_ref must be a safe existing repository file")
    elif _sha256(materializer_path) != data.get("materializer_sha256"):
        problems.append("materializer_sha256 mismatch")
    design_assembly = {}
    try:
        design = yaml.safe_load(DESIGN_SNAPSHOT.read_text(encoding="utf-8"))
        design_assembly = (design or {}).get("condition_input_assembly") or {}
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        problems.append(f"frozen condition design is invalid or unreadable: {exc}")
    design_components = design_assembly.get("components") or {}
    design_arms = design_assembly.get("arms") or {}
    slots = data.get("slots") or {}
    values: dict[str, list[str]] = {field: [] for field in (
        "slot_id", "slot_root", "workspace_path", "delivery_path", "session_id", "temp_dir", "cache_dir", "port_assignment"
    )}
    for role in ROLES:
        slot = slots.get(role) or {}
        for field in values:
            value = slot.get(field)
            if isinstance(value, str):
                values[field].append(value)
                if ROLE_LEAK_RE.search(value):
                    problems.append(f"slots.{role}.{field} leaks a role token")
        for field in ("slot_root", "workspace_path", "delivery_path", "temp_dir", "cache_dir"):
            if not _canonical_absolute(slot.get(field)):
                problems.append(f"slots.{role}.{field} must be a canonical absolute path without aliases")
        for list_field in ("allowed_paths", "forbidden_paths"):
            for raw_path in slot.get(list_field) or []:
                if not _canonical_absolute(raw_path):
                    problems.append(f"slots.{role}.{list_field} contains a non-canonical absolute path")
                if isinstance(raw_path, str) and ROLE_LEAK_RE.search(raw_path):
                    problems.append(f"slots.{role}.{list_field} leaks a role token")
        try:
            slot_root = Path(slot["slot_root"])
            workspace = Path(slot["workspace_path"])
            delivery = Path(slot["delivery_path"])
            temp_dir = Path(slot["temp_dir"])
            cache_dir = Path(slot["cache_dir"])
        except (KeyError, TypeError):
            continue
        if not _under(slot_root, runtime_root) or slot_root == runtime_root:
            problems.append(f"slots.{role}.slot_root must be below runtime_root")
        expected_layout = {
            "workspace_path": slot_root / "workspace",
            "delivery_path": slot_root / "delivery" / "task.md",
            "temp_dir": slot_root / "tmp",
            "cache_dir": slot_root / "cache",
        }
        actual_layout = {
            "workspace_path": workspace,
            "delivery_path": delivery,
            "temp_dir": temp_dir,
            "cache_dir": cache_dir,
        }
        for field, expected_path in expected_layout.items():
            if actual_layout[field] != expected_path:
                problems.append(f"slots.{role}.{field} must use the canonical slot layout")
        if slot.get("allowed_paths") != [slot.get("workspace_path")]:
            problems.append(f"slots.{role}.allowed_paths must contain only workspace_path")
        forbidden = set(slot.get("forbidden_paths") or [])
        if str(delivery.parent) not in forbidden:
            problems.append(f"slots.{role}.forbidden_paths must include its delivery directory")
        expected_refs = {
            "benchmark_ref": ((design_components.get("benchmark") or {}).get("ref")),
            "shared_condition_ref": ((design_components.get("shared_condition") or {}).get("ref")),
            "overlay_ref": ((design_arms.get(role) or {}).get("overlay_ref")),
        }
        for field, expected_ref in expected_refs.items():
            if slot.get(field) != expected_ref:
                problems.append(f"slots.{role}.{field} must match the frozen condition design")
        try:
            payload = prompt_bytes(slot, repo_root)
        except (OSError, UnicodeError, ValueError) as exc:
            problems.append(f"slots.{role}: {exc}")
        else:
            if hashlib.sha256(payload).hexdigest() != slot.get("payload_sha256"):
                problems.append(f"slots.{role}.payload_sha256 mismatch")
    for field, observed in values.items():
        if len(observed) != 2 or len(set(observed)) != 2:
            problems.append(f"both slots must have distinct bound {field}")
    if all(_canonical_absolute((slots.get(role) or {}).get("slot_root")) for role in ROLES):
        first_root = Path(slots["control"]["slot_root"])
        second_root = Path(slots["treatment"]["slot_root"])
        if _under(first_root, second_root) or _under(second_root, first_root):
            problems.append("slot roots must be non-overlapping siblings")
    if all(isinstance((slots.get(role) or {}).get("slot_root"), str) for role in ROLES):
        if slots["treatment"]["slot_root"] not in set(slots["control"].get("forbidden_paths") or []):
            problems.append("control forbidden_paths must include the other slot root")
        if slots["control"]["slot_root"] not in set(slots["treatment"].get("forbidden_paths") or []):
            problems.append("treatment forbidden_paths must include the other slot root")
    return (data if not problems else None), problems


def _mapped_path(raw: str, canonical_root: Path, materialized_root: Path) -> Path:
    path = Path(raw)
    relative = path.relative_to(canonical_root)
    return materialized_root / relative


def inspect_materialization(data: dict, output_root: Path, repo_root: Path) -> list[str]:
    problems: list[str] = []
    canonical_root = Path(data["runtime_root"])
    expected_prompt_files: set[Path] = set()
    for role in ROLES:
        slot = data["slots"][role]
        workspace = _mapped_path(slot["workspace_path"], canonical_root, output_root)
        delivery = _mapped_path(slot["delivery_path"], canonical_root, output_root)
        temp_dir = _mapped_path(slot["temp_dir"], canonical_root, output_root)
        cache_dir = _mapped_path(slot["cache_dir"], canonical_root, output_root)
        for label, path in (("workspace", workspace), ("temp", temp_dir), ("cache", cache_dir)):
            if not path.is_dir() or path.is_symlink():
                problems.append(f"{role} {label} directory missing or unsafe")
        if workspace.is_dir() and any(workspace.iterdir()):
            problems.append(f"{role} workspace is not the empty canonical seed")
        if not delivery.is_file() or delivery.is_symlink():
            problems.append(f"{role} assigned prompt file missing or unsafe")
        else:
            payload = delivery.read_bytes()
            if hashlib.sha256(payload).hexdigest() != slot["payload_sha256"]:
                problems.append(f"{role} assigned prompt hash mismatch")
            if payload != prompt_bytes(slot, repo_root):
                problems.append(f"{role} assigned prompt bytes mismatch")
        expected_prompt_files.add(delivery)
    for path in output_root.rglob("*"):
        if path.is_symlink():
            problems.append(f"symlink forbidden in materialization: {path.relative_to(output_root)}")
        if path.is_file() and path not in expected_prompt_files:
            problems.append(f"unexpected file in materialization: {path.relative_to(output_root)}")
        if path.name == ".git":
            problems.append("repository metadata is forbidden in materialized slots")
    return problems


def materialize(plan_path: Path, output_root: Path, repo_root: Path) -> dict:
    data, problems = validate_plan(plan_path, repo_root)
    if problems or data is None:
        raise ValueError("; ".join(problems))
    output_root = output_root.resolve(strict=False)
    repo_resolved = repo_root.resolve()
    if output_root.exists() or output_root.is_symlink():
        raise FileExistsError(f"output already exists: {output_root}")
    if _under(output_root, repo_resolved) or output_root == repo_resolved:
        raise ValueError("output root must be outside the repository")
    output_root.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{output_root.name}.", dir=str(output_root.parent)))
    canonical_root = Path(data["runtime_root"])
    try:
        seed_path = _load_repo_file(data["seed_manifest_ref"], repo_root)
        if seed_path is None:
            raise ValueError("seed manifest unavailable")
        for role in ROLES:
            slot = data["slots"][role]
            slot_root = _mapped_path(slot["slot_root"], canonical_root, staging)
            workspace = _mapped_path(slot["workspace_path"], canonical_root, staging)
            delivery = _mapped_path(slot["delivery_path"], canonical_root, staging)
            temp_dir = _mapped_path(slot["temp_dir"], canonical_root, staging)
            cache_dir = _mapped_path(slot["cache_dir"], canonical_root, staging)
            slot_root.mkdir(parents=True, exist_ok=False)
            seed_builder.materialize(seed_path, workspace, repo_root)
            temp_dir.mkdir(parents=True, exist_ok=False)
            cache_dir.mkdir(parents=True, exist_ok=False)
            delivery.parent.mkdir(parents=True, exist_ok=False)
            delivery.write_bytes(prompt_bytes(slot, repo_root))
        inspection = inspect_materialization(data, staging, repo_root)
        if inspection:
            raise ValueError("; ".join(inspection))
        _rename_noreplace(staging, output_root)
        return {
            "plan_id": data["plan_id"],
            "output_root": str(output_root),
            "slot_ids": [data["slots"][role]["slot_id"] for role in ROLES],
            "prompt_sha256": [data["slots"][role]["payload_sha256"] for role in ROLES],
        }
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--output-root", type=Path)
    args = parser.parse_args(argv)
    data, problems = validate_plan(args.plan, REPO_ROOT)
    if problems or data is None:
        for problem in problems:
            print(f"ERROR: {problem}")
        return 1
    if args.output_root is None:
        print(
            f"OK plan_id={data['plan_id']} slots=2 runtime_root={data['runtime_root']} "
            f"seed={data['seed_manifest_sha256']}"
        )
        return 0
    try:
        report = materialize(args.plan, args.output_root, REPO_ROOT)
    except (FileExistsError, OSError, UnicodeError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"OK materialized plan_id={report['plan_id']} output_root={report['output_root']} slots=2")
    return 0


if __name__ == "__main__":
    sys.exit(main())
