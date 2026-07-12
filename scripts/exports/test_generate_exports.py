#!/usr/bin/env python3
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_exports import generate_exports  # noqa: E402


class RetiredExportGeneratorTests(unittest.TestCase):
    def test_generator_publishes_tombstones_without_instruction_body(self) -> None:
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
                self.assertNotIn("DO THE ACTIVE THING", text)

    def test_generator_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "instruction-blocks"
            source.mkdir()
            (source / "rule.md").write_text("---\nstatus: adopted\n---\nbody\n", encoding="utf-8")
            targets = {"cursor": root / "exports/cursor"}
            self.assertEqual(generate_exports(source, targets), generate_exports(source, targets))


if __name__ == "__main__":
    unittest.main()
