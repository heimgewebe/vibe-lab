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
import tempfile
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

    def test_minimal_chain_add_is_accepted(self) -> None:
        """Near-positive contrast for empty-asserted-state class.

        Same shape as ``empty_change_state`` (``change_type=add`` with
        ``exact_after`` set on both handoff and write_change), but
        ``exact_after`` carries non-empty content. Must validate cleanly,
        proving the new rule does not over-reach to non-empty post-states.
        """
        handoff, chain, expected = _load("valid/minimal_chain_add.json")
        self.assertEqual(expected, [])
        errors = vcc.validate_cross_contract(
            handoff, chain, "valid/minimal_chain_add.json", self.validators
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
        """Handoff targets file A, chain operates on file B (missing coverage)."""
        observed, expected = self._observed("invalid/target_drift.json")
        self.assertIn("handoff_target_drift", observed)
        self.assertEqual(observed, expected)

    def test_target_drift_extra_fails(self) -> None:
        """Chain write_change includes a file not listed in handoff.target_files."""
        observed, expected = self._observed("invalid/target_drift_extra.json")
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

    def test_empty_change_state_fails(self) -> None:
        """Empty asserted state: ``change_type=add`` with ``exact_after=""``
        passes the schema but asserts a vacuous post-state.

        Phase 2 (Semantic Contradiction) class **empty asserted state**:
        when an ``exact_*`` field is present on the side that the
        ``change_type`` semantically asserts (``add → exact_after``,
        ``remove → exact_before``, ``modify``/``replace`` → both), the
        value must not be the empty string. The negative fixture isolates
        exactly this invariant; the near-positive contrast
        (``valid/minimal_chain_add.json``) validates cleanly.
        """
        observed, expected = self._observed("invalid/empty_change_state.json")
        self.assertIn("semantic_contradiction", observed)
        self.assertEqual(observed, expected)

    def test_version_conflict_fails(self) -> None:
        """Mixed command versions in the chain."""
        observed, expected = self._observed("invalid/version_conflict.json")
        self.assertIn("command_sequence_invalid", observed)
        self.assertEqual(observed, expected)

    def test_state_drift_fails(self) -> None:
        """Handoff pins exact_before/exact_after; write_change silently omits them."""
        observed, expected = self._observed("invalid/state_drift.json")
        self.assertIn("handoff_state_drift", observed)
        self.assertEqual(observed, expected)

    def test_locator_drift_fails(self) -> None:
        """Locator drift between handoff and write_change must be detected.

        Validates the ``handoff_locator_drift`` cross-contract invariant:
        when ``handoff.locator`` and ``write_change.locator`` are both set
        but carry divergent values, the validator must emit
        ``handoff_locator_drift``.

        Fixture design note: all fields mirror the valid minimal baseline,
        except that ``handoff.locator`` and ``write_change.locator`` carry
        deliberately divergent values to isolate exactly one violated invariant.
        """
        observed, expected = self._observed(
            "invalid/handoff_locator_drift/locator_drift.json"
        )
        self.assertIn("handoff_locator_drift", observed)
        self.assertEqual(observed, expected)

    def test_handoff_contract_invalid_fails(self) -> None:
        """Handoff itself violates agent.handoff.schema.json (missing 'status')."""
        observed, expected = self._observed("invalid/contract_invalid.json")
        self.assertIn("handoff_contract_invalid", observed)
        self.assertEqual(observed, expected)

    def test_handoff_contract_invalid_short_circuits(self) -> None:
        """When the handoff is schema-invalid, no cross-contract codes are emitted.

        Rationale: cross-contract checks read fields the schema has not
        blessed. Short-circuiting prevents false secondary errors from
        unstructured handoff data.
        """
        handoff, chain, _ = _load("invalid/contract_invalid.json")
        errors = vcc.validate_cross_contract(
            handoff, chain, "invalid/contract_invalid.json", self.validators
        )
        codes = {e.code for e in errors}
        cross_contract_codes = {
            "handoff_target_drift",
            "handoff_intent_mismatch",
            "handoff_state_drift",
        }
        self.assertIn("handoff_contract_invalid", codes)
        self.assertTrue(
            codes.isdisjoint(cross_contract_codes),
            f"cross-contract codes emitted after handoff_contract_invalid: "
            f"{codes & cross_contract_codes}",
        )


class CrossContractLoaderTests(unittest.TestCase):
    """Guards the fixture loader against malformed input."""

    def test_malformed_chain_element_is_setup_error(self) -> None:
        """A chain element that is not a JSON object must produce exit code 2.

        Rationale: a non-dict element would cause a silent AttributeError or
        TypeError later in the validator. The loader must catch it early and
        abort cleanly.
        """
        fixture_data = {
            "handoff": {
                "status": "PASS",
                "target_files": ["docs/index.md"],
                "locator": "## Laufende Versuche",
                "change_type": "modify",
                "scope": "test",
                "normalized_task": "test",
                "critic_signature": "experiment-critic/v1",
                "handoff": {
                    "algo": "sha256",
                    "canon": "v1",
                    "hash": "0b327ba0e3a38afed841659cce2fc2a34c738a66cc73e2083a903ef8b6838fea",
                },
            },
            "chain": [42, "not_a_dict"],
            "expected_errors": [],
        }
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as fh:
            json.dump(fixture_data, fh)
            tmp = Path(fh.name)
        try:
            with self.assertRaises(SystemExit) as ctx:
                vcc.load_cross_contract_fixture(tmp)
            self.assertEqual(ctx.exception.code, 2)
        finally:
            tmp.unlink(missing_ok=True)


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
