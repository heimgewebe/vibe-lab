#!/usr/bin/env python3
"""test_generate_exports.py — Regression tests for the export generator.

Tests:
- Deterministic generation (same input → same output)
- Complete capture of all instruction-blocks/*.md
- Stable path/filename logic
- Sensible reaction to empty input or missing target directory
- Export header correctness
"""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

# Ensure import path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_exports import (  # noqa: E402
    EXPORT_TARGETS,
    GENERATOR_ID,
    REPO_ROOT,
    SOURCE_DIR,
    _build_export,
    _build_header,
    _strip_frontmatter,
    generate_exports,
)


class TestStripFrontmatter(unittest.TestCase):
    def test_with_frontmatter(self):
        text = "---\ntitle: Test\n---\nBody content"
        self.assertEqual(_strip_frontmatter(text), "Body content")

    def test_without_frontmatter(self):
        text = "No frontmatter here"
        self.assertEqual(_strip_frontmatter(text), "No frontmatter here")

    def test_incomplete_frontmatter(self):
        text = "---\ntitle: Test\nno closing"
        self.assertEqual(_strip_frontmatter(text), text)


class TestBuildHeader(unittest.TestCase):
    def test_header_contains_required_fields(self):
        header = _build_header("instruction-blocks/test.md", "copilot", "2026-04-20")
        self.assertIn("GENERATED FILE", header)
        self.assertIn("DO NOT EDIT MANUALLY", header)
        self.assertIn("instruction-blocks/test.md", header)
        self.assertIn("copilot", header)
        self.assertIn(GENERATOR_ID, header)
        self.assertIn("2026-04-20", header)

    def test_header_is_html_comment(self):
        header = _build_header("src.md", "cursor", "2026-01-01")
        for line in header.strip().splitlines():
            self.assertTrue(line.startswith("<!--"), f"Not a comment: {line}")
            self.assertTrue(line.endswith("-->"), f"Not a comment: {line}")


class TestDeterministicGeneration(unittest.TestCase):
    """Verifies that running the generator twice produces identical output."""

    def test_idempotent_output(self):
        fixed_date = "2026-04-20"
        result1 = generate_exports(generated_date=fixed_date)
        # Capture file contents
        contents1 = {}
        for target_system, target_dir in EXPORT_TARGETS.items():
            for f in sorted(target_dir.iterdir()):
                contents1[f"{target_system}/{f.name}"] = f.read_text(encoding="utf-8")

        result2 = generate_exports(generated_date=fixed_date)
        contents2 = {}
        for target_system, target_dir in EXPORT_TARGETS.items():
            for f in sorted(target_dir.iterdir()):
                contents2[f"{target_system}/{f.name}"] = f.read_text(encoding="utf-8")

        self.assertEqual(result1, result2)
        self.assertEqual(contents1, contents2)


class TestCompleteCapture(unittest.TestCase):
    """Verifies all instruction-blocks/*.md are exported to both targets."""

    def test_all_sources_exported(self):
        source_files = sorted(SOURCE_DIR.glob("*.md"))
        self.assertGreater(len(source_files), 0, "No source files found")

        generate_exports(generated_date="2026-04-20")

        for target_system, target_dir in EXPORT_TARGETS.items():
            exported = {f.name for f in target_dir.iterdir()}
            expected = {f.name for f in source_files}
            self.assertEqual(
                exported,
                expected,
                f"Mismatch in {target_system}: {exported.symmetric_difference(expected)}",
            )


class TestStablePathLogic(unittest.TestCase):
    """Verifies filename mapping is stable and predictable."""

    def test_filenames_match_source(self):
        generate_exports(generated_date="2026-04-20")
        source_names = {f.name for f in SOURCE_DIR.glob("*.md")}

        for target_system, target_dir in EXPORT_TARGETS.items():
            export_names = {f.name for f in target_dir.iterdir()}
            self.assertEqual(source_names, export_names)


class TestExportContent(unittest.TestCase):
    """Verifies export content structure."""

    def test_exports_contain_header_and_body(self):
        generate_exports(generated_date="2026-04-20")

        for target_system, target_dir in EXPORT_TARGETS.items():
            for export_file in target_dir.iterdir():
                content = export_file.read_text(encoding="utf-8")
                self.assertIn("GENERATED FILE", content)
                self.assertIn(f"target-system: {target_system}", content)
                self.assertIn("source: instruction-blocks/", content)
                # Body should be present (non-empty after header)
                lines = content.strip().splitlines()
                self.assertGreater(len(lines), 6, f"Export too short: {export_file}")

    def test_no_frontmatter_in_exports(self):
        generate_exports(generated_date="2026-04-20")

        for _, target_dir in EXPORT_TARGETS.items():
            for export_file in target_dir.iterdir():
                content = export_file.read_text(encoding="utf-8")
                # Exports should NOT start with YAML frontmatter
                self.assertFalse(
                    content.startswith("---"),
                    f"Export should not have frontmatter: {export_file}",
                )


class TestEdgeCases(unittest.TestCase):
    """Edge case handling: empty input, missing directories."""

    def test_empty_source_directory(self):
        """Generator should handle empty source dir gracefully."""
        import generate_exports as mod

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            empty_src = tmp_path / "instruction-blocks"
            empty_src.mkdir()

            # Temporarily replace SOURCE_DIR
            original_src = mod.SOURCE_DIR
            original_targets = mod.EXPORT_TARGETS
            mod.SOURCE_DIR = empty_src
            mod.EXPORT_TARGETS = {
                "copilot": tmp_path / "exports" / "copilot",
                "cursor": tmp_path / "exports" / "cursor",
            }

            try:
                stats = mod.generate_exports(generated_date="2026-04-20")
                for target, count in stats.items():
                    self.assertEqual(count, 0, f"Expected 0 exports for {target}")
                # Target dirs should exist but be empty
                for target_dir in mod.EXPORT_TARGETS.values():
                    self.assertTrue(target_dir.exists())
                    self.assertEqual(
                        list(target_dir.iterdir()),
                        [],
                        f"Expected empty dir: {target_dir}",
                    )
            finally:
                mod.SOURCE_DIR = original_src
                mod.EXPORT_TARGETS = original_targets

    def test_target_directory_created_if_missing(self):
        """Generator should create target dirs if they don't exist."""
        import generate_exports as mod

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Create a minimal source
            src_dir = tmp_path / "instruction-blocks"
            src_dir.mkdir()
            (src_dir / "test.md").write_text(
                "---\ntitle: Test\n---\nTest body\n", encoding="utf-8"
            )

            original_src = mod.SOURCE_DIR
            original_targets = mod.EXPORT_TARGETS
            original_root = mod.REPO_ROOT
            mod.SOURCE_DIR = src_dir
            mod.REPO_ROOT = tmp_path
            mod.EXPORT_TARGETS = {
                "copilot": tmp_path / "exports" / "copilot",
                "cursor": tmp_path / "exports" / "cursor",
            }

            try:
                # Target dirs don't exist yet
                for td in mod.EXPORT_TARGETS.values():
                    self.assertFalse(td.exists())

                stats = mod.generate_exports(generated_date="2026-04-20")

                for td in mod.EXPORT_TARGETS.values():
                    self.assertTrue(td.exists())
                    self.assertEqual(len(list(td.iterdir())), 1)
            finally:
                mod.SOURCE_DIR = original_src
                mod.EXPORT_TARGETS = original_targets
                mod.REPO_ROOT = original_root


if __name__ == "__main__":
    unittest.main()
