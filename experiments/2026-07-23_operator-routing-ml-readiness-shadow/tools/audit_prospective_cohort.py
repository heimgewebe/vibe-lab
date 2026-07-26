#!/usr/bin/env python3
"""Audit the prospective Grabowski routing-shadow cohort without training or routing effects.

The report is aggregate-only. It validates create-only identity chains, prospective
freeze ordering, semantic outcome evidence, no-effect constants, capture-attempt
accounting and preregistered coverage thresholds. Raw task, workspace,
recommendation and evidence identifiers are never emitted.
"""
from __future__ import annotations

import argparse
import collections
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any

NO_EFFECT = {
    "proposal_only": True,
    "routing": False,
    "policy": False,
    "queue": False,
    "merge": False,
    "runtime": False,
}
PROSPECTIVE_SCHEMA = "operator-routing-shadow-prospective-eligibility.v1"
PROSPECTIVE_SCHEMA_V2 = "operator-routing-shadow-prospective-eligibility.v2"
PROSPECTIVE_SCHEMAS = {PROSPECTIVE_SCHEMA, PROSPECTIVE_SCHEMA_V2}
ELIGIBILITY_SCHEMA = "operator-routing-shadow-eligibility.v2"
ELIGIBILITY_SCHEMA_V3 = "operator-routing-shadow-eligibility.v3"
ELIGIBILITY_SCHEMAS = {ELIGIBILITY_SCHEMA, ELIGIBILITY_SCHEMA_V3}
RECORD_SCHEMA = "operator-routing-shadow-record.v2"
RECORD_SCHEMA_V3 = "operator-routing-shadow-record.v3"
RECORD_SCHEMAS = {RECORD_SCHEMA, RECORD_SCHEMA_V3}
ATTEMPT_SCHEMA = "operator-routing-shadow-capture-attempt.v1"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
TASK_ID_RE = re.compile(r"^[0-9a-f]{24}$")
WORKSPACE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,199}$")
CATEGORIES = ("prospective", "eligibility", "records", "attempts")
EVIDENCE_PREFIXES = ("github-ci:", "diff-review:", "operator-decision:", "chronik:", "artifact:")
REVIEW_AUTHORITIES = {"diff_bound_review", "operator_decision", "ci_and_review", "bounded_chronik_evidence"}
CASE_ORIGINS = {"production", "test", "synthetic", "quarantined"}
CAPTURE_PATHS = {"agent_workspace_prestart", "direct_capture", "direct_task_prestart"}
EXECUTION_STATUSES = {"completed", "execution_aborted", "infrastructure_failure"}
OUTCOME_KINDS = {"task_correctness", "decision_quality"}
OUTCOME_LABELS = {"success", "partial", "failure"}
ABSTENTION_REASONS = {"no_semantic_review", "non_semantic_task", "insufficient_primary_evidence", "ambiguous_outcome"}
COMMON_FEATURE_FIELDS = {
    "task_kind",
    "changed_file_estimate",
    "expected_duration_minutes",
    "novelty",
    "risk_flags",
    "connector_instability",
    "user_requested_external",
}
V1_FEATURE_FIELDS = COMMON_FEATURE_FIELDS | {"parallel_work"}
V2_FEATURE_FIELDS = COMMON_FEATURE_FIELDS | {
    "risk_tier",
    "concurrent_external_activity",
    "parallelization_candidate",
    "decision_fork",
    "architecture_hypotheses",
}


class AuditError(RuntimeError):
    pass


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _sha256_json(value: Any) -> str:
    return hashlib.sha256(_json_bytes(value)).hexdigest()


def _case_id(task_id: str, recommendation_id: str) -> str:
    return _sha256_json({"schema_version": 1, "task_id": task_id, "recommendation_id": recommendation_id})


def _workspace_case_id(
    workspace_id: str,
    plan_sha256: str,
    route_evidence_sha256: str,
    *,
    route_source: str = "agent-workspace-manifest",
) -> str:
    payload: dict[str, Any] = {
        "schema_version": 1,
        "workspace_id": workspace_id,
        "plan_sha256": plan_sha256,
        "route_evidence_sha256": route_evidence_sha256,
    }
    if route_source != "agent-workspace-manifest":
        payload = {
            "schema_version": 2,
            "route_source": route_source,
            "workspace_id": workspace_id,
            "plan_sha256": plan_sha256,
            "route_evidence_sha256": route_evidence_sha256,
        }
    return _sha256_json(payload)


