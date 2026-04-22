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

    def test_locator_continuity_v01_scope_empty_locator(self) -> None:
        """locator_continuity_violation is triggered by empty/whitespace locator.

        This test encodes the v0.1 boundary: only the empty-locator case
        is checked. A non-empty locator that has no corresponding entry in
        read_context.extracted_facts does NOT trigger
        locator_continuity_violation in v0.1.
        See contracts/command-semantics.md §Chain Invariants.
        """
        # A non-empty locator with no extracted_facts coupling must NOT raise
        # locator_continuity_violation in v0.1.
        chain_no_violation = [
            {
                "command": "read_context",
                "version": "v0.1",
                "target_files": ["docs/index.md"],
                "extracted_facts": ["some fact unrelated to locator"],
            },
            {
                "command": "write_change",
                "version": "v0.1",
                "target_files": ["docs/index.md"],
                "locator": "## A Section Not In extracted_facts",
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
        errors = vcc.validate_chain(chain_no_violation, "synthetic", self.validators)
        codes = {e.code for e in errors}
        self.assertNotIn(
            "locator_continuity_violation",
            codes,
            "v0.1 must NOT raise locator_continuity_violation for a valid "
            "non-empty locator that has no extracted_facts counterpart — "
            "that coupling is documented for v0.2 only.",
        )

    def test_unhashable_command_yields_contract_invalid_not_crash(self) -> None:
        """An unhashable command value must produce contract_invalid, not TypeError.

        Python's `in` test on a dict uses hashing; dict/list values as
        the command field would previously crash the validator.
        """
        for bad_command in ({}, [], {"cmd": "read_context"}):
            with self.subTest(command=bad_command):
                chain = [{"command": bad_command, "version": "v0.1"}]
                # Must not raise TypeError or any other exception.
                try:
                    errors = vcc.validate_chain(chain, "synthetic", self.validators)
                except TypeError as exc:
                    self.fail(
                        f"validate_chain raised TypeError for unhashable "
                        f"command {bad_command!r}: {exc}"
                    )
                codes = {e.code for e in errors}
                self.assertIn(
                    "contract_invalid",
                    codes,
                    f"Expected contract_invalid for unhashable command "
                    f"{bad_command!r}, got: {codes}",
                )

    def test_unhashable_version_handled_without_crash(self) -> None:
        """An unhashable version value must not crash _validate_version_consistency.

        Schema validation already covers this as contract_invalid, but the
        version-consistency check must not throw TypeError when building the
        set of seen versions.
        """
        for bad_version in ({"x": 1}, [1, 2], []):
            with self.subTest(version=bad_version):
                chain = [
                    {
                        "command": "read_context",
                        "version": bad_version,
                        "target_files": ["docs/index.md"],
                    }
                ]
                try:
                    vcc.validate_chain(chain, "synthetic", self.validators)
                except TypeError as exc:
                    self.fail(
                        f"validate_chain raised TypeError for unhashable "
                        f"version {bad_version!r}: {exc}"
                    )

    # ------------------------------------------------------------------
    # validate_error_unbindable: error-check binding seam (v0.1)
    # ------------------------------------------------------------------

    def _make_chain(self, validate_record: dict) -> list[dict]:
        """Helper: wrap validate_record in a minimal valid chain."""
        return [
            {
                "command": "read_context",
                "version": "v0.1",
                "target_files": ["src/main.py"],
            },
            {
                "command": "write_change",
                "version": "v0.1",
                "target_files": ["src/main.py"],
                "locator": "def main",
                "change_type": "modify",
                "forbidden_changes": [],
            },
            validate_record,
        ]

    def test_error_with_check_prefix_passes(self) -> None:
        """Errors bound via check prefix do not trigger validate_error_unbindable."""
        chain = self._make_chain(
            {
                "command": "validate_change",
                "version": "v0.1",
                "checks": ["lint", "test"],
                "success": False,
                "errors": [
                    "lint: E501 line too long",
                    "test: test_main failed assertion",
                ],
            }
        )
        errors = vcc.validate_chain(chain, "synthetic", self.validators)
        codes = {e.code for e in errors}
        self.assertNotIn("validate_error_unbindable", codes)

    def test_error_no_prefix_triggers_unbindable(self) -> None:
        """An error string with no check prefix triggers validate_error_unbindable."""
        chain = self._make_chain(
            {
                "command": "validate_change",
                "version": "v0.1",
                "checks": ["lint", "test"],
                "success": False,
                "errors": ["something went wrong"],
            }
        )
        errors = vcc.validate_chain(chain, "synthetic", self.validators)
        codes = {e.code for e in errors}
        self.assertIn("validate_error_unbindable", codes)

    def test_error_unknown_check_prefix_triggers_unbindable(self) -> None:
        """A prefix not in checks[] triggers validate_error_unbindable."""
        chain = self._make_chain(
            {
                "command": "validate_change",
                "version": "v0.1",
                "checks": ["lint"],
                "success": False,
                "errors": ["test: test_foo failed"],
            }
        )
        errors = vcc.validate_chain(chain, "synthetic", self.validators)
        codes = {e.code for e in errors}
        self.assertIn("validate_error_unbindable", codes)

    def test_error_partial_binding_triggers_unbindable(self) -> None:
        """One bound + one unbound error: unbound entry is still reported."""
        chain = self._make_chain(
            {
                "command": "validate_change",
                "version": "v0.1",
                "checks": ["lint", "docs-guard"],
                "success": False,
                "errors": [
                    "lint: trailing whitespace on line 42",
                    "broken link detected",
                ],
            }
        )
        errors = vcc.validate_chain(chain, "synthetic", self.validators)
        codes = {e.code for e in errors}
        self.assertIn("validate_error_unbindable", codes)
        unbindable = [e for e in errors if e.code == "validate_error_unbindable"]
        self.assertEqual(len(unbindable), 1, "exactly one unbound entry expected")
        self.assertIn("broken link detected", unbindable[0].message)

    def test_success_true_skips_binding_check(self) -> None:
        """success=True chains (with empty errors[]) are not checked."""
        chain = self._make_chain(
            {
                "command": "validate_change",
                "version": "v0.1",
                "checks": ["lint"],
                "success": True,
                "errors": [],
            }
        )
        errors = vcc.validate_chain(chain, "synthetic", self.validators)
        codes = {e.code for e in errors}
        self.assertNotIn("validate_error_unbindable", codes)

    def test_errors_fixture_with_check_prefix_passes(self) -> None:
        chain = _chain("valid-errors-with-check-prefix.json")
        errors = vcc.validate_chain(chain, "valid-errors-with-check-prefix.json", self.validators)
        self.assertEqual(errors, [])

    def test_errors_fixture_no_prefix_detected(self) -> None:
        chain = _chain("invalid-error-no-check-prefix.json")
        errors = vcc.validate_chain(chain, "invalid-error-no-check-prefix.json", self.validators)
        codes = {e.code for e in errors}
        self.assertIn("validate_error_unbindable", codes)

    def test_errors_fixture_unknown_prefix_detected(self) -> None:
        chain = _chain("invalid-error-unknown-check-prefix.json")
        errors = vcc.validate_chain(chain, "invalid-error-unknown-check-prefix.json", self.validators)
        codes = {e.code for e in errors}
        self.assertIn("validate_error_unbindable", codes)

    def test_errors_fixture_partial_binding_detected(self) -> None:
        chain = _chain("invalid-error-partial-binding.json")
        errors = vcc.validate_chain(chain, "invalid-error-partial-binding.json", self.validators)
        codes = {e.code for e in errors}
        self.assertIn("validate_error_unbindable", codes)


if __name__ == "__main__":
    unittest.main()
