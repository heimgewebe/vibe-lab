#!/usr/bin/env python3
"""Regression tests for the Run-004 access-policy sandbox bundle."""

from __future__ import annotations

import atexit
import hashlib
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

import yaml

import probe_model_lab_run004_access_policy as probe
import run_model_lab_run004_sandbox as sandbox
import validate_model_lab_run004_access_policy as validator

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
FIXROOT = REPO_ROOT / "tests" / "fixtures" / "model_lab_execution_readiness"
REAL_POLICY = validator.DEFAULT_POLICY
REAL_BUNDLE_DIR = REAL_POLICY.parent
SCRATCH_PREFIX = f"_scratch_access_policy_{os.getpid()}_"
_CREATED_SCRATCH: set[Path] = set()


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _bundle_hash(entries: list[dict]) -> str:
    digest = hashlib.sha256()
    for entry in sorted(entries, key=lambda item: item["path"]):
        digest.update(entry["path"].encode("utf-8") + b"\0" + entry["sha256"].encode("ascii") + b"\n")
    return digest.hexdigest()


def _read_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _write_yaml(path: Path, data: dict) -> None:
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=False), encoding="utf-8")


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def _repo_rel(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()


def _register(path: Path) -> Path:
    resolved = path.resolve()
    if resolved.parent != FIXROOT.resolve() or not resolved.name.startswith(SCRATCH_PREFIX):
        raise ValueError(f"refusing to register scratch path: {path}")
    _CREATED_SCRATCH.add(resolved)
    return resolved


def _cleanup_one(path: Path) -> None:
    try:
        resolved = path.resolve()
    except OSError:
        return
    if (
        resolved in _CREATED_SCRATCH
        and resolved.parent == FIXROOT.resolve()
        and resolved.name.startswith(SCRATCH_PREFIX)
    ):
        shutil.rmtree(resolved, ignore_errors=True)
        _CREATED_SCRATCH.discard(resolved)


def _cleanup_all() -> None:
    for path in tuple(_CREATED_SCRATCH):
        _cleanup_one(path)


atexit.register(_cleanup_all)


class AccessPolicyBundleTests(unittest.TestCase):
    def make_bundle(self, mutate_policy=None, *, expect_valid: bool = True) -> Path:
        tmp = _register(Path(tempfile.mkdtemp(prefix=SCRATCH_PREFIX, dir=FIXROOT)))
        self.addCleanup(_cleanup_one, tmp)
        for name in (
            "access-policy.yml",
            "boundary-probe.json",
            "access-policy-evidence.yml",
            "visibility-boundary-evidence.yml",
            "freeze-manifest.yml",
        ):
            shutil.copy2(REAL_BUNDLE_DIR / name, tmp / name)
        policy_path = tmp / "access-policy.yml"
        self.refresh_bundle_hashes(tmp)
        self.assertEqual([], validator.validate_bundle(policy_path))
        if mutate_policy:
            data = _read_yaml(policy_path)
            mutate_policy(data)
            _write_yaml(policy_path, data)
            self.refresh_bundle_hashes(tmp)
        if expect_valid:
            self.assertEqual([], validator.validate_bundle(policy_path))
        return policy_path

    def refresh_bundle_hashes(self, bundle_dir: Path) -> None:
        policy_path = bundle_dir / "access-policy.yml"
        policy = _read_yaml(policy_path)
        probe_path = bundle_dir / "boundary-probe.json"
        probe_data = _read_json(probe_path)
        probe_data.update(
            policy_ref=_repo_rel(policy_path),
            policy_sha256=_sha(policy_path),
            launcher_ref=policy["launcher_ref"],
            launcher_sha256=_sha(REPO_ROOT / policy["launcher_ref"]),
            isolation_plan_ref=policy["isolation_plan_ref"],
            isolation_plan_sha256=_sha(REPO_ROOT / policy["isolation_plan_ref"]),
        )
        _write_json(probe_path, probe_data)
        entries = []
        for path in (
            policy_path,
            REPO_ROOT / policy["launcher_ref"],
            REPO_ROOT / validator.PROBE_RUNNER_REF,
            probe_path,
            REPO_ROOT / policy["isolation_plan_ref"],
            bundle_dir / "access-policy-evidence.yml",
            bundle_dir / "visibility-boundary-evidence.yml",
        ):
            entries.append({"path": _repo_rel(path), "sha256": _sha(path)})
        freeze = _read_yaml(bundle_dir / "freeze-manifest.yml")
        freeze["hashes"] = entries
        freeze["content_sha256"] = _bundle_hash(entries)
        _write_yaml(bundle_dir / "freeze-manifest.yml", freeze)

    def assert_bundle_problem(self, policy_path: Path, expected: str) -> None:
        problems = validator.validate_bundle(policy_path)
        self.assertTrue(problems, "expected bundle validation to fail")
        self.assertTrue(any(expected in problem for problem in problems), problems)

    def test_real_access_policy_bundle_validates(self):
        self.assertEqual([], validator.validate_bundle(REAL_POLICY))

    def test_policy_hash_drift_fails(self):
        policy_path = self.make_bundle()
        probe_path = policy_path.parent / "boundary-probe.json"
        data = _read_json(probe_path)
        data["policy_sha256"] = "0" * 64
        _write_json(probe_path, data)
        self.assert_bundle_problem(policy_path, "boundary probe policy_sha256 mismatch")

    def test_launcher_hash_drift_fails(self):
        def mutate(data: dict) -> None:
            data["launcher_sha256"] = "0" * 64

        policy_path = self.make_bundle(mutate_policy=mutate, expect_valid=False)
        self.assert_bundle_problem(policy_path, "launcher_sha256 mismatch")

    def test_probe_runner_hash_drift_fails(self):
        policy_path = self.make_bundle()
        freeze_path = policy_path.parent / "freeze-manifest.yml"
        freeze = _read_yaml(freeze_path)
        for entry in freeze["hashes"]:
            if entry["path"] == validator.PROBE_RUNNER_REF:
                entry["sha256"] = "0" * 64
        freeze["content_sha256"] = _bundle_hash(freeze["hashes"])
        _write_yaml(freeze_path, freeze)
        self.assert_bundle_problem(policy_path, "freeze hash mismatch")

    def test_freeze_content_hash_drift_fails(self):
        policy_path = self.make_bundle()
        freeze_path = policy_path.parent / "freeze-manifest.yml"
        freeze = _read_yaml(freeze_path)
        freeze["content_sha256"] = "0" * 64
        _write_yaml(freeze_path, freeze)
        self.assert_bundle_problem(policy_path, "freeze content_sha256 mismatch")

    def test_isolation_plan_hash_drift_fails(self):
        def mutate(data: dict) -> None:
            data["isolation_plan_sha256"] = "0" * 64

        policy_path = self.make_bundle(mutate_policy=mutate, expect_valid=False)
        self.assert_bundle_problem(policy_path, "isolation_plan_sha256 mismatch")

    def test_isolation_plan_field_drift_fails(self):
        def mutate(data: dict) -> None:
            data["arms"]["control"]["slot_id"] += "-drift"

        policy_path = self.make_bundle(mutate_policy=mutate, expect_valid=False)
        self.assert_bundle_problem(policy_path, "arms.control.slot_id must match")

    def test_role_leak_in_visible_policy_path_fails(self):
        def mutate(data: dict) -> None:
            data["arms"]["control"]["workspace_source"] = "/tmp/vibe-lab-run004-v1/control/workspace"

        policy_path = self.make_bundle(mutate_policy=mutate, expect_valid=False)
        self.assert_bundle_problem(policy_path, "leaks a role token")

    def test_relative_or_outside_executable_path_fails(self):
        policy, problems = sandbox.validate_policy(REAL_POLICY, REPO_ROOT)
        self.assertEqual([], problems)
        assert policy is not None
        with self.assertRaisesRegex(ValueError, "absolute executable"):
            sandbox._validate_command(["python3", "-V"], policy)
        with self.assertRaisesRegex(ValueError, "outside allowed command roots"):
            sandbox._validate_command(["/usr/local/bin/python3", "-V"], policy)

    def test_canonical_deny_list_covers_async_io_and_new_mount_api(self):
        policy, problems = sandbox.validate_policy(REAL_POLICY, REPO_ROOT)
        self.assertEqual([], problems)
        assert policy is not None
        denied = set(policy["backend"]["denied_syscalls"])
        for name in (
            "io_uring_setup",
            "io_uring_enter",
            "io_uring_register",
            "open_tree",
            "move_mount",
            "fsopen",
            "fsconfig",
            "fsmount",
            "fspick",
            "mount_setattr",
        ):
            self.assertIn(name, denied)

    def test_prompt_hash_drift_fails_closed(self):
        with tempfile.TemporaryDirectory(dir="/tmp") as tmpdir:
            prompt = Path(tmpdir) / "task.md"
            prompt.write_bytes(b"assigned prompt\n")
            with self.assertRaisesRegex(ValueError, "assigned prompt hash mismatch"):
                sandbox._read_prompt_no_symlinks(prompt, "0" * 64)

    def test_symlink_in_workspace_or_prompt_path_fails_closed(self):
        with tempfile.TemporaryDirectory(dir="/tmp") as tmpdir:
            root = Path(tmpdir)
            real_workspace = root / "workspace"
            real_workspace.mkdir()
            workspace_link = root / "workspace-link"
            workspace_link.symlink_to(real_workspace, target_is_directory=True)
            with self.assertRaises(OSError):
                sandbox._open_directory_no_symlinks(workspace_link)
            prompt = root / "task.md"
            prompt.write_bytes(b"assigned prompt\n")
            prompt_link = root / "task-link.md"
            prompt_link.symlink_to(prompt)
            with self.assertRaises(OSError):
                sandbox._read_prompt_no_symlinks(prompt_link, _sha(prompt))

    def test_preexisting_runtime_root_is_not_replaced_or_deleted(self):
        policy = _read_yaml(REAL_POLICY)
        runtime_root = Path(policy["runtime_root"])
        if runtime_root.exists() or runtime_root.is_symlink():
            with self.assertRaises(probe.ProbeError):
                probe.run_probe(REAL_POLICY, generated_at="2026-06-27T11:30:01Z")
            self.assertTrue(runtime_root.exists() or runtime_root.is_symlink())
            return
        runtime_root.mkdir()
        sentinel = runtime_root / "sentinel"
        sentinel.write_text("do not delete\n", encoding="utf-8")
        try:
            with self.assertRaises(probe.ProbeError):
                probe.run_probe(REAL_POLICY, generated_at="2026-06-27T11:30:01Z")
            self.assertTrue(sentinel.exists())
        finally:
            shutil.rmtree(runtime_root)

    def test_live_probe_enforces_visibility_and_process_boundaries(self):
        result = probe.run_probe(REAL_POLICY, generated_at="2026-06-27T11:30:02Z")
        self.assertFalse(Path(result["materialized_runtime_root"]).exists())
        self.assertTrue(result["cleanup"]["runtime_root_removed_by_probe"])
        for role in ("control", "treatment"):
            checks = result["arms"][role]["checks"]
            for name in (
                "assigned_prompt_stdin_byte_equal",
                "workspace_read_write",
                "repo_root_not_visible",
                "home_not_visible",
                "delivery_not_visible",
                "other_slot_not_visible",
                "root_mount_surface_has_no_unexpected_host_paths",
                "environment_is_minimal",
                "network_socket_denied_eperm",
                "namespace_escape_denied_eperm",
                "io_uring_setup_denied_eperm",
                "new_mount_api_fsopen_denied_eperm",
                "visible_paths_role_tokens_absent",
                "workspace_has_no_git",
                "workspace_has_no_prompt_file",
            ):
                self.assertIs(checks[name], True, f"{role} {name}")

    def test_real_evidence_files_are_kind_separated(self):
        access = _read_yaml(REAL_BUNDLE_DIR / "access-policy-evidence.yml")
        visibility = _read_yaml(REAL_BUNDLE_DIR / "visibility-boundary-evidence.yml")
        self.assertEqual(["access_policy"], [claim["kind"] for claim in access["claims"]])
        self.assertEqual(["visibility_boundary"], [claim["kind"] for claim in visibility["claims"]])
        self.assertFalse(access["synthetic_fixture"])
        self.assertFalse(visibility["synthetic_fixture"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
