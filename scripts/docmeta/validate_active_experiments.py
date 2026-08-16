#!/usr/bin/env python3
"""Validate the bounded active-experiment registry and its source coherence."""
from __future__ import annotations

import argparse
import json
import re
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

from validate_experiment_registration import (
    V1_ENFORCEMENT_DATE,
    is_pre_t005_experiment,
    validate_registration,
)

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "experiments/active.v1.json"
SCHEMA = ROOT / "schemas/active-experiments.v1.schema.json"


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: root must be an object")
    return value


def _load_yaml_object(path: Path, label: str) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    return value


def _utc(value: str, label: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise ValueError(f"{label} must be UTC")
    return parsed.astimezone(timezone.utc)


def _experiment_date(experiment_id: str) -> date:
    try:
        return date.fromisoformat(experiment_id[:10])
    except ValueError as exc:
        raise ValueError(f"{experiment_id}: invalid experiment date prefix") from exc


def _registration_path(experiment_dir: Path) -> Path | None:
    for name in ("registration.v2.json", "registration.v1.json"):
        candidate = experiment_dir / name
        if candidate.is_file():
            return candidate
    return None


def _registration_review_at(registration: dict[str, Any]) -> str:
    if registration["schema_version"] == "experiment.registration.v2":
        return registration["review_at"]
    return registration["closure"]["review_at"]


def _registration_primary_metric(registration: dict[str, Any]) -> str:
    measurement = registration["measurement"]
    if registration["schema_version"] == "experiment.registration.v2":
        return measurement["primary_metric"]
    return measurement["metric"]


def _validate_registration_binding(
    *,
    item: dict[str, Any],
    experiment_dir: Path,
    clock: datetime,
) -> bool:
    experiment_id = item["experiment_id"]
    registration_path = _registration_path(experiment_dir)
    if registration_path is None:
        if (
            not is_pre_t005_experiment(experiment_id)
            or _experiment_date(experiment_id) >= V1_ENFORCEMENT_DATE
        ):
            raise ValueError(f"{experiment_id}: active experiment requires registration")
        return False

    registration = validate_registration(registration_path, now=clock)
    metric = _registration_primary_metric(registration)
    if item["primary_metric"] != metric:
        raise ValueError(
            f"{experiment_id}: active primary_metric conflicts with registration ({metric})"
        )

    registered_consumer = registration["consumer"]["organ"]
    if item["consumer"] != registered_consumer:
        raise ValueError(
            f"{experiment_id}: active consumer conflicts with registration ({registered_consumer})"
        )

    registered_question = registration["decision_target"]["question"]
    if item["decision_target"] != registered_question:
        raise ValueError(
            f"{experiment_id}: active decision_target conflicts with registration"
        )

    registered_review = _utc(
        _registration_review_at(registration),
        f"{experiment_id}.registration.review_at",
    )
    registered_expiry = _utc(
        registration["expires_at"],
        f"{experiment_id}.registration.expires_at",
    )
    active_review = _utc(item["review_at"], f"{experiment_id}.review_at")
    active_expiry = _utc(item["expires_at"], f"{experiment_id}.expires_at")
    if active_review != registered_review:
        raise ValueError(f"{experiment_id}: active review_at conflicts with registration")
    if active_expiry != registered_expiry:
        raise ValueError(f"{experiment_id}: active expires_at conflicts with registration")
    return True


def _validate_decision_binding(
    *,
    item: dict[str, Any],
    repo_root: Path,
    experiment_dir: Path,
) -> None:
    experiment_id = item["experiment_id"]
    source_ref_value = item["source_ref"]
    experiment_prefix = f"{item['path']}/"
    relative_ref = source_ref_value.removeprefix(experiment_prefix)
    if (
        relative_ref == source_ref_value
        or re.fullmatch(r"(?:results|p[0-9]+)/decision\.yml", relative_ref) is None
    ):
        raise ValueError(
            f"{experiment_id}: source_ref must be exactly results/decision.yml or "
            "pN/decision.yml within the experiment directory"
        )

    source_ref = (repo_root / source_ref_value).resolve()
    try:
        source_ref.relative_to(experiment_dir)
    except ValueError as exc:
        raise ValueError(f"{experiment_id}: source_ref must stay inside experiment directory") from exc
    if not source_ref.is_file():
        raise ValueError(f"{experiment_id}: source_ref is missing")

    decision = _load_yaml_object(source_ref, f"{experiment_id}.source_ref")
    verdict = decision.get("verdict")
    if not isinstance(verdict, str) or not verdict.strip():
        raise ValueError(f"{experiment_id}: source decision must contain a non-empty verdict")
    if item["state"] == "designed" and verdict != "not_executed":
        raise ValueError(
            f"{experiment_id}: designed active experiment must have verdict not_executed"
        )
    if item["state"] == "pilot":
        pilot_decision = decision.get("pilot_decision")
        if verdict != "pilot" and (
            not isinstance(pilot_decision, str) or not pilot_decision.strip()
        ):
            raise ValueError(
                f"{experiment_id}: pilot active experiment lacks a pilot decision signal"
            )


def validate_active_experiments(
    registry_path: Path = REGISTRY,
    *,
    repo_root: Path = ROOT,
    now: datetime | None = None,
) -> dict[str, Any]:
    payload = _load_json(registry_path)
    schema = _load_json(repo_root / "schemas/active-experiments.v1.schema.json")
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(payload)

    clock = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    ids: set[str] = set()
    paths: set[str] = set()
    checked: list[str] = []
    registration_bound = 0

    for item in payload["experiments"]:
        experiment_id = item["experiment_id"]
        path_value = item["path"]
        if experiment_id in ids:
            raise ValueError(f"duplicate active experiment_id: {experiment_id}")
        if path_value in paths:
            raise ValueError(f"duplicate active experiment path: {path_value}")
        ids.add(experiment_id)
        paths.add(path_value)

        experiment_dir = (repo_root / path_value).resolve()
        try:
            experiment_dir.relative_to(repo_root.resolve())
        except ValueError as exc:
            raise ValueError(f"{experiment_id}: path escapes repository") from exc
        if experiment_dir.name != experiment_id:
            raise ValueError(f"{experiment_id}: path basename must match experiment_id")
        if not experiment_dir.is_dir():
            raise ValueError(f"{experiment_id}: experiment directory is missing")

        review_at = _utc(item["review_at"], f"{experiment_id}.review_at")
        expires_at = _utc(item["expires_at"], f"{experiment_id}.expires_at")
        if review_at > expires_at:
            raise ValueError(f"{experiment_id}: review_at must not be after expires_at")
        if expires_at <= clock:
            raise ValueError(f"{experiment_id}: active experiment is expired")

        manifest_path = experiment_dir / "manifest.yml"
        if not manifest_path.is_file():
            raise ValueError(f"{experiment_id}: manifest.yml is missing")
        manifest = _load_yaml_object(manifest_path, f"{experiment_id}.manifest")
        status = manifest.get("experiment", {}).get("status")
        allowed = {"designed"} if item["state"] == "designed" else {"testing"}
        if status not in allowed:
            raise ValueError(
                f"{experiment_id}: active state {item['state']} conflicts with manifest status {status}"
            )

        _validate_decision_binding(
            item=item,
            repo_root=repo_root,
            experiment_dir=experiment_dir,
        )
        registration_bound += int(
            _validate_registration_binding(
                item=item,
                experiment_dir=experiment_dir,
                clock=clock,
            )
        )
        checked.append(experiment_id)

    return {
        "status": "valid",
        "active_count": len(checked),
        "max_active": payload["max_active"],
        "registration_bound_count": registration_bound,
        "grandfathered_count": len(checked) - registration_bound,
        "experiments": checked,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    parser.add_argument("--now")
    args = parser.parse_args()
    clock = _utc(args.now, "--now") if args.now else None
    print(json.dumps(validate_active_experiments(args.registry, now=clock), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
