#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
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
PLACEHOLDER = "replace-with"
SCHEMAS = {
    "experiment.registration.v1": ROOT / "schemas/experiment.registration.v1.schema.json",
    "experiment.registration.v2": ROOT / "schemas/experiment.registration.v2.schema.json",
}


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

        consumer_organ = re.sub(r"[-_\s]+", "", payload["consumer"]["organ"]).casefold()
        if consumer_organ == "vibelab":
            raise ValueError(f"{path}: consumer must be external to Vibe-Lab")

        surface_budget = payload["surface_budget"]
        added = surface_budget["durable_units_added"]
        removed = surface_budget["durable_units_removed_or_replaced"]
        balance = surface_budget["balance"]
        if balance == "non_positive" and len(removed) < len(added):
            raise ValueError(
                f"{path}: non_positive surface budget requires at least as many "
                "removed or replaced durable units as added units"
            )
        if balance == "reviewed_exception":
            if len(removed) >= len(added):
                raise ValueError(
                    f"{path}: reviewed_exception is only valid for positive net "
                    "durable surface"
                )
            reviewed_at = _utc(
                surface_budget["exception"]["reviewed_at"],
                f"{path}.surface_budget.exception.reviewed_at",
            )
            if reviewed_at > clock:
                raise ValueError(
                    f"{path}: surface budget exception cannot be reviewed in the future"
                )

        scorecard = payload["measurement"].get("scorecard")
        if scorecard is not None:
            component_ids = [component["id"] for component in scorecard["components"]]
            if len(component_ids) != len(set(component_ids)):
                raise ValueError(f"{path}: scorecard component ids must be unique")
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
