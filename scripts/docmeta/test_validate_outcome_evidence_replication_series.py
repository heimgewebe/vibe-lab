#!/usr/bin/env python3
"""Regression tests for validate_outcome_evidence_replication_series.py.

Tests run validate_series() against file-based fixtures in
  tests/fixtures/outcome_evidence_replication_series/
and against minimal in-memory structures built in temp directories.

Run:
    python3 scripts/docmeta/test_validate_outcome_evidence_replication_series.py
"""

from __future__ import annotations

import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR))

from validate_outcome_evidence_replication_series import (  # noqa: E402
    REQUIRED_RUN_ARTIFACTS,
    _changed_files_has_real_code,
    validate_run,
    validate_series,
)

REPO_ROOT = THIS_DIR.parent.parent
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "outcome_evidence_replication_series"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _w(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip("\n"), encoding="utf-8")


def _make_minimal_run(
    base: Path,
    run_id: str = "run-001",
    outcome: str = "PASS",
    comparability_verdict: str = "not_comparable",
    outcome_upgrade_allowed: bool = False,
    effect_claim_allowed: bool = False,
    promotion_claim_allowed: bool = False,
    task_class: str = "contract_documentation_alignment",
    negative_control: bool = False,
    independence_status: str = "partial",
    comparability_independence_status: str | None = None,
    provenance_level: str = "self_reported",
    run_effect_claim_allowed: bool = False,
    run_promotion_claim_allowed: bool = False,
    measurement_outcome_upgrade_allowed: bool = False,
    changed_files_content: str | None = None,
) -> Path:
    """Create a minimal valid run directory under base/artifacts/<run_id>/."""
    run_dir = base / "artifacts" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    _w(run_dir / "run.yml", f"""
        schema_version: "1.0.0"
        contract: "experiment_run_bundle"
        run:
          id: "{run_id}"
          experiment_path: "experiments/fixture"
          created_at: "2026-05-28T00:00:00Z"
          sequence: 1
        provenance:
          level: "{provenance_level}"
          executor: "test-agent"
        artifacts:
          auditor_output:
            path: "auditor-output.yml"
            contract: "auditor_output"
            canonical: true
          measurement:
            path: "measurement.yml"
            contract: "measurement_run"
            canonical: true
          evidence_pack:
            path: "evidence-pack.yml"
            contract: "run-evidence-pack.v1"
            canonical: true
        verdict:
          outcome: "{outcome}"
          effect_claim_allowed: {"true" if run_effect_claim_allowed else "false"}
          promotion_claim_allowed: {"true" if run_promotion_claim_allowed else "false"}
    """)

    _w(run_dir / "measurement.yml", f"""
        schema_version: "1.0.0"
        contract: "measurement_run"
        run_id: "{run_id}"
        auditor_verdict: "PASS"
        auditor_ref: "auditor-output.yml"
        metrics:
          validation_gap_count:
            value: 0
            evidence_status: "repo_local"
        extensions:
          series: "outcome-evidence-replication-series"
          task_class: "{task_class}"
          independence_status: "{independence_status}"
          outcome_upgrade_allowed: {"true" if measurement_outcome_upgrade_allowed else "false"}
    """)

    _w(run_dir / "auditor-output.yml", f"""
        schema_version: "1.0.0"
        contract: "auditor_output"
        run_id: "{run_id}"
        auditor_date: "2026-05-28"
        auditor:
          name: "fixture-self-audit"
        overall_verdict: "PASS"
        claims: []
    """)

    _w(run_dir / "evidence-pack.yml", f"""
        schema_version: "1.0.0"
        run_id: "{run_id}"
        claims: []
    """)

    _w(run_dir / "comparability.yml", f"""
        schema_version: "1.0.0"
        contract: "run_comparability_assessment"
        run_id: "{run_id}"
        assessed_at: "2026-05-28"
        series: "outcome-evidence-replication-series"
        task_class: "{task_class}"
        outcome_upgrade_allowed: {"true" if outcome_upgrade_allowed else "false"}
        effect_claim_allowed: {"true" if effect_claim_allowed else "false"}
        promotion_claim_allowed: {"true" if promotion_claim_allowed else "false"}
        negative_control: {"true" if negative_control else "false"}
        verdict: {comparability_verdict}
        {"independence_status: " + comparability_independence_status if comparability_independence_status else ""}
    """)

    default_changed = (
        f"A\texperiments/fixture/artifacts/{run_id}/run.yml\n"
    )
    (run_dir / "changed-files.txt").write_text(
        changed_files_content if changed_files_content is not None else default_changed,
        encoding="utf-8",
    )
    (run_dir / "timing.txt").write_text("start: 2026-05-28T00:00:00Z\n", encoding="utf-8")
    (run_dir / "make-validate.txt").write_text("✅ Validation passed.\n", encoding="utf-8")

    return run_dir


