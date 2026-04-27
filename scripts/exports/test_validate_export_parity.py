#!/usr/bin/env python3
"""test_validate_export_parity.py — Regression tests for validate_export_parity.py."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from export_contract import EXPORT_TARGETS, SOURCE_DIR, expected_export_name  # noqa: E402
from validate_export_parity import (  # noqa: E402
    _source_name_map,
    check_collisions,
    check_missing,
    check_orphans,
    validate,
)


class TestContractConsistency(unittest.TestCase):
    """Generator und Validator müssen dieselbe Export-Konfiguration sehen."""

    def test_validator_uses_contract_source_dir(self):
        """validate_export_parity importiert SOURCE_DIR aus export_contract."""
        import validate_export_parity as vep
        import export_contract as ec
        self.assertIs(vep.SOURCE_DIR, ec.SOURCE_DIR)

    def test_validator_uses_contract_export_targets(self):
        """validate_export_parity importiert EXPORT_TARGETS aus export_contract."""
        import validate_export_parity as vep
        import export_contract as ec
        self.assertIs(vep.EXPORT_TARGETS, ec.EXPORT_TARGETS)

    def test_generator_uses_contract_source_dir(self):
        """generate_exports importiert SOURCE_DIR aus export_contract."""
        import generate_exports as gen
        import export_contract as ec
        self.assertIs(gen.SOURCE_DIR, ec.SOURCE_DIR)

    def test_generator_uses_contract_export_targets(self):
        """generate_exports importiert EXPORT_TARGETS aus export_contract."""
        import generate_exports as gen
        import export_contract as ec
        self.assertIs(gen.EXPORT_TARGETS, ec.EXPORT_TARGETS)

    def test_expected_export_name_is_deterministic(self):
        """expected_export_name liefert für gleiche Eingabe stets gleiche Ausgabe."""
        p = Path("/some/dir/spec-first.md")
        self.assertEqual(expected_export_name(p), expected_export_name(p))

    def test_expected_export_name_returns_string(self):
        p = Path("/repo/instruction-blocks/constraint-before-code.md")
        result = expected_export_name(p)
        self.assertIsInstance(result, str)
        self.assertTrue(result.endswith(".md"))


class TestSourceNameMap(unittest.TestCase):
    def test_flat_files_no_collision(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp)
            (src / "a.md").write_text("a")
            (src / "b.md").write_text("b")
            result = _source_name_map(src)
            self.assertEqual(set(result.keys()), {"a.md", "b.md"})
            for srcs in result.values():
                self.assertEqual(len(srcs), 1)

    def test_empty_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = _source_name_map(Path(tmp))
            self.assertEqual(result, {})

    def test_non_md_files_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp)
            (src / "a.md").write_text("a")
            (src / "notes.txt").write_text("txt")
            (src / ".gitkeep").write_text("")
            result = _source_name_map(src)
            self.assertEqual(set(result.keys()), {"a.md"})


class TestCheckCollisions(unittest.TestCase):
    def test_no_collision(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp)
            (src / "a.md").write_text("a")
            (src / "b.md").write_text("b")
            name_map = _source_name_map(src)
            self.assertEqual(check_collisions(name_map), [])

    def test_collision_detected(self):
        p1 = Path("/repo/instruction-blocks/a.md")
        p2 = Path("/repo/instruction-blocks/sub/a.md")
        name_map = {"a.md": [p1, p2]}
        errors = check_collisions(name_map)
        self.assertEqual(len(errors), 1)
        self.assertIn("a.md", errors[0])
        self.assertIn("Kollision", errors[0])

    def test_multiple_collisions(self):
        name_map = {
            "a.md": [Path("/x/a.md"), Path("/y/a.md")],
            "b.md": [Path("/x/b.md"), Path("/y/b.md")],
            "c.md": [Path("/x/c.md")],
        }
        errors = check_collisions(name_map)
        self.assertEqual(len(errors), 2)


class TestCheckOrphans(unittest.TestCase):
    def test_no_orphans(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src"
            tgt = Path(tmp) / "tgt"
            src.mkdir()
            tgt.mkdir()
            (src / "a.md").write_text("a")
            (tgt / "a.md").write_text("a")
            name_map = _source_name_map(src)
            self.assertEqual(check_orphans(name_map, "copilot", tgt), [])

    def test_orphan_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src"
            tgt = Path(tmp) / "tgt"
            src.mkdir()
            tgt.mkdir()
            (src / "a.md").write_text("a")
            (tgt / "a.md").write_text("a")
            (tgt / "orphan.md").write_text("orphan")
            name_map = _source_name_map(src)
            errors = check_orphans(name_map, "copilot", tgt)
            self.assertEqual(len(errors), 1)
            self.assertIn("orphan.md", errors[0])
            self.assertIn("Orphan", errors[0])

    def test_non_md_files_in_target_not_reported_as_orphan(self):
        """Non-Markdown-Dateien im Export-Verzeichnis gelten nicht als Orphan."""
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src"
            tgt = Path(tmp) / "tgt"
            src.mkdir()
            tgt.mkdir()
            (src / "a.md").write_text("a")
            (tgt / "a.md").write_text("a")
            (tgt / ".gitkeep").write_text("")
            (tgt / "notes.txt").write_text("txt")
            name_map = _source_name_map(src)
            errors = check_orphans(name_map, "copilot", tgt)
            self.assertEqual(errors, [], f"Non-md files wrongly flagged: {errors}")

    def test_missing_target_dir_is_not_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src"
            src.mkdir()
            (src / "a.md").write_text("a")
            name_map = _source_name_map(src)
            nonexistent = Path(tmp) / "nonexistent"
            self.assertEqual(check_orphans(name_map, "copilot", nonexistent), [])


class TestCheckMissing(unittest.TestCase):
    def test_no_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src"
            tgt = Path(tmp) / "tgt"
            src.mkdir()
            tgt.mkdir()
            (src / "a.md").write_text("a")
            (tgt / "a.md").write_text("a")
            name_map = _source_name_map(src)
            self.assertEqual(check_missing(name_map, "copilot", tgt), [])

    def test_missing_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src"
            tgt = Path(tmp) / "tgt"
            src.mkdir()
            tgt.mkdir()
            (src / "a.md").write_text("a")
            (src / "b.md").write_text("b")
            (tgt / "a.md").write_text("a")
            name_map = _source_name_map(src)
            errors = check_missing(name_map, "copilot", tgt)
            self.assertEqual(len(errors), 1)
            self.assertIn("b.md", errors[0])
            self.assertIn("Fehlender Export", errors[0])

    def test_empty_target_all_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src"
            tgt = Path(tmp) / "tgt"
            src.mkdir()
            tgt.mkdir()
            (src / "a.md").write_text("a")
            (src / "b.md").write_text("b")
            name_map = _source_name_map(src)
            errors = check_missing(name_map, "copilot", tgt)
            self.assertEqual(len(errors), 2)

    def test_non_md_in_target_not_counted_as_present(self):
        """Nur *.md zählt — .gitkeep darf 'a.md' nicht als vorhanden markieren."""
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src"
            tgt = Path(tmp) / "tgt"
            src.mkdir()
            tgt.mkdir()
            (src / "a.md").write_text("a")
            (tgt / ".gitkeep").write_text("")
            name_map = _source_name_map(src)
            errors = check_missing(name_map, "copilot", tgt)
            self.assertEqual(len(errors), 1)
            self.assertIn("a.md", errors[0])


class TestValidateIntegration(unittest.TestCase):
    def test_clean_state_no_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "instruction-blocks"
            tgt_copilot = Path(tmp) / "exports" / "copilot"
            tgt_cursor = Path(tmp) / "exports" / "cursor"
            src.mkdir(parents=True)
            tgt_copilot.mkdir(parents=True)
            tgt_cursor.mkdir(parents=True)

            for name in ["a.md", "b.md"]:
                (src / name).write_text(name)
                (tgt_copilot / name).write_text(name)
                (tgt_cursor / name).write_text(name)

            errors = validate(src, {"copilot": tgt_copilot, "cursor": tgt_cursor})
            self.assertEqual(errors, [])

    def test_orphan_and_missing_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "instruction-blocks"
            tgt = Path(tmp) / "exports" / "copilot"
            src.mkdir(parents=True)
            tgt.mkdir(parents=True)

            (src / "a.md").write_text("a")
            (tgt / "orphan.md").write_text("orphan")

            errors = validate(src, {"copilot": tgt})
            error_text = "\n".join(errors)
            self.assertIn("orphan.md", error_text)
            self.assertIn("a.md", error_text)
            self.assertEqual(len(errors), 2)

    def test_empty_source_empty_target_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "instruction-blocks"
            tgt = Path(tmp) / "exports" / "copilot"
            src.mkdir(parents=True)
            tgt.mkdir(parents=True)

            errors = validate(src, {"copilot": tgt})
            self.assertEqual(errors, [])

    def test_non_md_in_target_does_not_cause_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "instruction-blocks"
            tgt = Path(tmp) / "exports" / "copilot"
            src.mkdir(parents=True)
            tgt.mkdir(parents=True)

            (src / "a.md").write_text("a")
            (tgt / "a.md").write_text("a")
            (tgt / ".gitkeep").write_text("")

            errors = validate(src, {"copilot": tgt})
            self.assertEqual(errors, [])


class TestLiveRepoState(unittest.TestCase):
    """Prüft den tatsächlichen committed Repo-Zustand — mutiert nichts."""

    def test_live_repo_parity(self):
        errors = validate()
        self.assertEqual(
            errors,
            [],
            "Export-Parität verletzt im Repo:\n" + "\n".join(f"  • {e}" for e in errors),
        )


if __name__ == "__main__":
    unittest.main()
