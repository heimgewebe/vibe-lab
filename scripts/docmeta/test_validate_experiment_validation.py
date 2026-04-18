#!/usr/bin/env python3
"""Regression tests for validate_experiment_validation.py."""

from __future__ import annotations

import unittest
from pathlib import Path

import validate_experiment_validation as vev


class ValidateExperimentValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = vev.load_validator(vev.SCHEMA_PATH)
        self.fixture_dir = vev.REPO_ROOT / "tests" / "fixtures" / "experiment_validation"

    def test_pass_clean_fixture(self) -> None:
        path = self.fixture_dir / "pass-clean.json"
        errors = vev.validate_one(path, self.validator)
        self.assertEqual(errors, [])

    def test_pass_with_conflict_fixture(self) -> None:
        path = self.fixture_dir / "pass-with-conflict.json"
        errors = vev.validate_one(path, self.validator)
        self.assertEqual(errors, [])

    def test_pass_error_abort_fixture(self) -> None:
        path = self.fixture_dir / "pass-error-abort.json"
        errors = vev.validate_one(path, self.validator)
        self.assertEqual(errors, [])

    def test_invalid_status_assessment_fixture(self) -> None:
        path = self.fixture_dir / "invalid-status-assessment.json"
        errors = vev.validate_one(path, self.validator)
        self.assertTrue(errors)
        self.assertIn("contract_invalid", errors[0])

    def test_invalid_confidence_range_fixture(self) -> None:
        path = self.fixture_dir / "invalid-confidence-range.json"
        errors = vev.validate_one(path, self.validator)
        self.assertTrue(errors)
        self.assertIn("contract_invalid", errors[0])

    def test_invalid_error_missing_array_fixture(self) -> None:
        path = self.fixture_dir / "invalid-error-missing-array.json"
        errors = vev.validate_one(path, self.validator)
        self.assertTrue(errors)
        self.assertIn("contract_invalid", errors[0])

    def test_display_path_internal(self) -> None:
        internal = vev.REPO_ROOT / "schemas" / "experiment.validation.schema.json"
        self.assertEqual(vev.display_path(internal), "schemas/experiment.validation.schema.json")

    def test_display_path_external(self) -> None:
        external = (vev.REPO_ROOT.parent / "__outside__" / "test.json").resolve()
        self.assertEqual(vev.display_path(external), str(external))


if __name__ == "__main__":
    unittest.main()
