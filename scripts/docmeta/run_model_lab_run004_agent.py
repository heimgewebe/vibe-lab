#!/usr/bin/env python3
"""Content-bound local model broker for future Run-004 execution.

This program does not authorize or start Run-004 on its own. It exposes a small,
validated tool surface to one exact local Ollama model and delegates process
execution to the already-bound Run-004 sandbox launcher.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import posixpath
import stat
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Protocol

import run_model_lab_run004_sandbox as sandbox

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_POLICY = REPO_ROOT / "experiments/2026-05-31_model-lab-replication-series/artifacts/run-004-access-policy/access-policy.yml"
DEFAULT_PROTOCOL = REPO_ROOT / "experiments/2026-05-31_model-lab-replication-series/artifacts/run-004-runtime-binding/agent-protocol.md"
PROTOCOL_SHA256 = "dd5cf3d5bc43ed592ae6993b5a66f996a09bf3949360acc742be25defe45469e"
MODEL_ALIAS = "qwen2.5-coder:14b"
MODEL_MANIFEST_SHA256 = "9ec8897f747e246e970bc5cfdda85d22f1123dc2e3d34978a010a75968716849"
MODEL_BLOB_SHA256 = "ac9bc7a69dab38da1c790838955f1293420b55ab555ef6b4615efa1c1507b1ed"
MODEL_MANIFEST = Path("/usr/share/ollama/.ollama/models/manifests/registry.ollama.ai/library/qwen2.5-coder/14b")
OLLAMA_ENDPOINT = "http://127.0.0.1:11434/api/chat"
OLLAMA_KEEP_ALIVE = "10m"
AGENT_VERSION = "run-004-local-tool-broker.v1"
MAX_TOOL_TURNS = 64
MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_TOOL_OUTPUT_BYTES = 2 * 1024 * 1024
MAX_TOOL_DECISION_BYTES = 64 * 1024
MAX_LIST_ENTRIES = 4096
MAX_COMMAND_SECONDS = 180
SAMPLING = {
    "temperature": 0,
    "top_p": 1,
    "top_k": 1,
    "num_predict": 4096,
    "seed": 424004,
    "num_ctx": 16384,
}
SHELL_EXECUTABLES = {
    "/bin/bash",
    "/bin/dash",
    "/bin/sh",
    "/usr/bin/bash",
    "/usr/bin/dash",
    "/usr/bin/sh",
}
SHELL_EXECUTABLE_NAMES = {"bash", "dash", "sh"}
ENV_EXECUTABLES = {"/bin/env", "/usr/bin/env"}
INLINE_EVAL_EXECUTABLE_NAMES = {"node", "python", "python3", "perl", "ruby", "php", "lua"}
INLINE_EVAL_FLAGS = {"-c", "-e", "-p", "--eval"}


class BrokerError(RuntimeError):
    """Fail-closed broker error."""


class ChatTransport(Protocol):
    def chat(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> dict[str, Any]: ...


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def verify_model_installation(manifest_path: Path = MODEL_MANIFEST) -> dict[str, Any]:
    try:
        if manifest_path.is_symlink() or not manifest_path.is_file():
            raise BrokerError("model manifest must be a regular non-symlink file")
        if sha256_file(manifest_path) != MODEL_MANIFEST_SHA256:
            raise BrokerError("model manifest hash mismatch")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise BrokerError(f"model manifest is unreadable or invalid: {exc}") from exc
    model_layers = [
        item for item in manifest.get("layers", [])
        if isinstance(item, dict) and item.get("mediaType") == "application/vnd.ollama.image.model"
    ]
    if len(model_layers) != 1 or model_layers[0].get("digest") != f"sha256:{MODEL_BLOB_SHA256}":
        raise BrokerError("model blob digest mismatch")
    blob_path = manifest_path.parents[4] / "blobs" / f"sha256-{MODEL_BLOB_SHA256}"
    if blob_path.is_symlink() or not blob_path.is_file():
        raise BrokerError("model blob is unavailable or unsafe")
    if sha256_file(blob_path) != MODEL_BLOB_SHA256:
        raise BrokerError("model blob content hash mismatch")
    return {
        "manifest_sha256": MODEL_MANIFEST_SHA256,
        "model_blob_sha256": MODEL_BLOB_SHA256,
        "model_blob_size": model_layers[0].get("size"),
    }


def _path_parts(raw: str, *, allow_root: bool = False) -> tuple[str, ...]:
    if not isinstance(raw, str) or "\x00" in raw or "\\" in raw:
        raise BrokerError("tool path must be a NUL-free POSIX relative path")
    path = Path(raw)
    if path.is_absolute():
        raise BrokerError("absolute tool paths are forbidden")
    parts = path.parts
    if not parts and allow_root:
        return ()
    if not parts or any(part in ("", ".", "..") for part in parts):
        raise BrokerError("tool path must be canonical and remain inside the workspace")
    return tuple(parts)


def _open_directory(root_fd: int, parts: tuple[str, ...]) -> int:
    current = os.dup(root_fd)
    flags = os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        for part in parts:
            next_fd = os.open(part, flags, dir_fd=current)
            os.close(current)
            current = next_fd
        return current
    except Exception:
        os.close(current)
        raise


def _open_parent(root_fd: int, parts: tuple[str, ...]) -> tuple[int, str]:
    if not parts:
        raise BrokerError("workspace root cannot be used as a file target")
    return _open_directory(root_fd, parts[:-1]), parts[-1]


class WorkspaceTools:
    def __init__(self, workspace: Path, policy_path: Path, arm: str) -> None:
        if not workspace.is_absolute():
            raise BrokerError("workspace path must be absolute")
        self.workspace = workspace
        self.policy_path = policy_path
        self.arm = arm
        self.root_fd = sandbox._open_directory_no_symlinks(workspace)

    def close(self) -> None:
        if self.root_fd >= 0:
            os.close(self.root_fd)
            self.root_fd = -1

    def __enter__(self) -> "WorkspaceTools":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def list_files(self, path: str = "") -> dict[str, Any]:
        parts = _path_parts(path, allow_root=True)
        directory_fd = _open_directory(self.root_fd, parts)
        try:
            names = sorted(os.listdir(directory_fd))
            if len(names) > MAX_LIST_ENTRIES:
                raise BrokerError("directory entry limit exceeded")
            entries = []
            for name in names:
                info = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
                if stat.S_ISLNK(info.st_mode):
                    kind = "symlink"
                elif stat.S_ISDIR(info.st_mode):
                    kind = "directory"
                elif stat.S_ISREG(info.st_mode):
                    kind = "file"
                else:
                    kind = "other"
                entries.append({"name": name, "kind": kind, "size": info.st_size})
            return {"path": path, "entries": entries}
        finally:
            os.close(directory_fd)

    def read_file(self, path: str) -> dict[str, Any]:
        parts = _path_parts(path)
        parent_fd, name = _open_parent(self.root_fd, parts)
        fd = None
        try:
            fd = os.open(
                name,
                os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
                dir_fd=parent_fd,
            )
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode):
                raise BrokerError("read_file target must be a regular file")
            if info.st_size > MAX_FILE_BYTES:
                raise BrokerError("read_file size limit exceeded")
            chunks: list[bytes] = []
            total = 0
            while chunk := os.read(fd, 65536):
                total += len(chunk)
                if total > MAX_FILE_BYTES:
                    raise BrokerError("read_file size limit exceeded")
                chunks.append(chunk)
            content = b"".join(chunks).decode("utf-8", errors="strict")
            return {"path": path, "content": content}
        except OSError as exc:
            raise BrokerError("read_file target is unavailable or unsafe") from exc
        except UnicodeError as exc:
            raise BrokerError("read_file requires valid UTF-8 text") from exc
        finally:
            if fd is not None:
                os.close(fd)
            os.close(parent_fd)

    def write_file(self, path: str, content: str) -> dict[str, Any]:
        if not isinstance(content, str):
            raise BrokerError("write_file content must be text")
        payload = content.encode("utf-8")
        if len(payload) > MAX_FILE_BYTES:
            raise BrokerError("write_file size limit exceeded")
        parts = _path_parts(path)
        parent_fd, name = _open_parent(self.root_fd, parts)
        temporary = f".{name}.run004-{os.getpid()}-{os.urandom(6).hex()}.tmp"
        fd = None
        try:
            try:
                current = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
            except FileNotFoundError:
                current = None
            if current is not None and not stat.S_ISREG(current.st_mode):
                raise BrokerError("write_file refuses non-regular existing targets")
            fd = os.open(
                temporary,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_CLOEXEC", 0),
                0o600,
                dir_fd=parent_fd,
            )
            view = memoryview(payload)
            while view:
                written = os.write(fd, view)
                view = view[written:]
            os.fsync(fd)
            os.close(fd)
            fd = None
            os.replace(temporary, name, src_dir_fd=parent_fd, dst_dir_fd=parent_fd)
            os.fsync(parent_fd)
            return {"path": path, "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}
        finally:
            if fd is not None:
                os.close(fd)
            try:
                os.unlink(temporary, dir_fd=parent_fd)
            except FileNotFoundError:
                pass
            os.close(parent_fd)

    def make_directory(self, path: str) -> dict[str, Any]:
        parts = _path_parts(path)
        current = os.dup(self.root_fd)
        flags = os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
        try:
            for part in parts:
                try:
                    os.mkdir(part, 0o700, dir_fd=current)
                except FileExistsError:
                    pass
                next_fd = os.open(part, flags, dir_fd=current)
                os.close(current)
                current = next_fd
            return {"path": path, "created": True}
        finally:
            os.close(current)

    def delete_path(self, path: str) -> dict[str, Any]:
        parts = _path_parts(path)
        parent_fd, name = _open_parent(self.root_fd, parts)
        try:
            info = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
            if stat.S_ISREG(info.st_mode):
                os.unlink(name, dir_fd=parent_fd)
            elif stat.S_ISDIR(info.st_mode):
                os.rmdir(name, dir_fd=parent_fd)
            else:
                raise BrokerError("delete_path accepts only regular files or empty directories")
            return {"path": path, "deleted": True}
        finally:
            os.close(parent_fd)

    def run_command(self, argv: list[str], timeout_seconds: int = MAX_COMMAND_SECONDS) -> dict[str, Any]:
        if not isinstance(argv, list) or not argv or any(not isinstance(item, str) for item in argv):
            raise BrokerError("run_command requires a non-empty string argv array")
        executable_name = posixpath.basename(argv[0])
        if argv[0] in SHELL_EXECUTABLES or executable_name in SHELL_EXECUTABLE_NAMES:
            raise BrokerError("shell interpreters are forbidden in run_command")
        if argv[0] in ENV_EXECUTABLES or executable_name == "env":
            raise BrokerError("env trampolines are forbidden in run_command")
        if executable_name in INLINE_EVAL_EXECUTABLE_NAMES and any(arg in INLINE_EVAL_FLAGS for arg in argv[1:]):
            raise BrokerError("inline code evaluation flags are forbidden in run_command")
        if not isinstance(timeout_seconds, int) or not 1 <= timeout_seconds <= MAX_COMMAND_SECONDS:
            raise BrokerError("run_command timeout is outside the allowed range")
        sandbox._validate_command(argv, self._validated_policy())
        try:
            completed = sandbox.run_sandbox(
                self.policy_path,
                self.arm,
                argv,
                repo_root=REPO_ROOT,
                capture_output=True,
                timeout=timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            raise BrokerError("run_command timed out") from exc
        stdout = completed.stdout or b""
        stderr = completed.stderr or b""
        if len(stdout) + len(stderr) > MAX_TOOL_OUTPUT_BYTES:
            raise BrokerError("run_command output limit exceeded")
        return {
            "argv": argv,
            "returncode": completed.returncode,
            "stdout": stdout.decode("utf-8", errors="replace"),
            "stderr": stderr.decode("utf-8", errors="replace"),
        }

    def _validated_policy(self) -> dict[str, Any]:
        policy, problems = sandbox.validate_policy(self.policy_path, REPO_ROOT)
        if problems or policy is None:
            raise BrokerError("access policy is invalid: " + "; ".join(problems))
        return policy


class OllamaTransport:
    def __init__(self, endpoint: str = OLLAMA_ENDPOINT) -> None:
        if endpoint != OLLAMA_ENDPOINT:
            raise BrokerError("only the bound Ollama loopback endpoint is allowed")
        self.endpoint = endpoint

    def chat(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> dict[str, Any]:
        payload = {
            "model": MODEL_ALIAS,
            "messages": messages,
            "tools": tools,
            "stream": False,
            "keep_alive": OLLAMA_KEEP_ALIVE,
            "options": dict(SAMPLING),
        }
        request = urllib.request.Request(
            self.endpoint,
            data=json.dumps(payload, ensure_ascii=True, separators=(",", ":")).encode("utf-8"),
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=300) as response:
                result = json.load(response)
        except (OSError, TimeoutError, urllib.error.URLError, ValueError) as exc:
            raise BrokerError(f"Ollama request failed closed: {exc}") from exc
        if result.get("model") != MODEL_ALIAS or result.get("done") is not True:
            raise BrokerError("Ollama response identity or completion status mismatch")
        message = result.get("message")
        if not isinstance(message, dict):
            raise BrokerError("Ollama response has no valid message")
        return message


def tool_definitions() -> list[dict[str, Any]]:
    def definition(name: str, description: str, properties: dict[str, Any], required: list[str]) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": properties,
                    "required": required,
                },
            },
        }

    path = {"type": "string", "minLength": 1}
    return [
        definition("list_files", "List one workspace directory.", {"path": {"type": "string"}}, []),
        definition("read_file", "Read one UTF-8 workspace file.", {"path": path}, ["path"]),
        definition("write_file", "Atomically write one UTF-8 workspace file.", {"path": path, "content": {"type": "string"}}, ["path", "content"]),
        definition("make_directory", "Create one workspace directory tree.", {"path": path}, ["path"]),
        definition("delete_path", "Delete one regular file or empty directory.", {"path": path}, ["path"]),
        definition(
            "run_command",
            "Run one argv-only command in the bound workspace sandbox.",
            {
                "argv": {"type": "array", "minItems": 1, "items": {"type": "string", "minLength": 1}},
                "timeout_seconds": {"type": "integer", "minimum": 1, "maximum": MAX_COMMAND_SECONDS},
            },
            ["argv"],
        ),
    ]


def _tool_parameter_schemas() -> dict[str, dict[str, Any]]:
    return {
        item["function"]["name"]: item["function"]["parameters"]
        for item in tool_definitions()
    }


def validate_tool_arguments(name: str, arguments: Any) -> dict[str, Any]:
    schema = _tool_parameter_schemas().get(name)
    if schema is None:
        raise BrokerError(f"unknown tool: {name}")
    if not isinstance(arguments, dict):
        raise BrokerError("tool arguments must be an object")
    properties = schema["properties"]
    observed = set(arguments)
    extras = sorted(observed - set(properties))
    missing = sorted(set(schema["required"]) - observed)
    if extras:
        raise BrokerError(f"invalid arguments for {name}: unexpected keys: {', '.join(extras)}")
    if missing:
        raise BrokerError(f"invalid arguments for {name}: missing keys: {', '.join(missing)}")
    for key, value in arguments.items():
        rule = properties[key]
        expected = rule.get("type")
        if expected == "string":
            if not isinstance(value, str):
                raise BrokerError(f"invalid arguments for {name}: {key} must be a string")
            if len(value) < int(rule.get("minLength", 0)):
                raise BrokerError(f"invalid arguments for {name}: {key} is too short")
        elif expected == "integer":
            if isinstance(value, bool) or not isinstance(value, int):
                raise BrokerError(f"invalid arguments for {name}: {key} must be an integer")
            if "minimum" in rule and value < int(rule["minimum"]):
                raise BrokerError(f"invalid arguments for {name}: {key} is below the minimum")
            if "maximum" in rule and value > int(rule["maximum"]):
                raise BrokerError(f"invalid arguments for {name}: {key} exceeds the maximum")
        elif expected == "array":
            if not isinstance(value, list):
                raise BrokerError(f"invalid arguments for {name}: {key} must be an array")
            if len(value) < int(rule.get("minItems", 0)):
                raise BrokerError(f"invalid arguments for {name}: {key} has too few items")
            item_rule = rule.get("items") or {}
            if item_rule.get("type") == "string":
                for item in value:
                    if not isinstance(item, str) or len(item) < int(item_rule.get("minLength", 0)):
                        raise BrokerError(f"invalid arguments for {name}: {key} items must be non-empty strings")
        else:
            raise BrokerError(f"unsupported argument schema for {name}.{key}")
    return arguments


def _decode_argument_object(raw: Any) -> dict[str, Any]:
    if isinstance(raw, str):
        if len(raw.encode("utf-8")) > MAX_TOOL_DECISION_BYTES:
            raise BrokerError("tool arguments JSON exceeds the size limit")
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise BrokerError("tool arguments JSON is invalid") from exc
    if not isinstance(raw, dict):
        raise BrokerError("tool arguments must be an object")
    return raw


def normalize_tool_calls(message: dict[str, Any]) -> list[dict[str, Any]]:
    if not isinstance(message, dict):
        raise BrokerError("agent response message must be an object")
    content = message.get("content")
    content_present = isinstance(content, str) and bool(content.strip())
    native = message.get("tool_calls")
    native_present = native not in (None, [])
    if native_present:
        if content_present:
            raise BrokerError("agent response mixes native and textual tool calls")
        if not isinstance(native, list):
            raise BrokerError("tool_calls must be a list")
        normalized = []
        for call in native:
            if not isinstance(call, dict) or set(call) != {"function"}:
                raise BrokerError("native tool call has an unsupported shape")
            function = call.get("function")
            if not isinstance(function, dict) or set(function) != {"name", "arguments"}:
                raise BrokerError("native tool function has an unsupported shape")
            name = function.get("name")
            if not isinstance(name, str):
                raise BrokerError("tool call has no valid name")
            arguments = validate_tool_arguments(name, _decode_argument_object(function.get("arguments")))
            normalized.append({"function": {"name": name, "arguments": arguments}})
        return normalized
    if native is not None and not isinstance(native, list):
        raise BrokerError("tool_calls must be a list")
    if not content_present:
        return []
    assert isinstance(content, str)
    if len(content.encode("utf-8")) > MAX_TOOL_DECISION_BYTES:
        raise BrokerError("agent content exceeds the tool-decision size limit")
    stripped = content.strip()
    try:
        action = json.loads(stripped)
    except json.JSONDecodeError as exc:
        if any(marker in stripped for marker in ("```", "<tool_call", "{", "}")):
            raise BrokerError("textual tool action must be exactly one JSON object") from exc
        return []
    if not isinstance(action, dict) or set(action) != {"name", "arguments"}:
        raise BrokerError("textual tool action must contain exactly name and arguments")
    name = action.get("name")
    if not isinstance(name, str):
        raise BrokerError("textual tool action name must be a string")
    arguments = validate_tool_arguments(name, action.get("arguments"))
    return [{"function": {"name": name, "arguments": arguments}}]


def execute_tool(tools: WorkspaceTools, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    arguments = validate_tool_arguments(name, _decode_argument_object(arguments))
    methods = {
        "list_files": tools.list_files,
        "read_file": tools.read_file,
        "write_file": tools.write_file,
        "make_directory": tools.make_directory,
        "delete_path": tools.delete_path,
        "run_command": tools.run_command,
    }
    method = methods.get(name)
    if method is None:
        raise BrokerError(f"unknown tool: {name}")
    try:
        return method(**arguments)
    except TypeError as exc:
        raise BrokerError(f"invalid arguments for {name}: {exc}") from exc


def run_agent(
    prompt: str,
    protocol: str,
    tools: WorkspaceTools,
    transport: ChatTransport,
    *,
    max_turns: int = MAX_TOOL_TURNS,
) -> str:
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": protocol},
        {"role": "user", "content": prompt},
    ]
    definitions = tool_definitions()
    for _ in range(max_turns):
        message = transport.chat(messages, definitions)
        messages.append(message)
        calls = normalize_tool_calls(message)
        if calls:
            for call in calls:
                function = call["function"]
                name = function["name"]
                arguments = function["arguments"]
                result = execute_tool(tools, name, arguments)
                messages.append({"role": "tool", "content": json.dumps(result, sort_keys=True, ensure_ascii=True)})
            continue
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise BrokerError("agent returned neither tool calls nor final content")
        return content
    raise BrokerError("maximum tool turns exceeded")


def _load_protocol(path: Path = DEFAULT_PROTOCOL) -> str:
    if path != DEFAULT_PROTOCOL:
        raise BrokerError("agent protocol override is forbidden")
    if path.is_symlink() or not path.is_file():
        raise BrokerError("agent protocol must be a regular non-symlink file")
    try:
        if sha256_file(path) != PROTOCOL_SHA256:
            raise BrokerError("agent protocol hash mismatch")
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise BrokerError(f"agent protocol is unreadable: {exc}") from exc
    if not text.strip():
        raise BrokerError("agent protocol is empty")
    return text


def _assigned_prompt(policy: dict[str, Any], arm: str) -> str:
    arm_data = (policy.get("arms") or {}).get(arm) or {}
    payload = sandbox._read_prompt_no_symlinks(
        Path(str(arm_data.get("delivery_source", ""))),
        str(arm_data.get("payload_sha256", "")),
    )
    try:
        return payload.decode("utf-8", errors="strict")
    except UnicodeError as exc:
        raise BrokerError("assigned prompt is not valid UTF-8") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", choices=("control", "treatment"), required=True)
    parser.add_argument("--check-runtime", action="store_true")
    args = parser.parse_args(argv)
    try:
        identity = verify_model_installation()
        policy, problems = sandbox.validate_policy(DEFAULT_POLICY, REPO_ROOT)
        if problems or policy is None:
            raise BrokerError("access policy is invalid: " + "; ".join(problems))
        protocol = _load_protocol()
        if args.check_runtime:
            print(json.dumps({"agent_version": AGENT_VERSION, "model": MODEL_ALIAS, **identity}, sort_keys=True))
            return 0
        arm_data = (policy.get("arms") or {}).get(args.arm) or {}
        prompt = _assigned_prompt(policy, args.arm)
        with WorkspaceTools(Path(str(arm_data.get("workspace_source", ""))), DEFAULT_POLICY, args.arm) as tools:
            final = run_agent(prompt, protocol, tools, OllamaTransport())
        sys.stdout.write(final.rstrip("\n") + "\n")
        return 0
    except (BrokerError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
