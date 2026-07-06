#!/usr/bin/env python3
"""Focused safety_value enum tests for Ecosystem Organ Preflight."""

from __future__ import annotations

import copy
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from validate_ecosystem_organ_preflight import (  # noqa: E402
    EXPERIMENT_REL,
    validate_ecosystem_organ_preflight,
)

VALID_RUN = {
    "schema_version": "0.1.0",
    "task_id": "run-safety-enum",
    "timestamp": "2026-07-06T00:00:00Z",
    "repo": "heimgewebe/vibe-lab",
    "pr": 292,
    "issue": None,
    "slice": "safety enum regression",
    "active_ball": "PR #292",
    "task_class": "experiment_instrumentation",
    "perceived_complexity": "medium",
    "primary_truth_source": "repo_pr_ci",
    "allowed_context_organs": ["vibe_lab"],
    "blocked_organs": ["bureau"],
    "stop_rules": ["CI gate required."],
    "predicted_primary_organ": "repo_pr_ci",
    "actual_primary_organ": "repo_pr_ci",
    "evidence_refs": ["results/evidence.jsonl"],
    "metrics": {
        "wrong_organ_corrections": 0,
        "rework_loops": 0,
        "next_step_ambiguity": "low",
        "friction_cost_minutes": 1,
        "safety_value": "none",
    },
    "verdict": "usability_only",
    "interpretation_budget": {
        "allowed_claims": ["The run record is structured."],
        "disallowed_claims": ["No broad outcome claim from one run."],
        "epistemic_gaps": ["Metric values are local to this test fixture."],
    },
}


class EcosystemOrganPreflightSafetyEnumTests(unittest.TestCase):
    def _root(self) -> tuple[tempfile.TemporaryDirectory, Path]:
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        exp = root / EXPERIMENT_REL
        (exp / "results" / "runs").mkdir(parents=True)
        (exp / "results" / "evidence.jsonl").write_text(
            '{"event_type":"observation","timestamp":"2026-07-06T00:00:00Z"}\n',
            encoding="utf-8",
        )
        (exp / "manifest.yml").write_text(
            "experiment:\n  execution_status: executed\n", encoding="utf-8"
        )
        return tmp, root

    def _write_run(self, root: Path, data: dict) -> None:
        path = root / EXPERIMENT_REL / "results" / "runs" / "run-001.yml"
        path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")

    def test_safety_value_high_passes(self) -> None:
        tmp, root = self._root()
        self.addCleanup(tmp.cleanup)
        data = copy.deepcopy(VALID_RUN)
        data["metrics"]["safety_value"] = "high"
        self._write_run(root, data)
        self.assertEqual(validate_ecosystem_organ_preflight(root), [])

    def test_safety_value_potential_fails(self) -> None:
        tmp, root = self._root()
        self.addCleanup(tmp.cleanup)
        data = copy.deepcopy(VALID_RUN)
        data["metrics"]["safety_value"] = "potential"
        self._write_run(root, data)
        errors = validate_ecosystem_organ_preflight(root)
        self.assertTrue(any("safety_value" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
