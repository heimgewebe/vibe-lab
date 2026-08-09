#!/usr/bin/env python3
"""Deterministically evaluate one prospectively registered experiment."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import statistics
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
REGISTRATION_GATE_PATH = ROOT / "scripts/docmeta/validate_experiment_registration.py"


def _load_registration_gate() -> Any:
    spec = importlib.util.spec_from_file_location("vibe_registration_gate_evaluate", REGISTRATION_GATE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load registration gate from {REGISTRATION_GATE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


REGISTRATION_GATE = _load_registration_gate()


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


def validate_registration_contract(
    registration: dict[str, Any],
    *,
    repo_root: Path,
    registration_path: Path | None = None,
) -> dict[str, Any]:
    if registration_path is not None:
        validated = REGISTRATION_GATE.validate_registration(
            registration_path,
            require_current=False,
        )
        if sha256_json(validated) != sha256_json(registration):
            raise ValueError("registration payload does not match registration path")
        return validated
    experiment_id = registration.get("experiment_id")
    synthetic_path = repo_root / "experiments" / str(experiment_id or "invalid") / "registration.v2.json"
    return REGISTRATION_GATE.validate_registration_payload(
        registration,
        path=synthetic_path,
        require_current=False,
    )


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


def _scorecard_weights(registration: dict[str, Any]) -> dict[str, float] | None:
    scorecard = registration["measurement"].get("scorecard")
    if scorecard is None:
        return None
    components = scorecard["components"]
    weights = {component["id"]: float(component["weight"]) for component in components}
    if len(weights) != len(components):
        raise ValueError("scorecard component ids must be unique")
    return weights


def _fatal_scorecard_components(registration: dict[str, Any]) -> set[str]:
    scorecard = registration["measurement"].get("scorecard")
    if scorecard is None:
        return set()
    return {
        component["id"]
        for component in scorecard["components"]
        if component.get("fatal_when_zero", False)
    }


def _registered_threshold_result(
    registration: dict[str, Any],
    treatment_mean: float | None,
) -> str:
    if treatment_mean is None:
        return "inconclusive"
    criteria = registration["measurement"]["outcome_criteria"]
    success = float(criteria["success_threshold"])
    harm = float(criteria["harm_or_falsification_threshold"])
    if registration["measurement"]["direction"] == "higher_is_better":
        if treatment_mean >= success:
            return "success"
        if treatment_mean <= harm:
            return "harm_or_falsification"
    else:
        if treatment_mean <= success:
            return "success"
        if treatment_mean >= harm:
            return "harm_or_falsification"
    return "inconclusive"


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


def evaluate(
    registration: dict[str, Any],
    observations: dict[str, Any],
    *,
    repo_root: Path = ROOT,
    registration_path: Path | None = None,
) -> dict[str, Any]:
    registration = validate_registration_contract(
        registration,
        repo_root=repo_root,
        registration_path=registration_path,
    )
    validate_schema(observations, repo_root / "schemas/effect-evaluation.observations.v2.schema.json")
    t005_contract = not REGISTRATION_GATE.is_pre_t005_experiment(registration["experiment_id"])
    registered_at = None
    if t005_contract:
        registered_at = datetime.fromisoformat(registration["registered_at"].replace("Z", "+00:00")).astimezone(timezone.utc)
    if registration["experiment_id"] != observations["experiment_id"]:
        raise ValueError("experiment_id mismatch")
    if observations["registration_sha256"] != sha256_json(registration):
        raise ValueError("registration digest mismatch")
    if registration["measurement"]["primary_metric"] != observations["metric"]:
        raise ValueError("primary metric mismatch")

    control_id = registration["control_condition"]["id"]
    treatment_id = registration["treatment_condition"]["id"]
    allowed_conditions = {control_id, treatment_id}
    rows = observations["observations"]
    ids: set[str] = set()
    evidence_refs: set[str] = set()
    evidence_digests: set[str] = set()
    scorecard_weights = _scorecard_weights(registration)
    self_scored_rows: list[str] = []
    unblinded_rows: list[str] = []
    reasons: list[str] = []
    for row in rows:
        if row["observation_id"] in ids:
            raise ValueError("duplicate observation_id")
        ids.add(row["observation_id"])
        if row["evidence_ref"] in evidence_refs:
            raise ValueError("duplicate evidence_ref")
        evidence_refs.add(row["evidence_ref"])
        if row["evidence_sha256"] in evidence_digests:
            raise ValueError("duplicate evidence_sha256")
        evidence_digests.add(row["evidence_sha256"])
        if row["condition"] not in allowed_conditions:
            raise ValueError("unknown condition")
        if not math.isfinite(float(row["value"])):
            raise ValueError("non-finite observation value")
        effort = float(row["effort_seconds"])
        if not math.isfinite(effort) or effort < 0:
            raise ValueError("effort_seconds must be finite and non-negative")
        if not row["scoring_blinded"]:
            unblinded_rows.append(row["observation_id"])
        components = row.get("score_components")
        if scorecard_weights is None and components is not None:
            raise ValueError("score_components are not registered for this metric")
        if scorecard_weights is not None:
            if not isinstance(components, dict) or set(components) != set(scorecard_weights):
                raise ValueError("score_components must match the registered scorecard exactly")
            expected = sum(scorecard_weights[key] * int(components[key]) for key in scorecard_weights)
            if not math.isclose(float(row["value"]), expected, rel_tol=0.0, abs_tol=1e-12):
                raise ValueError("observation value does not match registered scorecard")
        if row["observer_ref"] == row["decision_maker_ref"]:
            self_scored_rows.append(row["observation_id"])
        captured_at = datetime.fromisoformat(row["captured_at"].replace("Z", "+00:00"))
        expires_at = datetime.fromisoformat(registration["expires_at"].replace("Z", "+00:00"))
        if captured_at.tzinfo is None or expires_at.tzinfo is None:
            raise ValueError("timestamps must include timezone")
        captured_at_utc = captured_at.astimezone(timezone.utc)
        if registered_at is not None and captured_at_utc < registered_at:
            raise ValueError("observation predates experiment registration")
        if captured_at_utc > expires_at.astimezone(timezone.utc):
            raise ValueError("observation captured after experiment expiry")

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
        independence_met = all(row["independent"] for row in rows) and not self_scored_rows
        if any(not row["independent"] for row in rows):
            reasons.append("independent observation requirement not met")
        if self_scored_rows:
            reasons.append("independent scorer must differ from decision maker")

    blinding_met = not unblinded_rows
    comparable = blinding_met
    if not blinding_met:
        reasons.append("condition-label blinding requirement not met")
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
            same_decision_maker = [
                pair
                for pair, bucket in by_pair.items()
                if set(bucket) == allowed_conditions
                and bucket[control_id]["decision_maker_ref"]
                == bucket[treatment_id]["decision_maker_ref"]
            ]
            if incomplete:
                comparable = False
                reasons.append("paired comparison has incomplete pairs")
            if mismatched_keys:
                comparable = False
                reasons.append("paired comparison_key values differ within pairs")
            decision_maker_conflict = bool(same_decision_maker)
            if decision_maker_conflict:
                independence_met = False
                reasons.append("paired conditions require distinct decision_maker_ref values")
            if not incomplete and not mismatched_keys and not decision_maker_conflict:
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

    control_effort = [float(row["effort_seconds"]) for row in control]
    treatment_effort = [float(row["effort_seconds"]) for row in treatment]
    control_effort_mean = statistics.fmean(control_effort) if control_effort else None
    treatment_effort_mean = statistics.fmean(treatment_effort) if treatment_effort else None
    effort_difference = (
        treatment_effort_mean - control_effort_mean
        if control_effort_mean is not None and treatment_effort_mean is not None
        else None
    )

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

    fatal_components = _fatal_scorecard_components(registration)
    triggered_falsifications = sorted({
        component
        for row in treatment
        for component in fatal_components
        if row.get("score_components", {}).get(component) == 0
    })

    threshold = float(registration["measurement"]["minimum_material_effect"])
    comparative_verdict = "insufficient_evidence"
    if ci is not None:
        if ci["lower"] > threshold:
            comparative_verdict = "beneficial"
        elif ci["upper"] < -threshold:
            comparative_verdict = "harmful"
        elif ci["lower"] >= -threshold and ci["upper"] <= threshold:
            comparative_verdict = "no_material_effect"
        else:
            reasons.append("confidence interval crosses a material-effect boundary")
    if triggered_falsifications:
        comparative_verdict = "harmful"
        reasons.append("registered scorecard falsification triggered")

    verdict = comparative_verdict
    registered_result: str | None = None
    registered_closure_outcome: str | None = None
    if t005_contract:
        threshold_result = _registered_threshold_result(registration, treatment_mean)
        if comparative_verdict == "harmful" or (
            comparative_verdict != "insufficient_evidence"
            and threshold_result == "harm_or_falsification"
        ):
            registered_result = "harm_or_falsification"
        elif comparative_verdict == "beneficial" and threshold_result == "success":
            registered_result = "success"
        else:
            registered_result = "inconclusive"

        if comparative_verdict == "beneficial" and registered_result != "success":
            verdict = "insufficient_evidence"
            if threshold_result == "harm_or_falsification":
                reasons.append("registered harm_or_falsification threshold reached")
            else:
                reasons.append("registered success threshold not met")
        registered_closure_outcome = registration["closure"]["outcome_by_result"][registered_result]

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
        "operational_cost": {
            "metric": registration["measurement"]["cost_metric"]["id"],
            "unit": registration["measurement"]["cost_metric"]["unit"],
            "control_mean": _round(control_effort_mean),
            "treatment_mean": _round(treatment_effort_mean),
            "raw_difference": _round(effort_difference),
        },
        "data_quality": {
            "comparable": comparable,
            "minimum_sample_met": minimum_sample_met,
            "independence_met": independence_met,
            "blinding_met": blinding_met,
            "reasons": reasons,
        },
        "registered_falsification": {
            "triggered": bool(triggered_falsifications),
            "components": triggered_falsifications,
        },
        "effect_claim_allowed": verdict != "insufficient_evidence" and not triggered_falsifications,
        "verdict": verdict,
        "does_not_establish": [
            "causal_generality_beyond_registered_conditions",
            "automatic_policy_change",
            "automatic_routing_change",
            "automatic_bureau_task_creation",
            "automatic_registered_closure_application",
            "caller_supplied_independence_correctness",
            "caller_supplied_scorecard_judgment_correctness",
            "cost_effectiveness_or_acceptable_ceremony",
            "caller_supplied_effort_measurement_correctness",
            "caller_supplied_blinding_correctness",
            "caller_supplied_evidence_digest_correctness",
        ],
    }
    if registered_result is not None:
        result["registered_result"] = registered_result
        result["registered_closure_outcome"] = registered_closure_outcome
    result["result_sha256"] = result_sha256(result)
    validate_schema(result, repo_root / "schemas/effect-evaluation.result.v1.schema.json")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", required=True, type=Path)
    parser.add_argument("--observations", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = evaluate(
        load_object(args.registration),
        load_object(args.observations),
        registration_path=args.registration,
    )
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
