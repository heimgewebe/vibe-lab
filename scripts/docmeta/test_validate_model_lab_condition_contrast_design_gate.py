#!/usr/bin/env python3
"""Regression tests for model-lab-condition-contrast-design-gate validation."""

from __future__ import annotations

import json
import runpy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
VALIDATOR_PATH = (
    REPO_ROOT
    / "scripts"
    / "docmeta"
    / "validate_model_lab_condition_contrast_design_gate.py"
)
SCHEMA_PATH = (
    REPO_ROOT / "schemas" / "model-lab-condition-contrast-design-gate.v1.schema.json"
)
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "model_lab_condition_contrast_design_gate"
EV = "tests/fixtures/model_lab_condition_contrast_design_gate/_evidence"
REAL_ARTIFACT = (
    REPO_ROOT
    / "experiments"
    / "2026-05-31_model-lab-replication-series"
    / "results"
    / "condition-contrast-design-gate.yml"
)

VALID_FIXTURES = [
    "valid/basic.yml",
]

# Each invalid fixture must report at least the listed semantic rule (the value
# below). Some fixtures may co-report additional rules; the test only asserts that
# the listed rule is present, not that it is isolated. Pure-form (schema const /
# enum / required) violations are covered by the mutation tests below, not by full
# fixtures.
INVALID_FIXTURES = {
    "invalid/missing-triage-source.yml": "CONTRAST_GATE_REQUIRES_SINGLE_TRIAGE_SOURCE",
    "invalid/multiple-triage-sources.yml": "CONTRAST_GATE_REQUIRES_SINGLE_TRIAGE_SOURCE",
    "invalid/source-wrong-series.yml": "CONTRAST_GATE_REQUIRES_MATCHING_SOURCE_IDENTITY",
    "invalid/triage-wrong-task.yml": "CONTRAST_GATE_REQUIRES_TRIAGE_RECOMMENDATION",
    "invalid/triage-wrong-target-blocker.yml": "CONTRAST_GATE_REQUIRES_TRIAGE_RECOMMENDATION",
    "invalid/readiness-not-blocked.yml": "CONTRAST_GATE_REQUIRES_BLOCKED_READINESS",
    "invalid/readiness-assessment-allowed.yml": "CONTRAST_GATE_REQUIRES_BLOCKED_READINESS",
    "invalid/readiness-comparison-ready.yml": "CONTRAST_GATE_REQUIRES_BLOCKED_READINESS",
    "invalid/target-blocker-closed.yml": "CONTRAST_GATE_REQUIRES_OPEN_TARGET_BLOCKER",
    "invalid/missing-invariant-dimensions.yml": "CONTRAST_GATE_REQUIRES_COMPLETE_CRITERIA",
    "invalid/duplicate-semantic-id.yml": "CONTRAST_GATE_REQUIRES_UNIQUE_SEMANTIC_IDS",
    "invalid/confounder-control-incomplete.yml": "CONTRAST_GATE_REQUIRES_COMPLETE_CONFOUNDER_CONTROLS",
    "invalid/mandatory-non-claim-missing.yml": "CONTRAST_GATE_REQUIRES_MANDATORY_NON_CLAIMS",
    "invalid/source-path-escape.yml": "CONTRAST_GATE_REQUIRES_SAFE_EXISTING_SOURCE_PATHS",
    "invalid/source-file-missing.yml": "CONTRAST_GATE_REQUIRES_SAFE_EXISTING_SOURCE_PATHS",
}

# (label, mutation, expected instance_path) — each turns a fixed v1 value into a
# disallowed one and must surface as a schema error (exit 2) at a stable path. The
# exact jsonschema prose is intentionally not asserted.
SCHEMA_CONST_MUTATIONS = [
    (
        "target_blocker",
        lambda d: d.update(target_blocker="external_independence_not_attested"),
        "target_blocker",
    ),
    ("gate_status", lambda d: d.update(gate_status="blocked"), "gate_status"),
    ("run_004_design_allowed", lambda d: d.update(run_004_design_allowed=False), "run_004_design_allowed"),
    ("run_004_execution_allowed", lambda d: d.update(run_004_execution_allowed=True), "run_004_execution_allowed"),
    ("result_assessment_allowed_after_gate", lambda d: d.update(result_assessment_allowed_after_gate=True), "result_assessment_allowed_after_gate"),
    ("comparison_ready_after_gate", lambda d: d.update(comparison_ready_after_gate=True), "comparison_ready_after_gate"),
    ("decision.status", lambda d: d["decision"].update(status="blocked"), "decision.status"),
    ("decision.next_step", lambda d: d["decision"].update(next_step="run_004_execution_may_begin"), "decision.next_step"),
    ("primary_intervention_axis_required", lambda d: d["contrast_policy"].update(primary_intervention_axis_required=False), "contrast_policy.primary_intervention_axis_required"),
    ("required_primary_intervention_axis_count", lambda d: d["contrast_policy"].update(required_primary_intervention_axis_count=2), "contrast_policy.required_primary_intervention_axis_count"),
    ("primary_axis_selection_phase", lambda d: d["contrast_policy"].update(primary_axis_selection_phase="post_execution"), "contrast_policy.primary_axis_selection_phase"),
    ("materiality_evidence_required", lambda d: d["contrast_policy"].update(materiality_evidence_required=False), "contrast_policy.materiality_evidence_required"),
    ("evidence_required_missing", lambda d: d["materiality_criteria"][0].pop("evidence_required"), "materiality_criteria.0"),
    ("unknown_source_kind", lambda d: d["source_evidence"][0].update(kind="bogus_kind"), "source_evidence.0.kind"),
    ("unknown_control_requirement", lambda d: d["controlled_secondary_dimensions"][0].update(control_requirement="bogus"), "controlled_secondary_dimensions.0.control_requirement"),
]

