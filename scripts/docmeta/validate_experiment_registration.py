#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import date, datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "schemas/experiment.registration.v1.schema.json"
EXPERIMENTS = ROOT / "experiments"
ENFORCEMENT_DATE = date(2026, 7, 10)
DIR_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})_[a-z0-9][a-z0-9-]*$")
PLACEHOLDER = "replace-with"


def _load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: root must be object")
    return value


def validate_registration(path: Path, *, now: datetime | None = None) -> dict:
    payload = _load(path)
    schema = _load(SCHEMA)
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(payload)
    if PLACEHOLDER in json.dumps(payload, sort_keys=True):
        raise ValueError(f"{path}: unresolved template placeholder")
    experiment_dir = path.parent.name
    if payload["experiment_id"] != experiment_dir:
        raise ValueError(f"{path}: experiment_id must match directory name")
    expected_archive = f"experiments/_archive/{experiment_dir}"
    if payload["closure"]["archive_path"] != expected_archive:
        raise ValueError(f"{path}: archive_path must equal {expected_archive}")
    expires = datetime.fromisoformat(payload["expires_at"].replace("Z", "+00:00"))
    review = datetime.fromisoformat(payload["closure"]["review_at"].replace("Z", "+00:00"))
    clock = now or datetime.now(timezone.utc)
    if expires <= clock:
        raise ValueError(f"{path}: registration already expired")
    if review > expires:
        raise ValueError(f"{path}: review_at must not be after expires_at")
    return payload


def validate_all(*, now: datetime | None = None) -> dict:
    checked = 0
    grandfathered = 0
    for directory in sorted(path for path in EXPERIMENTS.iterdir() if path.is_dir() and not path.name.startswith("_")):
        match = DIR_RE.fullmatch(directory.name)
        if not match:
            raise ValueError(f"{directory}: experiment directory name is not date-prefixed")
        created = date.fromisoformat(match.group(1))
        registration = directory / "registration.v1.json"
        if created < ENFORCEMENT_DATE:
            grandfathered += 1
            if registration.exists():
                validate_registration(registration, now=now)
                checked += 1
            continue
        if not registration.is_file():
            raise ValueError(f"{directory}: new experiment requires registration.v1.json")
        validate_registration(registration, now=now)
        checked += 1
    return {"status": "valid", "checked": checked, "grandfathered": grandfathered, "enforcementDate": ENFORCEMENT_DATE.isoformat()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", type=Path)
    args = parser.parse_args()
    result = validate_registration(args.path.resolve()) if args.path else validate_all()
    print(json.dumps(result if args.path is None else {"status": "valid", "experiment_id": result["experiment_id"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
