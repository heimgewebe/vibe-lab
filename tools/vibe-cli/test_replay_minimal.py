#!/usr/bin/env python3
"""Regression tests for tools/vibe-cli/replay_minimal.py."""

from __future__ import annotations

import json
import sys
import unittest
from io import StringIO
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT / "tools" / "vibe-cli") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "tools" / "vibe-cli"))

import replay_minimal as rm  # noqa: E402


class ReplayMinimalTests(unittest.TestCase):
    def _run_capture(self, chain_path: Path) -> tuple[int, str]:
        buf = StringIO()
        saved = sys.stdout
        sys.stdout = buf
        try:
            code = rm.run(chain_path)
        finally:
            sys.stdout = saved
        return code, buf.getvalue()

    def test_valid_chain_returns_zero_and_emits_trace(self) -> None:
        chain_path = (
            rm.REPO_ROOT
            / "tests"
            / "fixtures"
            / "command_chains"
            / "valid-minimal.json"
        )
        code, output = self._run_capture(chain_path)
        self.assertEqual(code, 0)
        payload = json.loads(output)
        self.assertTrue(payload["validation"]["ok"])
        self.assertEqual(len(payload["trace"]), 3)
        self.assertEqual(payload["mutations"], [])

    def test_invalid_chain_returns_one_and_empty_trace(self) -> None:
        chain_path = (
            rm.REPO_ROOT
            / "tests"
            / "fixtures"
            / "command_chains"
            / "invalid-wrong-order.json"
        )
        code, output = self._run_capture(chain_path)
        self.assertEqual(code, 1)
        payload = json.loads(output)
        self.assertFalse(payload["validation"]["ok"])
        self.assertEqual(payload["trace"], [])
        codes = {err["code"] for err in payload["validation"]["errors"]}
        self.assertIn("command_sequence_invalid", codes)

    def test_output_is_deterministic(self) -> None:
        """Two runs of the same chain must produce byte-identical output."""
        chain_path = (
            rm.REPO_ROOT
            / "tests"
            / "fixtures"
            / "command_chains"
            / "valid-minimal.json"
        )
        _, first = self._run_capture(chain_path)
        _, second = self._run_capture(chain_path)
        self.assertEqual(first, second)

    def test_simulate_is_pure(self) -> None:
        """simulate() must not mutate the input chain."""
        chain = [
            {
                "command": "read_context",
                "version": "v0.1",
                "target_files": ["docs/index.md"],
            }
        ]
        snapshot = json.dumps(chain, sort_keys=True)
        rm.simulate(chain)
        self.assertEqual(json.dumps(chain, sort_keys=True), snapshot)

    def test_write_change_trace_marks_would_mutate_false(self) -> None:
        chain = [
            {
                "command": "write_change",
                "version": "v0.1",
                "target_files": ["docs/index.md"],
                "locator": "## X",
                "change_type": "modify",
                "forbidden_changes": [],
            }
        ]
        trace = rm.simulate(chain)
        self.assertFalse(trace[0]["would_mutate"])

    def test_dry_run_stdout_is_valid_json(self) -> None:
        """--dry-run must not pollute stdout with non-JSON text.

        The dry-run marker must go to stderr so that stdout remains parseable
        JSON. Previously, a `print(...)` call without `file=sys.stderr` broke
        JSON consumers.
        """
        import io

        chain_path = (
            rm.REPO_ROOT
            / "tests"
            / "fixtures"
            / "command_chains"
            / "valid-minimal.json"
        )
        buf_out = io.StringIO()
        buf_err = io.StringIO()
        saved_stdout, saved_stderr = sys.stdout, sys.stderr
        saved_argv = sys.argv
        sys.stdout = buf_out
        sys.stderr = buf_err
        sys.argv = ["replay_minimal.py", "--dry-run", str(chain_path)]
        try:
            with self.assertRaises(SystemExit) as cm:
                rm.main()
        finally:
            sys.stdout = saved_stdout
            sys.stderr = saved_stderr
            sys.argv = saved_argv
        self.assertEqual(cm.exception.code, 0)
        # stdout must be parseable JSON
        stdout_text = buf_out.getvalue()
        try:
            payload = json.loads(stdout_text)
        except json.JSONDecodeError as exc:
            self.fail(
                f"--dry-run stdout is not valid JSON: {exc}\nOutput was:\n{stdout_text}"
            )
        self.assertIn("mutations", payload)
        # dry-run marker must appear on stderr, not stdout
        self.assertIn("dry-run", buf_err.getvalue())


if __name__ == "__main__":
    unittest.main()
