#!/usr/bin/env python3
"""Tests for validate_artifact_taxonomy.py."""

from __future__ import annotations

import copy
import unittest

from validate_artifact_taxonomy import validate


VALID_TAXONOMY = {
    "schema_version": "1.0.0",
    "contract": "artifact_taxonomy",
    "contract_status": "diagnostic",
    "layers": ["governance", "experiment", "docs", "generated", "export", "test"],
    "authorities": [
        "sovereign_source", "normative_contract", "procedure_contract",
        "evidence_log", "decision_record", "diagnostic_signal",
        "navigation_surface", "generated_projection", "implementation_behavior",
        "test_expectation", "runtime_observation", "raw_capture",
        "historical_record", "result_interpretation", "unknown",
    ],
    "rules": [
        {
            "pattern": "repo.meta.yaml",
            "layer": "governance",
            "kind": "sovereign_source",
            "authority": "sovereign_source",
            "lifecycle": "handcrafted",
            "enforcement": ["owner_required"],
            "origin": "handcrafted",
        },
        {
            "pattern": "experiments/*/results/evidence.jsonl",
            "layer": "experiment",
            "kind": "evidence_log",
            "authority": "evidence_log",
            "lifecycle": "append_only",
            "enforcement": ["no_rewrite"],
            "origin": "handcrafted",
        },
    ],
}


class TaxonomyValidatorTest(unittest.TestCase):
    def test_valid_taxonomy(self) -> None:
        self.assertEqual(validate(copy.deepcopy(VALID_TAXONOMY)), [])

    def test_missing_contract_field_rejected(self) -> None:
        data = copy.deepcopy(VALID_TAXONOMY)
        data["contract"] = "wrong_contract"
        errors = validate(data)
        self.assertTrue(any("contract" in e for e in errors), errors)

    def test_empty_layers_rejected(self) -> None:
        data = copy.deepcopy(VALID_TAXONOMY)
        data["layers"] = []
        errors = validate(data)
        self.assertTrue(any("layers" in e for e in errors), errors)

    def test_empty_rules_rejected(self) -> None:
        data = copy.deepcopy(VALID_TAXONOMY)
        data["rules"] = []
        errors = validate(data)
        self.assertTrue(any("rules" in e for e in errors), errors)

    def test_rule_missing_pattern_rejected(self) -> None:
        data = copy.deepcopy(VALID_TAXONOMY)
        del data["rules"][0]["pattern"]
        errors = validate(data)
        self.assertTrue(any("'pattern'" in e for e in errors), errors)

    def test_rule_unknown_layer_rejected(self) -> None:
        data = copy.deepcopy(VALID_TAXONOMY)
        data["rules"][0]["layer"] = "made_up_layer"
        errors = validate(data)
        self.assertTrue(any("unknown layer" in e for e in errors), errors)

    def test_rule_unknown_authority_rejected(self) -> None:
        data = copy.deepcopy(VALID_TAXONOMY)
        data["rules"][0]["authority"] = "not_a_real_authority"
        errors = validate(data)
        self.assertTrue(any("unknown authority" in e for e in errors), errors)

    def test_rule_enforcement_not_list_rejected(self) -> None:
        data = copy.deepcopy(VALID_TAXONOMY)
        data["rules"][0]["enforcement"] = "string_not_list"
        errors = validate(data)
        self.assertTrue(any("must be a list" in e for e in errors), errors)

    def test_rule_missing_required_field_rejected(self) -> None:
        data = copy.deepcopy(VALID_TAXONOMY)
        del data["rules"][0]["lifecycle"]
        errors = validate(data)
        self.assertTrue(any("'lifecycle'" in e for e in errors), errors)

    def test_mapping_in_layers_rejected(self) -> None:
        data = copy.deepcopy(VALID_TAXONOMY)
        data["layers"] = ["governance", {"not": "a string"}]
        errors = validate(data)
        self.assertTrue(
            any("must be a non-empty string" in e for e in errors), errors
        )

    def test_mapping_in_authorities_rejected(self) -> None:
        data = copy.deepcopy(VALID_TAXONOMY)
        data["authorities"] = [{"not": "a string"}, "sovereign_source"]
        errors = validate(data)
        self.assertTrue(
            any("must be a non-empty string" in e for e in errors), errors
        )

    def test_mapping_in_layers_does_not_crash(self) -> None:
        """set(layers) with unhashable dicts would crash; validate() must not."""
        data = copy.deepcopy(VALID_TAXONOMY)
        data["layers"] = [{"unhashable": "dict"}]
        errors = validate(data)
        self.assertIsInstance(errors, list)
        self.assertTrue(len(errors) > 0)


if __name__ == "__main__":
    unittest.main()
