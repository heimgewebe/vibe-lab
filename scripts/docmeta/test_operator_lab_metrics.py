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
from operator_lab_metrics import (  # noqa: E402
    ARTIFACTS_REL,
    COUNT_METRICS,
    REQUIRED_METRICS,
    collect_operator_lab_metrics,
)
class OperatorLabMetricsTests(unittest.TestCase):
    def _root(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        (root / ARTIFACTS_REL).mkdir(parents=True)
        return tmp, root

    @staticmethod
    def _yaml_value(value: object) -> str:
        if isinstance(value, str):
            return repr(value)
        if isinstance(value, bool):
            return "true" if value else "false"
        return str(value)

    def _metrics(
        self,
        *,
        omit: tuple[str, ...] = (),
        **overrides: object,
    ) -> str:
        values: dict[str, object] = {name: 0 for name in COUNT_METRICS}
        values["task_completion_time_observed"] = "not_measured"
        values.update(overrides)
        lines = ["metrics:\n"]
        for name in REQUIRED_METRICS:
            if name in omit:
                continue
            lines.append(f"  {name}: {self._yaml_value(values[name])}\n")
        return "".join(lines)

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
            metrics=self._metrics(
                review_friction_count=2,
                rework_count=1,
                task_completion_time_observed="not_measured",
            ),
        )
        self._card(
            root,
            "run-002-beta",
            metrics=self._metrics(
                review_friction_count=3,
                rework_count=4,
                false_block_count=1,
                task_completion_time_observed="measured",
            ),
        )
        report = collect_operator_lab_metrics(root)
        self.assertEqual(report["run_card_count"], 2)
        self.assertEqual(report["metrics"]["review_friction_count"], 5)
        self.assertEqual(report["metrics"]["rework_count"], 5)
        self.assertEqual(report["metrics"]["false_block_count"], 1)
        self.assertEqual(report["task_completion_time_not_measured"], 1)

    def test_missing_metrics_block_fails(self) -> None:
        tmp, root = self._root()
        self.addCleanup(tmp.cleanup)
        self._card(root, "run-001-missing")
        report = collect_operator_lab_metrics(root)
        self.assertTrue(
            any("metrics must be a mapping" in error for error in report["errors"])
        )
        self.assertTrue(
            any(
                "metrics missing required fields" in error
                for error in report["errors"]
            )
        )

    def test_missing_single_metric_field_fails(self) -> None:
        tmp, root = self._root()
        self.addCleanup(tmp.cleanup)
        self._card(
            root,
            "run-001-missing-field",
            metrics=self._metrics(omit=("review_friction_count",)),
        )
        report = collect_operator_lab_metrics(root)
        self.assertEqual(len(report["errors"]), 1)
        self.assertIn("review_friction_count", report["errors"][0])

    def test_not_run_plus_changed_decision_yes_fails(self) -> None:
        tmp, root = self._root()
        self.addCleanup(tmp.cleanup)
        self._card(
            root,
            "run-001-bad",
            metrics=self._metrics(),
            probe=(
                "steuerboard_probe:\n"
                "  useful_signal: 'not_run; Git checks were enough'\n"
                "  changed_decision: 'yes'\n"
            ),
        )
        report = collect_operator_lab_metrics(root)
        self.assertEqual(report["errors"], [])
        self.assertEqual(len(report["steering_mismatches"]), 1)
        self.assertIn("not_run", report["steering_mismatches"][0])

    def test_not_run_spellings_are_normalized(self) -> None:
        variants = (
            "not_run; Git checks were enough",
            "not run; Git checks were enough",
            "not-run; Git checks were enough",
            "NOT RUN; Git checks were enough",
        )
        for useful_signal in variants:
            with self.subTest(useful_signal=useful_signal):
                tmp, root = self._root()
                self.addCleanup(tmp.cleanup)
                self._card(
                    root,
                    "run-001-bad",
                    metrics=self._metrics(),
                    probe=(
                        "steuerboard_probe:\n"
                        f"  useful_signal: {useful_signal!r}\n"
                        "  changed_decision: 'yes'\n"
                    ),
                )
                report = collect_operator_lab_metrics(root)
                self.assertEqual(report["errors"], [])
                self.assertEqual(len(report["steering_mismatches"]), 1)

    def test_not_run_plus_changed_decision_no_passes(self) -> None:
        tmp, root = self._root()
        self.addCleanup(tmp.cleanup)
        self._card(
            root,
            "run-001-good",
            metrics=self._metrics(),
            probe=(
                "steuerboard_probe:\n"
                "  useful_signal: 'not_run; Git checks were enough'\n"
                "  changed_decision: 'no'\n"
            ),
        )
        report = collect_operator_lab_metrics(root)
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["steering_mismatches"], [])

    def test_non_integer_metric_fails(self) -> None:
        tmp, root = self._root()
        self.addCleanup(tmp.cleanup)
        self._card(
            root,
            "run-001-shape",
            metrics=self._metrics(review_friction_count="1"),
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
