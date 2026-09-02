#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("audit_task_store.py")
spec = importlib.util.spec_from_file_location("operator_routing_ml_readiness_audit", MODULE_PATH)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class AuditTaskStoreTests(unittest.TestCase):
    def test_explicit_models_accept_split_and_equals_forms_and_normalize_aliases(self) -> None:
        argv = [
            "agy",
            "--model",
            "Gemini 3.1 Pro (High)",
            "--routing-model=Claude Opus 4.6 (Thinking)",
            "--model-v2",
            "gpt-oss-120b-medium",
        ]
        self.assertEqual(
            module._explicit_models(argv),
            [
                "gemini-3-1-pro-high",
                "claude-opus-4-6-thinking",
                "gpt-oss-120b-medium",
            ],
        )

    def test_json_nonempty_parses_whitespace_empty_array(self) -> None:
        self.assertEqual(module._json_nonempty("[ ]"), (False, True))
        self.assertEqual(module._json_nonempty("[\n]"), (False, True))
        self.assertEqual(module._json_nonempty('[{"id":"x"}]'), (True, True))
        self.assertEqual(module._json_nonempty("not-json"), (False, False))

    def test_workspace_route_coverage_counts_verified_evidence_without_exporting_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            verified = root / "workspace-a"
            missing = root / "workspace-b"
            absent = root / "workspace-c"
            for path in (verified, missing, absent):
                path.mkdir()
            (verified / "manifest.json").write_text(
                json.dumps({"workspace_id": "secret-a", "tasks": {"writer": "task-123"}, "route_evidence": {"schema_version": 2, "status": "verified", "evidence_complete": True, "recommendation_id": "secret"}}),
                encoding="utf-8",
            )
            (missing / "manifest.json").write_text(
                json.dumps({"workspace_id": "secret-b", "route_evidence": {"schema_version": 1, "status": "missing", "evidence_complete": False}}),
                encoding="utf-8",
            )
            (absent / "manifest.json").write_text(json.dumps({"workspace_id": "secret-c"}), encoding="utf-8")

            coverage = module._workspace_route_coverage(root, {"task-123"})
            self.assertEqual(coverage["manifest_count"], 3)
            self.assertEqual(coverage["route_evidence_present"], 2)
            self.assertEqual(coverage["route_evidence_verified"], 1)
            self.assertEqual(coverage["route_evidence_missing_status"], 1)
            self.assertEqual(coverage["route_evidence_schema_versions"], {"1": 1, "2": 1})
            self.assertTrue(coverage["task_reference_join_available"])
            self.assertEqual(coverage["verified_route_manifests_with_matching_task_rows"], 1)
            self.assertEqual(coverage["verified_route_manifest_task_join_coverage_percent"], 100.0)
            self.assertNotIn("workspace-a", json.dumps(coverage))
            self.assertNotIn("secret", json.dumps(coverage))


if __name__ == "__main__":
    unittest.main(verbosity=2)
