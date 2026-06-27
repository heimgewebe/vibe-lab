#!/usr/bin/env python3
"""Run one future Run-004 arm inside the content-bound access-policy sandbox."""
from __future__ import annotations

import argparse
import ctypes
import ctypes.util
import errno
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
from pathlib import Path, PurePosixPath

import yaml
from jsonschema import Draft202012Validator

import prepare_model_lab_run004_workspaces as workspace_builder

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_POLICY = REPO_ROOT / "experiments/2026-05-31_model-lab-replication-series/artifacts/run-004-access-policy/access-policy.yml"
POLICY_SCHEMA = REPO_ROOT / "schemas/model-lab-access-policy.v1.schema.json"
ROLES = ("control", "treatment")
ROLE_LEAK_RE = re.compile(r"(?i)(?:^|[^a-z0-9])(control|treatment)(?:[^a-z0-9]|$)")
MAX_PROMPT_BYTES = 4 * 1024 * 1024
SANDBOX_ENV = {
    "HOME": "/workspace",
    "LANG": "C.UTF-8",
    "LC_ALL": "C.UTF-8",
    "PATH": "/usr/bin:/bin",
    "TMPDIR": "/tmp",
    "XDG_CACHE_HOME": "/cache",
}
NETWORK_SYSCALLS = (
    "socket", "socketpair", "connect", "bind", "listen", "accept", "accept4",
    "sendto", "sendmsg", "sendmmsg", "recvfrom", "recvmsg", "recvmmsg",
    "shutdown", "getsockname", "getpeername", "setsockopt", "getsockopt",
)
ASYNC_KERNEL_IO_SYSCALLS = (
    "io_uring_setup", "io_uring_enter", "io_uring_register",
)
MOUNT_API_SYSCALLS = (
    "mount", "umount2", "open_tree", "move_mount", "fsopen", "fsconfig",
    "fsmount", "fspick", "mount_setattr", "pivot_root",
)
PRIVILEGED_SYSCALLS = (
    *MOUNT_API_SYSCALLS, "chroot", "setns", "unshare", "ptrace", "bpf",
    "perf_event_open", "keyctl", "add_key", "request_key", "open_by_handle_at",
    "name_to_handle_at",
)
DENIED_SYSCALLS = NETWORK_SYSCALLS + ASYNC_KERNEL_IO_SYSCALLS + PRIVILEGED_SYSCALLS


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _schema_sort_key(error):
    return tuple(str(part) for part in error.absolute_path), error.message


def _safe_repo_file(raw: str, repo_root: Path) -> Path | None:
    resolved, code = workspace_builder.readiness.resolve_repo_relative_path(raw, repo_root, must_exist=True)
    if code is not None or resolved is None or not resolved.is_file():
        return None
    if _has_symlink_component(resolved, repo_root):
        return None
    return resolved


def _has_symlink_component(path: Path, root: Path) -> bool:
    """Return true if any path component below root is a symlink."""
    try:
        root_resolved = root.resolve(strict=True)
        candidate = path if path.is_absolute() else root_resolved / path
        relative = candidate.relative_to(root_resolved)
    except (OSError, RuntimeError, ValueError):
        return True
    current = root_resolved
    for component in relative.parts:
        if component in ("", ".", ".."):
            return True
        current = current / component
        try:
            if stat.S_ISLNK(os.lstat(current).st_mode):
                return True
        except OSError:
            return True
    return False


def _safe_policy_path(policy_path: Path, repo_root: Path) -> Path | None:
    try:
        root = repo_root.resolve(strict=True)
        candidate = policy_path if policy_path.is_absolute() else root / policy_path
        candidate.relative_to(root)
    except (OSError, RuntimeError, ValueError):
        return None
    if _has_symlink_component(candidate, root):
        return None
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(root)
    except (OSError, RuntimeError, ValueError):
        return None
    if resolved != candidate or not resolved.is_file():
        return None
    return resolved


def _version_tuple(raw: str) -> tuple[int, ...]:
    match = re.search(r"(\d+(?:\.\d+)+)", raw)
    return tuple(int(part) for part in match.group(1).split(".")) if match else ()


