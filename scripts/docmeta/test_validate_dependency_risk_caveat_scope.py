#!/usr/bin/env python3
"""Regression tests for dependency-risk-caveat-scope validation."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
VALIDATOR_PATH = (
    REPO_ROOT / "scripts" / "docmeta" / "validate_dependency_risk_caveat_scope.py"
)
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "dependency_risk_caveat_scope"

VALID_FIXTURES = [
    "valid/scoped-not-remediated.yml",
]

# Each invalid fixture must report at least the listed semantic rule (the value
# below). Some fixtures intentionally co-report additional rules; the test only
# asserts that the listed rule is present, not that it is isolated.
INVALID_FIXTURES = {
    "invalid/scoped-but-remediated.yml": "SCOPED_NOT_REMEDIATED_REQUIRES_FALSE_REMEDIATED",
    "invalid/security-ready-despite-unremediated.yml": "SCOPED_NOT_REMEDIATED_BLOCKS_SECURITY_PRODUCTION",
    "invalid/production-ready-despite-unremediated.yml": "SCOPED_NOT_REMEDIATED_BLOCKS_SECURITY_PRODUCTION",
    "invalid/result-assessment-allowed.yml": "SCOPED_NOT_REMEDIATED_BLOCKS_RESULT_ASSESSMENT",
    "invalid/comparison-ready.yml": "SCOPED_NOT_REMEDIATED_BLOCKS_RESULT_ASSESSMENT",
    "invalid/functional-runtime-without-security-disclaimer.yml": "FUNCTIONAL_RUNTIME_EVIDENCE_MUST_NOT_BE_SECURITY_APPROVAL",
    "invalid/missing-does-not-establish.yml": "MISSING_MANDATORY_DOES_NOT_ESTABLISH",
    "invalid/source-evidence-missing.yml": "SOURCE_EVIDENCE_PATH_NOT_FOUND",
    "invalid/source-evidence-escape.yml": "SOURCE_EVIDENCE_PATH_ESCAPE",
    "invalid/nonzero-audit-marked-safe.yml": "AUDIT_EXIT_NONZERO_REQUIRES_NOT_REMEDIATED",
    "invalid/nonzero-audit-result-assessment-allowed.yml": "AUDIT_EXIT_NONZERO_REQUIRES_NOT_REMEDIATED",
    "invalid/nonzero-audit-comparison-ready.yml": "AUDIT_EXIT_NONZERO_REQUIRES_NOT_REMEDIATED",
    "invalid/remediated-out-of-scope.yml": "DEPENDENCY_RISK_REMEDIATED_OUT_OF_SCOPE",
    "invalid/remediation-performed-out-of-scope.yml": "REMEDIATION_PERFORMED_OUT_OF_SCOPE",
    "invalid/unknown-challenge-version.yml": "UNKNOWN_CHALLENGE_VERSION",
}


class DependencyRiskCaveatScopeValidatorTests(unittest.TestCase):
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

    def test_nonzero_audit_marked_safe_reports_audit_rule(self) -> None:
        # v1 has a single scope_status (scoped_not_remediated), so this fixture may
        # co-report a SCOPED_NOT_REMEDIATED_* rule. Contract coherence outweighs
        # artificial rule isolation; assert only that the audit rule is reported.
        completed = self.run_validator(
            FIXTURE_ROOT / "invalid/nonzero-audit-marked-safe.yml"
        )
        self.assertEqual(completed.returncode, 1, completed.stdout + completed.stderr)
        self.assertIn("AUDIT_EXIT_NONZERO_REQUIRES_NOT_REMEDIATED", completed.stdout)

    def test_schema_violation_exits_two(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            bad = Path(temp_dir) / "schema-invalid.yml"
            # Missing required fields (scope_status, source_evidence, ...).
            bad.write_text(
                'schema_version: "v1"\nartifact_type: "dependency_risk_caveat_scope"\n',
                encoding="utf-8",
            )
            completed = self.run_validator(bad)
            self.assertEqual(
                completed.returncode, 2, completed.stdout + completed.stderr
            )

    def test_wrong_schema_version_exits_two(self) -> None:
        # Start from an otherwise-valid fixture and change ONLY schema_version,
        # so this isolates the schema_version const check.
        base = (FIXTURE_ROOT / "valid/scoped-not-remediated.yml").read_text(
            encoding="utf-8"
        )
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
            bad.write_text("source_evidence: [\n", encoding="utf-8")
            completed = self.run_validator(bad)
            self.assertEqual(
                completed.returncode, 2, completed.stdout + completed.stderr
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
