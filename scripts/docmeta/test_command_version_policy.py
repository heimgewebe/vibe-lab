#!/usr/bin/env python3
"""Policy tests for v0.1 command and chain versioning."""

from __future__ import annotations

import json
import unittest

from jsonschema import ValidationError

import validate_agent_commands as vac
import validate_command_chain as vcc


CHAIN_FIXTURES = vcc.REPO_ROOT / "tests" / "fixtures" / "command_chains"
COMMAND_FIXTURES = vac.REPO_ROOT / "tests" / "fixtures" / "agent_commands"
CONTRACT_PATH = vcc.REPO_ROOT / "contracts" / "command-semantics.md"


def _load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _minimal_valid_chain() -> list[dict[str, object]]:
    return [
        {
            "command": "read_context",
            "version": "v0.1",
            "target_files": ["docs/index.md"],
        },
        {
            "command": "write_change",
            "version": "v0.1",
            "target_files": ["docs/index.md"],
            "locator": "## Einstieg",
            "change_type": "modify",
            "forbidden_changes": [],
        },
        {
            "command": "validate_change",
            "version": "v0.1",
            "checks": ["lint"],
            "success": True,
            "errors": [],
        },
    ]


def _contains_contract_invalid(errors: list[str]) -> bool:
    return any("contract_invalid" in error for error in errors)


class CommandVersionPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.chain_validators = vcc._validators_by_command()

    def test_consistent_v01_chain_is_valid(self) -> None:
        chain = _minimal_valid_chain()

        errors = vcc.validate_chain(chain, "inline-valid", self.chain_validators)

        self.assertFalse(
            errors,
            f"expected no errors for consistent v0.1 chain, got: {errors}",
        )

    def test_mixed_versions_constructed_inline_is_policy_invalid(self) -> None:
        chain = _minimal_valid_chain()
        chain[1]["version"] = "v0.2"

        errors = vcc.validate_chain(chain, "inline-mixed-versions", self.chain_validators)

        codes = {error.code for error in errors}
        self.assertIn("command_sequence_invalid", codes)
        self.assertIn("contract_invalid", codes)

    def test_mixed_versions_policy_fixture_remains_invalid(self) -> None:
        chain = _load_json(CHAIN_FIXTURES / "invalid-mixed-versions.json")
        errors = vcc.validate_chain(
            chain,
            "invalid-mixed-versions.json",
            self.chain_validators,
        )
        codes = {error.code for error in errors}
        self.assertIn("command_sequence_invalid", codes)
        self.assertIn("contract_invalid", codes)

    def test_missing_version_policy_fixture_is_contract_invalid(self) -> None:
        validator = vac.load_validator(vac.schema_path_for("read_context"))
        path = COMMAND_FIXTURES / "read_context" / "contract-invalid-missing-version.json"
        errors = vac.validate_one(path, validator)
        self.assertTrue(errors)
        self.assertTrue(
            _contains_contract_invalid(errors),
            "expected at least one contract_invalid error",
        )

    def test_missing_version_constructed_inline_is_contract_invalid(self) -> None:
        validator = vac.load_validator(vac.schema_path_for("read_context"))
        path = COMMAND_FIXTURES / "read_context" / "valid-minimal.json"
        record = _load_json(path)
        record.pop("version")

        with self.assertRaises(ValidationError) as ctx:
            validator.validate(record)

        self.assertIn("'version'", str(ctx.exception))

    def test_wrong_version_policy_fixture_is_contract_invalid(self) -> None:
        validator = vac.load_validator(vac.schema_path_for("write_change"))
        path = COMMAND_FIXTURES / "write_change" / "contract-invalid-wrong-version.json"
        errors = vac.validate_one(path, validator)
        self.assertTrue(errors)
        self.assertTrue(
            _contains_contract_invalid(errors),
            "expected at least one contract_invalid error",
        )

    def test_wrong_version_constructed_inline_is_contract_invalid(self) -> None:
        validator = vac.load_validator(vac.schema_path_for("write_change"))
        path = COMMAND_FIXTURES / "write_change" / "valid-minimal.json"
        record = _load_json(path)
        record["version"] = "v0.2"

        with self.assertRaises(ValidationError) as ctx:
            validator.validate(record)

        self.assertIn("'v0.1' was expected", str(ctx.exception))

    def test_contract_documents_version_policy_markers(self) -> None:
        contract = CONTRACT_PATH.read_text(encoding="utf-8")
        self.assertIn("## Versionsstrategie", contract)
        self.assertIn("v0.1", contract)
        self.assertIn("command_sequence_invalid", contract)
        self.assertIn("contract_invalid", contract)


if __name__ == "__main__":
    unittest.main()