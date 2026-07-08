from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import yaml

from validate_rlens_agent_context_conditions import (  # noqa: E402
    DEFAULT_PLAN,
    validate_measurement_plan,
)


class RlensAgentContextConditionsTest(unittest.TestCase):
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

    def test_missing_condition_is_rejected(self) -> None:
        data = self.load_plan()
        data["conditions"].pop("trace_gated")
        errors = validate_measurement_plan(self.write_plan(data))
        self.assertIn("missing required conditions: trace_gated", errors)

    def test_full_dump_cannot_be_default_candidate(self) -> None:
        data = self.load_plan()
        data["conditions"]["full_dump"]["default_candidate"] = True
        errors = validate_measurement_plan(self.write_plan(data))
        self.assertIn("full_dump must be present but default_candidate: false", errors)

    def test_required_metrics_are_enforced(self) -> None:
        data = self.load_plan()
        data["metrics"].pop("hallucinated_path_count")
        errors = validate_measurement_plan(self.write_plan(data))
        self.assertTrue(any("hallucinated_path_count" in error for error in errors))

    def test_pre_execution_promotion_is_rejected(self) -> None:
        data = self.load_plan()
        data["promotion_gate"]["default_access_may_be_promoted"] = True
        errors = validate_measurement_plan(self.write_plan(data))
        self.assertIn("pre-execution design must not promote default access", errors)

    def test_directional_metrics_are_required_for_promotion_gate(self) -> None:
        data = self.load_plan()
        data["promotion_gate"]["minimum_evidence_before_promotion"][
            "required_directional_metrics"
        ] = ["unsupported_claim_count"]
        errors = validate_measurement_plan(self.write_plan(data))
        joined = "\n".join(errors)
        self.assertIn("hallucinated_path_count", joined)
        self.assertIn("missing_evidence_count", joined)
        self.assertIn("rework_count", joined)


if __name__ == "__main__":
    unittest.main()
