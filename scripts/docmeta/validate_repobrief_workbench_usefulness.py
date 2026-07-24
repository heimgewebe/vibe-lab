#!/usr/bin/env python3
"""Validate the RepoBrief Workbench usefulness evaluation design.

This is a narrow historical validator for the archived 2026-07-09 RepoBrief Workbench experiment.
It validates the measurement design only. It does not execute runs or claim that
RepoBrief/Agent Workbench improves agent code work.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover - dependency failure path
    raise SystemExit("ERROR: PyYAML is required") from exc

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PLAN = (
    REPO_ROOT
    / "experiments"
    / "_archive"
    / "2026-07-09_repobrief-workbench-usefulness-eval"
    / "measurement-plan.yml"
)
REQUIRED_CONDITIONS = {
    "no_context_no_rlens",
    "reading_pack",
    "context_pack",
    "full_resolved_evidence",
    "trace_gated",
}
DIAGNOSTIC_CONDITION = "full_resolved_evidence"
REQUIRED_METRICS = {
    "localization",
    "evidence_completeness",
    "patch_scope",
    "check_fit",
    "miss_taxonomy",
    "false_confidence_risk",
}
FALSE_CONFIDENCE_FIELDS = {
    "unsupported_claim_count",
    "hallucinated_path_count",
    "uncited_claim_count",
    "stale_context_claim_count",
}
REQUIRED_MISS_CATEGORIES = {
    "localization_miss",
    "evidence_gap",
    "freshness_miss",
    "live_state_gap",
    "scope_creep",
    "check_miss",
    "contract_miss",
    "boundary_miss",
    "self_proof",
    "external_regression",
}
FORBIDDEN_PRE_EXECUTION_CLAIMS = {
    "condition superiority",
    "default workbench readiness",
    "agent quality improvement",
    "repo understanding improvement",
    "patch correctness",
    "test sufficiency",
    "merge readiness",
}
REQUIRED_NON_CLAIMS = {
    "runtime_correctness",
    "test_sufficiency",
    "review_completeness",
    "merge_readiness",
    "security_correctness",
    "agent_quality_improvement",
    "condition_superiority",
    "default_promotion_readiness",
}


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except FileNotFoundError as exc:
        raise ValueError(f"missing measurement plan: {path}") from exc
    except yaml.YAMLError as exc:
        raise ValueError(f"measurement plan is not valid YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("measurement plan must be a YAML mapping")
    return data


def _require_string(value: Any, field: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{field} must be a non-empty string")


def _require_list_contains(
    value: Any,
    required: set[str],
    field: str,
    errors: list[str],
) -> set[str]:
    if not isinstance(value, list):
        errors.append(f"{field} must be a list")
        return set()
    actual = {str(item) for item in value}
    missing = sorted(required - actual)
    if missing:
        errors.append(f"{field} omits: " + ", ".join(missing))
    return actual


def validate_measurement_plan(path: Path = DEFAULT_PLAN) -> list[str]:
    errors: list[str] = []
    try:
        data = _load_yaml(path)
    except ValueError as exc:
        return [str(exc)]

    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if data.get("experiment") != "repobrief-workbench-usefulness-eval":
        errors.append("experiment must be repobrief-workbench-usefulness-eval")
    if data.get("bureau_task") != "RPU-V1-T012":
        errors.append("bureau_task must bind to RPU-V1-T012")
    if data.get("status") != "designed":
        errors.append("status must remain designed until executed comparable runs exist")

    listed_conditions = _require_list_contains(
        data.get("required_condition_ids"),
        REQUIRED_CONDITIONS,
        "required_condition_ids",
        errors,
    )

    conditions = data.get("conditions")
    if not isinstance(conditions, dict):
        errors.append("conditions must be a mapping")
        conditions = {}
    missing_conditions = sorted(REQUIRED_CONDITIONS - set(conditions))
    if missing_conditions:
        errors.append("missing required conditions: " + ", ".join(missing_conditions))
    for condition_id in REQUIRED_CONDITIONS:
        condition = conditions.get(condition_id)
        if not isinstance(condition, dict):
            continue
        _require_string(condition.get("description"), f"condition {condition_id}.description", errors)
        if condition.get("default_candidate") not in {True, False}:
            errors.append(f"condition {condition_id} must declare default_candidate")
        for field in ("allowed_evidence", "disallowed_evidence"):
            if not isinstance(condition.get(field), list) or not condition.get(field):
                errors.append(f"condition {condition_id}.{field} must be a non-empty list")
    if listed_conditions and set(conditions) & REQUIRED_CONDITIONS != REQUIRED_CONDITIONS:
        errors.append("listed conditions and condition mappings are not aligned")
    full_resolved = conditions.get(DIAGNOSTIC_CONDITION)
    if not isinstance(full_resolved, dict):
        errors.append("full_resolved_evidence condition must be a mapping")
    else:
        if full_resolved.get("default_candidate") is not False:
            errors.append("full_resolved_evidence must not be a default candidate")
        if full_resolved.get("diagnostic_only") is not True:
            errors.append("full_resolved_evidence must be diagnostic_only: true")

    metrics = data.get("metrics")
    if not isinstance(metrics, dict):
        errors.append("metrics must be a mapping")
        metrics = {}
    missing_metrics = sorted(REQUIRED_METRICS - set(metrics))
    if missing_metrics:
        errors.append("missing required metrics: " + ", ".join(missing_metrics))
    for metric_id in REQUIRED_METRICS & set(metrics):
        metric = metrics.get(metric_id)
        if not isinstance(metric, dict):
            errors.append(f"metric {metric_id} must be a mapping")
            continue
        _require_string(metric.get("definition"), f"metric {metric_id}.definition", errors)
        if metric.get("lower_is_better") not in {True, False}:
            errors.append(f"metric {metric_id} must declare lower_is_better")
    false_confidence = metrics.get("false_confidence_risk", {})
    if isinstance(false_confidence, dict):
        _require_list_contains(
            false_confidence.get("required_fields"),
            FALSE_CONFIDENCE_FIELDS,
            "metrics.false_confidence_risk.required_fields",
            errors,
        )
    miss_taxonomy = metrics.get("miss_taxonomy", {})
    if isinstance(miss_taxonomy, dict):
        _require_list_contains(
            miss_taxonomy.get("required_categories"),
            REQUIRED_MISS_CATEGORIES,
            "metrics.miss_taxonomy.required_categories",
            errors,
        )

    no_self_proof = data.get("no_self_proof_rule")
    if not isinstance(no_self_proof, dict):
        errors.append("no_self_proof_rule must be a mapping")
    else:
        if no_self_proof.get("required") is not True:
            errors.append("no_self_proof_rule.required must be true")
        _require_list_contains(
            no_self_proof.get("violation_fields"),
            {"self_authored_check_only", "self_proof_violation"},
            "no_self_proof_rule.violation_fields",
            errors,
        )
        _require_string(no_self_proof.get("statement"), "no_self_proof_rule.statement", errors)

    gate = data.get("promotion_gate")
    if not isinstance(gate, dict):
        errors.append("promotion_gate must be a mapping")
        gate = {}
    if gate.get("default_access_may_be_promoted") is not False:
        errors.append("pre-execution design must not promote default workbench access")
    minimum = gate.get("minimum_evidence_before_promotion")
    if not isinstance(minimum, dict):
        errors.append("promotion_gate.minimum_evidence_before_promotion must be a mapping")
    else:
        if int(minimum.get("comparable_task_pairs", 0)) < 3:
            errors.append("promotion gate needs at least three comparable task pairs")
        _require_list_contains(
            minimum.get("required_directional_metrics"),
            REQUIRED_METRICS,
            "promotion_gate.minimum_evidence_before_promotion.required_directional_metrics",
            errors,
        )
        _require_list_contains(
            minimum.get("required_external_observations"),
            {"ci_or_existing_test_result", "operator_or_review_observation"},
            "promotion_gate.minimum_evidence_before_promotion.required_external_observations",
            errors,
        )
    _require_list_contains(
        gate.get("disallowed_pre_execution_claims"),
        FORBIDDEN_PRE_EXECUTION_CLAIMS,
        "promotion_gate.disallowed_pre_execution_claims",
        errors,
    )
    _require_list_contains(data.get("non_claims"), REQUIRED_NON_CLAIMS, "non_claims", errors)

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default=str(DEFAULT_PLAN))
    args = parser.parse_args(argv)
    errors = validate_measurement_plan(Path(args.path))
    if errors:
        print("RepoBrief Workbench usefulness validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("RepoBrief Workbench usefulness measurement plan valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
