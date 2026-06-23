#!/usr/bin/env python3
"""Regression tests for model-lab-condition-design validation."""

from __future__ import annotations

import json
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
VALIDATOR_PATH = REPO_ROOT / "scripts" / "docmeta" / "validate_model_lab_condition_design.py"
SCHEMA_PATH = REPO_ROOT / "schemas" / "model-lab-condition-design.v1.schema.json"
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "model_lab_condition_design"
EV = "tests/fixtures/model_lab_condition_design/_evidence"
REAL_ARTIFACT = (
    REPO_ROOT
    / "experiments"
    / "2026-05-31_model-lab-replication-series"
    / "artifacts"
    / "run-004-condition-contrast-design"
    / "condition-design.yml"
)

VALID_FIXTURES = [
    "valid/basic.yml",
]

# Each invalid fixture must report at least the listed semantic rule. Some fixtures may
# co-report additional rules (e.g. an unshared protocol ref also trips the "only primary
# axis may differ" rule); the test only asserts that the listed rule is present. Pure-form
# (schema const / enum / required) violations are covered by the mutation tests below.
INVALID_FIXTURES = {
    "invalid/missing-gate-source.yml": "CONDITION_DESIGN_REQUIRES_SINGLE_GATE_SOURCE",
    "invalid/multiple-gate-sources.yml": "CONDITION_DESIGN_REQUIRES_SINGLE_GATE_SOURCE",
    "invalid/source-wrong-series.yml": "CONDITION_DESIGN_REQUIRES_MATCHING_SOURCE_IDENTITY",
    "invalid/gate-allows-execution.yml": "CONDITION_DESIGN_REQUIRES_GATE_AUTHORIZES_DESIGN",
    "invalid/gate-result-assessment-allowed.yml": "CONDITION_DESIGN_REQUIRES_BLOCKED_READINESS",
    "invalid/readiness-not-blocked.yml": "CONDITION_DESIGN_REQUIRES_BLOCKED_READINESS",
    "invalid/target-blocker-closed.yml": "CONDITION_DESIGN_REQUIRES_OPEN_TARGET_BLOCKER",
    "invalid/duplicate-arm-role.yml": "CONDITION_DESIGN_REQUIRES_EXACTLY_TWO_ARMS",
    "invalid/arms-same-workflow-protocol.yml": "CONDITION_DESIGN_REQUIRES_SINGLE_PRIMARY_AXIS",
    "invalid/cosmetic-contrast.yml": "CONDITION_DESIGN_REQUIRES_MATERIAL_CONTRAST",
    "invalid/second-axis-difference.yml": "CONDITION_DESIGN_REQUIRES_ONLY_PRIMARY_AXIS_DIFFERENCE",
    "invalid/unshared-verification.yml": "CONDITION_DESIGN_REQUIRES_SHARED_VERIFICATION",
    "invalid/unshared-measurement.yml": "CONDITION_DESIGN_REQUIRES_SHARED_MEASUREMENT",
    "invalid/unshared-intervention.yml": "CONDITION_DESIGN_REQUIRES_SHARED_INTERVENTION_RULES",
    "invalid/missing-controlled-dimension.yml": "CONDITION_DESIGN_REQUIRES_COMPLETE_CONTROL_BINDINGS",
    "invalid/confounder-incomplete.yml": "CONDITION_DESIGN_REQUIRES_COMPLETE_CONFOUNDER_CONTROLS",
    "invalid/duplicate-semantic-id.yml": "CONDITION_DESIGN_REQUIRES_UNIQUE_SEMANTIC_IDS",
    "invalid/mandatory-non-claim-missing.yml": "CONDITION_DESIGN_REQUIRES_MANDATORY_NON_CLAIMS",
    "invalid/forbidden-selection-non-claim.yml": "CONDITION_DESIGN_REQUIRES_MANDATORY_NON_CLAIMS",
    "invalid/freeze-hash-mismatch.yml": "CONDITION_DESIGN_REQUIRES_VALID_FREEZE",
    "invalid/freeze-self-hash.yml": "CONDITION_DESIGN_REQUIRES_VALID_FREEZE",
    "invalid/source-path-escape.yml": "CONDITION_DESIGN_REQUIRES_SAFE_EXISTING_PATHS",
    "invalid/source-file-missing.yml": "CONDITION_DESIGN_REQUIRES_SAFE_EXISTING_PATHS",
}

