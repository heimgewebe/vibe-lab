#!/usr/bin/env python3
"""Regression tests for result-assessment-readiness validation."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
VALIDATOR_PATH = REPO_ROOT / "scripts" / "docmeta" / "validate_result_assessment_readiness.py"
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "result_assessment_readiness"

VALID_FIXTURES = [
    "valid/blocked-minimal.yml",
]

# Each invalid fixture must report at least the listed semantic rule.
INVALID_FIXTURES = {
    "invalid/blocked-but-assessment-allowed.yml": "READINESS_BLOCKED_REQUIRES_FALSE_ALLOWED",
    "invalid/ready-with-open-blocker.yml": "READINESS_READY_REQUIRES_NO_OPEN_BLOCKERS",
    "invalid/blocked-without-open-blocker.yml": "BLOCKED_REQUIRES_OPEN_BLOCKER",
    "invalid/claim-overlap.yml": "ALLOWED_DISALLOWED_CLAIM_OVERLAP",
    "invalid/missing-mandatory-disallowed-claim.yml": "MISSING_MANDATORY_DISALLOWED_CLAIM",
    "invalid/evidence-path-not-found.yml": "EVIDENCE_PATH_NOT_FOUND",
    "invalid/evidence-path-escape.yml": "EVIDENCE_PATH_ESCAPE",
    "invalid/ready-with-partial-runtime-gate.yml": "PARTIAL_RUNTIME_GATE_BLOCKS_READY",
}


class ResultAssessmentReadinessValidatorTests(unittest.TestCase):
    def run_validator(self, *paths: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VALIDATOR_PATH), *[str(path) for path in paths]],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_valid_fixtures_exit_zero(self) -> None:
        for rel_path in VALID_FIXTURES:
            with self.subTest(rel_path=rel_path):
                completed = self.run_validator(FIXTURE_ROOT / rel_path)
                self.assertEqual(
                    completed.returncode, 0, completed.stdout + completed.stderr
                )

    def test_invalid_fixtures_exit_one_with_rule_ids(self) -> None:
        for rel_path, rule_id in INVALID_FIXTURES.items():
            with self.subTest(rel_path=rel_path):
                completed = self.run_validator(FIXTURE_ROOT / rel_path)
                self.assertEqual(
                    completed.returncode, 1, completed.stdout + completed.stderr
                )
                self.assertIn(rule_id, completed.stdout)

    def test_partial_runtime_gate_fixture_only_flags_its_rule(self) -> None:
        # The ready-with-partial fixture is built to isolate the gate-coupling rule:
        # blockers is empty, so the open-blocker rule must NOT also fire.
        completed = self.run_validator(
            FIXTURE_ROOT / "invalid/ready-with-partial-runtime-gate.yml"
        )
        self.assertEqual(completed.returncode, 1, completed.stdout + completed.stderr)
        self.assertIn("PARTIAL_RUNTIME_GATE_BLOCKS_READY", completed.stdout)
        self.assertNotIn("READINESS_READY_REQUIRES_NO_OPEN_BLOCKERS", completed.stdout)

    def test_schema_violation_exits_two(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            bad = Path(temp_dir) / "schema-invalid.yml"
            # Missing required fields (blockers, claims, evidence, ...).
            bad.write_text(
                'schema_version: "v1"\nartifact_type: "result_assessment_readiness"\n',
                encoding="utf-8",
            )
            completed = self.run_validator(bad)
            self.assertEqual(
                completed.returncode, 2, completed.stdout + completed.stderr
            )

    def test_wrong_schema_version_exits_two(self) -> None:
        # Start from an otherwise-valid fixture and change ONLY schema_version,
        # so this isolates the schema_version const check.
        base = (FIXTURE_ROOT / "valid/blocked-minimal.yml").read_text(encoding="utf-8")
        mutated = base.replace('schema_version: "v1"', 'schema_version: "1.0.0"', 1)
        self.assertIn('schema_version: "1.0.0"', mutated)
        with tempfile.TemporaryDirectory() as temp_dir:
            bad = Path(temp_dir) / "wrong-version.yml"
            bad.write_text(mutated, encoding="utf-8")
            completed = self.run_validator(bad)
            self.assertEqual(
                completed.returncode, 2, completed.stdout + completed.stderr
            )

    def test_parse_error_exits_two(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            bad = Path(temp_dir) / "bad.yml"
            bad.write_text("blockers: [\n", encoding="utf-8")
            completed = self.run_validator(bad)
            self.assertEqual(
                completed.returncode, 2, completed.stdout + completed.stderr
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
