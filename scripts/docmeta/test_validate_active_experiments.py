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
        schema = json.loads((SCRIPT_DIR.parents[1] / "schemas/active-experiments.v1.schema.json").read_text())
        (self.root / "schemas/active-experiments.v1.schema.json").write_text(json.dumps(schema))
        self.exp = self.root / "experiments/2026-07-12_example"
        (self.exp / "results").mkdir(parents=True)
        (self.exp / "manifest.yml").write_text("experiment:\n  status: testing\n")
        (self.exp / "results/decision.yml").write_text("verdict: inconclusive\n")

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

    def test_valid_registry(self) -> None:
        result = validate_active_experiments(
            self.write(self.payload()), repo_root=self.root,
            now=datetime(2026, 7, 12, tzinfo=timezone.utc),
        )
        self.assertEqual(result["active_count"], 1)

    def test_expired_entry_fails(self) -> None:
        payload = self.payload()
        payload["experiments"][0]["review_at"] = "2026-06-01T00:00:00Z"
        payload["experiments"][0]["expires_at"] = "2026-07-01T00:00:00Z"
        with self.assertRaisesRegex(ValueError, "expired"):
            validate_active_experiments(
                self.write(payload), repo_root=self.root,
                now=datetime(2026, 7, 12, tzinfo=timezone.utc),
            )

    def test_source_ref_must_be_inside_experiment(self) -> None:
        payload = self.payload()
        outside = self.root / "outside.yml"
        outside.write_text("x")
        payload["experiments"][0]["source_ref"] = "outside.yml"
        with self.assertRaisesRegex(ValueError, "inside experiment"):
            validate_active_experiments(
                self.write(payload), repo_root=self.root,
                now=datetime(2026, 7, 12, tzinfo=timezone.utc),
            )

    def test_manifest_state_conflict_fails(self) -> None:
        (self.exp / "manifest.yml").write_text("experiment:\n  status: inconclusive\n")
        with self.assertRaisesRegex(ValueError, "conflicts"):
            validate_active_experiments(
                self.write(self.payload()), repo_root=self.root,
                now=datetime(2026, 7, 12, tzinfo=timezone.utc),
            )

    def test_duplicate_id_fails(self) -> None:
        payload = self.payload()
        payload["experiments"].append(dict(payload["experiments"][0]))
        with self.assertRaises(Exception):
            validate_active_experiments(
                self.write(payload), repo_root=self.root,
                now=datetime(2026, 7, 12, tzinfo=timezone.utc),
            )


if __name__ == "__main__":
    unittest.main()
