#!/usr/bin/env python3
"""Regression tests for validate_agent_handoff.py."""

from __future__ import annotations

import unittest
from pathlib import Path

import validate_agent_handoff as vah


class ValidateAgentHandoffTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = vah.load_validator(vah.SCHEMA_PATH)
        self.fixture_dir = vah.REPO_ROOT / "tests" / "fixtures" / "agent_handoff"

    def test_canonical_payload_v1_normalizes_and_keeps_locator_spacing(self) -> None:
        handoff = {
            "status": " PASS ",
            "target_files": [" b.py ", "a.py", "a.py", ""],
            "locator": "  line  42\r\nwith   spaces  ",
            "change_type": " modify ",
            "scope": "  alpha\r\n\t beta   gamma  ",
            "normalized_task": "\n  foo   bar\tbaz  ",
        }

        payload = vah.canonical_payload_v1(handoff)

        self.assertEqual(payload["status"], "PASS")
        self.assertEqual(payload["target_files"], ["a.py", "b.py"])
        self.assertEqual(payload["scope"], "alpha beta gamma")
        self.assertEqual(payload["normalized_task"], "foo bar baz")
        self.assertEqual(payload["locator"], "line  42\nwith   spaces")

    def test_compute_sha256_hex_is_deterministic(self) -> None:
        payload = {
            "status": "PASS",
            "target_files": ["a.py"],
            "locator": "x",
            "change_type": "add",
            "scope": "y",
            "normalized_task": "z",
        }
        first = vah.compute_sha256_hex(payload)
        second = vah.compute_sha256_hex(payload)
        self.assertEqual(first, second)

    def test_display_path_internal_and_external(self) -> None:
        internal = vah.REPO_ROOT / "schemas" / "agent.handoff.schema.json"
        external = (vah.REPO_ROOT.parent / "__outside_repo__" / "agent-handoff-outside.json").resolve()

        self.assertEqual(vah.display_path(internal), "schemas/agent.handoff.schema.json")
        self.assertEqual(vah.display_path(external), str(external))

    def test_validate_one_pass_fixture(self) -> None:
        path = self.fixture_dir / "pass-minimal.json"
        errors = vah.validate_one(path, self.validator)
        self.assertEqual(errors, [])

    def test_validate_one_hash_mismatch_fixture(self) -> None:
        path = self.fixture_dir / "hash-mismatch.json"
        errors = vah.validate_one(path, self.validator)
        self.assertTrue(errors)
        self.assertIn("hash_mismatch", errors[0])

    def test_validate_one_contract_invalid_fixture(self) -> None:
        path = self.fixture_dir / "contract-invalid-missing-handoff.json"
        errors = vah.validate_one(path, self.validator)
        self.assertTrue(errors)
        self.assertIn("contract_invalid", errors[0])

    # Phase E: Drift-Fixtures --------------------------------------------------

    def test_validate_one_fail_missing_target_files(self) -> None:
        """FAIL status without target_files must yield contract_invalid."""
        path = self.fixture_dir / "fail-missing-target-files.json"
        errors = vah.validate_one(path, self.validator)
        self.assertTrue(errors)
        self.assertIn("contract_invalid", errors[0])

    def test_validate_one_partial_missing_locator(self) -> None:
        """PARTIAL status without locator must yield contract_invalid."""
        path = self.fixture_dir / "partial-missing-locator.json"
        errors = vah.validate_one(path, self.validator)
        self.assertTrue(errors)
        self.assertIn("contract_invalid", errors[0])

    def test_validate_one_unsupported_canon(self) -> None:
        """PASS with canon: 'v2' must yield contract_invalid (const violation)."""
        path = self.fixture_dir / "pass-unsupported-canon.json"
        errors = vah.validate_one(path, self.validator)
        self.assertTrue(errors)
        self.assertIn("contract_invalid", errors[0])

    def test_validate_one_normalized_task_drift(self) -> None:
        """PASS with drifted normalized_task must yield hash_mismatch."""
        path = self.fixture_dir / "pass-normalized-task-drift.json"
        errors = vah.validate_one(path, self.validator)
        self.assertTrue(errors)
        self.assertIn("hash_mismatch", errors[0])

    def test_validate_one_pass_with_exact_before_after(self) -> None:
        """PASS with exact_before/exact_after must pass; optional fields do not affect hash."""
        path = self.fixture_dir / "pass-with-exact-before-after.json"
        errors = vah.validate_one(path, self.validator)
        self.assertEqual(errors, [])

    def test_validate_one_promotion_near_valid(self) -> None:
        """Promotion-near-valid PASS with all optional fields must pass."""
        path = self.fixture_dir / "promotion-near-valid.json"
        errors = vah.validate_one(path, self.validator)
        self.assertEqual(errors, [])

    def test_validate_one_promotion_near_invalid(self) -> None:
        """Promotion-near-invalid: scope drifted after signing must yield hash_mismatch."""
        path = self.fixture_dir / "promotion-near-invalid.json"
        errors = vah.validate_one(path, self.validator)
        self.assertTrue(errors)
        self.assertIn("hash_mismatch", errors[0])


if __name__ == "__main__":
    unittest.main()