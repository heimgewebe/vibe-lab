#!/usr/bin/env python3
"""Regression tests for validate_pr_scope.py.

Run with:
    python3 scripts/docmeta/test_validate_pr_scope.py
"""
from __future__ import annotations

import contextlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

try:
    import yaml
except ImportError as exc:
    print("ERROR: Missing PyYAML. Install with: pip install pyyaml", file=sys.stderr)
    raise SystemExit(2) from exc

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
VALIDATOR = REPO_ROOT / "scripts" / "docmeta" / "validate_pr_scope.py"
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "pr_scope"

_FORBIDDEN_PATTERNS = [
    "(^|/).*full.*diff.*",
    "(^|/).*pr.*diff.*",
    r"(^|/).*\.patch$",
    r"(^|/).*\.diff$",
    "(^|/).*api.*dump.*",
    "(^|/).*raw.*response.*",
    "(^|/).*ci.*full.*log.*",
    "(^|/).*workflow.*full.*log.*",
    "(^|/).*transcript.*",
    "(^|/).*screenshot.*",
]

# Fixtures that should produce exit 0
VALID_FIXTURES = [
    "valid/evidence-pack.yml",
    "valid/summary.md",
    "valid/test-output.txt",
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


@contextlib.contextmanager
def _cf_context(paths: list[Path]):
    """Context manager: write paths to a temp file, yield [--changed-files, path], then clean up."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        for p in paths:
            try:
                f.write(str(p.relative_to(REPO_ROOT)) + "\n")
            except ValueError:
                f.write(str(p) + "\n")
        tmp = Path(f.name)
    try:
        yield ["--changed-files", str(tmp)]
    finally:
        tmp.unlink(missing_ok=True)


def _run_with_roots(paths: list[Path], artifact_root_dirs: list[Path]) -> subprocess.CompletedProcess[str]:
    """Run the validator with a temp policy using the given artifact_roots and a changed-files list."""
    roots_relative = []
    for root in artifact_root_dirs:
        try:
            roots_relative.append(str(root.relative_to(REPO_ROOT)))
        except ValueError:
            roots_relative.append(str(root))

    policy = {
        "schema_version": "1.0.0",
        "scope": {"artifact_roots": roots_relative},
        "limits": {"max_repo_local_evidence_bytes": 262144},
        "forbidden_path_patterns": _FORBIDDEN_PATTERNS,
        "self_observation": {"forbid_pass_claim_referencing_same_evidence_pack": True},
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as pf:
        yaml.dump(policy, pf, allow_unicode=True, default_flow_style=False)
        policy_path = Path(pf.name)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as cf:
        for p in paths:
            try:
                cf.write(str(p.relative_to(REPO_ROOT)) + "\n")
            except ValueError:
                cf.write(str(p) + "\n")
        cf_path = Path(cf.name)

    try:
        return subprocess.run(
            [sys.executable, str(VALIDATOR),
             "--policy", str(policy_path),
             "--changed-files", str(cf_path)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
    finally:
        policy_path.unlink(missing_ok=True)
        cf_path.unlink(missing_ok=True)


def _run_with_fixture_root(paths: list[Path]) -> subprocess.CompletedProcess[str]:
    return _run_with_roots(paths, [FIXTURE_ROOT])


class ValidFixtureTests(unittest.TestCase):
    def test_valid_fixtures_individually_exit_zero(self) -> None:
        for rel in VALID_FIXTURES:
            with self.subTest(fixture=rel):
                path = FIXTURE_ROOT / rel
                result = _run_with_fixture_root([path])
                self.assertEqual(
                    result.returncode,
                    0,
                    f"Expected exit 0 for {rel}:\n{result.stdout}{result.stderr}",
                )
                self.assertEqual(result.stdout.strip(), "")

    def test_valid_fixtures_all_together_exit_zero(self) -> None:
        paths = [FIXTURE_ROOT / rel for rel in VALID_FIXTURES]
        result = _run_with_fixture_root(paths)
        self.assertEqual(
            result.returncode,
            0,
            f"Expected exit 0 for all valid fixtures:\n{result.stdout}{result.stderr}",
        )

    def test_changed_files_mode_no_forbidden_paths_exit_zero(self) -> None:
        safe = FIXTURE_ROOT / "valid" / "test-output.txt"
        result = _run_with_fixture_root([safe])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class InvalidFixtureTests(unittest.TestCase):
    def test_invalid_fixtures_exit_one_with_rule_id(self) -> None:
        for rel, expected_rule in INVALID_FIXTURES.items():
            with self.subTest(fixture=rel):
                path = FIXTURE_ROOT / rel
                result = _run_with_fixture_root([path])
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
        with tempfile.TemporaryDirectory() as tmp:
            big_path = Path(tmp) / "oversized.bin"
            big_path.write_bytes(b"x" * (300 * 1024))
            result = _run_with_roots([big_path], [Path(tmp)])
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("ARTIFACT_TOO_LARGE", result.stdout)

    def test_oversized_allowed_name_still_blocked(self) -> None:
        # A file named exactly "test-output.txt" must not bypass the size limit.
        with tempfile.TemporaryDirectory() as tmp:
            big_path = Path(tmp) / "test-output.txt"
            big_path.write_bytes(b"y" * (300 * 1024))
            result = _run_with_roots([big_path], [Path(tmp)])
            self.assertEqual(
                result.returncode,
                1,
                f"Oversized test-output.txt must be blocked:\n{result.stdout}{result.stderr}",
            )
            self.assertIn("ARTIFACT_TOO_LARGE", result.stdout)


class PolicyValidationTest(unittest.TestCase):
    def _run_with_policy_text(self, policy_text: str) -> subprocess.CompletedProcess[str]:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            f.write(policy_text)
            policy_path = Path(f.name)
        try:
            return _run(["--policy", str(policy_path)])
        finally:
            policy_path.unlink(missing_ok=True)

    def test_broken_yaml_exits_two(self) -> None:
        result = self._run_with_policy_text(": invalid: [yaml: {broken\n")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("POLICY_PARSE_ERROR", result.stderr)

    def test_missing_policy_exits_two(self) -> None:
        result = _run(["--policy", "/nonexistent/path/policy.yml"])
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("POLICY_PARSE_ERROR", result.stderr)

    def test_invalid_max_bytes_exits_two(self) -> None:
        policy = {
            "schema_version": "1.0.0",
            "scope": {"artifact_roots": ["experiments"]},
            "limits": {"max_repo_local_evidence_bytes": "nope"},
            "forbidden_path_patterns": [],
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            yaml.dump(policy, f)
            policy_path = Path(f.name)
        try:
            result = _run(["--policy", str(policy_path)])
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("POLICY_PARSE_ERROR", result.stderr)
        finally:
            policy_path.unlink(missing_ok=True)

    def test_forbidden_patterns_not_list_exits_two(self) -> None:
        policy = {
            "schema_version": "1.0.0",
            "scope": {"artifact_roots": ["experiments"]},
            "limits": {"max_repo_local_evidence_bytes": 262144},
            "forbidden_path_patterns": "not-a-list",
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            yaml.dump(policy, f)
            policy_path = Path(f.name)
        try:
            result = _run(["--policy", str(policy_path)])
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("POLICY_PARSE_ERROR", result.stderr)
        finally:
            policy_path.unlink(missing_ok=True)

    def test_artifact_roots_not_list_exits_two(self) -> None:
        policy = {
            "schema_version": "1.0.0",
            "scope": {"artifact_roots": "experiments"},
            "limits": {"max_repo_local_evidence_bytes": 262144},
            "forbidden_path_patterns": [],
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            yaml.dump(policy, f)
            policy_path = Path(f.name)
        try:
            result = _run(["--policy", str(policy_path)])
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("POLICY_PARSE_ERROR", result.stderr)
        finally:
            policy_path.unlink(missing_ok=True)


class ScopeFilterTest(unittest.TestCase):
    def test_changed_files_outside_artifact_roots_ignored(self) -> None:
        # A .patch file in a temp dir that is NOT under experiments/ or artifacts/
        # must be ignored when using the default policy (artifact_roots: experiments, artifacts).
        with tempfile.TemporaryDirectory() as tmp:
            patch_file = Path(tmp) / "full-pr-diff.patch"
            patch_file.write_bytes(b"diff --git a/x b/x\n")
            with _cf_context([patch_file]) as cf_args:
                result = _run(cf_args)
            self.assertEqual(
                result.returncode,
                0,
                f"File outside artifact_roots must be ignored:\n{result.stdout}{result.stderr}",
            )


class SelfObservationRelativePathTest(unittest.TestCase):
    def _self_obs_pack(self, evidence_path: str) -> dict:
        return {
            "schema_version": "1.0.0",
            "run_id": "test-rel-self-obs",
            "claims": [{
                "claim_id": "rel-self-obs",
                "text": "Self-referencing with relative path",
                "type": "process_result",
                "verdict": "PASS",
                "evidence": [{"path": evidence_path, "status": "repo_local"}],
            }],
        }

    def test_self_obs_bare_filename_blocked(self) -> None:
        # evidence path is just "evidence-pack.yml" — same directory as the pack
        with tempfile.TemporaryDirectory() as tmp:
            pack_path = Path(tmp) / "evidence-pack.yml"
            pack_path.write_text(yaml.dump(self._self_obs_pack("evidence-pack.yml")))
            result = _run_with_roots([pack_path], [Path(tmp)])
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("EVIDENCE_SELF_OBSERVATION", result.stdout)

    def test_self_obs_dotslash_filename_blocked(self) -> None:
        # evidence path is "./evidence-pack.yml"
        with tempfile.TemporaryDirectory() as tmp:
            pack_path = Path(tmp) / "evidence-pack.yml"
            pack_path.write_text(yaml.dump(self._self_obs_pack("./evidence-pack.yml")))
            result = _run_with_roots([pack_path], [Path(tmp)])
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("EVIDENCE_SELF_OBSERVATION", result.stdout)


class RepoScanTest(unittest.TestCase):
    def test_repo_scan_default_exits_zero(self) -> None:
        result = _run([])
        self.assertEqual(
            result.returncode,
            0,
            f"Repo scan produced unexpected violations:\n{result.stdout}{result.stderr}",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
