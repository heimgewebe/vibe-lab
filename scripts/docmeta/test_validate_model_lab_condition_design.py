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
import os
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
BASE_COMMIT = "41fa2031160f6a7288f2c90eaccff60c7c1b50f2"
_R = runpy.run_path(str(RENDERER), run_name="cd_renderer")
_render_shared = _R["render_shared_condition"]
_render_overlay = _R["render_arm_overlay"]
_extract_body = _R["extract_instruction_body"]


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
              freeze=None, frozen_gate=None, frozen_readiness=None, plant=None, snapshot_files=None,
              rerender=True, recompute_snapshot_hashes=True, recompute_freeze=True) -> Path:
        tmp = Path(tempfile.mkdtemp(prefix="_scratch_", dir=FIXROOT))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        (tmp / "source-snapshots").mkdir()
        for f in ALL_FILES:
            shutil.copy(VB / f, tmp / f)
        if snapshot_files:  # overwrite frozen-source bytes BEFORE hashes/render/freeze recompute
            for rel, content in snapshot_files.items():
                (tmp / rel).write_bytes(content if isinstance(content, bytes) else content.encode())
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
            basis = (tmp / "source-snapshots" / "spec-first.snapshot").read_text()
            (tmp / "common-condition.md").write_bytes(_render_shared(wf).encode("utf-8"))
            (tmp / "control-workflow-protocol.md").write_bytes(_render_overlay(wf, "control").encode("utf-8"))
            (tmp / "treatment-workflow-protocol.md").write_bytes(_render_overlay(wf, "treatment", basis).encode("utf-8"))

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
                   "frozen_before_execution": True, "source_base_commit_sha": BASE_COMMIT,
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
        self.assert_exit(self.build(workflow=lambda w: w["control_metadata"]["arms"]["control"].update(extra_tool="x")), 2)

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
            w["control_metadata"]["arms"]["treatment"] = {
                "pre_implementation_specification_required": False,
                "implementation_may_begin_immediately": True,
                "specification_completeness_check_required": False}
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
        def mut(d):
            t = next(a for a in d["arms"] if a["role"] == "treatment")
            t["role"] = "control"
            t.pop("spec_first_basis", None)  # control role forbids grounding (else it's a schema error)
        self.assert_rule(self.build(design=mut), "CONDITION_DESIGN_REQUIRES_EXACTLY_TWO_ARMS")

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

    # --- overwrite helper + render fixtures (boundary 3/4/§15) ---
    def _overwrite(self, c, rel, content):
        """Overwrite a built bundle file and refresh only its freeze hash, isolating content rules
        (render/blinding/normalization/distinctness) from the freeze check."""
        tmp = c.parent
        p = tmp / rel
        p.write_bytes(content if isinstance(content, bytes) else content.encode("utf-8"))
        man = yaml.safe_load((tmp / "freeze-manifest.yml").read_text())
        for h in man["hashes"]:
            if Path(h["path"]).name == Path(rel).name:
                h["sha256"] = _sha(p)
        (tmp / "freeze-manifest.yml").write_text(yaml.safe_dump(man, sort_keys=False, allow_unicode=True))
        return c

    def _wf(self):
        return yaml.safe_load((VB / "workflow-instruction-protocol.yml").read_text())

    def _basis(self):
        return (VB / "source-snapshots" / "spec-first.snapshot").read_text()

    def _treat(self, d):
        return next(a for a in d["arms"] if a["role"] == "treatment")

    def _ctl(self, d):
        return next(a for a in d["arms"] if a["role"] == "control")

    # === boundary 1: source role / provenance binding ===
    def test_source_path_not_canonical(self):
        self.assert_rule(self.build(snapshot=lambda s: s["sources"]["gate"].update(source_path="benchmarks/challenges/rest-api-v1.md")),
                         "CONDITION_DESIGN_REQUIRES_SOURCE_ROLE_BINDING")

    def test_readiness_source_path_not_canonical(self):
        self.assert_rule(self.build(snapshot=lambda s: s["sources"]["readiness"].update(source_path="instruction-blocks/spec-first.md")),
                         "CONDITION_DESIGN_REQUIRES_SOURCE_ROLE_BINDING")

    def test_gate_artifact_type_wrong(self):
        self.assert_rule(self.build(snapshot=lambda s: s["sources"]["gate"].update(artifact_type="instruction_block")),
                         "CONDITION_DESIGN_REQUIRES_SOURCE_ROLE_BINDING")

    def test_challenge_artifact_type_wrong(self):
        self.assert_rule(self.build(snapshot=lambda s: s["sources"]["challenge"].update(artifact_type="instruction_block")),
                         "CONDITION_DESIGN_REQUIRES_SOURCE_ROLE_BINDING")

    def test_spec_first_artifact_type_wrong(self):
        self.assert_rule(self.build(snapshot=lambda s: s["sources"]["spec_first"].update(artifact_type="benchmark_challenge")),
                         "CONDITION_DESIGN_REQUIRES_SOURCE_ROLE_BINDING")

    def test_challenge_path_incoherent_with_version(self):
        self.assert_rule(self.build(snapshot=lambda s: s["sources"]["challenge"].update(source_path="benchmarks/challenges/other-v9.md")),
                         "CONDITION_DESIGN_REQUIRES_SOURCE_ROLE_BINDING")

    def test_source_commit_unknown_fails_closed(self):
        # a source pointing at a commit absent from the object store cannot be verified -> exit 2
        self.assert_exit(self.build(snapshot=lambda s: s["sources"]["readiness"].update(
            source_commit_sha="deadbeef" * 5)), 2)

    def test_base_commit_drift_breaks_sources(self):
        self.assert_rule(self.build(freeze=lambda m, p: m.update(source_base_commit_sha="a" * 40)),
                         "CONDITION_DESIGN_REQUIRES_SOURCE_ROLE_BINDING")

    # === boundary 2: prompt-component role binding ===
    def test_shared_condition_not_common_condition(self):
        self.assert_rule(self.build(design=lambda d: d["condition_input_assembly"]["components"]["shared_condition"].update(
            ref=d["condition_input_assembly"]["components"]["benchmark"]["ref"])),
            "CONDITION_DESIGN_REQUIRES_INPUT_ASSEMBLY")

    def test_treatment_missing_spec_first_basis_is_schema_error(self):
        self.assert_exit(self.build(design=lambda d: self._treat(d).pop("spec_first_basis", None)), 2)

    def test_control_has_spec_first_basis_is_schema_error(self):
        def mut(d):
            self._ctl(d)["spec_first_basis"] = {"snapshot_ref": self._treat(d)["spec_first_basis"]["snapshot_ref"]}
        self.assert_exit(self.build(design=mut), 2)

    def test_treatment_grounding_wrong_snapshot(self):
        def mut(d):
            self._treat(d)["spec_first_basis"]["snapshot_ref"] = d["condition_input_assembly"]["components"]["benchmark"]["ref"]
        self.assert_rule(self.build(design=mut), "CONDITION_DESIGN_REQUIRES_SPEC_FIRST_BASIS")

    def test_arm_spec_first_basis_unknown_field_is_schema_error(self):
        self.assert_exit(self.build(design=lambda d: self._treat(d)["spec_first_basis"].update(extra="x")), 2)

    def test_operative_files_not_distinct(self):
        c = self.build()
        self._overwrite(c, "common-condition.md", (c.parent / "control-workflow-protocol.md").read_bytes())
        self.assert_rule(self.run_v(c), "CONDITION_DESIGN_REQUIRES_OPERATIVE_FILE_DISTINCTNESS")

    # === boundary 3: blinding the delivered prompt ===
    def test_shared_condition_leaks_role_word(self):
        c = self.build()
        self._overwrite(c, "common-condition.md", "# Task\n\nThe control arm must do X.\n")
        self.assert_rule(self.run_v(c), "CONDITION_DESIGN_REQUIRES_BLINDED_PROMPT")

    def test_overlay_leaks_experiment_word(self):
        c = self.build()
        self._overwrite(c, "control-workflow-protocol.md", "# Procedure\n\nThis experiment proceeds now.\n")
        self.assert_rule(self.run_v(c), "CONDITION_DESIGN_REQUIRES_BLINDED_PROMPT")

    def test_overlay_leaks_axis_word(self):
        c = self.build()
        self._overwrite(c, "treatment-workflow-protocol.md",
                        "# Procedure\n\nThe primary axis selects the specification.\n")
        self.assert_rule(self.run_v(c), "CONDITION_DESIGN_REQUIRES_BLINDED_PROMPT")

    def test_shared_condition_render_mismatch_clean(self):
        # clean text (no leaks) that simply is not the deterministic render -> single-axis render rule
        c = self.build()
        self._overwrite(c, "common-condition.md", "# Task\n\nDo the task as described.\n")
        self.assert_rule(self.run_v(c), "CONDITION_DESIGN_REQUIRES_SINGLE_AXIS_RENDER")

    def test_treatment_overlay_render_mismatch_clean(self):
        c = self.build()
        self._overwrite(c, "treatment-workflow-protocol.md",
                        "# Procedure\n\nCarry out the task using the materials provided above.\n\nProvide a specification.\n")
        self.assert_rule(self.run_v(c), "CONDITION_DESIGN_REQUIRES_SINGLE_AXIS_RENDER")

    # === boundary 4: control = absence of an added requirement ===
    def test_control_overlay_mentions_specification(self):
        c = self.build()
        self._overwrite(c, "control-workflow-protocol.md", "# Procedure\n\nWrite a full specification first.\n")
        self.assert_rule(self.run_v(c), "CONDITION_DESIGN_REQUIRES_CONTROL_ABSENCE")

    def test_control_overlay_negative_instruction(self):
        c = self.build()
        self._overwrite(c, "control-workflow-protocol.md",
                        "# Procedure\n\nBegin implementation immediately and skip planning.\n")
        self.assert_rule(self.run_v(c), "CONDITION_DESIGN_REQUIRES_CONTROL_ABSENCE")

    def test_treatment_overlay_without_specification(self):
        c = self.build()
        self._overwrite(c, "treatment-workflow-protocol.md",
                        "# Procedure\n\nCarry out the task using the materials provided above.\n\nProceed now.\n")
        self.assert_rule(self.run_v(c), "CONDITION_DESIGN_REQUIRES_CONTROL_ABSENCE")

    # === §15: text normalization ===
    def test_delivered_file_crlf(self):
        c = self.build()
        self._overwrite(c, "common-condition.md", b"# Task\r\n\r\nDo the task.\r\n")
        self.assert_rule(self.run_v(c), "CONDITION_DESIGN_REQUIRES_TEXT_NORMALIZATION")

    def test_delivered_file_no_final_newline(self):
        c = self.build()
        self._overwrite(c, "control-workflow-protocol.md",
                        b"# Procedure\n\nCarry out the task using the materials provided above.")
        self.assert_rule(self.run_v(c), "CONDITION_DESIGN_REQUIRES_TEXT_NORMALIZATION")

    def test_delivered_file_invalid_utf8(self):
        c = self.build()
        self._overwrite(c, "common-condition.md", b"# Task\n\n\xff\xfe not utf8\n")
        self.assert_rule(self.run_v(c), "CONDITION_DESIGN_REQUIRES_TEXT_NORMALIZATION")

    # === schema: new structure ===
    def test_promptscope_missing_bundled_axis_is_schema_error(self):
        self.assert_exit(self._schema_mut(lambda d: d["prompt_scope"].pop("bundled_axis_components")), 2)

    def test_workflow_unknown_delivered_field_is_schema_error(self):
        self.assert_exit(self.build(workflow=lambda w: w["delivered_shared_instructions"].update(extra="x")), 2)

    def test_workflow_missing_control_metadata_is_schema_error(self):
        self.assert_exit(self.build(workflow=lambda w: w.pop("control_metadata")), 2)

    # === renderer unit tests ===
    def test_render_control_is_pure_baseline(self):
        out = _render_overlay(self._wf(), "control")
        self.assertNotIn("specification", out.lower())
        self.assertTrue(out.endswith("\n"))
        self.assertNotIn("\r", out)

    def test_render_treatment_extends_control(self):
        wf = self._wf()
        ctrl = _render_overlay(wf, "control")
        treat = _render_overlay(wf, "treatment", self._basis())
        self.assertTrue(treat.startswith(ctrl))
        self.assertIn("specification", treat.lower())

    def test_render_treatment_embeds_frozen_spec_first(self):
        treat = _render_overlay(self._wf(), "treatment", self._basis())
        self.assertIn("Before generating any code", treat)
        self.assertIn("Never skip the specification step", treat)

    def test_render_treatment_requires_basis(self):
        with self.assertRaises(ValueError):
            _render_overlay(self._wf(), "treatment", None)

    def test_render_delivered_surface_is_blinded(self):
        wf = self._wf()
        for text in (_render_shared(wf), _render_overlay(wf, "control"), _render_overlay(wf, "treatment", self._basis())):
            low = text.lower()
            for bad in ("control", "treatment", "experiment", "axis", "hypothes", "primary", "overlay", "baseline", "contrast"):
                self.assertNotIn(bad, low, f"{bad!r} leaked into delivered text")

    def test_extract_instruction_body_strips_frontmatter(self):
        self.assertEqual("Hello body", _extract_body("---\ntitle: x\n---\n\nHello body\n"))
        self.assertEqual("No frontmatter", _extract_body("No frontmatter\n"))

    # === discovery fail-closed (Patch A) ===
    def test_discovery_includes_matching_path_with_wrong_artifact_type(self):
        mod = runpy.run_path(str(VALIDATOR), run_name="cd_disc")
        discover = mod["discover_artifacts"]
        with tempfile.TemporaryDirectory() as td:
            b = Path(td) / "experiments" / "s" / "artifacts" / "b"
            b.mkdir(parents=True)
            d = yaml.safe_load((VB / "condition-design.yml").read_text())
            d["artifact_type"] = "model_lab_condition_desing"  # typo must NOT hide it
            (b / "condition-design.yml").write_text(yaml.safe_dump(d, sort_keys=False, allow_unicode=True))
            self.assertEqual(1, len(discover(Path(td))))
        # and validating the mistyped artifact is a schema failure, never a green skip
        self.assert_exit(self.build(design=lambda x: x.update(artifact_type="model_lab_condition_desing")), 2)

    def test_no_discovered_condition_design_is_not_success(self):
        mod = runpy.run_path(str(VALIDATOR), run_name="cd_empty")
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual([], mod["discover_artifacts"](Path(td)))
        main = mod["main"]
        main.__globals__["discover_artifacts"] = lambda root: []  # simulate empty discovery
        self.assertEqual(2, main([]))  # empty discovery is a failure, not a green skip

    # === git-object provenance (Patch B) ===
    def test_snapshot_and_all_internal_hashes_cannot_self_attest_to_git_source(self):
        c = self.build(snapshot_files={"source-snapshots/spec-first.snapshot":
            (VB / "source-snapshots/spec-first.snapshot").read_bytes() + b"\nSmuggled extra line.\n"})
        self.assert_rule(self.run_v(c), "CONDITION_DESIGN_REQUIRES_GIT_SOURCE_PROVENANCE")

    def test_git_source_commit_missing_fails_closed(self):
        self.assert_exit(self.build(snapshot=lambda s: s["sources"]["gate"].update(
            source_commit_sha="deadbeef" * 5)), 2)

    def test_git_source_path_missing_fails_closed(self):
        self.assert_rule(self.build(snapshot=lambda s: s["sources"]["spec_first"].update(
            source_path="instruction-blocks/does-not-exist-at-base.md")),
            "CONDITION_DESIGN_REQUIRES_GIT_SOURCE_PROVENANCE")

    def test_real_snapshots_match_declared_git_sources(self):
        self.assert_exit(self.run_v(REAL), 0)  # committed sources match git <commit>:<path>

    # === closed bundle (Patch C) ===
    def test_unknown_extra_bundle_file_is_rejected(self):
        c = self.build()
        (c.parent / "notes").mkdir()
        (c.parent / "notes" / "hidden-instructions.txt").write_text("psst\n")
        self.assert_rule(self.run_v(c), "CONDITION_DESIGN_REQUIRES_CLOSED_BUNDLE")

    def test_unreferenced_source_file_is_rejected(self):
        c = self.build()
        (c.parent / "source-snapshots" / "extra.snapshot").write_text("x\n")
        self.assert_rule(self.run_v(c), "CONDITION_DESIGN_REQUIRES_CLOSED_BUNDLE")

    def test_bundle_symlink_is_rejected(self):
        c = self.build()
        try:
            os.symlink(REPO_ROOT / "AGENTS.md", c.parent / "link-to-agents.md")
        except OSError:
            self.skipTest("symlinks unsupported on this platform")
        self.assert_rule(self.run_v(c), "CONDITION_DESIGN_REQUIRES_CLOSED_BUNDLE")

    def test_freeze_hash_set_matches_closed_bundle_set(self):
        self.assert_rule(self.build(freeze=lambda m, p: m["hashes"].append(
            {"path": p + "source-snapshots/ghost.snapshot", "sha256": "0" * 64})),
            "CONDITION_DESIGN_REQUIRES_CLOSED_BUNDLE")

    # === honest bundled prompt axis (Patch D) ===
    def test_held_constant_and_bundled_axis_components_are_disjoint(self):
        self.assert_rule(self.build(design=lambda d: d["prompt_scope"]["held_constant_across_arms"].append("prompt_length")),
            "CONDITION_DESIGN_REQUIRES_HONEST_PROMPT_SCOPE")

    def test_dishonest_held_constant_tone_is_rejected(self):
        self.assert_rule(self.build(design=lambda d: d["prompt_scope"]["held_constant_across_arms"].append("tone")),
            "CONDITION_DESIGN_REQUIRES_HONEST_PROMPT_SCOPE")

    def test_bundled_axis_contains_actual_prompt_delta_classes(self):
        self.assert_rule(self.build(design=lambda d: d["prompt_scope"]["bundled_axis_components"].remove("prompt_length")),
            "CONDITION_DESIGN_REQUIRES_HONEST_PROMPT_SCOPE")

    def test_prompt_component_effect_isolation_nonclaims_are_required(self):
        self.assert_rule(self.build(design=lambda d: d["does_not_establish"].remove("canonical_spec_first_instruction_effect_isolated")),
            "CONDITION_DESIGN_REQUIRES_HONEST_PROMPT_SCOPE")

    def test_promptscope_missing_effect_attribution_is_schema_error(self):
        self.assert_exit(self._schema_mut(lambda d: d["prompt_scope"].pop("effect_attribution_scope")), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
