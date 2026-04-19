#!/usr/bin/env python3
"""Regression tests for validate_experiment_structure_phase1c_fixtures.py."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


def _load_module():
    script_path = (
        Path(__file__).resolve().parent / "validate_experiment_structure_phase1c_fixtures.py"
    )
    spec = importlib.util.spec_from_file_location(
        "validate_experiment_structure_phase1c_fixtures", script_path
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load validate_experiment_structure_phase1c_fixtures.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ValidateExperimentStructurePhase1cFixturesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = _load_module()
        self.fixture_dir = (
            self.mod.REPO_ROOT / "tests" / "fixtures" / "experiment_structure_phase1c"
        )
        self.manifest_validator = self.mod.load_schema_validator(self.mod.MANIFEST_SCHEMA_PATH)
        self.decision_validator = self.mod.load_schema_validator(self.mod.DECISION_SCHEMA_PATH)

    def test_expected_cases_load(self) -> None:
        cases = self.mod.load_expected_cases(self.fixture_dir)
        self.assertEqual(sorted(cases.keys()), ["inconsistent", "insufficient_input", "valid"])

    def test_valid_fixture_matches_expected(self) -> None:
        cases = self.mod.load_expected_cases(self.fixture_dir)
        case = cases["valid"]
        observed = self.mod.evaluate_case(
            "valid",
            self.mod.REPO_ROOT / case["fixture_path"],
            self.manifest_validator,
            self.decision_validator,
        )
        mismatches = self.mod.compare_case("valid", observed, case)
        self.assertEqual(mismatches, [])

    def test_inconsistent_fixture_matches_expected(self) -> None:
        cases = self.mod.load_expected_cases(self.fixture_dir)
        case = cases["inconsistent"]
        observed = self.mod.evaluate_case(
            "inconsistent",
            self.mod.REPO_ROOT / case["fixture_path"],
            self.manifest_validator,
            self.decision_validator,
        )
        mismatches = self.mod.compare_case("inconsistent", observed, case)
        self.assertEqual(mismatches, [])

    def test_insufficient_input_fixture_matches_expected(self) -> None:
        cases = self.mod.load_expected_cases(self.fixture_dir)
        case = cases["insufficient_input"]
        observed = self.mod.evaluate_case(
            "insufficient_input",
            self.mod.REPO_ROOT / case["fixture_path"],
            self.manifest_validator,
            self.decision_validator,
        )
        mismatches = self.mod.compare_case("insufficient_input", observed, case)
        self.assertEqual(mismatches, [])


if __name__ == "__main__":
    unittest.main()