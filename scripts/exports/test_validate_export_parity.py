#!/usr/bin/env python3
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_exports import generate_exports  # noqa: E402
from validate_export_parity import validate  # noqa: E402


class RetiredExportBoundaryTests(unittest.TestCase):
    def test_generated_tombstones_validate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "instruction-blocks"
            source.mkdir()
            (source / "rule.md").write_text("---\nstatus: adopted\n---\nbody\n", encoding="utf-8")
            targets = {"cursor": root / "exports/cursor"}
            generate_exports(source, targets)
            self.assertEqual(validate(source, targets), [])

    def test_active_instruction_copy_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "instruction-blocks"
            source.mkdir()
            (source / "rule.md").write_text("---\nstatus: adopted\n---\nbody\n", encoding="utf-8")
            target = root / "exports/cursor"
            target.mkdir(parents=True)
            (target / "rule.md").write_text("body\n", encoding="utf-8")
            errors = validate(source, {"cursor": target})
            self.assertTrue(any("active or drifted" in error for error in errors))

    def test_tombstone_version_drift_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "instruction-blocks"
            source.mkdir()
            (source / "rule.md").write_text("---\nstatus: adopted\n---\nbody\n", encoding="utf-8")
            target = root / "exports/cursor"
            generate_exports(source, {"cursor": target})
            marker = target / "rule.md"
            marker.write_text(
                marker.read_text(encoding="utf-8").replace(
                    "retirement-format: 1", "retirement-format: 0"
                ),
                encoding="utf-8",
            )
            errors = validate(source, {"cursor": target})
            self.assertTrue(any("active or drifted" in error for error in errors))

    def test_nested_and_non_markdown_files_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "instruction-blocks"
            source.mkdir()
            (source / "rule.md").write_text("---\nstatus: adopted\n---\nbody\n", encoding="utf-8")
            target = root / "exports/cursor"
            nested_markdown = target / "team/rule.md"
            nested_text = target / "team/rule.txt"
            nested_markdown.parent.mkdir(parents=True)
            nested_markdown.write_text("active nested instruction\n", encoding="utf-8")
            nested_text.write_text("active nested instruction\n", encoding="utf-8")
            errors = validate(source, {"cursor": target})
            self.assertTrue(any("team/rule.md" in error for error in errors))
            self.assertTrue(any("team/rule.txt" in error for error in errors))

    def test_missing_source_directory_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            errors = validate(root / "missing", {"cursor": root / "exports/cursor"})
            self.assertTrue(any("missing instruction source directory" in error for error in errors))

    def test_missing_and_unexpected_files_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "instruction-blocks"
            source.mkdir()
            (source / "expected.md").write_text("---\nstatus: adopted\n---\nbody\n", encoding="utf-8")
            target = root / "exports/cursor"
            target.mkdir(parents=True)
            (target / "orphan.md").write_text("retired\n", encoding="utf-8")
            errors = validate(source, {"cursor": target})
            self.assertTrue(any("missing retirement marker" in error for error in errors))
            self.assertTrue(any("unexpected file in retired surface" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
