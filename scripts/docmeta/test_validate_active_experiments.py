#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from validate_active_experiments import validate_active_experiments  # noqa: E402


class ActiveExperimentRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "schemas").mkdir()
        repo_root = SCRIPT_DIR.parents[1]
        schema = json.loads((repo_root / "schemas/active-experiments.v1.schema.json").read_text())
        (self.root / "schemas/active-experiments.v1.schema.json").write_text(json.dumps(schema))
        self.exp = self.root / "experiments/2026-07-12_example"
        (self.exp / "results").mkdir(parents=True)
        (self.exp / "manifest.yml").write_text("experiment:\n  status: testing\n")
        (self.exp / "results/decision.yml").write_text(
            "verdict: inconclusive\npilot_decision: pilot_without_promotion\n"
        )

        template = json.loads(
            (repo_root / "experiments/_template/registration.v2.json").read_text()
        )
        registration = json.loads(json.dumps(template).replace("replace-with", "example"))
        registration["experiment_id"] = self.exp.name
        registration["registered_at"] = "2026-07-12T00:00:00Z"
        registration["consumer"]["organ"] = "Bureau"
        registration["consumer"]["commitment"]["confirmed_at"] = "2026-07-12T00:00:00Z"
        registration["consumer"]["commitment"]["valid_until"] = "2026-09-01T00:00:00Z"
        registration["decision_target"]["question"] = (
            "Decide whether the example should continue."
        )
        registration["measurement"]["primary_metric"] = "decision_changed"
        registration["review_at"] = "2026-08-01T00:00:00Z"
        registration["expires_at"] = "2026-09-01T00:00:00Z"
        registration["closure"]["archive_path"] = f"experiments/_archive/{self.exp.name}"
        (self.exp / "registration.v2.json").write_text(json.dumps(registration))

    def payload(self) -> dict:
        return {
            "schema_version": "active-experiments.v1",
            "max_active": 5,
            "experiments": [{
                "experiment_id": "2026-07-12_example",
                "path": "experiments/2026-07-12_example",
                "state": "pilot",
                "consumer": "Bureau",
                "decision_target": "Decide whether the example should continue.",
                "primary_metric": "decision_changed",
                "review_at": "2026-08-01T00:00:00Z",
                "expires_at": "2026-09-01T00:00:00Z",
                "source_ref": "experiments/2026-07-12_example/results/decision.yml",
            }],
        }

    def write(self, payload: dict) -> Path:
        path = self.root / "experiments/active.v1.json"
        path.write_text(json.dumps(payload))
        return path

    def validate(self, payload: dict | None = None) -> dict:
        return validate_active_experiments(
            self.write(payload or self.payload()),
            repo_root=self.root,
            now=datetime(2026, 7, 12, tzinfo=timezone.utc),
        )

    @staticmethod
    def update_item_for_directory(payload: dict, experiment_dir: Path) -> None:
        item = payload["experiments"][0]
        item["experiment_id"] = experiment_dir.name
        item["path"] = f"experiments/{experiment_dir.name}"
        item["source_ref"] = f"experiments/{experiment_dir.name}/results/decision.yml"

    def test_valid_registry_is_registration_and_decision_bound(self) -> None:
        result = self.validate()
        self.assertEqual(result["active_count"], 1)
        self.assertEqual(result["registration_bound_count"], 1)
        self.assertEqual(result["grandfathered_count"], 0)

    def test_v1_registration_metric_is_supported(self) -> None:
        (self.exp / "registration.v2.json").unlink()
        v1_exp = self.root / "experiments/2026-07-09_repobrief-workbench-usefulness-eval"
        self.exp.rename(v1_exp)
        registration = {
            "schema_version": "experiment.registration.v1",
            "experiment_id": v1_exp.name,
            "consumer": {
                "organ": "Bureau",
                "use": "Use the result for a bounded reviewed decision.",
            },
            "decision_target": {
                "question": "Decide whether the example should continue.",
                "owner": "Bureau",
            },
            "measurement": {
                "metric": "decision_changed",
                "method": "Measure the evidence-bound decision outcome.",
                "success": "A material improvement is observed.",
                "falsification": "No material improvement is observed.",
            },
            "expires_at": "2026-09-01T00:00:00Z",
            "closure": {
                "review_at": "2026-08-01T00:00:00Z",
                "allowed_outcomes": ["promote", "reject", "archive"],
                "archive_path": f"experiments/_archive/{v1_exp.name}",
            },
            "boundary": {
                "experiment_only": True,
                "no_auto_policy": True,
                "no_auto_routing": True,
                "no_queue_authority": True,
                "no_runtime_authority": True,
            },
        }
        (v1_exp / "registration.v1.json").write_text(json.dumps(registration))
        payload = self.payload()
        self.update_item_for_directory(payload, v1_exp)
        result = self.validate(payload)
        self.assertEqual(result["registration_bound_count"], 1)

    def test_missing_required_registration_fails(self) -> None:
        (self.exp / "registration.v2.json").unlink()
        with self.assertRaisesRegex(ValueError, "requires registration"):
            self.validate()

    def test_explicit_pre_t005_experiment_remains_supported(self) -> None:
        (self.exp / "registration.v2.json").unlink()
        old_exp = self.root / "experiments/2026-07-08_operator-learning-capture-sample"
        self.exp.rename(old_exp)
        payload = self.payload()
        self.update_item_for_directory(payload, old_exp)
        result = self.validate(payload)
        self.assertEqual(result["registration_bound_count"], 0)
        self.assertEqual(result["grandfathered_count"], 1)

    def test_expired_entry_fails(self) -> None:
        payload = self.payload()
        payload["experiments"][0]["review_at"] = "2026-06-01T00:00:00Z"
        payload["experiments"][0]["expires_at"] = "2026-07-01T00:00:00Z"
        with self.assertRaisesRegex(ValueError, "expired"):
            self.validate(payload)

    def test_source_ref_must_be_canonical_decision(self) -> None:
        payload = self.payload()
        alternate = self.exp / "results/alternate.yml"
        alternate.write_text("verdict: inconclusive\n")
        payload["experiments"][0]["source_ref"] = (
            "experiments/2026-07-12_example/results/alternate.yml"
        )
        with self.assertRaisesRegex(
            ValueError,
            "exactly results/decision.yml or pN/decision.yml",
        ):
            self.validate(payload)

    def test_testing_experiment_accepts_phase_local_decision(self) -> None:
        phase_dir = self.exp / "p1"
        phase_dir.mkdir()
        (phase_dir / "decision.yml").write_text(
            "verdict: prepared_for_prospective_shadow_capture\n"
        )
        payload = self.payload()
        payload["experiments"][0]["state"] = "testing"
        payload["experiments"][0]["source_ref"] = (
            "experiments/2026-07-12_example/p1/decision.yml"
        )

        result = self.validate(payload)

        self.assertEqual(result["active_count"], 1)

    def test_phase_source_ref_rejects_non_decision_name(self) -> None:
        phase_dir = self.exp / "p1"
        phase_dir.mkdir()
        (phase_dir / "alternate.yml").write_text("verdict: inconclusive\n")
        payload = self.payload()
        payload["experiments"][0]["source_ref"] = (
            "experiments/2026-07-12_example/p1/alternate.yml"
        )

        with self.assertRaisesRegex(
            ValueError,
            "exactly results/decision.yml or pN/decision.yml",
        ):
            self.validate(payload)

    def test_phase_source_ref_rejects_nested_decision(self) -> None:
        nested_dir = self.exp / "p1/nested"
        nested_dir.mkdir(parents=True)
        (nested_dir / "decision.yml").write_text("verdict: inconclusive\n")
        payload = self.payload()
        payload["experiments"][0]["source_ref"] = (
            "experiments/2026-07-12_example/p1/nested/decision.yml"
        )

        with self.assertRaisesRegex(
            ValueError,
            "exactly results/decision.yml or pN/decision.yml",
        ):
            self.validate(payload)

    def test_phase_source_ref_rejects_malformed_phase_directory(self) -> None:
        for malformed in ("p", "phase1", "p-one", "p1x"):
            with self.subTest(malformed=malformed):
                payload = self.payload()
                payload["experiments"][0]["source_ref"] = (
                    f"experiments/2026-07-12_example/{malformed}/decision.yml"
                )
                with self.assertRaisesRegex(
                    ValueError,
                    "exactly results/decision.yml or pN/decision.yml",
                ):
                    self.validate(payload)

    def test_phase_source_ref_rejects_escape(self) -> None:
        payload = self.payload()
        payload["experiments"][0]["source_ref"] = (
            "experiments/2026-07-12_example/p1/../../outside/decision.yml"
        )

        with self.assertRaisesRegex(
            ValueError,
            "exactly results/decision.yml or pN/decision.yml",
        ):
            self.validate(payload)

    def test_phase_source_ref_requires_existing_file(self) -> None:
        payload = self.payload()
        payload["experiments"][0]["source_ref"] = (
            "experiments/2026-07-12_example/p9/decision.yml"
        )

        with self.assertRaisesRegex(ValueError, "source_ref is missing"):
            self.validate(payload)

    def test_source_decision_requires_verdict(self) -> None:
        (self.exp / "results/decision.yml").write_text("pilot_decision: pilot\n")
        with self.assertRaisesRegex(ValueError, "non-empty verdict"):
            self.validate()

    def test_manifest_state_conflict_fails(self) -> None:
        (self.exp / "manifest.yml").write_text("experiment:\n  status: inconclusive\n")
        with self.assertRaisesRegex(ValueError, "conflicts"):
            self.validate()

    def test_designed_state_requires_not_executed_decision(self) -> None:
        payload = self.payload()
        payload["experiments"][0]["state"] = "designed"
        (self.exp / "manifest.yml").write_text("experiment:\n  status: designed\n")
        with self.assertRaisesRegex(ValueError, "must have verdict not_executed"):
            self.validate(payload)

    def test_pilot_state_requires_pilot_signal(self) -> None:
        (self.exp / "results/decision.yml").write_text("verdict: inconclusive\n")
        with self.assertRaisesRegex(ValueError, "lacks a pilot decision signal"):
            self.validate()

    def test_primary_metric_must_match_registration(self) -> None:
        payload = self.payload()
        payload["experiments"][0]["primary_metric"] = "other_metric"
        with self.assertRaisesRegex(ValueError, "primary_metric conflicts"):
            self.validate(payload)

    def test_consumer_must_match_registration(self) -> None:
        payload = self.payload()
        payload["experiments"][0]["consumer"] = "Bureau RPU-V1"
        with self.assertRaisesRegex(ValueError, "consumer conflicts"):
            self.validate(payload)

    def test_decision_target_must_match_registration(self) -> None:
        payload = self.payload()
        payload["experiments"][0]["decision_target"] = "Decide something else entirely."
        with self.assertRaisesRegex(ValueError, "decision_target conflicts"):
            self.validate(payload)

    def test_review_at_must_match_registration(self) -> None:
        payload = self.payload()
        payload["experiments"][0]["review_at"] = "2026-08-02T00:00:00Z"
        with self.assertRaisesRegex(ValueError, "review_at conflicts"):
            self.validate(payload)

    def test_expires_at_must_match_registration(self) -> None:
        payload = self.payload()
        payload["experiments"][0]["expires_at"] = "2026-09-02T00:00:00Z"
        with self.assertRaisesRegex(ValueError, "expires_at conflicts"):
            self.validate(payload)

    def test_duplicate_id_fails(self) -> None:
        payload = self.payload()
        payload["experiments"].append(dict(payload["experiments"][0]))
        with self.assertRaises(Exception):
            self.validate(payload)


if __name__ == "__main__":
    unittest.main()
