#!/usr/bin/env python3
"""Tests for generate_artifact_taxonomy.py."""

from __future__ import annotations

import unittest

from generate_artifact_taxonomy import (
    _is_high_risk_fallback,
    build_report,
    classify_file,
    load_taxonomy,
    render_markdown,
)


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

    def test_manifest_authority_is_procedure_contract(self) -> None:
        c = self._classify("experiments/my-experiment/manifest.yml")
        self.assertEqual(c["status"], "classified")
        self.assertEqual(c["layer"], "experiment")
        self.assertEqual(c["authority"], "procedure_contract")


class FallbackShareTest(unittest.TestCase):
    """Tests for fallback_share calculation and report structure."""

    def _make_classified(
        self,
        path: str,
        catchall: bool,
        layer: str = "docs",
        authority: str = "navigation_surface",
    ) -> dict:
        return {
            "path": path,
            "status": "classified",
            "layer": layer,
            "kind": "doc",
            "authority": authority,
            "lifecycle": "handcrafted",
            "enforcement": [],
            "origin": "handcrafted",
            "matched_patterns": ["docs/**"] if catchall else [f"docs/{path}"],
            "catchall_match": catchall,
        }

    def _build(self, items: list[dict]) -> dict:
        return build_report(items, [])

    def test_summary_has_fallback_share_fields(self) -> None:
        items = [
            self._make_classified("docs/a.md", catchall=False),
            self._make_classified("docs/b.md", catchall=True),
        ]
        report = self._build(items)
        s = report["summary"]
        self.assertIn("fallback_share", s)
        self.assertIn("fallback_threshold", s)
        self.assertIn("fallback_threshold_status", s)

    def test_fallback_share_computed_correctly(self) -> None:
        items = [
            self._make_classified("docs/a.md", catchall=False),
            self._make_classified("docs/b.md", catchall=True),
            self._make_classified("docs/c.md", catchall=True),
        ]
        report = self._build(items)
        s = report["summary"]
        self.assertAlmostEqual(s["fallback_share"], 2 / 3)
        self.assertEqual(s["fallback_threshold"], 0.5)
        self.assertEqual(s["fallback_threshold_status"], "warning")

    def test_fallback_share_ok_below_threshold(self) -> None:
        items = [
            self._make_classified("docs/a.md", catchall=False),
            self._make_classified("docs/b.md", catchall=False),
            self._make_classified("docs/c.md", catchall=True),
        ]
        report = self._build(items)
        s = report["summary"]
        self.assertAlmostEqual(s["fallback_share"], 1 / 3)
        self.assertEqual(s["fallback_threshold_status"], "ok")

    def test_fallback_share_zero_classified(self) -> None:
        report = self._build([])
        s = report["summary"]
        self.assertEqual(s["fallback_share"], 0.0)

    def test_fallback_summary_keys_present(self) -> None:
        items = [self._make_classified("docs/a.md", catchall=True)]
        report = self._build(items)
        fs = report["fallback_summary"]
        self.assertIn("by_layer", fs)
        self.assertIn("by_authority", fs)
        self.assertIn("high_risk_count", fs)

    def test_fallback_summary_by_layer_and_authority(self) -> None:
        items = [
            self._make_classified("docs/a.md", catchall=True, layer="docs", authority="navigation_surface"),
            self._make_classified("docs/b.md", catchall=True, layer="docs", authority="navigation_surface"),
            self._make_classified("gov/c.md", catchall=True, layer="governance", authority="procedure_contract"),
            self._make_classified("exact/d.md", catchall=False, layer="docs", authority="navigation_surface"),
        ]
        report = self._build(items)
        fs = report["fallback_summary"]
        self.assertEqual(fs["by_layer"]["docs"], 2)
        self.assertEqual(fs["by_layer"]["governance"], 1)
        self.assertEqual(fs["by_authority"]["navigation_surface"], 2)
        self.assertEqual(fs["by_authority"]["procedure_contract"], 1)

    def test_fallback_summary_high_risk_count(self) -> None:
        items = [
            # high-risk: governance layer
            self._make_classified("gov/a.md", catchall=True, layer="governance", authority="procedure_contract"),
            # high-risk: sovereign_source authority
            self._make_classified("gov/b.md", catchall=True, layer="docs", authority="sovereign_source"),
            # low-risk
            self._make_classified("docs/c.md", catchall=True, layer="docs", authority="navigation_surface"),
        ]
        report = self._build(items)
        self.assertEqual(report["fallback_summary"]["high_risk_count"], 2)


class IsHighRiskFallbackTest(unittest.TestCase):
    def _item(self, layer: str | None, authority: str | None) -> dict:
        return {"layer": layer, "authority": authority}

    def test_governance_layer_is_high_risk(self) -> None:
        self.assertTrue(_is_high_risk_fallback(self._item("governance", "procedure_contract")))

    def test_contract_layer_is_high_risk(self) -> None:
        self.assertTrue(_is_high_risk_fallback(self._item("contract", "navigation_surface")))

    def test_generated_layer_is_high_risk(self) -> None:
        self.assertTrue(_is_high_risk_fallback(self._item("generated", "navigation_surface")))

    def test_test_layer_is_high_risk(self) -> None:
        self.assertTrue(_is_high_risk_fallback(self._item("test", "navigation_surface")))

    def test_sovereign_source_authority_is_high_risk(self) -> None:
        self.assertTrue(_is_high_risk_fallback(self._item("docs", "sovereign_source")))

    def test_normative_contract_authority_is_high_risk(self) -> None:
        self.assertTrue(_is_high_risk_fallback(self._item("docs", "normative_contract")))

    def test_generated_projection_authority_is_high_risk(self) -> None:
        self.assertTrue(_is_high_risk_fallback(self._item("docs", "generated_projection")))

    def test_docs_navigation_surface_is_low_risk(self) -> None:
        self.assertFalse(_is_high_risk_fallback(self._item("docs", "navigation_surface")))

    def test_capture_raw_capture_is_low_risk(self) -> None:
        self.assertFalse(_is_high_risk_fallback(self._item("capture", "raw_capture")))