# ---------------------------------------------------------------------------
# Unit: _changed_files_has_real_code
# ---------------------------------------------------------------------------

class TestChangedFilesRealCode(unittest.TestCase):
    def _path(self, tmp: Path, content: str) -> Path:
        p = tmp / "changed-files.txt"
        p.write_text(content, encoding="utf-8")
        return p

    def test_scripts_path_counts(self):
        with tempfile.TemporaryDirectory() as d:
            p = self._path(Path(d), "M\tscripts/docmeta/foo.py\n")
            self.assertTrue(_changed_files_has_real_code(p))

    def test_tests_path_counts(self):
        with tempfile.TemporaryDirectory() as d:
            p = self._path(Path(d), "A\ttests/fixtures/bar.yml\n")
            self.assertTrue(_changed_files_has_real_code(p))

    def test_github_workflows_counts(self):
        with tempfile.TemporaryDirectory() as d:
            p = self._path(Path(d), "M\t.github/workflows/validate.yml\n")
            self.assertTrue(_changed_files_has_real_code(p))

    def test_makefile_counts(self):
        with tempfile.TemporaryDirectory() as d:
            p = self._path(Path(d), "M\tMakefile\n")
            self.assertTrue(_changed_files_has_real_code(p))

    def test_experiments_path_does_not_count(self):
        with tempfile.TemporaryDirectory() as d:
            p = self._path(
                Path(d),
                "A\texperiments/2026-05-25_outcome-evidence-replication-series/artifacts/run-001/run.yml\n",
            )
            self.assertFalse(_changed_files_has_real_code(p))

    def test_blank_and_comment_lines_ignored(self):
        with tempfile.TemporaryDirectory() as d:
            p = self._path(Path(d), "# comment\n\nexperiments/foo.yml\n")
            self.assertFalse(_changed_files_has_real_code(p))

    def test_mixed_real_and_experiments_counts(self):
        with tempfile.TemporaryDirectory() as d:
            p = self._path(
                Path(d),
                "A\texperiments/foo.yml\nM\tscripts/docmeta/validator.py\n",
            )
            self.assertTrue(_changed_files_has_real_code(p))


# ---------------------------------------------------------------------------
# Unit: validate_run
# ---------------------------------------------------------------------------

