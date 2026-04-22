#!/usr/bin/env python3
"""Regression tests for fixture-matrix known-gaps per-gap audit markers."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MATRIX_PATH = REPO_ROOT / "docs" / "reference" / "agent-operability-fixture-matrix.md"


class FixtureMatrixKnownGapsAuditTests(unittest.TestCase):
    def _section_body(self, matrix: str, heading: str) -> str:
        pattern = re.compile(
            rf"{re.escape(heading)}\n(.*?)(?=\n## [^#]|\Z)",
            re.DOTALL,
        )
        match = pattern.search(matrix)
        self.assertIsNotNone(match, f"section not found: {heading}")
        return match.group(1)

    def _extract_gap_subsections(self, known_gaps_text: str) -> list[tuple[str, str]]:
        """Extract (gap_number, subsection_body) for all ### 5.x subsections."""
        pattern = re.compile(
            r"^###\s+5\.(\d+)\s+.*?\n(.*?)(?=^###\s+5\.\d+\s+|\Z)",
            re.DOTALL | re.MULTILINE,
        )
        matches = pattern.finditer(known_gaps_text)
        return [(m.group(1), m.group(2)) for m in matches]

    def test_known_gaps_per_gap_audit_markers(self) -> None:
        """Test that each open gap subsection contains normalized audit markers."""
        matrix = MATRIX_PATH.read_text(encoding="utf-8")
        known_gaps = self._section_body(matrix, "## 5. Known Gaps")

        self.assertNotIn(
            "| Gap | Abdeckung | Test-Ref | Status |",
            known_gaps,
            "Known Gaps section must not mix the per-gap audit form with a redundant summary table",
        )

        gap_subsections = self._extract_gap_subsections(known_gaps)
        self.assertGreater(
            len(gap_subsections),
            0,
            "Known Gaps section must contain subsections (### 5.x)",
        )

        for gap_num, gap_body in gap_subsections:
            self.assertIn(
                "**Audit:**",
                gap_body,
                f"Gap 5.{gap_num} muss einen **Audit:**-Block enthalten",
            )
            self.assertRegex(
                gap_body,
                r"`covered:\s*(true|false)`",
                f"Gap 5.{gap_num} muss ein `covered: true|false` Marker haben",
            )
            self.assertIn(
                "`test_ref:",
                gap_body,
                f"Gap 5.{gap_num} muss ein `test_ref:` Marker haben",
            )
            self.assertRegex(
                gap_body,
                r"`gap:\s*(missing|intentional \(v0\.2\))`",
                f"Gap 5.{gap_num} muss ein `gap: missing` oder `gap: intentional (v0.2)` Marker haben",
            )


if __name__ == "__main__":
    unittest.main()
