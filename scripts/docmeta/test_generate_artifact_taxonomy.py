#!/usr/bin/env python3
"""Tests for generate_artifact_taxonomy.py."""

from __future__ import annotations

import unittest

from generate_artifact_taxonomy import classify_file, load_taxonomy


class TaxonomyClassificationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rules = load_taxonomy()["rules"]

    def _classify(self, path: str) -> dict:
        return classify_file(path, self.rules)

    def test_evidence_jsonl_classified(self) -> None:
        c = self._classify("experiments/foo/results/evidence.jsonl")
        self.assertEqual(c["status"], "classified")
        self.assertEqual(c["layer"], "experiment")
        self.assertEqual(c["authority"], "evidence_log")
        self.assertEqual(c["kind"], "evidence_log")

    def test_decision_yml_classified(self) -> None:
        c = self._classify("experiments/foo/results/decision.yml")
        self.assertEqual(c["layer"], "experiment")
        self.assertEqual(c["authority"], "decision_record")
        self.assertEqual(c["kind"], "decision_record")

    def test_generated_doc_classified(self) -> None:
        c = self._classify("docs/_generated/system-map.md")
        self.assertEqual(c["layer"], "generated")
        self.assertEqual(c["authority"], "diagnostic_signal")
        self.assertEqual(c["kind"], "generated_artifact")

    def test_export_projection_classified(self) -> None:
        c = self._classify("exports/copilot/some-block.md")
        self.assertEqual(c["layer"], "export")
        self.assertEqual(c["kind"], "tool_projection")
        self.assertEqual(c["authority"], "generated_projection")

    def test_unknown_file_reported(self) -> None:
        c = self._classify("totally/unmapped/path.bin")
        self.assertEqual(c["status"], "unknown")
        self.assertEqual(c["authority"], "unknown")

    def test_github_workflow_classified(self) -> None:
        c = self._classify(".github/workflows/validate.yml")
        self.assertEqual(c["status"], "classified")
        self.assertEqual(c["layer"], "governance")
        self.assertEqual(c["kind"], "ci_workflow")
        self.assertEqual(c["authority"], "procedure_contract")

    def test_github_agent_classified(self) -> None:
        c = self._classify(".github/agents/experiment-critic.agent.md")
        self.assertEqual(c["status"], "classified")
        self.assertEqual(c["layer"], "agent")
        self.assertEqual(c["kind"], "agent_definition")

    def test_github_pr_template_classified(self) -> None:
        c = self._classify(".github/pull_request_template.md")
        self.assertEqual(c["status"], "classified")
        self.assertEqual(c["layer"], "governance")
        self.assertEqual(c["kind"], "contribution_template")

    def test_github_issue_template_classified(self) -> None:
        c = self._classify(".github/ISSUE_TEMPLATE/experiment-proposal.yml")
        self.assertEqual(c["status"], "classified")
        self.assertEqual(c["layer"], "governance")
        self.assertEqual(c["kind"], "issue_template")

    def test_github_codeowners_classified(self) -> None:
        c = self._classify(".github/CODEOWNERS")
        self.assertEqual(c["status"], "classified")
        self.assertEqual(c["layer"], "governance")
        self.assertEqual(c["kind"], "code_ownership")


if __name__ == "__main__":
    unittest.main()