# (label, mutation, expected instance_path) — each turns a fixed v1 value into a
# disallowed one and must surface as a schema error (exit 2) at a stable path. The exact
# jsonschema prose is intentionally not asserted. The wrong-primary-axis case lives here
# (primary_intervention_axis.id is const), mirroring how the neighbour gate covers its
# const target_blocker as a schema mutation.
SCHEMA_CONST_MUTATIONS = [
    ("schema_version", lambda d: d.update(schema_version="1.0.0"), "schema_version"),
    ("artifact_type", lambda d: d.update(artifact_type="bogus"), "artifact_type"),
    ("design_status", lambda d: d.update(design_status="draft"), "design_status"),
    ("target_blocker", lambda d: d.update(target_blocker="external_independence_not_attested"), "target_blocker"),
    ("target_blocker_status_after_design", lambda d: d.update(target_blocker_status_after_design="resolved"), "target_blocker_status_after_design"),
    ("run_004_execution_allowed", lambda d: d.update(run_004_execution_allowed=True), "run_004_execution_allowed"),
    ("result_assessment_allowed_after_design", lambda d: d.update(result_assessment_allowed_after_design=True), "result_assessment_allowed_after_design"),
    ("comparison_ready_after_design", lambda d: d.update(comparison_ready_after_design=True), "comparison_ready_after_design"),
    ("primary_axis_id", lambda d: d["primary_intervention_axis"].update(id="tool_and_agent_mode"), "primary_intervention_axis.id"),
    ("primary_axis_selection_status", lambda d: d["primary_intervention_axis"].update(selection_status="pending"), "primary_intervention_axis.selection_status"),
    ("required_axis_count", lambda d: d["primary_intervention_axis"].update(required_axis_count=2), "primary_intervention_axis.required_axis_count"),
    ("frozen_before_execution", lambda d: d["freeze"].update(frozen_before_execution=False), "freeze.frozen_before_execution"),
    ("decision_status", lambda d: d["decision"].update(status="draft"), "decision.status"),
    ("decision_next_step", lambda d: d["decision"].update(next_step="run_004_execution_may_begin"), "decision.next_step"),
    ("unknown_arm_role", lambda d: d["arms"][0].update(role="placebo"), "arms.0.role"),
    ("same_value_required_false", lambda d: d["controlled_dimensions"][0].update(same_value_across_arms_required=False), "controlled_dimensions.0.same_value_across_arms_required"),
    ("unknown_confounder_effect", lambda d: d["confounder_controls"][0].update(effect_if_uncontrolled="bogus"), "confounder_controls.0.effect_if_uncontrolled"),
    ("unknown_source_kind", lambda d: d["source_evidence"][0].update(kind="bogus_kind"), "source_evidence.0.kind"),
]

# (label, foundational kind, replacement path, expected diagnostic) — each points a
# declared foundational source at a non-mapping/non-file target; the design must exit 1
# with READABLE_FOUNDATIONAL_SOURCES and the matching diagnostic.
READABILITY_MUTATIONS = [
    ("gate_wrong_extension", "condition_contrast_design_gate", f"{EV}/foundation-not-yaml.txt", "is not a .yml/.yaml file"),
    ("gate_invalid_yaml", "condition_contrast_design_gate", f"{EV}/foundation-invalid.yml", "is not valid YAML"),
    ("gate_not_mapping", "condition_contrast_design_gate", f"{EV}/foundation-list.yml", "is not a YAML mapping"),
    ("gate_directory", "condition_contrast_design_gate", f"{EV}/source-directory", "is not a regular file"),
    ("readiness_wrong_extension", "readiness_gate", f"{EV}/foundation-not-yaml.txt", "is not a .yml/.yaml file"),
    ("readiness_invalid_yaml", "readiness_gate", f"{EV}/foundation-invalid.yml", "is not valid YAML"),
    ("readiness_not_mapping", "readiness_gate", f"{EV}/foundation-list.yml", "is not a YAML mapping"),
    ("readiness_directory", "readiness_gate", f"{EV}/source-directory", "is not a regular file"),
]


