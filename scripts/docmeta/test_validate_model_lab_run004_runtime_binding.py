#!/usr/bin/env python3
"""Regression tests for the closed Run-004 runtime-binding bundle validator."""

from __future__ import annotations

import atexit
import hashlib
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts" / "docmeta"))

import validate_model_lab_run004_runtime_binding as validator  # noqa: E402

REAL_DIR = (
    REPO_ROOT
    / "experiments"
    / "2026-05-31_model-lab-replication-series"
    / "artifacts"
    / "run-004-runtime-binding"
)
FIXROOT = REPO_ROOT / "tests" / "fixtures" / "model_lab_runtime_binding"
SCRATCH_PREFIX = f"_scratch_runtime_binding_{os.getpid()}_"
EXPECTED_HASHED_FILES = [
    "agent-protocol.md",
    "runtime-contract.yml",
    "neutral-probe.yml",
    "model-identity-evidence.yml",
    "agent-identity-evidence.yml",
    "sampling-config-evidence.yml",
    "execution-order-evidence.yml",
    "runtime-environment-evidence.yml",
]
_CREATED_SCRATCH: set[Path] = set()


def _read_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _write_yaml(path: Path, data: dict) -> None:
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=False), encoding="utf-8")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _bundle_hash(entries: list[dict]) -> str:
    digest = hashlib.sha256()
    for entry in sorted(entries, key=lambda item: item["path"]):
        digest.update(entry["path"].encode("utf-8") + b"\0" + entry["sha256"].encode("ascii") + b"\n")
    return digest.hexdigest()


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
    if resolved in _CREATED_SCRATCH and resolved.parent == FIXROOT.resolve() and resolved.name.startswith(SCRATCH_PREFIX):
        shutil.rmtree(resolved, ignore_errors=True)
        _CREATED_SCRATCH.discard(resolved)


def _cleanup_all() -> None:
    for path in tuple(_CREATED_SCRATCH):
        _cleanup_one(path)


atexit.register(_cleanup_all)