class TestValidateRun(unittest.TestCase):

    def test_valid_run_no_errors(self):
        with tempfile.TemporaryDirectory() as d:
            run_dir = _make_minimal_run(Path(d))
            errors = validate_run(run_dir)
            self.assertEqual(errors, [], f"Unexpected errors: {errors}")

    def test_g1_missing_artifact(self):
        with tempfile.TemporaryDirectory() as d:
            run_dir = _make_minimal_run(Path(d))
            (run_dir / "make-validate.txt").unlink()
            errors = validate_run(run_dir)
            self.assertTrue(
                any("G1" in e and "make-validate.txt" in e for e in errors),
                f"Expected G1 error, got: {errors}",
            )

    def test_g2_not_comparable_with_upgrade(self):
        with tempfile.TemporaryDirectory() as d:
            run_dir = _make_minimal_run(
                Path(d),
                comparability_verdict="not_comparable",
                outcome_upgrade_allowed=True,
            )
            errors = validate_run(run_dir)
            self.assertTrue(
                any("G2" in e for e in errors),
                f"Expected G2 error, got: {errors}",
            )

    def test_g2_not_comparable_with_effect_claim(self):
        with tempfile.TemporaryDirectory() as d:
            run_dir = _make_minimal_run(
                Path(d),
                comparability_verdict="not_comparable",
                effect_claim_allowed=True,
            )
            errors = validate_run(run_dir)
            self.assertTrue(
                any("G2" in e and "effect_claim_allowed" in e for e in errors),
                f"Expected G2 effect error, got: {errors}",
            )

    def test_g3_fake_task_diversity(self):
        with tempfile.TemporaryDirectory() as d:
            run_dir = _make_minimal_run(
                Path(d),
                task_class="validator_test_hardening",
                outcome_upgrade_allowed=True,
                changed_files_content="A\texperiments/foo/run.yml\n",
            )
            errors = validate_run(run_dir)
            self.assertTrue(
                any("G3" in e for e in errors),
                f"Expected G3 error, got: {errors}",
            )

    def test_g3_real_code_paths_allowed(self):
        with tempfile.TemporaryDirectory() as d:
            run_dir = _make_minimal_run(
                Path(d),
                task_class="validator_test_hardening",
                outcome_upgrade_allowed=False,
                changed_files_content=(
                    "A\tscripts/docmeta/validate_foo.py\n"
                    "A\tscripts/docmeta/test_validate_foo.py\n"
                ),
            )
            errors = validate_run(run_dir)
            g3_errors = [e for e in errors if "G3" in e]
            self.assertEqual(g3_errors, [], f"Should not get G3 error with real code paths: {errors}")

    def test_g5_negative_control_wrong_outcome(self):
        with tempfile.TemporaryDirectory() as d:
            run_dir = _make_minimal_run(
                Path(d),
                task_class="negative_control",
                negative_control=True,
                outcome="PASS",
            )
            errors = validate_run(run_dir)
            self.assertTrue(
                any("G5" in e for e in errors),
                f"Expected G5 error, got: {errors}",
            )

    def test_g5_negative_control_correct_outcome(self):
        with tempfile.TemporaryDirectory() as d:
            run_dir = _make_minimal_run(
                Path(d),
                task_class="negative_control",
                negative_control=True,
                outcome="CLAIM_NOT_PROVEN",
            )
            errors = validate_run(run_dir)
            g5_errors = [e for e in errors if "G5" in e]
            self.assertEqual(g5_errors, [], f"Should not get G5 error: {errors}")

    def test_g5_negative_control_missing_outcome(self):
        with tempfile.TemporaryDirectory() as d:
            run_dir = _make_minimal_run(
                Path(d),
                task_class="negative_control",
                negative_control=True,
                outcome="CLAIM_NOT_PROVEN",
            )
            run_path = run_dir / "run.yml"
            run_text = run_path.read_text(encoding="utf-8").replace(
                '  outcome: "CLAIM_NOT_PROVEN"\n', ""
            )
            run_path.write_text(run_text, encoding="utf-8")
            errors = validate_run(run_dir)
            self.assertTrue(
                any("G5" in e for e in errors),
                f"Expected G5 error for missing verdict.outcome, got: {errors}",
            )

    def test_malformed_comparability_yaml_fails(self):
        with tempfile.TemporaryDirectory() as d:
            run_dir = _make_minimal_run(Path(d))
            (run_dir / "comparability.yml").write_text("verdict: [", encoding="utf-8")
            errors = validate_run(run_dir)
            self.assertTrue(
                any("malformed YAML in comparability.yml" in e for e in errors),
                f"Expected malformed comparability.yml error, got: {errors}",
            )

    def test_empty_comparability_yaml_fails(self):
        with tempfile.TemporaryDirectory() as d:
            run_dir = _make_minimal_run(Path(d))
            (run_dir / "comparability.yml").write_text("", encoding="utf-8")
            errors = validate_run(run_dir)
            self.assertTrue(
                any("empty YAML document in comparability.yml" in e for e in errors),
                f"Expected empty comparability.yml error, got: {errors}",
            )

    def test_unknown_verdict_fails(self):
        with tempfile.TemporaryDirectory() as d:
            run_dir = _make_minimal_run(Path(d), comparability_verdict="mystery")
            errors = validate_run(run_dir)
            self.assertTrue(
                any("verdict must be one of" in e for e in errors),
                f"Expected unknown verdict error, got: {errors}",
            )

    def test_g2_not_comparable_with_run_effect_claim(self):
        with tempfile.TemporaryDirectory() as d:
            run_dir = _make_minimal_run(
                Path(d),
                comparability_verdict="not_comparable",
                run_effect_claim_allowed=True,
            )
            errors = validate_run(run_dir)
            self.assertTrue(
                any("G2" in e and "run.yml verdict.effect_claim_allowed" in e for e in errors),
                f"Expected G2 run effect-claim error, got: {errors}",
            )

    def test_outcome_upgrade_allowed_string_is_type_error(self):
        with tempfile.TemporaryDirectory() as d:
            run_dir = _make_minimal_run(Path(d))
            comp_path = run_dir / "comparability.yml"
            comp_text = comp_path.read_text(encoding="utf-8").replace(
                "outcome_upgrade_allowed: false",
                'outcome_upgrade_allowed: "false"',
            )
            comp_path.write_text(comp_text, encoding="utf-8")
            errors = validate_run(run_dir)
            self.assertTrue(
                any("must be a YAML boolean" in e and "outcome_upgrade_allowed" in e for e in errors),
                f"Expected bool type error, got: {errors}",
            )

    def test_g6_self_reported_full_independence_in_comparability(self):
        with tempfile.TemporaryDirectory() as d:
            run_dir = _make_minimal_run(
                Path(d),
                provenance_level="self_reported",
                comparability_independence_status="full_independence",
            )
            errors = validate_run(run_dir)
            self.assertTrue(
                any("G6" in e and "comparability.yml independence_status" in e for e in errors),
                f"Expected G6 comparability independence error, got: {errors}",
            )

    def test_g6_self_reported_full_independence(self):
        with tempfile.TemporaryDirectory() as d:
            run_dir = _make_minimal_run(
                Path(d),
                provenance_level="self_reported",
                independence_status="full_independence",
            )
            errors = validate_run(run_dir)
            self.assertTrue(
                any("G6" in e for e in errors),
                f"Expected G6 error, got: {errors}",
            )

    def test_g6_self_reported_partial_allowed(self):
        with tempfile.TemporaryDirectory() as d:
            run_dir = _make_minimal_run(
                Path(d),
                provenance_level="self_reported",
                independence_status="partial",
            )
            errors = validate_run(run_dir)
            g6_errors = [e for e in errors if "G6" in e]
            self.assertEqual(g6_errors, [], f"Should not get G6 error: {errors}")


