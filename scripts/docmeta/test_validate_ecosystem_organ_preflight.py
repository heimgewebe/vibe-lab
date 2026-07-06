#!/usr/bin/env python3
"""Regression tests for validate_ecosystem_organ_preflight.py."""

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

VALID_RUN: dict = {
    "schema_version": "0.1.0",
    "task_id": "run-001-example",
    "timestamp": "2026-07-06T00:00:00Z",
    "repo": "heimgewebe/vibe-lab",
    "pr": 292,
    "issue": None,
    "slice": "example slice",
    "active_ball": "PR #292",
    "task_class": "experiment_instrumentation",
    "perceived_complexity": "medium",
    "primary_truth_source": "repo_pr_ci",
    "allowed_context_organs": ["vibe_lab"],
    "blocked_organs": ["bureau"],
    "stop_rules": ["Kein Merge ohne CI-Gate."],
    "predicted_primary_organ": "repo_pr_ci",
    "actual_primary_organ": "repo_pr_ci",
    "evidence_refs": ["results/evidence.jsonl"],
    "metrics": {
        "wrong_organ_corrections": 0,
        "rework_loops": 0,
        "next_step_ambiguity": "low",
        "friction_cost_minutes": 5,
        "safety_value": "none",
    },
    "verdict": "usability_only",
    "interpretation_budget": {
        "allowed_claims": ["Die Run-Struktur ist real erfasst."],
        "disallowed_claims": ["Ein Run belegt Wirksamkeit."],
        "epistemic_gaps": ["friction_cost_minutes ist self_reported."],
    },
}


class EcosystemOrganPreflightTests(unittest.TestCase):
    def _root(self) -> tuple[tempfile.TemporaryDirectory, Path]:
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        exp = root / EXPERIMENT_REL
        (exp / "results" / "runs").mkdir(parents=True)
        (exp / "results" / "evidence.jsonl").write_text(
            '{"event_type":"observation","timestamp":"2026-07-06T00:00:00Z",'
            '"iteration":1,"metric":"seed","value":"x","context":"t"}\n',
            encoding="utf-8",
        )
        (exp / "manifest.yml").write_text(
            "experiment:\n  execution_status: executed\n", encoding="utf-8"
        )
        return tmp, root

    def _write_run(self, root: Path, data: dict, name: str = "run-001.yml") -> None:
        path = root / EXPERIMENT_REL / "results" / "runs" / name
        path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")

    def _write_result(self, root: Path, body: str) -> None:
        path = root / EXPERIMENT_REL / "results" / "result.md"
        path.write_text(body, encoding="utf-8")

    # --- happy path -----------------------------------------------------
    def test_valid_run_passes(self) -> None:
        tmp, root = self._root()
        self.addCleanup(tmp.cleanup)
        self._write_run(root, copy.deepcopy(VALID_RUN))
        self.assertEqual(validate_ecosystem_organ_preflight(root), [])

    def test_template_is_ignored(self) -> None:
        tmp, root = self._root()
        self.addCleanup(tmp.cleanup)
        self._write_run(root, copy.deepcopy(VALID_RUN))
        # A broken TEMPLATE.yml must not trip the validator.
        self._write_run(root, {"garbage": True}, name="TEMPLATE.yml")
        self.assertEqual(validate_ecosystem_organ_preflight(root), [])

    # --- required field -------------------------------------------------
    def test_missing_required_field_fails(self) -> None:
        tmp, root = self._root()
        self.addCleanup(tmp.cleanup)
        data = copy.deepcopy(VALID_RUN)
        del data["stop_rules"]
        self._write_run(root, data)
        errors = validate_ecosystem_organ_preflight(root)
        self.assertTrue(any("missing required field 'stop_rules'" in e for e in errors))

    # --- forbidden efficacy claim (run + result.md) ---------------------
    def test_forbidden_claim_in_run_fails(self) -> None:
        tmp, root = self._root()
        self.addCleanup(tmp.cleanup)
        data = copy.deepcopy(VALID_RUN)
        data["interpretation_budget"]["allowed_claims"] = [
            "Der Organ-Preflight verbessert bereits Oekosystem-Arbeit."
        ]
        self._write_run(root, data)
        errors = validate_ecosystem_organ_preflight(root)
        self.assertTrue(any("forbidden" in e for e in errors))

    def test_forbidden_claim_in_result_md_fails(self) -> None:
        tmp, root = self._root()
        self.addCleanup(tmp.cleanup)
        self._write_run(root, copy.deepcopy(VALID_RUN))
        self._write_result(
            root,
            "# result\n\nDer Organ-Preflight verbessert bereits Oekosystem-Arbeit.\n",
        )
        errors = validate_ecosystem_organ_preflight(root)
        self.assertTrue(any("forbidden efficacy claim in result.md" in e for e in errors))

    def test_disallowed_claims_section_is_exempt(self) -> None:
        tmp, root = self._root()
        self.addCleanup(tmp.cleanup)
        self._write_run(root, copy.deepcopy(VALID_RUN))
        self._write_result(
            root,
            "# result\n\n## Verdict\n\nSeed only.\n\n"
            "### Disallowed Claims\n\n"
            "- Der Organ-Preflight verbessert bereits Oekosystem-Arbeit.\n",
        )
        self.assertEqual(validate_ecosystem_organ_preflight(root), [])

    # --- invalid enum ---------------------------------------------------
    def test_invalid_next_step_ambiguity_fails(self) -> None:
        tmp, root = self._root()
        self.addCleanup(tmp.cleanup)
        data = copy.deepcopy(VALID_RUN)
        data["metrics"]["next_step_ambiguity"] = "very_high"
        self._write_run(root, data)
        errors = validate_ecosystem_organ_preflight(root)
        self.assertTrue(any("next_step_ambiguity" in e for e in errors))

    # --- missing evidence ref -------------------------------------------
    def test_missing_evidence_ref_fails(self) -> None:
        tmp, root = self._root()
        self.addCleanup(tmp.cleanup)
        data = copy.deepcopy(VALID_RUN)
        data["evidence_refs"] = []
        self._write_run(root, data)
        errors = validate_ecosystem_organ_preflight(root)
        self.assertTrue(any("evidence_refs" in e for e in errors))

    def test_nonexistent_evidence_ref_fails(self) -> None:
        tmp, root = self._root()
        self.addCleanup(tmp.cleanup)
        data = copy.deepcopy(VALID_RUN)
        data["evidence_refs"] = ["results/does-not-exist.jsonl"]
        self._write_run(root, data)
        errors = validate_ecosystem_organ_preflight(root)
        self.assertTrue(any("does not exist" in e for e in errors))

    # --- executed manifest without run metrics --------------------------
    def test_executed_without_run_metrics_fails(self) -> None:
        tmp, root = self._root()
        self.addCleanup(tmp.cleanup)
        # No run file written; manifest already says executed.
        errors = validate_ecosystem_organ_preflight(root)
        self.assertTrue(any("no results/runs/run-*.yml carries a metrics block" in e for e in errors))

    # --- real repository ------------------------------------------------
    def test_real_repository_is_valid(self) -> None:
        self.assertEqual(validate_ecosystem_organ_preflight(), [])


if __name__ == "__main__":
    unittest.main()