def validate_policy(policy_path: Path, repo_root: Path = REPO_ROOT) -> tuple[dict | None, list[str]]:
    problems: list[str] = []
    resolved = _safe_policy_path(policy_path, repo_root)
    if resolved is None:
        return None, ["policy must be a safe existing repository file"]
    try:
        data = yaml.safe_load(resolved.read_text(encoding="utf-8"))
        schema = json.loads(POLICY_SCHEMA.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError, yaml.YAMLError) as exc:
        return None, [f"policy or schema is invalid/unreadable: {exc}"]
    for error in sorted(Draft202012Validator(schema).iter_errors(data), key=_schema_sort_key):
        where = ".".join(str(part) for part in error.absolute_path) or "$"
        problems.append(f"schema {where}: {error.message}")
    if not isinstance(data, dict):
        return None, problems or ["policy must be a mapping"]
    rel = resolved.relative_to(repo_root.resolve()).as_posix()
    if data.get("synthetic_fixture") is True and not rel.startswith("tests/fixtures/"):
        problems.append("synthetic policy is forbidden outside tests/fixtures")
    launcher_path = _safe_repo_file(str(data.get("launcher_ref", "")), repo_root)
    if launcher_path is None:
        problems.append("launcher_ref must be a safe existing repository file")
    elif sha256(launcher_path) != data.get("launcher_sha256"):
        problems.append("launcher_sha256 mismatch")
    elif data.get("synthetic_fixture") is not True and launcher_path.resolve() != Path(__file__).resolve():
        problems.append("real policy must bind this exact launcher path")
    isolation_path = _safe_repo_file(str(data.get("isolation_plan_ref", "")), repo_root)
    isolation = None
    if isolation_path is None:
        problems.append("isolation_plan_ref must be a safe existing repository file")
    else:
        if sha256(isolation_path) != data.get("isolation_plan_sha256"):
            problems.append("isolation_plan_sha256 mismatch")
        isolation, isolation_problems = workspace_builder.validate_plan(isolation_path, repo_root)
        problems.extend(f"isolation plan: {problem}" for problem in isolation_problems)
    backend = data.get("backend") or {}
    expected_backend = {
        "executable": "/usr/bin/bwrap",
        "host_filesystem_base_mounted": False,
        "network_enforcement": "libseccomp-errno-eperm",
        "namespace_mode": "unshare-all-share-net-seccomp-network-deny",
        "share_net_required_due_to_netlink_route": True,
        "drop_capabilities": True,
        "clear_environment": True,
        "new_session": True,
        "die_with_parent": True,
        "close_fds": True,
        "argv_only": True,
        "shell_eval_forbidden": True,
        "bind_implementation": "directory-fd-no-symlink-components",
        "prompt_delivery": "stdin-only",
        "unset_pwd": True,
        "pwd_removed_by_argv_wrapper": True,
        "environment_wrapper": ["/usr/bin/env", "-u", "PWD", "--"],
        "tty": False,
    }
    for field, value in expected_backend.items():
        if backend.get(field) != value:
            problems.append(f"backend.{field} must equal {value!r}")
    if tuple(backend.get("denied_syscalls") or ()) != DENIED_SYSCALLS:
        problems.append("backend.denied_syscalls must equal the canonical deny set")
    if data.get("sandbox_environment") != SANDBOX_ENV:
        problems.append("sandbox_environment must equal the canonical minimal environment")
    if data.get("allowed_command_roots") != ["/usr/bin", "/bin"]:
        problems.append("allowed_command_roots must be exactly /usr/bin and /bin")
    if data.get("required_read_only_roots") != ["/usr"]:
        problems.append("required_read_only_roots must contain only /usr")
    if data.get("optional_read_only_roots") != ["/lib", "/lib64", "/etc/ld.so.cache"]:
        problems.append("optional_read_only_roots must equal the canonical runtime compatibility set")
    if isolation is not None:
        if data.get("runtime_root") != isolation.get("runtime_root"):
            problems.append("runtime_root must match the isolation plan")
        policy_arms = data.get("arms") or {}
        slots = isolation.get("slots") or {}
        for role in ROLES:
            arm = policy_arms.get(role) or {}
            slot = slots.get(role) or {}
            expected = {
                "slot_id": slot.get("slot_id"),
                "workspace_source": slot.get("workspace_path"),
                "temp_source": slot.get("temp_dir"),
                "cache_source": slot.get("cache_dir"),
                "delivery_source": slot.get("delivery_path"),
                "payload_sha256": slot.get("payload_sha256"),
                "workspace_target": "/workspace",
                "temp_target": "/tmp",
                "cache_target": "/cache",
            }
            for field, expected_value in expected.items():
                if arm.get(field) != expected_value:
                    problems.append(f"arms.{role}.{field} must match isolation plan/canonical target")
            for field in ("slot_id", "workspace_source", "temp_source", "cache_source", "delivery_source"):
                value = arm.get(field)
                if isinstance(value, str) and ROLE_LEAK_RE.search(value):
                    problems.append(f"arms.{role}.{field} leaks a role token")
        if policy_arms.get("control") == policy_arms.get("treatment"):
            problems.append("policy arms must be distinct")
    return (data if not problems else None), problems


