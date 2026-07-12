#!/usr/bin/env python3
"""Validate the bounded active-experiment registry."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "experiments/active.v1.json"
SCHEMA = ROOT / "schemas/active-experiments.v1.schema.json"


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: root must be an object")
    return value


def _utc(value: str, label: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise ValueError(f"{label} must be UTC")
    return parsed.astimezone(timezone.utc)


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

        source_ref = (repo_root / item["source_ref"]).resolve()
        try:
            source_ref.relative_to(experiment_dir)
        except ValueError as exc:
            raise ValueError(f"{experiment_id}: source_ref must stay inside experiment directory") from exc
        if not source_ref.is_file():
            raise ValueError(f"{experiment_id}: source_ref is missing")

        review_at = _utc(item["review_at"], f"{experiment_id}.review_at")
        expires_at = _utc(item["expires_at"], f"{experiment_id}.expires_at")
        if review_at > expires_at:
            raise ValueError(f"{experiment_id}: review_at must not be after expires_at")
        if expires_at <= clock:
            raise ValueError(f"{experiment_id}: active experiment is expired")

        manifest_path = experiment_dir / "manifest.yml"
        if not manifest_path.is_file():
            raise ValueError(f"{experiment_id}: manifest.yml is missing")
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        status = (manifest or {}).get("experiment", {}).get("status")
        allowed = {"designed"} if item["state"] == "designed" else {"testing"}
        if status not in allowed:
            raise ValueError(
                f"{experiment_id}: active state {item['state']} conflicts with manifest status {status}"
            )
        checked.append(experiment_id)

    return {
        "status": "valid",
        "active_count": len(checked),
        "max_active": payload["max_active"],
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
