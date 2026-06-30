#!/usr/bin/env python3
"""Regression tests for the PR context capture helper."""

from __future__ import annotations

import importlib.util
import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "pr_context_capture.py"
SPEC = importlib.util.spec_from_file_location("pr_context_capture", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
pr_context_capture = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pr_context_capture)


class PrContextCaptureTests(unittest.TestCase):
    def test_main_reports_capture_error_without_name_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            stderr = io.StringIO()
            stdout = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                rc = pr_context_capture.main([
                    "--work-root", tmp,
                    "prepare",
                    "--run-id", "run-invalid-base",
                    "--pair-id", "pair-small-doc-a",
                    "--slot", "1",
                    "--executor", "tester",
                    "--base-commit", "not-a-sha",
                ])
        self.assertEqual(rc, 1)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("error: invalid slot, executor, or base commit", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
