#!/usr/bin/env python3
"""Schema fixture tests for run-evidence-pack.v1 schema.

PR 4 scope: validates structure and enums only.
No semantic claim-evidence enforcement is implemented here.
"""

from __future__ import annotations

import json
from pathlib import Path

import unittest

import yaml
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCHEMA_PATH = REPO_ROOT / "schemas" / "run-evidence-pack.v1.schema.json"
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "claim_evidence"

VALID_FIXTURES = [
    "valid/minimal-pass-repo-local.yml",
    "valid/missing-evidence-verdict.yml",
    "valid/external-unverified.yml",
]

INVALID_FIXTURES = [
    "invalid/missing-run-id.yml",
    "invalid/empty-evidence-path.yml",
    "invalid/path-escape.yml",
    "invalid/unknown-evidence-status.yml",
]


class RunEvidencePackSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        cls.validator = Draft202012Validator(
            schema,
            format_checker=Draft202012Validator.FORMAT_CHECKER,
        )

    def _load_fixture(self, rel_path: str) -> dict:
        path = FIXTURE_ROOT / rel_path
        return yaml.safe_load(path.read_text(encoding="utf-8"))

    def test_valid_fixtures(self) -> None:
        for rel_path in VALID_FIXTURES:
            with self.subTest(rel_path=rel_path):
                instance = self._load_fixture(rel_path)
                self.validator.validate(instance)

    def test_invalid_fixtures(self) -> None:
        for rel_path in INVALID_FIXTURES:
            with self.subTest(rel_path=rel_path):
                instance = self._load_fixture(rel_path)
                with self.assertRaises(ValidationError):
                    self.validator.validate(instance)


if __name__ == "__main__":
    unittest.main(verbosity=2)
