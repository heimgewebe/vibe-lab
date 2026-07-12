#!/usr/bin/env python3
"""Deterministically evaluate one prospectively registered experiment."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from collections import Counter
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def result_sha256(value: dict[str, Any]) -> str:
    """Hash a result with its self-referential digest field omitted."""
    unsigned = dict(value)
    unsigned.pop("result_sha256", None)
    return sha256_json(unsigned)


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: root must be object")
    return value


def validate_schema(value: dict[str, Any], schema_path: Path) -> None:
    Draft202012Validator(load_object(schema_path), format_checker=FormatChecker()).validate(value)


def _round(value: float | None) -> float | None:
    if value is None:
        return None
    rounded = round(value, 10)
    return 0.0 if rounded == -0.0 else rounded


def _sample_variance(values: list[float]) -> float:
    return statistics.variance(values) if len(values) >= 2 else 0.0


_T_95 = {
    1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571,
    6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
    11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131,
    16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086,
    21: 2.080, 22: 2.074, 23: 2.069, 24: 2.064, 25: 2.060,
    26: 2.056, 27: 2.052, 28: 2.048, 29: 2.045, 30: 2.042,
}


def _t_critical_95(df: int) -> float:
    if df < 1:
        raise ValueError("positive degrees of freedom required")
    return _T_95.get(min(df, 30), 2.042)


def _build_base(registration: dict[str, Any], observations: dict[str, Any]) -> dict[str, Any]:
    measurement = registration["measurement"]
    return {
        "schema_version": "effect-evaluation.result.v1",
        "experiment_id": registration["experiment_id"],
        "registration_sha256": sha256_json(registration),
        "observations_sha256": sha256_json(observations),
        "metric": measurement["primary_metric"],
        "direction": measurement["direction"],
        "unit": measurement["unit"],
        "minimum_material_effect": measurement["minimum_material_effect"],
        "comparison_mode": registration["comparison"]["mode"],
    }


def evaluate(registration: dict[str, Any], observations: dict[str, Any], *, repo_root: Path = ROOT) -> dict[str, Any]:
    validate_schema(registration, repo_root / "schemas/experiment.registration.v2.schema.json")
    validate_schema(observations, repo_root / "schemas/effect-evaluation.observations.v1.schema.json")
    if registration["experiment_id"] != observations["experiment_id"]:
        raise ValueError("experiment_id mismatch")
    if registration["measurement"]["primary_metric"] != observations["metric"]:
        raise ValueError("primary metric mismatch")

    control_id = registration["control_condition"]["id"]
    treatment_id = registration["treatment_condition"]["id"]
    allowed_conditions = {control_id, treatment_id}
    rows = observations["observations"]
    ids: set[str] = set()
    evidence_refs: set[str] = set()
    reasons: list[str] = []
    for row in rows:
        if row["observation_id"] in ids:
            raise ValueError("duplicate observation_id")
        ids.add(row["observation_id"])
        if row["evidence_ref"] in evidence_refs:
            raise ValueError("duplicate evidence_ref")
        evidence_refs.add(row["evidence_ref"])
        if row["condition"] not in allowed_conditions:
            raise ValueError("unknown condition")
        if not math.isfinite(float(row["value"])):
            raise ValueError("non-finite observation value")

    control = [row for row in rows if row["condition"] == control_id]
    treatment = [row for row in rows if row["condition"] == treatment_id]
    comparison = registration["comparison"]
    minimum_sample_met = (
        len(control) >= comparison["minimum_control"]
        and len(treatment) >= comparison["minimum_treatment"]
    )
    if not minimum_sample_met:
        reasons.append("minimum sample size not met")

    independence_met = True
    if registration["evidence_sources"]["independent_observation_required"]:
        independence_met = all(row["independent"] for row in rows)
        if not independence_met:
            reasons.append("independent observation requirement not met")

    comparable = True
    paired_differences: list[float] = []
    complete_pairs: int | None = None
    if comparison["mode"] == "paired":
        if any(not row.get("pair_id") for row in rows):
            comparable = False
            reasons.append("paired comparison requires pair_id on every observation")
        else:
            by_pair: dict[str, dict[str, dict[str, Any]]] = {}
            for row in rows:
                bucket = by_pair.setdefault(row["pair_id"], {})
                if row["condition"] in bucket:
                    raise ValueError("duplicate condition within pair")
                bucket[row["condition"]] = row
            incomplete = [pair for pair, bucket in by_pair.items() if set(bucket) != allowed_conditions]
            mismatched_keys = [
                pair
                for pair, bucket in by_pair.items()
                if set(bucket) == allowed_conditions
                and bucket[control_id]["comparison_key"] != bucket[treatment_id]["comparison_key"]
            ]
            if incomplete:
                comparable = False
                reasons.append("paired comparison has incomplete pairs")
            if mismatched_keys:
                comparable = False
                reasons.append("paired comparison_key values differ within pairs")
            if not incomplete and not mismatched_keys:
                complete_pairs = len(by_pair)
                for pair in sorted(by_pair):
                    c = float(by_pair[pair][control_id]["value"])
                    t = float(by_pair[pair][treatment_id]["value"])
                    raw = t - c
                    paired_differences.append(raw if registration["measurement"]["direction"] == "higher_is_better" else -raw)
    else:
        control_keys = Counter(row["comparison_key"] for row in control)
        treatment_keys = Counter(row["comparison_key"] for row in treatment)
        if control_keys != treatment_keys:
            comparable = False
            reasons.append("unpaired comparison_key distributions differ")

    control_values = [float(row["value"]) for row in control]
    treatment_values = [float(row["value"]) for row in treatment]
    control_mean = statistics.fmean(control_values) if control_values else None
    treatment_mean = statistics.fmean(treatment_values) if treatment_values else None
    raw_difference = treatment_mean - control_mean if control_mean is not None and treatment_mean is not None else None
    direction = registration["measurement"]["direction"]
    favorable_effect = raw_difference if direction == "higher_is_better" else (-raw_difference if raw_difference is not None else None)
    relative_difference = None
    if raw_difference is not None and control_mean not in (None, 0.0):
        relative_difference = raw_difference / abs(control_mean)

    ci = None
    if comparable and minimum_sample_met and independence_met:
        if comparison["mode"] == "paired":
            if len(paired_differences) >= 2:
                mean = statistics.fmean(paired_differences)
                se = math.sqrt(_sample_variance(paired_differences) / len(paired_differences))
                critical = _t_critical_95(len(paired_differences) - 1)
                ci = {"lower": _round(mean - critical * se), "upper": _round(mean + critical * se), "method": "student_t_95_paired"}
            else:
                reasons.append("at least two complete pairs are required for uncertainty")
        elif len(control_values) >= 2 and len(treatment_values) >= 2 and favorable_effect is not None:
            se = math.sqrt(_sample_variance(control_values) / len(control_values) + _sample_variance(treatment_values) / len(treatment_values))
            # Conservative small-sample bound: use the smaller arm degrees of freedom.
            critical = _t_critical_95(min(len(control_values) - 1, len(treatment_values) - 1))
            ci = {"lower": _round(favorable_effect - critical * se), "upper": _round(favorable_effect + critical * se), "method": "student_t_95_unpaired_conservative"}

    threshold = float(registration["measurement"]["minimum_material_effect"])
    verdict = "insufficient_evidence"
    if ci is not None:
        if ci["lower"] > threshold:
            verdict = "beneficial"
        elif ci["upper"] < -threshold:
            verdict = "harmful"
        elif ci["lower"] >= -threshold and ci["upper"] <= threshold:
            verdict = "no_material_effect"
        else:
            reasons.append("confidence interval crosses a material-effect boundary")

    result = {
        **_build_base(registration, observations),
        "sample": {"control": len(control), "treatment": len(treatment), "complete_pairs": complete_pairs},
        "statistics": {
            "control_mean": _round(control_mean),
            "treatment_mean": _round(treatment_mean),
            "raw_difference": _round(raw_difference),
            "favorable_effect": _round(favorable_effect),
            "relative_difference": _round(relative_difference),
            "confidence_interval_95": ci,
        },
        "data_quality": {
            "comparable": comparable,
            "minimum_sample_met": minimum_sample_met,
            "independence_met": independence_met,
            "reasons": reasons,
        },
        "effect_claim_allowed": verdict != "insufficient_evidence",
        "verdict": verdict,
        "does_not_establish": [
            "causal_generality_beyond_registered_conditions",
            "automatic_policy_change",
            "automatic_routing_change",
            "automatic_bureau_task_creation",
            "caller_supplied_independence_correctness",
        ],
    }
    result["result_sha256"] = result_sha256(result)
    validate_schema(result, repo_root / "schemas/effect-evaluation.result.v1.schema.json")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", required=True, type=Path)
    parser.add_argument("--observations", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = evaluate(load_object(args.registration), load_object(args.observations))
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
