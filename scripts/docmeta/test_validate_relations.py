#!/usr/bin/env python3
"""Regression tests for ``validate_relations.py``.

Covers:
- valid relations resolve to existing files
- broken relations get reported
- path-escape relations get reported
- non-list ``relations`` field is rejected
- non-mapping relation entries are rejected
- ``#issue`` references are skipped
- missing type/target is rejected
- module call leaves no global state behind (re-run isolation)
"""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


def _load_module():
    script_path = Path(__file__).resolve().parent / "validate_relations.py"
    spec = importlib.util.spec_from_file_location("validate_relations", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load validate_relations.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write(repo_root: Path, rel: str, body: str) -> Path:
    p = repo_root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8")
    return p


class ValidateRelationsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = _load_module()
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        # docs/ subdir keeps the layout faithful to real usage.
        (self.repo / "docs").mkdir()

    def tearDown(self) -> None:
        self._tmp.cleanup()

    # --- happy path -----------------------------------------------------

    def test_valid_relation_to_existing_file(self) -> None:
        _write(
            self.repo,
            "docs/target.md",
            "---\ntitle: Target\nstatus: active\n---\n# t\n",
        )
        _write(
            self.repo,
            "docs/source.md",
            "---\ntitle: Source\nstatus: active\nrelations:\n"
            "  - type: references\n    target: target.md\n---\n",
        )
        errors = self.mod.collect_errors(self.repo, quiet=True)
        self.assertEqual(errors, [])

    def test_issue_reference_is_skipped(self) -> None:
        _write(
            self.repo,
            "docs/source.md",
            "---\ntitle: Source\nstatus: active\nrelations:\n"
            "  - type: references\n    target: '#42'\n---\n",
        )
        errors = self.mod.collect_errors(self.repo, quiet=True)
        self.assertEqual(errors, [])

    # --- failure modes --------------------------------------------------

    def test_missing_target_is_reported(self) -> None:
        _write(
            self.repo,
            "docs/source.md",
            "---\ntitle: Source\nstatus: active\nrelations:\n"
            "  - type: references\n    target: not-here.md\n---\n",
        )
        errors = self.mod.collect_errors(self.repo, quiet=True)
        self.assertEqual(len(errors), 1)
        self.assertIn("does not exist", errors[0])

    def test_path_escape_is_reported(self) -> None:
        _write(
            self.repo,
            "docs/source.md",
            "---\ntitle: Source\nstatus: active\nrelations:\n"
            "  - type: references\n    target: ../../../etc/passwd\n---\n",
        )
        errors = self.mod.collect_errors(self.repo, quiet=True)
        self.assertEqual(len(errors), 1)
        self.assertIn("escapes repository root", errors[0])

    def test_non_list_relations_is_reported(self) -> None:
        _write(
            self.repo,
            "docs/source.md",
            "---\ntitle: Source\nstatus: active\nrelations: \"not-a-list\"\n---\n",
        )
        errors = self.mod.collect_errors(self.repo, quiet=True)
        self.assertEqual(len(errors), 1)
        self.assertIn("'relations' must be a list", errors[0])

    def test_non_mapping_relation_entry_is_reported(self) -> None:
        _write(
            self.repo,
            "docs/source.md",
            "---\ntitle: Source\nstatus: active\nrelations:\n  - just-a-string\n---\n",
        )
        errors = self.mod.collect_errors(self.repo, quiet=True)
        self.assertEqual(len(errors), 1)
        self.assertIn("relation entry must be an object", errors[0])

    def test_missing_type_or_target_is_reported(self) -> None:
        _write(
            self.repo,
            "docs/source.md",
            "---\ntitle: Source\nstatus: active\nrelations:\n  - type: references\n---\n",
        )
        errors = self.mod.collect_errors(self.repo, quiet=True)
        self.assertEqual(len(errors), 1)
        self.assertIn("missing 'type' or 'target'", errors[0])

    # --- isolation ------------------------------------------------------

    def test_repeated_calls_do_not_accumulate_errors(self) -> None:
        """Guards against the previous global ``errors = []`` bug."""
        _write(
            self.repo,
            "docs/source.md",
            "---\ntitle: Source\nstatus: active\nrelations:\n"
            "  - type: references\n    target: not-here.md\n---\n",
        )
        first = self.mod.collect_errors(self.repo, quiet=True)
        second = self.mod.collect_errors(self.repo, quiet=True)
        self.assertEqual(first, second)
        self.assertEqual(len(first), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
