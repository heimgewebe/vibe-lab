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


if __name__ == "__main__":
    unittest.main()
