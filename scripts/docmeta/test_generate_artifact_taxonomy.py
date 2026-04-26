#!/usr/bin/env python3
"""Tests for generate_artifact_taxonomy.py."""

from __future__ import annotations

import unittest

from generate_artifact_taxonomy import (
    _build_residual_cluster_views,
    _build_residual_clusters,
    _format_top_items,
    _is_high_risk_fallback,
    _md_code_span,
    _select_fallback_pattern,
    _top_n,
    build_report,
    classify_file,
    fallback_review_sort_key,
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

    def test_experiment_run_meta_is_specific_runtime_observation(self) -> None:
        c = self._classify("experiments/my-exp/artifacts/run-001/run_meta.json")
        self.assertEqual(c["status"], "classified")
        self.assertEqual(c["layer"], "experiment")
        self.assertEqual(c["kind"], "run_metadata")
        self.assertEqual(c["authority"], "runtime_observation")
        self.assertFalse(c["catchall_match"])

    def test_experiment_execution_txt_is_specific_runtime_observation(self) -> None:
        c = self._classify("experiments/my-exp/artifacts/run-001/execution.txt")
        self.assertEqual(c["status"], "classified")
        self.assertEqual(c["kind"], "execution_trace")
        self.assertEqual(c["authority"], "runtime_observation")
        self.assertFalse(c["catchall_match"])

    def test_experiment_test_output_is_specific_runtime_observation(self) -> None:
        c = self._classify("experiments/my-exp/artifacts/run-001/test_output.txt")
        self.assertEqual(c["status"], "classified")
        self.assertEqual(c["kind"], "test_output")
        self.assertEqual(c["authority"], "runtime_observation")
        self.assertFalse(c["catchall_match"])

    def test_experiment_test_output_direct_artifacts_path_is_specific_runtime_observation(self) -> None:
        c = self._classify("experiments/my-exp/artifacts/test_output.txt")
        self.assertEqual(c["status"], "classified")
        self.assertEqual(c["layer"], "experiment")
        self.assertEqual(c["kind"], "test_output")
        self.assertEqual(c["authority"], "runtime_observation")
        self.assertFalse(c["catchall_match"])

    def test_experiment_timing_measurement_is_specific_runtime_observation(self) -> None:
        c = self._classify("experiments/my-exp/artifacts/run-001/time_to_first_pass_seconds.txt")
        self.assertEqual(c["status"], "classified")
        self.assertEqual(c["kind"], "timing_measurement")
        self.assertEqual(c["authority"], "runtime_observation")
        self.assertFalse(c["catchall_match"])

    def test_experiment_metrics_json_is_specific_runtime_observation(self) -> None:
        c = self._classify("experiments/my-exp/artifacts/metrics.json")
        self.assertEqual(c["status"], "classified")
        self.assertEqual(c["kind"], "experiment_metric")
        self.assertEqual(c["authority"], "runtime_observation")
        self.assertFalse(c["catchall_match"])


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
            "matched_patterns": ["docs/**"] if catchall else [path],
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
        self.assertIn("by_matched_pattern", fs)
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

    def test_fallback_share_ignores_ambiguous_and_conflict(self) -> None:
        """ambiguous/conflict items with catchall_match must not inflate classified or fallback_share."""
        items = [
            self._make_classified("docs/a.md", catchall=True),
            {**self._make_classified("docs/b.md", catchall=True), "status": "ambiguous"},
            {**self._make_classified("docs/c.md", catchall=True), "status": "conflict"},
        ]
        report = self._build(items)
        s = report["summary"]
        self.assertEqual(s["classified"], 1)
        self.assertEqual(s["fallback_classified"], 1)
        self.assertEqual(s["fallback_share"], 1.0)
        self.assertEqual(s["ambiguous"], 1)
        self.assertEqual(s["conflict"], 1)


    def test_fallback_summary_by_matched_pattern(self) -> None:
        items = [
            self._make_classified("docs/a.md", catchall=True),   # matched_patterns=["docs/**"]
            self._make_classified("docs/b.md", catchall=True),   # matched_patterns=["docs/**"]
            self._make_classified("gov/c.md", catchall=True, layer="governance", authority="procedure_contract"),
            self._make_classified("exact/d.md", catchall=False),
        ]
        # Override matched_patterns for the gov item to use a distinct pattern
        items[2]["matched_patterns"] = ["gov/**"]
        report = self._build(items)
        fs = report["fallback_summary"]
        self.assertEqual(fs["by_matched_pattern"]["docs/**"], 2)
        self.assertEqual(fs["by_matched_pattern"]["gov/**"], 1)
        self.assertNotIn("exact/d.md", fs["by_matched_pattern"])

    def test_fallback_summary_by_matched_pattern_empty_patterns(self) -> None:
        item = self._make_classified("docs/a.md", catchall=True)
        item["matched_patterns"] = []
        report = self._build([item])
        fs = report["fallback_summary"]
        self.assertIn("<missing>", fs["by_matched_pattern"])
        self.assertEqual(fs["by_matched_pattern"]["<missing>"], 1)

    def test_fallback_summary_by_matched_pattern_ignores_non_classified(self) -> None:
        items = [
            self._make_classified("scripts/a.py", catchall=True),
            {**self._make_classified("scripts/b.py", catchall=True), "status": "ambiguous"},
            {**self._make_classified("scripts/c.py", catchall=True), "status": "conflict"},
        ]
        for item in items:
            item["matched_patterns"] = ["scripts/**"]
        report = self._build(items)
        by_pattern = report["fallback_summary"]["by_matched_pattern"]
        self.assertEqual(by_pattern["scripts/**"], 1)


class TopNFunctionTest(unittest.TestCase):
    """Tests for the _top_n helper."""

    def test_returns_top_n_by_count(self) -> None:
        counter = {"a.py": 5, "b.py": 2, "c.py": 8, "d.py": 1}
        result = _top_n(counter, n=2)
        self.assertEqual(list(result.keys()), ["c.py", "a.py"])
        self.assertEqual(result["c.py"], 8)
        self.assertEqual(result["a.py"], 5)

    def test_ties_broken_by_key_ascending(self) -> None:
        counter = {"b.py": 3, "a.py": 3}
        result = _top_n(counter, n=2)
        self.assertEqual(list(result.keys()), ["a.py", "b.py"])

    def test_returns_all_when_fewer_than_n(self) -> None:
        counter = {"x.py": 1}
        result = _top_n(counter, n=10)
        self.assertEqual(len(result), 1)

    def test_empty_counter_returns_empty(self) -> None:
        self.assertEqual(_top_n({}, n=5), {})


class MdCodeSpanTest(unittest.TestCase):
    """Tests for _md_code_span helper."""

    def test_wraps_plain_value_in_code_span(self) -> None:
        self.assertEqual(_md_code_span("__init__.py"), "`__init__.py`")

    def test_escapes_pipe_inside_table_cell(self) -> None:
        self.assertEqual(_md_code_span("a|b"), "`a\\|b`")

    def test_normalizes_newline(self) -> None:
        self.assertEqual(_md_code_span("a\nb"), "`a b`")

    def test_uses_longer_fence_when_value_contains_backtick(self) -> None:
        self.assertEqual(_md_code_span("a`b"), "``a`b``")

    def test_uses_longer_fence_for_double_backtick_run(self) -> None:
        self.assertEqual(_md_code_span("a``b"), "```a``b```")

    def test_wraps_single_backtick_content_with_inner_spaces(self) -> None:
        self.assertEqual(_md_code_span("`"), "`` ` ``")

    def test_wraps_leading_backtick_content_with_inner_spaces(self) -> None:
        self.assertEqual(_md_code_span("`x"), "`` `x ``")

    def test_wraps_trailing_backtick_content_with_inner_spaces(self) -> None:
        self.assertEqual(_md_code_span("x`"), "`` x` ``")

    def test_wraps_double_backtick_content_with_longer_fence_and_inner_spaces(self) -> None:
        self.assertEqual(_md_code_span("``"), "``` `` ```")

    def test_normalizes_carriage_return_newline(self) -> None:
        self.assertEqual(_md_code_span("a\r\nb"), "`a b`")


class FormatTopItemsTest(unittest.TestCase):
    """Tests for _format_top_items helper."""

    def test_returns_dash_for_empty(self) -> None:
        self.assertEqual(_format_top_items({}), "-")

    def test_formats_key_value_pairs_as_code_spans(self) -> None:
        result = _format_top_items({"foo.py": 3, "bar.py": 1}, limit=5)
        self.assertEqual(result, "`foo.py`=3, `bar.py`=1")

    def test_limits_to_given_number(self) -> None:
        items = {f"f{i}.py": i for i in range(10, 0, -1)}
        result = _format_top_items(items, limit=3)
        self.assertEqual(len(result.split(", ")), 3)

    def test_escapes_pipe_in_key(self) -> None:
        result = _format_top_items({"a|b": 1}, limit=5)
        self.assertIn("`a\\|b`=1", result)


class ResidualClustersTest(unittest.TestCase):
    """Tests for _build_residual_clusters and build_report residual_clusters field."""

    def _make_item(
        self,
        path: str,
        pattern: str = "scripts/**",
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
            "matched_patterns": [pattern],
            "catchall_match": True,
        }

    def test_residual_clusters_present_in_fallback_summary(self) -> None:
        items = [self._make_item("scripts/foo.py")]
        report = build_report(items, [])
        self.assertIn("residual_clusters", report["fallback_summary"])

    def test_residual_clusters_structure(self) -> None:
        items = [
            self._make_item("scripts/foo.py", pattern="scripts/**"),
            self._make_item("scripts/bar.py", pattern="scripts/**"),
        ]
        clusters = _build_residual_clusters(items)
        self.assertEqual(len(clusters), 1)
        c = clusters[0]
        self.assertEqual(c["matched_pattern"], "scripts/**")
        self.assertEqual(c["total"], 2)
        self.assertIn("high_risk_count", c)
        self.assertIn("top_basenames", c)
        self.assertIn("top_parent_dirs", c)

    def test_residual_clusters_groups_by_pattern(self) -> None:
        items = [
            self._make_item("scripts/a.py", pattern="scripts/**"),
            self._make_item("scripts/b.py", pattern="scripts/**"),
            self._make_item("tests/x.py", pattern="tests/**"),
        ]
        clusters = _build_residual_clusters(items)
        self.assertEqual(len(clusters), 2)
        totals = {c["matched_pattern"]: c["total"] for c in clusters}
        self.assertEqual(totals["scripts/**"], 2)
        self.assertEqual(totals["tests/**"], 1)

    def test_residual_clusters_sorted_by_high_risk_then_total_then_pattern(self) -> None:
        """High-risk clusters must sort before low-risk clusters regardless of total."""
        items = (
            [self._make_item(f"experiments/{i}.md", pattern="experiments/**", layer="docs", authority="navigation_surface") for i in range(10)]
            + [self._make_item(f"scripts/{i}.py", pattern="scripts/**", layer="test", authority="navigation_surface") for i in range(2)]
        )
        clusters = _build_residual_clusters(items)
        # scripts/** has high_risk (test layer) but only 2 items
        # experiments/** has 10 items but high_risk_count 0
        self.assertEqual(clusters[0]["matched_pattern"], "scripts/**")
        self.assertEqual(clusters[1]["matched_pattern"], "experiments/**")

    def test_residual_clusters_tie_break_higher_total_first(self) -> None:
        """When high_risk_count is equal, higher total comes first."""
        items = (
            [self._make_item(f"docs/{i}.md", pattern="docs/**") for i in range(5)]
            + [self._make_item(f"capture/{i}.md", pattern="capture/**") for i in range(2)]
        )
        clusters = _build_residual_clusters(items)
        # both have high_risk_count 0; docs/** has more items
        self.assertEqual(clusters[0]["matched_pattern"], "docs/**")
        self.assertEqual(clusters[1]["matched_pattern"], "capture/**")

    def test_residual_clusters_tie_break_pattern_asc(self) -> None:
        """When high_risk_count and total are equal, matched_pattern sorts ascending."""
        items = (
            [self._make_item(f"zz/{i}.md", pattern="zz/**") for i in range(3)]
            + [self._make_item(f"aa/{i}.md", pattern="aa/**") for i in range(3)]
        )
        clusters = _build_residual_clusters(items)
        self.assertEqual(clusters[0]["matched_pattern"], "aa/**")
        self.assertEqual(clusters[1]["matched_pattern"], "zz/**")

    def test_residual_clusters_high_risk_count(self) -> None:
        items = [
            self._make_item("gov/a.md", pattern="governance/**", layer="governance", authority="procedure_contract"),
            self._make_item("gov/b.md", pattern="governance/**", layer="docs", authority="navigation_surface"),
        ]
        clusters = _build_residual_clusters(items)
        self.assertEqual(len(clusters), 1)
        self.assertEqual(clusters[0]["high_risk_count"], 1)

    def test_residual_clusters_top_basenames(self) -> None:
        items = [
            self._make_item("scripts/foo.py"),
            self._make_item("scripts/sub/foo.py"),
            self._make_item("scripts/bar.py"),
        ]
        clusters = _build_residual_clusters(items)
        basenames = clusters[0]["top_basenames"]
        self.assertEqual(basenames["foo.py"], 2)
        self.assertEqual(basenames["bar.py"], 1)

    def test_residual_clusters_top_parent_dirs(self) -> None:
        items = [
            self._make_item("scripts/sub/a.py"),
            self._make_item("scripts/sub/b.py"),
            self._make_item("scripts/other/c.py"),
        ]
        clusters = _build_residual_clusters(items)
        parents = clusters[0]["top_parent_dirs"]
        self.assertEqual(parents["scripts/sub"], 2)
        self.assertEqual(parents["scripts/other"], 1)

    def test_residual_clusters_excludes_non_catchall(self) -> None:
        """Non-catchall items must not appear in residual_clusters."""
        items = [
            {
                "path": "docs/README.md",
                "status": "classified",
                "layer": "docs",
                "kind": "doc",
                "authority": "navigation_surface",
                "lifecycle": "handcrafted",
                "enforcement": [],
                "origin": "handcrafted",
                "matched_patterns": ["docs/README.md"],
                "catchall_match": False,
            },
            self._make_item("scripts/foo.py", pattern="scripts/**"),
        ]
        clusters = _build_residual_clusters(
            [i for i in items if i.get("status") == "classified" and i.get("catchall_match")]
        )
        self.assertEqual(len(clusters), 1)
        self.assertEqual(clusters[0]["matched_pattern"], "scripts/**")

    def test_residual_clusters_empty_when_no_fallback(self) -> None:
        self.assertEqual(_build_residual_clusters([]), [])

    def test_residual_clusters_excludes_unknown_and_non_classified_via_build_report(self) -> None:
        """build_report must not pass unknown/ambiguous/conflict items to residual_clusters."""
        items = [
            self._make_item("scripts/a.py", pattern="scripts/**"),
            {**self._make_item("scripts/b.py", pattern="scripts/**"), "status": "unknown"},
            {**self._make_item("scripts/c.py", pattern="scripts/**"), "status": "ambiguous"},
            {**self._make_item("scripts/d.py", pattern="scripts/**"), "status": "conflict"},
        ]
        report = build_report(items, [])
        clusters = report["fallback_summary"]["residual_clusters"]
        self.assertEqual(len(clusters), 1)
        self.assertEqual(clusters[0]["total"], 1)

    def test_residual_cluster_views_present_in_fallback_summary(self) -> None:
        items = [self._make_item("scripts/foo.py")]
        report = build_report(items, [])
        fs = report["fallback_summary"]
        self.assertIn("residual_cluster_views", fs)
        views = fs["residual_cluster_views"]
        self.assertIn("risk_first", views)
        self.assertIn("volume_first", views)

    def test_residual_cluster_views_risk_first_matches_residual_clusters(self) -> None:
        """risk_first view must equal the existing residual_clusters list (risk-first sorted)."""
        items = [
            self._make_item("scripts/a.py", pattern="scripts/**", layer="test"),
            self._make_item("tests/b.py", pattern="tests/**", layer="docs"),
        ]
        report = build_report(items, [])
        fs = report["fallback_summary"]
        self.assertEqual(fs["residual_cluster_views"]["risk_first"], fs["residual_clusters"])

    def test_residual_cluster_views_volume_first_orders_by_total(self) -> None:
        """volume_first must rank larger clusters before smaller ones regardless of risk."""
        items = [
            # scripts/**: 1 item, high-risk (test layer)
            self._make_item("scripts/a.py", pattern="scripts/**", layer="test", authority="sovereign_source"),
            # experiments/**: 3 items, low-risk
            self._make_item("experiments/a.md", pattern="experiments/**"),
            self._make_item("experiments/b.md", pattern="experiments/**"),
            self._make_item("experiments/c.md", pattern="experiments/**"),
        ]
        report = build_report(items, [])
        views = report["fallback_summary"]["residual_cluster_views"]
        risk_patterns = [c["matched_pattern"] for c in views["risk_first"]]
        volume_patterns = [c["matched_pattern"] for c in views["volume_first"]]
        # risk-first: scripts/** has high_risk_count=1, experiments/** has 0 → scripts first
        self.assertEqual(risk_patterns[0], "scripts/**")
        # volume-first: experiments/** has total=3, scripts/** has total=1 → experiments first
        self.assertEqual(volume_patterns[0], "experiments/**")

    def test_residual_cluster_views_empty_when_no_fallback(self) -> None:
        views = _build_residual_cluster_views([])
        self.assertEqual(views["risk_first"], [])
        self.assertEqual(views["volume_first"], [])


class ResidualClustersMarkdownTest(unittest.TestCase):
    """Tests for the Residual fallback clusters section in Markdown output."""

    @classmethod
    def setUpClass(cls) -> None:
        def _make(path: str, pattern: str, layer: str = "docs", authority: str = "navigation_surface") -> dict:
            return {
                "path": path,
                "status": "classified",
                "layer": layer,
                "kind": "doc",
                "authority": authority,
                "lifecycle": "handcrafted",
                "enforcement": [],
                "origin": "handcrafted",
                "matched_patterns": [pattern],
                "catchall_match": True,
            }
        # 7 clusters: 2 high-risk small ones and 1 large low-risk one so the two
        # sort views (risk-first vs. volume-first) produce meaningfully different orderings.
        # scripts/docmeta/ items give us a stable parent-dir (scripts/docmeta=2) and
        # two __init__.py files (one in scripts/docmeta, one in scripts/exports) give a
        # stable basename (__init__.py=2) that can be asserted as code-spans in the Markdown.
        items = (
            [_make(f"scripts/{i}.py", "scripts/**", "test", "navigation_surface") for i in range(2)]
            + [_make("scripts/docmeta/__init__.py", "scripts/**", "test", "navigation_surface")]
            + [_make("scripts/docmeta/helper.py", "scripts/**", "test", "navigation_surface")]
            + [_make("scripts/exports/__init__.py", "scripts/**", "test", "navigation_surface")]
            + [_make(f"tests/{i}.py", "tests/**", "test", "navigation_surface") for i in range(4)]
            + [_make(f"experiments/{i}.md", "experiments/**") for i in range(10)]
            + [_make(f"docs/{i}.md", "docs/**") for i in range(3)]
            + [_make(f"capture/{i}.md", "capture/**") for i in range(2)]
            + [_make(f"exports/{i}.md", "exports/**") for i in range(2)]
            + [_make("tools/one.sh", "tools/**")]
        )
        report = build_report(items, [])
        cls.report = report
        cls.md = render_markdown(report)

    def test_markdown_contains_residual_clusters_section(self) -> None:
        self.assertIn("## Residual fallback clusters", self.md)

    def test_markdown_residual_clusters_correct_table_header(self) -> None:
        self.assertIn(
            "| matched_pattern | total | high_risk_count | top_basenames | top_parent_dirs |",
            self.md,
        )

    def test_markdown_residual_clusters_no_subsection_headers(self) -> None:
        """Per-cluster backtick-prefixed ### headers must not appear (section headers are plain text)."""
        self.assertNotIn("### `", self.md)

    def test_markdown_residual_clusters_has_risk_first_subsection(self) -> None:
        self.assertIn("### Risk-first clusters", self.md)

    def test_markdown_residual_clusters_has_volume_first_subsection(self) -> None:
        self.assertIn("### Volume-first clusters", self.md)

    def _count_rows_in_subsection(self, subsection_header: str) -> int:
        lines = self.md.splitlines()
        in_sub = False
        count = 0
        for line in lines:
            if line.startswith(subsection_header):
                in_sub = True
                continue
            if in_sub and (line.startswith("## ") or line.startswith("### ")):
                break
            if in_sub and line.startswith("| `"):
                count += 1
        return count

    def _pattern_positions_in_subsection(self, subsection_header: str) -> dict[str, int]:
        lines = self.md.splitlines()
        in_sub = False
        positions: dict[str, int] = {}
        row_index = 0
        for line in lines:
            if line.startswith(subsection_header):
                in_sub = True
                continue
            if in_sub and (line.startswith("## ") or line.startswith("### ")):
                break
            if in_sub and line.startswith("| `"):
                # Extract the pattern from the first backtick-quoted segment
                parts = line.split("`")
                if len(parts) >= 2:
                    positions[parts[1]] = row_index
                row_index += 1
        return positions

    def test_markdown_both_tables_render_at_most_5_rows(self) -> None:
        """Each subsection table must show at most 5 data rows."""
        for header in ("### Risk-first clusters", "### Volume-first clusters"):
            count = self._count_rows_in_subsection(header)
            self.assertLessEqual(count, 5, f"{header} rendered more than 5 rows")

    def test_markdown_risk_first_orders_high_risk_before_large_lowrisk(self) -> None:
        """scripts/** (high_risk=5) must rank above experiments/** (high_risk=0) in risk-first view."""
        pos = self._pattern_positions_in_subsection("### Risk-first clusters")
        self.assertIn("scripts/**", pos)
        self.assertIn("experiments/**", pos)
        self.assertLess(pos["scripts/**"], pos["experiments/**"])

    def test_markdown_volume_first_orders_large_lowrisk_before_small_highrisk(self) -> None:
        """experiments/** (total=10) must rank above scripts/** (total=5) in volume-first view."""
        pos = self._pattern_positions_in_subsection("### Volume-first clusters")
        self.assertIn("experiments/**", pos)
        self.assertIn("scripts/**", pos)
        self.assertLess(pos["experiments/**"], pos["scripts/**"])

    def test_markdown_risk_first_renders_pattern_as_code_span(self) -> None:
        self.assertIn("| `scripts/**` |", self.md)

    def test_markdown_volume_first_renders_pattern_as_code_span(self) -> None:
        self.assertIn("| `experiments/**` |", self.md)

    def test_markdown_top_basenames_render_as_code_spans(self) -> None:
        """top_basenames entries must appear as code-spans in the rendered Markdown tables.

        The fixture includes two __init__.py files under scripts/**:
        scripts/docmeta/__init__.py and scripts/exports/__init__.py.
        __init__.py is therefore the most frequent basename in that cluster and must
        appear as a code-span (`` `__init__.py`=2 ``) somewhere in the Markdown.
        """
        self.assertIn("`__init__.py`=2", self.md)

    def test_markdown_top_parent_dirs_render_as_code_spans(self) -> None:
        """top_parent_dirs entries must appear as code-spans in the rendered Markdown tables.

        The fixture places two files under scripts/docmeta, making it the top parent dir
        for the scripts/** cluster and guaranteeing `` `scripts/docmeta`=2 `` in the output.
        """
        self.assertIn("`scripts/docmeta`=2", self.md)

    def test_markdown_residual_section_before_review_section(self) -> None:
        """Residual section must appear before the 'requiring review' section."""
        idx_residual = self.md.find("## Residual fallback clusters")
        idx_review = self.md.find("## Fallback classified artifacts requiring review")
        self.assertLess(idx_residual, idx_review)

    def test_markdown_residual_section_after_by_matched_pattern_section(self) -> None:
        """Residual section must appear after the 'by matched pattern' section."""
        idx_pattern = self.md.find("## Fallback classified: by matched pattern")
        idx_residual = self.md.find("## Residual fallback clusters")
        self.assertLess(idx_pattern, idx_residual)

    def test_render_markdown_reads_residual_cluster_views_not_residual_clusters(self) -> None:
        """render_markdown() must use residual_cluster_views as sole source of truth.

        Injects a sentinel pattern ("legacy-only/**") into residual_clusters that is
        absent from residual_cluster_views. Verifies the sentinel does NOT appear in
        the rendered Markdown, and that only the patterns from residual_cluster_views
        (risk_first / volume_first) do appear — in the correct subsection order.
        """

        def _cluster(pattern: str, total: int = 1, high: int = 0) -> dict:
            return {
                "matched_pattern": pattern,
                "total": total,
                "high_risk_count": high,
                "top_basenames": {"sentinel.md": 1},
                "top_parent_dirs": {"sentinel": 1},
            }

        def _make_item(path: str, pattern: str) -> dict:
            return {
                "path": path,
                "status": "classified",
                "layer": "docs",
                "kind": "doc",
                "authority": "navigation_surface",
                "lifecycle": "handcrafted",
                "enforcement": [],
                "origin": "handcrafted",
                "matched_patterns": [pattern],
                "catchall_match": True,
            }

        def _subsection(md: str, start_header: str, end_header: str) -> str:
            start = md.find(start_header)
            end = md.find(end_header, start + 1)
            if start == -1:
                return ""
            return md[start:end] if end != -1 else md[start:]

        report = build_report([_make_item("docs/x.md", "docs/**")], [])
        # Override fallback_summary to inject controlled views and a deceptive legacy field.
        report["fallback_summary"]["residual_clusters"] = [
            _cluster("legacy-only/**", total=999, high=999),
        ]
        report["fallback_summary"]["residual_cluster_views"] = {
            "risk_first": [
                _cluster("risk-first-a/**", total=1, high=3),
                _cluster("risk-first-b/**", total=2, high=2),
                _cluster("risk-first-c/**", total=3, high=1),
            ],
            "volume_first": [
                _cluster("volume-first-a/**", total=30, high=0),
                _cluster("volume-first-b/**", total=20, high=0),
                _cluster("volume-first-c/**", total=10, high=0),
            ],
        }

        md = render_markdown(report)

        # Section and subsection headers must be present.
        self.assertIn("## Residual fallback clusters", md)
        self.assertIn("### Risk-first clusters", md)
        self.assertIn("### Volume-first clusters", md)

        # Legacy sentinel must NOT appear — Markdown must not read residual_clusters.
        self.assertNotIn("legacy-only/**", md)

        # Extract subsection texts for order-sensitive assertions.
        risk_section = _subsection(md, "### Risk-first clusters", "### Volume-first clusters")
        volume_section = _subsection(md, "### Volume-first clusters", "## Fallback classified artifacts requiring review")

        # Risk-first section must contain all three risk patterns, in order.
        self.assertIn("risk-first-a/**", risk_section)
        self.assertIn("risk-first-b/**", risk_section)
        self.assertIn("risk-first-c/**", risk_section)
        self.assertLess(risk_section.find("risk-first-a/**"), risk_section.find("risk-first-b/**"))
        self.assertLess(risk_section.find("risk-first-b/**"), risk_section.find("risk-first-c/**"))

        # Volume-first section must contain all three volume patterns, in order.
        self.assertIn("volume-first-a/**", volume_section)
        self.assertIn("volume-first-b/**", volume_section)
        self.assertIn("volume-first-c/**", volume_section)
        self.assertLess(volume_section.find("volume-first-a/**"), volume_section.find("volume-first-b/**"))
        self.assertLess(volume_section.find("volume-first-b/**"), volume_section.find("volume-first-c/**"))

        # Cross-check: every risk pattern must be absent from the volume subsection,
        # and every volume pattern must be absent from the risk subsection.
        for pattern in ("risk-first-a/**", "risk-first-b/**", "risk-first-c/**"):
            self.assertNotIn(pattern, volume_section, f"{pattern!r} must not appear in volume subsection")
        for pattern in ("volume-first-a/**", "volume-first-b/**", "volume-first-c/**"):
            self.assertNotIn(pattern, risk_section, f"{pattern!r} must not appear in risk subsection")


class SelectFallbackPatternTest(unittest.TestCase):
    """Tests for _select_fallback_pattern helper."""

    def test_selects_first_double_glob_pattern(self) -> None:
        self.assertEqual(_select_fallback_pattern(["scripts/**", "other"]), "scripts/**")

    def test_selects_bare_double_glob(self) -> None:
        self.assertEqual(_select_fallback_pattern(["**"]), "**")

    def test_prefers_double_glob_over_non_glob(self) -> None:
        self.assertEqual(_select_fallback_pattern(["exact/path", "experiments/**"]), "experiments/**")

    def test_falls_back_to_first_when_no_double_glob(self) -> None:
        self.assertEqual(_select_fallback_pattern(["*.md", "docs/*"]), "*.md")

    def test_returns_missing_sentinel_for_empty_list(self) -> None:
        self.assertEqual(_select_fallback_pattern([]), "<missing>")


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

    def test_agent_layer_is_high_risk(self) -> None:
        self.assertTrue(_is_high_risk_fallback(self._item("agent", "navigation_surface")))

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
    """Tests for the risk-weighted sorting of fallback review items.

    These tests call the production `fallback_review_sort_key` directly, so
    any change to production sorting will immediately break these tests.
    """

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

    def test_high_risk_before_low_risk(self) -> None:
        items = [
            self._make_item("docs/low.md", True, "docs", "navigation_surface"),
            self._make_item("gov/high.md", True, "governance", "procedure_contract"),
        ]
        report = build_report(items, [])
        fallback_items = [c for c in report["classifications"] if c.get("catchall_match")]
        sorted_items = sorted(fallback_items, key=fallback_review_sort_key)
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
        sorted_items = sorted(fallback_items, key=fallback_review_sort_key)
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

    def test_markdown_contains_by_matched_pattern_section(self) -> None:
        self.assertIn("Fallback classified: by matched pattern", self.md)

    def test_markdown_by_matched_pattern_has_table(self) -> None:
        self.assertIn("| matched_pattern | count | share_of_fallback |", self.md)

    def test_markdown_review_section_has_table(self) -> None:
        self.assertIn("| Path | Layer | Kind | Authority | Risk | Matched pattern |", self.md)


if __name__ == "__main__":
    unittest.main()
