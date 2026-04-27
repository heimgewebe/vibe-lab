#!/usr/bin/env python3
"""test_validate_export_parity.py — Regression tests for validate_export_parity.py."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_export_parity import (  # noqa: E402
    SOURCE_DIR,
    EXPORT_TARGETS,
    check_collisions,
    check_missing,
    check_orphans,
    validate,
    _source_names,
)


class TestSourceNames(unittest.TestCase):
    def test_flat_files_no_collision(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp)
            (src / "a.md").write_text("a")
            (src / "b.md").write_text("b")
            result = _source_names(src)
            self.assertEqual(set(result.keys()), {"a.md", "b.md"})
            for srcs in result.values():
                self.assertEqual(len(srcs), 1)

    def test_empty_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = _source_names(Path(tmp))
            self.assertEqual(result, {})


class TestCheckCollisions(unittest.TestCase):
    def test_no_collision(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp)
            (src / "a.md").write_text("a")
            (src / "b.md").write_text("b")
            name_map = _source_names(src)
            self.assertEqual(check_collisions(name_map), [])

    def test_collision_detected(self):
        # Simulate a collision by injecting a duplicate into name_map
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
            name_map = _source_names(src)
            self.assertEqual(check_orphans(name_map, "copilot", tgt), [])

    def test_orphan_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src"
            tgt = Path(tmp) / "tgt"
            src.mkdir()
            tgt.mkdir()
            (src / "a.md").write_text("a")
            (tgt / "a.md").write_text("a")
            (tgt / "orphan.md").write_text("orphan")  # no source
            name_map = _source_names(src)
            errors = check_orphans(name_map, "copilot", tgt)
            self.assertEqual(len(errors), 1)
            self.assertIn("orphan.md", errors[0])
            self.assertIn("Orphan", errors[0])

    def test_missing_target_dir_is_not_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src"
            src.mkdir()
            (src / "a.md").write_text("a")
            name_map = _source_names(src)
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
            name_map = _source_names(src)
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
            # b.md is missing in target
            name_map = _source_names(src)
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
            name_map = _source_names(src)
            errors = check_missing(name_map, "copilot", tgt)
            self.assertEqual(len(errors), 2)


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
            (tgt / "orphan.md").write_text("orphan")  # no source
            # a.md is missing in target

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


class TestLiveRepoState(unittest.TestCase):
    """Prüft den tatsächlichen committed Repo-Zustand — mutiert nichts."""

    def test_live_repo_parity(self):
        errors = validate()
        self.assertEqual(
            errors,
            [],
            f"Export-Parität verletzt im Repo:\n" + "\n".join(f"  • {e}" for e in errors),
        )


if __name__ == "__main__":
    unittest.main()
