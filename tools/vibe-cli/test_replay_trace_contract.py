#!/usr/bin/env python3
"""Contract tests for the v0.2 replay trace format (--emit-json mode).

Seven invariants verified:
  T1  Valid minimal chain → JSON conforms to schemas/replay.trace.schema.json
  T2  Every step has would_mutate: false
  T3  Top-level has would_mutate: false
  T4  Output is byte-identical over two runs (determinism)
  T5  Invalid chain → clear error structure (valid_chain=false, errors non-empty)
  T6  --dry-run --emit-json work together; stdout is schema-conformant v0.2 JSON
  T7  JSON contains no absolute local machine paths
"""

from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT / "tools" / "vibe-cli") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "tools" / "vibe-cli"))

import replay_minimal as rm  # noqa: E402

try:
    from jsonschema import Draft202012Validator
    from jsonschema.validators import validator_for
except ImportError:
    print("ERROR: Missing dependencies. Run: python3 -m pip install jsonschema")
    sys.exit(1)

SCHEMA_PATH = REPO_ROOT / "schemas" / "replay.trace.schema.json"
VALID_CHAIN = (
    REPO_ROOT / "tests" / "fixtures" / "command_chains" / "valid-minimal.json"
)
INVALID_CHAIN = (
    REPO_ROOT / "tests" / "fixtures" / "command_chains" / "invalid-wrong-order.json"
)


def _load_validator() -> Draft202012Validator:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    cls = validator_for(schema, default=Draft202012Validator)
    return cls(schema)


def _capture_emit_json(chain_path: Path) -> tuple[int, str]:
    """Run rm.run() in emit_json=True mode; return (exit_code, raw_stdout)."""
    buf = io.StringIO()
    saved = sys.stdout
    sys.stdout = buf
    try:
        code = rm.run(chain_path, emit_json=True)
    finally:
        sys.stdout = saved
    return code, buf.getvalue()


class ReplayTraceContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = _load_validator()

    # ------------------------------------------------------------------
    # T1 — schema conformance for valid chain
    # ------------------------------------------------------------------

    def test_t1_valid_chain_conforms_to_schema(self) -> None:
        """Valid minimal chain → JSON conforms to schemas/replay.trace.schema.json."""
        _, raw = _capture_emit_json(VALID_CHAIN)
        payload = json.loads(raw)
        # validate() raises ValidationError on failure — no error means pass.
        self.validator.validate(payload)
        # Structural spot-checks beyond schema.
        self.assertEqual(payload["version"], "v0.2")
        self.assertEqual(payload["mode"], "dry_run")
        self.assertTrue(payload["valid_chain"])
        self.assertEqual(payload["summary"]["non_mutation_guarantee"], True)
        self.assertEqual(payload["summary"]["record_count"], 3)
        self.assertEqual(payload["summary"]["skipped_record_count"], 0)

    # ------------------------------------------------------------------
    # T2 — every step has would_mutate: false
    # ------------------------------------------------------------------

    def test_t2_every_step_would_mutate_false(self) -> None:
        """Every step in steps[] carries would_mutate: false."""
        _, raw = _capture_emit_json(VALID_CHAIN)
        payload = json.loads(raw)
        steps = payload["steps"]
        self.assertGreater(len(steps), 0, "steps[] must be non-empty for valid chain")
        for step in steps:
            self.assertFalse(
                step["would_mutate"],
                f"step index={step['index']} has would_mutate=True",
            )

    # ------------------------------------------------------------------
    # T3 — top-level would_mutate: false
    # ------------------------------------------------------------------

    def test_t3_top_level_would_mutate_false(self) -> None:
        """Top-level would_mutate is false."""
        _, raw = _capture_emit_json(VALID_CHAIN)
        payload = json.loads(raw)
        self.assertFalse(payload["would_mutate"])

    # ------------------------------------------------------------------
    # T4 — determinism
    # ------------------------------------------------------------------

    def test_t4_output_is_deterministic(self) -> None:
        """Two consecutive runs of the same chain produce byte-identical output."""
        _, first = _capture_emit_json(VALID_CHAIN)
        _, second = _capture_emit_json(VALID_CHAIN)
        self.assertEqual(first, second)

    def test_summary_counts_are_consistent_for_valid_chain(self) -> None:
        """Summary counters must match the materialized top-level and step-level data."""
        _, raw = _capture_emit_json(VALID_CHAIN)
        payload = json.loads(raw)

        self.assertEqual(
            payload["summary"]["record_count"],
            payload["summary"]["step_count"]
            + payload["summary"]["skipped_record_count"],
        )
        self.assertEqual(
            payload["summary"]["error_count"],
            len(payload["errors"])
            + sum(len(step["errors"]) for step in payload["steps"]),
        )

    # ------------------------------------------------------------------
    # T5 — invalid chain produces clear error structure
    # ------------------------------------------------------------------

    def test_t5_invalid_chain_produces_error_structure(self) -> None:
        """Invalid chain → valid_chain=false and at least one error reported."""
        code, raw = _capture_emit_json(INVALID_CHAIN)
        self.assertEqual(code, 1, "invalid chain must return exit code 1")
        payload = json.loads(raw)
        self.assertFalse(payload["valid_chain"])
        # At least one error must be surfaced (top-level or step-level).
        has_errors = bool(payload["errors"]) or any(
            s["errors"] for s in payload["steps"]
        )
        self.assertTrue(has_errors, "invalid chain must carry at least one error message")
        # The v0.2 structure must still be schema-conformant.
        self.validator.validate(payload)

    # ------------------------------------------------------------------
    # T6 — --dry-run --emit-json work together
    # ------------------------------------------------------------------

    def test_t6_dry_run_and_emit_json_combined(self) -> None:
        """--dry-run --emit-json: stdout is schema-conformant v0.2 JSON; dry-run on stderr."""
        buf_out = io.StringIO()
        buf_err = io.StringIO()
        saved_stdout, saved_stderr = sys.stdout, sys.stderr
        saved_argv = sys.argv
        sys.stdout = buf_out
        sys.stderr = buf_err
        sys.argv = ["replay_minimal.py", "--dry-run", "--emit-json", str(VALID_CHAIN)]
        try:
            with self.assertRaises(SystemExit) as cm:
                rm.main()
        finally:
            sys.stdout = saved_stdout
            sys.stderr = saved_stderr
            sys.argv = saved_argv
        self.assertEqual(cm.exception.code, 0)
        payload = json.loads(buf_out.getvalue())
        self.validator.validate(payload)
        self.assertIn(
            "dry-run",
            buf_err.getvalue(),
            "dry-run marker must appear on stderr",
        )

    # ------------------------------------------------------------------
    # T7 — no absolute local machine paths in output
    # ------------------------------------------------------------------

    def test_t7_no_absolute_paths_in_output(self) -> None:
        """External chain paths are redacted deterministically and remain schema-valid."""
        with tempfile.TemporaryDirectory() as tmpdir:
            external_chain = Path(tmpdir) / "valid-minimal.json"
            external_chain.write_text(VALID_CHAIN.read_text(encoding="utf-8"), encoding="utf-8")

            _, raw = _capture_emit_json(external_chain)
            payload = json.loads(raw)

            self.validator.validate(payload)
            self.assertEqual(payload["chain_path"], "<external>/valid-minimal.json")
            self.assertNotIn(str(REPO_ROOT), raw)
            self.assertNotIn(tmpdir, raw)

    def test_unknown_command_is_visible_via_summary_counts(self) -> None:
        """Unknown commands must not disappear semantically from the v0.2 trace."""
        with tempfile.TemporaryDirectory() as tmpdir:
            chain_path = Path(tmpdir) / "unknown-command.json"
            chain_path.write_text(
                json.dumps([
                    {
                        "command": "unknown_command",
                        "version": "v0.1",
                    }
                ]),
                encoding="utf-8",
            )

            code, raw = _capture_emit_json(chain_path)
            payload = json.loads(raw)

            self.assertEqual(code, 1)
            self.validator.validate(payload)
            self.assertFalse(payload["valid_chain"])
            self.assertTrue(payload["errors"] or any(step["errors"] for step in payload["steps"]))
            self.assertEqual(payload["summary"]["record_count"], 1)
            self.assertEqual(payload["summary"]["step_count"], 0)
            self.assertEqual(payload["summary"]["skipped_record_count"], 1)
            self.assertEqual(
                payload["summary"]["record_count"],
                payload["summary"]["step_count"]
                + payload["summary"]["skipped_record_count"],
            )
            self.assertEqual(
                payload["summary"]["error_count"],
                len(payload["errors"])
                + sum(len(step["errors"]) for step in payload["steps"]),
            )


if __name__ == "__main__":
    unittest.main()
