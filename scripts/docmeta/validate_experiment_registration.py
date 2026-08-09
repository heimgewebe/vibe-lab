#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import re
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENTS = ROOT / "experiments"
V1_ENFORCEMENT_DATE = date(2026, 7, 10)
V2_ENFORCEMENT_DATE = date(2026, 7, 12)
DIR_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})_[a-z0-9][a-z0-9-]*$")
EXTERNAL_REF_RE = re.compile(r"^(?P<namespace>[a-z][a-z0-9+.-]*):\S+$")
PLACEHOLDER = "replace-with"
SELF_REFERENCES = frozenset({
    "internal",
    "self",
    "this experiment",
    "this repository",
    "vibe lab",
    "vibelab",
})
SELF_REFERENCE_PREFIXES = (
    "internal ",
    "self ",
    "this experiment ",
    "this repository ",
    "vibe lab ",
    "vibelab ",
)
VAGUE_EXTERNAL_NAMES = frozenset({
    "consumer",
    "current consumer",
    "external",
    "external consumer",
    "external team",
    "n/a",
    "none",
    "someone",
    "tbd",
    "team",
    "unknown",
})
# Closed compatibility set from the authorized T005 preimage at
# 6cc50a357ce75d49db3507390e08ec38c9901029. New work cannot obtain legacy
# treatment by backdating its directory. Historical registrations are not
# rewritten with prospective consumer or review claims.
PRE_T005_EXPERIMENTS = frozenset({
    "2026-04-08_spec-first",
    "2026-04-11_yolo-vs-spec-first",
    "2026-04-12_spec-first-legacy",
    "2026-04-14_incremental-debuggability",
    "2026-04-14_incremental-refinement",
    "2026-04-14_premortem-prompting",
    "2026-04-14_prompt-length-control",
    "2026-04-14_tdd-vibe",
    "2026-04-14_upfront-structuring",
    "2026-04-14_upfront-structuring-replication",
    "2026-04-15_agent-task-validity",
    "2026-04-19_generated-artifact-contract-validation",
    "2026-04-23_agent-failure-surface",
    "2026-04-23_phase-1-drift-injection",
    "2026-05-01_agent-skill-minimal-layer-instrumentation",
    "2026-05-25_outcome-evidence-replication-series",
    "2026-05-31_model-lab-replication-series",
    "2026-06-10_pr-agent-context-comparison-series",
    "2026-07-01_operator-lab-loop",
    "2026-07-05_ecosystem-organ-preflight",
    "2026-07-08_operator-learning-capture-sample",
    "2026-07-08_rlens-agent-context-conditions",
    "2026-07-09_repobrief-workbench-usefulness-eval",
    "2026-07-12_operator-intervention-effect-evaluator",
    "2026-07-13_chronik-history-brief-effect",
    "2026-07-23_operator-routing-ml-readiness-shadow",
})
SCHEMAS = {
    "experiment.registration.v1": ROOT / "schemas/experiment.registration.v1.schema.json",
    "experiment.registration.v2": ROOT / "schemas/experiment.registration.v2.schema.json",
}


def is_pre_t005_experiment(experiment_id: str) -> bool:
    return experiment_id in PRE_T005_EXPERIMENTS


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: root must be object")
    return value


