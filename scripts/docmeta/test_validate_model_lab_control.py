#!/usr/bin/env python3
"""Regression tests for the opt-in Model-Lab control validator."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR))

from validate_model_lab_control import validate_files  # noqa: E402

REPO_ROOT = THIS_DIR.parent.parent
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "model_lab_control"


class ModelLabControlValidatorTests(unittest.TestCase):
    def test_valid_minimal_run_meta_passes(self) -> None:
        result = validate_files([FIXTURE_ROOT / "valid" / "minimal-run-meta.json"])

        self.assertTrue(result.ok)
        self.assertEqual(result.checked, 1)
        self.assertEqual(result.activated, 1)
        self.assertEqual(result.errors, ())

    def test_missing_model_id_fails_when_activated(self) -> None:
        result = validate_files([FIXTURE_ROOT / "invalid" / "missing-model-id.json"])

        self.assertFalse(result.ok)
        self.assertEqual(result.activated, 1)
        self.assertTrue(any("model_id" in error for error in result.errors))

    def test_missing_challenge_version_fails_when_activated(self) -> None:
        result = validate_files(
            [FIXTURE_ROOT / "invalid" / "missing-challenge-version.json"]
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.activated, 1)
        self.assertTrue(any("challenge_version" in error for error in result.errors))

    def test_empty_evidence_artifacts_fails_when_activated(self) -> None:
        result = validate_files(
            [FIXTURE_ROOT / "invalid" / "empty-evidence-artifacts.json"]
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.activated, 1)
        self.assertTrue(any("evidence_artifacts" in error for error in result.errors))

    def test_non_string_model_id_fails_when_activated(self) -> None:
        result = validate_files(
            [FIXTURE_ROOT / "invalid" / "non-string-model-id.json"]
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.activated, 1)
        self.assertTrue(any("model_id" in error for error in result.errors))

    def test_legacy_run_without_activation_is_ignored(self) -> None:
        result = validate_files([FIXTURE_ROOT / "legacy" / "legacy-run-meta.json"])

        self.assertTrue(result.ok)
        self.assertEqual(result.checked, 1)
        self.assertEqual(result.activated, 0)
        self.assertEqual(result.errors, ())

    def test_directory_scan_combines_results(self) -> None:
        result = validate_files([FIXTURE_ROOT / "valid", FIXTURE_ROOT / "legacy"])

        self.assertTrue(result.ok)
        self.assertEqual(result.checked, 2)
        self.assertEqual(result.activated, 1)


if __name__ == "__main__":
    unittest.main()
