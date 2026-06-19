#!/usr/bin/env python3
"""Regression tests for model-lab-next-blocker-triage validation."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
VALIDATOR_PATH = (
    REPO_ROOT / "scripts" / "docmeta" / "validate_model_lab_next_blocker_triage.py"
)
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "model_lab_next_blocker_triage"

VALID_FIXTURES = [
    "valid/basic.yml",
]

# Each invalid fixture must report at least the listed semantic rule (the value
# below). Some fixtures may co-report additional rules; the test only asserts that
# the listed rule is present, not that it is isolated.
INVALID_FIXTURES = {
    "invalid/readiness-gate-not-blocked.yml": "TRIAGE_REQUIRES_BLOCKED_ASSESSMENT",
    "invalid/readiness-gate-wrong-series.yml": "TRIAGE_REQUIRES_MATCHING_READINESS_GATE_SOURCE",
    "invalid/readiness-gate-wrong-artifact-type.yml": "TRIAGE_REQUIRES_MATCHING_READINESS_GATE_SOURCE",
    "invalid/result-assessment-allowed.yml": "TRIAGE_REQUIRES_FALSE_RESULT_ASSESSMENT_ALLOWED",
    "invalid/comparison-ready.yml": "TRIAGE_REQUIRES_FALSE_COMPARISON_READY",
    "invalid/missing-recommended-next-task.yml": "TRIAGE_REQUIRES_RECOMMENDED_NEXT_TASK",
    "invalid/recommended-target-blocker-not-listed.yml": "TRIAGE_REQUIRES_RECOMMENDED_TARGET_BLOCKER",
    "invalid/resolved-remaining-blocker.yml": "TRIAGE_REQUIRES_OPEN_REMAINING_BLOCKERS",
    "invalid/missing-dependency-risk-scope-source.yml": "TRIAGE_REQUIRES_DEPENDENCY_RISK_SCOPE_SOURCE",
    "invalid/dependency-risk-scope-wrong-series.yml": "TRIAGE_REQUIRES_MATCHING_DEPENDENCY_RISK_SCOPE_SOURCE",
    "invalid/dependency-risk-scope-wrong-artifact-type.yml": "TRIAGE_REQUIRES_MATCHING_DEPENDENCY_RISK_SCOPE_SOURCE",
    "invalid/missing-scope-blocker.yml": "TRIAGE_REQUIRES_ALL_SCOPE_BLOCKERS",
    "invalid/unexpected-scope-blocker.yml": "TRIAGE_REQUIRES_ALL_SCOPE_BLOCKERS",
    "invalid/source-evidence-missing.yml": "SOURCE_EVIDENCE_PATH_NOT_FOUND",
    "invalid/source-evidence-escape.yml": "SOURCE_EVIDENCE_PATH_ESCAPE",
    "invalid/missing-does-not-establish.yml": "MISSING_MANDATORY_DOES_NOT_ESTABLISH",
    "invalid/recommended-next-task-missing-reason.yml": "TRIAGE_REQUIRES_RECOMMENDED_NEXT_TASK",
    "invalid/multiple-readiness-gates.yml": "TRIAGE_REQUIRES_SINGLE_READINESS_GATE_SOURCE",
    "invalid/multiple-dependency-risk-scopes.yml": "TRIAGE_REQUIRES_SINGLE_DEPENDENCY_RISK_SCOPE_SOURCE",
    "invalid/dependency-risk-scope-invalid-remaining-blockers.yml": "TRIAGE_REQUIRES_VALID_DEPENDENCY_RISK_SCOPE_BLOCKERS",
    "invalid/readiness-missing-result-assessment-allowed.yml": "TRIAGE_REQUIRES_BLOCKED_ASSESSMENT",
    "invalid/readiness-comparison-ready-true.yml": "TRIAGE_REQUIRES_BLOCKED_ASSESSMENT",
    "invalid/readiness-missing-comparison-ready.yml": "TRIAGE_REQUIRES_BLOCKED_ASSESSMENT",
    "invalid/task-shape-mismatch.yml": "TRIAGE_REQUIRES_RECOMMENDED_TASK_SHAPE_MATCH",
    "invalid/target-not-top-priority.yml": "TRIAGE_REQUIRES_TOP_PRIORITY_TARGET",
    "invalid/duplicate-blocker-id.yml": "TRIAGE_REQUIRES_UNIQUE_BLOCKER_IDS",
    "invalid/duplicate-recommended-position.yml": "TRIAGE_REQUIRES_UNIQUE_RECOMMENDED_POSITIONS",
    "invalid/duplicate-triage-criteria-id.yml": "TRIAGE_REQUIRES_UNIQUE_TRIAGE_CRITERIA_IDS",
    "invalid/scope-missing-remaining-blockers.yml": "TRIAGE_REQUIRES_VALID_DEPENDENCY_RISK_SCOPE_BLOCKERS",
}


class ModelLabNextBlockerTriageValidatorTests(unittest.TestCase):
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
                'schema_version: "v1"\nartifact_type: "model_lab_next_blocker_triage"\n',
                encoding="utf-8",
            )
            self.assert_exit_code(self.run_validator(bad), 2)

    def test_wrong_schema_version_exits_two(self) -> None:
        # Start from an otherwise-valid fixture and change ONLY schema_version via a
        # real YAML round-trip (robust to formatting), isolating the const check.
        data = yaml.safe_load((FIXTURE_ROOT / "valid/basic.yml").read_text(encoding="utf-8"))
        data["schema_version"] = "1.0.0"
        with tempfile.TemporaryDirectory() as temp_dir:
            bad = Path(temp_dir) / "wrong-version.yml"
            bad.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
            self.assert_exit_code(self.run_validator(bad), 2)

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

    def test_empty_triage_criteria_is_schema_error(self) -> None:
        data = self._basic_data()
        data["triage_criteria"] = []
        completed = self._run_on_data(data)
        self.assert_exit_code(completed, 2)
        self.assertIn("instance_path=triage_criteria", completed.stdout)

    def test_empty_must_not_mix_with_is_schema_error(self) -> None:
        data = self._basic_data()
        data["remaining_blockers"][0]["must_not_mix_with"] = []
        completed = self._run_on_data(data)
        self.assert_exit_code(completed, 2)
        self.assertIn("must_not_mix_with", completed.stdout)

    def test_scope_missing_remaining_blockers_diagnostic(self) -> None:
        completed = self.run_validator(
            FIXTURE_ROOT / "invalid/scope-missing-remaining-blockers.yml"
        )
        self.assert_exit_code(completed, 1)
        self.assertIn("'remaining_blockers' is missing", completed.stdout)

    def test_scope_wrong_type_remaining_blockers_diagnostic(self) -> None:
        completed = self.run_validator(
            FIXTURE_ROOT / "invalid/dependency-risk-scope-invalid-remaining-blockers.yml"
        )
        self.assert_exit_code(completed, 1)
        self.assertIn("'remaining_blockers' must be a list", completed.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
