#!/usr/bin/env python3
"""Contract tests for the v0.2 replay trace format (--emit-json mode).

Core invariants verified:
    T1  Valid minimal chain → JSON conforms to schemas/replay.trace.schema.json
    T2  Every step has would_mutate: false
    T3  Top-level has would_mutate: false
    T4  Output is byte-identical over two runs (determinism)
    T5  Invalid chain → clear error structure (valid_chain=false, errors non-empty)
    T6  --dry-run --emit-json work together; stdout is schema-conformant v0.2 JSON
    T7  No absolute local machine paths in any v0.2 payload string
    T8  Setup failures still emit schema-conformant v0.2 JSON (exit code 2)
"""

from __future__ import annotations

import io
import json
import re
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
    cls.check_schema(schema)
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


def _capture_legacy_output(chain_path: Path) -> tuple[int, str]:
    """Run rm.run() in legacy mode; return (exit_code, raw_stdout)."""
    buf = io.StringIO()
    saved = sys.stdout
    sys.stdout = buf
    try:
        code = rm.run(chain_path, emit_json=False)
    finally:
        sys.stdout = saved
    return code, buf.getvalue()


def _iter_strings(node: Any) -> list[str]:
    """Collect all string leaves recursively from a JSON-like structure."""
    out: list[str] = []
    if isinstance(node, dict):
        for v in node.values():
            out.extend(_iter_strings(v))
    elif isinstance(node, list):
        for item in node:
            out.extend(_iter_strings(item))
    elif isinstance(node, str):
        out.append(node)
    return out


