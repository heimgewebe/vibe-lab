#!/usr/bin/env python3
"""Regression tests for hardened model-lab-condition-design validation.

Negative cases build a complete in-repo temp bundle (copy of the valid fixture bundle with
refs rewritten to the temp location and the freeze recomputed), then mutate exactly one
thing. This lets the design-self-identity, bundle-boundary, child-identity, and freeze
guarantees be tested honestly rather than bypassed.
"""

from __future__ import annotations

import copy
import hashlib
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
VALID_BUNDLE = FIXTURE_ROOT / "valid" / "bundle"
FIX_PREFIX = "tests/fixtures/model_lab_condition_design/valid/bundle/"
BUNDLE_FILES = [
    "condition-design.yml", "common-condition.md", "control-workflow-protocol.md",
    "treatment-workflow-protocol.md", "verification-protocol.yml",
    "measurement-protocol.yml", "precondition-snapshot.yml",
]
REAL_ARTIFACT = (
    REPO_ROOT / "experiments" / "2026-05-31_model-lab-replication-series"
    / "artifacts" / "run-004-condition-contrast-design" / "condition-design.yml"
)


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


class ModelLabConditionDesignValidatorTests(unittest.TestCase):
    def run_validator(self, *paths: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VALIDATOR_PATH), *[str(p) for p in paths]],
            cwd=REPO_ROOT, capture_output=True, text=True, check=False,
        )

    def assert_exit(self, completed, expected: int) -> None:
        self.assertEqual(expected, completed.returncode, completed.stdout + completed.stderr)

    # --- temp bundle helper --------------------------------------------------

    def build_bundle(self, *, design=None, snapshot=None, verification=None,
                     measurement=None, freeze=None, plant=None, recompute_freeze=True) -> Path:
        tmp = Path(tempfile.mkdtemp(prefix="_scratch_", dir=FIXTURE_ROOT))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        tmp_prefix = tmp.relative_to(REPO_ROOT).as_posix() + "/"
        for fn in BUNDLE_FILES:
            shutil.copy(VALID_BUNDLE / fn, tmp / fn)

        # condition-design.yml: rewrite refs to the temp location, then apply override.
        text = (VALID_BUNDLE / "condition-design.yml").read_text().replace(FIX_PREFIX, tmp_prefix)
        d = yaml.safe_load(text)
        if design:
            design(d)
        (tmp / "condition-design.yml").write_text(yaml.safe_dump(d, sort_keys=False, allow_unicode=True))

        for fn, mut in (("precondition-snapshot.yml", snapshot),
                        ("verification-protocol.yml", verification),
                        ("measurement-protocol.yml", measurement)):
            if mut:
                doc = yaml.safe_load((tmp / fn).read_text())
                mut(doc)
                (tmp / fn).write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True))

        if recompute_freeze:
            ident = yaml.safe_load((tmp / "condition-design.yml").read_text())
            man = {
                "artifact_type": "model_lab_condition_design_freeze_manifest",
                "design_id": ident.get("design_id"), "series_id": ident.get("series_id"),
                "challenge_version": ident.get("challenge_version"),
                "frozen_at": "2026-06-23T00:00:00Z", "frozen_before_execution": True,
                "source_base_commit_sha": "0" * 40,
                "change_rule": "temp bundle freeze; never self-hashes; records no commit SHA.",
                "hashes": [{"path": tmp_prefix + f, "sha256": _sha(tmp / f)}
                           for f in BUNDLE_FILES],
            }
            if freeze:
                freeze(man, tmp_prefix)
            (tmp / "freeze-manifest.yml").write_text(yaml.safe_dump(man, sort_keys=False, allow_unicode=True))

        if plant:
            for rel, content in plant.items():
                target = tmp / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                if content is None:
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.write_text(content)
        return tmp / "condition-design.yml"

    def assert_rule(self, completed, rule: str) -> None:
        self.assert_exit(completed, 1)
        self.assertIn(rule, completed.stdout)
        self.assertNotIn("Traceback", completed.stdout + completed.stderr)

    # --- baseline ------------------------------------------------------------

    def test_valid_bundle_exits_zero(self):
        self.assert_exit(self.run_validator(VALID_BUNDLE / "condition-design.yml"), 0)

    def test_built_bundle_exits_zero(self):
        self.assert_exit(self.run_validator(self.build_bundle()), 0)

    def test_real_series_artifact_exits_zero(self):
        self.assertTrue(REAL_ARTIFACT.is_file(), f"missing real artifact: {REAL_ARTIFACT}")
        self.assert_exit(self.run_validator(REAL_ARTIFACT), 0)

    def test_discovery_finds_and_passes_real_artifact(self):
        completed = self.run_validator()
        self.assert_exit(completed, 0)
        self.assertIn(REAL_ARTIFACT.resolve().relative_to(REPO_ROOT).as_posix(), completed.stdout)

    def test_multiple_paths_return_highest_exit_code(self):
        bad = self.build_bundle(design=lambda d: d["does_not_establish"].remove("model_quality"))
        completed = self.run_validator(VALID_BUNDLE / "condition-design.yml", bad)
        self.assert_exit(completed, 1)

    # --- snapshot / identity -------------------------------------------------

    def test_snapshot_wrong_challenge_is_invalid(self):
        c = self.build_bundle(snapshot=lambda s: s.update(challenge_version="rest-api-v2"))
        self.assert_rule(self.run_validator(c), "CONDITION_DESIGN_REQUIRES_VALID_PRECONDITION_SNAPSHOT")

    def test_snapshot_wrong_series_is_invalid(self):
        c = self.build_bundle(snapshot=lambda s: s.update(series_id="other-series"))
        self.assert_rule(self.run_validator(c), "CONDITION_DESIGN_REQUIRES_VALID_PRECONDITION_SNAPSHOT")

    def test_snapshot_gate_allows_execution_is_invalid(self):
        c = self.build_bundle(snapshot=lambda s: s["captured_sources"]["gate"].update(run_004_execution_allowed=True))
        self.assert_rule(self.run_validator(c), "CONDITION_DESIGN_REQUIRES_VALID_PRECONDITION_SNAPSHOT")

    def test_snapshot_gate_target_resolved_is_invalid(self):
        c = self.build_bundle(snapshot=lambda s: s["captured_sources"]["gate"].update(blocker_status_after_gate="resolved"))
        self.assert_rule(self.run_validator(c), "CONDITION_DESIGN_REQUIRES_VALID_PRECONDITION_SNAPSHOT")

    def test_snapshot_readiness_not_blocked_is_invalid(self):
        c = self.build_bundle(snapshot=lambda s: s["captured_sources"]["readiness"].update(readiness_status_at_design="ready"))
        self.assert_rule(self.run_validator(c), "CONDITION_DESIGN_REQUIRES_VALID_PRECONDITION_SNAPSHOT")

    def test_gate_required_dimension_missing_is_subset_violation(self):
        c = self.build_bundle(design=lambda d: d.update(
            controlled_dimensions=[x for x in d["controlled_dimensions"] if x["id"] != "test_harness"]))
        self.assert_rule(self.run_validator(c), "CONDITION_DESIGN_REQUIRES_GATE_REQUIREMENTS_SUBSET")

    def test_gate_confounder_effect_weakened_is_subset_violation(self):
        def mut(d):
            for c in d["confounder_controls"]:
                if c["id"] == "multi_axis_drift":
                    c["effect_if_uncontrolled"] = "must_be_reported"
        c = self.build_bundle(design=mut)
        self.assert_rule(self.run_validator(c), "CONDITION_DESIGN_REQUIRES_GATE_REQUIREMENTS_SUBSET")

    # --- child protocols -----------------------------------------------------

    def test_child_wrong_design_id_is_identity_violation(self):
        c = self.build_bundle(verification=lambda v: v.update(design_id="other-design"))
        self.assert_rule(self.run_validator(c), "CONDITION_DESIGN_REQUIRES_CHILD_IDENTITY")

    def test_verification_not_equal_for_both_arms_is_invalid(self):
        c = self.build_bundle(verification=lambda v: v.update(applies_equally_to_both_arms=False))
        self.assert_rule(self.run_validator(c), "CONDITION_DESIGN_REQUIRES_SHARED_VERIFICATION")

    def test_verification_executes_is_invalid(self):
        c = self.build_bundle(verification=lambda v: v.update(does_not_execute=False))
        self.assert_rule(self.run_validator(c), "CONDITION_DESIGN_REQUIRES_SHARED_VERIFICATION")

    def test_measurement_records_values_is_invalid(self):
        c = self.build_bundle(measurement=lambda m: m.update(does_not_record_values=False))
        self.assert_rule(self.run_validator(c), "CONDITION_DESIGN_REQUIRES_SHARED_MEASUREMENT")

    def test_measurement_post_hoc_allowed_is_invalid(self):
        c = self.build_bundle(measurement=lambda m: m.update(post_hoc_metric_selection_forbidden=False))
        self.assert_rule(self.run_validator(c), "CONDITION_DESIGN_REQUIRES_SHARED_MEASUREMENT")

    def test_measurement_metric_with_value_is_invalid(self):
        c = self.build_bundle(measurement=lambda m: m["primary_metrics"][0].update(value="0.9"))
        self.assert_rule(self.run_validator(c), "CONDITION_DESIGN_REQUIRES_SHARED_MEASUREMENT")

    def test_measurement_ratio_without_range_is_invalid(self):
        c = self.build_bundle(measurement=lambda m: m["primary_metrics"][0].pop("range"))
        self.assert_rule(self.run_validator(c), "CONDITION_DESIGN_REQUIRES_SHARED_MEASUREMENT")

    def test_measurement_missing_compliance_metric_is_invalid(self):
        def mut(m):
            m["primary_metrics"] = [x for x in m["primary_metrics"] if x["id"] != "workflow_protocol_compliance"]
        c = self.build_bundle(measurement=mut)
        self.assert_rule(self.run_validator(c), "CONDITION_DESIGN_REQUIRES_SHARED_MEASUREMENT")

    # --- condition semantics -------------------------------------------------

    def test_treatment_without_spec_requirement_is_not_material(self):
        def mut(d):
            t = next(a for a in d["arms"] if a["role"] == "treatment")
            t["workflow_protocol_spec"] = {
                "pre_implementation_specification_required": False,
                "implementation_may_begin_immediately": True,
                "specification_completeness_checked_before_implementation": False,
                "required_specification_sections": [],
            }
        c = self.build_bundle(design=mut)
        self.assert_rule(self.run_validator(c), "CONDITION_DESIGN_REQUIRES_MATERIAL_CONTRAST")

    def test_treatment_may_implement_with_incomplete_spec_is_not_material(self):
        def mut(d):
            t = next(a for a in d["arms"] if a["role"] == "treatment")
            t["workflow_protocol_spec"]["implementation_may_begin_immediately"] = True
        c = self.build_bundle(design=mut)
        self.assert_rule(self.run_validator(c), "CONDITION_DESIGN_REQUIRES_MATERIAL_CONTRAST")

    def test_arms_same_workflow_protocol_is_single_axis_violation(self):
        def mut(d):
            next(a for a in d["arms"] if a["role"] == "treatment")["workflow_protocol"] = "direct_implementation"
        c = self.build_bundle(design=mut)
        self.assert_rule(self.run_validator(c), "CONDITION_DESIGN_REQUIRES_SINGLE_PRIMARY_AXIS")

    def test_primary_axis_in_controlled_dimensions_is_invalid(self):
        def mut(d):
            d["controlled_dimensions"].append({
                "id": "workflow_protocol", "control_method": "x", "binding_status": "bound_at_design",
                "binding_source": "x", "same_value_across_arms_required": True, "blocking_divergence": "x"})
        c = self.build_bundle(design=mut)
        self.assert_rule(self.run_validator(c), "CONDITION_DESIGN_REQUIRES_PRIMARY_AXIS_NOT_CONTROLLED")

    def test_treatment_process_artifact_missing_is_separation_violation(self):
        c = self.build_bundle(design=lambda d: d["artifact_surfaces"]["arm_specific_process_artifacts"].update(treatment=[]))
        self.assert_rule(self.run_validator(c), "CONDITION_DESIGN_REQUIRES_ASSIGNED_VS_OBSERVED_SEPARATION")

    def test_control_with_process_artifact_is_separation_violation(self):
        c = self.build_bundle(design=lambda d: d["artifact_surfaces"]["arm_specific_process_artifacts"].update(control=["sneaky"]))
        self.assert_rule(self.run_validator(c), "CONDITION_DESIGN_REQUIRES_ASSIGNED_VS_OBSERVED_SEPARATION")

    def test_duplicate_arm_role_is_two_arms_violation(self):
        c = self.build_bundle(design=lambda d: next(a for a in d["arms"] if a["role"] == "treatment").update(role="control"))
        self.assert_rule(self.run_validator(c), "CONDITION_DESIGN_REQUIRES_EXACTLY_TWO_ARMS")

    def test_duplicate_arm_id_is_unique_ids_violation(self):
        c = self.build_bundle(design=lambda d: next(a for a in d["arms"] if a["role"] == "treatment").update(id="control"))
        self.assert_rule(self.run_validator(c), "CONDITION_DESIGN_REQUIRES_UNIQUE_SEMANTIC_IDS")

    # --- bundle / paths / self-identity --------------------------------------

    def test_wrong_design_self_path_is_invalid(self):
        c = self.build_bundle(design=lambda d: d.update(
            design_artifact_path="tests/fixtures/model_lab_condition_design/valid/bundle/common-condition.md"))
        self.assert_rule(self.run_validator(c), "CONDITION_DESIGN_REQUIRES_DESIGN_SELF_IDENTITY")

    def test_child_outside_bundle_is_boundary_violation(self):
        c = self.build_bundle(design=lambda d: d["verification_surface"].update(
            protocol_ref=FIX_PREFIX + "verification-protocol.yml"))  # points back at the canonical fixture, outside temp bundle
        self.assert_rule(self.run_validator(c), "CONDITION_DESIGN_REQUIRES_BUNDLE_BOUNDARY")

    def test_context_source_directory_is_unsafe_path(self):
        c = self.build_bundle(design=lambda d: d.update(source_evidence=[
            {"path": "tests/fixtures/model_lab_condition_design/_evidence/source-directory", "kind": "assessment_context"},
            {"path": "tests/fixtures/model_lab_condition_design/_evidence/method-context.txt", "kind": "method_context"}]))
        self.assert_rule(self.run_validator(c), "CONDITION_DESIGN_REQUIRES_SAFE_EXISTING_PATHS")

    def test_context_source_escape_is_unsafe_path(self):
        c = self.build_bundle(design=lambda d: d.update(source_evidence=[
            {"path": "../../../../etc/passwd", "kind": "assessment_context"},
            {"path": "tests/fixtures/model_lab_condition_design/_evidence/method-context.txt", "kind": "method_context"}]))
        self.assert_rule(self.run_validator(c), "CONDITION_DESIGN_REQUIRES_SAFE_EXISTING_PATHS")

    # --- recursive execution artifacts ---------------------------------------

    def test_nested_execution_artifacts_are_forbidden(self):
        cases = {
            "nested_run_yml": {"nested/run.yml": "x\n"},
            "nested_run_meta": {"nested/run_meta.json": "{}\n"},
            "nested_implementation_dir": {"nested/implementation": None},
            "nested_src_dir": {"nested/src": None},
            "deep_execute_py": {"nested/deeper/execute-run.py": "x\n"},
            "deep_verify_py": {"nested/deeper/verify-run.py": "x\n"},
        }
        for label, plant in cases.items():
            with self.subTest(case=label):
                c = self.build_bundle(plant=plant)
                self.assert_rule(self.run_validator(c), "CONDITION_DESIGN_FORBIDS_EXECUTION_ARTIFACTS")

    # --- freeze --------------------------------------------------------------

    def test_freeze_hash_mismatch_is_invalid(self):
        def fr(man, prefix):
            man["hashes"][1]["sha256"] = "0" * 64
        c = self.build_bundle(freeze=fr)
        self.assert_rule(self.run_validator(c), "CONDITION_DESIGN_REQUIRES_VALID_FREEZE")

    def test_freeze_self_hash_is_invalid(self):
        def fr(man, prefix):
            man["hashes"].append({"path": prefix + "freeze-manifest.yml", "sha256": "0" * 64})
        c = self.build_bundle(freeze=fr)
        self.assert_rule(self.run_validator(c), "CONDITION_DESIGN_REQUIRES_VALID_FREEZE")

    def test_freeze_duplicate_path_is_invalid(self):
        def fr(man, prefix):
            man["hashes"].append(dict(man["hashes"][0]))
        c = self.build_bundle(freeze=fr)
        self.assert_rule(self.run_validator(c), "CONDITION_DESIGN_REQUIRES_VALID_FREEZE")

    def test_freeze_missing_bundle_path_is_invalid(self):
        def fr(man, prefix):
            man["hashes"] = man["hashes"][:-1]  # drop the snapshot coverage
        c = self.build_bundle(freeze=fr)
        self.assert_rule(self.run_validator(c), "CONDITION_DESIGN_REQUIRES_VALID_FREEZE")

    def test_freeze_invalid_timestamp_is_invalid(self):
        def fr(man, prefix):
            man["frozen_at"] = "yesterday"
        c = self.build_bundle(freeze=fr)
        self.assert_rule(self.run_validator(c), "CONDITION_DESIGN_REQUIRES_VALID_FREEZE")

    def test_freeze_commit_self_reference_is_invalid(self):
        def fr(man, prefix):
            man["final_commit_sha"] = "a" * 40
        c = self.build_bundle(freeze=fr)
        self.assert_rule(self.run_validator(c), "CONDITION_DESIGN_REQUIRES_VALID_FREEZE")

    def test_freeze_wrong_child_identity_is_invalid(self):
        def fr(man, prefix):
            man["design_id"] = "other-design"
        c = self.build_bundle(freeze=fr)
        self.assert_rule(self.run_validator(c), "CONDITION_DESIGN_REQUIRES_VALID_FREEZE")

    # --- non-claims ----------------------------------------------------------

    def test_each_mandatory_non_claim_is_required(self):
        for claim in ("weak_condition_contrast_resolved", "execution_environment_bound",
                      "single_paired_execution_establishes_condition_effect", "model_quality"):
            with self.subTest(claim=claim):
                c = self.build_bundle(design=lambda d, cl=claim: d["does_not_establish"].remove(cl))
                completed = self.run_validator(c)
                self.assert_rule(completed, "CONDITION_DESIGN_REQUIRES_MANDATORY_NON_CLAIMS")
                self.assertIn(claim, completed.stdout)

    def test_established_selection_claims_must_not_be_denied(self):
        for claim in ("primary_intervention_axis_selected", "concrete_condition_selected"):
            with self.subTest(claim=claim):
                c = self.build_bundle(design=lambda d, cl=claim: d["does_not_establish"].append(cl))
                self.assert_rule(self.run_validator(c), "CONDITION_DESIGN_REQUIRES_MANDATORY_NON_CLAIMS")

    # --- schema (form) violations -> exit 2 ----------------------------------

    def _run_schema_mutation(self, mutate) -> subprocess.CompletedProcess[str]:
        d = yaml.safe_load((VALID_BUNDLE / "condition-design.yml").read_text())
        mutate(d)
        with tempfile.TemporaryDirectory() as t:
            f = Path(t) / "condition-design.yml"
            f.write_text(yaml.safe_dump(d, sort_keys=False, allow_unicode=True))
            return self.run_validator(f)

    def test_schema_constant_mutations_are_schema_errors(self):
        cases = [
            ("schema_version", lambda d: d.update(schema_version="1.0.0")),
            ("design_status", lambda d: d.update(design_status="draft")),
            ("target_blocker", lambda d: d.update(target_blocker="other")),
            ("run_004_execution_allowed", lambda d: d.update(run_004_execution_allowed=True)),
            ("execution_binding_status", lambda d: d.update(execution_binding_status="bound")),
            ("runtime_values_bound", lambda d: d.update(runtime_values_bound=True)),
            ("condition_semantics_status", lambda d: d.update(condition_semantics_status="draft")),
            ("axis_id", lambda d: d["primary_intervention_axis"].update(id="tool_and_agent_mode")),
            ("axis_semantics", lambda d: d["primary_intervention_axis"].update(semantics="enforced_thought")),
            ("required_axis_count", lambda d: d["primary_intervention_axis"].update(required_axis_count=2)),
            ("process_scored_as_outcome", lambda d: d.update(process_artifacts_scored_as_outcome=True)),
            ("harness_bound_at_design", lambda d: d["executable_harness_instance"].update(binding_status="bound_at_design")),
            ("verification_deferred", lambda d: d["verification_surface"].update(binding_status="deferred_to_execution_readiness")),
            ("readiness_req_false", lambda d: d["execution_readiness_requirements"].update(fresh_session_per_arm=False)),
            ("condition_input_claim", lambda d: d.update(condition_input_claim="identical_full_input")),
            ("unknown_arm_role", lambda d: d["arms"][0].update(role="placebo")),
            ("controlled_same_value_false", lambda d: d["controlled_dimensions"][0].update(same_value_across_arms_required=False)),
            ("decision_next_step", lambda d: d["decision"].update(next_step="run_004_execution_may_begin")),
            ("human_intervention_async", lambda d: d["human_intervention"].update(asymmetric_intervention_forbidden=False)),
        ]
        for label, mut in cases:
            with self.subTest(case=label):
                self.assert_exit(self._run_schema_mutation(mut), 2)

    def test_unknown_top_level_property_is_schema_error(self):
        self.assert_exit(self._run_schema_mutation(lambda d: d.update(selected_condition_winner="treatment")), 2)

    def test_arm_count_must_be_two(self):
        self.assert_exit(self._run_schema_mutation(lambda d: d.update(arms=[d["arms"][0]])), 2)

    def test_whitespace_token_rejected(self):
        for label, mut in [("series_id", lambda d: d.update(series_id="   ")),
                           ("design_id_newline", lambda d: d.update(design_id="x\n")),
                           ("summary_blank", lambda d: d.update(summary="   "))]:
            with self.subTest(case=label):
                self.assert_exit(self._run_schema_mutation(mut), 2)

    def test_challenge_sha_must_be_hex(self):
        self.assert_exit(self._run_schema_mutation(lambda d: d["challenge"].update(source_sha256="nothex")), 2)

    def test_parse_and_utf8_errors_exit_two(self):
        with tempfile.TemporaryDirectory() as t:
            bad = Path(t) / "bad.yml"
            bad.write_text("arms: [\n")
            self.assert_exit(self.run_validator(bad), 2)
            badu = Path(t) / "u.yml"
            badu.write_bytes(b"\xff\xfe\xfa")
            completed = self.run_validator(badu)
            self.assert_exit(completed, 2)
            self.assertNotIn("Traceback", completed.stdout + completed.stderr)

    def test_schema_accepts_valid_unicode_and_text(self):
        validator = Draft202012Validator(json.loads(SCHEMA_PATH.read_text(encoding="utf-8")))
        d = yaml.safe_load((VALID_BUNDLE / "condition-design.yml").read_text())
        d["summary"] = "Mehrzeiliger\nText 日本語."
        self.assertEqual([], list(validator.iter_errors(d)))

    # --- resolver hardening --------------------------------------------------

    def test_resolver_rejects_unsafe_values(self):
        module = runpy.run_path(str(VALIDATOR_PATH), run_name="cd_validator_module")
        resolve = module["resolve_repo_relative_path"]
        for value in ("a\x00b", "a\tb", "a\nb", "a\x7fb", "a\ud800b", "../x.yml",
                      " lead.yml", "trail.yml ", "/abs.yml", "C:/x.yml", "a\\b.yml"):
            with self.subTest(value=ascii(value)):
                resolved, code = resolve(value, REPO_ROOT, must_exist=False)
                self.assertIsNone(resolved)
                self.assertEqual("ESCAPE", code)


if __name__ == "__main__":
    unittest.main(verbosity=2)
