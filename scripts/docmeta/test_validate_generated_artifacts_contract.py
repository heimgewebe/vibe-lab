#!/usr/bin/env python3
"""Tests for validate_generated_artifacts_contract.py."""

from __future__ import annotations

import copy
import unittest

from validate_generated_artifacts_contract import validate


VALID_CONTRACT = {
    "schema_version": "2.0.0",
    "contract": "generated_artifacts",
    "classes": {
        "diagnostic_report": {
            "description": "Generated diagnostic report.",
            "authority": "diagnostic_signal",
        },
        "generated_projection": {
            "description": "Tool-specific projection.",
            "authority": "generated_projection",
        },
    },
    "artifacts": [
        {
            "path": "docs/_generated/system-map.md",
            "class": "diagnostic_report",
            "generator": "scripts/docmeta/generate_system_map.py",
            "authority": "diagnostic_signal",
            "origin": "generated",
            "lifecycle": "regenerated",
            "enforcement": ["non_blocking_diagnostic", "no_manual_edit"],
            "activation": "always",
            "commit_policy": "optional",
            "ci_policy": "non_blocking",
        },
        {
            "path": "exports/copilot/",
            "class": "generated_projection",
            "generator": "scripts/exports/generate_exports.py",
            "derives_from": "instruction-blocks/*.md",
            "target_surface": "copilot",
            "authority": "generated_projection",
            "origin": "projected",
            "lifecycle": "regenerated",
            "enforcement": ["ci_blocking", "no_manual_edit"],
            "activation": "always",
            "deterministic": True,
            "regenerable": True,
            "commit_policy": "commit_required",
            "ci_policy": "blocking",
        },
    ],
}


class ContractValidatorTest(unittest.TestCase):
    def test_valid_contract(self) -> None:
        self.assertEqual(validate(copy.deepcopy(VALID_CONTRACT)), [])

    def test_legacy_bucket_rejected(self) -> None:
        data = copy.deepcopy(VALID_CONTRACT)
        data["canonical"] = {"files": ["docs/_generated/doc-index.md"]}
        errors = validate(data)
        self.assertTrue(any("'canonical'" in e for e in errors), errors)

    def test_legacy_root_key_rejected(self) -> None:
        data = copy.deepcopy(VALID_CONTRACT)
        data["generated_artifact_contract"] = {"derived": {"files": []}}
        errors = validate(data)
        self.assertTrue(
            any("generated_artifact_contract" in e for e in errors), errors
        )

    def test_missing_required_field_rejected(self) -> None:
        data = copy.deepcopy(VALID_CONTRACT)
        del data["artifacts"][0]["authority"]
        errors = validate(data)
        self.assertTrue(any("'authority'" in e for e in errors), errors)

    def test_unknown_class_rejected(self) -> None:
        data = copy.deepcopy(VALID_CONTRACT)
        data["artifacts"][0]["class"] = "made_up_class"
        errors = validate(data)
        self.assertTrue(any("unknown class" in e for e in errors), errors)

    def test_projection_without_derives_from_rejected(self) -> None:
        data = copy.deepcopy(VALID_CONTRACT)
        del data["artifacts"][1]["derives_from"]
        errors = validate(data)
        self.assertTrue(any("derives_from" in e for e in errors), errors)

    def test_projection_without_deterministic_rejected(self) -> None:
        data = copy.deepcopy(VALID_CONTRACT)
        data["artifacts"][1]["deterministic"] = False
        errors = validate(data)
        self.assertTrue(any("deterministic" in e for e in errors), errors)

    def test_duplicate_path_rejected(self) -> None:
        data = copy.deepcopy(VALID_CONTRACT)
        dup = copy.deepcopy(data["artifacts"][0])
        data["artifacts"].append(dup)
        errors = validate(data)
        self.assertTrue(any("duplicate artifact path" in e for e in errors), errors)

    def test_blocking_requires_commit_required(self) -> None:
        data = copy.deepcopy(VALID_CONTRACT)
        data["artifacts"][1]["commit_policy"] = "optional"
        errors = validate(data)
        self.assertTrue(
            any("commit_policy='commit_required'" in e for e in errors), errors
        )

    def test_no_manual_edit_required(self) -> None:
        data = copy.deepcopy(VALID_CONTRACT)
        data["artifacts"][0]["enforcement"] = ["non_blocking_diagnostic"]
        errors = validate(data)
        self.assertTrue(any("no_manual_edit" in e for e in errors), errors)

    def test_no_manual_edit_can_be_justified(self) -> None:
        data = copy.deepcopy(VALID_CONTRACT)
        data["artifacts"][0]["enforcement"] = ["non_blocking_diagnostic"]
        data["artifacts"][0]["manual_edit_justification"] = "explicitly editable"
        errors = validate(data)
        self.assertFalse(any("no_manual_edit" in e for e in errors), errors)

    def test_wrong_schema_version_rejected(self) -> None:
        data = copy.deepcopy(VALID_CONTRACT)
        data["schema_version"] = "0.1.0"
        errors = validate(data)
        self.assertTrue(any("schema_version" in e for e in errors), errors)

    def test_artifact_only_ephemeral_valid(self) -> None:
        data = copy.deepcopy(VALID_CONTRACT)
        data["classes"]["ephemeral_trace"] = {
            "description": "Short-lived runtime trace.",
            "authority": "runtime_observation",
        }
        data["artifacts"].append({
            "path": "docs/_generated/ephemeral-state.md",
            "class": "ephemeral_trace",
            "authority": "runtime_observation",
            "origin": "generated",
            "lifecycle": "regenerated",
            "enforcement": ["artifact_only", "no_manual_edit"],
            "activation": "always",
            "commit_policy": "do_not_commit",
            "ci_policy": "artifact_only",
        })
        self.assertEqual(validate(data), [])

    def test_unknown_authority_rejected(self) -> None:
        data = copy.deepcopy(VALID_CONTRACT)
        data["artifacts"][0]["authority"] = "not_a_real_authority"
        errors = validate(data)
        self.assertTrue(any("unknown authority" in e for e in errors), errors)

    def test_unknown_ci_policy_rejected(self) -> None:
        data = copy.deepcopy(VALID_CONTRACT)
        data["artifacts"][0]["ci_policy"] = "made_up_policy"
        errors = validate(data)
        self.assertTrue(any("unknown ci_policy" in e for e in errors), errors)

    def test_unknown_enforcement_value_rejected(self) -> None:
        data = copy.deepcopy(VALID_CONTRACT)
        data["artifacts"][0]["enforcement"] = ["no_manual_edit", "zombie_tag"]
        errors = validate(data)
        self.assertTrue(any("unknown enforcement value" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