def _contains_absolute_posix_path(value: str) -> bool:
    """Return true when value contains a likely POSIX absolute path token."""
    # Ignore redaction marker and URL authorities.
    if value.startswith("<external>/") or "//" in value:
        return False
    # Detect path-like tokens such as /tmp/a.txt or /home/x/file.py:12
    return bool(
        re.search(r"(^|[\s:=\[\]\(\)\{\}\"',])/[^\s\"'<>|\[\]{}(),;]+", value)
    )


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
        self.assertEqual(payload["skipped_records"], [])
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

    def _assert_summary_counts_consistent(self, payload: dict) -> None:
        """Helper: verify that all summary counters are consistent with materialized data."""
        # record_count = step_count + skipped_record_count
        self.assertEqual(
            payload["summary"]["record_count"],
            payload["summary"]["step_count"]
            + payload["summary"]["skipped_record_count"],
        )
        # skipped_record_count must match len(skipped_records)
        self.assertEqual(
            payload["summary"]["skipped_record_count"],
            len(payload["skipped_records"]),
        )
        # error_count = len(top-level errors) + sum(step-level errors)
        self.assertEqual(
            payload["summary"]["error_count"],
            len(payload["errors"])
            + sum(len(step["errors"]) for step in payload["steps"]),
        )
        # commands_seen must equal the unique commands from steps, sorted.
        commands_from_steps = sorted({step["command"] for step in payload["steps"]})
        self.assertEqual(payload["summary"]["commands_seen"], commands_from_steps)
        # Uniqueness: no duplicates in commands_seen.
        self.assertEqual(
            len(payload["summary"]["commands_seen"]),
            len(set(payload["summary"]["commands_seen"])),
        )

    def test_summary_counts_are_consistent_for_valid_chain(self) -> None:
        """Summary counters must match the materialized top-level and step-level data."""
        _, raw = _capture_emit_json(VALID_CHAIN)
        payload = json.loads(raw)
        self._assert_summary_counts_consistent(payload)

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
        # Verify summary counts consistency even for invalid chains.
        self._assert_summary_counts_consistent(payload)

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
        self._assert_summary_counts_consistent(payload)
        self.assertIn(
            "dry-run",
            buf_err.getvalue(),
            "dry-run marker must appear on stderr",
        )

    # ------------------------------------------------------------------
    # T8 — setup failures must still emit schema-valid JSON
    # ------------------------------------------------------------------

    def test_emit_json_missing_chain_file_returns_schema_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            missing_path = Path(tmpdir) / "does-not-exist.json"
            code, raw = _capture_emit_json(missing_path)
            payload = json.loads(raw)

            self.assertEqual(code, 2)
            self.validator.validate(payload)
            self.assertFalse(payload["valid_chain"])
            self.assertEqual(payload["steps"], [])
            self.assertEqual(payload["skipped_records"], [])
            self.assertEqual(payload["summary"]["record_count"], 0)
            self.assertEqual(payload["summary"]["step_count"], 0)
            self.assertEqual(payload["summary"]["skipped_record_count"], 0)
            self.assertGreaterEqual(payload["summary"]["error_count"], 1)
            self.assertTrue(payload["errors"])
            self.assertNotIn(tmpdir, raw)

    def test_emit_json_malformed_json_returns_schema_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            malformed_path = Path(tmpdir) / "malformed.json"
            malformed_path.write_text("{not json", encoding="utf-8")

            code, raw = _capture_emit_json(malformed_path)
            payload = json.loads(raw)

            self.assertEqual(code, 2)
            self.validator.validate(payload)
            self.assertFalse(payload["valid_chain"])
            self.assertTrue(payload["errors"])
            self.assertEqual(payload["steps"], [])
            self.assertNotIn(tmpdir, raw)

    def test_emit_json_non_array_json_returns_schema_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            non_array_path = Path(tmpdir) / "non-array.json"
            non_array_path.write_text(
                json.dumps({"command": "read_context"}),
                encoding="utf-8",
            )

            code, raw = _capture_emit_json(non_array_path)
            payload = json.loads(raw)

            self.assertEqual(code, 2)
            self.validator.validate(payload)
            self.assertFalse(payload["valid_chain"])
            self.assertEqual(payload["steps"], [])
            self.assertEqual(payload["summary"]["record_count"], 0)
            self.assertGreaterEqual(payload["summary"]["error_count"], 1)

    # ------------------------------------------------------------------
    # T7 — no absolute local machine paths in output
    # ------------------------------------------------------------------

    def test_v0_2_payload_contains_no_absolute_paths_recursively(self) -> None:
        """No absolute local paths may appear in any payload string leaf."""
        with tempfile.TemporaryDirectory() as tmpdir:
            external_chain = Path(tmpdir) / "valid-minimal.json"
            external_chain.write_text(VALID_CHAIN.read_text(encoding="utf-8"), encoding="utf-8")

            _, raw = _capture_emit_json(external_chain)
            payload = json.loads(raw)
            self._assert_summary_counts_consistent(payload)

            self.validator.validate(payload)
            for s in _iter_strings(payload):
                self.assertFalse(
                    _contains_absolute_posix_path(s),
                    f"absolute path leaked in payload string: {s!r}",
                )
            self.assertNotIn(str(REPO_ROOT), raw)
            self.assertNotIn(tmpdir, raw)

    def test_absolute_target_files_are_redacted_or_normalized(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            chain_path = Path(tmpdir) / "abs-target.json"
            abs_target = "/tmp/sensitive/readme.md"
            chain_path.write_text(
                json.dumps(
                    [
                        {
                            "command": "read_context",
                            "version": "v0.1",
                            "target_files": [abs_target],
                            "extracted_facts": ["fact"],
                        },
                        {
                            "command": "write_change",
                            "version": "v0.1",
                            "target_files": [abs_target],
                            "change_type": "modify",
                            "locator": "docs/index.md#L1",
                            "exact_before": "a",
                            "exact_after": "b",
                            "forbidden_changes": [],
                        },
                        {
                            "command": "validate_change",
                            "version": "v0.1",
                            "checks": ["lint"],
                            "success": True,
                            "errors": [],
                        },
                    ]
                ),
                encoding="utf-8",
            )

            _, raw = _capture_emit_json(chain_path)
            payload = json.loads(raw)
            self.validator.validate(payload)
            self.assertNotIn(abs_target, raw)
            for s in _iter_strings(payload):
                self.assertFalse(_contains_absolute_posix_path(s), s)

    def test_absolute_locator_is_redacted(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            chain_path = Path(tmpdir) / "abs-locator.json"
            abs_locator = "/tmp/sensitive/readme.md:10"
            chain_path.write_text(
                json.dumps(
                    [
                        {
                            "command": "read_context",
                            "version": "v0.1",
                            "target_files": ["docs/index.md"],
                            "extracted_facts": ["fact"],
                        },
                        {
                            "command": "write_change",
                            "version": "v0.1",
                            "target_files": ["docs/index.md"],
                            "change_type": "modify",
                            "locator": abs_locator,
                            "exact_before": "a",
                            "exact_after": "b",
                            "forbidden_changes": [],
                        },
                        {
                            "command": "validate_change",
                            "version": "v0.1",
                            "checks": ["lint"],
                            "success": True,
                            "errors": [],
                        },
                    ]
                ),
                encoding="utf-8",
            )

            _, raw = _capture_emit_json(chain_path)
            payload = json.loads(raw)
            self.validator.validate(payload)
            self.assertNotIn(abs_locator, raw)
            for s in _iter_strings(payload):
                self.assertFalse(_contains_absolute_posix_path(s), s)

    def test_absolute_locator_with_hash_line_is_redacted(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            chain_path = Path(tmpdir) / "abs-locator-hash.json"
            abs_locator = "/tmp/sensitive/readme.md#L42"
            chain_path.write_text(
                json.dumps(
                    [
                        {
                            "command": "read_context",
                            "version": "v0.1",
                            "target_files": ["docs/index.md"],
                            "extracted_facts": ["fact"],
                        },
                        {
                            "command": "write_change",
                            "version": "v0.1",
                            "target_files": ["docs/index.md"],
                            "change_type": "modify",
                            "locator": abs_locator,
                            "exact_before": "a",
                            "exact_after": "b",
                            "forbidden_changes": [],
                        },
                        {
                            "command": "validate_change",
                            "version": "v0.1",
                            "checks": ["lint"],
                            "success": True,
                            "errors": [],
                        },
                    ]
                ),
                encoding="utf-8",
            )

            _, raw = _capture_emit_json(chain_path)
            payload = json.loads(raw)
            self.validator.validate(payload)
            self.assertNotIn(abs_locator, raw)
            self.assertIn("<external>/readme.md#L42", raw)
            for s in _iter_strings(payload):
                self.assertFalse(_contains_absolute_posix_path(s), s)

    def test_redaction_handles_backtick_prefixed_absolute_path(self) -> None:
        self.assertEqual(
            rm._redact_absolute_paths_in_string("`/tmp/secret.txt`"),
            "`<external>/secret.txt`",
        )

    def test_redaction_handles_external_prefix_then_absolute_path(self) -> None:
        self.assertEqual(
            rm._redact_absolute_paths_in_string("<external> /tmp/secret.txt"),
            "<external> <external>/secret.txt",
        )

    def test_redaction_keeps_already_redacted_path_unchanged(self) -> None:
        self.assertEqual(
            rm._redact_absolute_paths_in_string("<external>/secret.txt"),
            "<external>/secret.txt",
        )

    def test_repo_relative_hash_locator_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            chain_path = Path(tmpdir) / "repo-relative-locator-hash.json"
            repo_relative_locator = "docs/index.md#L42"
            chain_path.write_text(
                json.dumps(
                    [
                        {
                            "command": "read_context",
                            "version": "v0.1",
                            "target_files": ["docs/index.md"],
                            "extracted_facts": ["fact"],
                        },
                        {
                            "command": "write_change",
                            "version": "v0.1",
                            "target_files": ["docs/index.md"],
                            "change_type": "modify",
                            "locator": repo_relative_locator,
                            "exact_before": "a",
                            "exact_after": "b",
                            "forbidden_changes": [],
                        },
                        {
                            "command": "validate_change",
                            "version": "v0.1",
                            "checks": ["lint"],
                            "success": True,
                            "errors": [],
                        },
                    ]
                ),
                encoding="utf-8",
            )

            _, raw = _capture_emit_json(chain_path)
            payload = json.loads(raw)
            self.validator.validate(payload)
            self.assertIn(repo_relative_locator, raw)
            self.assertNotIn("<external>/index.md#L42", raw)
            for step in payload["steps"]:
                if step["command"] == "write_change":
                    self.assertEqual(step.get("locator"), repo_relative_locator)

    def test_legacy_external_chain_path_remains_unredacted(self) -> None:
        """Legacy output keeps its external path behavior; v0.2 keeps redacted behavior."""
        with tempfile.TemporaryDirectory() as tmpdir:
            external_chain = Path(tmpdir) / "valid-minimal.json"
            external_chain.write_text(
                VALID_CHAIN.read_text(encoding="utf-8"),
                encoding="utf-8",
            )

            legacy_code, legacy_raw = _capture_legacy_output(external_chain)
            self.assertEqual(legacy_code, 0)
            legacy_payload = json.loads(legacy_raw)
            self.assertEqual(legacy_payload["chain"], str(external_chain))

            json_code, json_raw = _capture_emit_json(external_chain)
            self.assertEqual(json_code, 0)
            json_payload = json.loads(json_raw)
            self.assertEqual(json_payload["chain_path"], "<external>/valid-minimal.json")

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
            self.assertEqual(
                payload["skipped_records"],
                [
                    {
                        "index": 0,
                        "command": "unknown_command",
                        "reason": "unknown_command",
                    }
                ],
            )
            self.assertEqual(payload["summary"]["record_count"], 1)
            self.assertEqual(payload["summary"]["step_count"], 0)
            self.assertEqual(payload["summary"]["skipped_record_count"], 1)
            self._assert_summary_counts_consistent(payload)

    def test_missing_command_field_is_visible_as_separate_reason(self) -> None:
        """Records without 'command' field: reason=missing_or_non_string_command, deterministic label."""
        with tempfile.TemporaryDirectory() as tmpdir:
            chain_path = Path(tmpdir) / "missing-cmd.json"
            chain_path.write_text(
                json.dumps([{"version": "v0.1"}]),  # missing "command" field
                encoding="utf-8",
            )

            code, raw = _capture_emit_json(chain_path)
            payload = json.loads(raw)
            self.assertEqual(code, 1)
            self.validator.validate(payload)
            self.assertFalse(payload["valid_chain"])
            self.assertEqual(
                payload["skipped_records"],
                [
                    {
                        "index": 0,
                        "command": "<missing_or_non_string_command>",
                        "reason": "missing_or_non_string_command",
                    }
                ],
            )
            self.assertEqual(payload["summary"]["record_count"], 1)
            self.assertEqual(payload["summary"]["step_count"], 0)
            self.assertEqual(payload["summary"]["skipped_record_count"], 1)
            self._assert_summary_counts_consistent(payload)

    def test_empty_command_field_is_visible_as_missing_or_non_string(self) -> None:
        """Records with empty command string are treated as missing/non-string command."""
        with tempfile.TemporaryDirectory() as tmpdir:
            chain_path = Path(tmpdir) / "empty-cmd.json"
            chain_path.write_text(
                json.dumps([{"command": "", "version": "v0.1"}]),
                encoding="utf-8",
            )

            code, raw = _capture_emit_json(chain_path)
            payload = json.loads(raw)
            self.assertEqual(code, 1)
            self.validator.validate(payload)
            self.assertFalse(payload["valid_chain"])
            self.assertEqual(
                payload["skipped_records"],
                [
                    {
                        "index": 0,
                        "command": "<missing_or_non_string_command>",
                        "reason": "missing_or_non_string_command",
                    }
                ],
            )
            self._assert_summary_counts_consistent(payload)

    def test_invalid_list_fields_are_not_partially_filtered(self) -> None:
        """Invalid mixed-type list fields are omitted rather than partially projected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            chain_path = Path(tmpdir) / "mixed-list-fields.json"
            chain_path.write_text(
                json.dumps(
                    [
                        {
                            "command": "read_context",
                            "version": "v0.1",
                            "target_files": ["docs/index.md", 123],
                        },
                        {
                            "command": "validate_change",
                            "version": "v0.1",
                            "checks": ["lint", 123],
                            "success": False,
                            "errors": ["check failed"],
                        },
                    ]
                ),
                encoding="utf-8",
            )

            code, raw = _capture_emit_json(chain_path)
            payload = json.loads(raw)
            self.assertEqual(code, 1)
            self.validator.validate(payload)
            self.assertFalse(payload["valid_chain"])

            step_by_index = {step["index"]: step for step in payload["steps"]}
            self.assertNotIn("target_files", step_by_index[0])
            self.assertNotIn("checks", step_by_index[1])
            self._assert_summary_counts_consistent(payload)

    def test_non_object_record_is_visible_as_skipped_record(self) -> None:
        """Builder hardening: non-object records are surfaced as skipped_records entries."""
        chain = ["not-an-object"]
        errors = [
            rm.vcc.ChainError(
                code="contract_invalid",
                message="chain[0] must be an object",
                command_index=0,
                path="<external>/non-object-record.json",
            )
        ]

        payload = rm._build_trace_v0_2("<external>/non-object-record.json", chain, errors)
        self.validator.validate(payload)
        self.assertFalse(payload["valid_chain"])
        self.assertEqual(
            payload["skipped_records"],
            [
                {
                    "index": 0,
                    "command": "<non_object_record>",
                    "reason": "non_object_record",
                }
            ],
        )
        self.assertEqual(payload["summary"]["record_count"], 1)
        self.assertEqual(payload["summary"]["step_count"], 0)
        self.assertEqual(payload["summary"]["skipped_record_count"], 1)
        self._assert_summary_counts_consistent(payload)

    def test_non_object_record_does_not_crash_emit_json_path(self) -> None:
        """CLI path: non-object records must produce v0.2 diagnostics, not crash."""
        with tempfile.TemporaryDirectory() as tmpdir:
            chain_path = Path(tmpdir) / "non-object-record.json"
            chain_path.write_text(
                json.dumps(["not-an-object"]),
                encoding="utf-8",
            )

            code, raw = _capture_emit_json(chain_path)
            payload = json.loads(raw)

            self.assertEqual(code, 1)
            self.validator.validate(payload)
            self.assertFalse(payload["valid_chain"])
            self.assertEqual(
                payload["skipped_records"],
                [
                    {
                        "index": 0,
                        "command": "<non_object_record>",
                        "reason": "non_object_record",
                    }
                ],
            )
            self._assert_summary_counts_consistent(payload)

    def test_builder_marks_skipped_record_invalid_even_without_validator_error(self) -> None:
        """Skipped records must force valid_chain=false even when errors[] is empty."""
        payload = rm._build_trace_v0_2(
            "<external>/unknown.json",
            [{"command": "unknown_command"}],
            [],
        )
        self.validator.validate(payload)
        self.assertFalse(payload["valid_chain"])
        self.assertEqual(payload["summary"]["skipped_record_count"], 1)
        self._assert_summary_counts_consistent(payload)


if __name__ == "__main__":
    unittest.main()
