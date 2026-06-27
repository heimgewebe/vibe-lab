#!/usr/bin/env python3
"""Live negative probe for the Run-004 access-policy sandbox.

This probe does not start a model or agent. It materializes the two empty
Run-004 slots, runs a neutral Python diagnostic program through the sandbox
launcher for each slot, records the boundary checks, and removes only the
runtime root it created itself.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import shutil
import sys
from pathlib import Path

import yaml

import prepare_model_lab_run004_workspaces as workspace_builder
import run_model_lab_run004_sandbox as sandbox

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ACCESS_POLICY_DIR = (
    REPO_ROOT
    / "experiments/2026-05-31_model-lab-replication-series/artifacts/run-004-access-policy"
)
DEFAULT_POLICY = ACCESS_POLICY_DIR / "access-policy.yml"
DEFAULT_OUTPUT = ACCESS_POLICY_DIR / "boundary-probe.json"
TRIGGERED_BY = "user-request-2026-06-27-run-004-access-policy"
NON_CLAIMS = [
    "run_004_executed",
    "model_process_started",
    "agent_process_started",
    "runtime_model_agent_sampling_bound",
    "result_assessment_allowed",
    "comparison_ready",
    "general_container_security",
]

DIAGNOSTIC_PROGRAM = r"""
import ctypes
import errno
import hashlib
import json
import os
import re
import socket
import sys

EXPECTED_ENV = {
    "HOME": "/workspace",
    "LANG": "C.UTF-8",
    "LC_ALL": "C.UTF-8",
    "PATH": "/usr/bin:/bin",
    "TMPDIR": "/tmp",
    "XDG_CACHE_HOME": "/cache",
}
ALLOWED_ROOT_ENTRIES = {
    "bin",
    "cache",
    "dev",
    "etc",
    "lib",
    "lib64",
    "proc",
    "tmp",
    "usr",
    "workspace",
}
ROLE_RE = re.compile(r"control|treatment", re.IGNORECASE)
SYS_UNSHARE_X86_64 = 272
SYS_IO_URING_SETUP_X86_64 = 425
SYS_FSOPEN_X86_64 = 430
CLONE_NEWNS = 0x00020000

expected_hash, repo_root, home_path, delivery_path, other_slot_root = sys.argv[1:6]
stdin_payload = sys.stdin.buffer.read()
observed_hash = hashlib.sha256(stdin_payload).hexdigest()

workspace_write = False
try:
    path = "/workspace/.probe-write-read"
    with open(path, "wb") as handle:
        handle.write(b"run004-probe\n")
    with open(path, "rb") as handle:
        workspace_write = handle.read() == b"run004-probe\n"
except OSError:
    workspace_write = False

root_entries = sorted(os.listdir("/"))
visible_sample = sorted(
    {"/", "/workspace", "/tmp", "/cache"} | {"/" + entry for entry in root_entries}
)
unexpected_root_entries = sorted(set(root_entries) - ALLOWED_ROOT_ENTRIES)
visible_text = "\n".join(visible_sample + list(os.environ.values()))

network_errno = None
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except PermissionError as exc:
    network_errno = exc.errno
else:
    sock.close()

namespace_errno = None
libc = ctypes.CDLL(None, use_errno=True)

def syscall_errno(number, *args):
    ctypes.set_errno(0)
    result = libc.syscall(number, *args)
    if result >= 0:
        try:
            os.close(result)
        except OSError:
            pass
        return 0
    return ctypes.get_errno()

namespace_errno = syscall_errno(SYS_UNSHARE_X86_64, CLONE_NEWNS)
io_uring_errno = syscall_errno(SYS_IO_URING_SETUP_X86_64, 1, ctypes.c_void_p(0))
new_mount_api_errno = syscall_errno(SYS_FSOPEN_X86_64, ctypes.c_char_p(b"tmpfs"), 0)

def errno_label(value):
    if value == 0:
        return "SUCCESS"
    if value == errno.EPERM:
        return "EPERM"
    return str(value)

checks = {
    "assigned_prompt_stdin_byte_equal": observed_hash == expected_hash,
    "workspace_read_write": workspace_write,
    "repo_root_not_visible": not os.path.exists(repo_root),
    "home_not_visible": not os.path.exists(home_path),
    "delivery_not_visible": not os.path.exists(delivery_path),
    "other_slot_not_visible": not os.path.exists(other_slot_root),
    "root_mount_surface_has_no_unexpected_host_paths": not unexpected_root_entries,
    "environment_is_minimal": dict(os.environ) == EXPECTED_ENV,
    "network_socket_denied_eperm": network_errno == errno.EPERM,
    "namespace_escape_denied_eperm": namespace_errno == errno.EPERM,
    "io_uring_setup_denied_eperm": io_uring_errno == errno.EPERM,
    "new_mount_api_fsopen_denied_eperm": new_mount_api_errno == errno.EPERM,
    "visible_paths_role_tokens_absent": ROLE_RE.search(visible_text) is None,
    "workspace_has_no_git": not os.path.exists("/workspace/.git"),
    "workspace_has_no_prompt_file": not os.path.exists("/workspace/task.md"),
}

