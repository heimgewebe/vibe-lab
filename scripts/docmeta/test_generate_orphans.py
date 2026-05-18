#!/usr/bin/env python3
"""Regression tests for ``generate_orphans.py``.

Covers:
- unreferenced file appears in orphan set
- plain relation target removes the target file from the orphan set
- fragment-suffixed target (``file.md#section``) counts as a reference to
  ``file.md``, so ``file.md`` is NOT reported as an orphan
- pure fragment targets (``#issue``) do not count as a file reference
- path-escape targets are silently skipped (no crash, no effect on orphan set)
- expected orphan matched by policy rule is classified as expected with reason
- unmatched orphan stays in unexpected
- policy entry with empty reason is rejected with ValueError
- policy entry with missing reason field is rejected with ValueError
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


def _load_module():
    script_path = Path(__file__).resolve().parent / "generate_orphans.py"
    spec = importlib.util.spec_from_file_location("generate_orphans", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load generate_orphans.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write(repo_root: Path, rel: str, body: str) -> Path:
    p = repo_root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8")
    return p


class GenerateOrphansTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = _load_module()
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        (self.repo / "docs").mkdir()

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_unreferenced_file_is_orphan(self) -> None:
        """A file with no incoming references is reported as an orphan."""
        _write(self.repo, "docs/alone.md", "---\ntitle: Alone\n---\n")
        orphans = self.mod.collect_unreferenced(self.repo)
        self.assertIn("docs/alone.md", orphans)

    def test_plain_target_removes_file_from_orphan_set(self) -> None:
        """A file that is a plain relation target must not appear in orphans."""
        _write(self.repo, "docs/target.md", "---\ntitle: Target\n---\n")
        _write(
            self.repo,
            "docs/source.md",
            "---\ntitle: Source\nrelations:\n"
            "  - type: references\n    target: target.md\n---\n",
        )
        orphans = self.mod.collect_unreferenced(self.repo)
        self.assertNotIn("docs/target.md", orphans)

    def test_fragment_target_counts_as_reference_to_file(self) -> None:
        """``target.md#section`` must count as a reference to ``target.md``
        so that ``target.md`` is NOT reported as an orphan."""
        _write(self.repo, "docs/target.md", "---\ntitle: Target\n---\n")
        _write(
            self.repo,
            "docs/source.md",
            "---\ntitle: Source\nrelations:\n"
            "  - type: references\n    target: target.md#section\n---\n",
        )
        orphans = self.mod.collect_unreferenced(self.repo)
        self.assertNotIn("docs/target.md", orphans)

    def test_pure_fragment_does_not_count_as_file_reference(self) -> None:
        """``#issue`` targets must not count as a reference to any file."""
        _write(self.repo, "docs/target.md", "---\ntitle: Target\n---\n")
        _write(
            self.repo,
            "docs/source.md",
            "---\ntitle: Source\nrelations:\n"
            "  - type: references\n    target: '#42'\n---\n",
        )
        # target.md has no real incoming references → still an orphan
        orphans = self.mod.collect_unreferenced(self.repo)
        self.assertIn("docs/target.md", orphans)

    def test_path_escape_target_does_not_affect_orphan_set(self) -> None:
        """Targets that escape the repo root must be silently dropped."""
        _write(self.repo, "docs/target.md", "---\ntitle: Target\n---\n")
        _write(
            self.repo,
            "docs/source.md",
            "---\ntitle: Source\nrelations:\n"
            "  - type: references\n    target: ../../../etc/passwd\n---\n",
        )
        # target.md still has no valid incoming reference → remains an orphan
        orphans = self.mod.collect_unreferenced(self.repo)
        self.assertIn("docs/target.md", orphans)


class OrphanPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = _load_module()
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        (self.repo / "docs").mkdir()

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _write_policy(self, content: str) -> None:
        policy_dir = self.repo / ".vibe"
        policy_dir.mkdir(exist_ok=True)
        (policy_dir / "orphan-policy.yml").write_text(content, encoding="utf-8")

    def test_expected_orphan_classified_with_reason(self) -> None:
        """An orphan matched by a policy rule appears in expected, not unexpected."""
        _write(self.repo, "experiments/run-001/CONTEXT.md", "---\ntitle: Context\n---\n")
        _write(self.repo, "docs/other.md", "---\ntitle: Other\n---\n")
        self._write_policy(
            "schema_version: '0.1.0'\n"
            "expected_orphans:\n"
            "  - pattern: 'experiments/*/CONTEXT.md'\n"
            "    reason: 'experiment_bundle_local_context'\n"
        )
        rules = self.mod.load_orphan_policy(self.repo)
        orphans = list(self.mod.collect_unreferenced(self.repo))
        unexpected, expected = self.mod.classify_orphans(orphans, rules)

        expected_paths = [p for p, _ in expected]
        self.assertIn("experiments/run-001/CONTEXT.md", expected_paths)
        self.assertNotIn("experiments/run-001/CONTEXT.md", unexpected)

        matched_reason = next(r for p, r in expected if p == "experiments/run-001/CONTEXT.md")
        self.assertEqual(matched_reason, "experiment_bundle_local_context")

    def test_unmatched_orphan_stays_unexpected(self) -> None:
        """An orphan that matches no policy rule remains in the unexpected list."""
        _write(self.repo, "docs/stray.md", "---\ntitle: Stray\n---\n")
        self._write_policy(
            "schema_version: '0.1.0'\n"
            "expected_orphans:\n"
            "  - pattern: 'experiments/*/CONTEXT.md'\n"
            "    reason: 'experiment_bundle_local_context'\n"
        )
        rules = self.mod.load_orphan_policy(self.repo)
        orphans = list(self.mod.collect_unreferenced(self.repo))
        unexpected, expected = self.mod.classify_orphans(orphans, rules)

        self.assertIn("docs/stray.md", unexpected)
        self.assertNotIn("docs/stray.md", [p for p, _ in expected])

    def test_empty_reason_raises_value_error(self) -> None:
        """A policy entry with an empty reason string must be rejected."""
        self._write_policy(
            "schema_version: '0.1.0'\n"
            "expected_orphans:\n"
            "  - pattern: 'experiments/*/CONTEXT.md'\n"
            "    reason: ''\n"
        )
        with self.assertRaises(ValueError):
            self.mod.load_orphan_policy(self.repo)

    def test_missing_reason_raises_value_error(self) -> None:
        """A policy entry without a reason field must be rejected."""
        self._write_policy(
            "schema_version: '0.1.0'\n"
            "expected_orphans:\n"
            "  - pattern: 'experiments/*/CONTEXT.md'\n"
        )
        with self.assertRaises(ValueError):
            self.mod.load_orphan_policy(self.repo)

    def test_missing_policy_file_returns_empty_rules(self) -> None:
        """When .vibe/orphan-policy.yml does not exist, rules list is empty."""
        rules = self.mod.load_orphan_policy(self.repo)
        self.assertEqual(rules, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
