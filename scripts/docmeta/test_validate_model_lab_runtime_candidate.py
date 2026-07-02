#!/usr/bin/env python3
"""Regression tests for Run-004 runtime-candidate validation."""

from __future__ import annotations

import atexit
import contextlib
import hashlib
import io
import os
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
VALIDATOR = REPO_ROOT / "scripts" / "docmeta" / "validate_model_lab_runtime_candidate.py"
REAL_DIR = (
    REPO_ROOT
    / "experiments/2026-05-31_model-lab-replication-series/artifacts/run-004-runtime-candidate"
)
REAL = REAL_DIR / "runtime-candidate.yml"
FIXROOT = REPO_ROOT / "tests" / "fixtures" / "model_lab_runtime_candidate"
SCRATCH_PREFIX = f"_scratch_runtime_candidate_{os.getpid()}_"
_CREATED_SCRATCH: set[Path] = set()


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _bundle_hash(entries: list[dict]) -> str:
    digest = hashlib.sha256()
    for entry in sorted(entries, key=lambda item: item["path"]):
        digest.update(entry["path"].encode("utf-8"))
        digest.update(b"\0")
        digest.update(entry["sha256"].encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def _read_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _write_yaml(path: Path, data: dict) -> None:
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=False), encoding="utf-8")


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