class FallbackReviewSectionSortTest(unittest.TestCase):
    """Tests for the risk-weighted sorting of fallback review items."""

    _LAYER_PRIORITY = [
        "governance", "contract", "generated", "test", "export", "agent",
        "experiment", "docs", "catalog", "runtime", "capture", "archive",
    ]
    _AUTHORITY_PRIORITY = [
        "sovereign_source", "normative_contract", "schema_truth", "decision_record",
        "evidence_log", "generated_projection", "procedure_contract", "diagnostic_signal",
        "navigation_surface", "runtime_observation", "raw_capture", "historical_record",
        "unknown",
    ]

    @classmethod
    def setUpClass(cls) -> None:
        cls.rules = load_taxonomy()["rules"]

    def _make_item(
        self,
        path: str,
        catchall: bool,
        layer: str,
        authority: str,
    ) -> dict:
        return {
            "path": path,
            "status": "classified",
            "layer": layer,
            "kind": "doc",
            "authority": authority,
            "lifecycle": "handcrafted",
            "enforcement": [],
            "origin": "handcrafted",
            "matched_patterns": ["**"],
            "catchall_match": catchall,
        }

    def _sort_key(self, item: dict) -> tuple:
        layer = item.get("layer") or ""
        authority = item.get("authority") or ""
        layer_idx = self._LAYER_PRIORITY.index(layer) if layer in self._LAYER_PRIORITY else len(self._LAYER_PRIORITY)
        auth_idx = self._AUTHORITY_PRIORITY.index(authority) if authority in self._AUTHORITY_PRIORITY else len(self._AUTHORITY_PRIORITY)
        return (not _is_high_risk_fallback(item), layer_idx, auth_idx, item.get("path", ""))

    def test_high_risk_before_low_risk(self) -> None:
        items = [
            self._make_item("docs/low.md", True, "docs", "navigation_surface"),
            self._make_item("gov/high.md", True, "governance", "procedure_contract"),
        ]
        report = build_report(items, [])
        fallback_items = [c for c in report["classifications"] if c.get("catchall_match")]
        sorted_items = sorted(fallback_items, key=self._sort_key)
        self.assertTrue(_is_high_risk_fallback(sorted_items[0]))
        self.assertFalse(_is_high_risk_fallback(sorted_items[-1]))

    def test_same_risk_sorted_by_layer_then_authority_then_path(self) -> None:
        items = [
            self._make_item("docs/z.md", True, "docs", "navigation_surface"),
            self._make_item("docs/a.md", True, "docs", "navigation_surface"),
            self._make_item("capture/b.md", True, "capture", "raw_capture"),
        ]
        report = build_report(items, [])
        fallback_items = [c for c in report["classifications"] if c.get("catchall_match")]
        sorted_items = sorted(fallback_items, key=self._sort_key)
        paths = [i["path"] for i in sorted_items]
        # docs (layer index 7) < capture (index 10) → docs items first
        self.assertLess(paths.index("docs/a.md"), paths.index("capture/b.md"))
        self.assertLess(paths.index("docs/z.md"), paths.index("capture/b.md"))
        # within docs: alphabetical path
        self.assertLess(paths.index("docs/a.md"), paths.index("docs/z.md"))


class MarkdownOutputTest(unittest.TestCase):
    """Tests for Markdown output of the artifact taxonomy report."""

    @classmethod
    def setUpClass(cls) -> None:
        items = [
            {
                "path": "docs/a.md",
                "status": "classified",
                "layer": "docs",
                "kind": "doc",
                "authority": "navigation_surface",
                "lifecycle": "handcrafted",
                "enforcement": [],
                "origin": "handcrafted",
                "matched_patterns": ["docs/**"],
                "catchall_match": True,
            },
            {
                "path": "gov/b.md",
                "status": "classified",
                "layer": "governance",
                "kind": "config",
                "authority": "procedure_contract",
                "lifecycle": "handcrafted",
                "enforcement": [],
                "origin": "handcrafted",
                "matched_patterns": [".github/**"],
                "catchall_match": True,
            },
        ]
        report = build_report(items, [])
        cls.md = render_markdown(report)

    def test_markdown_contains_fallback_share(self) -> None:
        self.assertIn("fallback_share:", self.md)

    def test_markdown_contains_fallback_threshold(self) -> None:
        self.assertIn("fallback_threshold:", self.md)

    def test_markdown_contains_review_section(self) -> None:
        self.assertIn("Fallback classified artifacts requiring review", self.md)

    def test_markdown_review_section_has_table(self) -> None:
        self.assertIn("| Path | Layer | Kind | Authority | Risk | Matched pattern |", self.md)


if __name__ == "__main__":
    unittest.main()
