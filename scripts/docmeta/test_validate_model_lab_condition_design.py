#!/usr/bin/env python3
"""Regression tests for source-bound, fail-closed model-lab-condition-design validation.

Negative cases build a complete in-repo temp bundle (a copy of the valid fixture bundle with
refs rewritten to the temp location, overlays re-rendered, snapshot hashes and freeze
recomputed), then inject exactly one invalid property. Closed child contracts make many
violations schema errors (exit 2); cross-artifact/source/freeze violations are semantic (exit 1).
"""

from __future__ import annotations

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
VALIDATOR = REPO_ROOT / "scripts" / "docmeta" / "validate_model_lab_condition_design.py"
RENDERER = REPO_ROOT / "scripts" / "docmeta" / "render_condition_overlays.py"
SCHEMA = REPO_ROOT / "schemas" / "model-lab-condition-design.v1.schema.json"
FIXROOT = REPO_ROOT / "tests" / "fixtures" / "model_lab_condition_design"
VB = FIXROOT / "valid" / "bundle"
FIX_PRE = "tests/fixtures/model_lab_condition_design/valid/bundle/"
TOP_FILES = ["condition-design.yml", "common-condition.md", "control-workflow-protocol.md",
             "treatment-workflow-protocol.md", "verification-protocol.yml", "measurement-protocol.yml",
             "precondition-snapshot.yml", "workflow-instruction-protocol.yml"]
SRC_FILES = ["source-snapshots/condition-contrast-design-gate.snapshot",
             "source-snapshots/result-assessment-readiness.snapshot",
             "source-snapshots/rest-api-v1.snapshot", "source-snapshots/spec-first.snapshot"]
ALL_FILES = TOP_FILES + SRC_FILES
REAL = (REPO_ROOT / "experiments" / "2026-05-31_model-lab-replication-series" / "artifacts"
        / "run-004-condition-contrast-design" / "condition-design.yml")
_render = runpy.run_path(str(RENDERER), run_name="cd_renderer")["render_overlay"]


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