def _utc(value: str, label: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise ValueError(f"{label} must be UTC")
    return parsed.astimezone(timezone.utc)


def _normalise_name(value: str) -> str:
    return re.sub(r"[\s_-]+", " ", value.strip().casefold())


def _is_self_or_vague_name(value: str) -> bool:
    normalised = _normalise_name(value)
    return (
        normalised in SELF_REFERENCES
        or normalised in VAGUE_EXTERNAL_NAMES
        or normalised.startswith(SELF_REFERENCE_PREFIXES)
    )


def _require_external_name(value: str, label: str) -> None:
    if _is_self_or_vague_name(value):
        raise ValueError(f"{label} must name an external consumer or decision owner")


def _require_external_ref(value: str, label: str) -> None:
    match = EXTERNAL_REF_RE.fullmatch(value)
    if match is None or _is_self_or_vague_name(match.group("namespace")):
        raise ValueError(f"{label} must be a namespaced external reference")


def _require_path(payload: dict[str, Any], keys: tuple[str, ...], path: Path) -> Any:
    current: Any = payload
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            raise ValueError(f"{path}: new experiment requires {'.'.join(keys)}")
        current = current[key]
    return current


def _validate_t005_contract(
    payload: dict[str, Any],
    *,
    path: Path,
    review: datetime,
    expires: datetime,
    clock: datetime,
) -> None:
    required_paths = (
        ("consumer", "relationship"),
        ("consumer", "commitment"),
        ("decision_target", "decision_ref"),
        ("measurement", "outcome_criteria"),
        ("closure", "outcome_by_result"),
        ("surface_budget",),
        ("boundary", "no_merge_authority"),
    )
    for keys in required_paths:
        _require_path(payload, keys, path)

    consumer = payload["consumer"]
    commitment = consumer["commitment"]
    _require_external_name(consumer["organ"], f"{path}.consumer.organ")
    _require_external_ref(
        commitment["evidence_ref"],
        f"{path}.consumer.commitment.evidence_ref",
    )
    confirmed_at = _utc(
        commitment["confirmed_at"],
        f"{path}.consumer.commitment.confirmed_at",
    )
    valid_until = _utc(
        commitment["valid_until"],
        f"{path}.consumer.commitment.valid_until",
    )
    if confirmed_at > clock:
        raise ValueError(f"{path}: consumer commitment cannot be confirmed in the future")
    if valid_until <= clock:
        raise ValueError(f"{path}: consumer commitment is not current")
    if valid_until < expires:
        raise ValueError(f"{path}: consumer commitment must remain current through expires_at")

    decision_target = payload["decision_target"]
    _require_external_name(
        decision_target["owner"],
        f"{path}.decision_target.owner",
    )
    _require_external_ref(
        decision_target["decision_ref"],
        f"{path}.decision_target.decision_ref",
    )

    measurement = payload["measurement"]
    criteria = measurement["outcome_criteria"]
    success = criteria["success_threshold"]
    harm = criteria["harm_or_falsification_threshold"]
    numeric_criteria = {
        "measurement.minimum_material_effect": measurement["minimum_material_effect"],
        "measurement.outcome_criteria.success_threshold": success,
        "measurement.outcome_criteria.harm_or_falsification_threshold": harm,
    }
    for label, value in numeric_criteria.items():
        if not math.isfinite(float(value)):
            raise ValueError(f"{path}.{label} must be finite")
    separated = success > harm if measurement["direction"] == "higher_is_better" else success < harm
    if not separated:
        raise ValueError(f"{path}: success and harm_or_falsification criteria must not overlap")

    surface_budget = payload["surface_budget"]
    added_units = len(surface_budget["durable_additions"])
    offset_units = len(surface_budget["durable_offsets"])
    offset_refs = [item.split(":", 1)[1] for item in surface_budget["durable_offsets"]]
    if len(offset_refs) != len(set(offset_refs)):
        raise ValueError(f"{path}: surface refs must be unique within each budget side")
    exception = surface_budget["reviewed_exception"]
    if added_units > offset_units and exception is None:
        raise ValueError(f"{path}: net durable surface cost requires a reviewed surface-budget exception")
    if exception is not None:
        _require_external_name(
            exception["reviewed_by"],
            f"{path}.surface_budget.reviewed_exception.reviewed_by",
        )
        _require_external_ref(
            exception["review_ref"],
            f"{path}.surface_budget.reviewed_exception.review_ref",
        )
        reviewed_at = _utc(
            exception["reviewed_at"],
            f"{path}.surface_budget.reviewed_exception.reviewed_at",
        )
        if reviewed_at > clock:
            raise ValueError(f"{path}: surface-budget exception review cannot be in the future")

    if review <= clock:
        raise ValueError(f"{path}: review_at must be in the future at registration")


def validate_registration(path: Path, *, now: datetime | None = None) -> dict[str, Any]:
    payload = _load(path)
    version = payload.get("schema_version")
    schema_path = SCHEMAS.get(str(version))
    if schema_path is None:
        raise ValueError(f"{path}: unsupported schema_version {version}")
    Draft202012Validator(_load(schema_path), format_checker=FormatChecker()).validate(payload)
    if PLACEHOLDER in json.dumps(payload, sort_keys=True):
        raise ValueError(f"{path}: unresolved template placeholder")

    experiment_dir = path.parent.name
    if payload["experiment_id"] != experiment_dir:
        raise ValueError(f"{path}: experiment_id must match directory name")
    if not is_pre_t005_experiment(experiment_dir) and (
        version != "experiment.registration.v2" or path.name != "registration.v2.json"
    ):
        raise ValueError(f"{path.parent}: new experiment requires registration.v2.json")
    expected_archive = f"experiments/_archive/{experiment_dir}"
    if payload["closure"]["archive_path"] != expected_archive:
        raise ValueError(f"{path}: archive_path must equal {expected_archive}")

    review_key = "review_at" if version == "experiment.registration.v2" else None
    review_value = payload[review_key] if review_key else payload["closure"]["review_at"]
    review = _utc(review_value, f"{path}.review_at")
    expires = _utc(payload["expires_at"], f"{path}.expires_at")
    clock = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    if expires <= clock:
        raise ValueError(f"{path}: registration already expired")
    if review > expires:
        raise ValueError(f"{path}: review_at must not be after expires_at")

    if version == "experiment.registration.v2":
        if payload["control_condition"]["id"] == payload["treatment_condition"]["id"]:
            raise ValueError(f"{path}: control and treatment ids must differ")
        if payload["decision_target"]["owner"] == "":
            raise ValueError(f"{path}: decision owner must be named")
        scorecard = payload["measurement"].get("scorecard")
        if scorecard is not None:
            component_ids = [component["id"] for component in scorecard["components"]]
            if len(component_ids) != len(set(component_ids)):
                raise ValueError(f"{path}: scorecard component ids must be unique")
        if not is_pre_t005_experiment(experiment_dir):
            _validate_t005_contract(
                payload,
                path=path,
                review=review,
                expires=expires,
                clock=clock,
            )
    return payload


def validate_all(*, now: datetime | None = None) -> dict[str, Any]:
    checked_v1 = 0
    checked_v2 = 0
    grandfathered = 0
    for directory in sorted(path for path in EXPERIMENTS.iterdir() if path.is_dir() and not path.name.startswith("_")):
        match = DIR_RE.fullmatch(directory.name)
        if not match:
            raise ValueError(f"{directory}: experiment directory name is not date-prefixed")
        created = date.fromisoformat(match.group(1))
        v1 = directory / "registration.v1.json"
        v2 = directory / "registration.v2.json"
        if not is_pre_t005_experiment(directory.name):
            if not v2.is_file():
                raise ValueError(f"{directory}: new experiment requires registration.v2.json")
            validate_registration(v2, now=now)
            checked_v2 += 1
            continue
        if created < V1_ENFORCEMENT_DATE:
            grandfathered += 1
            candidate = v2 if v2.exists() else v1 if v1.exists() else None
            if candidate:
                payload = validate_registration(candidate, now=now)
                checked_v2 += payload["schema_version"].endswith("v2")
                checked_v1 += payload["schema_version"].endswith("v1")
            continue
        if created >= V2_ENFORCEMENT_DATE:
            if not v2.is_file():
                raise ValueError(f"{directory}: new experiment requires registration.v2.json")
            validate_registration(v2, now=now)
            checked_v2 += 1
            continue
        candidate = v2 if v2.is_file() else v1
        if not candidate.is_file():
            raise ValueError(f"{directory}: experiment requires registration.v1.json or registration.v2.json")
        payload = validate_registration(candidate, now=now)
        checked_v2 += payload["schema_version"].endswith("v2")
        checked_v1 += payload["schema_version"].endswith("v1")
    return {
        "status": "valid",
        "checked_v1": checked_v1,
        "checked_v2": checked_v2,
        "grandfathered": grandfathered,
        "v1_enforcement_date": V1_ENFORCEMENT_DATE.isoformat(),
        "v2_enforcement_date": V2_ENFORCEMENT_DATE.isoformat(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", type=Path)
    args = parser.parse_args()
    result = validate_registration(args.path.resolve()) if args.path else validate_all()
    print(json.dumps(result if args.path is None else {"status": "valid", "experiment_id": result["experiment_id"], "schema_version": result["schema_version"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
