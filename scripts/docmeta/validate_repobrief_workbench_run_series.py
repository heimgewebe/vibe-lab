#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("ERROR: PyYAML is required") from exc

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RUN_SERIES = (
    REPO_ROOT
    / "experiments"
    / "_archive"
    / "2026-07-09_repobrief-workbench-usefulness-eval"
    / "results"
    / "run-series.yml"
)
REQUIRED_SCORE_GROUPS = {
    "localization",
    "evidence_completeness",
    "patch_scope",
    "check_fit",
    "miss_taxonomy",
    "false_confidence_risk",
    "effort_overhead",
}
REQUIRED_FALSE_CONFIDENCE_FIELDS = {
    "unsupported_claim_count",
    "hallucinated_path_count",
    "uncited_claim_count",
    "stale_context_claim_count",
}
REQUIRED_EXTERNAL_TYPES = {"ci", "merge"}
REQUIRED_FINAL_DECISIONS = {
    "no_context_no_rlens",
    "reading_pack",
    "context_pack",
    "full_resolved_evidence",
    "trace_gated",
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
        raise ValueError(f"missing run series: {path}") from exc
    except yaml.YAMLError as exc:
        raise ValueError(f"run series is not valid YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("run series must be a YAML mapping")
    return data


def _as_set(value: Any) -> set[str]:
    if isinstance(value, dict):
        return {str(key) for key in value}
    if isinstance(value, list):
        return {str(item) for item in value}
    return set()


def validate_run_series(path: Path = DEFAULT_RUN_SERIES) -> list[str]:
    errors: list[str] = []
    try:
        data = _load_yaml(path)
    except ValueError as exc:
        return [str(exc)]
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if data.get("bureau_task") != "RPU-V1-T021":
        errors.append("bureau_task must be RPU-V1-T021")
    if data.get("status") != "executed_limited":
        errors.append("status must be executed_limited")

    runs = data.get("runs")
    if not isinstance(runs, list) or len(runs) < 3:
        errors.append("run series must contain at least three runs")
        runs = [] if not isinstance(runs, list) else runs
    for idx, run in enumerate(runs, start=1):
        if not isinstance(run, dict):
            errors.append(f"run {idx} must be a mapping")
            continue
        for field in ("id", "task_id", "source_pr", "condition", "task_class", "decision_signal"):
            if not isinstance(run.get(field), str) or not run[field].strip():
                errors.append(f"run {idx}.{field} must be a non-empty string")
        scores = run.get("scores")
        if not isinstance(scores, dict):
            errors.append(f"run {idx}.scores must be a mapping")
            scores = {}
        missing_scores = sorted(REQUIRED_SCORE_GROUPS - set(scores))
        if missing_scores:
            errors.append(f"run {idx}.scores omits: " + ", ".join(missing_scores))
        false_confidence = scores.get("false_confidence_risk", {})
        if isinstance(false_confidence, dict):
            missing = sorted(REQUIRED_FALSE_CONFIDENCE_FIELDS - set(false_confidence))
            if missing:
                errors.append(f"run {idx}.false_confidence_risk omits: " + ", ".join(missing))
        external_types = {
            str(item.get("type"))
            for item in run.get("external_observations", [])
            if isinstance(item, dict)
        }
        missing_external = sorted(REQUIRED_EXTERNAL_TYPES - external_types)
        if missing_external:
            errors.append(f"run {idx}.external_observations omits: " + ", ".join(missing_external))
        boundaries = run.get("evidence_boundaries")
        if not isinstance(boundaries, dict) or not boundaries.get("disallowed_claims"):
            errors.append(f"run {idx}.evidence_boundaries.disallowed_claims must be present")

    aggregate = data.get("aggregate")
    if not isinstance(aggregate, dict):
        errors.append("aggregate must be a mapping")
        aggregate = {}
    if int(aggregate.get("comparable_run_count", 0)) < 3:
        errors.append("aggregate.comparable_run_count must be at least 3")
    if aggregate.get("comparable_pair_count") != 0:
        errors.append("this limited execution must record zero comparable pairs")
    if aggregate.get("smaller_minimum_justified") is not True:
        errors.append("aggregate.smaller_minimum_justified must be true")

    final_decisions = data.get("final_decisions")
    if not isinstance(final_decisions, dict):
        errors.append("final_decisions must be a mapping")
        final_decisions = {}
    missing_decisions = sorted(REQUIRED_FINAL_DECISIONS - set(final_decisions))
    if missing_decisions:
        errors.append("final_decisions omits: " + ", ".join(missing_decisions))
    if any(str(value) == "promote" for value in final_decisions.values()):
        errors.append("limited run series must not promote a default condition")

    missing_non_claims = sorted(REQUIRED_NON_CLAIMS - _as_set(data.get("non_claims")))
    if missing_non_claims:
        errors.append("non_claims omits: " + ", ".join(missing_non_claims))
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default=str(DEFAULT_RUN_SERIES))
    args = parser.parse_args(argv)
    errors = validate_run_series(Path(args.path))
    if errors:
        print("RepoBrief Workbench run-series validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("RepoBrief Workbench run series valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