def _read_json(path: Path) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise AuditError("cohort entry is not a regular non-symlink file")
    if path.stat().st_size > 2_000_000:
        raise AuditError("cohort entry exceeds 2 MiB")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AuditError("cohort entry is not valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise AuditError("cohort entry is not a JSON object")
    return value


def _read_category(root: Path, category: str) -> list[dict[str, Any]]:
    directory = root / category
    if not directory.is_dir() or directory.is_symlink():
        raise AuditError(f"missing safe cohort directory: {category}")
    values: list[dict[str, Any]] = []
    for path in sorted(directory.iterdir()):
        if path.suffix != ".json":
            raise AuditError(f"unexpected cohort directory entry: {category}")
        values.append(_read_json(path))
    return values


def _timestamp(value: Any) -> datetime:
    if not isinstance(value, str) or not value or len(value) > 64:
        raise AuditError("timestamp is missing or unbounded")
    candidate = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise AuditError("timestamp is invalid") from exc
    if parsed.tzinfo is None:
        raise AuditError("timestamp has no timezone")
    return parsed


def _canonical_timestamp(value: Any, label: str) -> datetime:
    parsed = _timestamp(value)
    normalized = parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if value != normalized:
        raise AuditError(f"{label} is not normalized to canonical UTC-Z")
    return parsed


def _exact(value: Any, expected: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != expected:
        raise AuditError(f"{label} shape is invalid")
    return value


def _require_sha(value: Any, label: str) -> str:
    if not isinstance(value, str) or SHA256_RE.fullmatch(value) is None:
        raise AuditError(f"{label} is not a SHA-256")
    return value


def _validate_no_effect(value: Any) -> None:
    if value != NO_EFFECT:
        raise AuditError("no_effect boundary is invalid")


def _manifest_identity_sha256(
    workspace_id: str,
    plan_sha256: str,
    route_evidence_sha256: str,
    *,
    route_source: str,
) -> str:
    payload: dict[str, Any] = {
        "schema_version": "operator-routing-shadow-manifest-identity.v1",
        "workspace_id": workspace_id,
        "plan_sha256": plan_sha256,
        "route_evidence_sha256": route_evidence_sha256,
    }
    if route_source != "agent-workspace-manifest":
        payload = {
            "schema_version": "operator-routing-shadow-manifest-identity.v2",
            "route_source": route_source,
            "workspace_id": workspace_id,
            "plan_sha256": plan_sha256,
            "route_evidence_sha256": route_evidence_sha256,
        }
    return _sha256_json(payload)


def _validate_route_ref(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise AuditError("canonical_route_evidence shape is invalid")
    legacy_fields = {"source", "schema_version", "recommendation_id", "route_evidence_sha256", "manifest_sha256"}
    current_fields = {"source", "schema_version", "recommendation_id", "route_evidence_sha256", "manifest_identity_sha256"}
    if set(value) == legacy_fields:
        if value["source"] != "agent-workspace-manifest":
            raise AuditError("legacy canonical route source is invalid")
        manifest_field = "manifest_sha256"
    elif set(value) == current_fields:
        if value["source"] not in {"agent-workspace-manifest", "direct-task-start"}:
            raise AuditError("canonical route source is invalid")
        manifest_field = "manifest_identity_sha256"
    else:
        raise AuditError("canonical_route_evidence shape is invalid")
    if value["schema_version"] not in {1, 2}:
        raise AuditError("canonical route schema version is invalid")
    for field in ("recommendation_id", "route_evidence_sha256", manifest_field):
        _require_sha(value[field], f"canonical_route_evidence.{field}")
    return value


def _validate_case_provenance(value: Any) -> dict[str, str]:
    provenance = _exact(value, {"case_origin", "capture_path"}, "case_provenance")
    if provenance["case_origin"] not in CASE_ORIGINS or provenance["capture_path"] not in CAPTURE_PATHS:
        raise AuditError("case provenance value is invalid")
    if provenance["case_origin"] == "production" and provenance["capture_path"] == "direct_capture":
        raise AuditError("direct capture cannot claim production provenance")
    return provenance

def _validate_features(features: Any, *, route_schema_version: int) -> None:
    expected_fields = (
        V1_FEATURE_FIELDS
        if route_schema_version == 1
        else V2_FEATURE_FIELDS
        if route_schema_version == 2
        else set()
    )
    if not isinstance(features, dict) or set(features) != expected_fields:
        raise AuditError("features shape is invalid for route schema version")
    if not isinstance(features["task_kind"], str) or not 1 <= len(features["task_kind"]) <= 40:
        raise AuditError("features.task_kind is invalid")
    for field in ("changed_file_estimate", "expected_duration_minutes"):
        value = features[field]
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise AuditError(f"features.{field} is invalid")
    if not isinstance(features["novelty"], str) or not 1 <= len(features["novelty"]) <= 32:
        raise AuditError("features.novelty is invalid")
    flags = features["risk_flags"]
    if (
        not isinstance(flags, list)
        or len(flags) > 32
        or any(not isinstance(item, str) or not 1 <= len(item) <= 32 for item in flags)
        or len(set(flags)) != len(flags)
    ):
        raise AuditError("features.risk_flags is invalid")
    for field in ("connector_instability", "user_requested_external"):
        if not isinstance(features[field], bool):
            raise AuditError(f"features.{field} is invalid")
    if route_schema_version == 1:
        if not isinstance(features["parallel_work"], bool):
            raise AuditError("features.parallel_work is invalid")
        return
    if not isinstance(features["risk_tier"], str) or not 1 <= len(features["risk_tier"]) <= 32:
        raise AuditError("features.risk_tier is invalid")
    for field in ("concurrent_external_activity", "parallelization_candidate", "decision_fork"):
        if not isinstance(features[field], bool):
            raise AuditError(f"features.{field} is invalid")
    hypotheses = features["architecture_hypotheses"]
    if isinstance(hypotheses, bool) or not isinstance(hypotheses, int) or not 1 <= hypotheses <= 4:
        raise AuditError("features.architecture_hypotheses is invalid")


def _bounded_features(route: dict[str, Any]) -> dict[str, Any]:
    facts = route.get("input_facts")
    if not isinstance(facts, dict):
        raise AuditError("verified route evidence is missing input_facts")
    raw_risk_flags = facts.get("risk_flags", [])
    if not isinstance(raw_risk_flags, list):
        raise AuditError("verified route evidence risk_flags are invalid")
    common = {
        "task_kind": facts.get("task_kind"),
        "changed_file_estimate": facts.get("changed_file_estimate"),
        "expected_duration_minutes": facts.get("expected_duration_minutes"),
        "novelty": facts.get("novelty"),
        "risk_flags": list(raw_risk_flags),
        "connector_instability": facts.get("connector_instability"),
        "user_requested_external": facts.get("user_requested_external"),
    }
    if route.get("schema_version") == 1:
        features = {**common, "parallel_work": facts.get("parallel_work")}
    elif route.get("schema_version") == 2:
        features = {
            **common,
            "risk_tier": route.get("risk_tier"),
            "concurrent_external_activity": facts.get("concurrent_external_activity"),
            "parallelization_candidate": facts.get("parallelization_candidate"),
            "decision_fork": facts.get("decision_fork"),
            "architecture_hypotheses": facts.get("architecture_hypotheses"),
        }
    else:
        raise AuditError("verified route evidence schema version is unsupported")
    _validate_features(features, route_schema_version=route["schema_version"])
    return features


def _validate_prospective(value: dict[str, Any]) -> dict[str, Any]:
    schema = value.get("schema_version")
    expected = {
        "schema_version", "prospective_eligibility_id", "workspace_case",
        "canonical_route_evidence", "features", "frozen_at", "no_effect",
    }
    if schema == PROSPECTIVE_SCHEMA_V2:
        expected.add("case_provenance")
    receipt = _exact(value, expected, "prospective eligibility")
    if schema not in PROSPECTIVE_SCHEMAS:
        raise AuditError("prospective schema is invalid")
    receipt_id = _require_sha(receipt["prospective_eligibility_id"], "prospective_eligibility_id")
    workspace_case = _exact(receipt["workspace_case"], {"workspace_id", "plan_sha256", "case_id"}, "workspace_case")
    if not isinstance(workspace_case["workspace_id"], str) or WORKSPACE_ID_RE.fullmatch(workspace_case["workspace_id"]) is None:
        raise AuditError("workspace_id is invalid")
    _require_sha(workspace_case["plan_sha256"], "plan_sha256")
    _require_sha(workspace_case["case_id"], "workspace_case.case_id")
    route_ref = _validate_route_ref(receipt["canonical_route_evidence"])
    expected_case_id = _workspace_case_id(
        workspace_case["workspace_id"],
        workspace_case["plan_sha256"],
        route_ref["route_evidence_sha256"],
        route_source=route_ref["source"],
    )
    if workspace_case["case_id"] != expected_case_id:
        raise AuditError("workspace_case.case_id is not bound to workspace, plan and route")
    if "manifest_identity_sha256" in route_ref:
        expected_manifest_identity = _manifest_identity_sha256(
            workspace_case["workspace_id"], workspace_case["plan_sha256"],
            route_ref["route_evidence_sha256"], route_source=route_ref["source"],
        )
        if route_ref["manifest_identity_sha256"] != expected_manifest_identity:
            raise AuditError("manifest identity is not bound to workspace, plan and route")
    _validate_features(receipt["features"], route_schema_version=route_ref["schema_version"])
    if schema == PROSPECTIVE_SCHEMA_V2:
        _validate_case_provenance(receipt["case_provenance"])
        _canonical_timestamp(receipt["frozen_at"], "prospective frozen_at")
    else:
        _timestamp(receipt["frozen_at"])
    _validate_no_effect(receipt["no_effect"])
    payload = {key: receipt[key] for key in receipt if key != "prospective_eligibility_id"}
    if _sha256_json(payload) != receipt_id:
        raise AuditError("prospective eligibility hash does not match payload")
    return receipt


def _validate_eligibility(value: dict[str, Any]) -> dict[str, Any]:
    schema = value.get("schema_version")
    expected = {
        "schema_version", "eligibility_id", "prospective_eligibility", "eligible_case",
        "canonical_route_evidence", "features", "frozen_at", "no_effect",
    }
    if schema == ELIGIBILITY_SCHEMA_V3:
        expected.add("case_provenance")
    receipt = _exact(value, expected, "bound eligibility")
    if schema not in ELIGIBILITY_SCHEMAS:
        raise AuditError("eligibility schema is invalid")
    eligibility_id = _require_sha(receipt["eligibility_id"], "eligibility_id")
    prospective = _exact(
        receipt["prospective_eligibility"],
        {"schema_version", "prospective_eligibility_id", "workspace_id", "plan_sha256", "workspace_case_id", "frozen_at"},
        "prospective eligibility reference",
    )
    expected_prospective_schema = PROSPECTIVE_SCHEMA_V2 if schema == ELIGIBILITY_SCHEMA_V3 else PROSPECTIVE_SCHEMA
    if prospective["schema_version"] != expected_prospective_schema:
        raise AuditError("prospective eligibility reference schema is invalid")
    _require_sha(prospective["prospective_eligibility_id"], "prospective reference id")
    _require_sha(prospective["plan_sha256"], "prospective plan hash")
    _require_sha(prospective["workspace_case_id"], "prospective case hash")
    if not isinstance(prospective["workspace_id"], str) or WORKSPACE_ID_RE.fullmatch(prospective["workspace_id"]) is None:
        raise AuditError("prospective workspace id is invalid")
    eligible = _exact(receipt["eligible_case"], {"task_id", "case_id"}, "eligible_case")
    if not isinstance(eligible["task_id"], str) or TASK_ID_RE.fullmatch(eligible["task_id"]) is None:
        raise AuditError("eligible task id is invalid")
    _require_sha(eligible["case_id"], "eligible case id")
    route_ref = _validate_route_ref(receipt["canonical_route_evidence"])
    if eligible["case_id"] != _case_id(eligible["task_id"], route_ref["recommendation_id"]):
        raise AuditError("eligible case id is not bound to task and route")
    _validate_features(receipt["features"], route_schema_version=route_ref["schema_version"])
    if schema == ELIGIBILITY_SCHEMA_V3:
        _validate_case_provenance(receipt["case_provenance"])
        _canonical_timestamp(receipt["frozen_at"], "eligibility frozen_at")
        _canonical_timestamp(prospective["frozen_at"], "prospective reference frozen_at")
    if _timestamp(receipt["frozen_at"]) != _timestamp(prospective["frozen_at"]):
        raise AuditError("eligibility does not preserve prospective freeze time")
    _validate_no_effect(receipt["no_effect"])
    payload = {key: receipt[key] for key in receipt if key != "eligibility_id"}
    if _sha256_json(payload) != eligibility_id:
        raise AuditError("eligibility hash does not match payload")
    return receipt


def _validate_refs(
    value: Any,
    *,
    required: bool,
    label: str,
    canonical_order: bool = False,
) -> list[str]:
    if (
        not isinstance(value, list)
        or (required and not value)
        or len(value) > 16
        or any(
            not isinstance(item, str)
            or not 1 <= len(item) <= 300
            or not item.startswith(EVIDENCE_PREFIXES)
            for item in value
        )
        or len(set(value)) != len(value)
    ):
        raise AuditError(f"{label} are invalid")
    if canonical_order and value != sorted(value):
        raise AuditError(f"{label} are not in canonical order")
    return value


def _validate_execution_provenance(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise AuditError("execution provenance is invalid")
    if value.get("status") == "unknown":
        result = _exact(value, {"status", "reason_code"}, "execution provenance")
        if result["reason_code"] not in {"not_observed", "ambiguous"}:
            raise AuditError("execution provenance reason is invalid")
        return result
    result = _exact(value, {"status", "observed_at", "evidence_refs"}, "execution provenance")
    if result["status"] not in EXECUTION_STATUSES:
        raise AuditError("execution provenance status is invalid")
    _canonical_timestamp(result["observed_at"], "execution provenance observed_at")
    _validate_refs(
        result["evidence_refs"],
        required=True,
        label="execution evidence references",
        canonical_order=True,
    )
    return result


def _validate_semantic_assessments(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list) or (value and not 2 <= len(value) <= 4):
        raise AuditError("semantic assessments cardinality is invalid")
    reviewers: set[str] = set()
    assessments: list[dict[str, Any]] = []
    for item in value:
        assessment = _exact(
            item,
            {"reviewer_pseudonym_sha256", "kind", "label", "observed_at", "review_authority", "primary_evidence_refs"},
            "semantic assessment",
        )
        reviewer = _require_sha(assessment["reviewer_pseudonym_sha256"], "reviewer pseudonym")
        if reviewer in reviewers:
            raise AuditError("semantic assessment reviewer is duplicated")
        reviewers.add(reviewer)
        if assessment["kind"] not in OUTCOME_KINDS or assessment["label"] not in OUTCOME_LABELS:
            raise AuditError("semantic assessment kind or label is invalid")
        if assessment["review_authority"] not in REVIEW_AUTHORITIES:
            raise AuditError("semantic assessment authority is invalid")
        _canonical_timestamp(assessment["observed_at"], "semantic assessment observed_at")
        _validate_refs(
            assessment["primary_evidence_refs"],
            required=True,
            label="semantic assessment evidence references",
            canonical_order=True,
        )
        assessments.append(assessment)
    if assessments != sorted(assessments, key=lambda item: item["reviewer_pseudonym_sha256"]):
        raise AuditError("semantic assessments are not in canonical reviewer order")
    return assessments


def _adjudicated_assessment_label(assessments: list[dict[str, Any]]) -> str:
    labels = {item["label"] for item in assessments}
    if len(labels) == 1:
        return next(iter(labels))
    # Individual labels remain visible and disagreement remains counted. The
    # aggregate label is conservatively partial rather than optimistic success.
    return "partial"


def _validate_record(value: dict[str, Any]) -> dict[str, Any]:
    schema = value.get("schema_version")
    expected = {
        "schema_version", "record_id", "eligibility", "eligible_case", "canonical_route_evidence",
        "features", "outcome", "primary_evidence_refs", "captured_at", "no_effect",
    }
    if schema == RECORD_SCHEMA_V3:
        expected |= {"case_provenance", "execution_provenance", "semantic_assessments"}
    record = _exact(value, expected, "shadow record")
    if schema not in RECORD_SCHEMAS:
        raise AuditError("record schema is invalid")
    record_id = _require_sha(record["record_id"], "record_id")
    eligibility_expected = {"schema_version", "eligibility_id", "prospective_eligibility_id", "frozen_at"}
    if schema == RECORD_SCHEMA_V3:
        eligibility_expected |= {"workspace_id", "plan_sha256", "workspace_case_id"}
    eligibility = _exact(record["eligibility"], eligibility_expected, "record eligibility reference")
    expected_eligibility_schema = ELIGIBILITY_SCHEMA_V3 if schema == RECORD_SCHEMA_V3 else ELIGIBILITY_SCHEMA
    if eligibility["schema_version"] != expected_eligibility_schema:
        raise AuditError("record eligibility schema is invalid")
    _require_sha(eligibility["eligibility_id"], "record eligibility id")
    _require_sha(eligibility["prospective_eligibility_id"], "record prospective id")
    if schema == RECORD_SCHEMA_V3:
        _require_sha(eligibility["plan_sha256"], "record plan hash")
        _require_sha(eligibility["workspace_case_id"], "record workspace case hash")
        if not isinstance(eligibility["workspace_id"], str) or WORKSPACE_ID_RE.fullmatch(eligibility["workspace_id"]) is None:
            raise AuditError("record workspace id is invalid")
    eligible = _exact(record["eligible_case"], {"task_id", "case_id"}, "record eligible_case")
    if not isinstance(eligible["task_id"], str) or TASK_ID_RE.fullmatch(eligible["task_id"]) is None:
        raise AuditError("record task id is invalid")
    _require_sha(eligible["case_id"], "record case id")
    route_ref = _validate_route_ref(record["canonical_route_evidence"])
    if eligible["case_id"] != _case_id(eligible["task_id"], route_ref["recommendation_id"]):
        raise AuditError("record case id is not bound to task and route")
    _validate_features(record["features"], route_schema_version=route_ref["schema_version"])
    outcome = record["outcome"]
    if not isinstance(outcome, dict) or outcome.get("status") not in {"reviewed", "abstained"}:
        raise AuditError("record outcome is invalid")
    if outcome["status"] == "reviewed":
        if set(outcome) != {"status", "kind", "label", "observed_at", "review_authority"}:
            raise AuditError("reviewed outcome shape is invalid")
        if outcome["kind"] not in OUTCOME_KINDS or outcome["label"] not in OUTCOME_LABELS:
            raise AuditError("reviewed outcome kind or label is invalid")
        if outcome["review_authority"] not in REVIEW_AUTHORITIES:
            raise AuditError("reviewed outcome authority is invalid")
    else:
        if set(outcome) != {"status", "reason_code", "observed_at"}:
            raise AuditError("abstained outcome shape is invalid")
        if outcome["reason_code"] not in ABSTENTION_REASONS:
            raise AuditError("abstention reason is invalid")
    refs = _validate_refs(
        record["primary_evidence_refs"],
        required=False,
        label="primary evidence references",
        canonical_order=schema == RECORD_SCHEMA_V3,
    )
    if schema == RECORD_SCHEMA_V3:
        frozen_at = _canonical_timestamp(eligibility["frozen_at"], "record eligibility frozen_at")
        observed_at = _canonical_timestamp(outcome["observed_at"], "record outcome observed_at")
        captured_at = _canonical_timestamp(record["captured_at"], "record captured_at")
    else:
        frozen_at = _timestamp(eligibility["frozen_at"])
        observed_at = _timestamp(outcome["observed_at"])
        captured_at = _timestamp(record["captured_at"])
    if frozen_at > observed_at or observed_at > captured_at:
        raise AuditError("prospective freeze/outcome/capture ordering is invalid")
    if schema == RECORD_SCHEMA_V3:
        _validate_case_provenance(record["case_provenance"])
        execution = _validate_execution_provenance(record["execution_provenance"])
        assessments = _validate_semantic_assessments(record["semantic_assessments"])
        if assessments:
            if outcome["status"] != "reviewed" or any(item["kind"] != outcome["kind"] for item in assessments):
                raise AuditError("semantic assessments are not bound to the reviewed outcome kind")
            if outcome["label"] != _adjudicated_assessment_label(assessments):
                raise AuditError("reviewed outcome label contradicts semantic assessment adjudication")
        if outcome["status"] == "reviewed" and not refs:
            # Retained as a valid-but-incomplete observation so the gate can quantify missingness.
            pass
        timeline = [("outcome observation", observed_at)]
        timeline.extend(
            ("semantic assessment", _timestamp(item["observed_at"])) for item in assessments
        )
        if execution.get("status") in EXECUTION_STATUSES:
            execution_at = _timestamp(execution["observed_at"])
            timeline.append(("execution observation", execution_at))
        else:
            execution_at = None
        for label, timestamp in timeline:
            if timestamp < frozen_at:
                raise AuditError(f"{label} predates prospective eligibility freeze")
            if timestamp > captured_at:
                raise AuditError(f"{label} occurs after record capture")
        if outcome.get("kind") == "task_correctness" and execution_at is not None:
            correctness_observations = [("outcome observation", observed_at)]
            correctness_observations.extend(
                ("semantic assessment", _timestamp(item["observed_at"])) for item in assessments
            )
            for label, timestamp in correctness_observations:
                if timestamp < execution_at:
                    raise AuditError(f"task-correctness {label} predates execution observation")
    _validate_no_effect(record["no_effect"])
    payload = {key: record[key] for key in record if key != "record_id"}
    if _sha256_json(payload) != record_id:
        raise AuditError("record hash does not match payload")
    return record

def _validate_attempt(value: dict[str, Any]) -> dict[str, Any]:
    attempt = _exact(
        value,
        {"schema_version", "attempt_id", "workspace_id", "plan_sha256", "stage", "status", "reason_code", "prospective_eligibility_id", "attempted_at", "no_effect"},
        "capture attempt",
    )
    if attempt["schema_version"] != ATTEMPT_SCHEMA or attempt["stage"] != "prospective_eligibility_freeze":
        raise AuditError("capture attempt schema or stage is invalid")
    attempt_id = _require_sha(attempt["attempt_id"], "attempt_id")
    if attempt["status"] not in {"created", "duplicate", "rejected", "error"}:
        raise AuditError("capture attempt status is invalid")
    if not isinstance(attempt["workspace_id"], str) or WORKSPACE_ID_RE.fullmatch(attempt["workspace_id"]) is None:
        raise AuditError("attempt workspace id is invalid")
    _require_sha(attempt["plan_sha256"], "attempt plan hash")
    prospective_id = attempt["prospective_eligibility_id"]
    if prospective_id is not None:
        _require_sha(prospective_id, "attempt prospective id")
    if not isinstance(attempt["reason_code"], str) or not attempt["reason_code"]:
        raise AuditError("attempt reason code is invalid")
    _timestamp(attempt["attempted_at"])
    _validate_no_effect(attempt["no_effect"])
    identity_payload = {
        "schema_version": "operator-routing-shadow-capture-attempt-identity.v1",
        "workspace_id": attempt["workspace_id"],
        "plan_sha256": attempt["plan_sha256"],
        "stage": attempt["stage"],
        "status": attempt["status"],
        "reason_code": attempt["reason_code"],
        "prospective_eligibility_id": attempt["prospective_eligibility_id"],
    }
    legacy_payload = {key: attempt[key] for key in attempt if key != "attempt_id"}
    if attempt_id not in {_sha256_json(identity_payload), _sha256_json(legacy_payload)}:
        raise AuditError("attempt id does not match canonical or legacy identity")
    return attempt


def _repository_context(repository: Any) -> str:
    if not isinstance(repository, str) or not repository:
        return "unavailable"
    return "repo-sha256:" + hashlib.sha256(repository.encode("utf-8")).hexdigest()[:12]


def _direct_task_plan_sha256(task_id: str, task_identity: dict[str, Any], route: dict[str, Any]) -> str:
    return _sha256_json(
        {
            "schema_version": "operator-routing-shadow-direct-task-plan.v1",
            "task_id": task_id,
            "task_identity": task_identity,
            "route_evidence_sha256": _sha256_json(route),
        }
    )


def _validate_direct_task_binding(
    value: Any,
    *,
    receipt: dict[str, Any],
    eligibility: dict[str, Any],
) -> dict[str, Any]:
    expected = {
        "schema_version", "binding_id", "task_id", "workspace_id", "plan_sha256",
        "task_identity", "route_evidence", "prospective", "created_at", "no_effect",
    }
    binding = _exact(value, expected, "direct task binding")
    if binding["schema_version"] != "operator-routing-shadow-direct-task-binding.v1":
        raise AuditError("direct task binding schema is invalid")
    task_id = eligibility["eligible_case"]["task_id"]
    workspace_case = receipt["workspace_case"]
    if (
        binding["task_id"] != task_id
        or binding["workspace_id"] != workspace_case["workspace_id"]
        or binding["workspace_id"] != f"gaw-direct-task-{task_id}"
        or binding["plan_sha256"] != workspace_case["plan_sha256"]
    ):
        raise AuditError("direct task binding identity does not match eligibility")
    identity = _exact(
        binding["task_identity"],
        {"host_sha256", "argv_sha256", "cwd_sha256", "resource_keys_sha256", "runtime_seconds"},
        "direct task identity",
    )
    for field in ("host_sha256", "argv_sha256", "cwd_sha256", "resource_keys_sha256"):
        _require_sha(identity[field], f"direct task identity {field}")
    runtime_seconds = identity["runtime_seconds"]
    if isinstance(runtime_seconds, bool) or not isinstance(runtime_seconds, int) or not 1 <= runtime_seconds <= 604800:
        raise AuditError("direct task runtime_seconds is invalid")
    route = binding["route_evidence"]
    if not isinstance(route, dict):
        raise AuditError("direct task route evidence is invalid")
    _bounded_features(route)
    if binding["plan_sha256"] != _direct_task_plan_sha256(task_id, identity, route):
        raise AuditError("direct task plan identity is invalid")
    prospective = _exact(
        binding["prospective"],
        {"status", "prospective_eligibility_id", "workspace_case_id"},
        "direct task prospective reference",
    )
    if (
        prospective["status"] != "created"
        or prospective["prospective_eligibility_id"] != receipt["prospective_eligibility_id"]
        or prospective["workspace_case_id"] != workspace_case["case_id"]
    ):
        raise AuditError("direct task prospective reference is invalid")
    binding_created_at = _canonical_timestamp(binding["created_at"], "direct task binding created_at")
    frozen_at = _canonical_timestamp(receipt["frozen_at"], "direct task prospective frozen_at")
    if binding_created_at != frozen_at:
        raise AuditError("direct task binding created_at does not match prospective freeze")
    _validate_no_effect(binding["no_effect"])
    binding_id = _require_sha(binding["binding_id"], "direct task binding_id")
    payload = {key: item for key, item in binding.items() if key != "binding_id"}
    if binding_id != _sha256_json(payload):
        raise AuditError("direct task binding_id does not match payload")
    return binding


def _source_context_binding_sha256(
    *,
    route_ref: dict[str, Any],
    workspace_id: str,
    plan_sha256: str,
    repository_context: str,
    source_binding_id: str,
) -> str:
    return _sha256_json(
        {
            "schema_version": "operator-routing-shadow-source-context-binding.v1",
            "route_source": route_ref["source"],
            "workspace_id": workspace_id,
            "plan_sha256": plan_sha256,
            "canonical_route_evidence": route_ref,
            "repository_context": repository_context,
            "source_binding_id": source_binding_id,
        }
    )


def _resolve_route_context(
    receipt: dict[str, Any],
    eligibility: dict[str, Any],
    workspace_root: Path,
    direct_task_binding_root: Path | None,
) -> tuple[dict[str, Any] | None, str | None, str | None, str | None]:
    workspace_case = receipt["workspace_case"]
    workspace_id = workspace_case["workspace_id"]
    route_ref = receipt["canonical_route_evidence"]
    if route_ref["source"] == "direct-task-start":
        if direct_task_binding_root is None:
            return None, None, None, "direct_task_binding_root_unavailable"
        task_id = eligibility["eligible_case"]["task_id"]
        path = direct_task_binding_root / f"{task_id}.json"
        try:
            binding = _read_json(path)
        except AuditError:
            return None, None, None, "direct_task_binding_unavailable"
        try:
            binding = _validate_direct_task_binding(binding, receipt=receipt, eligibility=eligibility)
        except AuditError:
            return None, None, None, "direct_task_binding_invalid"
        route = binding["route_evidence"]
        if not isinstance(route, dict) or _sha256_json(route) != route_ref["route_evidence_sha256"]:
            return None, None, None, "route_hash_mismatch"
        if route.get("schema_version") != route_ref["schema_version"] or route.get("recommendation_id") != route_ref["recommendation_id"]:
            return None, None, None, "route_identity_mismatch"
        try:
            current_features = _bounded_features(route)
        except AuditError:
            return None, None, None, "route_features_invalid"
        if current_features != receipt["features"]:
            return None, None, None, "route_feature_binding_mismatch"
        identity = binding["task_identity"]
        cwd_sha256 = identity["cwd_sha256"]
        repository_context = f"cwd-sha256:{cwd_sha256[:12]}"
        source_context_sha256 = _source_context_binding_sha256(
            route_ref=route_ref,
            workspace_id=workspace_id,
            plan_sha256=workspace_case["plan_sha256"],
            repository_context=repository_context,
            source_binding_id=binding["binding_id"],
        )
        return route, repository_context, source_context_sha256, None

    path = workspace_root / workspace_id / "manifest.json"
    try:
        manifest = _read_json(path)
    except AuditError:
        return None, None, None, "manifest_unavailable"
    if manifest.get("workspace_id") != workspace_id or manifest.get("plan_sha256") != workspace_case["plan_sha256"]:
        return None, None, None, "manifest_workspace_or_plan_mismatch"
    route = manifest.get("route_evidence")
    if not isinstance(route, dict) or _sha256_json(route) != route_ref["route_evidence_sha256"]:
        return None, None, None, "route_hash_mismatch"
    if route.get("schema_version") != route_ref["schema_version"] or route.get("recommendation_id") != route_ref["recommendation_id"]:
        return None, None, None, "route_identity_mismatch"
    try:
        current_features = _bounded_features(route)
    except AuditError:
        return None, None, None, "route_features_invalid"
    if current_features != receipt["features"]:
        return None, None, None, "route_feature_binding_mismatch"
    repository_context = _repository_context(manifest.get("repository"))
    source_binding_id = route_ref.get("manifest_sha256") or route_ref.get("manifest_identity_sha256")
    assert isinstance(source_binding_id, str)
    source_context_sha256 = _source_context_binding_sha256(
        route_ref=route_ref,
        workspace_id=workspace_id,
        plan_sha256=workspace_case["plan_sha256"],
        repository_context=repository_context,
        source_binding_id=source_binding_id,
    )
    return route, repository_context, source_context_sha256, None

def _percent(numerator: int, denominator: int) -> float:
    return round(100.0 * numerator / denominator, 2) if denominator else 0.0


def audit(
    cohort_root: Path,
    workspace_root: Path,
    criteria: dict[str, Any],
    direct_task_binding_root: Path | None = None,
) -> dict[str, Any]:
    raw = {category: _read_category(cohort_root, category) for category in CATEGORIES}
    criteria_sha256 = _sha256_json(criteria)
    content_hashes = {
        category: sorted(_sha256_json(value) for value in raw[category])
        for category in CATEGORIES
    }
    source_context_binding_hashes: list[str] = []

    errors: collections.Counter[str] = collections.Counter()
    no_effect_violations = 0
    prospectives: dict[str, dict[str, Any]] = {}
    eligibilities: dict[str, dict[str, Any]] = {}
    records: list[dict[str, Any]] = []
    attempts: list[dict[str, Any]] = []
    record_ids: set[str] = set()
    attempt_ids: set[str] = set()

    def validate_many(values: list[dict[str, Any]], validator: Any, sink: Any, category: str) -> None:
        nonlocal no_effect_violations
        for value in values:
            try:
                validated = validator(value)
            except AuditError as exc:
                errors[f"{category}:{exc}"] += 1
                if "no_effect" in str(exc):
                    no_effect_violations += 1
                continue
            sink(validated)

    def add_prospective(item: dict[str, Any]) -> None:
        key = item["prospective_eligibility_id"]
        if key in prospectives:
            errors["prospective:duplicate_identity"] += 1
            return
        prospectives[key] = item

    def add_eligibility(item: dict[str, Any]) -> None:
        key = item["eligibility_id"]
        if key in eligibilities:
            errors["eligibility:duplicate_identity"] += 1
            return
        eligibilities[key] = item

    def add_record(item: dict[str, Any]) -> None:
        key = item["record_id"]
        if key in record_ids:
            errors["records:duplicate_identity"] += 1
            return
        record_ids.add(key)
        records.append(item)

    def add_attempt(item: dict[str, Any]) -> None:
        key = item["attempt_id"]
        if key in attempt_ids:
            errors["attempts:duplicate_identity"] += 1
            return
        attempt_ids.add(key)
        attempts.append(item)

    validate_many(raw["prospective"], _validate_prospective, add_prospective, "prospective")
    validate_many(raw["eligibility"], _validate_eligibility, add_eligibility, "eligibility")
    validate_many(raw["records"], _validate_record, add_record, "records")
    validate_many(raw["attempts"], _validate_attempt, add_attempt, "attempts")

    coverage: dict[str, collections.Counter[str]] = {
        dimension: collections.Counter() for dimension in criteria["coverage_dimensions"]
    }
    route_schema_versions: collections.Counter[str] = collections.Counter()
    unresolved_manifests: collections.Counter[str] = collections.Counter()
    orphan_eligibility = 0
    prospective_ids_referenced_by_eligibility: set[str] = set()
    prospective_eligibility_counts: collections.Counter[str] = collections.Counter()
    for eligibility in eligibilities.values():
        ref = eligibility["prospective_eligibility"]["prospective_eligibility_id"]
        prospective_ids_referenced_by_eligibility.add(ref)
        source = prospectives.get(ref)
        if source is None:
            orphan_eligibility += 1
            continue
        prospective_ref = eligibility["prospective_eligibility"]
        source_workspace_case = source["workspace_case"]
        expected_prospective_ref = {
            "schema_version": source["schema_version"],
            "prospective_eligibility_id": source["prospective_eligibility_id"],
            "workspace_id": source_workspace_case["workspace_id"],
            "plan_sha256": source_workspace_case["plan_sha256"],
            "workspace_case_id": source_workspace_case["case_id"],
            "frozen_at": source["frozen_at"],
        }
        if prospective_ref != expected_prospective_ref:
            errors["eligibility:prospective_reference_mismatch"] += 1
        if eligibility["frozen_at"] != source["frozen_at"] or eligibility["features"] != source["features"]:
            errors["eligibility:prospective_binding_mismatch"] += 1
        if eligibility.get("case_provenance") != source.get("case_provenance"):
            errors["eligibility:case_provenance_binding_mismatch"] += 1
        source_route = source["canonical_route_evidence"]
        bound_route = eligibility["canonical_route_evidence"]
        route_binding_valid = source_route == bound_route
        if not route_binding_valid:
            errors["eligibility:route_binding_mismatch"] += 1
        prospective_eligibility_counts[ref] += 1
        if route_binding_valid:
            route_schema_versions[str(bound_route["schema_version"])] += 1
            route, repository_context, source_context_sha256, problem = _resolve_route_context(
                source, eligibility, workspace_root, direct_task_binding_root
            )
            if problem:
                unresolved_manifests[problem] += 1
                source_context_binding_hashes.append(
                    _sha256_json(
                        {
                            "schema_version": "operator-routing-shadow-source-context-observation.v1",
                            "eligibility_id": eligibility["eligibility_id"],
                            "status": "unresolved",
                            "reason": problem,
                        }
                    )
                )
            else:
                assert route is not None and source_context_sha256 is not None
                source_context_binding_hashes.append(source_context_sha256)
                task_kind = eligibility["features"].get("task_kind")
                if isinstance(task_kind, str) and task_kind:
                    coverage["task_kind"][task_kind] += 1
                risk_tier = route.get("risk_tier") or eligibility["features"].get("risk_tier") or "legacy-v1-unspecified"
                actual_route = route.get("actual_route") or "unavailable"
                recommended_route = route.get("recommended_route") or "unavailable"
                coverage["risk_tier"][str(risk_tier)] += 1
                coverage["actual_route"][str(actual_route)] += 1
                coverage["recommended_route"][str(recommended_route)] += 1
                coverage["repository_context"][str(repository_context or "unavailable")] += 1

    record_eligibility_refs: set[str] = set()
    record_eligibility_counts: collections.Counter[str] = collections.Counter()
    complete_eligibility_ids: set[str] = set()
    complete_records = 0
    reviewed_records = 0
    abstained_records = 0
    reviewed_missing_primary_evidence = 0
    outcome_labels: collections.Counter[str] = collections.Counter()
    execution_statuses: collections.Counter[str] = collections.Counter()
    case_origin_counts: collections.Counter[str] = collections.Counter()
    capture_path_counts: collections.Counter[str] = collections.Counter()
    independent_label_pair_count = 0
    disagreement_count = 0
    v3_record_count = 0
    observed_execution_eligibility_ids: set[str] = set()
    unknown_execution_eligibility_ids: set[str] = set()
    orphan_records = 0
    for record in records:
        eligibility_id = record["eligibility"]["eligibility_id"]
        record_eligibility_refs.add(eligibility_id)
        record_eligibility_counts[eligibility_id] += 1
        if record_eligibility_counts[eligibility_id] > 1:
            errors["records:multiple_records_for_eligibility"] += 1
        eligibility = eligibilities.get(eligibility_id)
        prospective_id: str | None = None
        if eligibility is None:
            orphan_records += 1
        else:
            prospective_id = eligibility["prospective_eligibility"]["prospective_eligibility_id"]
            expected_record_eligibility_ref: dict[str, Any] = {
                "schema_version": eligibility["schema_version"],
                "eligibility_id": eligibility["eligibility_id"],
                "prospective_eligibility_id": prospective_id,
                "frozen_at": eligibility["frozen_at"],
            }
            if record["schema_version"] == RECORD_SCHEMA_V3:
                prospective_ref = eligibility["prospective_eligibility"]
                expected_record_eligibility_ref |= {
                    "workspace_id": prospective_ref["workspace_id"],
                    "plan_sha256": prospective_ref["plan_sha256"],
                    "workspace_case_id": prospective_ref["workspace_case_id"],
                }
            if record["eligibility"] != expected_record_eligibility_ref:
                errors["records:eligibility_reference_mismatch"] += 1
            if (
                record["eligible_case"] != eligibility["eligible_case"]
                or record["features"] != eligibility["features"]
                or record["canonical_route_evidence"] != eligibility["canonical_route_evidence"]
                or record.get("case_provenance") != eligibility.get("case_provenance")
            ):
                errors["records:eligibility_binding_mismatch"] += 1
        outcome = record["outcome"]
        complete = False
        if outcome["status"] == "reviewed":
            reviewed_records += 1
            outcome_labels[str(outcome.get("label", "unknown"))] += 1
            if not record["primary_evidence_refs"]:
                reviewed_missing_primary_evidence += 1
            elif record["schema_version"] == RECORD_SCHEMA_V3:
                assessments = record["semantic_assessments"]
                execution_observed = record["execution_provenance"]["status"] in EXECUTION_STATUSES
                if len(assessments) >= 2:
                    independent_label_pair_count += 1
                    if len({item["label"] for item in assessments}) > 1:
                        disagreement_count += 1
                    complete = execution_observed or not criteria["require_execution_failure_provenance_for_pass"]
            elif not criteria["require_disagreement_observability_for_pass"]:
                complete = True
        else:
            abstained_records += 1
        if record["schema_version"] == RECORD_SCHEMA_V3:
            v3_record_count += 1
            provenance = record["case_provenance"]
            case_origin_counts[provenance["case_origin"]] += 1
            capture_path_counts[provenance["capture_path"]] += 1
            execution_status = record["execution_provenance"]["status"]
            execution_statuses[execution_status] += 1
            if execution_status in EXECUTION_STATUSES:
                observed_execution_eligibility_ids.add(eligibility_id)
            else:
                unknown_execution_eligibility_ids.add(eligibility_id)
        if complete:
            complete_records += 1
            if eligibility is not None:
                complete_eligibility_ids.add(eligibility_id)

    attempt_statuses: collections.Counter[str] = collections.Counter()
    attempt_reasons: collections.Counter[str] = collections.Counter()
    attempted_prospective_ids: set[str] = set()
    dangling_attempt_refs = 0
    for attempt in attempts:
        attempt_statuses[attempt["status"]] += 1
        attempt_reasons[attempt["reason_code"]] += 1
        ref = attempt["prospective_eligibility_id"]
        if isinstance(ref, str):
            attempted_prospective_ids.add(ref)
            if ref not in prospectives:
                dangling_attempt_refs += 1

    production_eligibility_ids = {
        key for key, value in eligibilities.items()
        if value.get("case_provenance", {}).get("case_origin") == "production"
    }
    legacy_eligibility_ids = {
        key for key, value in eligibilities.items() if value["schema_version"] == ELIGIBILITY_SCHEMA
    }
    treatment_eligibility_ids = set(production_eligibility_ids)
    if not criteria["require_test_quarantine_provenance_for_pass"]:
        treatment_eligibility_ids |= legacy_eligibility_ids
    nonproduction_eligibility_count = sum(
        1 for value in eligibilities.values()
        if value.get("case_provenance", {}).get("case_origin") in {"test", "synthetic", "quarantined"}
    )
    treatment_execution_provenance_missing_count = len(
        treatment_eligibility_ids - observed_execution_eligibility_ids
    )
    prospective_count = len(prospectives)
    treatment_case_count = len(treatment_eligibility_ids)
    complete_treatment_case_count = len(complete_eligibility_ids & treatment_eligibility_ids)
    completeness_percent = _percent(complete_treatment_case_count, treatment_case_count)
    missing_evidence_percent = _percent(reviewed_missing_primary_evidence, reviewed_records)
    observed_stratum_deficits: dict[str, int] = {}
    per_stratum_minimum = int(criteria["minimum_cases_per_observed_stratum"])
    for dimension, counts in coverage.items():
        deficient = sum(1 for count in counts.values() if count < per_stratum_minimum)
        if deficient:
            observed_stratum_deficits[dimension] = deficient

    integrity_error_count = sum(errors.values()) + orphan_eligibility + orphan_records + dangling_attempt_refs
    attempt_accounting_gap_count = len(set(prospectives) - attempted_prospective_ids)
    capture_error_count = attempt_statuses.get("error", 0)
    capture_rejection_count = attempt_statuses.get("rejected", 0)
    disagreement_observable = v3_record_count > 0
    test_quarantine_provenance_observable = any(
        value["schema_version"] == ELIGIBILITY_SCHEMA_V3 for value in eligibilities.values()
    )
    execution_failure_provenance_observable = (
        bool(treatment_eligibility_ids)
        and treatment_execution_provenance_missing_count == 0
    )
    disagreement_rate = _percent(disagreement_count, independent_label_pair_count) if independent_label_pair_count else None
    cohort_identity_sha256 = _sha256_json(
        {
            "criteria_sha256": criteria_sha256,
            "content_hashes": content_hashes,
            "source_context_binding_hashes": sorted(source_context_binding_hashes),
        }
    )

    reasons: list[str] = []
    result = "PASS"
    if criteria["require_zero_integrity_errors"] and integrity_error_count:
        result = "FAIL"
        reasons.append("integrity_errors_present")
    if criteria["require_zero_no_effect_violations"] and no_effect_violations:
        result = "FAIL"
        reasons.append("no_effect_violation")
    if criteria["capture_error_blocks_pass"] and capture_error_count:
        result = "FAIL"
        reasons.append("capture_errors_present")
    if reviewed_records and missing_evidence_percent > float(criteria["maximum_missing_primary_evidence_percent_of_non_abstaining"]):
        result = "FAIL"
        reasons.append("primary_evidence_missingness_above_limit")
    if result != "FAIL":
        if criteria["capture_rejection_blocks_pass"] and capture_rejection_count:
            result = "CONTINUE-COLLECTING"
            reasons.append("capture_rejections_require_selection_bias_review")
        if criteria["require_disagreement_observability_for_pass"] and not disagreement_observable:
            result = "CONTINUE-COLLECTING"
            reasons.append("semantic_reviewer_disagreement_unobservable")
        if (
            criteria["require_test_quarantine_provenance_for_pass"]
            and not test_quarantine_provenance_observable
        ):
            result = "CONTINUE-COLLECTING"
            reasons.append("test_quarantine_provenance_unobservable")
        if (
            criteria["require_execution_failure_provenance_for_pass"]
            and not execution_failure_provenance_observable
        ):
            result = "CONTINUE-COLLECTING"
            reasons.append("execution_failure_provenance_unobservable")
        if treatment_case_count < int(criteria["minimum_treatment_cases"]):
            result = "CONTINUE-COLLECTING"
            reasons.append("minimum_treatment_cases_not_met")
        elif completeness_percent < float(criteria["inconclusive_floor_percent"]):
            result = "FAIL"
            reasons.append("completeness_below_falsification_floor")
        elif completeness_percent < float(criteria["pass_completeness_percent"]):
            result = "CONTINUE-COLLECTING"
            reasons.append("pass_completeness_not_met")
        if unresolved_manifests and criteria["require_zero_unresolved_manifest_bindings_for_pass"] and result == "PASS":
            result = "CONTINUE-COLLECTING"
            reasons.append("manifest_bindings_unresolved")
        if attempt_accounting_gap_count and criteria["require_attempt_accounting_for_pass"] and result == "PASS":
            result = "CONTINUE-COLLECTING"
            reasons.append("attempt_accounting_incomplete")
        if observed_stratum_deficits and result == "PASS":
            result = "CONTINUE-COLLECTING"
            reasons.append("observed_stratum_minimum_not_met")

    report = {
        "schema_version": "operator-routing-shadow-readiness-gate-report.v1",
        "task": "OPERATOR-ML-READINESS-V1-T004",
        "gate_result": result,
        "gate_reasons": reasons,
        "criteria_sha256": criteria_sha256,
        "cohort_identity_sha256": cohort_identity_sha256,
        "sources": {
            "cohort": "Grabowski create-only operator-routing-shadow cohort",
            "agent_workspace_manifests": "read_only",
            "source_context_binding_count": len(source_context_binding_hashes),
            "raw_payload_exported": False,
            "model_training_performed": False,
        },
        "counts": {
            "prospective": prospective_count,
            "eligibility": len(eligibilities),
            "eligible_treatment_cases": treatment_case_count,
            "excluded_nonproduction_cases": nonproduction_eligibility_count,
            "legacy_provenance_unobservable_cases": len(legacy_eligibility_ids),
            "records": len(records),
            "attempts": len(attempts),
            "prospective_unbound": len(set(prospectives) - prospective_ids_referenced_by_eligibility),
            "eligibility_unsealed": len(set(eligibilities) - record_eligibility_refs),
            "reviewed_records": reviewed_records,
            "abstained_records": abstained_records,
            "complete_records": complete_records,
            "complete_treatment_cases": complete_treatment_case_count,
            "prospective_cases_with_multiple_eligibilities": sum(
                1 for count in prospective_eligibility_counts.values() if count > 1
            ),
            "reviewed_missing_primary_evidence": reviewed_missing_primary_evidence,
        },
        "quality": {
            "direct_route_plus_reviewed_outcome_completeness_percent": completeness_percent,
            "reviewed_missing_primary_evidence_percent": missing_evidence_percent,
            "integrity_error_count": integrity_error_count,
            "no_effect_violation_count": no_effect_violations,
            "unresolved_manifest_binding_count": sum(unresolved_manifests.values()),
            "attempt_accounting_gap_count": attempt_accounting_gap_count,
            "capture_rejection_count": capture_rejection_count,
        },
        "attempt_accounting": {
            "status_counts": dict(sorted(attempt_statuses.items())),
            "reason_counts": dict(sorted(attempt_reasons.items())),
            "dangling_prospective_reference_count": dangling_attempt_refs,
            "unbound_prospective_count": len(set(prospectives) - prospective_ids_referenced_by_eligibility),
            "unsealed_eligibility_count": len(set(eligibilities) - record_eligibility_refs),
            "execution_abort_reason_observable": execution_failure_provenance_observable,
            "infrastructure_failure_reason_observable": execution_failure_provenance_observable,
            "execution_status_counts": dict(sorted(execution_statuses.items())),
            "treatment_execution_provenance_missing_count": treatment_execution_provenance_missing_count,
            "selection_bias_interpretation": (
                "capture attempts, unbound prospective cases and unsealed eligibility are counted; "
                "v3 records additionally separate completion, execution abort and infrastructure failure"
                if execution_failure_provenance_observable
                else "capture attempts, unbound prospective cases and unsealed eligibility are counted, but legacy capture does not encode execution failure provenance"
            ),
        },
        "coverage": {
            "route_schema_versions": {version: route_schema_versions.get(str(version), 0) for version in criteria["route_schema_versions_reported_separately"]},
            "dimensions": {dimension: dict(sorted(counts.items())) for dimension, counts in coverage.items()},
            "observed_stratum_deficits": dict(sorted(observed_stratum_deficits.items())),
            "unresolved_manifest_reasons": dict(sorted(unresolved_manifests.items())),
            "representativeness_claim": "none_for_unobserved_or_undercovered_strata",
        },
        "outcomes": {
            "reviewed_label_counts": dict(sorted(outcome_labels.items())),
            "lifecycle_state_promoted_to_semantic_label": False,
            "semantic_review_disagreement": {
                "observable": disagreement_observable,
                "independent_label_pair_count": independent_label_pair_count,
                "disagreement_count": disagreement_count if disagreement_observable else None,
                "disagreement_rate_percent": disagreement_rate,
                "limitation": (
                    "v3 makes independent pseudonymized assessments observable; records without two assessments remain incomplete"
                    if disagreement_observable
                    else "legacy v2 records contain no independently attributable second semantic assessment"
                ),
            },
        },
        "cohort_provenance": {
            "test_quarantine_provenance_observable": test_quarantine_provenance_observable,
            "test_or_quarantine_contamination_count": 0 if test_quarantine_provenance_observable else None,
            "excluded_case_origin_counts": {
                key: value for key, value in sorted(case_origin_counts.items()) if key != "production"
            },
            "case_origin_counts": dict(sorted(case_origin_counts.items())),
            "capture_path_counts": dict(sorted(capture_path_counts.items())),
            "execution_failure_provenance_observable": execution_failure_provenance_observable,
            "limitation": (
                "v3 provenance is observable and non-production cases are excluded from the treatment denominator"
                if test_quarantine_provenance_observable
                else "legacy capture has no explicit production/test/synthetic/quarantine provenance"
            ),
        },
        "privacy_and_effect_boundary": {
            "raw_transcripts_exported": False,
            "raw_prompts_exported": False,
            "raw_argv_exported": False,
            "raw_workspace_or_task_ids_exported": False,
            "no_effect_expected": dict(NO_EFFECT),
        },
        "errors": dict(sorted(errors.items())),
        "does_not_establish": list(criteria["does_not_establish"]),
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cohort-root", required=True)
    parser.add_argument("--agent-workspace-root", required=True)
    parser.add_argument("--direct-task-binding-root")
    parser.add_argument("--criteria", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    criteria = _read_json(Path(args.criteria))
    report = audit(
        Path(args.cohort_root),
        Path(args.agent_workspace_root),
        criteria,
        Path(args.direct_task_binding_root) if args.direct_task_binding_root else None,
    )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"gate_result": report["gate_result"], "cohort_identity_sha256": report["cohort_identity_sha256"], "output": str(output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
