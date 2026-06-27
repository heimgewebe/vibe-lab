#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import tempfile
import unittest
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
SCRIPT = HERE / "prepare_model_lab_run004_workspaces.py"
spec = importlib.util.spec_from_file_location("run004_workspace", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class Run004WorkspaceIsolationTests(unittest.TestCase):
    def load_plan(self):
        return yaml.safe_load(module.DEFAULT_PLAN.read_text(encoding="utf-8"))

    def write_mutated_plan(self, mutate):
        temp = tempfile.TemporaryDirectory(dir=REPO_ROOT)
        path = Path(temp.name) / "plan.yml"
        data = copy.deepcopy(self.load_plan())
        mutate(data)
        path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
        return temp, path

    def test_real_plan_validates(self):
        data, problems = module.validate_plan(module.DEFAULT_PLAN, REPO_ROOT)
        self.assertEqual([], problems)
        self.assertEqual(2, len(data["slots"]))

    def test_materializes_two_opaque_slots_with_only_assigned_prompts(self):
        with tempfile.TemporaryDirectory() as parent:
            output = Path(parent) / "prepared"
            report = module.materialize(module.DEFAULT_PLAN, output, REPO_ROOT)
            self.assertEqual(2, len(report["slot_ids"]))
            data = self.load_plan()
            self.assertEqual([], module.inspect_materialization(data, output, REPO_ROOT))
            prompt_files = sorted(output.rglob("task.md"))
            self.assertEqual(2, len(prompt_files))
            self.assertNotEqual(prompt_files[0].read_bytes(), prompt_files[1].read_bytes())
            for path in output.rglob("*"):
                self.assertNotRegex(path.as_posix().lower(), r"control|treatment")

    def test_workspaces_remain_empty(self):
        with tempfile.TemporaryDirectory() as parent:
            output = Path(parent) / "prepared"
            module.materialize(module.DEFAULT_PLAN, output, REPO_ROOT)
            data = self.load_plan()
            canonical = Path(data["runtime_root"])
            for role in module.ROLES:
                rel = Path(data["slots"][role]["workspace_path"]).relative_to(canonical)
                self.assertEqual([], list((output / rel).iterdir()))

    def test_preexisting_output_is_rejected(self):
        with tempfile.TemporaryDirectory() as parent:
            output = Path(parent) / "prepared"
            output.mkdir()
            with self.assertRaises(FileExistsError):
                module.materialize(module.DEFAULT_PLAN, output, REPO_ROOT)

    def test_output_inside_repo_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as parent:
            output = Path(parent) / "prepared"
            with self.assertRaises(ValueError):
                module.materialize(module.DEFAULT_PLAN, output, REPO_ROOT)

    def test_duplicate_session_is_rejected(self):
        temp, path = self.write_mutated_plan(
            lambda data: data["slots"]["treatment"].update(session_id=data["slots"]["control"]["session_id"])
        )
        try:
            _, problems = module.validate_plan(path, REPO_ROOT)
            self.assertTrue(any("distinct bound session_id" in problem for problem in problems), problems)
        finally:
            temp.cleanup()

    def test_role_leaking_path_is_rejected(self):
        def mutate(data):
            data["slots"]["control"]["workspace_path"] = "/tmp/vibe-lab-run004-v1/control/workspace"
        temp, path = self.write_mutated_plan(mutate)
        try:
            _, problems = module.validate_plan(path, REPO_ROOT)
            self.assertTrue(any("leaks a role token" in problem for problem in problems), problems)
        finally:
            temp.cleanup()

    def test_wrong_payload_hash_is_rejected(self):
        temp, path = self.write_mutated_plan(
            lambda data: data["slots"]["control"].update(payload_sha256="0" * 64)
        )
        try:
            _, problems = module.validate_plan(path, REPO_ROOT)
            self.assertTrue(any("payload_sha256 mismatch" in problem for problem in problems), problems)
        finally:
            temp.cleanup()

    def test_other_slot_must_be_forbidden(self):
        def mutate(data):
            data["slots"]["control"]["forbidden_paths"] = [
                str(Path(data["slots"]["control"]["delivery_path"]).parent),
                "/tmp/unrelated",
            ]
        temp, path = self.write_mutated_plan(mutate)
        try:
            _, problems = module.validate_plan(path, REPO_ROOT)
            self.assertTrue(any("other slot root" in problem for problem in problems), problems)
        finally:
            temp.cleanup()

    def test_cli_check_succeeds(self):
        self.assertEqual(0, module.main([]))

    def test_path_alias_is_rejected(self):
        def mutate(data):
            root = data["slots"]["control"]["slot_root"]
            data["slots"]["control"]["workspace_path"] = f"{root}/tmp/../workspace"
        temp, path = self.write_mutated_plan(mutate)
        try:
            _, problems = module.validate_plan(path, REPO_ROOT)
            self.assertTrue(any("canonical absolute path" in problem for problem in problems), problems)
        finally:
            temp.cleanup()

    def test_nested_slot_roots_are_rejected(self):
        def mutate(data):
            base = data["slots"]["control"]["slot_root"] + "/nested-node"
            slot = data["slots"]["treatment"]
            slot["slot_root"] = base
            slot["workspace_path"] = base + "/workspace"
            slot["delivery_path"] = base + "/delivery/task.md"
            slot["temp_dir"] = base + "/tmp"
            slot["cache_dir"] = base + "/cache"
            slot["allowed_paths"] = [slot["workspace_path"]]
            slot["forbidden_paths"] = [base + "/delivery", data["slots"]["control"]["slot_root"]]
            data["slots"]["control"]["forbidden_paths"][1] = base
        temp, path = self.write_mutated_plan(mutate)
        try:
            _, problems = module.validate_plan(path, REPO_ROOT)
            self.assertTrue(any("non-overlapping siblings" in problem for problem in problems), problems)
        finally:
            temp.cleanup()

    def test_prompt_refs_must_match_frozen_design(self):
        def mutate(data):
            data["slots"]["control"]["overlay_ref"] = data["slots"]["treatment"]["overlay_ref"]
            data["slots"]["control"]["payload_sha256"] = data["slots"]["treatment"]["payload_sha256"]
        temp, path = self.write_mutated_plan(mutate)
        try:
            _, problems = module.validate_plan(path, REPO_ROOT)
            self.assertTrue(any("must match the frozen condition design" in problem for problem in problems), problems)
        finally:
            temp.cleanup()

    def test_atomic_publication_does_not_replace_destination(self):
        with tempfile.TemporaryDirectory() as parent:
            root = Path(parent)
            source = root / "source"
            destination = root / "destination"
            source.mkdir()
            destination.mkdir()
            with self.assertRaises(FileExistsError):
                module._rename_noreplace(source, destination)
            self.assertTrue(source.is_dir())
            self.assertTrue(destination.is_dir())

    def test_materializer_hash_drift_is_rejected(self):
        temp, path = self.write_mutated_plan(
            lambda data: data.update(materializer_sha256="0" * 64)
        )
        try:
            _, problems = module.validate_plan(path, REPO_ROOT)
            self.assertTrue(any("materializer_sha256 mismatch" in problem for problem in problems), problems)
        finally:
            temp.cleanup()


if __name__ == "__main__":
    unittest.main(verbosity=2)
