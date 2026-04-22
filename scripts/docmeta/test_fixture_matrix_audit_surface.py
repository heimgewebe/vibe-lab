#!/usr/bin/env python3
"""Regression tests for fixture-matrix audit markers."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MATRIX_PATH = REPO_ROOT / "docs" / "reference" / "agent-operability-fixture-matrix.md"


class FixtureMatrixAuditSurfaceTests(unittest.TestCase):
    def _section_body(self, matrix: str, heading: str) -> str:
        pattern = re.compile(
            rf"{re.escape(heading)}\n(.*?)(?=\n## [^#]|\Z)",
            re.DOTALL,
        )
        match = pattern.search(matrix)
        self.assertIsNotNone(match, f"section not found: {heading}")
        return match.group(1)

    def test_matrix_contains_section_scoped_audit_surface(self) -> None:
        matrix = MATRIX_PATH.read_text(encoding="utf-8")

        command_level = self._section_body(matrix, "## 1. Command-Level Coverage")
        chain_level = self._section_body(matrix, "## 2. Chain-Level Coverage")
        cross_contract = self._section_body(matrix, "## 3. Cross-Contract Coverage")
        known_gaps = self._section_body(matrix, "## 5. Known Gaps")

        for section_name, section_body in (
            ("Command-Level", command_level),
            ("Chain-Level", chain_level),
            ("Cross-Contract", cross_contract),
        ):
            self.assertRegex(
                section_body,
                r"covered:\s*(true|false)",
                f"{section_name} section must contain covered markers",
            )
            self.assertIn(
                "test_ref:",
                section_body,
                f"{section_name} section must contain test_ref markers",
            )

        self.assertIn("gap:", known_gaps)
        self.assertIn("gap: intentional (v0.2)", known_gaps)
        self.assertTrue(
            "gap: missing" in known_gaps or "covered: false" in known_gaps,
            "Known Gaps section must preserve an explicit open audit signal",
        )


if __name__ == "__main__":
    unittest.main()