# (label, foundational kind, replacement path, expected diagnostic) — each points a
# declared foundational source at a non-mapping/non-file target; the gate must exit 1
# with READABLE_FOUNDATIONAL_SOURCES and the matching diagnostic.
READABILITY_MUTATIONS = [
    ("triage_wrong_extension", "next_blocker_triage", f"{EV}/foundation-not-yaml.txt", "is not a .yml/.yaml file"),
    ("triage_invalid_yaml", "next_blocker_triage", f"{EV}/foundation-invalid.yml", "is not valid YAML"),
    ("triage_not_mapping", "next_blocker_triage", f"{EV}/foundation-list.yml", "is not a YAML mapping"),
    ("triage_directory", "next_blocker_triage", f"{EV}/source-directory", "is not a regular file"),
    ("readiness_wrong_extension", "readiness_gate", f"{EV}/foundation-not-yaml.txt", "is not a .yml/.yaml file"),
    ("readiness_invalid_yaml", "readiness_gate", f"{EV}/foundation-invalid.yml", "is not valid YAML"),
    ("readiness_not_mapping", "readiness_gate", f"{EV}/foundation-list.yml", "is not a YAML mapping"),
    ("readiness_directory", "readiness_gate", f"{EV}/source-directory", "is not a regular file"),
]


