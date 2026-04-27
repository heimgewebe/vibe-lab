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
    compute_source_hash,
    detect_collisions,
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
        header = _build_header("instruction-blocks/test.md", "copilot", "abc123")
        self.assertIn("GENERATED FILE", header)
        self.assertIn("DO NOT EDIT MANUALLY", header)
        self.assertIn("instruction-blocks/test.md", header)
        self.assertIn("copilot", header)
        self.assertIn(GENERATOR_ID, header)
        self.assertIn("source-hash: abc123", header)

    def test_header_contains_no_date(self):
        """Header must not contain a calendar date — dates break determinism."""
        header = _build_header("instruction-blocks/test.md", "copilot", "abc123")
        self.assertNotIn("generated:", header)

    def test_header_is_html_comment(self):
        header = _build_header("src.md", "cursor", "def456")
        for line in header.strip().splitlines():
            self.assertTrue(line.startswith("<!--"), f"Not a comment: {line}")
            self.assertTrue(line.endswith("-->"), f"Not a comment: {line}")


class TestDetectCollisions(unittest.TestCase):
    """detect_collisions() must use expected_export_name(), not src.name."""

    def test_no_collision_flat_files(self):
        files = [Path(f"/repo/instruction-blocks/{n}.md") for n in ("a", "b", "c")]
        self.assertEqual(detect_collisions(files), [])

    def test_collision_uses_expected_export_name(self):
        """If expected_export_name() maps two paths to the same target, detect it."""
        from unittest.mock import patch
        files = [
            Path("/repo/instruction-blocks/a.md"),
            Path("/repo/instruction-blocks/b.md"),
        ]
        with patch("generate_exports.expected_export_name", lambda _p: "same.md"):
            collisions = detect_collisions(files)
        self.assertEqual(len(collisions), 1, "Expected one collision")
        name, srcs = collisions[0]
        self.assertEqual(name, "same.md")
        self.assertEqual(len(srcs), 2)

    def test_no_collision_empty_input(self):
        self.assertEqual(detect_collisions([]), [])


class TestDeterministicGeneration(unittest.TestCase):
    """Verifies that running the generator twice produces identical output."""

    def test_idempotent_output(self):
        """Default (no-arg) call must produce identical output on re-run."""
        result1 = generate_exports()
        contents1 = {}
        for target_system, target_dir in EXPORT_TARGETS.items():
            for f in sorted(target_dir.iterdir()):
                contents1[f"{target_system}/{f.name}"] = f.read_text(encoding="utf-8")

        result2 = generate_exports()
        contents2 = {}
        for target_system, target_dir in EXPORT_TARGETS.items():
            for f in sorted(target_dir.iterdir()):
                contents2[f"{target_system}/{f.name}"] = f.read_text(encoding="utf-8")

        self.assertEqual(result1, result2)
        self.assertEqual(contents1, contents2)

    def test_no_date_in_exported_files(self):
        """Generator-added header lines must not contain a calendar date.

        Only the HTML comment block (lines starting with <!--) is inspected.
        The body may legitimately contain dates (examples, specs, user content).
        """
        import re
        generate_exports()
        date_pattern = re.compile(r"\d{4}-\d{2}-\d{2}")
        for target_system, target_dir in EXPORT_TARGETS.items():
            for export_file in target_dir.iterdir():
                content = export_file.read_text(encoding="utf-8")
                header_lines = [
                    ln for ln in content.splitlines()
                    if ln.startswith("<!--") and ln.endswith("-->")
                ]
                for line in header_lines:
                    match = date_pattern.search(line)
                    if match is not None:
                        self.fail(
                            f"Calendar date in generator header of "
                            f"{target_system}/{export_file.name}: "
                            f"'{line}' — breaks determinism across days."
                        )


class TestCompleteCapture(unittest.TestCase):
    """Verifies all instruction-blocks/*.md are exported to both targets."""

    def test_all_sources_exported(self):
        source_files = sorted(SOURCE_DIR.glob("*.md"))
        self.assertGreater(len(source_files), 0, "No source files found")

        generate_exports()

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
        generate_exports()
        source_names = {f.name for f in SOURCE_DIR.glob("*.md")}

        for target_system, target_dir in EXPORT_TARGETS.items():
            export_names = {f.name for f in target_dir.iterdir()}
            self.assertEqual(source_names, export_names)


