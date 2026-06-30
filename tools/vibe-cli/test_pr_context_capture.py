#!/usr/bin/env python3
"""Regression tests for the PR context capture helper."""

from __future__ import annotations

import importlib.util
import io
import json
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import yaml

SCRIPT = Path(__file__).resolve().parent / "pr_context_capture.py"
SPEC = importlib.util.spec_from_file_location("pr_context_capture", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
pr_context_capture = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pr_context_capture)


class PrContextCaptureTests(unittest.TestCase):
    def _ready_pilot(self, root: Path) -> tuple[Path, Path]:
        experiment = root / "experiments/2026-06-10_pr-agent-context-comparison-series"
        experiment.mkdir(parents=True)
        source_experiment = pr_context_capture.PILOT.parent
        for relative in (
            Path("artifacts/run-002-vibe-lab-handoff/condition-input.md"),
            Path("artifacts/run-004-minimal-decision-first-checklist/condition-input.md"),
        ):
            target = experiment / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source_experiment / relative, target)
        data = yaml.safe_load(pr_context_capture.PILOT.read_text(encoding="utf-8"))
        for pair in data["pairing"]["pairs"]:
            pair["task_refs"] = [f"task:{pair['pair_id']}:slot-1", f"task:{pair['pair_id']}:slot-2"]
        data["role_bindings"] = {
            "executor": "executor:test",
            "reviewer": "reviewer:test",
            "auditor": "auditor:test",
        }
        data["blockers"] = []
        data["execution_allowed"] = True
        pilot = experiment / "pilot-v1.yml"
        pilot.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
        return pilot, root / "runs"

    def test_main_reports_capture_error_without_name_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            stderr = io.StringIO()
            stdout = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                rc = pr_context_capture.main([
                    "--work-root", tmp,
                    "prepare",
                    "--run-id", "run-invalid-base",
                    "--pair-id", "pair-small-doc-a",
                    "--slot", "1",
                    "--executor", "tester",
                    "--base-commit", "not-a-sha",
                ])
        self.assertEqual(rc, 1)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("error: invalid slot, executor, or base commit", stderr.getvalue())

    def test_lifecycle_writes_required_summary_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pilot, work_root = self._ready_pilot(Path(tmp))
            directory = pr_context_capture.prepare(
                "run-lifecycle-ok",
                "pair-01",
                1,
                "tester",
                "abcdef0",
                pilot_path=pilot,
                work_root=work_root,
            )
            self.assertTrue((directory / "condition-input.md").is_file())
            for index, phase in enumerate(pr_context_capture.PHASES):
                started = float(index * 10)
                pr_context_capture.start(directory, phase, clock=started)
                event = pr_context_capture.stop(directory, clock=started + 1.25)
                self.assertEqual(event["name"], phase)
                self.assertEqual(event["duration_seconds"], 1.25)
            (directory / "agent-output.md").write_text("agent output\n", encoding="utf-8")
            (directory / "targeted-tests.txt").write_text("tests passed\n", encoding="utf-8")
            (directory / "changed-files.txt").write_text("tools/vibe-cli/pr_context_capture.py\n", encoding="utf-8")
            pr_context_capture.review(directory, "PR-245", 2, ["abcdef1"])
            summary = pr_context_capture.finalize(directory)
            self.assertEqual(summary["run_id"], "run-lifecycle-ok")
            self.assertEqual(summary["condition"], "D")
            self.assertEqual(summary["task_completion_time_observed"], 6.25)
            self.assertEqual(summary["review_friction_count"], 2)
            self.assertEqual(summary["rework_count"], 1)
            timing = (directory / "timing.txt").read_text(encoding="utf-8")
            self.assertIn("duration_seconds: 6.250000", timing)
            self.assertIn("preparation_seconds: 1.250000", timing)
            stored_summary = json.loads((directory / "collector-summary.json").read_text(encoding="utf-8"))
            self.assertEqual(stored_summary, summary)
            state = json.loads((directory / "collector-state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["status"], "finalized")


if __name__ == "__main__":
    unittest.main()