class CD(unittest.TestCase):
    def run_v(self, *paths: Path):
        return subprocess.run([sys.executable, str(VALIDATOR), *[str(p) for p in paths]],
                              cwd=REPO_ROOT, capture_output=True, text=True, check=False)

    def _coerce(self, c):
        return self.run_v(c) if isinstance(c, Path) else c

    def assert_exit(self, c, code):
        c = self._coerce(c)
        self.assertEqual(code, c.returncode, c.stdout + c.stderr)

    def assert_rule(self, c, rule):
        c = self._coerce(c)
        self.assert_exit(c, 1)
        self.assertIn(rule, c.stdout)
        self.assertNotIn("Traceback", c.stdout + c.stderr)

    def build(self, *, design=None, snapshot=None, workflow=None, verification=None, measurement=None,
              freeze=None, frozen_gate=None, frozen_readiness=None, plant=None,
              rerender=True, recompute_snapshot_hashes=True, recompute_freeze=True) -> Path:
        tmp = Path(tempfile.mkdtemp(prefix="_scratch_", dir=FIXROOT))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        (tmp / "source-snapshots").mkdir()
        for f in ALL_FILES:
            shutil.copy(VB / f, tmp / f)
        pre = tmp.relative_to(REPO_ROOT).as_posix() + "/"

        d = yaml.safe_load((VB / "condition-design.yml").read_text().replace(FIX_PRE, pre))
        if design:
            design(d)
        (tmp / "condition-design.yml").write_text(yaml.safe_dump(d, sort_keys=False, allow_unicode=True))

        for fn, mut in (("workflow-instruction-protocol.yml", workflow),
                        ("verification-protocol.yml", verification),
                        ("measurement-protocol.yml", measurement)):
            if mut:
                doc = yaml.safe_load((tmp / fn).read_text()); mut(doc)
                (tmp / fn).write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True))
        for fn, mut in (("source-snapshots/condition-contrast-design-gate.snapshot", frozen_gate),
                        ("source-snapshots/result-assessment-readiness.snapshot", frozen_readiness)):
            if mut:
                doc = yaml.safe_load((tmp / fn).read_text()); mut(doc)
                (tmp / fn).write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True))

        if rerender:
            wf = yaml.safe_load((tmp / "workflow-instruction-protocol.yml").read_text())
            for role in ("control", "treatment"):
                (tmp / f"{role}-workflow-protocol.md").write_text(_render(wf, role))

        s = yaml.safe_load((VB / "precondition-snapshot.yml").read_text().replace(FIX_PRE, pre))
        if recompute_snapshot_hashes:
            for src in s["sources"].values():
                fp = REPO_ROOT / src["snapshot_path"]
                if fp.is_file():
                    src["snapshot_sha256"] = src["source_sha256"] = _sha(fp)
        if snapshot:
            snapshot(s)
        (tmp / "precondition-snapshot.yml").write_text(yaml.safe_dump(s, sort_keys=False, allow_unicode=True))

        if recompute_freeze:
            ident = yaml.safe_load((tmp / "condition-design.yml").read_text())
            man = {"artifact_type": "model_lab_condition_design_freeze_manifest",
                   "design_id": ident["design_id"], "series_id": ident["series_id"],
                   "challenge_version": ident["challenge_version"], "frozen_at": "2026-06-24T02:30:00Z",
                   "frozen_before_execution": True, "source_base_commit_sha": "0" * 40,
                   "change_rule": "temp", "hashes": [{"path": pre + f, "sha256": _sha(tmp / f)} for f in ALL_FILES]}
            if freeze:
                freeze(man, pre)
            (tmp / "freeze-manifest.yml").write_text(yaml.safe_dump(man, sort_keys=False, allow_unicode=True))
        if plant:
            for rel, content in plant.items():
                t = tmp / rel
                t.parent.mkdir(parents=True, exist_ok=True)
                t.mkdir() if content is None else t.write_text(content)
        return tmp / "condition-design.yml"

    # --- baseline ---
    def test_valid_bundle(self):
        self.assert_exit(self.run_v(VB / "condition-design.yml"), 0)

    def test_built_bundle(self):
        self.assert_exit(self.run_v(self.build()), 0)

    def test_real_artifact(self):
        self.assertTrue(REAL.is_file())
        self.assert_exit(self.run_v(REAL), 0)

    def test_discovery(self):
        c = self.run_v()
        self.assert_exit(c, 0)
        self.assertIn(REAL.resolve().relative_to(REPO_ROOT).as_posix(), c.stdout)

    # --- historical source snapshots (exit 1) ---
    def test_snapshot_path_escape(self):
        self.assert_rule(self.build(snapshot=lambda s: s["sources"]["gate"].update(snapshot_path="../../etc/passwd"),
                                    recompute_snapshot_hashes=False), "CONDITION_DESIGN_REQUIRES_VALID_PRECONDITION_SNAPSHOT")

    def test_readiness_snapshot_missing(self):
        self.assert_rule(self.build(snapshot=lambda s: s["sources"]["readiness"].update(snapshot_path=FIX_PRE + "source-snapshots/missing.yml"),
                                    recompute_snapshot_hashes=False), "CONDITION_DESIGN_REQUIRES_VALID_PRECONDITION_SNAPSHOT")

    def test_snapshot_hash_mismatch(self):
        self.assert_rule(self.build(frozen_gate=lambda g: g.update(extra="x"), recompute_snapshot_hashes=False),
                         "CONDITION_DESIGN_REQUIRES_VALID_PRECONDITION_SNAPSHOT")

    def test_source_sha_diverges_from_snapshot(self):
        self.assert_rule(self.build(snapshot=lambda s: s["sources"]["gate"].update(source_sha256="0" * 64),
                                    recompute_snapshot_hashes=False), "CONDITION_DESIGN_REQUIRES_VALID_PRECONDITION_SNAPSHOT")

    def test_snapshot_identity_mismatch(self):
        self.assert_rule(self.build(snapshot=lambda s: s.update(design_id="other")),
                         "CONDITION_DESIGN_REQUIRES_VALID_PRECONDITION_SNAPSHOT")

    def test_frozen_readiness_claims_not_blocked(self):
        self.assert_rule(self.build(frozen_readiness=lambda r: r.update(readiness_status="ready")),
                         "CONDITION_DESIGN_REQUIRES_VALID_PRECONDITION_SNAPSHOT")

    def test_frozen_readiness_target_not_open(self):
        self.assert_rule(self.build(frozen_readiness=lambda r: r.update(blockers=[])),
                         "CONDITION_DESIGN_REQUIRES_VALID_PRECONDITION_SNAPSHOT")

    def test_frozen_gate_allows_execution(self):
        self.assert_rule(self.build(frozen_gate=lambda g: g.update(run_004_execution_allowed=True)),
                         "CONDITION_DESIGN_REQUIRES_VALID_PRECONDITION_SNAPSHOT")

    def test_snapshot_captured_at_impossible(self):
        self.assert_rule(self.build(snapshot=lambda s: s.update(captured_at="2026-99-99T00:00:00Z")),
                         "CONDITION_DESIGN_REQUIRES_VALID_PRECONDITION_SNAPSHOT")

    def test_old_reduced_gate_list_is_schema_error(self):
        # §4.1: a snapshot that carries its own reduced gate list is rejected by the closed schema.
        self.assert_exit(self.build(snapshot=lambda s: s.update(required_control_dimensions=[])), 2)

    # --- gate subset (exit 1) ---
    def test_gate_required_dimension_missing(self):
        self.assert_rule(self.build(design=lambda d: d.update(
            controlled_dimensions=[x for x in d["controlled_dimensions"] if x["id"] != "test_harness"])),
            "CONDITION_DESIGN_REQUIRES_GATE_REQUIREMENTS_SUBSET")

    def test_gate_confounder_weakened(self):
        def mut(d):
            for c in d["confounder_controls"]:
                if c["id"] == "multi_axis_drift":
                    c["effect_if_uncontrolled"] = "must_be_reported"
        self.assert_rule(self.build(design=mut), "CONDITION_DESIGN_REQUIRES_GATE_REQUIREMENTS_SUBSET")

    # --- input assembly ---
    def test_assembly_order_wrong_is_schema_error(self):
        self.assert_exit(self.build(design=lambda d: d["condition_input_assembly"]["arms"]["control"].update(
            composition_order=["shared_condition", "benchmark", "arm_overlay"])), 2)

    def test_assembly_missing_benchmark_is_schema_error(self):
        self.assert_exit(self.build(design=lambda d: d["condition_input_assembly"]["arms"]["control"].update(
            composition_order=["shared_condition", "arm_overlay"])), 2)

    def test_assembly_duplicate_element_is_schema_error(self):
        self.assert_exit(self.build(design=lambda d: d["condition_input_assembly"]["arms"]["treatment"].update(
            composition_order=["benchmark", "benchmark", "arm_overlay"])), 2)

    def test_assembly_control_uses_treatment_overlay(self):
        def mut(d):
            t = d["condition_input_assembly"]["arms"]["treatment"]["overlay_ref"]
            d["condition_input_assembly"]["arms"]["control"]["overlay_ref"] = t
        self.assert_rule(self.build(design=mut), "CONDITION_DESIGN_REQUIRES_INPUT_ASSEMBLY")

    def test_assembly_benchmark_not_frozen_challenge(self):
        def mut(d):
            d["condition_input_assembly"]["components"]["benchmark"]["ref"] = d["condition_input_assembly"]["components"]["shared_condition"]["ref"]
        self.assert_rule(self.build(design=mut), "CONDITION_DESIGN_REQUIRES_INPUT_ASSEMBLY")

    # --- single axis ---
    def test_overlay_smuggles_extra_axis(self):
        # An overlay hand-edited to differ from the rendered structured source is rejected.
        def design(d):
            pass
        c = self.build(design=design, rerender=False)
        # overwrite the committed control overlay with an extra line, keep freeze consistent
        tmp = c.parent
        (tmp / "control-workflow-protocol.md").write_text(
            (tmp / "control-workflow-protocol.md").read_text() + "\nUse any extra tools you like.\n")
        # recompute freeze so only the render check fails
        man = yaml.safe_load((tmp / "freeze-manifest.yml").read_text())
        for h in man["hashes"]:
            if h["path"].endswith("control-workflow-protocol.md"):
                h["sha256"] = _sha(tmp / "control-workflow-protocol.md")
        (tmp / "freeze-manifest.yml").write_text(yaml.safe_dump(man, sort_keys=False, allow_unicode=True))
        self.assert_rule(self.run_v(c), "CONDITION_DESIGN_REQUIRES_SINGLE_AXIS_RENDER")

    def test_workflow_unknown_arm_field_is_schema_error(self):
        self.assert_exit(self.build(workflow=lambda w: w["arms"]["control"].update(extra_tool="x")), 2)

    def test_arms_same_protocol(self):
        self.assert_rule(self.build(design=lambda d: next(a for a in d["arms"] if a["role"] == "treatment").update(workflow_protocol="direct_implementation")),
                         "CONDITION_DESIGN_REQUIRES_SINGLE_PRIMARY_AXIS")

    def test_primary_axis_in_controlled(self):
        def mut(d):
            d["controlled_dimensions"].append({"id": "workflow_protocol", "control_method": "x",
                "binding_status": "bound_at_design", "binding_source": "x",
                "same_value_across_arms_required": True, "blocking_divergence": "x"})
        self.assert_rule(self.build(design=mut), "CONDITION_DESIGN_REQUIRES_PRIMARY_AXIS_NOT_CONTROLLED")

    def test_material_contrast_treatment_no_spec(self):
        def mut(w):
            w["arms"]["treatment"] = {"pre_implementation_specification_required": False,
                "implementation_may_begin_immediately": True,
                "specification_completeness_check_required": False, "required_specification_sections": []}
        self.assert_rule(self.build(workflow=mut), "CONDITION_DESIGN_REQUIRES_MATERIAL_CONTRAST")

    # --- verification (schema-closed) ---
    def test_verification_control_only_tests_schema_error(self):
        self.assert_exit(self.build(verification=lambda v: v.update(control_only_tests=["x"])), 2)

    def test_verification_executes_schema_error(self):
        self.assert_exit(self.build(verification=lambda v: v.update(does_not_execute=False)), 2)

    # --- measurement (schema + semantic) ---
    def test_measurement_observed_values_schema_error(self):
        self.assert_exit(self.build(measurement=lambda m: m.update(observed_values={"control": 1})), 2)

    def test_measurement_ratio_inverted_range(self):
        self.assert_rule(self.build(measurement=lambda m: m["primary_metrics"][0].update(range={"minimum": 9, "maximum": -3})),
                         "CONDITION_DESIGN_REQUIRES_SHARED_MEASUREMENT")

    def test_measurement_duplicate_metric_id(self):
        self.assert_rule(self.build(measurement=lambda m: m["secondary_metrics"][0].update(id="functional_test_pass_ratio", unit="count", formula="x")),
                         "CONDITION_DESIGN_REQUIRES_SHARED_MEASUREMENT")

    def test_measurement_missing_formula_schema_error(self):
        self.assert_exit(self.build(measurement=lambda m: m["primary_metrics"][0].pop("formula")), 2)

    def test_measurement_abort_time_not_modeled(self):
        def mut(m):
            for x in m["primary_metrics"]:
                if x["id"] == "time_to_validated_change_seconds":
                    x["value_if_aborted_before_pass"] = "stop_time"
        self.assert_rule(self.build(measurement=mut), "CONDITION_DESIGN_REQUIRES_SHARED_MEASUREMENT")

    # --- assigned vs observed ---
    def test_treatment_process_artifact_missing(self):
        self.assert_rule(self.build(design=lambda d: d["artifact_surfaces"]["arm_specific_process_artifacts"].update(treatment=[])),
                         "CONDITION_DESIGN_REQUIRES_ASSIGNED_VS_OBSERVED_SEPARATION")

    # --- self identity / bundle / arms ---
    def test_wrong_self_path(self):
        self.assert_rule(self.build(design=lambda d: d.update(design_artifact_path=FIX_PRE + "common-condition.md")),
                         "CONDITION_DESIGN_REQUIRES_DESIGN_SELF_IDENTITY")

    def test_child_outside_bundle(self):
        self.assert_rule(self.build(design=lambda d: d["verification_surface"].update(protocol_ref=FIX_PRE + "verification-protocol.yml")),
                         "CONDITION_DESIGN_REQUIRES_BUNDLE_BOUNDARY")

    def test_duplicate_arm_role(self):
        self.assert_rule(self.build(design=lambda d: next(a for a in d["arms"] if a["role"] == "treatment").update(role="control")),
                         "CONDITION_DESIGN_REQUIRES_EXACTLY_TWO_ARMS")

    # --- recursive execution artifacts ---
    def test_nested_execution_artifacts(self):
        for label, plant in {"run_yml": {"nested/run.yml": "x\n"}, "impl_dir": {"nested/implementation": None},
                             "src_dir": {"deep/src": None}, "execute_py": {"a/b/execute-run.py": "x\n"},
                             "verify_py": {"a/b/verify-run.py": "x\n"}}.items():
            with self.subTest(case=label):
                self.assert_rule(self.run_v(self.build(plant=plant)), "CONDITION_DESIGN_FORBIDS_EXECUTION_ARTIFACTS")

    # --- freeze ---
    def test_freeze_impossible_date(self):
        self.assert_rule(self.build(freeze=lambda m, p: m.update(frozen_at="2026-99-99T99:99:99Z")),
                         "CONDITION_DESIGN_REQUIRES_VALID_FREEZE")

    def test_freeze_captured_after_frozen(self):
        self.assert_rule(self.build(freeze=lambda m, p: m.update(frozen_at="2020-01-01T00:00:00Z")),
                         "CONDITION_DESIGN_REQUIRES_VALID_FREEZE")

    def test_freeze_hidden_commit_key_schema_error(self):
        self.assert_exit(self.build(freeze=lambda m, p: m.update(repository_commit_sha="a" * 40)), 2)

    def test_freeze_missing_source_snapshot(self):
        self.assert_rule(self.build(freeze=lambda m, p: m.update(hashes=[h for h in m["hashes"] if "source-snapshots" not in h["path"]])),
                         "CONDITION_DESIGN_REQUIRES_VALID_FREEZE")

    def test_freeze_duplicate_path(self):
        self.assert_rule(self.build(freeze=lambda m, p: m["hashes"].append(dict(m["hashes"][0]))),
                         "CONDITION_DESIGN_REQUIRES_VALID_FREEZE")

    def test_freeze_self_hash(self):
        self.assert_rule(self.build(freeze=lambda m, p: m["hashes"].append({"path": p + "freeze-manifest.yml", "sha256": "0" * 64})),
                         "CONDITION_DESIGN_REQUIRES_VALID_FREEZE")

    def test_freeze_bad_base_commit_schema_error(self):
        self.assert_exit(self.build(freeze=lambda m, p: m.update(source_base_commit_sha="banana")), 2)

    # --- non-claims ---
    def test_missing_non_claim(self):
        c = self.build(design=lambda d: d["does_not_establish"].remove("single_paired_execution_establishes_condition_effect"))
        self.assert_rule(self.run_v(c), "CONDITION_DESIGN_REQUIRES_MANDATORY_NON_CLAIMS")

    def test_denied_selection_claim(self):
        c = self.build(design=lambda d: d["does_not_establish"].append("primary_intervention_axis_selected"))
        self.assert_rule(self.run_v(c), "CONDITION_DESIGN_REQUIRES_MANDATORY_NON_CLAIMS")

    # --- main schema const ---
    def _schema_mut(self, mutate):
        d = yaml.safe_load((VB / "condition-design.yml").read_text())
        mutate(d)
        with tempfile.TemporaryDirectory() as t:
            f = Path(t) / "condition-design.yml"
            f.write_text(yaml.safe_dump(d, sort_keys=False, allow_unicode=True))
            return self.run_v(f)

    def test_main_schema_consts(self):
        for label, mut in [
            ("design_status", lambda d: d.update(design_status="draft")),
            ("run_exec", lambda d: d.update(run_004_execution_allowed=True)),
            ("exec_binding", lambda d: d.update(execution_binding_status="bound")),
            ("axis_semantics", lambda d: d["primary_intervention_axis"].update(semantics="enforced_thought")),
            ("input_claim", lambda d: d.update(condition_input_claim="identical_full_input")),
            ("unknown_top", lambda d: d.update(winner="treatment")),
        ]:
            with self.subTest(case=label):
                self.assert_exit(self._schema_mut(mut), 2)

    def test_schema_accepts_unicode(self):
        v = Draft202012Validator(json.loads(SCHEMA.read_text()))
        d = yaml.safe_load((VB / "condition-design.yml").read_text())
        d["summary"] = "Mehrzeiliger\nText 日本語."
        self.assertEqual([], list(v.iter_errors(d)))

    def test_resolver_rejects_unsafe(self):
        mod = runpy.run_path(str(VALIDATOR), run_name="cd_mod")
        resolve = mod["resolve_repo_relative_path"]
        for val in ("a\x00b", "a\tb", "../x", "/abs", "C:/x", "a\\b", " lead", "trail "):
            with self.subTest(v=ascii(val)):
                r, code = resolve(val, REPO_ROOT, must_exist=False)
                self.assertIsNone(r); self.assertEqual("ESCAPE", code)


if __name__ == "__main__":
    unittest.main(verbosity=2)
