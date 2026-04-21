#!/usr/bin/env python3
"""End-to-end cross-contract test: HANDOFF_BLOCK → Command Chain → Validation.

The purpose of this module is not to prove functionality but to prove
**consistency between contracts**. Each test asserts that the existing
validators — without invented logic, without implicit defaults — detect
drift between the three cooperating contracts:

* ``schemas/agent.handoff.schema.json``
* ``schemas/command.*.schema.json``
* ``contracts/command-semantics.md`` (operationalized by
  ``scripts/docmeta/validate_command_chain.py``)

Fixture files live under ``tests/fixtures/cross_contract/{valid,invalid}/``
and follow the shape ``{handoff, chain, expected_errors?}``.
"""

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts" / "docmeta"))

import validate_command_chain as vcc  # noqa: E402

FIXTURES = REPO_ROOT / "tests" / "fixtures" / "cross_contract"


def _load(relative: str) -> tuple[dict, list[dict], list[str]]:
    path = FIXTURES / relative
    return vcc.load_cross_contract_fixture(path)


class CrossContractPositiveTests(unittest.TestCase):
    """A valid handoff + derived chain must validate cleanly with no
    implicit defaults and no invented fields."""

    def setUp(self) -> None:
        self.validators = vcc._validators_by_command()

    def test_minimal_chain_is_accepted(self) -> None:
        handoff, chain, expected = _load("valid/minimal_chain.json")
        self.assertEqual(expected, [])  # fixture declares no expected errors
        errors = vcc.validate_cross_contract(
            handoff, chain, "valid/minimal_chain.json", self.validators
        )
        self.assertEqual(errors, [])

    def test_no_implicit_defaults_are_injected(self) -> None:
        """Validation must not mutate handoff or chain (no silent
        defaults, no field invention)."""
        handoff, chain, _ = _load("valid/minimal_chain.json")
        handoff_snapshot = copy.deepcopy(handoff)
        chain_snapshot = copy.deepcopy(chain)
        vcc.validate_cross_contract(
            handoff, chain, "valid/minimal_chain.json", self.validators
        )
        self.assertEqual(handoff, handoff_snapshot)
        self.assertEqual(chain, chain_snapshot)


class CrossContractNegativeTests(unittest.TestCase):
    """Four independent negative classes. Each class must fail for a
    named reason that is visible in the code, not inferred by heuristic."""

    def setUp(self) -> None:
        self.validators = vcc._validators_by_command()

    def _observed(self, relative: str) -> tuple[list[str], list[str]]:
        handoff, chain, expected = _load(relative)
        errors = vcc.validate_cross_contract(
            handoff, chain, relative, self.validators
        )
        observed_codes = sorted({e.code for e in errors})
        return observed_codes, sorted(set(expected))

    def test_target_drift_fails(self) -> None:
        """Handoff targets file A, chain operates on file B."""
        observed, expected = self._observed("invalid/target_drift.json")
        self.assertIn("handoff_target_drift", observed)
        self.assertEqual(observed, expected)

    def test_semantic_mismatch_fails(self) -> None:
        """Handoff requires a change; chain contains only read/validate."""
        observed, expected = self._observed("invalid/semantic_mismatch.json")
        self.assertIn("handoff_intent_mismatch", observed)
        self.assertEqual(observed, expected)

    def test_contradiction_fails(self) -> None:
        """Chain is formally valid but semantically contradictory
        (remove with exact_after set)."""
        observed, expected = self._observed("invalid/contradiction.json")
        self.assertIn("semantic_contradiction", observed)
        self.assertEqual(observed, expected)

    def test_version_conflict_fails(self) -> None:
        """Mixed command versions in the chain."""
        observed, expected = self._observed("invalid/version_conflict.json")
        self.assertIn("command_sequence_invalid", observed)
        self.assertEqual(observed, expected)


class CrossContractErrorSurfaceTests(unittest.TestCase):
    """Guards against silent drift between the contract doc, the
    validator's ``ERROR_CODES``, and the fixture corpus."""

    def test_handoff_error_codes_are_in_contract(self) -> None:
        contract = (REPO_ROOT / "contracts" / "command-semantics.md").read_text(
            encoding="utf-8"
        )
        for code in (
            "handoff_contract_invalid",
            "handoff_target_drift",
            "handoff_intent_mismatch",
            "handoff_state_drift",
        ):
            self.assertIn(code, contract, f"missing from semantics doc: {code}")
            self.assertIn(code, vcc.ERROR_CODES)

    def test_all_invalid_fixtures_declare_expected_errors(self) -> None:
        for fixture in (FIXTURES / "invalid").glob("*.json"):
            data = json.loads(fixture.read_text(encoding="utf-8"))
            self.assertIn(
                "expected_errors", data, f"{fixture.name} missing expected_errors"
            )
            self.assertTrue(
                data["expected_errors"],
                f"{fixture.name} declares empty expected_errors",
            )


if __name__ == "__main__":
    unittest.main()