def _open_directory_no_symlinks(path: Path) -> int:
    if not path.is_absolute():
        raise ValueError(f"directory path must be absolute: {path}")
    flags = os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_CLOEXEC", 0)
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    current = os.open("/", flags)
    try:
        for component in path.parts[1:]:
            if component in ("", ".", ".."):
                raise ValueError(f"non-canonical directory component: {path}")
            next_fd = os.open(component, flags | nofollow, dir_fd=current)
            os.close(current)
            current = next_fd
        if not stat.S_ISDIR(os.fstat(current).st_mode):
            raise ValueError(f"not a directory: {path}")
        return current
    except Exception:
        os.close(current)
        raise


def _read_prompt_no_symlinks(path: Path, expected_sha256: str) -> bytes:
    parent_fd = _open_directory_no_symlinks(path.parent)
    fd = None
    try:
        fd = os.open(path.name, os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0), dir_fd=parent_fd)
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise ValueError(f"prompt is not a regular file: {path}")
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(fd, 65536)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_PROMPT_BYTES:
                raise ValueError("assigned prompt exceeds the maximum supported size")
            chunks.append(chunk)
        payload = b"".join(chunks)
    finally:
        if fd is not None:
            os.close(fd)
        os.close(parent_fd)
    if hashlib.sha256(payload).hexdigest() != expected_sha256:
        raise ValueError("assigned prompt hash mismatch")
    return payload


def _seccomp_library(name: str):
    resolved = ctypes.util.find_library("seccomp")
    if resolved is None:
        raise RuntimeError("libseccomp is unavailable; refusing unsandboxed execution")
    if name not in (resolved, "libseccomp.so.2"):
        raise RuntimeError("policy requests an unexpected seccomp library")
    library = ctypes.CDLL(resolved, use_errno=True)
    library.seccomp_init.argtypes = [ctypes.c_uint32]
    library.seccomp_init.restype = ctypes.c_void_p
    library.seccomp_rule_add.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_int, ctypes.c_uint]
    library.seccomp_rule_add.restype = ctypes.c_int
    library.seccomp_syscall_resolve_name.argtypes = [ctypes.c_char_p]
    library.seccomp_syscall_resolve_name.restype = ctypes.c_int
    library.seccomp_export_bpf.argtypes = [ctypes.c_void_p, ctypes.c_int]
    library.seccomp_export_bpf.restype = ctypes.c_int
    library.seccomp_release.argtypes = [ctypes.c_void_p]
    return library


def build_seccomp_bpf(policy: dict) -> int:
    library = _seccomp_library(policy["backend"]["seccomp_library"])
    context = library.seccomp_init(0x7FFF0000)
    if not context:
        raise RuntimeError("seccomp_init failed")
    fd = os.memfd_create("run004-seccomp", os.MFD_CLOEXEC)
    try:
        for name in policy["backend"]["denied_syscalls"]:
            number = library.seccomp_syscall_resolve_name(name.encode("ascii"))
            if number < 0:
                raise RuntimeError(f"required seccomp syscall is unknown: {name}")
            result = library.seccomp_rule_add(context, 0x00050000 | errno.EPERM, number, 0)
            if result != 0:
                raise OSError(-result, f"seccomp_rule_add failed for {name}")
        result = library.seccomp_export_bpf(context, fd)
        if result != 0:
            raise OSError(-result, "seccomp_export_bpf failed")
    except Exception:
        os.close(fd)
        raise
    finally:
        library.seccomp_release(context)
    os.lseek(fd, 0, os.SEEK_SET)
    return fd


def _validate_command(command: list[str], policy: dict) -> None:
    if not command or any(not isinstance(item, str) or not item or "\0" in item for item in command):
        raise ValueError("command must be a non-empty NUL-free argv array")
    executable = Path(command[0])
    if not executable.is_absolute():
        raise ValueError("sandbox command must use an absolute executable path")
    posix = PurePosixPath(command[0])
    if any(part in ("", ".", "..") for part in posix.parts):
        raise ValueError("sandbox executable path must be canonical")
    roots = [Path(item) for item in policy["allowed_command_roots"]]
    if not any(executable == root or root in executable.parents for root in roots):
        raise ValueError("sandbox executable is outside allowed command roots")


