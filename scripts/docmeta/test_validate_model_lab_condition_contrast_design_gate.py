#!/usr/bin/env python3
"""Regression tests for model-lab-condition-contrast-design-gate validation."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
VALIDATOR_PATH = (
    REPO_ROOT
    / "scripts"
    / "docmeta"
    / "validate_model_lab_condition_contrast_design_gate.py"
)
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "model_lab_condition_contrast_design_gate"
REAL_ARTIFACT = (
    REPO_ROOT
    / "experiments"
    / "2026-05-31_model-lab-replication-series"
    / "results"
    / "condition-contrast-design-gate.yml"
)

VALID_FIXTURES = [
    "valid/basic.yml",
]

# Each invalid fixture must report at least the listed semantic rule (the value
# below). Some fixtures may co-report additional rules; the test only asserts that
# the listed rule is present, not that it is isolated.
INVALID_FIXTURES = {
    "invalid/missing-triage-source.yml": "CONTRAST_GATE_REQUIRES_SINGLE_TRIAGE_SOURCE",
    "invalid/multiple-triage-sources.yml": "CONTRAST_GATE_REQUIRES_SINGLE_TRIAGE_SOURCE",
    "invalid/source-wrong-series.yml": "CONTRAST_GATE_REQUIRES_MATCHING_SOURCE_IDENTITY",
    "invalid/triage-wrong-task.yml": "CONTRAST_GATE_REQUIRES_TRIAGE_RECOMMENDATION",
    "invalid/triage-wrong-target-blocker.yml": "CONTRAST_GATE_REQUIRES_TRIAGE_RECOMMENDATION",
    "invalid/readiness-not-blocked.yml": "CONTRAST_GATE_REQUIRES_BLOCKED_READINESS",
    "invalid/readiness-assessment-allowed.yml": "CONTRAST_GATE_REQUIRES_BLOCKED_READINESS",
    "invalid/readiness-comparison-ready.yml": "CONTRAST_GATE_REQUIRES_BLOCKED_READINESS",
    "invalid/target-blocker-closed.yml": "CONTRAST_GATE_REQUIRES_OPEN_TARGET_BLOCKER",
    "invalid/primary-axis-not-required.yml": "CONTRAST_GATE_REQUIRES_SINGLE_PRIMARY_AXIS_POLICY",
    "invalid/primary-axis-count-not-one.yml": "CONTRAST_GATE_REQUIRES_SINGLE_PRIMARY_AXIS_POLICY",
    "invalid/missing-invariant-dimensions.yml": "CONTRAST_GATE_REQUIRES_COMPLETE_CRITERIA",
    "invalid/materiality-evidence-missing.yml": "CONTRAST_GATE_REQUIRES_COMPLETE_CRITERIA",
    "invalid/duplicate-semantic-id.yml": "CONTRAST_GATE_REQUIRES_UNIQUE_SEMANTIC_IDS",
    "invalid/confounder-control-incomplete.yml": "CONTRAST_GATE_REQUIRES_COMPLETE_CONFOUNDER_CONTROLS",
    "invalid/criteria-defined-design-disallowed.yml": "CONTRAST_GATE_REQUIRES_STATUS_PERMISSION_CONSISTENCY",
    "invalid/blocked-design-allowed.yml": "CONTRAST_GATE_REQUIRES_STATUS_PERMISSION_CONSISTENCY",
    "invalid/run-004-execution-allowed.yml": "CONTRAST_GATE_FORBIDS_EXECUTION_AND_ASSESSMENT",
    "invalid/result-assessment-allowed.yml": "CONTRAST_GATE_FORBIDS_EXECUTION_AND_ASSESSMENT",
    "invalid/comparison-ready.yml": "CONTRAST_GATE_FORBIDS_EXECUTION_AND_ASSESSMENT",
    "invalid/mandatory-non-claim-missing.yml": "CONTRAST_GATE_REQUIRES_MANDATORY_NON_CLAIMS",
    "invalid/source-path-escape.yml": "CONTRAST_GATE_REQUIRES_SAFE_EXISTING_SOURCE_PATHS",
    "invalid/source-file-missing.yml": "CONTRAST_GATE_REQUIRES_SAFE_EXISTING_SOURCE_PATHS",
}


class ModelLabConditionContrastDesignGateValidatorTests(unittest.TestCase):
    def run_validator(self, *paths: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VALIDATOR_PATH), *[str(path) for path in paths]],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def assert_exit_code(
        self, completed: subprocess.CompletedProcess[str], expected: int
    ) -> None:
        self.assertEqual(expected, completed.returncode, completed.stdout + completed.stderr)

    def test_valid_fixtures_exit_zero(self) -> None:
        for rel_path in VALID_FIXTURES:
            with self.subTest(rel_path=rel_path):
                self.assert_exit_code(self.run_validator(FIXTURE_ROOT / rel_path), 0)

    def test_real_series_artifact_exits_zero(self) -> None:
        # The real series gate artifact must validate (also exercises discovery glob
        # consumers indirectly: this is the artifact `make validate-...` resolves).
        self.assertTrue(REAL_ARTIFACT.is_file(), f"missing real artifact: {REAL_ARTIFACT}")
        self.assert_exit_code(self.run_validator(REAL_ARTIFACT), 0)

    def test_invalid_fixtures_exit_one_with_rule_ids(self) -> None:
        for rel_path, rule_id in INVALID_FIXTURES.items():
            with self.subTest(rel_path=rel_path):
                completed = self.run_validator(FIXTURE_ROOT / rel_path)
                self.assert_exit_code(completed, 1)
                self.assertIn(rule_id, completed.stdout)

    def test_schema_violation_exits_two(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            bad = Path(temp_dir) / "schema-invalid.yml"
            # Missing required fields (series_id, source_evidence, ...).
            bad.write_text(
                'schema_version: "v1"\n'
                'artifact_type: "model_lab_condition_contrast_design_gate"\n',
                encoding="utf-8",
            )
            self.assert_exit_code(self.run_validator(bad), 2)

    def test_wrong_schema_version_exits_two(self) -> None:
        # Start from an otherwise-valid fixture and change ONLY schema_version via a
        # real YAML round-trip (robust to formatting), isolating the const check.
        data = self._basic_data()
        data["schema_version"] = "1.0.0"
        completed = self._run_on_data(data)
        self.assert_exit_code(completed, 2)

    def test_parse_error_exits_two(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            bad = Path(temp_dir) / "bad.yml"
            bad.write_text("source_evidence: [\n", encoding="utf-8")
            self.assert_exit_code(self.run_validator(bad), 2)

    def _basic_data(self) -> dict:
        return yaml.safe_load((FIXTURE_ROOT / "valid/basic.yml").read_text(encoding="utf-8"))

    def _run_on_data(self, data: dict) -> subprocess.CompletedProcess[str]:
        # Repo-relative source_evidence paths resolve against the repo root, so the
        # mutated file may live in a temp dir.
        with tempfile.TemporaryDirectory() as temp_dir:
            mutated = Path(temp_dir) / "mutated.yml"
            mutated.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
            return self.run_validator(mutated)

    def test_empty_invariant_dimensions_is_schema_error(self) -> None:
        data = self._basic_data()
        data["invariant_dimensions"] = []
        completed = self._run_on_data(data)
        self.assert_exit_code(completed, 2)
        self.assertIn("instance_path=invariant_dimensions", completed.stdout)

    def test_empty_evidence_required_is_schema_error(self) -> None:
        data = self._basic_data()
        data["materiality_criteria"][0]["evidence_required"] = []
        completed = self._run_on_data(data)
        self.assert_exit_code(completed, 2)
        self.assertIn(
            "instance_path=materiality_criteria.0.evidence_required", completed.stdout
        )

    def test_invalid_gate_status_enum_is_schema_error(self) -> None:
        data = self._basic_data()
        data["gate_status"] = "open"  # not in {blocked, criteria_defined}
        completed = self._run_on_data(data)
        self.assert_exit_code(completed, 2)
        self.assertIn("instance_path=gate_status", completed.stdout)

    def test_blocker_status_after_gate_must_be_open(self) -> None:
        data = self._basic_data()
        data["blocker_status_after_gate"] = "resolved"
        completed = self._run_on_data(data)
        self.assert_exit_code(completed, 2)
        self.assertIn("instance_path=blocker_status_after_gate", completed.stdout)

    def test_invalid_effect_if_uncontrolled_is_schema_error(self) -> None:
        data = self._basic_data()
        data["confounder_controls"][0]["effect_if_uncontrolled"] = "ignore"
        completed = self._run_on_data(data)
        self.assert_exit_code(completed, 2)
        self.assertIn(
            "instance_path=confounder_controls.0.effect_if_uncontrolled", completed.stdout
        )

    def test_blocked_readiness_diagnostic_names_all_required_signals(self) -> None:
        completed = self.run_validator(
            FIXTURE_ROOT / "invalid/readiness-comparison-ready.yml"
        )
        self.assert_exit_code(completed, 1)
        self.assertIn("CONTRAST_GATE_REQUIRES_BLOCKED_READINESS", completed.stdout)
        self.assertIn("readiness_status=blocked", completed.stdout)
        self.assertIn("result_assessment_allowed=false", completed.stdout)
        self.assertIn("comparison_ready=false", completed.stdout)
        self.assertIn("missing fields do not count as false", completed.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
