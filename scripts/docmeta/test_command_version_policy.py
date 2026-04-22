#!/usr/bin/env python3
"""Policy tests for v0.1 command and chain versioning."""

from __future__ import annotations

import json
import re
import unittest

import validate_agent_commands as vac
import validate_command_chain as vcc


CHAIN_FIXTURES = vcc.REPO_ROOT / "tests" / "fixtures" / "command_chains"
COMMAND_FIXTURES = vac.REPO_ROOT / "tests" / "fixtures" / "agent_commands"
CONTRACT_PATH = vcc.REPO_ROOT / "contracts" / "command-semantics.md"


def _load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


class CommandVersionPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.chain_validators = vcc._validators_by_command()

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
        self.assertIn("contract_invalid", errors[0])

    def test_wrong_version_policy_fixture_is_contract_invalid(self) -> None:
        validator = vac.load_validator(vac.schema_path_for("write_change"))
        path = COMMAND_FIXTURES / "write_change" / "contract-invalid-wrong-version.json"
        errors = vac.validate_one(path, validator)
        self.assertTrue(errors)
        self.assertIn("contract_invalid", errors[0])

    def test_contract_documents_version_policy_markers(self) -> None:
        contract = CONTRACT_PATH.read_text(encoding="utf-8").lower()
        self.assertIn("v0.1", contract)
        self.assertRegex(contract, r"gemischte versionen|mixed versions")
        self.assertIn("command_sequence_invalid", contract)
        self.assertIn("contract_invalid", contract)


if __name__ == "__main__":
    unittest.main()