class ModelLabConditionContrastDesignGateValidatorTests(unittest.TestCase):
    def run_validator(self, *paths: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VALIDATOR_PATH), *[str(path) for path in paths]],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def assert_exit_code(
        self, completed: subprocess.CompletedProcess[str], expected: int
    ) -> None:
        self.assertEqual(expected, completed.returncode, completed.stdout + completed.stderr)

    def _basic_data(self) -> dict:
        return yaml.safe_load((FIXTURE_ROOT / "valid/basic.yml").read_text(encoding="utf-8"))

    def _run_on_data(self, data: dict) -> subprocess.CompletedProcess[str]:
        # Repo-relative source_evidence paths resolve against the repo root, so the
        # mutated file may live in a temp dir.
        with tempfile.TemporaryDirectory() as temp_dir:
            mutated = Path(temp_dir) / "mutated.yml"
            mutated.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
            return self.run_validator(mutated)

    def _set_source_path(self, data: dict, kind: str, new_path: str) -> None:
        for entry in data["source_evidence"]:
            if entry.get("kind") == kind:
                entry["path"] = new_path
                return
        raise AssertionError(f"no source_evidence of kind {kind!r}")

    # --- baseline guarantees -------------------------------------------------

    def test_valid_fixtures_exit_zero(self) -> None:
        for rel_path in VALID_FIXTURES:
            with self.subTest(rel_path=rel_path):
                self.assert_exit_code(self.run_validator(FIXTURE_ROOT / rel_path), 0)

    def test_real_series_artifact_exits_zero(self) -> None:
        self.assertTrue(REAL_ARTIFACT.is_file(), f"missing real artifact: {REAL_ARTIFACT}")
        self.assert_exit_code(self.run_validator(REAL_ARTIFACT), 0)

    def test_invalid_fixtures_exit_one_with_rule_ids(self) -> None:
        for rel_path, rule_id in INVALID_FIXTURES.items():
            with self.subTest(rel_path=rel_path):
                completed = self.run_validator(FIXTURE_ROOT / rel_path)
                self.assert_exit_code(completed, 1)
                self.assertIn(rule_id, completed.stdout)

    # --- schema (form) violations via mutation -------------------------------

    def test_schema_constant_mutations_are_schema_errors(self) -> None:
        for label, mutate, instance_path in SCHEMA_CONST_MUTATIONS:
            with self.subTest(case=label):
                data = self._basic_data()
                mutate(data)
                completed = self._run_on_data(data)
                self.assert_exit_code(completed, 2)
                self.assertIn(f"instance_path={instance_path}", completed.stdout)

    def test_schema_violation_exits_two(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            bad = Path(temp_dir) / "schema-invalid.yml"
            # Missing required fields (series_id, source_evidence, ...).
            bad.write_text(
                'schema_version: "v1"\n'
                'artifact_type: "model_lab_condition_contrast_design_gate"\n',
                encoding="utf-8",
            )
            self.assert_exit_code(self.run_validator(bad), 2)

    def test_wrong_schema_version_exits_two(self) -> None:
        data = self._basic_data()
        data["schema_version"] = "1.0.0"
        self.assert_exit_code(self._run_on_data(data), 2)

    def test_parse_error_exits_two(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            bad = Path(temp_dir) / "bad.yml"
            bad.write_text("source_evidence: [\n", encoding="utf-8")
            self.assert_exit_code(self.run_validator(bad), 2)

    # --- foundational source cardinality + readability -----------------------

    def test_readiness_missing_is_single_readiness(self) -> None:
        data = self._basic_data()
        data["source_evidence"] = [
            e for e in data["source_evidence"] if e.get("kind") != "readiness_gate"
        ]
        completed = self._run_on_data(data)
        self.assert_exit_code(completed, 1)
        self.assertIn("CONTRAST_GATE_REQUIRES_SINGLE_READINESS_SOURCE", completed.stdout)

    def test_readiness_multiple_is_single_readiness(self) -> None:
        data = self._basic_data()
        data["source_evidence"].append(
            {"path": f"{EV}/readiness-alt.yml", "kind": "readiness_gate"}
        )
        completed = self._run_on_data(data)
        self.assert_exit_code(completed, 1)
        self.assertIn("CONTRAST_GATE_REQUIRES_SINGLE_READINESS_SOURCE", completed.stdout)

    def test_unreadable_foundational_sources_are_readability_errors(self) -> None:
        for label, kind, new_path, expected_message in READABILITY_MUTATIONS:
            with self.subTest(case=label):
                data = self._basic_data()
                self._set_source_path(data, kind, new_path)
                completed = self._run_on_data(data)
                self.assert_exit_code(completed, 1)
                self.assertIn(
                    "CONTRAST_GATE_REQUIRES_READABLE_FOUNDATIONAL_SOURCES", completed.stdout
                )
                self.assertIn(expected_message, completed.stdout)
                self.assertNotIn("Traceback", completed.stdout + completed.stderr)

    def test_context_source_directory_is_unsafe_path(self) -> None:
        data = self._basic_data()
        self._set_source_path(data, "assessment_context", f"{EV}/source-directory")
        completed = self._run_on_data(data)
        self.assert_exit_code(completed, 1)
        self.assertIn("CONTRAST_GATE_REQUIRES_SAFE_EXISTING_SOURCE_PATHS", completed.stdout)

    def test_invalid_utf8_foundational_source_is_readability_error(self) -> None:
        # Create the invalid-UTF-8 source inside the repo fixture tree (so its
        # repo-relative path resolves) and remove it immediately after the run.
        evidence_dir = FIXTURE_ROOT / "_evidence"
        with tempfile.TemporaryDirectory(dir=evidence_dir) as temp_dir:
            invalid_source = Path(temp_dir) / "invalid-utf8.yml"
            invalid_source.write_bytes(b"\xff\xfe\xfa")
            data = self._basic_data()
            self._set_source_path(
                data,
                "next_blocker_triage",
                invalid_source.relative_to(REPO_ROOT).as_posix(),
            )
            completed = self._run_on_data(data)
        self.assert_exit_code(completed, 1)
        self.assertIn("CONTRAST_GATE_REQUIRES_READABLE_FOUNDATIONAL_SOURCES", completed.stdout)
        self.assertIn("could not be read as UTF-8 text", completed.stdout)
        self.assertNotIn("Traceback", completed.stdout + completed.stderr)

    def test_invalid_utf8_gate_exits_two_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            invalid_gate = Path(temp_dir) / "invalid-utf8.yml"
            invalid_gate.write_bytes(b"\xff\xfe\xfa")
            completed = self.run_validator(invalid_gate)
        self.assert_exit_code(completed, 2)
        self.assertIn("not valid UTF-8", completed.stdout)
        self.assertNotIn("Traceback", completed.stdout + completed.stderr)

    def test_invalid_source_path_forms_are_schema_errors(self) -> None:
        cases = (
            ("blank", "   "),
            ("leading_whitespace", " tests/example.yml"),
            ("trailing_whitespace", "tests/example.yml "),
            ("nul", "a\x00b"),
            ("tab", "a\tb"),
            ("line_feed", "a\nb"),
            ("carriage_return", "a\rb"),
            ("delete", "a\x7fb"),
            ("lone_surrogate", "a\ud800b"),
        )
        for label, value in cases:
            with self.subTest(case=label):
                data = self._basic_data()
                data["source_evidence"][2]["path"] = value
                completed = self._run_on_data(data)
                self.assert_exit_code(completed, 2)
                self.assertIn("instance_path=source_evidence.2.path", completed.stdout)
                self.assertNotIn("Traceback", completed.stdout + completed.stderr)

    def test_resolver_rejects_control_and_surrogate_codepoints(self) -> None:
        # The resolver must stay fail-closed (ESCAPE) on these values even without
        # the upstream schema check — NUL/surrogate otherwise crash pathlib.
        module = runpy.run_path(
            str(VALIDATOR_PATH), run_name="condition_contrast_validator_module"
        )
        resolve = module["resolve_repo_relative_path"]
        for value in ("a\x00b", "a\tb", "a\nb", "a\rb", "a\x7fb", "a\ud800b"):
            with self.subTest(value=ascii(value)):
                resolved, code = resolve(value, REPO_ROOT, must_exist=True)
                self.assertIsNone(resolved)
                self.assertEqual("ESCAPE", code)

    def test_valid_unicode_source_paths_pass_schema_form(self) -> None:
        # Guard against over-rejection: non-ASCII path characters stay valid form.
        validator = Draft202012Validator(json.loads(SCHEMA_PATH.read_text(encoding="utf-8")))
        for value in ("äöü/datei.yml", "日本語/file.yml", "dir/file name.yml"):
            with self.subTest(value=value):
                data = self._basic_data()
                data["source_evidence"][2]["path"] = value
                self.assertEqual([], list(validator.iter_errors(data)))

    def test_weak_condition_contrast_resolution_non_claim_is_required(self) -> None:
        data = self._basic_data()
        data["does_not_establish"].remove("weak_condition_contrast_resolved")
        completed = self._run_on_data(data)
        self.assert_exit_code(completed, 1)
        self.assertIn("CONTRAST_GATE_REQUIRES_MANDATORY_NON_CLAIMS", completed.stdout)
        self.assertIn("weak_condition_contrast_resolved", completed.stdout)

    def test_source_resolution_passes_raw_path_to_resolver(self) -> None:
        # Defense-in-depth: the caller hands the resolver the unmodified raw path, so an
        # edge control character is rejected even without upstream schema validation.
        module = runpy.run_path(
            str(VALIDATOR_PATH), run_name="condition_contrast_validator_module"
        )
        resolve_entries = module["resolve_source_evidence_entries"]
        data = self._basic_data()
        data["source_evidence"][2]["path"] = (
            "\ttests/fixtures/model_lab_condition_contrast_design_gate/"
            "_evidence/assessment-context.txt"
        )
        resolutions = resolve_entries(data, REPO_ROOT)
        context_resolution = resolutions[2]
        self.assertEqual("ESCAPE", context_resolution.code)
        self.assertIsNone(context_resolution.resolved)

    # --- mandatory sets ------------------------------------------------------

    def test_missing_controlled_secondary_dimension_is_incomplete(self) -> None:
        data = self._basic_data()
        data["controlled_secondary_dimensions"] = [
            x for x in data["controlled_secondary_dimensions"] if x.get("id") != "test_harness"
        ]
        completed = self._run_on_data(data)
        self.assert_exit_code(completed, 1)
        self.assertIn("CONTRAST_GATE_REQUIRES_COMPLETE_CRITERIA", completed.stdout)

    def test_confounder_wrong_effect_is_incomplete(self) -> None:
        data = self._basic_data()
        for control in data["confounder_controls"]:
            if control.get("id") == "multi_axis_drift":
                control["effect_if_uncontrolled"] = "must_be_reported"
        completed = self._run_on_data(data)
        self.assert_exit_code(completed, 1)
        self.assertIn("CONTRAST_GATE_REQUIRES_COMPLETE_CONFOUNDER_CONTROLS", completed.stdout)

    # --- diagnostics ---------------------------------------------------------

    def test_blocked_readiness_diagnostic_names_all_required_signals(self) -> None:
        completed = self.run_validator(
            FIXTURE_ROOT / "invalid/readiness-comparison-ready.yml"
        )
        self.assert_exit_code(completed, 1)
        self.assertIn("CONTRAST_GATE_REQUIRES_BLOCKED_READINESS", completed.stdout)
        self.assertIn("readiness_status=blocked", completed.stdout)
        self.assertIn("result_assessment_allowed=false", completed.stdout)
        self.assertIn("comparison_ready=false", completed.stdout)
        self.assertIn("missing fields do not count as false", completed.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