class RuntimeBindingValidatorTests(unittest.TestCase):
    def build(
        self,
        *,
        mutate_contract=None,
        mutate_neutral=None,
        mutate_freeze=None,
        mutate_file=None,
        extra: dict[str, str] | None = None,
        recompute_freeze: bool = True,
    ) -> Path:
        FIXROOT.mkdir(parents=True, exist_ok=True)
        tmp = _register(Path(tempfile.mkdtemp(prefix=SCRATCH_PREFIX, dir=FIXROOT)))
        self.addCleanup(_cleanup_one, tmp)
        shutil.copytree(REAL_DIR, tmp, dirs_exist_ok=True)
        old_prefix = REAL_DIR.relative_to(REPO_ROOT).as_posix()
        new_prefix = tmp.relative_to(REPO_ROOT).as_posix()
        for item in tmp.iterdir():
            if item.is_file():
                item.write_text(item.read_text(encoding="utf-8").replace(old_prefix, new_prefix), encoding="utf-8")
        if mutate_neutral:
            neutral = _read_yaml(tmp / "neutral-probe.yml")
            mutate_neutral(neutral)
            _write_yaml(tmp / "neutral-probe.yml", neutral)
        contract = _read_yaml(tmp / "runtime-contract.yml")
        contract["neutral_probe"]["sha256"] = _sha(tmp / "neutral-probe.yml")
        if mutate_contract:
            mutate_contract(contract)
        _write_yaml(tmp / "runtime-contract.yml", contract)
        if mutate_file:
            mutate_file(tmp)
        if recompute_freeze:
            self._recompute_freeze(tmp, mutate_freeze=mutate_freeze)
        elif mutate_freeze:
            freeze = _read_yaml(tmp / "freeze-manifest.yml")
            mutate_freeze(freeze)
            _write_yaml(tmp / "freeze-manifest.yml", freeze)
        if extra:
            for rel, content in extra.items():
                target = tmp / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
        return tmp / "runtime-contract.yml"

    def _recompute_freeze(self, tmp: Path, mutate_freeze=None) -> None:
        contract = _read_yaml(tmp / "runtime-contract.yml")
        entries = [
            {"path": (tmp / name).relative_to(REPO_ROOT).as_posix(), "sha256": _sha(tmp / name)}
            for name in EXPECTED_HASHED_FILES
        ]
        freeze = {
            "artifact_type": "model_lab_runtime_binding_freeze_manifest",
            "contract_version": "run-004-runtime-binding-freeze.v1",
            "binding_id": contract["binding_id"],
            "series_id": contract["series_id"],
            "design_id": contract["design_id"],
            "challenge_version": contract["challenge_version"],
            "frozen_at": contract["generated_at"],
            "manifest_excludes_itself": True,
            "hash_algorithm": "sha256(sorted(repo_relative_path + NUL + file_sha256 + LF) over hashed files)",
            "content_sha256": _bundle_hash(entries),
            "hashes": entries,
        }
        if mutate_freeze:
            mutate_freeze(freeze)
        _write_yaml(tmp / "freeze-manifest.yml", freeze)

    def test_real_runtime_binding_bundle_validates(self):
        self.assertEqual([], validator.validate_bundle(REAL_DIR / "runtime-contract.yml"))

    def test_scratch_runtime_binding_bundle_validates(self):
        self.assertEqual([], validator.validate_bundle(self.build()))

    def test_agent_program_hash_drift_reopens_agent_blocker(self):
        path = self.build(mutate_contract=lambda data: data["agent"].update(program_sha256="0" * 64))
        problems, affected = validator.validate_bundle_with_blockers(path)
        self.assertTrue(any("agent program_ref/program_sha256 mismatch" in problem for problem in problems), problems)
        self.assertIn("AGENT_BINDING_UNRESOLVED", affected)

    def test_neutral_probe_hash_drift_reopens_identity_blockers(self):
        path = self.build(mutate_contract=lambda data: data["neutral_probe"].update(sha256="0" * 64))
        problems, affected = validator.validate_bundle_with_blockers(path)
        self.assertTrue(any("neutral probe ref/sha256 mismatch" in problem for problem in problems), problems)
        self.assertIn("MODEL_BINDING_UNRESOLVED", affected)
        self.assertIn("AGENT_BINDING_UNRESOLVED", affected)

    def test_freeze_content_hash_drift_fails(self):
        path = self.build(mutate_freeze=lambda data: data.update(content_sha256="0" * 64))
        problems, affected = validator.validate_bundle_with_blockers(path)
        self.assertTrue(any("freeze content_sha256 mismatch" in problem for problem in problems), problems)
        self.assertIn("SAMPLING_BINDING_UNRESOLVED", affected)

    def test_wrong_single_purpose_evidence_kind_fails(self):
        def mutate(tmp: Path) -> None:
            evidence = _read_yaml(tmp / "agent-identity-evidence.yml")
            evidence["claims"][0]["kind"] = "model_identity"
            _write_yaml(tmp / "agent-identity-evidence.yml", evidence)

        path = self.build(mutate_file=mutate)
        problems, affected = validator.validate_bundle_with_blockers(path)
        self.assertTrue(any("exactly one agent_identity claim" in problem for problem in problems), problems)
        self.assertIn("AGENT_BINDING_UNRESOLVED", affected)

    def test_unexpected_bundle_file_fails_closed(self):
        path = self.build(extra={"notes.txt": "not part of the closed runtime binding bundle\n"})
        problems, affected = validator.validate_bundle_with_blockers(path)
        self.assertTrue(any("unexpected files" in problem for problem in problems), problems)
        self.assertIn("MODEL_BINDING_UNRESOLVED", affected)

    def test_runtime_profile_must_match_across_arms(self):
        def mutate(data: dict) -> None:
            data["runtime_profile"]["treatment_profile_id"] = "other-runtime"

        path = self.build(mutate_contract=mutate)
        problems, affected = validator.validate_bundle_with_blockers(path)
        self.assertTrue(any("runtime profile must be identical" in problem for problem in problems), problems)
        self.assertIn("SAMPLING_BINDING_UNRESOLVED", affected)

    def test_mandatory_non_claims_are_required(self):
        def mutate(data: dict) -> None:
            data["non_claims"].remove("comparison_ready")

        path = self.build(mutate_contract=mutate)
        problems, affected = validator.validate_bundle_with_blockers(path)
        self.assertTrue(any("mandatory non-claims" in problem for problem in problems), problems)
        self.assertIn("EXECUTION_ORDER_UNRESOLVED", affected)



if __name__ == "__main__":
    unittest.main(verbosity=2)