# ---------------------------------------------------------------------------
# Unit: validate_series (G4 — premature upgrade)
# ---------------------------------------------------------------------------

class TestValidateSeries(unittest.TestCase):

    def test_valid_series_no_errors(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            _make_minimal_run(base, "run-001", outcome_upgrade_allowed=False)
            errors = validate_series(base)
            self.assertEqual(errors, [], f"Unexpected errors: {errors}")

    def test_g4_premature_upgrade_single_comparable_run(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            _make_minimal_run(
                base,
                "run-001",
                comparability_verdict="comparable",
                outcome_upgrade_allowed=True,
            )
            errors = validate_series(base)
            self.assertTrue(
                any("G4" in e for e in errors),
                f"Expected G4 error, got: {errors}",
            )

    def test_g4_no_error_when_upgrade_false(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            _make_minimal_run(
                base,
                "run-001",
                comparability_verdict="comparable",
                outcome_upgrade_allowed=False,
            )
            errors = validate_series(base)
            g4_errors = [e for e in errors if "G4" in e]
            self.assertEqual(g4_errors, [], f"Should not get G4 error: {errors}")

    def test_unknown_verdict_does_not_count_as_comparable(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            _make_minimal_run(base, "run-001", comparability_verdict="comparable")
            _make_minimal_run(base, "run-002", comparability_verdict="comparable")
            _make_minimal_run(base, "run-003", comparability_verdict="mystery")
            _make_minimal_run(
                base,
                "run-004",
                comparability_verdict="comparable",
                outcome_upgrade_allowed=True,
            )
            errors = validate_series(base)
            self.assertTrue(
                any("verdict must be one of" in e for e in errors),
                f"Expected unknown verdict error, got: {errors}",
            )
            self.assertTrue(
                any("G4" in e and "run-004" in e for e in errors),
                f"Expected G4 error because unknown verdict must not count as comparable, got: {errors}",
            )

    def test_g4_premature_upgrade_via_run_promotion_flag(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            _make_minimal_run(
                base,
                "run-001",
                comparability_verdict="comparable",
                run_promotion_claim_allowed=True,
            )
            errors = validate_series(base)
            self.assertTrue(
                any("G4" in e and "run.yml verdict.promotion_claim_allowed" in e for e in errors),
                f"Expected G4 run promotion error, got: {errors}",
            )

    def test_g7_insufficient_task_classes(self):
        """G7: 4 comparable runs but only 1 task_class + upgrade=true → G7 error"""
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            # Create 4 comparable runs with same task_class
            for i in range(1, 5):
                _make_minimal_run(
                    base,
                    f"run-{i:03d}",
                    comparability_verdict="comparable",
                    task_class="same_task",
                    outcome_upgrade_allowed=(i == 1),  # Set upgrade flag on first run
                    negative_control=False,
                    independence_status="full",  # Enough independence
                )
            # Add one negative control
            _make_minimal_run(
                base,
                "run-005",
                comparability_verdict="comparable",
                task_class="same_task",
                negative_control=True,
                outcome="CLAIM_NOT_PROVEN",
            )
            errors = validate_series(base)
            self.assertTrue(
                any("G7" in e and "distinct task class" in e for e in errors),
                f"Expected G7 task class error, got: {errors}",
            )

    def test_g7_no_negative_control(self):
        """G7: 4 comparable runs but no negative_control → G7 error"""
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            # Create 4 comparable runs with different task_classes but no negative_control
            task_classes = ["task_a", "task_b", "task_c", "task_d"]
            for i, tc in enumerate(task_classes, 1):
                _make_minimal_run(
                    base,
                    f"run-{i:03d}",
                    comparability_verdict="comparable",
                    task_class=tc,
                    outcome_upgrade_allowed=(i == 1),  # Set upgrade flag on first run
                    negative_control=False,
                    independence_status="full",
                )
            errors = validate_series(base)
            self.assertTrue(
                any("G7" in e and "negative_control run" in e for e in errors),
                f"Expected G7 negative control error, got: {errors}",
            )

    def test_g7_insufficient_independence(self):
        """G7: 4 comparable runs with 3+ task_classes but only partial/self_reported independence → G7 error"""
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            # Create 4 comparable runs, first 3 with self_reported+partial (don't count),
            # 4th with external+independent_review (counts as 1). Need 2 for G7.
            task_classes = ["task_a", "task_b", "task_c", "task_d"]
            for i, tc in enumerate(task_classes, 1):
                _make_minimal_run(
                    base,
                    f"run-{i:03d}",
                    comparability_verdict="comparable",
                    task_class=tc,
                    outcome_upgrade_allowed=(i == 1),  # Set upgrade flag on first run
                    negative_control=False,
                    provenance_level="self_reported" if i < 4 else "external",
                    independence_status="partial" if i < 4 else "independent_review",
                )
            # Add negative control
            _make_minimal_run(
                base,
                "run-005",
                comparability_verdict="comparable",
                task_class="task_e",
                negative_control=True,
                outcome="CLAIM_NOT_PROVEN",
            )
            errors = validate_series(base)
            self.assertTrue(
                any("G7" in e and "independent review" in e for e in errors),
                f"Expected G7 independence error, got: {errors}",
            )


    def test_g7_audit_local_full_by_model_family_does_not_count_for_series_gate(self):
        """G7: audit-local full_by_model_family_for_this_audit must not count as series full independence"""
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)

            _make_minimal_run(
                base,
                "run-001",
                comparability_verdict="comparable",
                task_class="task_a",
                outcome_upgrade_allowed=True,
                provenance_level="external",
                independence_status="independent_review",
            )
            _make_minimal_run(
                base,
                "run-002",
                comparability_verdict="comparable",
                task_class="task_b",
                provenance_level="external",
                independence_status="independent_review",
            )
            _make_minimal_run(
                base,
                "run-003",
                comparability_verdict="comparable",
                task_class="task_c",
                provenance_level="external",
                independence_status="full_by_model_family_for_this_audit",
            )
            _make_minimal_run(
                base,
                "run-004",
                comparability_verdict="comparable",
                task_class="task_d",
                provenance_level="external",
                independence_status="partial",
            )
            _make_minimal_run(
                base,
                "run-005",
                comparability_verdict="comparable",
                task_class="negative_control_task",
                negative_control=True,
                outcome="CLAIM_NOT_PROVEN",
                provenance_level="external",
                independence_status="partial",
            )

            errors = validate_series(base)
            self.assertTrue(
                any("G7" in e and "full_independence" in e for e in errors),
                f"Expected G7 full independence error for audit-local independence value, got: {errors}",
            )

    def test_g7_complete_gate_passes(self):
        """G7: Full playbook criteria met with upgrade=true -> no errors"""
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)

            _make_minimal_run(
                base,
                "run-001",
                comparability_verdict="comparable",
                task_class="task_a",
                outcome_upgrade_allowed=True,
                provenance_level="external",
                independence_status="full_independence",
            )
            _make_minimal_run(
                base,
                "run-002",
                comparability_verdict="comparable",
                task_class="task_b",
                provenance_level="external",
                independence_status="independent_review",
            )
            _make_minimal_run(
                base,
                "run-003",
                comparability_verdict="comparable",
                task_class="task_c",
                provenance_level="external",
                independence_status="partial",
            )
            _make_minimal_run(
                base,
                "run-004",
                comparability_verdict="comparable",
                task_class="task_d",
                provenance_level="external",
                independence_status="partial",
            )
            _make_minimal_run(
                base,
                "run-005",
                comparability_verdict="comparable",
                task_class="negative_control_task",
                negative_control=True,
                outcome="CLAIM_NOT_PROVEN",
                provenance_level="external",
                independence_status="partial",
            )

            errors = validate_series(base)
            self.assertEqual(errors, [], f"Complete gate fixture should produce no errors: {errors}")

    def test_g7_fake_task_diversity_filtered(self):
        """G7: validator_test_hardening without real code changes should not count toward task diversity"""
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            # Create 4 comparable runs:
            # - run-001: test_task_a, comparable, upgrade=true
            # - run-002: test_task_b, comparable
            # - run-003: validator_test_hardening (no real code changes), comparable
            # - run-004: validator_test_hardening (no real code changes), comparable
            # Distinct task classes WITHOUT filtering: 3 (test_task_a, test_task_b, validator_test_hardening)
            # Distinct task classes WITH filtering: 2 (test_task_a, test_task_b) → G7 fails
            
            _make_minimal_run(
                base,
                "run-001",
                comparability_verdict="comparable",
                task_class="test_task_a",
                outcome_upgrade_allowed=True,  # Set upgrade flag
                independence_status="full",
                provenance_level="external",
            )
            _make_minimal_run(
                base,
                "run-002",
                comparability_verdict="comparable",
                task_class="test_task_b",
                independence_status="full",
                provenance_level="external",
            )
            # Two validator_test_hardening runs with no real code changes (only experiments/fixture changes)
            _make_minimal_run(
                base,
                "run-003",
                comparability_verdict="comparable",
                task_class="validator_test_hardening",
                independence_status="independent_review",
                provenance_level="external",
                changed_files_content="A\texperiments/fixture/artifacts/run-003/run.yml\n",
            )
            _make_minimal_run(
                base,
                "run-004",
                comparability_verdict="comparable",
                task_class="validator_test_hardening",
                independence_status="independent_review",
                provenance_level="external",
                changed_files_content="M\texperiments/fixture/artifacts/run-004/comparability.yml\n",
            )
            # Add negative control with a task class that already exists to not increase diversity
            _make_minimal_run(
                base,
                "run-005",
                comparability_verdict="not_comparable",  # Not comparable, so doesn't count in G7 diversity
                task_class="test_task_a",  # Same task_class as run-001, doesn't add diversity
                negative_control=True,
                outcome="CLAIM_NOT_PROVEN",
            )
            errors = validate_series(base)
            self.assertTrue(
                any("G7" in e and "distinct task class(es)" in e for e in errors),
                f"Expected G7 task diversity error, got: {errors}",
            )

    def test_g7_fake_task_diversity_with_real_code_passes(self):
        """G7: validator_test_hardening WITH real code changes should count toward task diversity"""
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            # Create 4 comparable runs:
            # - run-001: test_task_a
            # - run-002: test_task_b
            # - run-003: validator_test_hardening (with real code changes in scripts/)
            # - run-004: validator_test_hardening (with real code changes in tests/)
            # Total distinct: 3 (test_task_a, test_task_b, validator_test_hardening) → G7 should pass
            
            _make_minimal_run(
                base,
                "run-001",
                comparability_verdict="comparable",
                task_class="test_task_a",
                outcome_upgrade_allowed=True,  # Set upgrade flag
                independence_status="full",
                provenance_level="external",
            )
            _make_minimal_run(
                base,
                "run-002",
                comparability_verdict="comparable",
                task_class="test_task_b",
                independence_status="full",
                provenance_level="external",
            )
            # validator_test_hardening with real code changes (scripts/)
            _make_minimal_run(
                base,
                "run-003",
                comparability_verdict="comparable",
                task_class="validator_test_hardening",
                independence_status="independent_review",
                provenance_level="external",
                changed_files_content="A\tscripts/docmeta/validator_test.py\nM\texperiments/fixture/artifacts/run-003/run.yml\n",
            )
            # validator_test_hardening with real code changes (tests/)
            _make_minimal_run(
                base,
                "run-004",
                comparability_verdict="comparable",
                task_class="validator_test_hardening",
                independence_status="independent_review",
                provenance_level="external",
                changed_files_content="M\ttests/fixtures/test_data.yml\n",
            )
            # Add negative control
            _make_minimal_run(
                base,
                "run-005",
                comparability_verdict="comparable",
                task_class="task_control",
                negative_control=True,
                outcome="CLAIM_NOT_PROVEN",
            )
            errors = validate_series(base)
            g7_errors = [e for e in errors if "G7" in e]
            self.assertEqual(g7_errors, [], f"Should not get G7 error with real code changes: {errors}")


    def test_no_artifacts_dir_returns_error(self):
        with tempfile.TemporaryDirectory() as d:
            errors = validate_series(Path(d))
            self.assertTrue(len(errors) == 1 and "no artifacts/" in errors[0])

    def test_empty_artifacts_dir_ok(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "artifacts").mkdir()
            errors = validate_series(Path(d))
            self.assertEqual(errors, [])


# ---------------------------------------------------------------------------
# File-based fixture tests
# ---------------------------------------------------------------------------

class TestFileFixtures(unittest.TestCase):

    def test_valid_fixture_passes(self):
        series_dir = FIXTURE_ROOT / "valid"
        errors = validate_series(series_dir)
        self.assertEqual(errors, [], f"Valid fixture should produce no errors: {errors}")

    def test_missing_artifact_fixture_fails(self):
        series_dir = FIXTURE_ROOT / "invalid" / "missing-artifact"
        errors = validate_series(series_dir)
        self.assertTrue(
            any("G1" in e and "make-validate.txt" in e for e in errors),
            f"Expected G1/make-validate.txt error, got: {errors}",
        )

    def test_not_comparable_upgrades_fails(self):
        series_dir = FIXTURE_ROOT / "invalid" / "not-comparable-upgrades"
        errors = validate_series(series_dir)
        self.assertTrue(
            any("G2" in e for e in errors),
            f"Expected G2 error, got: {errors}",
        )

    def test_fake_task_diversity_fails(self):
        series_dir = FIXTURE_ROOT / "invalid" / "fake-task-diversity"
        errors = validate_series(series_dir)
        self.assertTrue(
            any("G3" in e for e in errors),
            f"Expected G3 error, got: {errors}",
        )

    def test_premature_upgrade_fails(self):
        series_dir = FIXTURE_ROOT / "invalid" / "premature-upgrade"
        errors = validate_series(series_dir)
        self.assertTrue(
            any("G4" in e for e in errors),
            f"Expected G4 error, got: {errors}",
        )

    def test_wrong_negative_control_fails(self):
        series_dir = FIXTURE_ROOT / "invalid" / "wrong-negative-control"
        errors = validate_series(series_dir)
        self.assertTrue(
            any("G5" in e for e in errors),
            f"Expected G5 error, got: {errors}",
        )

    def test_self_reported_full_independence_fails(self):
        series_dir = FIXTURE_ROOT / "invalid" / "self-reported-full-independence"
        errors = validate_series(series_dir)
        self.assertTrue(
            any("G6" in e for e in errors),
            f"Expected G6 error, got: {errors}",
        )

    def test_all_invalid_fixtures_have_errors(self):
        invalid_dir = FIXTURE_ROOT / "invalid"
        for case_dir in sorted(invalid_dir.iterdir()):
            if not case_dir.is_dir():
                continue
            with self.subTest(case=case_dir.name):
                errors = validate_series(case_dir)
                self.assertGreater(
                    len(errors), 0,
                    f"Fixture {case_dir.name} should produce at least one error",
                )


if __name__ == "__main__":
    unittest.main()
