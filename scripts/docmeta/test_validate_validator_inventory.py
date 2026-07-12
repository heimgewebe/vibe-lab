#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from validate_validator_inventory import validate_validator_inventory  # noqa: E402

ROOT = SCRIPT_DIR.parents[1]


class ValidatorInventoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / ".vibe").mkdir()
        (self.root / "schemas").mkdir()
        (self.root / ".github/workflows").mkdir(parents=True)
        for path in ("contracts", "docs", "experiments", "tests/fixtures", "tools/vibe-cli", "scripts/docmeta"):
            (self.root / path).mkdir(parents=True, exist_ok=True)
        schema = json.loads((ROOT / "schemas/validator-inventory.v1.schema.json").read_text())
        (self.root / "schemas/validator-inventory.v1.schema.json").write_text(json.dumps(schema))
        self.inventory = {
            "schema_version": "validator-inventory.v1",
            "baseline_commit": "a" * 40,
            "policy": {
                "max_active_specialist_targets": 2,
                "historical_evidence_retained": True,
                "pull_request_runs_all_groups": True,
                "main_runs_all_groups": True,
                "new_target_requires_classification": True,
                "classified_target_count": 3,
                "max_validate_job_named_steps": 10,
            },
            "groups": [
                {"id": "core", "consumer": "all repository contracts", "failure_classes": ["contract_drift"], "scope_paths": ["schemas"], "execution_policy": {"pull_request": "blocking", "main": "blocking"}, "targets": ["validate-core-one"]},
                {"id": "active", "consumer": "active experiment registry", "failure_classes": ["active_drift"], "scope_paths": ["experiments"], "execution_policy": {"pull_request": "blocking", "main": "blocking"}, "targets": ["validate-active-one"]},
                {"id": "legacy", "consumer": "historical experiment corpus", "failure_classes": ["legacy_drift"], "scope_paths": ["tests/fixtures"], "execution_policy": {"pull_request": "blocking", "main": "blocking"}, "review_at": "2026-09-01", "retirement_rule": "Remove only after equivalent generic coverage is proven.", "targets": ["validate-legacy-one"]},
            ],
            "supplemental_checks": [
                {"target": "validate-replay-mutation-guard", "consumer": "CI clean checkout proof", "failure_class": "replay_mutation", "execution_policy": {"pull_request": "blocking", "main": "blocking"}},
                {"target": "generate-blocking", "consumer": "committed generated outputs", "failure_class": "generated_drift", "execution_policy": {"pull_request": "blocking", "main": "blocking"}},
            ],
        }
        self.makefile = (
            "validate: validate-core validate-active validate-legacy\n"
            "validate-core: validate-core-one\n"
            "validate-active: validate-active-one\n"
            "validate-legacy: validate-legacy-one\n"
            "validate-core-one:\nvalidate-active-one:\nvalidate-legacy-one:\n"
            "validate-replay-mutation-guard:\ngenerate-blocking:\n"
        )
        self.workflow = (
            "jobs:\n  validate:\n    steps:\n"
            "      - name: core\n        run: make validate-core\n"
            "      - name: active\n        run: make validate-active\n"
            "      - name: legacy\n        run: make validate-legacy\n"
            "      - name: replay\n        run: make validate-replay-mutation-guard\n"
            "      - name: generated\n        run: make generate-blocking\n"
            "  non-blocking-diagnostics:\n"
        )
        self.write()

    def write(self) -> None:
        (self.root / ".vibe/validator-inventory.v1.json").write_text(json.dumps(self.inventory))
        (self.root / "Makefile").write_text(self.makefile)
        (self.root / ".github/workflows/validate.yml").write_text(self.workflow)

    def test_valid_inventory(self) -> None:
        result = validate_validator_inventory(repo_root=self.root)
        self.assertEqual(result["grouped_target_count"], 3)
        self.assertEqual(result["validate_job_named_steps"], 5)

    def test_unclassified_target_fails(self) -> None:
        self.makefile += "validate-surprise:\n"
        self.write()
        with self.assertRaisesRegex(ValueError, "unclassified"):
            validate_validator_inventory(repo_root=self.root)

    def test_group_dependency_drift_fails(self) -> None:
        self.makefile = self.makefile.replace(
            "validate-active: validate-active-one", "validate-active: validate-legacy-one"
        )
        self.write()
        with self.assertRaisesRegex(ValueError, "dependencies differ"):
            validate_validator_inventory(repo_root=self.root)

    def test_direct_workflow_validator_fails(self) -> None:
        self.workflow = self.workflow.replace(
            "  non-blocking-diagnostics:",
            "      - name: bypass\n        run: python3 scripts/docmeta/validate_schema.py\n  non-blocking-diagnostics:",
        )
        self.write()
        with self.assertRaisesRegex(ValueError, "bypasses grouped"):
            validate_validator_inventory(repo_root=self.root)

    def test_classified_count_drift_fails(self) -> None:
        self.inventory["policy"]["classified_target_count"] = 4
        self.write()
        with self.assertRaisesRegex(ValueError, "classified target count"):
            validate_validator_inventory(repo_root=self.root)

    def test_workflow_step_budget_fails(self) -> None:
        self.inventory["policy"]["max_validate_job_named_steps"] = 5
        self.workflow = self.workflow.replace(
            "  non-blocking-diagnostics:",
            "      - name: harmless extra\n"
            "        run: echo ok\n"
            "  non-blocking-diagnostics:",
        )
        self.write()
        with self.assertRaisesRegex(ValueError, "named-step budget"):
            validate_validator_inventory(repo_root=self.root)

    def test_active_budget_fails(self) -> None:
        self.inventory["policy"]["max_active_specialist_targets"] = 1
        self.inventory["groups"][1]["targets"].append("validate-active-two")
        self.makefile = self.makefile.replace(
            "validate-active: validate-active-one",
            "validate-active: validate-active-one validate-active-two",
        ) + "validate-active-two:\n"
        self.write()
        with self.assertRaisesRegex(ValueError, "budget exceeded"):
            validate_validator_inventory(repo_root=self.root)

    def test_real_repository_inventory(self) -> None:
        result = validate_validator_inventory()
        self.assertLessEqual(result["group_counts"]["active"], 12)
        self.assertTrue(result["historical_evidence_retained"])


if __name__ == "__main__":
    unittest.main()
