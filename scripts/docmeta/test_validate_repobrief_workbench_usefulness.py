from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import yaml

from validate_repobrief_workbench_usefulness import (  # noqa: E402
    DEFAULT_PLAN,
    validate_measurement_plan,
)


class RepoBriefWorkbenchUsefulnessValidationTest(unittest.TestCase):
    def load_plan(self) -> dict:
        return yaml.safe_load(DEFAULT_PLAN.read_text(encoding="utf-8"))

    def write_plan(self, data: dict) -> Path:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        path = Path(temp.name) / "measurement-plan.yml"
        path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
        return path

    def test_canonical_plan_is_valid(self) -> None:
        self.assertEqual(validate_measurement_plan(), [])

    def test_missing_required_condition_is_rejected(self) -> None:
        data = self.load_plan()
        data["conditions"].pop("trace_gated")
        errors = validate_measurement_plan(self.write_plan(data))
        self.assertIn("missing required conditions: trace_gated", errors)

    def test_full_resolved_evidence_cannot_be_default_candidate(self) -> None:
        data = self.load_plan()
        data["conditions"]["full_resolved_evidence"]["default_candidate"] = True
        errors = validate_measurement_plan(self.write_plan(data))
        self.assertIn("full_resolved_evidence must not be a default candidate", errors)

    def test_false_confidence_fields_are_required(self) -> None:
        data = self.load_plan()
        data["metrics"]["false_confidence_risk"]["required_fields"].remove(
            "hallucinated_path_count"
        )
        errors = validate_measurement_plan(self.write_plan(data))
        self.assertTrue(any("hallucinated_path_count" in error for error in errors))

    def test_no_self_proof_rule_is_required(self) -> None:
        data = self.load_plan()
        data["no_self_proof_rule"]["required"] = False
        errors = validate_measurement_plan(self.write_plan(data))
        self.assertIn("no_self_proof_rule.required must be true", errors)

    def test_pre_execution_promotion_is_rejected(self) -> None:
        data = self.load_plan()
        data["promotion_gate"]["default_access_may_be_promoted"] = True
        errors = validate_measurement_plan(self.write_plan(data))
        self.assertIn("pre-execution design must not promote default workbench access", errors)

    def test_disallowed_claims_include_merge_readiness(self) -> None:
        data = self.load_plan()
        data["promotion_gate"]["disallowed_pre_execution_claims"].remove("merge readiness")
        errors = validate_measurement_plan(self.write_plan(data))
        self.assertTrue(any("merge readiness" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
