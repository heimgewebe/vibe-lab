#!/usr/bin/env python3
"""Regression tests for operator_lab_metrics.py."""
from __future__ import annotations
import sys
import tempfile
import unittest
from pathlib import Path
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
from operator_lab_metrics import ARTIFACTS_REL, collect_operator_lab_metrics  # noqa: E402
class OperatorLabMetricsTests(unittest.TestCase):
    def _root(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        (root / ARTIFACTS_REL).mkdir(parents=True)
        return tmp, root
    def _card(
        self,
        root: Path,
        name: str,
        *,
        metrics: str = "",
        probe: str = "",
    ) -> None:
        run_dir = root / ARTIFACTS_REL / name
        run_dir.mkdir(parents=True)
        body = (
            "schema_version: '0.1.0'\n"
            f"run_id: {name!r}\n"
            f"{metrics}"
            f"{probe}"
        )
        (run_dir / "run-card.yml").write_text(body, encoding="utf-8")
    def test_empty_repository_reports_zeroes(self) -> None:
        tmp, root = self._root()
        self.addCleanup(tmp.cleanup)
        report = collect_operator_lab_metrics(root)
        self.assertEqual(report["run_card_count"], 0)
        self.assertEqual(report["metrics"]["review_friction_count"], 0)
        self.assertEqual(report["task_completion_time_not_measured"], 0)
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["steering_mismatches"], [])
    def test_sums_metrics_and_not_measured_tasks(self) -> None:
        tmp, root = self._root()
        self.addCleanup(tmp.cleanup)
        self._card(
            root,
            "run-001-alpha",
            metrics=(
                "metrics:\n"
                "  review_friction_count: 2\n"
                "  rework_count: 1\n"
                "  false_block_count: 0\n"
                "  task_completion_time_observed: 'not_measured'\n"
            ),
        )
        self._card(
            root,
            "run-002-beta",
            metrics=(
                "metrics:\n"
                "  review_friction_count: 3\n"
                "  rework_count: 4\n"
                "  false_block_count: 1\n"
                "  task_completion_time_observed: 'measured'\n"
            ),
        )
        report = collect_operator_lab_metrics(root)
        self.assertEqual(report["run_card_count"], 2)
        self.assertEqual(report["metrics"]["review_friction_count"], 5)
        self.assertEqual(report["metrics"]["rework_count"], 5)
        self.assertEqual(report["metrics"]["false_block_count"], 1)
        self.assertEqual(report["task_completion_time_not_measured"], 1)
    def test_not_run_plus_changed_decision_yes_fails(self) -> None:
        tmp, root = self._root()
        self.addCleanup(tmp.cleanup)
        self._card(
            root,
            "run-001-bad",
            probe=(
                "steuerboard_probe:\n"
                "  useful_signal: 'not_run; Git checks were enough'\n"
                "  changed_decision: 'yes'\n"
            ),
        )
        report = collect_operator_lab_metrics(root)
        self.assertEqual(len(report["steering_mismatches"]), 1)
        self.assertIn("not_run", report["steering_mismatches"][0])
    def test_not_run_plus_changed_decision_no_passes(self) -> None:
        tmp, root = self._root()
        self.addCleanup(tmp.cleanup)
        self._card(
            root,
            "run-001-good",
            probe=(
                "steuerboard_probe:\n"
                "  useful_signal: 'not_run; Git checks were enough'\n"
                "  changed_decision: 'no'\n"
            ),
        )
        report = collect_operator_lab_metrics(root)
        self.assertEqual(report["steering_mismatches"], [])
    def test_non_integer_metric_fails(self) -> None:
        tmp, root = self._root()
        self.addCleanup(tmp.cleanup)
        self._card(
            root,
            "run-001-shape",
            metrics=(
                "metrics:\n"
                "  review_friction_count: '1'\n"
            ),
        )
        report = collect_operator_lab_metrics(root)
        self.assertEqual(len(report["errors"]), 1)
        self.assertIn("review_friction_count", report["errors"][0])
    def test_real_repository_metrics_are_valid(self) -> None:
        report = collect_operator_lab_metrics()
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["steering_mismatches"], [])
if __name__ == "__main__":
    unittest.main()
