#!/usr/bin/env python3
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_exports import generate_exports  # noqa: E402


class RetiredExportGeneratorTests(unittest.TestCase):
    def test_generator_publishes_versioned_tombstones_without_instruction_body(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "instruction-blocks"
            source.mkdir()
            (source / "rule.md").write_text(
                "---\nstatus: adopted\ntitle: Secret rule\n---\nDO THE ACTIVE THING\n",
                encoding="utf-8",
            )
            targets = {"copilot": root / "exports/copilot", "cursor": root / "exports/cursor"}
            stats = generate_exports(source, targets)
            self.assertEqual(stats, {"copilot": 1, "cursor": 1})
            for target in targets.values():
                text = (target / "rule.md").read_text(encoding="utf-8")
                self.assertIn("Tool projection retired", text)
                self.assertIn("retirement-format: 1", text)
                self.assertIn("retired-on: 2026-07-12", text)
                self.assertIn("decision: decisions/export/README.md", text)
                self.assertNotIn("DO THE ACTIVE THING", text)

    def test_generator_is_byte_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "instruction-blocks"
            source.mkdir()
            (source / "rule.md").write_text("---\nstatus: adopted\n---\nbody\n", encoding="utf-8")
            targets = {"cursor": root / "exports/cursor"}
            generate_exports(source, targets)
            first = (targets["cursor"] / "rule.md").read_bytes()
            generate_exports(source, targets)
            second = (targets["cursor"] / "rule.md").read_bytes()
            self.assertEqual(first, second)

    def test_status_transition_removes_retirement_marker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "instruction-blocks"
            source.mkdir()
            source_file = source / "rule.md"
            source_file.write_text("---\nstatus: adopted\n---\nbody\n", encoding="utf-8")
            target = root / "exports/cursor"
            generate_exports(source, {"cursor": target})
            marker = target / "rule.md"
            self.assertTrue(marker.exists())

            source_file.write_text("---\nstatus: retired\n---\nbody\n", encoding="utf-8")
            generate_exports(source, {"cursor": target})
            self.assertFalse(marker.exists())

    def test_generator_removes_nested_and_non_markdown_files(self) -> None:
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
            generate_exports(source, {"cursor": target})
            self.assertFalse(nested_markdown.exists())
            self.assertFalse(nested_text.exists())
            self.assertTrue((target / "rule.md").exists())


if __name__ == "__main__":
    unittest.main()