class TestExportContent(unittest.TestCase):
    """Verifies export content structure."""

    def test_exports_contain_header_and_body(self):
        generate_exports()

        for target_system, target_dir in EXPORT_TARGETS.items():
            for export_file in target_dir.iterdir():
                content = export_file.read_text(encoding="utf-8")
                self.assertIn("GENERATED FILE", content)
                self.assertIn(f"target-system: {target_system}", content)
                self.assertIn("source: instruction-blocks/", content)
                # Body should be present (non-empty after header)
                lines = content.strip().splitlines()
                self.assertGreater(len(lines), 6, f"Export too short: {export_file}")

    def test_exports_contain_source_hash(self):
        """Every export must contain a source-hash header line."""
        generate_exports()

        for target_system, target_dir in EXPORT_TARGETS.items():
            for export_file in target_dir.iterdir():
                content = export_file.read_text(encoding="utf-8")
                self.assertIn(
                    "source-hash:",
                    content,
                    f"Missing source-hash in {target_system}/{export_file.name}",
                )

    def test_no_frontmatter_in_exports(self):
        generate_exports()

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
                stats = mod.generate_exports()
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

    def test_stale_exports_removed_when_source_becomes_empty(self):
        """Stale exports must be deleted when all source files are removed.

        This guards the mirror-consistency invariant: if instruction-blocks/ is
        emptied, exports/ must become empty too — not silently keep old files.
        The fix is that generate_exports() is called even on an empty source set.
        """
        import generate_exports as mod

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            src_dir = tmp_path / "instruction-blocks"
            src_dir.mkdir()

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
                # First: generate with one source file
                (src_dir / "example.md").write_text(
                    "---\ntitle: Example\n---\nContent\n", encoding="utf-8"
                )
                mod.generate_exports()
                for td in mod.EXPORT_TARGETS.values():
                    self.assertEqual(len(list(td.iterdir())), 1, "Export should exist after generation")

                # Then: remove the source file and regenerate
                (src_dir / "example.md").unlink()
                mod.generate_exports()
                for td in mod.EXPORT_TARGETS.values():
                    self.assertEqual(
                        list(td.iterdir()),
                        [],
                        f"Stale export not removed from {td}",
                    )
            finally:
                mod.SOURCE_DIR = original_src
                mod.EXPORT_TARGETS = original_targets
                mod.REPO_ROOT = original_root

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

                stats = mod.generate_exports()

                for td in mod.EXPORT_TARGETS.values():
                    self.assertTrue(td.exists())
                    self.assertEqual(len(list(td.iterdir())), 1)
            finally:
                mod.SOURCE_DIR = original_src
                mod.EXPORT_TARGETS = original_targets
                mod.REPO_ROOT = original_root


class TestSourceHashDeterminism(unittest.TestCase):
    """Verifies source-hash is deterministic and content-bound."""

    def test_same_content_same_hash(self):
        """Identical content must produce identical hash."""
        h1 = compute_source_hash("Hello World")
        h2 = compute_source_hash("Hello World")
        self.assertEqual(h1, h2)

    def test_different_content_different_hash(self):
        """Different content must produce different hash."""
        h1 = compute_source_hash("Hello World")
        h2 = compute_source_hash("Hello World!")
        self.assertNotEqual(h1, h2)

    def test_hash_is_hex_sha256(self):
        """Hash must be a valid 64-char hex string (SHA-256)."""
        import re
        h = compute_source_hash("test")
        self.assertRegex(h, r"^[0-9a-f]{64}$")


