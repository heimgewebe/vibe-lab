#!/usr/bin/env python3
"""Regression tests for ``generate_orphans.py``.

Covers:
- unreferenced file appears in orphan set
- plain relation target removes the target file from the orphan set
- fragment-suffixed target (``file.md#section``) counts as a reference to
  ``file.md``, so ``file.md`` is NOT reported as an orphan
- pure fragment targets (``#issue``) do not count as a file reference
- path-escape targets are silently skipped (no crash, no effect on orphan set)
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
