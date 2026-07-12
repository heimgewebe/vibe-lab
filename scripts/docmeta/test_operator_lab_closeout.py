#!/usr/bin/env python3
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from operator_lab_closeout import build_closeout  # noqa: E402


class OperatorLabCloseoutTests(unittest.TestCase):
    def root(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        base = root / "experiments/2026-07-01_operator-lab-loop/artifacts"
        base.mkdir(parents=True)
        return tmp, root

    def card(self, root: Path, name: str, *, changed: str, measured: bool, meta: bool) -> None:
        path = root / "experiments/2026-07-01_operator-lab-loop/artifacts" / name
        path.mkdir()
        path.joinpath("run-card.yml").write_text(
            "schema_version: '0.1.0'\n"
            f"run_id: {name}\n"
            "condition: decision_first\n"
            "decision: iterate\n"
            "claims:\n  - claim: bounded\n    status: observed\n    evidence:\n      - path: x\n        evidence_status: repo_local\n"
            "metrics:\n"
            "  scope_drift_count: 0\n  unsupported_claim_count: 0\n"
            "  missing_locator_count: 0\n  validation_gap_count: 0\n"
            "  review_friction_count: 1\n  rework_count: 1\n  false_block_count: 0\n"
            f"  task_completion_time_observed: {'measured' if measured else 'not_measured'}\n"
            f"steuerboard_probe:\n  changed_decision: {changed}\n",
            encoding="utf-8",
        )
        if meta:
            path.joinpath("run_meta.json").write_text("{}\n", encoding="utf-8")

    def test_closeout_is_deterministic_and_fail_closed(self) -> None:
        _, root = self.root()
        self.card(root, "run-001-a", changed="yes", measured=False, meta=True)
        self.card(root, "run-002-b", changed="no", measured=False, meta=False)
        first = build_closeout(root)
        second = build_closeout(root)
        self.assertEqual(first, second)
        self.assertEqual(first["verdict"], "insufficient_evidence")
        self.assertFalse(first["effect_claim_allowed"])
        self.assertEqual(first["missing_run_meta_count"], 1)
        self.assertEqual(first["task_completion_time_not_measured_count"], 2)
        self.assertEqual(first["metrics"]["review_friction_count"], 2)
        self.assertEqual(first["comparison_ready_groups"], [])

    def test_invalid_metric_refuses_closeout(self) -> None:
        _, root = self.root()
        self.card(root, "run-001-a", changed="yes", measured=False, meta=True)
        card = next(root.glob("experiments/**/run-card.yml"))
        text = card.read_text().replace("review_friction_count: 1", "review_friction_count: bad")
        card.write_text(text)
        with self.assertRaisesRegex(ValueError, "review_friction_count"):
            build_closeout(root)

    def test_real_repository_closeout_matches_expected_boundary(self) -> None:
        report = build_closeout()
        self.assertEqual(report["run_card_count"], 36)
        self.assertEqual(report["missing_run_meta_count"], 7)
        self.assertEqual(report["task_completion_time_measured_count"], 0)
        self.assertEqual(report["verdict"], "insufficient_evidence")


if __name__ == "__main__":
    unittest.main()
