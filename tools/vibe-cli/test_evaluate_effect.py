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
            "consumer": {
                "organ": "bureau",
                "use": "Use the effect result to decide whether to promote the intervention.",
                "relation": "external",
                "status": "current",
                "evidence_ref": "bureau-task:TEST-T001",
            },
            "decision_target": {"question": "Should the intervention be promoted after the pilot?", "owner": "bureau"},
            "intervention": {"name": "typed_grip", "description": "Use one typed grip instead of the baseline command sequence."},
            "control_condition": {"id": "control", "description": "Use the existing baseline operator workflow."},
            "treatment_condition": {"id": "treatment", "description": "Use the typed-grip operator workflow."},
            "measurement": {
                "primary_metric": "rework_count",
                "direction": direction,
                "unit": "count",
                "minimum_material_effect": threshold,
                "cost_metric": {
                    "id": "review_effort_seconds",
                    "unit": "seconds",
                    "method": "Measure elapsed review effort for each decision.",
                },
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
            "surface_budget": {
                "durable_units_added": [],
                "durable_units_removed_or_replaced": [],
                "balance": "non_positive",
            },
            "boundary": {"experiment_only": True, "no_auto_policy": True, "no_auto_routing": True, "no_queue_authority": True, "no_runtime_authority": True},
        }

    def observations(self, control: list[float], treatment: list[float], *, independent: bool = True) -> dict:
        rows = []
        for index, value in enumerate(control, 1):
            rows.append({"observation_id": f"c{index}", "condition": "control", "value": value, "effort_seconds": 60 + index, "scoring_blinded": True, "comparison_key": "same", "pair_id": f"p{index}", "evidence_ref": f"receipt:c{index}", "evidence_sha256": f"{index:064x}", "decision_maker_ref": f"receipt:manual-decider-{index}", "observer_ref": f"receipt:auditor-{index}", "independent": independent, "captured_at": "2026-08-01T00:00:00Z"})
        for index, value in enumerate(treatment, 1):
            rows.append({"observation_id": f"t{index}", "condition": "treatment", "value": value, "effort_seconds": 70 + index, "scoring_blinded": True, "comparison_key": "same", "pair_id": f"p{index}", "evidence_ref": f"receipt:t{index}", "evidence_sha256": f"{index + 100:064x}", "decision_maker_ref": f"receipt:evaluator-decider-{index}", "observer_ref": f"receipt:auditor-{index}", "independent": independent, "captured_at": "2026-08-01T00:00:00Z"})
        registration = self.registration()
        return {"schema_version": "effect-evaluation.observations.v2", "experiment_id": "2026-07-12_example-effect", "registration_sha256": EFFECT.sha256_json(registration), "metric": "rework_count", "observations": rows}

    def test_beneficial_effect(self) -> None:
        registration = self.registration()
        observations = self.observations([5, 6, 7], [1, 2, 3])
        observations["registration_sha256"] = EFFECT.sha256_json(registration)
        result = EFFECT.evaluate(registration, observations)
        self.assertEqual(result["verdict"], "beneficial")
        self.assertTrue(result["effect_claim_allowed"])
        self.assertEqual(result["statistics"]["favorable_effect"], 4.0)

    def test_harmful_effect(self) -> None:
        registration = self.registration()
        observations = self.observations([1, 2, 3], [5, 6, 7])
        observations["registration_sha256"] = EFFECT.sha256_json(registration)
        result = EFFECT.evaluate(registration, observations)
        self.assertEqual(result["verdict"], "harmful")

    def test_no_material_effect(self) -> None:
        registration = self.registration(threshold=1.0)
        observations = self.observations([2, 2, 2], [2, 2, 2])
        observations["registration_sha256"] = EFFECT.sha256_json(registration)
        result = EFFECT.evaluate(registration, observations)
        self.assertEqual(result["verdict"], "no_material_effect")

    def test_minimum_sample_fails_closed(self) -> None:
        registration = self.registration(minimum=3)
        observations = self.observations([2, 2], [1, 1])
        observations["registration_sha256"] = EFFECT.sha256_json(registration)
        result = EFFECT.evaluate(registration, observations)
        self.assertEqual(result["verdict"], "insufficient_evidence")
        self.assertFalse(result["effect_claim_allowed"])
        self.assertIn("minimum sample size not met", result["data_quality"]["reasons"])

    def test_incomplete_pair_fails_closed(self) -> None:
        observations = self.observations([2, 2, 2], [1, 1, 1])
        observations["observations"][-1]["pair_id"] = "other"
        registration = self.registration()
        observations["registration_sha256"] = EFFECT.sha256_json(registration)
        result = EFFECT.evaluate(registration, observations)
        self.assertEqual(result["verdict"], "insufficient_evidence")
        self.assertFalse(result["data_quality"]["comparable"])

    def test_non_independent_observation_fails_closed(self) -> None:
        registration = self.registration()
        observations = self.observations([5, 6, 7], [1, 2, 3], independent=False)
        observations["registration_sha256"] = EFFECT.sha256_json(registration)
        result = EFFECT.evaluate(registration, observations)
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
        registration = self.registration()
        observations["registration_sha256"] = EFFECT.sha256_json(registration)
        result = EFFECT.evaluate(registration, observations)
        self.assertEqual(result["verdict"], "insufficient_evidence")
        self.assertFalse(result["data_quality"]["comparable"])

    def test_registration_digest_mismatch_is_rejected(self) -> None:
        registration = self.registration()
        observations = self.observations([5, 6, 7], [1, 2, 3])
        observations["registration_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "registration digest mismatch"):
            EFFECT.evaluate(registration, observations)

    def test_duplicate_evidence_digest_is_rejected(self) -> None:
        registration = self.registration()
        observations = self.observations([5, 6, 7], [1, 2, 3])
        observations["observations"][1]["evidence_sha256"] = observations["observations"][0]["evidence_sha256"]
        observations["registration_sha256"] = EFFECT.sha256_json(registration)
        with self.assertRaisesRegex(ValueError, "duplicate evidence_sha256"):
            EFFECT.evaluate(registration, observations)

    def test_same_decision_maker_within_pair_fails_independence(self) -> None:
        registration = self.registration()
        observations = self.observations([5, 6, 7], [1, 2, 3])
        observations["observations"][3]["decision_maker_ref"] = observations["observations"][0]["decision_maker_ref"]
        observations["registration_sha256"] = EFFECT.sha256_json(registration)
        result = EFFECT.evaluate(registration, observations)
        self.assertEqual(result["verdict"], "insufficient_evidence")
        self.assertFalse(result["data_quality"]["independence_met"])
        self.assertIn(
            "paired conditions require distinct decision_maker_ref values",
            result["data_quality"]["reasons"],
        )

    def test_self_scored_observation_fails_independence(self) -> None:
        registration = self.registration()
        observations = self.observations([5, 6, 7], [1, 2, 3])
        observations["observations"][0]["observer_ref"] = observations["observations"][0]["decision_maker_ref"]
        observations["registration_sha256"] = EFFECT.sha256_json(registration)
        result = EFFECT.evaluate(registration, observations)
        self.assertEqual(result["verdict"], "insufficient_evidence")
        self.assertFalse(result["data_quality"]["independence_met"])
        self.assertIn(
            "independent scorer must differ from decision maker",
            result["data_quality"]["reasons"],
        )

    def test_registered_scorecard_derives_and_checks_values(self) -> None:
        registration = self.registration()
        registration["measurement"]["scorecard"] = {
            "schema_version": "additive-binary-scorecard.v1",
            "components": [
                {"id": "aligned", "weight": 2, "criterion": "Decision aligns with adjudication."},
                {"id": "calibrated", "weight": 1, "criterion": "Decision preserves uncertainty."},
            ],
        }
        observations = self.observations([3, 3, 3], [3, 3, 3])
        for row in observations["observations"]:
            row["score_components"] = {"aligned": 1, "calibrated": 1}
        observations["registration_sha256"] = EFFECT.sha256_json(registration)
        result = EFFECT.evaluate(registration, observations)
        self.assertEqual(result["verdict"], "no_material_effect")

    def test_scorecard_value_mismatch_is_rejected(self) -> None:
        registration = self.registration()
        registration["measurement"]["scorecard"] = {
            "schema_version": "additive-binary-scorecard.v1",
            "components": [
                {"id": "aligned", "weight": 1, "criterion": "Decision aligns with adjudication."},
            ],
        }
        observations = self.observations([2, 2, 2], [2, 2, 2])
        for row in observations["observations"]:
            row["score_components"] = {"aligned": 1}
        observations["registration_sha256"] = EFFECT.sha256_json(registration)
        with self.assertRaisesRegex(ValueError, "value does not match registered scorecard"):
            EFFECT.evaluate(registration, observations)

    def test_fatal_scorecard_component_overrides_favorable_average(self) -> None:
        registration = self.registration(direction="higher_is_better", threshold=1.0)
        registration["measurement"]["scorecard"] = {
            "schema_version": "additive-binary-scorecard.v1",
            "components": [
                {
                    "id": "overclaim_free",
                    "weight": 1,
                    "criterion": "Decision contains no misleading effect claim.",
                    "fatal_when_zero": True,
                },
            ],
        }
        observations = self.observations([0, 0, 0], [1, 1, 1])
        for row in observations["observations"]:
            row["score_components"] = {"overclaim_free": int(row["value"])}
        observations["observations"][3]["score_components"]["overclaim_free"] = 0
        observations["observations"][3]["value"] = 0
        observations["registration_sha256"] = EFFECT.sha256_json(registration)
        result = EFFECT.evaluate(registration, observations)
        self.assertEqual(result["verdict"], "harmful")
        self.assertFalse(result["effect_claim_allowed"])
        self.assertTrue(result["registered_falsification"]["triggered"])
        self.assertEqual(result["registered_falsification"]["components"], ["overclaim_free"])

    def test_unblinded_scoring_is_insufficient(self) -> None:
        registration = self.registration()
        observations = self.observations([5, 6, 7], [1, 2, 3])
        observations["observations"][0]["scoring_blinded"] = False
        observations["registration_sha256"] = EFFECT.sha256_json(registration)
        result = EFFECT.evaluate(registration, observations)
        self.assertEqual(result["verdict"], "insufficient_evidence")
        self.assertFalse(result["data_quality"]["blinding_met"])
        self.assertIn("condition-label blinding requirement not met", result["data_quality"]["reasons"])

    def test_operational_cost_is_reported_without_claiming_cost_effectiveness(self) -> None:
        registration = self.registration()
        observations = self.observations([5, 6, 7], [1, 2, 3])
        observations["registration_sha256"] = EFFECT.sha256_json(registration)
        result = EFFECT.evaluate(registration, observations)
        self.assertEqual(result["operational_cost"]["control_mean"], 62.0)
        self.assertEqual(result["operational_cost"]["treatment_mean"], 72.0)
        self.assertEqual(result["operational_cost"]["raw_difference"], 10.0)
        self.assertIn("cost_effectiveness_or_acceptable_ceremony", result["does_not_establish"])

    def test_observation_after_expiry_is_rejected(self) -> None:
        registration = self.registration()
        observations = self.observations([5, 6, 7], [1, 2, 3])
        observations["observations"][0]["captured_at"] = "2026-10-01T00:00:01Z"
        observations["registration_sha256"] = EFFECT.sha256_json(registration)
        with self.assertRaisesRegex(ValueError, "captured after experiment expiry"):
            EFFECT.evaluate(registration, observations)

    def test_result_digest_excludes_only_self_field(self) -> None:
        result = EFFECT.evaluate(self.registration(), self.observations([5, 6, 7], [1, 2, 3]))
        self.assertEqual(result["result_sha256"], EFFECT.result_sha256(result))

    def test_result_is_deterministic(self) -> None:
        registration = self.registration()
        observations = self.observations([5, 6, 7], [1, 2, 3])
        self.assertEqual(EFFECT.evaluate(registration, observations), EFFECT.evaluate(registration, observations))


if __name__ == "__main__":
    unittest.main()
