#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("audit_prospective_cohort.py")
spec = importlib.util.spec_from_file_location("operator_routing_shadow_gate", MODULE_PATH)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

CRITERIA_PATH = MODULE_PATH.parents[1] / "readiness-gate.v1.json"
CRITERIA = json.loads(CRITERIA_PATH.read_text(encoding="utf-8"))


class ProspectiveCohortAuditTests(unittest.TestCase):
    def _roots(self, tmp: str) -> tuple[Path, Path]:
        base = Path(tmp)
        cohort = base / "cohort"
        workspaces = base / "workspaces"
        for category in module.CATEGORIES:
            (cohort / category).mkdir(parents=True, exist_ok=True)
        workspaces.mkdir()
        return cohort, workspaces

    def _write(self, path: Path, value: dict) -> None:
        path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def _criteria_without_structural_capture_gaps(self) -> dict:
        criteria = dict(CRITERIA)
        criteria["require_disagreement_observability_for_pass"] = False
        criteria["require_test_quarantine_provenance_for_pass"] = False
        criteria["require_execution_failure_provenance_for_pass"] = False
        return criteria

    def _case(self, cohort: Path, workspaces: Path, index: int) -> None:
        workspace_id = f"gaw-test-{index:02d}"
        recommendation_id = module.hashlib.sha256(f"recommendation-{index}".encode()).hexdigest()
        plan_sha256 = module.hashlib.sha256(f"plan-{index}".encode()).hexdigest()
        route = {
            "schema_version": 2,
            "recommendation_id": recommendation_id,
            "actual_route": "full_workspace",
            "recommended_route": "full_workspace",
            "risk_tier": "R2",
            "input_facts": {
                "task_kind": "code",
                "changed_file_estimate": 2,
                "expected_duration_minutes": 30,
                "novelty": "medium",
                "risk_flags": [],
                "connector_instability": False,
                "user_requested_external": False,
                "concurrent_external_activity": False,
                "parallelization_candidate": False,
                "decision_fork": False,
                "architecture_hypotheses": 1,
            },
        }
        manifest = {
            "workspace_id": workspace_id,
            "plan_sha256": plan_sha256,
            "repository": "/example/repo-a",
            "route_evidence": route,
        }
        workspace = workspaces / workspace_id
        workspace.mkdir()
        self._write(workspace / "manifest.json", manifest)
        route_ref = {
            "source": "agent-workspace-manifest",
            "schema_version": 2,
            "recommendation_id": recommendation_id,
            "route_evidence_sha256": module._sha256_json(route),
            "manifest_sha256": module._sha256_json(manifest),
        }
        workspace_case_id = module._workspace_case_id(
            workspace_id, plan_sha256, route_ref["route_evidence_sha256"]
        )
        frozen_at = "2026-07-23T10:00:00Z"
        prospective_payload = {
            "schema_version": module.PROSPECTIVE_SCHEMA,
            "workspace_case": {
                "workspace_id": workspace_id,
                "plan_sha256": plan_sha256,
                "case_id": workspace_case_id,
            },
            "canonical_route_evidence": route_ref,
            "features": module._bounded_features(route),
            "frozen_at": frozen_at,
            "no_effect": dict(module.NO_EFFECT),
        }
        prospective = {
            "prospective_eligibility_id": module._sha256_json(prospective_payload),
            **prospective_payload,
        }
        prospective_id = prospective["prospective_eligibility_id"]
        self._write(cohort / "prospective" / f"{index}.json", prospective)

        task_id = f"{index + 1:024x}"
        case_id = module._case_id(task_id, recommendation_id)
        eligibility_payload = {
            "schema_version": module.ELIGIBILITY_SCHEMA,
            "prospective_eligibility": {
                "schema_version": module.PROSPECTIVE_SCHEMA,
                "prospective_eligibility_id": prospective_id,
                "workspace_id": workspace_id,
                "plan_sha256": plan_sha256,
                "workspace_case_id": workspace_case_id,
                "frozen_at": frozen_at,
            },
            "eligible_case": {"task_id": task_id, "case_id": case_id},
            "canonical_route_evidence": route_ref,
            "features": dict(prospective["features"]),
            "frozen_at": frozen_at,
            "no_effect": dict(module.NO_EFFECT),
        }
        eligibility = {"eligibility_id": module._sha256_json(eligibility_payload), **eligibility_payload}
        self._write(cohort / "eligibility" / f"{index}.json", eligibility)

        record_payload = {
            "schema_version": module.RECORD_SCHEMA,
            "eligibility": {
                "schema_version": module.ELIGIBILITY_SCHEMA,
                "eligibility_id": eligibility["eligibility_id"],
                "prospective_eligibility_id": prospective_id,
                "frozen_at": frozen_at,
            },
            "eligible_case": dict(eligibility["eligible_case"]),
            "canonical_route_evidence": route_ref,
            "features": dict(prospective["features"]),
            "outcome": {
                "status": "reviewed",
                "kind": "task_correctness",
                "label": "success",
                "observed_at": "2026-07-23T11:00:00Z",
                "review_authority": "diff_bound_review",
            },
            "primary_evidence_refs": ["diff-review:fixture"],
            "captured_at": "2026-07-23T12:00:00Z",
            "no_effect": dict(module.NO_EFFECT),
        }
        record = {"record_id": module._sha256_json(record_payload), **record_payload}
        self._write(cohort / "records" / f"{index}.json", record)

        attempt_payload = {
            "schema_version": module.ATTEMPT_SCHEMA,
            "workspace_id": workspace_id,
            "plan_sha256": plan_sha256,
            "stage": "prospective_eligibility_freeze",
            "status": "created",
            "reason_code": "eligible_verified_route",
            "prospective_eligibility_id": prospective_id,
            "attempted_at": frozen_at,
            "no_effect": dict(module.NO_EFFECT),
        }
        attempt = {"attempt_id": module._sha256_json(attempt_payload), **attempt_payload}
        self._write(cohort / "attempts" / f"{index}.json", attempt)

    def test_empty_live_shape_requires_continued_collection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cohort, workspaces = self._roots(tmp)
            report = module.audit(cohort, workspaces, CRITERIA)
            self.assertEqual(report["gate_result"], "CONTINUE-COLLECTING")
            self.assertEqual(report["counts"]["prospective"], 0)
            self.assertEqual(report["quality"]["integrity_error_count"], 0)
            self.assertIn("minimum_treatment_cases_not_met", report["gate_reasons"])
            self.assertIn("semantic_reviewer_disagreement_unobservable", report["gate_reasons"])
            self.assertIn("test_quarantine_provenance_unobservable", report["gate_reasons"])
            self.assertIn("execution_failure_provenance_unobservable", report["gate_reasons"])
            self.assertFalse(report["outcomes"]["semantic_review_disagreement"]["observable"])
            self.assertIsNone(report["cohort_provenance"]["test_or_quarantine_contamination_count"])

    def test_twenty_complete_integrity_bound_cases_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cohort, workspaces = self._roots(tmp)
            for index in range(20):
                self._case(cohort, workspaces, index)
            report = module.audit(
                cohort, workspaces, self._criteria_without_structural_capture_gaps()
            )
            self.assertEqual(report["gate_result"], "PASS")
            self.assertEqual(report["quality"]["direct_route_plus_reviewed_outcome_completeness_percent"], 100.0)
            self.assertEqual(report["quality"]["integrity_error_count"], 0)
            self.assertEqual(report["quality"]["attempt_accounting_gap_count"], 0)
            self.assertEqual(report["coverage"]["dimensions"]["actual_route"], {"full_workspace": 20})
            self.assertFalse(report["privacy_and_effect_boundary"]["raw_workspace_or_task_ids_exported"])

    def test_multiple_task_cases_for_one_prospective_count_separately(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cohort, workspaces = self._roots(tmp)
            for index in range(20):
                self._case(cohort, workspaces, index)
            prospective = json.loads((cohort / "prospective" / "0.json").read_text(encoding="utf-8"))
            route_ref = prospective["canonical_route_evidence"]
            task_id = "f" * 24
            case_id = module._case_id(task_id, route_ref["recommendation_id"])
            eligibility_payload = {
                "schema_version": module.ELIGIBILITY_SCHEMA,
                "prospective_eligibility": {
                    "schema_version": module.PROSPECTIVE_SCHEMA,
                    "prospective_eligibility_id": prospective["prospective_eligibility_id"],
                    "workspace_id": prospective["workspace_case"]["workspace_id"],
                    "plan_sha256": prospective["workspace_case"]["plan_sha256"],
                    "workspace_case_id": prospective["workspace_case"]["case_id"],
                    "frozen_at": prospective["frozen_at"],
                },
                "eligible_case": {"task_id": task_id, "case_id": case_id},
                "canonical_route_evidence": dict(route_ref),
                "features": dict(prospective["features"]),
                "frozen_at": prospective["frozen_at"],
                "no_effect": dict(module.NO_EFFECT),
            }
            eligibility = {"eligibility_id": module._sha256_json(eligibility_payload), **eligibility_payload}
            self._write(cohort / "eligibility" / "extra.json", eligibility)
            record_payload = {
                "schema_version": module.RECORD_SCHEMA,
                "eligibility": {
                    "schema_version": module.ELIGIBILITY_SCHEMA,
                    "eligibility_id": eligibility["eligibility_id"],
                    "prospective_eligibility_id": prospective["prospective_eligibility_id"],
                    "frozen_at": prospective["frozen_at"],
                },
                "eligible_case": dict(eligibility["eligible_case"]),
                "canonical_route_evidence": dict(route_ref),
                "features": dict(prospective["features"]),
                "outcome": {
                    "status": "reviewed",
                    "kind": "task_correctness",
                    "label": "success",
                    "observed_at": "2026-07-23T11:30:00Z",
                    "review_authority": "diff_bound_review",
                },
                "primary_evidence_refs": ["diff-review:extra-fixture"],
                "captured_at": "2026-07-23T12:30:00Z",
                "no_effect": dict(module.NO_EFFECT),
            }
            record = {"record_id": module._sha256_json(record_payload), **record_payload}
            self._write(cohort / "records" / "extra.json", record)
            report = module.audit(
                cohort, workspaces, self._criteria_without_structural_capture_gaps()
            )
            self.assertEqual(report["gate_result"], "PASS")
            self.assertEqual(report["counts"]["eligible_treatment_cases"], 21)
            self.assertEqual(report["counts"]["complete_records"], 21)
            self.assertEqual(report["counts"]["complete_treatment_cases"], 21)
            self.assertEqual(report["counts"]["prospective_cases_with_multiple_eligibilities"], 1)
            self.assertEqual(report["quality"]["direct_route_plus_reviewed_outcome_completeness_percent"], 100.0)

    def test_mutated_workspace_manifest_keeps_frozen_route_binding_verifiable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cohort, workspaces = self._roots(tmp)
            for index in range(20):
                self._case(cohort, workspaces, index)
            path = workspaces / "gaw-test-00" / "manifest.json"
            manifest = json.loads(path.read_text(encoding="utf-8"))
            manifest["tasks"] = {"writer": "000000000000000000000001"}
            self._write(path, manifest)
            report = module.audit(
                cohort, workspaces, self._criteria_without_structural_capture_gaps()
            )
            self.assertEqual(report["gate_result"], "PASS")
            self.assertEqual(report["quality"]["unresolved_manifest_binding_count"], 0)

    def test_eligibility_prospective_reference_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cohort, workspaces = self._roots(tmp)
            for index in range(20):
                self._case(cohort, workspaces, index)
            path = cohort / "eligibility" / "0.json"
            eligibility = json.loads(path.read_text(encoding="utf-8"))
            eligibility["prospective_eligibility"]["workspace_case_id"] = "0" * 64
            payload = {key: eligibility[key] for key in eligibility if key != "eligibility_id"}
            eligibility["eligibility_id"] = module._sha256_json(payload)
            self._write(path, eligibility)
            report = module.audit(cohort, workspaces, CRITERIA)
            self.assertEqual(report["gate_result"], "FAIL")
            self.assertEqual(report["errors"]["eligibility:prospective_reference_mismatch"], 1)

    def test_record_route_binding_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cohort, workspaces = self._roots(tmp)
            for index in range(20):
                self._case(cohort, workspaces, index)
            path = cohort / "records" / "0.json"
            record = json.loads(path.read_text(encoding="utf-8"))
            record["canonical_route_evidence"]["manifest_sha256"] = "f" * 64
            payload = {key: record[key] for key in record if key != "record_id"}
            record["record_id"] = module._sha256_json(payload)
            self._write(path, record)
            report = module.audit(cohort, workspaces, CRITERIA)
            self.assertEqual(report["gate_result"], "FAIL")
            self.assertEqual(report["errors"]["records:eligibility_binding_mismatch"], 1)

    def test_route_feature_binding_mismatch_blocks_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cohort, workspaces = self._roots(tmp)
            for index in range(20):
                self._case(cohort, workspaces, index)
            prospective_path = cohort / "prospective" / "0.json"
            prospective = json.loads(prospective_path.read_text(encoding="utf-8"))
            prospective["features"]["changed_file_estimate"] = 99
            payload = {key: prospective[key] for key in prospective if key != "prospective_eligibility_id"}
            prospective["prospective_eligibility_id"] = module._sha256_json(payload)
            self._write(prospective_path, prospective)

            eligibility_path = cohort / "eligibility" / "0.json"
            eligibility = json.loads(eligibility_path.read_text(encoding="utf-8"))
            eligibility["prospective_eligibility"]["prospective_eligibility_id"] = prospective[
                "prospective_eligibility_id"
            ]
            eligibility["features"] = dict(prospective["features"])
            eligibility_payload = {key: eligibility[key] for key in eligibility if key != "eligibility_id"}
            eligibility["eligibility_id"] = module._sha256_json(eligibility_payload)
            self._write(eligibility_path, eligibility)

            report = module.audit(cohort, workspaces, CRITERIA)
            self.assertNotEqual(report["gate_result"], "PASS")
            self.assertEqual(report["quality"]["unresolved_manifest_binding_count"], 1)
            self.assertEqual(report["coverage"]["unresolved_manifest_reasons"], {"route_feature_binding_mismatch": 1})

    def test_no_effect_violation_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cohort, workspaces = self._roots(tmp)
            self._case(cohort, workspaces, 0)
            path = cohort / "records" / "0.json"
            record = json.loads(path.read_text(encoding="utf-8"))
            record["no_effect"]["routing"] = True
            payload = {key: record[key] for key in record if key != "record_id"}
            record["record_id"] = module._sha256_json(payload)
            self._write(path, record)
            report = module.audit(cohort, workspaces, CRITERIA)
            self.assertEqual(report["gate_result"], "FAIL")
            self.assertGreater(report["quality"]["no_effect_violation_count"], 0)
            self.assertIn("no_effect_violation", report["gate_reasons"])

    def test_duplicate_prospective_identity_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cohort, workspaces = self._roots(tmp)
            for index in range(20):
                self._case(cohort, workspaces, index)
            duplicate = json.loads((cohort / "prospective" / "0.json").read_text(encoding="utf-8"))
            self._write(cohort / "prospective" / "duplicate.json", duplicate)
            report = module.audit(cohort, workspaces, CRITERIA)
            self.assertEqual(report["gate_result"], "FAIL")
            self.assertEqual(report["errors"]["prospective:duplicate_identity"], 1)
            self.assertGreater(report["quality"]["integrity_error_count"], 0)

    def test_capture_rejection_prevents_pass_pending_bias_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cohort, workspaces = self._roots(tmp)
            for index in range(20):
                self._case(cohort, workspaces, index)
            path = cohort / "attempts" / "0.json"
            attempt = json.loads(path.read_text(encoding="utf-8"))
            attempt["status"] = "rejected"
            attempt["reason_code"] = "ineligible_route_evidence"
            payload = {key: attempt[key] for key in attempt if key != "attempt_id"}
            attempt["attempt_id"] = module._sha256_json(payload)
            self._write(path, attempt)
            report = module.audit(cohort, workspaces, CRITERIA)
            self.assertEqual(report["gate_result"], "CONTINUE-COLLECTING")
            self.assertEqual(report["quality"]["capture_rejection_count"], 1)
            self.assertIn("capture_rejections_require_selection_bias_review", report["gate_reasons"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
