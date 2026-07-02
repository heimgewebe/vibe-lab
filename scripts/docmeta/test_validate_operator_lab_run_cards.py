#!/usr/bin/env python3
"""Regression tests for validate_operator_lab_run_cards.py."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from validate_operator_lab_run_cards import validate_operator_lab_run_cards  # noqa: E402


class OperatorLabRunCardValidationTests(unittest.TestCase):
    def _root(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        (root / "raw-vibes").mkdir(parents=True)
        (root / "experiments/2026-07-01_operator-lab-loop/artifacts").mkdir(parents=True)
        return tmp, root

    def _raw_note(self, root: Path) -> None:
        (root / "raw-vibes/operator-lab-run-20260701-example.md").write_text(
            "# raw operator lab note\n", encoding="utf-8"
        )

    def _run_card(self, root: Path, *, source_path: str = "raw-vibes/operator-lab-run-20260701-example.md", with_meta: bool = True) -> None:
        run_dir = root / "experiments/2026-07-01_operator-lab-loop/artifacts/run-001-example"
        run_dir.mkdir(parents=True)
        (run_dir / "run-card.yml").write_text(
            f"schema_version: '0.1.0'\nsource_note:\n  path: {source_path!r}\n",
            encoding="utf-8",
        )
        if with_meta:
            (run_dir / "run_meta.json").write_text(
                '{"schema_version":"1.0.0","run_id":"run-001-example"}\n',
                encoding="utf-8",
            )

    def test_real_repository_is_valid(self) -> None:
        errors = validate_operator_lab_run_cards()
        self.assertEqual(errors, [])

    def test_raw_note_without_structured_run_card_fails(self) -> None:
        tmp, root = self._root()
        self.addCleanup(tmp.cleanup)
        self._raw_note(root)
        errors = validate_operator_lab_run_cards(root)
        self.assertEqual(len(errors), 1)
        self.assertIn("has no structured Operator-Lab run-card", errors[0])

    def test_source_note_reference_satisfies_raw_note(self) -> None:
        tmp, root = self._root()
        self.addCleanup(tmp.cleanup)
        self._raw_note(root)
        self._run_card(root)
        self.assertEqual(validate_operator_lab_run_cards(root), [])

    def test_source_note_missing_file_fails(self) -> None:
        tmp, root = self._root()
        self.addCleanup(tmp.cleanup)
        self._run_card(root, source_path="raw-vibes/operator-lab-run-20260701-missing.md")
        errors = validate_operator_lab_run_cards(root)
        self.assertEqual(len(errors), 1)
        self.assertIn("references missing source_note.path", errors[0])

    def test_run_card_referencing_raw_note_requires_run_meta(self) -> None:
        tmp, root = self._root()
        self.addCleanup(tmp.cleanup)
        self._raw_note(root)
        self._run_card(root, with_meta=False)
        errors = validate_operator_lab_run_cards(root)
        self.assertEqual(len(errors), 1)
        self.assertIn("sibling run_meta.json is missing", errors[0])

    def _operator_manifest(self, root: Path, refs: list[str]) -> None:
        manifest = root / "experiments/2026-07-01_operator-lab-loop/manifest.yml"
        manifest.parent.mkdir(parents=True, exist_ok=True)
        lines = ["schema_version: '0.1.0'", "experiment:", "  execution_refs:"]
        lines.extend(f"    - {ref}" for ref in refs)
        manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _numbered_run_card(self, root: Path, run_dir_name: str) -> None:
        run_dir = root / "experiments/2026-07-01_operator-lab-loop/artifacts" / run_dir_name
        run_dir.mkdir(parents=True)
        (run_dir / "run-card.yml").write_text(
            f"schema_version: '0.1.0'\nrun_id: {run_dir_name!r}\n",
            encoding="utf-8",
        )

    def test_recent_run_card_requires_manifest_registration(self) -> None:
        tmp, root = self._root()
        self.addCleanup(tmp.cleanup)
        self._numbered_run_card(root, "run-015-missing-manifest")
        self._operator_manifest(root, [])
        errors = validate_operator_lab_run_cards(root)
        self.assertEqual(len(errors), 1)
        self.assertIn("is not registered", errors[0])

    def test_recent_run_slot_collision_fails(self) -> None:
        tmp, root = self._root()
        self.addCleanup(tmp.cleanup)
        self._numbered_run_card(root, "run-015-alpha")
        self._numbered_run_card(root, "run-015-beta")
        self._operator_manifest(root, [
            "artifacts/run-015-alpha/run-card.yml",
            "artifacts/run-015-beta/run-card.yml",
        ])
        errors = validate_operator_lab_run_cards(root)
        self.assertEqual(len(errors), 1)
        self.assertIn("run-015", errors[0])
        self.assertIn("multiple run-cards", errors[0])

    def test_legacy_run_slot_collision_is_tolerated(self) -> None:
        tmp, root = self._root()
        self.addCleanup(tmp.cleanup)
        self._numbered_run_card(root, "run-014-alpha")
        self._numbered_run_card(root, "run-014-beta")
        self.assertEqual(validate_operator_lab_run_cards(root), [])


if __name__ == "__main__":
    unittest.main()
