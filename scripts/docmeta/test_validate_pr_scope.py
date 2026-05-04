#!/usr/bin/env python3
"""Regression tests for validate_pr_scope.py.

Run with:
    python3 scripts/docmeta/test_validate_pr_scope.py
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
VALIDATOR = REPO_ROOT / "scripts" / "docmeta" / "validate_pr_scope.py"
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "pr_scope"

# Fixtures that should produce exit 0 when passed via --changed-files
VALID_FIXTURES = [
    "valid/evidence-pack.yml",
    "valid/summary.md",
    "valid/test-output.txt",
    # PASS claim referencing itself + real other evidence — must be allowed
    "valid/evidence-pack-with-self-plus-real-evidence.yml",
]

# Fixtures with their expected rule IDs (all should produce exit 1)
INVALID_FIXTURES: dict[str, str] = {
    "invalid/full-pr-diff.patch": "FORBIDDEN_FULL_DIFF_ARTIFACT",
    "invalid/workflow-full-log.txt": "FORBIDDEN_RAW_DUMP_ARTIFACT",
    "invalid/api-dump.json": "FORBIDDEN_RAW_DUMP_ARTIFACT",
    "invalid/self-observation/evidence-pack.yml": "EVIDENCE_SELF_OBSERVATION",
}


def _run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def _changed_files_arg(paths: list[Path]) -> list[str]:
    """Write paths to a temp file, return [--changed-files, tmppath]."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        for p in paths:
            try:
                f.write(str(p.relative_to(REPO_ROOT)) + "\n")
            except ValueError:
                f.write(str(p) + "\n")
        tmp = f.name
    return ["--changed-files", tmp]


class ValidFixtureTests(unittest.TestCase):
    def test_valid_fixtures_individually_exit_zero(self) -> None:
        for rel in VALID_FIXTURES:
            with self.subTest(fixture=rel):
                path = FIXTURE_ROOT / rel
                cf_args = _changed_files_arg([path])
                result = _run(cf_args)
                self.assertEqual(
                    result.returncode,
                    0,
                    f"Expected exit 0 for {rel}:\n{result.stdout}{result.stderr}",
                )
                self.assertEqual(result.stdout.strip(), "")

    def test_valid_fixtures_all_together_exit_zero(self) -> None:
        paths = [FIXTURE_ROOT / rel for rel in VALID_FIXTURES]
        cf_args = _changed_files_arg(paths)
        result = _run(cf_args)
        self.assertEqual(
            result.returncode,
            0,
            f"Expected exit 0 for all valid fixtures:\n{result.stdout}{result.stderr}",
        )

    def test_changed_files_mode_no_forbidden_paths_exit_zero(self) -> None:
        safe_paths = [FIXTURE_ROOT / "valid" / "test-output.txt"]
        cf_args = _changed_files_arg(safe_paths)
        result = _run(cf_args)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class InvalidFixtureTests(unittest.TestCase):
    def test_invalid_fixtures_exit_one_with_rule_id(self) -> None:
        for rel, expected_rule in INVALID_FIXTURES.items():
            with self.subTest(fixture=rel):
                path = FIXTURE_ROOT / rel
                cf_args = _changed_files_arg([path])
                result = _run(cf_args)
                self.assertEqual(
                    result.returncode,
                    1,
                    f"Expected exit 1 for {rel}:\n{result.stdout}{result.stderr}",
                )
                self.assertIn(
                    expected_rule,
                    result.stdout,
                    f"Rule ID '{expected_rule}' not found in output for {rel}:\n{result.stdout}",
                )


class OversizedArtifactTest(unittest.TestCase):
    def test_oversized_generic_artifact_exits_one(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="wb", suffix="-oversized.bin", delete=False
        ) as f:
            f.write(b"x" * (300 * 1024))
            big_path = Path(f.name)
        try:
            cf_args = _changed_files_arg([big_path])
            result = _run(cf_args)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("ARTIFACT_TOO_LARGE", result.stdout)
        finally:
            big_path.unlink(missing_ok=True)

    def test_oversized_allowed_name_still_blocked(self) -> None:
        # A file named exactly "test-output.txt" must not bypass the size limit.
        with tempfile.TemporaryDirectory() as tmp:
            big_path = Path(tmp) / "test-output.txt"
            big_path.write_bytes(b"y" * (300 * 1024))
            cf_args = _changed_files_arg([big_path])
            result = _run(cf_args)
            self.assertEqual(
                result.returncode,
                1,
                f"Oversized test-output.txt must be blocked:\n{result.stdout}{result.stderr}",
            )
            self.assertIn("ARTIFACT_TOO_LARGE", result.stdout)


class BrokenPolicyTest(unittest.TestCase):
    def test_broken_policy_exits_two(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yml", delete=False
        ) as f:
            f.write(": invalid: [yaml: {broken\n")
            broken_policy = f.name
        try:
            result = _run(["--policy", broken_policy])
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("POLICY_PARSE_ERROR", result.stderr)
        finally:
            Path(broken_policy).unlink(missing_ok=True)

    def test_missing_policy_exits_two(self) -> None:
        result = _run(["--policy", "/nonexistent/path/policy.yml"])
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("POLICY_PARSE_ERROR", result.stderr)


class RepoScanCleanTest(unittest.TestCase):
    def test_repo_scan_default_exits_zero(self) -> None:
        result = _run([])
        self.assertEqual(
            result.returncode,
            0,
            f"Repo scan produced unexpected violations:\n{result.stdout}{result.stderr}",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
