#!/usr/bin/env python3
"""Validate the rLens agent-context condition measurement seed.

This is a narrow validator for experiments/2026-07-08_rlens-agent-context-conditions.
It checks the design surface only; it does not execute runs or claim condition effects.
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
    / "2026-07-08_rlens-agent-context-conditions"
    / "measurement-plan.yml"
)
REQUIRED_CONDITIONS = {
    "no_rlens",
    "reading_pack",
    "context_pack",
    "trace_gated",
}
DIAGNOSTIC_CONDITION = "full_dump"
REQUIRED_METRICS = {
    "unsupported_claim_count",
    "hallucinated_path_count",
    "missing_evidence_count",
    "rework_count",
}
FORBIDDEN_PRE_EXECUTION_CLAIMS = {
    "context condition superiority",
    "default rLens access level readiness",
    "agent quality improvement",
    "repo understanding improvement",
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


def validate_measurement_plan(path: Path = DEFAULT_PLAN) -> list[str]:
    errors: list[str] = []
    try:
        data = _load_yaml(path)
    except ValueError as exc:
        return [str(exc)]

    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if data.get("experiment") != "rlens-agent-context-conditions":
        errors.append("experiment must be rlens-agent-context-conditions")
    if data.get("status") != "designed":
        errors.append("status must remain designed until real runs exist")
    if data.get("bureau_task") != "BUR-2026-002-T005":
        errors.append("bureau_task must bind to BUR-2026-002-T005")

    conditions = data.get("conditions")
    if not isinstance(conditions, dict):
        errors.append("conditions must be a mapping")
        conditions = {}
    condition_ids = set(conditions)
    missing_conditions = sorted(REQUIRED_CONDITIONS - condition_ids)
    if missing_conditions:
        errors.append("missing required conditions: " + ", ".join(missing_conditions))
    if DIAGNOSTIC_CONDITION not in condition_ids:
        errors.append("missing diagnostic full_dump condition")
    else:
        full_dump = conditions.get(DIAGNOSTIC_CONDITION)
        if not isinstance(full_dump, dict) or full_dump.get("default_candidate") is not False:
            errors.append("full_dump must be present but default_candidate: false")

    required_condition_ids = data.get("required_condition_ids")
    if not isinstance(required_condition_ids, list):
        errors.append("required_condition_ids must be a list")
    else:
        listed = set(str(item) for item in required_condition_ids)
        expected = REQUIRED_CONDITIONS | {DIAGNOSTIC_CONDITION}
        missing_listed = sorted(expected - listed)
        if missing_listed:
            errors.append("required_condition_ids omits: " + ", ".join(missing_listed))

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
        if metric.get("lower_is_better") is not True:
            errors.append(f"metric {metric_id} must set lower_is_better: true")
        definition = metric.get("definition")
        if not isinstance(definition, str) or not definition.strip():
            errors.append(f"metric {metric_id} needs a definition")

    gate = data.get("promotion_gate")
    if not isinstance(gate, dict):
        errors.append("promotion_gate must be a mapping")
        gate = {}
    if gate.get("default_access_may_be_promoted") is not False:
        errors.append("pre-execution design must not promote default access")
    minimum = gate.get("minimum_evidence_before_promotion")
    if not isinstance(minimum, dict):
        errors.append("promotion_gate.minimum_evidence_before_promotion must be a mapping")
    else:
        if int(minimum.get("comparable_task_pairs", 0)) < 3:
            errors.append("promotion gate needs at least three comparable task pairs")
        directional = set(minimum.get("required_directional_metrics") or [])
        missing_directional = sorted(REQUIRED_METRICS - directional)
        if missing_directional:
            errors.append("promotion gate omits directional metrics: " + ", ".join(missing_directional))
    disallowed = set(str(item) for item in gate.get("disallowed_pre_execution_claims") or [])
    missing_disallowed = sorted(FORBIDDEN_PRE_EXECUTION_CLAIMS - disallowed)
    if missing_disallowed:
        errors.append("missing disallowed pre-execution claims: " + ", ".join(missing_disallowed))

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default=str(DEFAULT_PLAN))
    args = parser.parse_args(argv)
    errors = validate_measurement_plan(Path(args.path))
    if errors:
        print("rLens agent-context condition validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("rLens agent-context condition measurement plan valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
