#!/usr/bin/env python3
"""Regression tests for the archived Phase-1c fixture inventory guard."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


def _load_module():
    script_path = Path(__file__).resolve().parent / "validate_experiment_structure_phase1c_fixtures.py"
    spec = importlib.util.spec_from_file_location("phase1c_archive_guard", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load Phase-1c archive guard")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Phase1cArchiveGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = _load_module()

    def test_repository_archive_is_intact(self) -> None:
        self.assertEqual(self.mod.archive_errors(), [])

    def _temporary_archive(self):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        fixture_root = root / "tests" / "fixtures" / "experiment_structure_phase1c"
        fixture_root.mkdir(parents=True)
        cases = {}
        for name, (verdict, status, confidence) in self.mod.EXPECTED_CASES.items():
            case_dir = fixture_root / name
            case_dir.mkdir()
            (case_dir / "historical.txt").write_text("archived\n", encoding="utf-8")
            cases[name] = {
                "fixture_path": case_dir.relative_to(root).as_posix(),
                "expected_verdict": verdict,
                "expected_status_assessment": status,
                "expected_confidence": confidence,
                "notes": ["historical expectation"],
            }
        index = fixture_root / "expected-outcomes.json"
        index.write_text(json.dumps({"cases": cases}), encoding="utf-8")
        return temp, root, fixture_root, index, cases

    def test_missing_case_is_rejected(self) -> None:
        temp, root, fixture_root, index, cases = self._temporary_archive()
        with temp:
            cases.pop("inconsistent")
            index.write_text(json.dumps({"cases": cases}), encoding="utf-8")
            errors = self.mod.archive_errors(index, fixture_root, root)
            self.assertIn("missing archived case: inconsistent", errors)

    def test_path_escape_is_rejected(self) -> None:
        temp, root, fixture_root, index, cases = self._temporary_archive()
        with temp:
            cases["valid"]["fixture_path"] = "../outside"
            index.write_text(json.dumps({"cases": cases}), encoding="utf-8")
            errors = self.mod.archive_errors(index, fixture_root, root)
            self.assertTrue(any("escapes the archive root" in error for error in errors))

    def test_historical_verdict_drift_is_rejected(self) -> None:
        temp, root, fixture_root, index, cases = self._temporary_archive()
        with temp:
            cases["valid"]["expected_verdict"] = "INCONSISTENT"
            index.write_text(json.dumps({"cases": cases}), encoding="utf-8")
            errors = self.mod.archive_errors(index, fixture_root, root)
            self.assertIn("case valid expected_verdict drifted", errors)


if __name__ == "__main__":
    unittest.main()
