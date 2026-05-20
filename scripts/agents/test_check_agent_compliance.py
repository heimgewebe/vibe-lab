#!/usr/bin/env python3
"""Regression tests for ``check_agent_compliance.py``.

Covers:
- canonical paths fail by default and pass with ``--allow-canonical``
- generated paths (file + directory pattern) fail and pass with override
- non-protected paths always pass
- protected-path patterns are read from ``.vibe/generated-artifacts.yml``
  and from ``agent-policy.yaml`` (combined, deduplicated)
- explicit ``--paths`` overrides git-diff discovery
- the violation report references the rule and the canonical source
"""

from __future__ import annotations

import importlib.util
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path


def _load_module():
    script_path = Path(__file__).resolve().parent / "check_agent_compliance.py"
    spec = importlib.util.spec_from_file_location(
        "check_agent_compliance", script_path
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load check_agent_compliance.py")
    module = importlib.util.module_from_spec(spec)
    # dataclass() resolves cls.__module__ via sys.modules, so register first.
    sys.modules["check_agent_compliance"] = module
    spec.loader.exec_module(module)
    return module


class CheckCanonicalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = _load_module()

    def test_repo_meta_yaml_is_canonical(self) -> None:
        violations = self.mod.check_canonical(
            ["repo.meta.yaml"], allowed=False
        )
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].rule, "canonical-source")
        self.assertIn("AGENTS.md", violations[0].reference)

    def test_agents_md_is_canonical(self) -> None:
        violations = self.mod.check_canonical(["AGENTS.md"], allowed=False)
        self.assertEqual(len(violations), 1)

    def test_agent_policy_yaml_is_canonical(self) -> None:
        violations = self.mod.check_canonical(
            ["agent-policy.yaml"], allowed=False
        )
        self.assertEqual(len(violations), 1)

    def test_pr_scope_policy_is_canonical(self) -> None:
        violations = self.mod.check_canonical(
            [".vibe/pr-scope-policy.yml"], allowed=False
        )
        self.assertEqual(len(violations), 1)

    def test_other_vibe_files_are_not_canonical(self) -> None:
        # constraints.yml and quality-gates.yml are operative, not canonical.
        violations = self.mod.check_canonical(
            [".vibe/constraints.yml", ".vibe/quality-gates.yml"],
            allowed=False,
        )
        self.assertEqual(violations, [])

    def test_allowed_flag_disables_check(self) -> None:
        violations = self.mod.check_canonical(
            ["repo.meta.yaml", "AGENTS.md"], allowed=True
        )
        self.assertEqual(violations, [])

    def test_non_protected_path_is_silent(self) -> None:
        violations = self.mod.check_canonical(
            ["README.md", "scripts/agents/check_agent_compliance.py"],
            allowed=False,
        )
        self.assertEqual(violations, [])


class CheckGeneratedTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = _load_module()
        # Realistic patterns from the v2 contract and agent-policy.yaml.
        self.patterns = [
            "docs/_generated/doc-index.md",
            "docs/_generated/",
            "exports/",
            "exports/copilot/",
            ".cursor/rules/",
        ]

    def test_exact_file_match_is_blocked(self) -> None:
        violations = self.mod.check_generated(
            ["docs/_generated/doc-index.md"],
            self.patterns,
            allowed=False,
        )
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].rule, "generated-artifact")

    def test_directory_pattern_blocks_nested_files(self) -> None:
        violations = self.mod.check_generated(
            ["exports/copilot/foo.md", "exports/cursor/bar.md"],
            self.patterns,
            allowed=False,
        )
        self.assertEqual(len(violations), 2)

    def test_cursor_rules_dir_is_blocked(self) -> None:
        violations = self.mod.check_generated(
            [".cursor/rules/abc.mdc"], self.patterns, allowed=False
        )
        self.assertEqual(len(violations), 1)

    def test_non_protected_path_is_silent(self) -> None:
        violations = self.mod.check_generated(
            ["docs/policies/foo.md", "scripts/agents/x.py"],
            self.patterns,
            allowed=False,
        )
        self.assertEqual(violations, [])

    def test_allowed_flag_disables_check(self) -> None:
        violations = self.mod.check_generated(
            ["docs/_generated/doc-index.md"],
            self.patterns,
            allowed=True,
        )
        self.assertEqual(violations, [])


class LoadGeneratedPathsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = _load_module()
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_reads_from_contract_v2(self) -> None:
        (self.repo / ".vibe").mkdir()
        (self.repo / ".vibe" / "generated-artifacts.yml").write_text(
            'schema_version: "2.0.0"\n'
            "artifacts:\n"
            "  - path: docs/_generated/doc-index.md\n"
            "  - path: exports/copilot/\n",
            encoding="utf-8",
        )
        paths = self.mod.load_generated_paths(self.repo)
        self.assertIn("docs/_generated/doc-index.md", paths)
        self.assertIn("exports/copilot/", paths)

    def test_combines_contract_and_agent_policy(self) -> None:
        (self.repo / ".vibe").mkdir()
        (self.repo / ".vibe" / "generated-artifacts.yml").write_text(
            'schema_version: "2.0.0"\n'
            "artifacts:\n"
            "  - path: docs/_generated/doc-index.md\n",
            encoding="utf-8",
        )
        (self.repo / "agent-policy.yaml").write_text(
            "generated_artifacts:\n"
            "  paths:\n"
            "    - 'exports/*'\n"
            "    - '.cursor/rules/*'\n",
            encoding="utf-8",
        )
        paths = self.mod.load_generated_paths(self.repo)
        self.assertIn("docs/_generated/doc-index.md", paths)
        self.assertIn("exports/", paths)
        self.assertIn(".cursor/rules/", paths)

    def test_fallback_used_when_no_sources(self) -> None:
        paths = self.mod.load_generated_paths(self.repo)
        # Fallback must cover all three core generated prefixes.
        self.assertIn("docs/_generated/", paths)
        self.assertIn("exports/", paths)
        self.assertIn(".cursor/rules/", paths)

    def test_paths_are_deduplicated(self) -> None:
        (self.repo / ".vibe").mkdir()
        (self.repo / ".vibe" / "generated-artifacts.yml").write_text(
            'schema_version: "2.0.0"\n'
            "artifacts:\n"
            "  - path: exports/copilot/\n",
            encoding="utf-8",
        )
        (self.repo / "agent-policy.yaml").write_text(
            "generated_artifacts:\n"
            "  paths:\n"
            "    - 'exports/*'\n",
            encoding="utf-8",
        )
        paths = self.mod.load_generated_paths(self.repo)
        self.assertEqual(paths.count("exports/"), 1)
        self.assertEqual(paths.count("exports/copilot/"), 1)


class RunChecksTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = _load_module()
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        (self.repo / ".vibe").mkdir()
        (self.repo / ".vibe" / "generated-artifacts.yml").write_text(
            'schema_version: "2.0.0"\n'
            "artifacts:\n"
            "  - path: docs/_generated/doc-index.md\n"
            "  - path: exports/copilot/\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_no_violations_for_clean_paths(self) -> None:
        violations = self.mod.run_checks(
            repo_root=self.repo,
            paths=["README.md", "docs/policies/agent-compliance.md"],
            allow_canonical=False,
            allow_generated=False,
        )
        self.assertEqual(violations, [])

    def test_canonical_and_generated_combine(self) -> None:
        violations = self.mod.run_checks(
            repo_root=self.repo,
            paths=["repo.meta.yaml", "docs/_generated/doc-index.md"],
            allow_canonical=False,
            allow_generated=False,
        )
        rules = sorted(v.rule for v in violations)
        self.assertEqual(rules, ["canonical-source", "generated-artifact"])


class MainCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = _load_module()

    def _run(self, argv: list[str]) -> tuple[int, str, str]:
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = self.mod.main(argv)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_paths_flag_clean_run_returns_zero(self) -> None:
        code, out, err = self._run(["--paths", "README.md"])
        self.assertEqual(code, 0)
        self.assertIn("OK", out)
        self.assertEqual(err, "")

    def test_paths_flag_canonical_violation_returns_one(self) -> None:
        code, out, err = self._run(["--paths", "AGENTS.md"])
        self.assertEqual(code, 1)
        self.assertIn("FAILED", err)
        self.assertIn("canonical-source", err)

    def test_paths_flag_generated_violation_returns_one(self) -> None:
        code, out, err = self._run(["--paths", "docs/_generated/doc-index.md"])
        self.assertEqual(code, 1)
        self.assertIn("generated-artifact", err)

    def test_allow_canonical_passes(self) -> None:
        code, _out, _err = self._run(
            ["--paths", "AGENTS.md", "--allow-canonical"]
        )
        self.assertEqual(code, 0)

    def test_allow_generated_passes(self) -> None:
        code, _out, _err = self._run(
            [
                "--paths",
                "docs/_generated/doc-index.md",
                "--allow-generated",
            ]
        )
        self.assertEqual(code, 0)

    def test_quiet_suppresses_success_message(self) -> None:
        code, out, _err = self._run(["--paths", "README.md", "--quiet"])
        self.assertEqual(code, 0)
        self.assertEqual(out, "")

    def test_violations_reference_canonical_sources(self) -> None:
        # The error message must point the agent at the binding source so
        # an LLM that reads only the failure can find the canonical rule.
        _code, _out, err = self._run(["--paths", "AGENTS.md"])
        self.assertIn("AGENTS.md", err)
        self.assertIn("constraints.yml", err)


if __name__ == "__main__":
    unittest.main(verbosity=2)