print(json.dumps({
    "observed_prompt_sha256": observed_hash,
    "checks": checks,
    "observed": {
        "environment": dict(sorted(os.environ.items())),
        "root_entries": root_entries,
        "visible_path_sample": visible_sample,
        "network_socket_errno": errno_label(network_errno),
        "namespace_escape_errno": errno_label(namespace_errno),
        "io_uring_setup_errno": errno_label(io_uring_errno),
        "new_mount_api_fsopen_errno": errno_label(new_mount_api_errno),
    },
}, sort_keys=True))
"""


class ProbeError(Exception):
    """A fail-closed probe failure."""


def _utc_now() -> str:
    return _dt.datetime.now(_dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_yaml(path: Path) -> dict:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ProbeError(f"YAML document must be an object: {path}")
    return loaded


def _repo_rel(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()


def _load_policy(policy_path: Path) -> dict:
    policy, problems = sandbox.validate_policy(policy_path, REPO_ROOT)
    if problems or policy is None:
        raise ProbeError("; ".join(problems))
    return policy


def _load_plan(policy: dict) -> dict:
    plan_path = REPO_ROOT / policy["isolation_plan_ref"]
    plan, problems = workspace_builder.validate_plan(plan_path, REPO_ROOT)
    if problems or plan is None:
        raise ProbeError("; ".join(problems))
    return plan


def _role_command(expected_hash: str, repo_root: Path, home_path: Path, delivery_path: str, other_slot_root: str) -> list[str]:
    return [
        "/usr/bin/python3",
        "-c",
        DIAGNOSTIC_PROGRAM,
        expected_hash,
        repo_root.as_posix(),
        home_path.as_posix(),
        delivery_path,
        other_slot_root,
    ]


def _run_arm(policy_path: Path, policy: dict, role: str, plan: dict) -> dict:
    slot = plan["slots"][role]
    other = "treatment" if role == "control" else "control"
    expected_hash = slot["payload_sha256"]
    completed = sandbox.run_sandbox(
        policy_path,
        role,
        _role_command(
            expected_hash,
            REPO_ROOT,
            Path.home(),
            slot["delivery_path"],
            plan["slots"][other]["slot_root"],
        ),
        capture_output=True,
        timeout=30,
    )
    stdout = completed.stdout.decode("utf-8", errors="strict")
    stderr = completed.stderr.decode("utf-8", errors="strict")
    if completed.returncode != 0:
        raise ProbeError(f"{role} diagnostic exited {completed.returncode}: {stderr.strip()}")
    try:
        observed = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise ProbeError(f"{role} diagnostic emitted invalid JSON: {exc}") from exc
    checks = observed.get("checks") or {}
    failed = sorted(name for name, value in checks.items() if value is not True)
    if failed:
        raise ProbeError(f"{role} failed boundary checks: {', '.join(failed)}")
    return {
        "slot_id": slot["slot_id"],
        "exit_code": completed.returncode,
        "expected_prompt_sha256": expected_hash,
        "observed_prompt_sha256": observed.get("observed_prompt_sha256"),
        "checks": checks,
        "observed": observed.get("observed") or {},
    }


def run_probe(policy_path: Path, *, generated_at: str | None = None) -> dict:
    policy = _load_policy(policy_path)
    plan = _load_plan(policy)
    runtime_root = Path(policy["runtime_root"])
    if not runtime_root.is_absolute() or runtime_root.as_posix() != plan["runtime_root"]:
        raise ProbeError("runtime_root must match the isolation plan")
    if runtime_root.exists() or runtime_root.is_symlink():
        raise ProbeError(f"canonical runtime root already exists; refusing to replace or delete it: {runtime_root}")

    created = False
    removed = False
    try:
        workspace_builder.materialize(REPO_ROOT / policy["isolation_plan_ref"], runtime_root, REPO_ROOT)
        created = True
        arms = {
            role: _run_arm(policy_path, policy, role, plan)
            for role in workspace_builder.ROLES
        }
    finally:
        if created:
            shutil.rmtree(runtime_root, ignore_errors=False)
            removed = not runtime_root.exists()

    if not removed:
        raise ProbeError(f"failed to remove self-created runtime root: {runtime_root}")

    launcher_ref = policy["launcher_ref"]
    isolation_ref = policy["isolation_plan_ref"]
    return {
        "schema_version": "v1",
        "artifact_type": "model_lab_access_policy_probe",
        "contract_version": "run-004-access-policy-probe.v1",
        "probe_id": "run-004-access-policy-boundary-probe-v1",
        "synthetic_fixture": False,
        "triggered_by": TRIGGERED_BY,
        "generated_at": generated_at or _utc_now(),
        "policy_ref": _repo_rel(policy_path),
        "policy_sha256": _sha256(policy_path),
        "launcher_ref": launcher_ref,
        "launcher_sha256": _sha256(REPO_ROOT / launcher_ref),
        "isolation_plan_ref": isolation_ref,
        "isolation_plan_sha256": _sha256(REPO_ROOT / isolation_ref),
        "materialized_runtime_root": runtime_root.as_posix(),
        "command": {
            "executable": "/usr/bin/python3",
            "argv_only": True,
            "shell_eval_used": False,
            "model_process_started": False,
            "agent_process_started": False,
            "tty": False,
        },
        "cleanup": {
            "canonical_runtime_root_preexisting": False,
            "runtime_root_created_by_probe": True,
            "runtime_root_removed_by_probe": True,
        },
        "arms": arms,
        "non_claims": NON_CLAIMS,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Run the Run-004 access-policy live negative probe.")
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--generated-at", help="RFC-3339 Z timestamp for reproducible fixture generation")
    args = parser.parse_args(argv)
    try:
        result = run_probe(args.policy, generated_at=args.generated_at)
    except (OSError, RuntimeError, UnicodeError, ValueError, ProbeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    output = args.output if args.output.is_absolute() else REPO_ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    print(f"OK boundary_probe={_repo_rel(output) if output.is_relative_to(REPO_ROOT) else output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