def build_bwrap_argv(policy: dict, arm: dict, command: list[str], directory_fds: tuple[int, int, int], seccomp_fd: int) -> list[str]:
    _validate_command(command, policy)
    workspace_fd, temp_fd, cache_fd = directory_fds
    argv = [
        policy["backend"]["executable"], "--unshare-all", "--share-net",
        "--die-with-parent", "--new-session", "--cap-drop", "ALL", "--clearenv",
        "--hostname", "run004-sandbox", "--ro-bind", "/usr", "/usr",
        "--symlink", "usr/bin", "/bin", "--ro-bind-try", "/lib", "/lib",
        "--ro-bind-try", "/lib64", "/lib64", "--dir", "/etc",
        "--ro-bind-try", "/etc/ld.so.cache", "/etc/ld.so.cache",
        "--proc", "/proc", "--dev", "/dev",
        "--dir", arm["workspace_target"], "--bind-fd", str(workspace_fd), arm["workspace_target"],
        "--dir", arm["temp_target"], "--bind-fd", str(temp_fd), arm["temp_target"],
        "--dir", arm["cache_target"], "--bind-fd", str(cache_fd), arm["cache_target"],
    ]
    for key, value in policy["sandbox_environment"].items():
        argv.extend(("--setenv", key, value))
    argv.extend(("--chdir", "/workspace", "--unsetenv", "PWD", "--seccomp", str(seccomp_fd), "--"))
    return argv + policy["backend"]["environment_wrapper"] + command


def run_sandbox(policy_path: Path, arm_name: str, command: list[str], *, repo_root: Path = REPO_ROOT, capture_output: bool = False, timeout: int | None = None) -> subprocess.CompletedProcess:
    policy, problems = validate_policy(policy_path, repo_root)
    if problems or policy is None:
        raise ValueError("; ".join(problems))
    if arm_name not in ROLES:
        raise ValueError("unknown arm")
    executable = Path(policy["backend"]["executable"])
    if not executable.is_file() or executable.is_symlink():
        raise RuntimeError("bubblewrap executable is unavailable or unsafe")
    version = subprocess.run([str(executable), "--version"], capture_output=True, text=True, encoding="utf-8", errors="strict", check=False, timeout=10)
    if version.returncode != 0 or _version_tuple(version.stdout) < _version_tuple(policy["backend"]["minimum_version"]):
        raise RuntimeError("bubblewrap version does not satisfy the policy")
    arm = policy["arms"][arm_name]
    prompt = _read_prompt_no_symlinks(Path(arm["delivery_source"]), arm["payload_sha256"])
    directory_fds: list[int] = []
    seccomp_fd = None
    try:
        for field in ("workspace_source", "temp_source", "cache_source"):
            directory_fds.append(_open_directory_no_symlinks(Path(arm[field])))
        seccomp_fd = build_seccomp_bpf(policy)
        argv = build_bwrap_argv(policy, arm, command, tuple(directory_fds), seccomp_fd)
        return subprocess.run(
            argv, input=prompt, capture_output=capture_output, timeout=timeout, check=False,
            env={"LANG": "C.UTF-8", "LC_ALL": "C.UTF-8", "PATH": "/usr/bin:/bin"},
            close_fds=True, pass_fds=tuple(directory_fds) + (seccomp_fd,),
        )
    finally:
        if seccomp_fd is not None:
            os.close(seccomp_fd)
        for fd in directory_fds:
            os.close(fd)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--arm", choices=ROLES)
    parser.add_argument("--check-policy", action="store_true")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    policy, problems = validate_policy(args.policy, REPO_ROOT)
    if problems or policy is None:
        for problem in problems:
            print(f"ERROR: {problem}")
        return 1
    if args.check_policy:
        print(f"OK policy_id={policy['policy_id']} backend={policy['backend']['id']} arms=2")
        return 0
    command = list(args.command)
    if command[:1] == ["--"]:
        command = command[1:]
    if args.arm is None or not command:
        parser.error("--arm and a command after -- are required unless --check-policy is used")
    try:
        completed = run_sandbox(args.policy, args.arm, command, timeout=None)
    except (OSError, RuntimeError, UnicodeError, ValueError, subprocess.SubprocessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
