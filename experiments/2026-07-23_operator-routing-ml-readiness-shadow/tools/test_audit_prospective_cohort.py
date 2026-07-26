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

    def _v3_direct_case(
        self,
        cohort: Path,
        *,
        index: int,
        origin: str = "production",
        reviewed: bool = True,
        disagree: bool = False,
        execution_unknown: bool = False,
        outcome_label: str | None = None,
        assessment_labels: tuple[str, str] | None = None,
    ) -> Path:
        bindings = cohort / "direct-task-bindings"
        bindings.mkdir(exist_ok=True)
        task_id = f"{index + 1000:024x}"
        workspace_id = f"gaw-direct-task-{task_id}"
        recommendation_id = module.hashlib.sha256(f"v3-recommendation-{index}".encode()).hexdigest()
        route = {
            "schema_version": 2,
            "recommendation_id": recommendation_id,
            "actual_route": "direct_operator",
            "recommended_route": "direct_operator",
            "risk_tier": "R1",
            "input_facts": {
                "task_kind": "code",
                "changed_file_estimate": 1,
                "expected_duration_minutes": 15,
                "novelty": "low",
                "risk_flags": [],
                "connector_instability": False,
                "user_requested_external": False,
                "concurrent_external_activity": False,
                "parallelization_candidate": False,
                "decision_fork": False,
                "architecture_hypotheses": 1,
            },
        }
        route_hash = module._sha256_json(route)
        task_identity = {
            "host_sha256": module.hashlib.sha256(b"host-v3").hexdigest(),
            "argv_sha256": module.hashlib.sha256(f"argv-v3-{index}".encode()).hexdigest(),
            "cwd_sha256": module.hashlib.sha256(b"/example/repo-v3").hexdigest(),
            "resource_keys_sha256": module._sha256_json(["repo:/example/repo-v3"]),
            "runtime_seconds": 60,
        }
        plan_sha256 = module._direct_task_plan_sha256(task_id, task_identity, route)
        route_ref = {
            "source": "direct-task-start",
            "schema_version": 2,
            "recommendation_id": recommendation_id,
            "route_evidence_sha256": route_hash,
            "manifest_identity_sha256": module._manifest_identity_sha256(
                workspace_id, plan_sha256, route_hash, route_source="direct-task-start"
            ),
        }
        workspace_case_id = module._workspace_case_id(
            workspace_id, plan_sha256, route_hash, route_source="direct-task-start"
        )
        provenance = {"case_origin": origin, "capture_path": "direct_task_prestart"}
        frozen_at = "2026-07-24T10:00:00Z"
        prospective_payload = {
            "schema_version": module.PROSPECTIVE_SCHEMA_V2,
            "workspace_case": {
                "workspace_id": workspace_id,
                "plan_sha256": plan_sha256,
                "case_id": workspace_case_id,
            },
            "canonical_route_evidence": route_ref,
            "features": module._bounded_features(route),
            "case_provenance": provenance,
            "frozen_at": frozen_at,
            "no_effect": dict(module.NO_EFFECT),
        }
        prospective = {
            "prospective_eligibility_id": module._sha256_json(prospective_payload),
            **prospective_payload,
        }
        prospective_id = prospective["prospective_eligibility_id"]
        self._write(cohort / "prospective" / f"v3-{index}.json", prospective)
        case_id = module._case_id(task_id, recommendation_id)
        eligibility_payload = {
            "schema_version": module.ELIGIBILITY_SCHEMA_V3,
            "prospective_eligibility": {
                "schema_version": module.PROSPECTIVE_SCHEMA_V2,
                "prospective_eligibility_id": prospective_id,
                "workspace_id": workspace_id,
                "plan_sha256": plan_sha256,
                "workspace_case_id": workspace_case_id,
                "frozen_at": frozen_at,
            },
            "eligible_case": {"task_id": task_id, "case_id": case_id},
            "canonical_route_evidence": route_ref,
            "features": dict(prospective["features"]),
            "case_provenance": provenance,
            "frozen_at": frozen_at,
            "no_effect": dict(module.NO_EFFECT),
        }
        eligibility = {"eligibility_id": module._sha256_json(eligibility_payload), **eligibility_payload}
        self._write(cohort / "eligibility" / f"v3-{index}.json", eligibility)
        observed_at = "2026-07-24T11:00:00Z"
        if reviewed:
            labels = assessment_labels or ("success", "partial" if disagree else "success")
            adjudicated_label = labels[0] if labels[0] == labels[1] else "partial"
            outcome = {
                "status": "reviewed",
                "kind": "task_correctness",
                "label": outcome_label or adjudicated_label,
                "observed_at": observed_at,
                "review_authority": "diff_bound_review",
            }
            refs = ["diff-review:v3-fixture"]
            assessments = sorted([
                {
                    "reviewer_pseudonym_sha256": module.hashlib.sha256(b"reviewer-a").hexdigest(),
                    "kind": "task_correctness",
                    "label": labels[0],
                    "observed_at": observed_at,
                    "review_authority": "diff_bound_review",
                    "primary_evidence_refs": ["diff-review:v3-fixture-a"],
                },
                {
                    "reviewer_pseudonym_sha256": module.hashlib.sha256(b"reviewer-b").hexdigest(),
                    "kind": "task_correctness",
                    "label": labels[1],
                    "observed_at": observed_at,
                    "review_authority": "ci_and_review",
                    "primary_evidence_refs": ["github-ci:v3-fixture-b"],
                },
            ], key=lambda item: item["reviewer_pseudonym_sha256"])
        else:
            outcome = {
                "status": "abstained",
                "reason_code": "no_semantic_review",
                "observed_at": observed_at,
            }
            refs = []
            assessments = []
        record_payload = {
            "schema_version": module.RECORD_SCHEMA_V3,
            "eligibility": {
                "schema_version": module.ELIGIBILITY_SCHEMA_V3,
                "eligibility_id": eligibility["eligibility_id"],
                "prospective_eligibility_id": prospective_id,
                "workspace_id": workspace_id,
                "plan_sha256": plan_sha256,
                "workspace_case_id": workspace_case_id,
                "frozen_at": frozen_at,
            },
            "eligible_case": dict(eligibility["eligible_case"]),
            "canonical_route_evidence": route_ref,
            "features": dict(prospective["features"]),
            "case_provenance": provenance,
            "execution_provenance": (
                {"status": "unknown", "reason_code": "not_observed"}
                if execution_unknown
                else {
                    "status": "completed",
                    "observed_at": "2026-07-24T10:55:00Z",
                    "evidence_refs": ["artifact:v3-lifecycle"],
                }
            ),
            "outcome": outcome,
            "primary_evidence_refs": refs,
            "semantic_assessments": assessments,
            "captured_at": "2026-07-24T12:00:00Z",
            "no_effect": dict(module.NO_EFFECT),
        }
        record = {"record_id": module._sha256_json(record_payload), **record_payload}
        self._write(cohort / "records" / f"v3-{index}.json", record)
        attempt_identity = {
            "schema_version": "operator-routing-shadow-capture-attempt-identity.v1",
            "workspace_id": workspace_id,
            "plan_sha256": plan_sha256,
            "stage": "prospective_eligibility_freeze",
            "status": "created",
            "reason_code": "eligible_verified_route",
            "prospective_eligibility_id": prospective_id,
        }
        attempt = {
            "schema_version": module.ATTEMPT_SCHEMA,
            "attempt_id": module._sha256_json(attempt_identity),
            "workspace_id": workspace_id,
            "plan_sha256": plan_sha256,
            "stage": "prospective_eligibility_freeze",
            "status": "created",
            "reason_code": "eligible_verified_route",
            "prospective_eligibility_id": prospective_id,
            "attempted_at": frozen_at,
            "no_effect": dict(module.NO_EFFECT),
        }
        self._write(cohort / "attempts" / f"v3-{index}.json", attempt)
        binding_payload = {
            "schema_version": "operator-routing-shadow-direct-task-binding.v1",
            "task_id": task_id,
            "workspace_id": workspace_id,
            "plan_sha256": plan_sha256,
            "task_identity": task_identity,
            "route_evidence": route,
            "prospective": {
                "status": "created",
                "prospective_eligibility_id": prospective_id,
                "workspace_case_id": workspace_case_id,
            },
            "created_at": frozen_at,
            "no_effect": dict(module.NO_EFFECT),
        }
        binding = {"binding_id": module._sha256_json(binding_payload), **binding_payload}
        self._write(bindings / f"{task_id}.json", binding)
        return bindings

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

    def test_v3_direct_case_exposes_provenance_reviews_and_route_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cohort, workspaces = self._roots(tmp)
            bindings = self._v3_direct_case(cohort, index=1)
            report = module.audit(cohort, workspaces, CRITERIA, bindings)
            self.assertEqual(report["gate_result"], "CONTINUE-COLLECTING")
            self.assertEqual(report["counts"]["eligible_treatment_cases"], 1)
            self.assertEqual(report["counts"]["complete_treatment_cases"], 1)
            self.assertTrue(report["cohort_provenance"]["test_quarantine_provenance_observable"])
            self.assertTrue(report["cohort_provenance"]["execution_failure_provenance_observable"])
            self.assertTrue(report["outcomes"]["semantic_review_disagreement"]["observable"])
            self.assertEqual(report["outcomes"]["semantic_review_disagreement"]["independent_label_pair_count"], 1)
            self.assertEqual(report["coverage"]["dimensions"]["actual_route"], {"direct_operator": 1})
            self.assertEqual(report["quality"]["integrity_error_count"], 0)

    def test_v3_abstention_stays_in_denominator_but_is_incomplete(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cohort, workspaces = self._roots(tmp)
            bindings = self._v3_direct_case(cohort, index=2, reviewed=False)
            report = module.audit(cohort, workspaces, CRITERIA, bindings)
            self.assertEqual(report["counts"]["eligible_treatment_cases"], 1)
            self.assertEqual(report["counts"]["abstained_records"], 1)
            self.assertEqual(report["counts"]["complete_treatment_cases"], 0)
            self.assertEqual(report["quality"]["direct_route_plus_reviewed_outcome_completeness_percent"], 0.0)
            self.assertEqual(report["quality"]["integrity_error_count"], 0)

    def test_v3_unknown_execution_provenance_cannot_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cohort, workspaces = self._roots(tmp)
            bindings = None
            for index in range(20):
                bindings = self._v3_direct_case(cohort, index=100 + index, execution_unknown=True)
            assert bindings is not None
            report = module.audit(cohort, workspaces, CRITERIA, bindings)
            self.assertNotEqual(report["gate_result"], "PASS")
            self.assertIn("execution_failure_provenance_unobservable", report["gate_reasons"])
            self.assertEqual(report["attempt_accounting"]["treatment_execution_provenance_missing_count"], 20)
            self.assertEqual(report["counts"]["complete_treatment_cases"], 0)

    def test_direct_binding_repository_context_is_identity_bound(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cohort, workspaces = self._roots(tmp)
            bindings = self._v3_direct_case(cohort, index=200)
            before = module.audit(cohort, workspaces, CRITERIA, bindings)
            binding_path = next(bindings.glob("*.json"))
            binding = json.loads(binding_path.read_text(encoding="utf-8"))
            binding["task_identity"]["cwd_sha256"] = module.hashlib.sha256(b"/tampered/repo").hexdigest()
            payload = {key: value for key, value in binding.items() if key != "binding_id"}
            binding["binding_id"] = module._sha256_json(payload)
            self._write(binding_path, binding)
            after = module.audit(cohort, workspaces, CRITERIA, bindings)
            self.assertNotEqual(before["cohort_identity_sha256"], after["cohort_identity_sha256"])
            self.assertGreater(after["quality"]["unresolved_manifest_binding_count"], 0)
            self.assertNotEqual(after["gate_result"], "PASS")

    def test_v3_outcome_label_must_follow_assessment_adjudication(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cohort, workspaces = self._roots(tmp)
            bindings = self._v3_direct_case(
                cohort,
                index=300,
                outcome_label="success",
                assessment_labels=("failure", "failure"),
            )
            report = module.audit(cohort, workspaces, CRITERIA, bindings)
            self.assertEqual(report["gate_result"], "FAIL")
            self.assertTrue(
                any("reviewed outcome label contradicts semantic assessment adjudication" in key for key in report["errors"])
            )

    def test_route_source_and_manifest_identity_remain_exactly_bound(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cohort, workspaces = self._roots(tmp)
            bindings = self._v3_direct_case(cohort, index=400)
            eligibility_path = next((cohort / "eligibility").glob("*.json"))
            record_path = next((cohort / "records").glob("*.json"))
            eligibility = json.loads(eligibility_path.read_text(encoding="utf-8"))
            eligibility["canonical_route_evidence"]["source"] = "agent-workspace-manifest"
            eligibility_payload = {key: value for key, value in eligibility.items() if key != "eligibility_id"}
            eligibility["eligibility_id"] = module._sha256_json(eligibility_payload)
            self._write(eligibility_path, eligibility)
            record = json.loads(record_path.read_text(encoding="utf-8"))
            record["eligibility"]["eligibility_id"] = eligibility["eligibility_id"]
            record["canonical_route_evidence"] = dict(eligibility["canonical_route_evidence"])
            record_payload = {key: value for key, value in record.items() if key != "record_id"}
            record["record_id"] = module._sha256_json(record_payload)
            self._write(record_path, record)
            report = module.audit(cohort, workspaces, CRITERIA, bindings)
            self.assertEqual(report["gate_result"], "FAIL")
            self.assertGreater(report["errors"].get("eligibility:route_binding_mismatch", 0), 0)

    def test_v3_semantic_assessment_before_freeze_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cohort, workspaces = self._roots(tmp)
            bindings = self._v3_direct_case(cohort, index=4)
            record_path = cohort / "records" / "v3-4.json"
            record = json.loads(record_path.read_text(encoding="utf-8"))
            record["semantic_assessments"][0]["observed_at"] = "2026-07-24T09:59:59Z"
            payload = {key: value for key, value in record.items() if key != "record_id"}
            record["record_id"] = module._sha256_json(payload)
            self._write(record_path, record)
            report = module.audit(cohort, workspaces, CRITERIA, bindings)
            self.assertEqual(report["gate_result"], "FAIL")
            self.assertGreater(report["quality"]["integrity_error_count"], 0)
            self.assertTrue(
                any("semantic assessment predates prospective eligibility freeze" in key for key in report["errors"])
            )

    def test_v3_nonproduction_case_is_excluded_from_treatment_denominator(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cohort, workspaces = self._roots(tmp)
            bindings = self._v3_direct_case(cohort, index=3, origin="test")
            report = module.audit(cohort, workspaces, CRITERIA, bindings)
            self.assertEqual(report["counts"]["eligible_treatment_cases"], 0)
            self.assertEqual(report["counts"]["excluded_nonproduction_cases"], 1)
            self.assertEqual(report["cohort_provenance"]["test_or_quarantine_contamination_count"], 0)
            self.assertEqual(report["quality"]["integrity_error_count"], 0)

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
