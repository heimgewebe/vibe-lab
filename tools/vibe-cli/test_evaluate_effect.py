#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("effect", Path(__file__).with_name("evaluate_effect.py"))
assert SPEC and SPEC.loader
EFFECT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EFFECT)


class EffectEvaluatorTests(unittest.TestCase):
    def registration(self, *, mode: str = "paired", minimum: int = 3, direction: str = "lower_is_better", threshold: float = 1.0) -> dict:
        return {
            "schema_version": "experiment.registration.v2",
            "experiment_id": "2026-07-12_example-effect",
            "consumer": {"organ": "bureau", "use": "Use the effect result to decide whether to promote the intervention."},
            "decision_target": {"question": "Should the intervention be promoted after the pilot?", "owner": "bureau"},
            "intervention": {"name": "typed_grip", "description": "Use one typed grip instead of the baseline command sequence."},
            "control_condition": {"id": "control", "description": "Use the existing baseline operator workflow."},
            "treatment_condition": {"id": "treatment", "description": "Use the typed-grip operator workflow."},
            "measurement": {
                "primary_metric": "rework_count",
                "direction": direction,
                "unit": "count",
                "minimum_material_effect": threshold,
                "method": "Compare evidence-bound paired task observations.",
                "success": "Material favorable effect.",
                "falsification": "Harm or no material effect.",
            },
            "comparison": {
                "mode": mode,
                "unit": "same task class, risk and context band",
                "minimum_control": minimum,
                "minimum_treatment": minimum,
                "comparability_constraints": ["same task class", "same risk level"],
                "confounders": ["operator familiarity"],
            },
            "evidence_sources": {"allowed": ["typed execution receipt"], "independent_observation_required": True},
            "review_at": "2026-09-01T00:00:00Z",
            "expires_at": "2026-10-01T00:00:00Z",
            "closure": {"allowed_outcomes": ["promote", "pilot", "defer", "reject", "archive"], "archive_path": "experiments/_archive/2026-07-12_example-effect"},
            "boundary": {"experiment_only": True, "no_auto_policy": True, "no_auto_routing": True, "no_queue_authority": True, "no_runtime_authority": True},
        }

    def observations(self, control: list[float], treatment: list[float], *, independent: bool = True) -> dict:
        rows = []
        for index, value in enumerate(control, 1):
            rows.append({"observation_id": f"c{index}", "condition": "control", "value": value, "comparison_key": "same", "pair_id": f"p{index}", "evidence_ref": f"receipt:c{index}", "independent": independent})
        for index, value in enumerate(treatment, 1):
            rows.append({"observation_id": f"t{index}", "condition": "treatment", "value": value, "comparison_key": "same", "pair_id": f"p{index}", "evidence_ref": f"receipt:t{index}", "independent": independent})
        return {"schema_version": "effect-evaluation.observations.v1", "experiment_id": "2026-07-12_example-effect", "metric": "rework_count", "observations": rows}

    def test_beneficial_effect(self) -> None:
        result = EFFECT.evaluate(self.registration(), self.observations([5, 6, 7], [1, 2, 3]))
        self.assertEqual(result["verdict"], "beneficial")
        self.assertTrue(result["effect_claim_allowed"])
        self.assertEqual(result["statistics"]["favorable_effect"], 4.0)

    def test_harmful_effect(self) -> None:
        result = EFFECT.evaluate(self.registration(), self.observations([1, 2, 3], [5, 6, 7]))
        self.assertEqual(result["verdict"], "harmful")

    def test_no_material_effect(self) -> None:
        result = EFFECT.evaluate(self.registration(threshold=1.0), self.observations([2, 2, 2], [2, 2, 2]))
        self.assertEqual(result["verdict"], "no_material_effect")

    def test_minimum_sample_fails_closed(self) -> None:
        result = EFFECT.evaluate(self.registration(minimum=3), self.observations([2, 2], [1, 1]))
        self.assertEqual(result["verdict"], "insufficient_evidence")
        self.assertFalse(result["effect_claim_allowed"])
        self.assertIn("minimum sample size not met", result["data_quality"]["reasons"])

    def test_incomplete_pair_fails_closed(self) -> None:
        observations = self.observations([2, 2, 2], [1, 1, 1])
        observations["observations"][-1]["pair_id"] = "other"
        result = EFFECT.evaluate(self.registration(), observations)
        self.assertEqual(result["verdict"], "insufficient_evidence")
        self.assertFalse(result["data_quality"]["comparable"])

    def test_non_independent_observation_fails_closed(self) -> None:
        result = EFFECT.evaluate(self.registration(), self.observations([5, 6, 7], [1, 2, 3], independent=False))
        self.assertEqual(result["verdict"], "insufficient_evidence")
        self.assertFalse(result["data_quality"]["independence_met"])

    def test_duplicate_observation_id_is_rejected(self) -> None:
        observations = self.observations([5, 6, 7], [1, 2, 3])
        observations["observations"][1]["observation_id"] = observations["observations"][0]["observation_id"]
        with self.assertRaisesRegex(ValueError, "duplicate observation_id"):
            EFFECT.evaluate(self.registration(), observations)

    def test_duplicate_evidence_ref_is_rejected(self) -> None:
        observations = self.observations([5, 6, 7], [1, 2, 3])
        observations["observations"][1]["evidence_ref"] = observations["observations"][0]["evidence_ref"]
        with self.assertRaisesRegex(ValueError, "duplicate evidence_ref"):
            EFFECT.evaluate(self.registration(), observations)

    def test_pair_comparison_key_mismatch_fails_closed(self) -> None:
        observations = self.observations([5, 6, 7], [1, 2, 3])
        observations["observations"][-1]["comparison_key"] = "different"
        result = EFFECT.evaluate(self.registration(), observations)
        self.assertEqual(result["verdict"], "insufficient_evidence")
        self.assertFalse(result["data_quality"]["comparable"])

    def test_result_digest_excludes_only_self_field(self) -> None:
        result = EFFECT.evaluate(self.registration(), self.observations([5, 6, 7], [1, 2, 3]))
        self.assertEqual(result["result_sha256"], EFFECT.result_sha256(result))

    def test_result_is_deterministic(self) -> None:
        registration = self.registration()
        observations = self.observations([5, 6, 7], [1, 2, 3])
        self.assertEqual(EFFECT.evaluate(registration, observations), EFFECT.evaluate(registration, observations))


if __name__ == "__main__":
    unittest.main()
