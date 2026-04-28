#!/usr/bin/env python3
"""Regression tests for validate_agent_commands.py."""

from __future__ import annotations

import unittest
from pathlib import Path

import validate_agent_commands as vac


class ValidateAgentCommandsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture_root = vac.REPO_ROOT / "tests" / "fixtures" / "agent_commands"

    def _validator_for(self, command: str) -> object:
        return vac.load_validator(vac.schema_path_for(command))

    # Schemas load cleanly ------------------------------------------------
    def test_all_command_schemas_load(self) -> None:
        for command in vac.COMMANDS:
            with self.subTest(command=command):
                self.assertTrue(vac.schema_path_for(command).is_file())
                # Must not raise.
                self._validator_for(command)

    # read_context --------------------------------------------------------
    def test_read_context_valid_minimal(self) -> None:
        validator = self._validator_for("read_context")
        path = self.fixture_root / "read_context" / "valid-minimal.json"
        self.assertEqual(vac.validate_one(path, validator), [])

    def test_read_context_contract_invalid_empty_target_files(self) -> None:
        validator = self._validator_for("read_context")
        path = self.fixture_root / "read_context" / "contract-invalid-empty-target-files.json"
        errors = vac.validate_one(path, validator)
        self.assertTrue(errors)
        self.assertIn("contract_invalid", errors[0])

    def test_read_context_contract_invalid_wrong_command(self) -> None:
        validator = self._validator_for("read_context")
        path = self.fixture_root / "read_context" / "contract-invalid-wrong-command.json"
        errors = vac.validate_one(path, validator)
        self.assertTrue(errors)
        self.assertIn("contract_invalid", errors[0])

    # write_change --------------------------------------------------------
    def test_write_change_valid_minimal(self) -> None:
        validator = self._validator_for("write_change")
        path = self.fixture_root / "write_change" / "valid-minimal.json"
        self.assertEqual(vac.validate_one(path, validator), [])

    def test_write_change_contract_invalid_missing_locator(self) -> None:
        validator = self._validator_for("write_change")
        path = self.fixture_root / "write_change" / "contract-invalid-missing-locator.json"
        errors = vac.validate_one(path, validator)
        self.assertTrue(errors)
        self.assertIn("contract_invalid", errors[0])

    def test_write_change_contract_invalid_wrong_version(self) -> None:
        validator = self._validator_for("write_change")
        path = self.fixture_root / "write_change" / "contract-invalid-wrong-version.json"
        errors = vac.validate_one(path, validator)
        self.assertTrue(errors)
        self.assertIn("contract_invalid", errors[0])

    # validate_change -----------------------------------------------------
    def test_validate_change_valid_success(self) -> None:
        validator = self._validator_for("validate_change")
        path = self.fixture_root / "validate_change" / "valid-success.json"
        self.assertEqual(vac.validate_one(path, validator), [])

    def test_validate_change_valid_failure(self) -> None:
        validator = self._validator_for("validate_change")
        path = self.fixture_root / "validate_change" / "valid-failure.json"
        self.assertEqual(vac.validate_one(path, validator), [])

    def test_validate_change_contract_invalid_success_with_errors(self) -> None:
        validator = self._validator_for("validate_change")
        path = (
            self.fixture_root
            / "validate_change"
            / "contract-invalid-success-with-errors.json"
        )
        errors = vac.validate_one(path, validator)
        self.assertTrue(errors)
        self.assertIn("contract_invalid", errors[0])

    def test_validate_change_contract_invalid_failure_empty_errors(self) -> None:
        validator = self._validator_for("validate_change")
        path = (
            self.fixture_root
            / "validate_change"
            / "contract-invalid-failure-empty-errors.json"
        )
        errors = vac.validate_one(path, validator)
        self.assertTrue(errors)
        self.assertIn("contract_invalid", errors[0])

    def test_validate_change_contract_invalid_wrong_version(self) -> None:
        """validate_change with version 'v0.2' must yield contract_invalid (const violation).

        This is the Phase E gap that was previously marked covered: false in the
        fixture-matrix (section 1.3 validate_change).
        """
        validator = self._validator_for("validate_change")
        path = (
            self.fixture_root
            / "validate_change"
            / "contract-invalid-wrong-version.json"
        )
        errors = vac.validate_one(path, validator)
        self.assertTrue(errors)
        self.assertIn("contract_invalid", errors[0])

    # Helpers -------------------------------------------------------------
    def test_detect_expected_error_supported_only(self) -> None:
        path = (
            self.fixture_root
            / "read_context"
            / "contract-invalid-empty-target-files.json"
        )
        self.assertEqual(vac.detect_expected_error(path), "contract_invalid")

    def test_display_path_internal_and_external(self) -> None:
        internal = vac.REPO_ROOT / "schemas" / "command.read_context.schema.json"
        external = (
            vac.REPO_ROOT.parent / "__outside_repo__" / "x.json"
        ).resolve()
        self.assertEqual(
            vac.display_path(internal),
            "schemas/command.read_context.schema.json",
        )
        self.assertEqual(vac.display_path(external), str(external))


if __name__ == "__main__":
    unittest.main()
