#!/usr/bin/env python3
"""Regression tests for validate_command_chain.py."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

import validate_command_chain as vcc


CHAIN_FIXTURES = vcc.REPO_ROOT / "tests" / "fixtures" / "command_chains"


def _chain(name: str) -> list[dict]:
    return json.loads((CHAIN_FIXTURES / name).read_text(encoding="utf-8"))


class ChainValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validators = vcc._validators_by_command()

    def test_valid_minimal_passes(self) -> None:
        chain = _chain("valid-minimal.json")
        errors = vcc.validate_chain(chain, "valid-minimal.json", self.validators)
        self.assertEqual(errors, [])

    def test_wrong_order_detects_sequence_violation(self) -> None:
        chain = _chain("invalid-wrong-order.json")
        errors = vcc.validate_chain(
            chain, "invalid-wrong-order.json", self.validators
        )
        codes = {e.code for e in errors}
        self.assertIn("command_sequence_invalid", codes)

    def test_target_files_mismatch_detected(self) -> None:
        chain = _chain("invalid-target-files-mismatch.json")
        errors = vcc.validate_chain(
            chain, "invalid-target-files-mismatch.json", self.validators
        )
        codes = {e.code for e in errors}
        self.assertIn("target_files_mismatch", codes)

    def test_semantic_contradiction_remove_with_exact_after(self) -> None:
        chain = _chain("invalid-remove-with-exact-after.json")
        errors = vcc.validate_chain(
            chain,
            "invalid-remove-with-exact-after.json",
            self.validators,
        )
        codes = {e.code for e in errors}
        self.assertIn("semantic_contradiction", codes)

    def test_mixed_versions_yields_sequence_invalid(self) -> None:
        chain = _chain("invalid-mixed-versions.json")
        errors = vcc.validate_chain(
            chain, "invalid-mixed-versions.json", self.validators
        )
        codes = {e.code for e in errors}
        self.assertIn("command_sequence_invalid", codes)
        # The v0.2 record is also schema-invalid (const "v0.1"):
        self.assertIn("contract_invalid", codes)

    def test_chain_error_rejects_unknown_code(self) -> None:
        with self.assertRaises(ValueError):
            vcc.ChainError(
                code="made_up_code",
                message="x",
                command_index=0,
                path="x",
            )

    def test_chain_error_codes_align_with_contract(self) -> None:
        contract = (vcc.REPO_ROOT / "contracts" / "command-semantics.md").read_text(
            encoding="utf-8"
        )
        for code in vcc.ERROR_CODES:
            self.assertIn(
                code,
                contract,
                f"error code {code!r} not documented in command-semantics.md",
            )

    def test_semantic_add_with_exact_before_detected(self) -> None:
        chain = [
            {
                "command": "read_context",
                "version": "v0.1",
                "target_files": ["docs/index.md"],
            },
            {
                "command": "write_change",
                "version": "v0.1",
                "target_files": ["docs/index.md"],
                "locator": "## X",
                "change_type": "add",
                "exact_before": "old\n",
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
        errors = vcc.validate_chain(chain, "synthetic", self.validators)
        codes = {e.code for e in errors}
        self.assertIn("semantic_contradiction", codes)

    def test_duplicate_target_files_detected(self) -> None:
        chain = [
            {
                "command": "read_context",
                "version": "v0.1",
                "target_files": ["docs/index.md", "docs/index.md"],
            },
            {
                "command": "write_change",
                "version": "v0.1",
                "target_files": ["docs/index.md"],
                "locator": "## X",
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
        errors = vcc.validate_chain(chain, "synthetic", self.validators)
        codes = {e.code for e in errors}
        self.assertIn("semantic_contradiction", codes)


if __name__ == "__main__":
    unittest.main()