class TestSourceHashConsistency(unittest.TestCase):
    """Verifies source-hash in exports matches the actual source content."""

    def _extract_source_hash(self, content: str) -> str | None:
        """Extracts source-hash value from export header."""
        import re
        m = re.search(r"<!-- source-hash: ([0-9a-f]+) -->", content)
        return m.group(1) if m else None

    def test_source_hash_matches_source_content(self):
        """source-hash in each export must match SHA-256 of the source file."""
        generate_exports()

        for target_system, target_dir in EXPORT_TARGETS.items():
            for export_file in sorted(target_dir.iterdir()):
                export_content = export_file.read_text(encoding="utf-8")
                source_hash = self._extract_source_hash(export_content)
                self.assertIsNotNone(
                    source_hash,
                    f"No source-hash found in {target_system}/{export_file.name}",
                )

                source_file = SOURCE_DIR / export_file.name
                self.assertTrue(
                    source_file.exists(),
                    f"Source file missing: {source_file}",
                )
                expected_hash = compute_source_hash(
                    source_file.read_text(encoding="utf-8")
                )
                self.assertEqual(
                    source_hash,
                    expected_hash,
                    f"source-hash mismatch in {target_system}/{export_file.name}",
                )

    def test_changed_source_changes_export(self):
        """When source content changes, export content (incl. hash) must differ."""
        import generate_exports as mod

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            src_dir = tmp_path / "instruction-blocks"
            src_dir.mkdir()

            original_src = mod.SOURCE_DIR
            original_targets = mod.EXPORT_TARGETS
            original_root = mod.REPO_ROOT
            mod.SOURCE_DIR = src_dir
            mod.REPO_ROOT = tmp_path
            mod.EXPORT_TARGETS = {
                "copilot": tmp_path / "exports" / "copilot",
            }

            try:
                # Write initial source
                (src_dir / "test.md").write_text(
                    "---\ntitle: Test\n---\nOriginal body\n", encoding="utf-8"
                )
                mod.generate_exports()
                v1 = (tmp_path / "exports" / "copilot" / "test.md").read_text(
                    encoding="utf-8"
                )

                # Modify source
                (src_dir / "test.md").write_text(
                    "---\ntitle: Test\n---\nModified body\n", encoding="utf-8"
                )
                mod.generate_exports()
                v2 = (tmp_path / "exports" / "copilot" / "test.md").read_text(
                    encoding="utf-8"
                )

                self.assertNotEqual(v1, v2, "Export must change when source changes")
                # source-hash must also differ
                h1 = self._extract_source_hash(v1)
                h2 = self._extract_source_hash(v2)
                self.assertNotEqual(h1, h2, "source-hash must change when source changes")
            finally:
                mod.SOURCE_DIR = original_src
                mod.EXPORT_TARGETS = original_targets
                mod.REPO_ROOT = original_root


class TestExportDriftGuard(unittest.TestCase):
    """Validates committed source↔export parity without mutating state.

    These tests read the current repository state directly — they do NOT call
    generate_exports() before asserting. Calling the generator first would
    repair any drift before measurement, making the guard ineffective
    (the doctor takes the temperature after giving ibuprofen).

    Generator repair behavior (stale removal, missing creation) is covered
    separately in TestEdgeCases using isolated temporary directories.
    """

    def test_no_orphaned_exports(self):
        """Every file in exports/ must correspond to a source in instruction-blocks/."""
        source_names = {f.name for f in SOURCE_DIR.glob("*.md")}

        for target_system, target_dir in EXPORT_TARGETS.items():
            if not target_dir.exists():
                continue
            for export_file in target_dir.iterdir():
                self.assertIn(
                    export_file.name,
                    source_names,
                    f"Orphaned export without source: {target_system}/{export_file.name}",
                )

    def test_no_missing_exports(self):
        """Every source in instruction-blocks/ must have a corresponding export."""
        for target_system, target_dir in EXPORT_TARGETS.items():
            export_names = (
                {f.name for f in target_dir.iterdir()}
                if target_dir.exists()
                else set()
            )
            for source_file in SOURCE_DIR.glob("*.md"):
                self.assertIn(
                    source_file.name,
                    export_names,
                    f"Missing export for {source_file.name} in {target_system}/",
                )


if __name__ == "__main__":
    unittest.main()
