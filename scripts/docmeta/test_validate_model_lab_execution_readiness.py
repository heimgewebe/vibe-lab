#!/usr/bin/env python3
"""Regression tests for Run-004-v1 execution-readiness validation."""

from __future__ import annotations

import atexit
import contextlib
import copy
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
VALIDATOR = REPO_ROOT / "scripts" / "docmeta" / "validate_model_lab_execution_readiness.py"
FIXROOT = REPO_ROOT / "tests" / "fixtures" / "model_lab_execution_readiness"
VALID_BLOCKED = FIXROOT / "valid" / "blocked"
VALID_READY = FIXROOT / "valid" / "ready"
INVALID_WRONG_SERIES = FIXROOT / "invalid" / "wrong-series" / "execution-readiness.yml"
REAL = (
    REPO_ROOT
    / "experiments"
    / "2026-05-31_model-lab-replication-series"
    / "artifacts"
    / "run-004-execution-readiness"
    / "execution-readiness.yml"
)
SCRATCH_PREFIX = f"_scratch_exec_ready_{os.getpid()}_"
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


class ExecutionReadinessTests(unittest.TestCase):
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

    def build(self, *, source: Path = VALID_READY, mutate=None, mutate_freeze=None, plant=None, remove=None,
              recompute_freeze: bool = True) -> Path:
        tmp = _register(Path(tempfile.mkdtemp(prefix=SCRATCH_PREFIX, dir=FIXROOT)))
        self.addCleanup(_cleanup_one, tmp)
        shutil.copytree(source, tmp, dirs_exist_ok=True)
        old_prefix = source.relative_to(REPO_ROOT).as_posix()
        new_prefix = tmp.relative_to(REPO_ROOT).as_posix()
        ready_path = tmp / "execution-readiness.yml"
        data = _read_yaml(ready_path)
        data = self._rewrite_paths(data, old_prefix, new_prefix)
        data["bundle_artifact_path"] = f"{new_prefix}/execution-readiness.yml"
        data["freeze"]["freeze_manifest_ref"] = f"{new_prefix}/freeze-manifest.yml"
        if mutate:
            mutate(data, tmp)
        _write_yaml(ready_path, data)
        if remove:
            for rel in remove:
                target = tmp / rel
                if target.is_dir():
                    shutil.rmtree(target)
                elif target.exists() or target.is_symlink():
                    target.unlink()
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
        if recompute_freeze:
            self._recompute_freeze(tmp, mutate_freeze=mutate_freeze)
        elif mutate_freeze:
            freeze = _read_yaml(tmp / "freeze-manifest.yml")
            mutate_freeze(freeze, tmp)
            _write_yaml(tmp / "freeze-manifest.yml", freeze)
        return ready_path

    def _rewrite_paths(self, value, old: str, new: str):
        if isinstance(value, dict):
            return {k: self._rewrite_paths(v, old, new) for k, v in value.items()}
        if isinstance(value, list):
            return [self._rewrite_paths(v, old, new) for v in value]
        if isinstance(value, str):
            return value.replace(old, new)
        return value

    def _recompute_freeze(self, tmp: Path, mutate_freeze=None) -> None:
        data = _read_yaml(tmp / "execution-readiness.yml")
        files = [
            tmp / "execution-readiness.yml",
            tmp / "source-snapshots" / "condition-design.snapshot",
            tmp / "source-snapshots" / "design-freeze-manifest.snapshot",
        ]
        entries = [{"path": f.relative_to(REPO_ROOT).as_posix(), "sha256": _sha(f)} for f in files if f.exists()]
        freeze = {
            "artifact_type": "model_lab_execution_readiness_freeze_manifest",
            "contract_version": "run-004-execution-readiness.v1",
            "readiness_bundle_id": data["readiness_bundle_id"],
            "series_id": data["series_id"],
            "design_id": data["design_id"],
            "challenge_version": data["challenge_version"],
            "source_captured_at": data["source_captured_at"],
            "readiness_frozen_at": data["readiness_frozen_at"],
            "authorized_at": data["authorized_at"],
            "source_design_commit_sha": data["provenance"]["design_source_commit_sha"],
            "design_input_source_base_commit_sha": data["provenance"]["design_input_source_base_commit_sha"],
            "future_execution_seed_status": "unresolved",
            "future_execution_seed_sha256": None,
            "readiness_bundle_hash_algorithm": "sha256(sorted(repo_relative_path + NUL + file_sha256 + LF) over hashed files)",
            "readiness_bundle_content_sha256": _bundle_hash(entries),
            "hashes": entries,
        }
        arms = data["workspace_session_isolation"]["arms"]
        seed_hashes = {arms[role].get("seed_hash") for role in ("control", "treatment")}
        seed_refs = {arms[role].get("execution_seed_ref") for role in ("control", "treatment")}
        seed_ids = {arms[role].get("execution_seed") for role in ("control", "treatment")}
        seed_kinds = {arms[role].get("execution_seed_kind") for role in ("control", "treatment")}
        if (
            len(seed_hashes) == len(seed_refs) == len(seed_ids) == len(seed_kinds) == 1
            and None not in seed_hashes | seed_refs | seed_ids | seed_kinds
        ):
            freeze["future_execution_seed_status"] = "bound"
            freeze["future_execution_seed_sha256"] = next(iter(seed_hashes))
        if mutate_freeze:
            mutate_freeze(freeze, tmp)
        _write_yaml(tmp / "freeze-manifest.yml", freeze)

    # 1-2 valid fixtures and real artifact
    def test_valid_blocked_fixture(self):
        self.assert_exit(self.run_v(VALID_BLOCKED / "execution-readiness.yml"), 0)

    def test_valid_synthetic_ready_fixture(self):
        self.assert_exit(self.run_v(VALID_READY / "execution-readiness.yml"), 0)

    def test_real_artifact_is_valid_blocked(self):
        self.assert_exit(self.run_v(REAL), 0)

    # 3-5 identity
    def test_wrong_series(self):
        self.assert_rule(self.build(mutate=lambda d, _: d.update(series_id="wrong-series")), "EXECUTION_READINESS_REQUIRES_RUN004_IDENTITY")
        self.assert_exit(self.run_v(INVALID_WRONG_SERIES), 2)

    def test_wrong_design_id(self):
        self.assert_rule(self.build(mutate=lambda d, _: d.update(design_id="wrong-design")), "EXECUTION_READINESS_REQUIRES_RUN004_IDENTITY")

    def test_wrong_challenge_version(self):
        self.assert_rule(self.build(mutate=lambda d, _: d.update(challenge_version="other-v1")), "EXECUTION_READINESS_REQUIRES_RUN004_IDENTITY")

    # 6-10 provenance, paths, closed bundle
    def test_wrong_design_freeze_hash(self):
        self.assert_rule(
            self.build(mutate=lambda d, _: d["provenance"].update(design_freeze_manifest_sha256="0" * 64)),
            "EXECUTION_READINESS_REQUIRES_DESIGN_PROVENANCE",
        )

    def test_missing_source_file(self):
        self.assert_rule(
            self.build(remove=["source-snapshots/condition-design.snapshot"]),
            "EXECUTION_READINESS_REQUIRES_DESIGN_PROVENANCE",
            code=1,
        )

    def test_path_escape(self):
        self.assert_rule(
            self.build(mutate=lambda d, _: d["provenance"].update(condition_design_snapshot_ref="../escape.yml")),
            "EXECUTION_READINESS_REQUIRES_DESIGN_PROVENANCE",
        )

    def test_symlink_in_bundle(self):
        path = self.build()
        try:
            os.symlink(REPO_ROOT / "AGENTS.md", path.parent / "link-to-agents.md")
        except OSError:
            self.skipTest("symlinks unsupported on this platform")
        self.assert_rule(path, "EXECUTION_READINESS_REQUIRES_VALID_FREEZE")

    def test_unexpected_bundle_file(self):
        self.assert_rule(
            self.build(plant={"notes/extra.txt": "unexpected\n"}),
            "EXECUTION_READINESS_REQUIRES_VALID_FREEZE",
        )

    # 11-17 ready binding
    def test_ready_unknown_model(self):
        self.assert_rule(
            self.build(mutate=lambda d, _: d["runtime_binding"]["exact_model_id"].update(value="unknown")),
            "EXECUTION_READINESS_REQUIRES_FULL_READY_BINDING",
        )

    def test_ready_unknown_agent(self):
        self.assert_rule(
            self.build(mutate=lambda d, _: d["runtime_binding"]["agent_program"].update(value="tbd")),
            "EXECUTION_READINESS_REQUIRES_FULL_READY_BINDING",
        )

    def test_ready_bound_model_requires_evidence(self):
        self.assert_rule(
            self.build(mutate=lambda d, _: d["runtime_binding"]["exact_model_id"].update(evidence=[])),
            "EXECUTION_READINESS_REQUIRES_FULL_READY_BINDING",
        )

    def test_ready_unbound_sampling(self):
        self.assert_rule(
            self.build(mutate=lambda d, _: d["runtime_binding"]["sampling"]["temperature"].update(status="unresolved", value=None)),
            "EXECUTION_READINESS_REQUIRES_FULL_READY_BINDING",
        )

    def test_ready_different_arm_runtimes(self):
        self.assert_rule(
            self.build(mutate=lambda d, _: d["runtime_binding"]["arms"]["treatment"].update(profile_id="other-runtime")),
            "EXECUTION_READINESS_REQUIRES_FULL_READY_BINDING",
        )

    def test_same_workspace_for_both_arms(self):
        def mut(d, _):
            d["workspace_session_isolation"]["arms"]["treatment"]["workspace_path"] = d["workspace_session_isolation"]["arms"]["control"]["workspace_path"]
        self.assert_rule(self.build(mutate=mut), "EXECUTION_READINESS_REQUIRES_FULL_READY_BINDING")

    def test_same_session_for_both_arms(self):
        def mut(d, _):
            d["workspace_session_isolation"]["arms"]["treatment"]["session_id"] = d["workspace_session_isolation"]["arms"]["control"]["session_id"]
        self.assert_rule(self.build(mutate=mut), "EXECUTION_READINESS_REQUIRES_FULL_READY_BINDING")

    def test_dirty_start_state(self):
        self.assert_rule(
            self.build(mutate=lambda d, _: d["workspace_session_isolation"]["arms"]["control"].update(clean_start_state=False)),
            "EXECUTION_READINESS_REQUIRES_FULL_READY_BINDING",
        )

    # 18-24 order, harness, intervention, prompt isolation
    def test_missing_execution_order(self):
        self.assert_rule(
            self.build(mutate=lambda d, _: d["execution_order"].update(binding_status="unbound", strategy=None)),
            "EXECUTION_READINESS_REQUIRES_FULL_READY_BINDING",
        )

    def test_arm_dependent_harness(self):
        self.assert_rule(
            self.build(mutate=lambda d, _: d["harness"].update(identical_surface_for_both_arms=False)),
            "EXECUTION_READINESS_REQUIRES_FULL_READY_BINDING",
        )

    def test_missing_harness_hash(self):
        self.assert_rule(
            self.build(mutate=lambda d, _: d["harness"].update(file_hashes=[])),
            "EXECUTION_READINESS_REQUIRES_FULL_READY_BINDING",
        )

    def test_missing_start_or_test_command(self):
        self.assert_rule(
            self.build(mutate=lambda d, _: d["harness"].update(start_command=None, test_command=None)),
            "EXECUTION_READINESS_REQUIRES_FULL_READY_BINDING",
        )

    def test_missing_timeout(self):
        self.assert_rule(
            self.build(mutate=lambda d, _: d["harness"]["timeouts"].update(start_seconds=None)),
            "EXECUTION_READINESS_REQUIRES_FULL_READY_BINDING",
        )

    def test_asymmetric_human_intervention_rules(self):
        self.assert_exit(
            self.run_v(self.build(mutate=lambda d, _: d["human_intervention"].update(same_policy_across_arms=False))),
            2,
        )

    def test_both_payloads_visible_in_workspace(self):
        self.assert_rule(
            self.build(mutate=lambda d, _: d["prompt_delivery"]["arms"]["control"].update(only_assigned_payload_delivered=False)),
            "EXECUTION_READINESS_REQUIRES_PROMPT_DELIVERY",
        )

    # 25-33 state and prompt
    def test_wrong_prompt_hash(self):
        self.assert_rule(
            self.build(mutate=lambda d, _: d["prompt_delivery"]["arms"]["treatment"].update(payload_sha256="0" * 64)),
            "EXECUTION_READINESS_REQUIRES_PROMPT_DELIVERY",
        )

    def test_authorization_before_freeze(self):
        self.assert_rule(
            self.build(mutate=lambda d, _: d.update(authorized_at="2026-06-26T12:00:00Z")),
            "EXECUTION_READINESS_REQUIRES_VALID_FREEZE",
        )

    def test_ready_requires_authorization_timestamp(self):
        self.assert_rule(
            self.build(mutate=lambda d, _: d.update(authorized_at=None)),
            "EXECUTION_READINESS_REQUIRES_STATE_MODEL",
        )

    def test_ready_evidence_path_must_be_registered(self):
        def mut(d, _):
            d["runtime_binding"]["exact_model_id"]["evidence"] = [
                "tests/fixtures/model_lab_execution_readiness/_evidence/does-not-exist.txt"
            ]
        self.assert_rule(self.build(mutate=mut), "EXECUTION_READINESS_REQUIRES_FULL_READY_BINDING")

    def test_ready_evidence_registry_hash_must_match(self):
        def mut(d, _):
            d["evidence_registry"][0]["sha256"] = "0" * 64
        self.assert_rule(self.build(mutate=mut), "EXECUTION_READINESS_REQUIRES_EVIDENCE_REGISTRY")

    def test_ready_workspace_names_must_not_leak_role(self):
        def mut(d, _):
            d["workspace_session_isolation"]["arms"]["control"]["workspace_path"] = "/tmp/run004/control/workspace"
        self.assert_rule(self.build(mutate=mut), "EXECUTION_READINESS_REQUIRES_FULL_READY_BINDING")

    def test_ready_visibility_requires_registered_evidence(self):
        self.assert_rule(
            self.build(mutate=lambda d, _: d["visibility_boundary"].update(evidence=[])),
            "EXECUTION_READINESS_REQUIRES_FULL_READY_BINDING",
        )

    def test_ready_harness_neutrality_requires_registered_evidence(self):
        self.assert_rule(
            self.build(mutate=lambda d, _: d["harness"]["framework_neutrality"].update(evidence=[])),
            "EXECUTION_READINESS_REQUIRES_FULL_READY_BINDING",
        )

    def test_ready_first_mutation_trace_requires_registered_evidence(self):
        self.assert_rule(
            self.build(mutate=lambda d, _: d["metric_operationalization"]["first_mutation_trace"].update(evidence=[])),
            "EXECUTION_READINESS_REQUIRES_FULL_READY_BINDING",
        )

    def test_authorized_when_blocked(self):
        def mut(d, _):
            d["state"]["authorization_status"] = "authorized"
            d["authorized_at"] = "2026-06-26T13:45:00Z"
        self.assert_rule(self.build(source=VALID_BLOCKED, mutate=mut), "EXECUTION_READINESS_REQUIRES_STATE_MODEL")

    def test_execution_allowed_without_authorization(self):
        def mut(d, _):
            d["state"]["authorization_status"] = "not_authorized"
            d["state"]["run_004_execution_allowed"] = True
            d["authorized_at"] = None
        self.assert_rule(self.build(mutate=mut), "EXECUTION_READINESS_REQUIRES_STATE_MODEL")

    def test_run_004_executed_true(self):
        self.assert_exit(self.run_v(self.build(mutate=lambda d, _: d["state"].update(run_004_executed=True))), 2)

    def test_result_assessment_allowed_true(self):
        self.assert_exit(self.run_v(self.build(mutate=lambda d, _: d["state"].update(result_assessment_allowed=True))), 2)

    def test_comparison_ready_true(self):
        self.assert_exit(self.run_v(self.build(mutate=lambda d, _: d["state"].update(comparison_ready=True))), 2)

    def test_closed_blocker_is_invalid(self):
        def mut(d, _):
            d["blockers"][0]["status"] = "closed"
        self.assert_rule(self.build(source=VALID_BLOCKED, mutate=mut), "EXECUTION_READINESS_REQUIRES_STATE_MODEL")

    def test_blocked_requires_all_derived_blockers(self):
        def mut(d, _):
            d["blockers"] = [item for item in d["blockers"] if item["id"] != "EXECUTION_ORDER_UNRESOLVED"]
        self.assert_rule(self.build(source=VALID_BLOCKED, mutate=mut), "EXECUTION_READINESS_REQUIRES_STATE_MODEL")

    def test_missing_mandatory_non_claim(self):
        def mut(d, _):
            d["required_non_claims"].remove("condition_effect")
        self.assert_rule(self.build(mutate=mut), "EXECUTION_READINESS_REQUIRES_STATE_MODEL")

    # 34-40 execution artifacts, discovery, encoding, git, source manipulation, chronology
    def test_execution_artifacts_in_readiness_bundle(self):
        self.assert_rule(
            self.build(plant={"run.yml": "not allowed\n", "implementation": None}),
            "EXECUTION_READINESS_REQUIRES_VALID_FREEZE",
        )

    def test_mixed_discovery_candidates_fail(self):
        mod = runpy.run_path(str(VALIDATOR), run_name="exec_ready_mixed")
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
                Path("experiments/a/artifacts/good/execution-readiness.yml"),
                Path("experiments/b/artifacts/bad/execution-readiness.yml"),
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
                "experiments/a/artifacts/good/execution-readiness.yml",
                "experiments/b/artifacts/bad/execution-readiness.yml",
            ],
            calls,
        )
        self.assertIn("checked=2, passed=1, failed=1", output.getvalue())

    def test_empty_discovery_fails(self):
        mod = runpy.run_path(str(VALIDATOR), run_name="exec_ready_empty")
        main = mod["main"]
        main.__globals__["discover_run_004_v1_artifacts"] = lambda root: []
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(2, main([]))

    def test_invalid_utf8(self):
        path = self.build(recompute_freeze=False)
        path.write_bytes(b"\xff\xfe not yaml\n")
        self.assert_exit(self.run_v(path), 2)

    def test_unknown_git_commit_fails_closed(self):
        def mut(d, _):
            d["provenance"]["design_source_commit_sha"] = "deadbeef" * 5

        self.assert_exit(self.run_v(self.build(mutate=mut)), 2)

    def test_manipulated_frozen_design_source(self):
        def mut(d, tmp):
            snap = tmp / "source-snapshots" / "condition-design.snapshot"
            snap.write_bytes(snap.read_bytes() + b"\n# fixture tamper\n")
            d["provenance"]["condition_design_sha256"] = _sha(snap)

        self.assert_rule(self.build(mutate=mut), "EXECUTION_READINESS_REQUIRES_DESIGN_PROVENANCE")

    def test_inconsistent_chronology(self):
        self.assert_rule(
            self.build(mutate=lambda d, _: d.update(source_captured_at="2026-06-26T14:00:00Z")),
            "EXECUTION_READINESS_REQUIRES_VALID_FREEZE",
        )

    def test_forbidden_execution_artifact_reports_once(self):
        completed = self.run_v(self.build(plant={"run.yml": "not allowed\n"}))
        self.assert_exit(completed, 1)
        self.assertEqual(1, completed.stdout.count("execution artifact forbidden in readiness bundle: run.yml"))
        self.assertNotIn("unexpected file in closed readiness bundle: run.yml", completed.stdout)

    def test_invalid_snapshot_yaml_fails_closed(self):
        def mut(d, tmp):
            snap = tmp / "source-snapshots" / "condition-design.snapshot"
            snap.write_text(": invalid yaml: [\n", encoding="utf-8")
            d["provenance"]["condition_design_sha256"] = _sha(snap)
        completed = self.run_v(self.build(mutate=mut))
        self.assert_exit(completed, 2)
        self.assertIn("invalid or unreadable", completed.stdout)

    def test_ready_rejects_untyped_readme_evidence(self):
        def mut(d, _):
            path = "README.md"
            d["evidence_registry"][0]["path"] = path
            d["evidence_registry"][0]["sha256"] = _sha(REPO_ROOT / path)
        self.assert_rule(self.build(mutate=mut), "EXECUTION_READINESS_REQUIRES_EVIDENCE_REGISTRY")

    def test_ready_seed_hash_binds_manifest_bytes(self):
        def mut(d, _):
            d["workspace_session_isolation"]["arms"]["control"]["seed_hash"] = "0" * 64
        self.assert_rule(self.build(mutate=mut), "EXECUTION_READINESS_REQUIRES_FULL_READY_BINDING")

    def test_ready_prompt_delivery_status_must_be_bound(self):
        self.assert_rule(
            self.build(mutate=lambda d, _: d["prompt_delivery"].update(binding_status="unbound")),
            "EXECUTION_READINESS_REQUIRES_PROMPT_DELIVERY",
        )

    def test_blocker_derivation_rejects_status_only_model_binding(self):
        def mut(d, _):
            d["blockers"] = [item for item in d["blockers"] if item["id"] != "MODEL_BINDING_UNRESOLVED"]
            for key in ("provider", "exact_model_id", "model_revision_or_version"):
                d["runtime_binding"][key].update(status="bound", value=None, evidence=[])
        self.assert_rule(self.build(source=VALID_BLOCKED, mutate=mut), "EXECUTION_READINESS_REQUIRES_STATE_MODEL")

    def test_ready_metric_rule_must_match_frozen_protocol(self):
        def mut(d, _):
            for item in d["metric_operationalization"]["metrics"]:
                if item["id"] == "rework_steps":
                    item["rule"] = "a post-hoc alternative rule"
        self.assert_rule(self.build(mutate=mut), "EXECUTION_READINESS_REQUIRES_FULL_READY_BINDING")

    def test_source_capture_must_follow_design_freeze(self):
        self.assert_rule(
            self.build(mutate=lambda d, _: d.update(source_captured_at="2026-06-26T12:00:00Z")),
            "EXECUTION_READINESS_REQUIRES_DESIGN_PROVENANCE",
        )

    def test_ready_workspace_camelcase_role_leak_is_rejected(self):
        def mut(d, _):
            d["workspace_session_isolation"]["arms"]["control"]["session_id"] = "fixtureControlA"
        self.assert_rule(self.build(mutate=mut), "EXECUTION_READINESS_REQUIRES_FULL_READY_BINDING")

    def test_ready_total_timeout_must_cover_start_and_test(self):
        def mut(d, _):
            d["harness"]["timeouts"].update(start_seconds=30, test_seconds=120, total_seconds=100)
        self.assert_rule(self.build(mutate=mut), "EXECUTION_READINESS_REQUIRES_FULL_READY_BINDING")

    def test_seed_manifest_must_cover_every_root_file(self):
        mod = runpy.run_path(str(VALIDATOR), run_name="exec_ready_seed_coverage")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo = root / "repo"
            seed_root = repo / "seed"
            seed_root.mkdir(parents=True)
            included = seed_root / "included.txt"
            omitted = seed_root / "omitted.txt"
            included.write_text("included\n", encoding="utf-8")
            omitted.write_text("omitted\n", encoding="utf-8")
            entry = {"path": "seed/included.txt", "sha256": _sha(included)}
            manifest = repo / "manifest.yml"
            _write_yaml(
                manifest,
                {
                    "schema_version": "v1",
                    "artifact_type": "model_lab_execution_seed_manifest",
                    "seed_id": "fixture-seed",
                    "seed_kind": "file_manifest",
                    "synthetic_fixture": True,
                    "root_ref": "seed",
                    "content_hash_algorithm": "sha256(sorted(repo_relative_path + NUL + file_sha256 + LF) over files)",
                    "content_sha256": _bundle_hash([entry]),
                    "files": [entry],
                },
            )
            problems = mod["_seed_manifest_errors"]("manifest.yml", _sha(manifest), repo, True)
        self.assertTrue(any("omits root file" in problem for problem in problems), problems)

    def test_real_evidence_file_must_bind_one_claim_kind(self):
        mod = runpy.run_path(str(VALIDATOR), run_name="exec_ready_single_purpose_evidence")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            evidence = root / "evidence.yml"
            _write_yaml(
                evidence,
                {
                    "schema_version": "v1",
                    "artifact_type": "model_lab_execution_readiness_evidence",
                    "evidence_id": "combined-real-evidence",
                    "synthetic_fixture": False,
                    "claims": [
                        {"kind": "model_identity", "status": "verified", "subject": "model", "value": "m"},
                        {"kind": "agent_identity", "status": "verified", "subject": "agent", "value": "a"},
                    ],
                },
            )
            artifact = root / "experiments" / "x" / "artifacts" / "r" / "execution-readiness.yml"
            artifact.parent.mkdir(parents=True)
            artifact.write_text("placeholder\n", encoding="utf-8")
            data = {
                "evidence_registry": [
                    {
                        "path": "evidence.yml",
                        "sha256": _sha(evidence),
                        "kinds": ["model_identity", "agent_identity"],
                    }
                ]
            }
            _, problems = mod["_evidence_registry"](data, artifact, root)
        self.assertTrue(any("exactly one claim kind" in problem for problem in problems), problems)

    def test_real_artifact_binds_execution_seed_and_sessions(self):
        data = yaml.safe_load((REPO_ROOT / "experiments/2026-05-31_model-lab-replication-series/artifacts/run-004-execution-readiness/execution-readiness.yml").read_text(encoding="utf-8"))
        ids = {item["id"] for item in data["blockers"]}
        self.assertNotIn("EXECUTION_SEED_UNRESOLVED", ids)
        self.assertNotIn("SESSION_ISOLATION_UNPROVEN", ids)
        self.assertIn("BLINDED_WORKSPACE_UNRESOLVED", ids)
        for role in ("control", "treatment"):
            arm = data["workspace_session_isolation"]["arms"][role]
            self.assertEqual("empty_directory", arm["execution_seed_kind"])
            self.assertEqual("run-004-rest-api-v1-empty-workspace", arm["execution_seed"])
            self.assertTrue(arm["clean_start_state"])

    def test_seed_kind_must_match_manifest(self):
        def mut(d, _):
            d["workspace_session_isolation"]["arms"]["control"]["execution_seed_kind"] = "empty_directory"
        self.assert_rule(self.build(source=VALID_READY, mutate=mut), "EXECUTION_READINESS_REQUIRES_FULL_READY_BINDING")


    def test_real_blocked_freeze_binds_prepared_seed(self):
        data = yaml.safe_load((REPO_ROOT / "experiments/2026-05-31_model-lab-replication-series/artifacts/run-004-execution-readiness/execution-readiness.yml").read_text(encoding="utf-8"))
        freeze = yaml.safe_load((REPO_ROOT / "experiments/2026-05-31_model-lab-replication-series/artifacts/run-004-execution-readiness/freeze-manifest.yml").read_text(encoding="utf-8"))
        self.assertEqual("not_authorized", data["state"]["authorization_status"])
        self.assertEqual("bound", freeze["future_execution_seed_status"])
        self.assertEqual(data["workspace_session_isolation"]["arms"]["control"]["seed_hash"], freeze["future_execution_seed_sha256"])

    def test_bound_seed_cannot_be_unresolved_in_freeze(self):
        def mut_freeze(freeze, _):
            freeze["future_execution_seed_status"] = "unresolved"
            freeze["future_execution_seed_sha256"] = None
        self.assert_rule(
            self.build(source=VALID_READY, mutate_freeze=mut_freeze),
            "EXECUTION_READINESS_REQUIRES_VALID_FREEZE",
        )

    def test_real_artifact_closes_session_isolation_only(self):
        data = yaml.safe_load((REPO_ROOT / "experiments/2026-05-31_model-lab-replication-series/artifacts/run-004-execution-readiness/execution-readiness.yml").read_text(encoding="utf-8"))
        ids = {item["id"] for item in data["blockers"]}
        self.assertNotIn("SESSION_ISOLATION_UNPROVEN", ids)
        self.assertIn("BLINDED_WORKSPACE_UNRESOLVED", ids)
        self.assertEqual("bound", data["workspace_session_isolation"]["binding_status"])
        self.assertEqual("unresolved", data["visibility_boundary"]["boundary_status"])

    def test_real_prompt_packages_are_assigned_but_visibility_is_not_overclaimed(self):
        data = yaml.safe_load((REPO_ROOT / "experiments/2026-05-31_model-lab-replication-series/artifacts/run-004-execution-readiness/execution-readiness.yml").read_text(encoding="utf-8"))
        for role in ("control", "treatment"):
            self.assertTrue(data["prompt_delivery"]["arms"][role]["only_assigned_payload_delivered"])
        self.assertTrue(data["visibility_boundary"]["path_names_role_neutral"])
        self.assertFalse(data["visibility_boundary"]["repo_metadata_reconstruction_prevented"])
        self.assertTrue(data["visibility_boundary"]["normal_repo_read_access_can_reconstruct_experiment"])

    def test_real_isolation_plan_is_content_bound(self):
        data = yaml.safe_load(REAL.read_text(encoding="utf-8"))
        binding = data["workspace_session_isolation"]
        plan = REPO_ROOT / binding["isolation_plan_ref"]
        self.assertEqual(_sha(plan), binding["isolation_plan_sha256"])

    def test_isolation_plan_hash_drift_reopens_session_blocker(self):
        def mut(data, _):
            data["workspace_session_isolation"]["isolation_plan_sha256"] = "0" * 64
        self.assert_rule(
            self.build(source=REAL.parent, mutate=mut),
            "EXECUTION_READINESS_REQUIRES_STATE_MODEL",
        )

    def test_isolation_plan_field_drift_reopens_session_blocker(self):
        def mut(data, _):
            data["workspace_session_isolation"]["arms"]["control"]["session_id"] += "-drift"
        self.assert_rule(
            self.build(source=REAL.parent, mutate=mut),
            "EXECUTION_READINESS_REQUIRES_STATE_MODEL",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
