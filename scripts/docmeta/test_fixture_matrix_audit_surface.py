#!/usr/bin/env python3
"""Regression tests for fixture-matrix audit markers."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MATRIX_PATH = REPO_ROOT / "docs" / "reference" / "agent-operability-fixture-matrix.md"


class FixtureMatrixAuditSurfaceTests(unittest.TestCase):
    def test_matrix_contains_audit_surface_markers(self) -> None:
        matrix = MATRIX_PATH.read_text(encoding="utf-8")

        self.assertIn("## 1. Command-Level Coverage", matrix)
        self.assertIn("## 2. Chain-Level Coverage", matrix)
        self.assertIn("## 3. Cross-Contract Coverage", matrix)
        self.assertIn("## 5. Known Gaps", matrix)
        self.assertRegex(matrix, r"covered:\s*(true|false)")
        self.assertIn("test_ref:", matrix)
        self.assertIn("gap: missing", matrix)
        self.assertIn("gap: intentional (v0.2)", matrix)


if __name__ == "__main__":
    unittest.main()