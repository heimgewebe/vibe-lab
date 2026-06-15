#!/usr/bin/env python3
"""Regression tests for runtime-evidence-gate validation."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
VALIDATOR_PATH = REPO_ROOT / "scripts" / "docmeta" / "validate_runtime_evidence_gate.py"
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "runtime_evidence_gate"

VALID_FIXTURES = [
    "valid/pass-minimal.yml",
    "valid/partial-with-limitations.yml",
    "valid/missing-evidence-explicit.yml",
]

# Each invalid fixture must report at least a single semantic rule (the value below).
INVALID_FIXTURES = {
    "invalid/pass-with-missing-command-output.yml": "PASS_WITH_MISSING_COMMAND_OUTPUT",
    "invalid/pass-with-failed-check.yml": "PASS_WITH_NON_PASS_CHECK",
    "invalid/pass-with-nonzero-command.yml": "PASS_WITH_NONZERO_COMMAND",
    "invalid/pass-with-unexecuted-command.yml": "PASS_WITH_UNEXECUTED_COMMAND",
    "invalid/command-exit-code-mismatch.yml": "COMMAND_EXIT_CODE_MISMATCH",
    "invalid/non-pass-without-limitations.yml": "NON_PASS_REQUIRES_LIMITATIONS",
    "invalid/implementation-path-not-found.yml": "IMPLEMENTATION_PATH_NOT_FOUND",
    "invalid/path-escape-evidence.yml": "RUNTIME_EVIDENCE_PATH_ESCAPE",
    "invalid/missing-does-not-establish.yml": "MISSING_DOES_NOT_ESTABLISH",
    "invalid/unknown-challenge-version.yml": "UNKNOWN_CHALLENGE_VERSION",
    "invalid/challenge-version-mismatch.yml": "CHALLENGE_VERSION_MISMATCH",
}


class RuntimeEvidenceGateValidatorTests(unittest.TestCase):
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

    def test_strong_claim_without_runtime_evidence_reports_its_rule(self) -> None:
        # STRONG_CLAIM is a pass-state backstop that necessarily co-occurs with
        # whatever made the checks non-evidenced; assert the specific rule id is
        # reported rather than relying on the co-occurring rule.
        completed = self.run_validator(
            FIXTURE_ROOT / "invalid/strong-claim-without-runtime-evidence.yml"
        )
        self.assertEqual(completed.returncode, 1, completed.stdout + completed.stderr)
        self.assertIn("STRONG_CLAIM_WITHOUT_RUNTIME_EVIDENCE", completed.stdout)

    def test_pass_nonzero_command_does_not_also_flag_unexecuted(self) -> None:
        # A non-zero (executed) command must be flagged as nonzero, never as
        # unexecuted; guards against conflating exit_code=N with exit_code=null.
        completed = self.run_validator(
            FIXTURE_ROOT / "invalid/pass-with-nonzero-command.yml"
        )
        self.assertEqual(completed.returncode, 1, completed.stdout + completed.stderr)
        self.assertIn("PASS_WITH_NONZERO_COMMAND", completed.stdout)
        self.assertNotIn("PASS_WITH_UNEXECUTED_COMMAND", completed.stdout)

    def test_schema_violation_exits_two(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            bad = Path(temp_dir) / "schema-invalid.yml"
            # Missing required fields (commands, checks, does_not_establish, ...).
            bad.write_text(
                'schema_version: "v1"\nrun_id: "x"\n', encoding="utf-8"
            )
            completed = self.run_validator(bad)
            self.assertEqual(
                completed.returncode, 2, completed.stdout + completed.stderr
            )

    def test_wrong_schema_version_exits_two(self) -> None:
        # Start from an otherwise-valid fixture and change ONLY schema_version,
        # so this isolates the schema_version const check.
        base = (FIXTURE_ROOT / "valid/pass-minimal.yml").read_text(encoding="utf-8")
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
            bad.write_text("commands: [\n", encoding="utf-8")
            completed = self.run_validator(bad)
            self.assertEqual(
                completed.returncode, 2, completed.stdout + completed.stderr
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