class RuntimeCandidateTests(unittest.TestCase):
    def run_v(self, *paths: Path):
        return subprocess.run(
            [sys.executable, str(VALIDATOR), *[str(p) for p in paths]],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="strict",
            check=False,
        )

    def assert_exit(self, completed, code: int) -> None:
        self.assertEqual(code, completed.returncode, completed.stdout + completed.stderr)

    def assert_rule(self, path: Path, rule: str, code: int = 1) -> None:
        completed = self.run_v(path)
        self.assert_exit(completed, code)
        self.assertIn(rule, completed.stdout)
        self.assertNotIn("Traceback", completed.stdout + completed.stderr)

    def build(self, *, mutate=None, mutate_freeze=None, plant=None, recompute_freeze: bool = True) -> Path:
        tmp = _register(Path(tempfile.mkdtemp(prefix=SCRATCH_PREFIX, dir=FIXROOT)))
        self.addCleanup(_cleanup_one, tmp)
        shutil.copytree(REAL_DIR, tmp, dirs_exist_ok=True)
        old_prefix = REAL_DIR.relative_to(REPO_ROOT).as_posix()
        new_prefix = tmp.relative_to(REPO_ROOT).as_posix()
        candidate_path = tmp / "runtime-candidate.yml"
        data = self._rewrite_paths(_read_yaml(candidate_path), old_prefix, new_prefix)
        data["candidate_artifact_path"] = f"{new_prefix}/runtime-candidate.yml"
        data["freeze"]["freeze_manifest_ref"] = f"{new_prefix}/freeze-manifest.yml"
        if mutate:
            mutate(data, tmp)
        _write_yaml(candidate_path, data)
        if recompute_freeze:
            self.refresh_hashes(tmp, mutate_freeze=mutate_freeze)
        elif mutate_freeze:
            freeze = _read_yaml(tmp / "freeze-manifest.yml")
            mutate_freeze(freeze, tmp)
            _write_yaml(tmp / "freeze-manifest.yml", freeze)
        if plant:
            for rel, content in plant.items():
                target = tmp / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                if content is None:
                    target.mkdir(exist_ok=True)
                elif isinstance(content, bytes):
                    target.write_bytes(content)
                else:
                    target.write_text(content, encoding="utf-8")
        return candidate_path

    def _rewrite_paths(self, value, old: str, new: str):
        if isinstance(value, dict):
            return {key: self._rewrite_paths(item, old, new) for key, item in value.items()}
        if isinstance(value, list):
            return [self._rewrite_paths(item, old, new) for item in value]
        if isinstance(value, str):
            return value.replace(old, new)
        return value

    def refresh_hashes(self, bundle_dir: Path, mutate_freeze=None) -> None:
        candidate_path = bundle_dir / "runtime-candidate.yml"
        data = _read_yaml(candidate_path)
        for entry in data["evidence_registry"]:
            entry["sha256"] = _sha(REPO_ROOT / entry["path"])
        _write_yaml(candidate_path, data)
        entries = []
        for name in (
            "runtime-candidate.yml",
            "model-identity-evidence.yml",
            "runtime-environment-evidence.yml",
        ):
            path = bundle_dir / name
            entries.append({"path": _repo_rel(path), "sha256": _sha(path)})
        freeze = _read_yaml(bundle_dir / "freeze-manifest.yml")
        freeze["hashes"] = entries
        freeze["content_sha256"] = _bundle_hash(entries)
        freeze["candidate_id"] = data["candidate_id"]
        if mutate_freeze:
            mutate_freeze(freeze, bundle_dir)
        _write_yaml(bundle_dir / "freeze-manifest.yml", freeze)

    def test_real_runtime_candidate_validates(self):
        self.assert_exit(self.run_v(REAL), 0)

    def test_missing_broker_blocker_is_rejected(self):
        def mut(data, _):
            data["blockers"] = [item for item in data["blockers"] if item["id"] != "AGENT_TOOL_BROKER_UNRESOLVED"]

        self.assert_rule(self.build(mutate=mut), "RUNTIME_CANDIDATE_REQUIRES_BLOCKED_STATE")

    def test_false_broker_ready_is_rejected(self):
        path = self.build(mutate=lambda data, _: data["broker"].update(broker_ready=True))
        self.assert_rule(path, "instance_path=broker.broker_ready", code=2)

    def test_execution_allowed_claim_is_rejected(self):
        path = self.build(mutate=lambda data, _: data["state"].update(run_004_execution_allowed=True))
        self.assert_rule(path, "instance_path=state.run_004_execution_allowed", code=2)

    def test_model_accessible_through_sandbox_claim_is_rejected(self):
        path = self.build(
            mutate=lambda data, _: data["sandbox_access"].update(model_accessible_through_bound_sandbox=True)
        )
        self.assert_rule(path, "instance_path=sandbox_access.model_accessible_through_bound_sandbox", code=2)

    def test_usr_local_command_root_is_rejected(self):
        def mut(data, _):
            data["sandbox_access"]["allowed_command_roots"] = ["/usr/bin", "/bin", "/usr/local/bin"]

        self.assert_rule(self.build(mutate=mut), "instance_path=sandbox_access.allowed_command_roots", code=2)

    def test_codex_binding_is_rejected(self):
        path = self.build(mutate=lambda data, _: data["agent_binding"].update(codex_bound_for_run004=True))
        self.assert_rule(path, "instance_path=agent_binding.codex_bound_for_run004", code=2)

    def test_sampling_binding_is_rejected(self):
        path = self.build(mutate=lambda data, _: data["sampling_binding"].update(binding_status="bound"))
        self.assert_rule(path, "instance_path=sampling_binding.binding_status", code=2)

    def test_evidence_hash_drift_is_rejected(self):
        path = self.build()
        data = _read_yaml(path)
        data["evidence_registry"][0]["sha256"] = "0" * 64
        _write_yaml(path, data)
        entries = []
        for name in (
            "runtime-candidate.yml",
            "model-identity-evidence.yml",
            "runtime-environment-evidence.yml",
        ):
            artifact = path.parent / name
            entries.append({"path": _repo_rel(artifact), "sha256": _sha(artifact)})
        freeze = _read_yaml(path.parent / "freeze-manifest.yml")
        freeze["hashes"] = entries
        freeze["content_sha256"] = _bundle_hash(entries)
        _write_yaml(path.parent / "freeze-manifest.yml", freeze)
        self.assert_rule(path, "RUNTIME_CANDIDATE_REQUIRES_EVIDENCE_REGISTRY")

    def test_freeze_hash_drift_is_rejected(self):
        def mut_freeze(freeze, _):
            freeze["hashes"][0]["sha256"] = "0" * 64
            freeze["content_sha256"] = _bundle_hash(freeze["hashes"])

        self.assert_rule(
            self.build(mutate_freeze=mut_freeze),
            "RUNTIME_CANDIDATE_REQUIRES_VALID_FREEZE",
        )

    def test_extra_bundle_file_is_rejected(self):
        self.assert_rule(
            self.build(plant={"notes/extra.txt": "unexpected\n"}),
            "RUNTIME_CANDIDATE_REQUIRES_VALID_FREEZE",
        )

    def test_symlink_in_bundle_is_rejected(self):
        path = self.build()
        try:
            os.symlink(REPO_ROOT / "AGENTS.md", path.parent / "link-to-agents.md")
        except OSError:
            self.skipTest("symlinks unsupported on this platform")
        self.assert_rule(path, "RUNTIME_CANDIDATE_REQUIRES_VALID_FREEZE")

    def test_path_escape_is_rejected(self):
        def mut(data, _):
            data["evidence_registry"][0]["path"] = "../escape.yml"

        self.assert_rule(
            self.build(mutate=mut, recompute_freeze=False),
            "instance_path=evidence_registry.0.path",
            code=2,
        )

    def test_model_digest_drift_is_rejected(self):
        def mut(data, _):
            data["model_candidate"]["model_blob_digest"] = "sha256:" + "0" * 64

        self.assert_rule(self.build(mutate=mut), "instance_path=model_candidate.model_blob_digest", code=2)

    def test_provider_version_drift_is_rejected(self):
        def mut(data, _):
            data["model_candidate"]["provider_version"] = "0.12.7"

        self.assert_rule(self.build(mutate=mut), "instance_path=model_candidate.provider_version", code=2)

    def test_rejected_snapshot_drift_is_rejected(self):
        def mut(data, _):
            data["agent_binding"]["rejected_snapshot"] = "gpt-5.5"

        self.assert_rule(self.build(mutate=mut), "instance_path=agent_binding.rejected_snapshot", code=2)

    def test_provenance_hash_drift_is_rejected(self):
        def mut(data, _):
            data["provenance"]["access_policy_sha256"] = "0" * 64

        self.assert_rule(self.build(mutate=mut), "RUNTIME_CANDIDATE_REQUIRES_PROVENANCE")

    def test_candidate_generated_after_freeze_is_rejected(self):
        def mut(data, _):
            data["generated_at"] = "2030-01-01T00:00:00Z"

        self.assert_rule(self.build(mutate=mut), "RUNTIME_CANDIDATE_REQUIRES_VALID_FREEZE")

    def test_mixed_discovery_candidates_fail(self):
        mod = runpy.run_path(str(VALIDATOR), run_name="runtime_candidate_mixed")
        main = mod["main"]
        calls = []

        def fake_validate(path, validator, repo_root=None):
            rel = path.relative_to(repo_root).as_posix()
            calls.append(rel)
            return (1, [f"invalid {rel}"]) if "bad" in rel else (0, [])

        main.__globals__["load_validator"] = lambda path: object()
        main.__globals__["validate_file"] = fake_validate
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for rel in (
                Path("experiments/a/artifacts/good/runtime-candidate.yml"),
                Path("experiments/b/artifacts/bad/runtime-candidate.yml"),
            ):
                target = root / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("artifact_type: wrong\n", encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = main([], repo_root=root)
        self.assertEqual(1, code)
        self.assertEqual(
            [
                "experiments/a/artifacts/good/runtime-candidate.yml",
                "experiments/b/artifacts/bad/runtime-candidate.yml",
            ],
            calls,
        )
        self.assertIn("checked=2, passed=1, failed=1", output.getvalue())

    def test_empty_discovery_fails(self):
        mod = runpy.run_path(str(VALIDATOR), run_name="runtime_candidate_empty")
        main = mod["main"]
        main.__globals__["discover_run_004_runtime_candidates"] = lambda root: []
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(2, main([]))

    def test_validator_source_has_no_model_or_network_execution_imports(self):
        source = VALIDATOR.read_text(encoding="utf-8")
        self.assertNotIn("import subprocess", source)
        self.assertNotIn("from subprocess", source)
        self.assertNotIn("import requests", source)
        self.assertNotIn("urllib.request", source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
