#!/usr/bin/env python3
"""Regression tests for the AP-2 challenge-version validator."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR))

from validate_challenge_versions import (  # noqa: E402
    build_challenge_registry,
    decision_requires_challenge_version,
    validate_decision_file,
    validate_paths,
)

REPO_ROOT = THIS_DIR.parent.parent
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "challenge_versions"
BENCHMARK_CHALLENGES = REPO_ROOT / "benchmarks" / "challenges"
EXPERIMENTS_ROOT = REPO_ROOT / "experiments"
VALID_CHALLENGE = FIXTURE_ROOT / "valid" / "challenges" / "rest-api-v1.md"


class ChallengeVersionValidatorTests(unittest.TestCase):
    def test_valid_challenge_passes(self) -> None:
        result = validate_paths([VALID_CHALLENGE])

        self.assertTrue(result.ok, result.errors)
        self.assertEqual(result.checked_challenges, 1)
        self.assertEqual(result.errors, ())

    def test_valid_activated_decision_passes(self) -> None:
        result = validate_paths([FIXTURE_ROOT / "valid"])

        self.assertTrue(result.ok, result.errors)
        self.assertGreaterEqual(result.checked_challenges, 1)
        self.assertEqual(result.activated_decisions, 1)

    def test_challenge_without_version_fails(self) -> None:
        result = validate_paths(
            [FIXTURE_ROOT / "invalid" / "challenges" / "missing-version.md"]
        )

        self.assertFalse(result.ok)
        self.assertTrue(any("version" in error for error in result.errors))

    def test_challenge_filename_mismatch_fails(self) -> None:
        result = validate_paths(
            [FIXTURE_ROOT / "invalid" / "challenges" / "wrong-name.md"]
        )

        self.assertFalse(result.ok)
        self.assertTrue(any("does not match" in error for error in result.errors))

    def test_activated_decision_without_challenge_version_fails(self) -> None:
        result = validate_paths(
            [FIXTURE_ROOT / "invalid" / "decisions" / "missing-challenge-version.yml"]
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.activated_decisions, 1)
        self.assertTrue(any("challenge_version" in error for error in result.errors))

    def test_activated_decision_with_unknown_version_fails(self) -> None:
        result = validate_paths(
            [FIXTURE_ROOT / "invalid" / "decisions" / "unknown-challenge-version.yml"]
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.activated_decisions, 1)
        self.assertTrue(
            any("not a known challenge version" in error for error in result.errors)
        )

    def test_legacy_decision_without_activation_is_ignored(self) -> None:
        result = validate_paths(
            [FIXTURE_ROOT / "legacy" / "decisions" / "legacy-decision.yml"]
        )

        self.assertTrue(result.ok, result.errors)
        self.assertEqual(result.checked_decisions, 1)
        self.assertEqual(result.activated_decisions, 0)

    def test_repo_wide_run_does_not_crash_and_passes(self) -> None:
        result = validate_paths([BENCHMARK_CHALLENGES, EXPERIMENTS_ROOT])

        self.assertTrue(result.ok, result.errors)
        self.assertGreaterEqual(result.checked_challenges, 3)
        # The AP-4 Model-Lab replication-series skeleton introduces the first
        # explicitly activated Model-Lab decision; historical decisions still do
        # not opt in, so the repo-wide run stays green with >= 1 activated.
        self.assertGreaterEqual(result.activated_decisions, 1)

    def test_activation_rule_is_narrow(self) -> None:
        self.assertTrue(
            decision_requires_challenge_version({"model_lab_control": True})
        )
        self.assertTrue(
            decision_requires_challenge_version({"comparability_scope": "model_lab"})
        )
        self.assertTrue(
            decision_requires_challenge_version(
                {"decision_type": "model_lab_comparison"}
            )
        )
        self.assertTrue(
            decision_requires_challenge_version({"challenge_version_required": True})
        )
        # Legacy / unrelated values must NOT activate (protects existing decisions).
        self.assertFalse(
            decision_requires_challenge_version(
                {"comparability_scope": "same outcome-evidence gate family"}
            )
        )
        self.assertFalse(
            decision_requires_challenge_version(
                {"decision_type": "execution_assessment"}
            )
        )
        self.assertFalse(
            decision_requires_challenge_version({"model_lab_control": False})
        )
        self.assertFalse(decision_requires_challenge_version({}))

    def test_activated_decision_challenge_id_mismatch_fails(self) -> None:
        registry = build_challenge_registry([VALID_CHALLENGE])
        with tempfile.TemporaryDirectory() as tmp:
            decision = Path(tmp) / "decisions" / "decision.yml"
            decision.parent.mkdir(parents=True)
            decision.write_text(
                "decision_type: model_lab_comparison\n"
                "challenge_id: kanban-board\n"
                "challenge_version: rest-api-v1\n",
                encoding="utf-8",
            )
            errors = validate_decision_file(decision, registry)

        self.assertTrue(errors)
        self.assertTrue(any("does not match challenge_id" in error for error in errors))

    def test_activated_decision_matching_challenge_id_passes(self) -> None:
        registry = build_challenge_registry([VALID_CHALLENGE])
        with tempfile.TemporaryDirectory() as tmp:
            decision = Path(tmp) / "decisions" / "decision.yml"
            decision.parent.mkdir(parents=True)
            decision.write_text(
                "decision_type: model_lab_comparison\n"
                "challenge_id: rest-api\n"
                "challenge_version: rest-api-v1\n",
                encoding="utf-8",
            )
            errors = validate_decision_file(decision, registry)

        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
