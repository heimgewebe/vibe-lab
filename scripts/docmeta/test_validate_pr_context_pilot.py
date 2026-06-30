#!/usr/bin/env python3
"""Regression tests for validate_pr_context_pilot.py."""

from __future__ import annotations

import copy
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from validate_pr_context_pilot import DEFAULT_PILOT, validate_pilot  # noqa: E402


class PrContextPilotValidationTests(unittest.TestCase):
    def _fixture(self) -> tuple[tempfile.TemporaryDirectory[str], Path, dict]:
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        experiment = root / "experiments/2026-06-10_pr-agent-context-comparison-series"
        experiment.mkdir(parents=True)
        source_experiment = DEFAULT_PILOT.parent
        for relative in (
            Path("artifacts/run-002-vibe-lab-handoff/condition-input.md"),
            Path("artifacts/run-004-minimal-decision-first-checklist/condition-input.md"),
        ):
            target = experiment / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((source_experiment / relative).read_bytes())
        data = yaml.safe_load(DEFAULT_PILOT.read_text(encoding="utf-8"))
        pilot = experiment / "pilot-v1.yml"
        pilot.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
        return tmp, pilot, data

    def _write(self, pilot: Path, data: dict) -> None:
        pilot.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")

    def test_repository_pilot_is_valid_but_blocked(self) -> None:
        errors, warnings, data = validate_pilot(DEFAULT_PILOT)
        self.assertEqual(errors, [])
        self.assertFalse(data["execution_allowed"])
        self.assertTrue(any("execution-blocked" in warning for warning in warnings))

    def test_hash_drift_fails(self) -> None:
        tmp, pilot, data = self._fixture()
        self.addCleanup(tmp.cleanup)
        mutated = copy.deepcopy(data)
        mutated["conditions"]["B"]["sha256"] = "0" * 64
        self._write(pilot, mutated)
        errors, _, _ = validate_pilot(pilot, repo_root=Path(tmp.name))
        self.assertTrue(any("does not match frozen bytes" in error for error in errors))

    def test_path_escape_fails(self) -> None:
        tmp, pilot, data = self._fixture()
        self.addCleanup(tmp.cleanup)
        mutated = copy.deepcopy(data)
        mutated["conditions"]["D"]["path"] = "../../../outside.md"
        self._write(pilot, mutated)
        errors, _, _ = validate_pilot(pilot, repo_root=Path(tmp.name))
        self.assertTrue(any("must resolve inside" in error for error in errors))

    def test_duplicate_assignment_fails(self) -> None:
        tmp, pilot, data = self._fixture()
        self.addCleanup(tmp.cleanup)
        mutated = copy.deepcopy(data)
        mutated["pairing"]["pairs"][0]["assignment_order"] = ["B", "B"]
        self._write(pilot, mutated)
        errors, _, _ = validate_pilot(pilot, repo_root=Path(tmp.name))
        self.assertTrue(any("assignment_order" in error for error in errors))

    def test_execution_allowed_cannot_ignore_blockers(self) -> None:
        tmp, pilot, data = self._fixture()
        self.addCleanup(tmp.cleanup)
        mutated = copy.deepcopy(data)
        mutated["execution_allowed"] = True
        self._write(pilot, mutated)
        errors, _, _ = validate_pilot(pilot, repo_root=Path(tmp.name))
        self.assertTrue(any("execution_allowed" in error for error in errors))

    def test_duplicate_task_refs_block_readiness(self) -> None:
        tmp, pilot, data = self._fixture()
        self.addCleanup(tmp.cleanup)
        mutated = copy.deepcopy(data)
        for pair in mutated["pairing"]["pairs"]:
            pair["task_refs"] = ["task:duplicate", "task:duplicate"]
        mutated["role_bindings"] = {
            "executor": "executor:test",
            "reviewer": "reviewer:test",
            "auditor": "auditor:test",
        }
        mutated["blockers"] = ["task_refs_not_unique"]
        self._write(pilot, mutated)
        errors, warnings, parsed = validate_pilot(pilot, repo_root=Path(tmp.name))
        self.assertEqual(errors, [])
        self.assertFalse(parsed["execution_allowed"])
        self.assertTrue(any("task_refs_not_unique" in warning for warning in warnings))

    def test_overlapping_roles_block_readiness(self) -> None:
        tmp, pilot, data = self._fixture()
        self.addCleanup(tmp.cleanup)
        mutated = copy.deepcopy(data)
        for pair in mutated["pairing"]["pairs"]:
            mutated_refs = [f"task:{pair['pair_id']}:1", f"task:{pair['pair_id']}:2"]
            pair["task_refs"] = mutated_refs
        mutated["role_bindings"] = {
            "executor": "agent:test",
            "reviewer": "agent:test",
            "auditor": "auditor:test",
        }
        mutated["blockers"] = ["role_bindings_not_distinct"]
        self._write(pilot, mutated)
        errors, warnings, parsed = validate_pilot(pilot, repo_root=Path(tmp.name))
        self.assertEqual(errors, [])
        self.assertFalse(parsed["execution_allowed"])
        self.assertTrue(any("role_bindings_not_distinct" in warning for warning in warnings))


    def test_primary_axes_drift_fails(self) -> None:
        tmp, pilot, data = self._fixture()
        self.addCleanup(tmp.cleanup)
        mutated = copy.deepcopy(data)
        mutated["primary_axes"]["correction_load"].append("false_block_count")
        self._write(pilot, mutated)
        errors, _, _ = validate_pilot(pilot, repo_root=Path(tmp.name))
        self.assertTrue(any("primary_axes.correction_load" in error for error in errors))

    def test_non_claim_drift_fails(self) -> None:
        tmp, pilot, data = self._fixture()
        self.addCleanup(tmp.cleanup)
        mutated = copy.deepcopy(data)
        mutated["does_not_establish"].remove("condition_superiority")
        self._write(pilot, mutated)
        errors, _, _ = validate_pilot(pilot, repo_root=Path(tmp.name))
        self.assertTrue(any("does_not_establish" in error for error in errors))

    def test_ready_state_requires_bound_tasks_and_roles(self) -> None:
        tmp, pilot, data = self._fixture()
        self.addCleanup(tmp.cleanup)
        ready = copy.deepcopy(data)
        for pair in ready["pairing"]["pairs"]:
            pair["task_refs"] = [f"task:{pair['pair_id']}:1", f"task:{pair['pair_id']}:2"]
        ready["role_bindings"] = {
            "executor": "executor:test",
            "reviewer": "reviewer:test",
            "auditor": "auditor:test",
        }
        ready["blockers"] = []
        ready["execution_allowed"] = True
        self._write(pilot, ready)
        errors, warnings, parsed = validate_pilot(pilot, repo_root=Path(tmp.name))
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])
        self.assertTrue(parsed["execution_allowed"])


if __name__ == "__main__":
    unittest.main()
