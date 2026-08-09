#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("capture_effect_observation.py")
SPEC = importlib.util.spec_from_file_location("capture_effect_observation", SCRIPT)
assert SPEC and SPEC.loader
CAPTURE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CAPTURE)


class CaptureEffectObservationTests(unittest.TestCase):
    def registration(self) -> dict:
        return {
            "schema_version": "experiment.registration.v2",
            "experiment_id": "2026-07-12_capture-example",
            "registered_at": "2026-08-08T00:00:00Z",
            "consumer": {
                "organ": "bureau",
                "use": "Use reviewed results to decide whether the intervention remains active.",
                "relationship": "external",
                "commitment": {
                    "status": "confirmed",
                    "evidence_ref": "bureau:capture-example-consumer",
                    "confirmed_at": "2026-08-08T00:00:00Z",
                    "valid_until": "2099-10-01T00:00:00Z",
                },
            },
            "decision_target": {
                "question": "Should the intervention remain active after the pilot?",
                "owner": "bureau",
                "decision_ref": "bureau:capture-example-decision",
            },
            "intervention": {
                "name": "effect_capture",
                "description": "Capture evidence-bound observations before deterministic review.",
            },
            "control_condition": {
                "id": "manual_review",
                "description": "Review the evidence manually without the effect report.",
            },
            "treatment_condition": {
                "id": "evaluator_assisted_review",
                "description": "Review the same evidence with the deterministic effect report.",
            },
            "measurement": {
                "primary_metric": "reviewed_decision_value_score",
                "direction": "higher_is_better",
                "unit": "score",
                "minimum_material_effect": 1,
                "cost_metric": {
                    "id": "review_effort_seconds",
                    "unit": "seconds",
                    "method": "Measure elapsed review effort for each decision.",
                },
                "method": "Compare evidence-bound paired review observations.",
                "success": "A material favorable effect without overclaiming.",
                "falsification": "No material effect, harm, or misleading evidence use.",
                "outcome_criteria": {
                    "success_threshold": 2,
                    "harm_or_falsification_threshold": 0,
                },
            },
            "comparison": {
                "mode": "paired",
                "unit": "same frozen evidence and decision question",
                "minimum_control": 3,
                "minimum_treatment": 3,
                "comparability_constraints": [
                    "same frozen evidence",
                    "same decision question",
                ],
                "confounders": ["reviewer expertise"],
            },
            "evidence_sources": {
                "allowed": ["typed execution receipt"],
                "independent_observation_required": True,
            },
            "review_at": "2099-09-15T00:00:00Z",
            "expires_at": "2099-10-01T00:00:00Z",
            "closure": {
                "allowed_outcomes": ["promote", "pilot", "defer", "reject", "archive"],
                "archive_path": "experiments/_archive/2026-07-12_capture-example",
                "outcome_by_result": {
                    "success": "promote",
                    "harm_or_falsification": "reject",
                    "inconclusive": "defer",
                    "expired": "archive",
                },
            },
            "surface_budget": {
                "durable_additions": [],
                "durable_offsets": [],
                "reviewed_exception": None,
            },
            "boundary": {
                "experiment_only": True,
                "no_auto_policy": True,
                "no_auto_routing": True,
                "no_queue_authority": True,
                "no_runtime_authority": True,
                "no_merge_authority": True,
            },
        }

    def setup_experiment(self, root: Path) -> tuple[Path, Path]:
        experiment = root / "experiments/2026-07-12_capture-example"
        results = experiment / "results"
        results.mkdir(parents=True)
        registration = experiment / "registration.v2.json"
        registration.write_text(json.dumps(self.registration()), encoding="utf-8")
        return registration, results / "observations.v2.json"

    def observation(self, identifier: str = "manual-1", *, digest_seed: str = "evidence-1") -> dict:
        return {
            "observation_id": identifier,
            "condition": "manual_review",
            "value": 2.0,
            "effort_seconds": 60.0,
            "scoring_blinded": True,
            "comparison_key": "pilot-1",
            "pair_id": "pilot-1",
            "evidence_ref": f"receipt:{identifier}",
            "evidence_sha256": hashlib.sha256(digest_seed.encode()).hexdigest(),
            "decision_maker_ref": f"receipt:decider-{identifier}",
            "observer_ref": f"receipt:observer-{identifier}",
            "independent": True,
            "captured_at": "2026-08-01T00:00:00Z",
        }

    def test_capture_creates_registration_bound_document(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            registration, observations = self.setup_experiment(Path(raw))
            result = CAPTURE.capture(registration, observations, self.observation())
            document = json.loads(observations.read_text(encoding="utf-8"))
            expected_registration = CAPTURE.sha256_json(self.registration())
            self.assertEqual(document["registration_sha256"], expected_registration)
            self.assertEqual(document["observations"][0]["observation_id"], "manual-1")
            self.assertEqual(result["observation_count"], 1)

    def test_registration_drift_is_rejected_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            registration, observations = self.setup_experiment(Path(raw))
            CAPTURE.capture(registration, observations, self.observation())
            before = observations.read_bytes()
            changed = self.registration()
            changed["decision_target"]["question"] = "Should the changed intervention remain active?"
            registration.write_text(json.dumps(changed), encoding="utf-8")
            with self.assertRaisesRegex(CAPTURE.CaptureError, "registration digest mismatch"):
                CAPTURE.capture(
                    registration,
                    observations,
                    self.observation("manual-2", digest_seed="evidence-2"),
                )
            self.assertEqual(observations.read_bytes(), before)

    def test_duplicate_evidence_digest_is_rejected_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            registration, observations = self.setup_experiment(Path(raw))
            CAPTURE.capture(registration, observations, self.observation())
            before = observations.read_bytes()
            with self.assertRaisesRegex(CAPTURE.CaptureError, "duplicate evidence_sha256"):
                CAPTURE.capture(
                    registration,
                    observations,
                    self.observation("manual-2", digest_seed="evidence-1"),
                )
            self.assertEqual(observations.read_bytes(), before)

    def test_duplicate_condition_within_pair_is_rejected_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            registration, observations = self.setup_experiment(Path(raw))
            CAPTURE.capture(registration, observations, self.observation("manual-1"))
            before = observations.read_bytes()
            duplicate = self.observation("manual-2", digest_seed="evidence-2")
            duplicate["pair_id"] = "pilot-1"
            with self.assertRaisesRegex(CAPTURE.CaptureError, "duplicate condition within pair"):
                CAPTURE.capture(registration, observations, duplicate)
            self.assertEqual(observations.read_bytes(), before)

    def test_t005_semantic_gate_runs_before_capture(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            registration, observations = self.setup_experiment(Path(raw))
            invalid = self.registration()
            del invalid["registered_at"]
            registration.write_text(json.dumps(invalid), encoding="utf-8")
            with self.assertRaisesRegex(CAPTURE.CaptureError, "registered_at"):
                CAPTURE.capture(registration, observations, self.observation())
            self.assertFalse(observations.exists())

    def test_expired_observation_is_rejected_before_file_creation(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            registration, observations = self.setup_experiment(Path(raw))
            row = self.observation()
            row["captured_at"] = "2099-10-01T00:00:01Z"
            with self.assertRaisesRegex(CAPTURE.CaptureError, "after experiment expiry"):
                CAPTURE.capture(registration, observations, row)
            self.assertFalse(observations.exists())

    def test_target_outside_results_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            registration, _observations = self.setup_experiment(root)
            outside = root / "outside.json"
            with self.assertRaisesRegex(CAPTURE.CaptureError, "inside the registered experiment results"):
                CAPTURE.capture(registration, outside, self.observation())
            self.assertFalse(outside.exists())

    def test_symlink_target_is_rejected_without_touching_victim(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            registration, observations = self.setup_experiment(root)
            victim = root / "victim.json"
            victim.write_text("victim\n", encoding="utf-8")
            observations.symlink_to(victim)
            with self.assertRaisesRegex(CAPTURE.CaptureError, "must not be a symlink"):
                CAPTURE.capture(registration, observations, self.observation())
            self.assertEqual(victim.read_text(encoding="utf-8"), "victim\n")

    def test_registered_scorecard_computes_value_from_components(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            registration, observations = self.setup_experiment(root)
            data = self.registration()
            data["measurement"]["scorecard"] = {
                "schema_version": "additive-binary-scorecard.v1",
                "components": [
                    {"id": "aligned", "weight": 2, "criterion": "Decision aligns with adjudication."},
                    {"id": "calibrated", "weight": 1, "criterion": "Decision preserves uncertainty."},
                ],
            }
            registration.write_text(json.dumps(data), encoding="utf-8")
            evidence = root / "scorecard.json"
            evidence.write_text("{}\n", encoding="utf-8")
            parser_args = type("Args", (), {
                "evidence_sha256": None,
                "evidence_file": evidence,
                "independent": True,
                "value": None,
                "score_component": ["aligned=1", "calibrated=0"],
                "effort_seconds": "75",
                "scoring_blinded": True,
                "observation_id": "manual-score",
                "condition": "manual_review",
                "comparison_key": "pilot-score",
                "evidence_ref": "receipt:manual-score",
                "decision_maker_ref": "receipt:decider-score",
                "observer_ref": "receipt:observer-score",
                "captured_at": "2026-08-01T00:00:00Z",
                "pair_id": "pilot-score",
            })()
            row = CAPTURE.build_observation(parser_args, data)
            self.assertEqual(row["value"], 2.0)
            self.assertEqual(row["score_components"], {"aligned": 1, "calibrated": 0})
            CAPTURE.capture(registration, observations, row)

    def test_self_scored_observation_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            registration, observations = self.setup_experiment(Path(raw))
            row = self.observation()
            row["observer_ref"] = row["decision_maker_ref"]
            with self.assertRaisesRegex(CAPTURE.CaptureError, "scorer must differ"):
                CAPTURE.capture(registration, observations, row)
            self.assertFalse(observations.exists())

    def test_evidence_symlink_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            target = root / "evidence.json"
            target.write_text("{}\n", encoding="utf-8")
            link = root / "evidence-link.json"
            link.symlink_to(target)
            with self.assertRaisesRegex(CAPTURE.CaptureError, "must not be a symlink"):
                CAPTURE.sha256_file(link)

    def test_negative_effort_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            registration, observations = self.setup_experiment(Path(raw))
            row = self.observation()
            row["effort_seconds"] = -1
            with self.assertRaisesRegex(CAPTURE.CaptureError, "effort_seconds"):
                CAPTURE.capture(registration, observations, row)
            self.assertFalse(observations.exists())

    def test_concurrent_cli_writers_are_all_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            registration, observations = self.setup_experiment(root)
            processes = []
            for index in range(4):
                evidence = root / f"evidence-{index}.txt"
                evidence.write_text(f"evidence {index}\n", encoding="utf-8")
                command = [
                    sys.executable,
                    str(SCRIPT),
                    "--registration", str(registration),
                    "--observations", str(observations),
                    "--observation-id", f"obs-{index}",
                    "--condition", "manual_review",
                    "--value", str(index),
                    "--effort-seconds", str(60 + index),
                    "--scoring-blinded",
                    "--comparison-key", "pilot-concurrent",
                    "--pair-id", f"pilot-{index}",
                    "--evidence-ref", f"receipt:obs-{index}",
                    "--evidence-file", str(evidence),
                    "--decision-maker-ref", f"receipt:decider-{index}",
                    "--observer-ref", f"receipt:observer-{index}",
                    "--independent",
                    "--captured-at", "2026-08-01T00:00:00Z",
                ]
                processes.append(subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True))
            failures = []
            for process in processes:
                stdout, stderr = process.communicate(timeout=20)
                if process.returncode != 0:
                    failures.append((process.returncode, stdout, stderr))
            self.assertEqual(failures, [])
            document = json.loads(observations.read_text(encoding="utf-8"))
            self.assertEqual(
                [row["observation_id"] for row in document["observations"]],
                ["obs-0", "obs-1", "obs-2", "obs-3"],
            )


if __name__ == "__main__":
    unittest.main()
