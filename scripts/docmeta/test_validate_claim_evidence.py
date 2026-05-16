#!/usr/bin/env python3
"""Regression tests for semantic claim-evidence validation."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
VALIDATOR_PATH = REPO_ROOT / "scripts" / "docmeta" / "validate_claim_evidence.py"
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "claim_evidence_semantic"

VALID_FIXTURES = [
    "valid/pass-with-repo-local-test-output.yml",
    "valid/missing-evidence-not-pass.yml",
    "valid/pass-with-ci-artifact.yml",
    "valid/pass-with-external-verified.yml",
    "valid/pass-with-derived-auditor-output.yml",
]

INVALID_FIXTURES = {
    "invalid/pass-with-self-reported-only.yml": "PASS_WITHOUT_STRONG_EVIDENCE",
    "invalid/pass-with-missing-evidence.yml": "PASS_WITH_MISSING_EVIDENCE",
    "invalid/missing-evidence-with-invalid-verdict.yml": "MISSING_EVIDENCE_WITH_INVALID_VERDICT",
    "invalid/external-verified-without-sha.yml": "EXTERNAL_VERIFIED_WITHOUT_SOURCE_OR_SHA256",
    "invalid/pass-with-external-unverified-only.yml": "PASS_WITH_EXTERNAL_UNVERIFIED_ONLY",
    "invalid/testcount-pass-without-test-output.yml": "TESTCOUNT_WITHOUT_TEST_OUTPUT",
    "invalid/ci-pass-without-ci-evidence.yml": "CI_PASS_WITHOUT_CI_EVIDENCE",
    "invalid/make-validate-pass-without-exit-zero.yml": "MAKE_VALIDATE_PASS_WITHOUT_EXIT_ZERO",
    "invalid/make-validate-pass-without-command-output.yml": "MAKE_VALIDATE_WITH_COMMAND_MISMATCH",
    "invalid/repo-local-nonexistent-path.yml": "REPO_LOCAL_EVIDENCE_PATH_NOT_FOUND",
}


class ClaimEvidenceValidatorTests(unittest.TestCase):
    def run_validator(self, *paths: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VALIDATOR_PATH), *[str(path) for path in paths]],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_valid_fixtures_exit_zero(self) -> None:
        paths = [FIXTURE_ROOT / rel_path for rel_path in VALID_FIXTURES]
        completed = self.run_validator(*paths)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertEqual(completed.stdout.strip(), "")

    def test_invalid_fixtures_exit_one_with_rule_ids(self) -> None:
        for rel_path, rule_id in INVALID_FIXTURES.items():
            with self.subTest(rel_path=rel_path):
                completed = self.run_validator(FIXTURE_ROOT / rel_path)
                self.assertEqual(completed.returncode, 1, completed.stdout + completed.stderr)
                self.assertIn(rule_id, completed.stdout)

    def test_path_escape_fixture_fails_schema_validation(self) -> None:
        # Path-escape is blocked at schema level (evidence.path pattern rejects `../../...`),
        # before semantic checks run. Exit code is 2 (schema error), not 1 (semantic error).
        completed = self.run_validator(FIXTURE_ROOT / "invalid/repo-local-path-escape.yml")
        self.assertEqual(completed.returncode, 2, completed.stdout + completed.stderr)
        self.assertIn("does not match", completed.stdout)

    def test_parse_error_exits_two(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            bad_fixture = Path(temp_dir) / "bad.yml"
            bad_fixture.write_text("claims: [\n", encoding="utf-8")
            completed = self.run_validator(bad_fixture)
            self.assertEqual(completed.returncode, 2, completed.stdout + completed.stderr)
            self.assertIn("ERROR path=", completed.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)