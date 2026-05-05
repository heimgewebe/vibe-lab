#!/usr/bin/env python3
"""Regression tests for ``generate_backlinks.py``.

Covers:
- plain relation target produces a backlink under the target file
- fragment-suffixed target (``file.md#section``) produces a backlink under
  ``file.md``, not under the non-existent ``file.md#section`` path
- pure fragment targets (``#issue``) are skipped and produce no backlink
- path-escape targets are silently skipped (no crash, no entry)
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


def _load_module():
    script_path = Path(__file__).resolve().parent / "generate_backlinks.py"
    spec = importlib.util.spec_from_file_location("generate_backlinks", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load generate_backlinks.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write(repo_root: Path, rel: str, body: str) -> Path:
    p = repo_root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8")
    return p


class GenerateBacklinksTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = _load_module()
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        (self.repo / "docs").mkdir()

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_plain_target_produces_backlink(self) -> None:
        """A plain ``target: target.md`` produces a backlink under ``docs/target.md``."""
        _write(self.repo, "docs/target.md", "---\ntitle: Target\n---\n")
        _write(
            self.repo,
            "docs/source.md",
            "---\ntitle: Source\nrelations:\n"
            "  - type: references\n    target: target.md\n---\n",
        )
        bl = self.mod.collect_backlinks(self.repo)
        self.assertIn("docs/target.md", bl)
        sources = [s for s, _ in bl["docs/target.md"]]
        self.assertIn("docs/source.md", sources)

    def test_fragment_target_backlink_recorded_under_file_not_fragment(self) -> None:
        """``target.md#section`` must produce a backlink under ``target.md``,
        not under the non-existent key ``target.md#section``."""
        _write(self.repo, "docs/target.md", "---\ntitle: Target\n---\n")
        _write(
            self.repo,
            "docs/source.md",
            "---\ntitle: Source\nrelations:\n"
            "  - type: references\n    target: target.md#section\n---\n",
        )
        bl = self.mod.collect_backlinks(self.repo)
        # Must be recorded under the file, not the fragment path
        self.assertIn("docs/target.md", bl)
        self.assertNotIn("docs/target.md#section", bl)
        sources = [s for s, _ in bl["docs/target.md"]]
        self.assertIn("docs/source.md", sources)

    def test_pure_fragment_target_is_skipped(self) -> None:
        """``#issue`` targets must not produce any backlink entry."""
        _write(
            self.repo,
            "docs/source.md",
            "---\ntitle: Source\nrelations:\n"
            "  - type: references\n    target: '#42'\n---\n",
        )
        bl = self.mod.collect_backlinks(self.repo)
        self.assertEqual(dict(bl), {})

    def test_path_escape_target_is_skipped(self) -> None:
        """Targets that escape the repo root must be silently dropped."""
        _write(
            self.repo,
            "docs/source.md",
            "---\ntitle: Source\nrelations:\n"
            "  - type: references\n    target: ../../../etc/passwd\n---\n",
        )
        bl = self.mod.collect_backlinks(self.repo)
        self.assertEqual(dict(bl), {})


if __name__ == "__main__":
    unittest.main(verbosity=2)