class ModelLabConditionDesignValidatorTests(unittest.TestCase):
    def run_validator(self, *paths: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VALIDATOR_PATH), *[str(path) for path in paths]],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def assert_exit_code(self, completed: subprocess.CompletedProcess[str], expected: int) -> None:
        self.assertEqual(expected, completed.returncode, completed.stdout + completed.stderr)

    def _basic_data(self) -> dict:
        return yaml.safe_load((FIXTURE_ROOT / "valid/basic.yml").read_text(encoding="utf-8"))

    def _run_on_data(self, data: dict) -> subprocess.CompletedProcess[str]:
        # Repo-relative source/freeze/arm paths resolve against the repo root, so the
        # mutated file may live in a temp dir without breaking valid references.
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

    def _arm(self, data: dict, role: str) -> dict:
        return next(a for a in data["arms"] if a.get("role") == role)

    # --- baseline guarantees -------------------------------------------------

    def test_valid_fixtures_exit_zero(self) -> None:
        for rel_path in VALID_FIXTURES:
            with self.subTest(rel_path=rel_path):
                self.assert_exit_code(self.run_validator(FIXTURE_ROOT / rel_path), 0)

    def test_real_series_artifact_exits_zero(self) -> None:
        self.assertTrue(REAL_ARTIFACT.is_file(), f"missing real artifact: {REAL_ARTIFACT}")
        self.assert_exit_code(self.run_validator(REAL_ARTIFACT), 0)

    def test_discovery_finds_and_passes_real_artifact(self) -> None:
        completed = self.run_validator()  # no args -> discover under experiments/
        self.assert_exit_code(completed, 0)
        rel = REAL_ARTIFACT.resolve().relative_to(REPO_ROOT).as_posix()
        self.assertIn(rel, completed.stdout)

    def test_invalid_fixtures_exit_one_with_rule_ids(self) -> None:
        for rel_path, rule_id in INVALID_FIXTURES.items():
            with self.subTest(rel_path=rel_path):
                completed = self.run_validator(FIXTURE_ROOT / rel_path)
                self.assert_exit_code(completed, 1)
                self.assertIn(rule_id, completed.stdout)
                self.assertNotIn("Traceback", completed.stdout + completed.stderr)

    def test_multiple_paths_return_highest_exit_code(self) -> None:
        completed = self.run_validator(
            FIXTURE_ROOT / "valid/basic.yml",
            FIXTURE_ROOT / "invalid/missing-gate-source.yml",
        )
        self.assert_exit_code(completed, 1)

    # --- schema (form) violations via mutation -------------------------------

    def test_schema_constant_mutations_are_schema_errors(self) -> None:
        for label, mutate, instance_path in SCHEMA_CONST_MUTATIONS:
            with self.subTest(case=label):
                data = self._basic_data()
                mutate(data)
                completed = self._run_on_data(data)
                self.assert_exit_code(completed, 2)
                self.assertIn(f"instance_path={instance_path}", completed.stdout)
                self.assertNotIn("Traceback", completed.stdout + completed.stderr)

    def test_arm_count_must_be_two(self) -> None:
        for label, arms in (("one", "first"), ("three", "three")):
            with self.subTest(case=label):
                data = self._basic_data()
                if arms == "first":
                    data["arms"] = [data["arms"][0]]
                else:
                    extra = dict(data["arms"][0])
                    extra["id"] = "extra"
                    data["arms"] = data["arms"] + [extra]
                completed = self._run_on_data(data)
                self.assert_exit_code(completed, 2)
                self.assertIn("instance_path=arms", completed.stdout)

    def test_schema_violation_exits_two(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            bad = Path(temp_dir) / "schema-invalid.yml"
            bad.write_text(
                'schema_version: "v1"\nartifact_type: "model_lab_condition_design"\n',
                encoding="utf-8",
            )
            self.assert_exit_code(self.run_validator(bad), 2)

    def test_unknown_top_level_property_is_schema_error(self) -> None:
        # A selection/result field is rejected by additionalProperties:false, proving no
        # execution/result leakage into the frozen design contract.
        data = self._basic_data()
        data["selected_condition_winner"] = "treatment"
        completed = self._run_on_data(data)
        self.assert_exit_code(completed, 2)
        self.assertNotIn("Traceback", completed.stdout + completed.stderr)

    def test_schema_non_blank_fields_reject_whitespace_only(self) -> None:
        mutations = [
            ("series_id", lambda d: d.update(series_id="   "), "series_id"),
            ("challenge_version", lambda d: d.update(challenge_version="   "), "challenge_version"),
            ("design_id", lambda d: d.update(design_id="   "), "design_id"),
            ("summary", lambda d: d.update(summary="   "), "summary"),
            ("materiality_rationale", lambda d: d.update(materiality_rationale="   "), "materiality_rationale"),
            ("arm_workflow_protocol", lambda d: d["arms"][0].update(workflow_protocol="   "), "arms.0.workflow_protocol"),
            ("arm_intervention_profile", lambda d: d["arms"][0].update(intervention_profile="   "), "arms.0.intervention_profile"),
            ("controlled_control_method", lambda d: d["controlled_dimensions"][0].update(control_method="   "), "controlled_dimensions.0.control_method"),
            ("controlled_binding_source", lambda d: d["controlled_dimensions"][0].update(binding_source="   "), "controlled_dimensions.0.binding_source"),
            ("confounder_controlled_by", lambda d: d["confounder_controls"][0].update(controlled_by="   "), "confounder_controls.0.controlled_by"),
            ("decision_reason", lambda d: d["decision"].update(reason="   "), "decision.reason"),
            ("does_not_establish_item", lambda d: d["does_not_establish"].__setitem__(0, "   "), "does_not_establish.0"),
        ]
        for label, mutate, instance_path in mutations:
            with self.subTest(case=label):
                data = self._basic_data()
                mutate(data)
                completed = self._run_on_data(data)
                self.assert_exit_code(completed, 2)
                self.assertIn(f"instance_path={instance_path}", completed.stdout)
                self.assertNotIn("Traceback", completed.stdout + completed.stderr)

    def test_non_blank_token_rejects_trailing_line_breaks(self) -> None:
        for loc in ("series_id", "challenge_version", "design_id"):
            for label, val in (("lf", "x\n"), ("cr", "x\r"), ("crlf", "x\r\n"), ("tab", "x\ty")):
                with self.subTest(loc=loc, case=label):
                    data = self._basic_data()
                    data[loc] = val
                    completed = self._run_on_data(data)
                    self.assert_exit_code(completed, 2)
                    self.assertIn(f"instance_path={loc}", completed.stdout)
        data = self._basic_data()
        data["does_not_establish"][0] = data["does_not_establish"][0] + "\n"
        completed = self._run_on_data(data)
        self.assert_exit_code(completed, 2)
        self.assertIn("instance_path=does_not_establish.0", completed.stdout)

    def test_schema_non_blank_fields_accept_valid_text(self) -> None:
        validator = Draft202012Validator(json.loads(SCHEMA_PATH.read_text(encoding="utf-8")))
        for text in ("Valid text.", "Text with internal spaces.", "Mehrzeiliger\nText.", "日本語の説明"):
            with self.subTest(text=text):
                data = self._basic_data()
                data["summary"] = text
                self.assertEqual([], list(validator.iter_errors(data)))
        for token in ("fixture-series", "rest-api-v1", "überprüfung_v1"):
            with self.subTest(token=token):
                data = self._basic_data()
                data["series_id"] = token
                self.assertEqual([], list(validator.iter_errors(data)))

    def test_wrong_schema_version_exits_two(self) -> None:
        data = self._basic_data()
        data["schema_version"] = "1.0.0"
        self.assert_exit_code(self._run_on_data(data), 2)

    def test_parse_error_exits_two(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            bad = Path(temp_dir) / "bad.yml"
            bad.write_text("source_evidence: [\n", encoding="utf-8")
            self.assert_exit_code(self.run_validator(bad), 2)

    def test_invalid_utf8_design_exits_two_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            invalid = Path(temp_dir) / "invalid-utf8.yml"
            invalid.write_bytes(b"\xff\xfe\xfa")
            completed = self.run_validator(invalid)
        self.assert_exit_code(completed, 2)
        self.assertIn("not valid UTF-8", completed.stdout)
        self.assertNotIn("Traceback", completed.stdout + completed.stderr)

    # --- source path forms ---------------------------------------------------

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

    def test_valid_unicode_source_paths_pass_schema_form(self) -> None:
        validator = Draft202012Validator(json.loads(SCHEMA_PATH.read_text(encoding="utf-8")))
        for value in ("äöü/datei.yml", "日本語/file.yml", "dir/file name.yml"):
            with self.subTest(value=value):
                data = self._basic_data()
                data["source_evidence"][2]["path"] = value
                self.assertEqual([], list(validator.iter_errors(data)))

    # --- foundational source readability -------------------------------------

    def test_unreadable_foundational_sources_are_readability_errors(self) -> None:
        for label, kind, new_path, expected_message in READABILITY_MUTATIONS:
            with self.subTest(case=label):
                data = self._basic_data()
                self._set_source_path(data, kind, new_path)
                completed = self._run_on_data(data)
                self.assert_exit_code(completed, 1)
                self.assertIn("CONDITION_DESIGN_REQUIRES_READABLE_FOUNDATIONAL_SOURCES", completed.stdout)
                self.assertIn(expected_message, completed.stdout)
                self.assertNotIn("Traceback", completed.stdout + completed.stderr)

    def test_context_source_directory_is_unsafe_path(self) -> None:
        data = self._basic_data()
        self._set_source_path(data, "assessment_context", f"{EV}/source-directory")
        completed = self._run_on_data(data)
        self.assert_exit_code(completed, 1)
        self.assertIn("CONDITION_DESIGN_REQUIRES_SAFE_EXISTING_PATHS", completed.stdout)

    # --- arm reference path safety -------------------------------------------

    def test_arm_ref_escape_is_unsafe_path(self) -> None:
        data = self._basic_data()
        for arm in data["arms"]:  # keep both arms equal so only the path rule is at issue
            arm["common_condition_ref"] = "../../../../etc/passwd"
        completed = self._run_on_data(data)
        self.assert_exit_code(completed, 1)
        self.assertIn("CONDITION_DESIGN_REQUIRES_SAFE_EXISTING_PATHS", completed.stdout)
        self.assertNotIn("Traceback", completed.stdout + completed.stderr)

    # --- forbidden execution artifacts in the design directory ---------------

    def test_clean_relocated_design_passes(self) -> None:
        # A valid design copied into an otherwise-empty directory still validates: proves
        # the execution-artifact scan does not false-positive and that mutation tests are
        # not spuriously failing on the freeze.
        with tempfile.TemporaryDirectory() as temp_dir:
            copy = Path(temp_dir) / "condition-design.yml"
            shutil.copy(FIXTURE_ROOT / "valid/basic.yml", copy)
            self.assert_exit_code(self.run_validator(copy), 0)

    def test_execution_artifacts_in_design_dir_are_forbidden(self) -> None:
        cases = [
            ("run_yml", lambda d: (d / "run.yml").write_text("x\n", encoding="utf-8")),
            ("run_meta", lambda d: (d / "run_meta.json").write_text("{}\n", encoding="utf-8")),
            ("package_json", lambda d: (d / "package.json").write_text("{}\n", encoding="utf-8")),
            ("implementation_dir", lambda d: (d / "implementation").mkdir()),
            ("src_dir", lambda d: (d / "src").mkdir()),
            ("execute_script", lambda d: (d / "execute-run.py").write_text("x\n", encoding="utf-8")),
            ("verify_script", lambda d: (d / "verify-run.py").write_text("x\n", encoding="utf-8")),
        ]
        for label, plant in cases:
            with self.subTest(case=label):
                with tempfile.TemporaryDirectory() as temp_dir:
                    design_dir = Path(temp_dir)
                    copy = design_dir / "condition-design.yml"
                    shutil.copy(FIXTURE_ROOT / "valid/basic.yml", copy)
                    plant(design_dir)
                    completed = self.run_validator(copy)
                    self.assert_exit_code(completed, 1)
                    self.assertIn("CONDITION_DESIGN_FORBIDS_EXECUTION_ARTIFACTS", completed.stdout)
                    self.assertNotIn("Traceback", completed.stdout + completed.stderr)

    # --- non-claims ----------------------------------------------------------

    def test_each_mandatory_non_claim_is_required(self) -> None:
        for claim in (
            "weak_condition_contrast_resolved",
            "run_004_executed",
            "execution_environment_bound",
            "model_quality",
            "comparison_ready",
        ):
            with self.subTest(claim=claim):
                data = self._basic_data()
                data["does_not_establish"].remove(claim)
                completed = self._run_on_data(data)
                self.assert_exit_code(completed, 1)
                self.assertIn("CONDITION_DESIGN_REQUIRES_MANDATORY_NON_CLAIMS", completed.stdout)
                self.assertIn(claim, completed.stdout)

    def test_established_selection_claims_must_not_be_denied(self) -> None:
        for claim in ("primary_intervention_axis_selected", "concrete_condition_selected"):
            with self.subTest(claim=claim):
                data = self._basic_data()
                data["does_not_establish"].append(claim)
                completed = self._run_on_data(data)
                self.assert_exit_code(completed, 1)
                self.assertIn("CONDITION_DESIGN_REQUIRES_MANDATORY_NON_CLAIMS", completed.stdout)
                self.assertIn(claim, completed.stdout)

    def test_non_claim_normalization_is_case_insensitive(self) -> None:
        data = self._basic_data()
        data["does_not_establish"] = [
            "MODEL_QUALITY" if item == "model_quality" else item
            for item in data["does_not_establish"]
        ]
        completed = self._run_on_data(data)
        self.assert_exit_code(completed, 0)

    def test_triggered_by_accepts_non_blank_reference(self) -> None:
        data = self._basic_data()
        data["triggered_by"] = "user-request-2026-06-23-some-other-anchor"
        self.assert_exit_code(self._run_on_data(data), 0)

    # --- single-primary-axis diagnostics -------------------------------------

    def test_arms_must_differ_along_primary_axis(self) -> None:
        # Both arms identical along the axis but the design otherwise valid-shaped: the
        # axis shows no variation.
        data = self._basic_data()
        treatment = self._arm(data, "treatment")
        treatment["workflow_protocol"] = "direct_implementation"
        completed = self._run_on_data(data)
        self.assert_exit_code(completed, 1)
        self.assertIn("CONDITION_DESIGN_REQUIRES_SINGLE_PRIMARY_AXIS", completed.stdout)

    # --- resolver hardening (white-box) --------------------------------------

    def test_resolver_rejects_control_and_surrogate_codepoints(self) -> None:
        module = runpy.run_path(str(VALIDATOR_PATH), run_name="condition_design_validator_module")
        resolve = module["resolve_repo_relative_path"]
        for value in ("a\x00b", "a\tb", "a\nb", "a\rb", "a\x7fb", "a\ud800b"):
            with self.subTest(value=ascii(value)):
                resolved, code = resolve(value, REPO_ROOT, must_exist=True)
                self.assertIsNone(resolved)
                self.assertEqual("ESCAPE", code)

    def test_resolver_rejects_ordinary_whitespace(self) -> None:
        module = runpy.run_path(str(VALIDATOR_PATH), run_name="condition_design_validator_module")
        resolve = module["resolve_repo_relative_path"]
        for value in (" tests/example.yml", "tests/example.yml ", " tests/example.yml "):
            with self.subTest(value=ascii(value)):
                resolved, code = resolve(value, REPO_ROOT, must_exist=False)
                self.assertIsNone(resolved)
                self.assertEqual("ESCAPE", code)

    def test_resolver_rejects_parent_escape(self) -> None:
        module = runpy.run_path(str(VALIDATOR_PATH), run_name="condition_design_validator_module")
        resolve = module["resolve_repo_relative_path"]
        resolved, code = resolve("../outside.yml", REPO_ROOT, must_exist=False)
        self.assertIsNone(resolved)
        self.assertEqual("ESCAPE", code)

    def test_display_path_exception_fallback(self) -> None:
        module = runpy.run_path(str(VALIDATOR_PATH), run_name="condition_design_validator_module")
        display_path_func = module["display_path"]

        class FailingPath:
            def __init__(self, path_str: str, exc: Exception):
                self.path_str = path_str
                self.exc = exc

            def resolve(self):
                raise self.exc

            def __str__(self):
                return self.path_str

        for exc_type in (OSError, RuntimeError, ValueError, UnicodeError):
            with self.subTest(exc=exc_type.__name__):
                fp = FailingPath("failing/path.yml", exc_type("mock error"))
                self.assertEqual("failing/path.yml", display_path_func(fp))


if __name__ == "__main__":
    unittest.main(verbosity=2)
