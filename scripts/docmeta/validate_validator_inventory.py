#!/usr/bin/env python3
"""Validate Vibe-Lab validator classification and CI group coverage."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
import yaml

ROOT = Path(__file__).resolve().parents[2]
INVENTORY = ROOT / ".vibe/validator-inventory.v1.json"
SCHEMA = ROOT / "schemas/validator-inventory.v1.schema.json"
MAKEFILE = ROOT / "Makefile"
WORKFLOW = ROOT / ".github/workflows/validate.yml"

_AGGREGATES = {"validate-core", "validate-active", "validate-legacy"}
_ALIASES = {"validate-ratchet"}
_REQUIRED_WORKFLOW_COMMANDS = (
    "make validate-core",
    "make validate-active",
    "make validate-legacy",
    "make validate-replay-mutation-guard",
    "make generate-blocking",
)


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: root must be an object")
    return value


def _parse_make_targets(text: str) -> dict[str, list[str]]:
    targets: dict[str, list[str]] = {}
    for raw in text.splitlines():
        if raw.startswith(("\t", " ")) or ":" not in raw:
            continue
        match = re.fullmatch(r"([A-Za-z0-9_.-]+):(?:\s+(.*))?", raw)
        if not match:
            continue
        name = match.group(1)
        deps = match.group(2).split() if match.group(2) else []
        targets[name] = deps
    return targets


def _validate_workflow(text: str) -> int:
    value = yaml.safe_load(text)
    try:
        steps = value["jobs"]["validate"]["steps"]
    except (KeyError, TypeError) as exc:
        raise ValueError("workflow must define jobs.validate.steps") from exc
    if not isinstance(steps, list):
        raise ValueError("jobs.validate.steps must be a list")

    executable_lines: list[str] = []
    for step in steps:
        if not isinstance(step, dict):
            raise ValueError("validate workflow step must be a mapping")
        run = step.get("run")
        if isinstance(run, str):
            executable_lines.extend(line.strip() for line in run.splitlines() if line.strip())

    for command in _REQUIRED_WORKFLOW_COMMANDS:
        if executable_lines.count(command) != 1:
            raise ValueError(f"validate workflow must contain exactly one executable `{command}`")
    forbidden_prefixes = (
        "python3 scripts/docmeta/validate_",
        "python3 scripts/adoption/validate_",
        "python3 scripts/exports/validate_",
    )
    for command in executable_lines:
        if command == "make validate" or command.startswith(forbidden_prefixes):
            raise ValueError(f"validate workflow bypasses grouped frontdoor via `{command}`")
    return sum(isinstance(step, dict) and isinstance(step.get("name"), str) for step in steps)


def validate_validator_inventory(
    *,
    repo_root: Path = ROOT,
    inventory_path: Path | None = None,
) -> dict[str, Any]:
    inventory_file = inventory_path or repo_root / ".vibe/validator-inventory.v1.json"
    inventory = _load_json(inventory_file)
    schema = _load_json(repo_root / "schemas/validator-inventory.v1.schema.json")
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(inventory)

    groups = {item["id"]: item for item in inventory["groups"]}
    if set(groups) != {"core", "active", "legacy"}:
        raise ValueError("validator groups must be exactly core, active and legacy")
    if len(groups["active"]["targets"]) > inventory["policy"]["max_active_specialist_targets"]:
        raise ValueError("active specialist target budget exceeded")
    declared_count = sum(len(group["targets"]) for group in groups.values())
    if declared_count != inventory["policy"]["classified_target_count"]:
        raise ValueError("classified target count differs from inventory policy")
    if "review_at" not in groups["legacy"] or "retirement_rule" not in groups["legacy"]:
        raise ValueError("legacy group requires review_at and retirement_rule")

    all_group_targets = [target for group in groups.values() for target in group["targets"]]
    if len(all_group_targets) != len(set(all_group_targets)):
        raise ValueError("validator target appears in more than one group")
    supplemental = [item["target"] for item in inventory["supplemental_checks"]]
    if len(supplemental) != len(set(supplemental)):
        raise ValueError("supplemental target is duplicated")
    if set(all_group_targets) & set(supplemental):
        raise ValueError("supplemental target must not also be a grouped target")

    make_text = (repo_root / "Makefile").read_text(encoding="utf-8")
    make_targets = _parse_make_targets(make_text)
    if make_targets.get("validate") != ["validate-core", "validate-active", "validate-legacy"]:
        raise ValueError("validate frontdoor must depend only on core, active and legacy groups")
    for group_id in ("core", "active", "legacy"):
        declared = make_targets.get(f"validate-{group_id}")
        if declared != groups[group_id]["targets"]:
            raise ValueError(f"Makefile validate-{group_id} dependencies differ from inventory")

    classified = set(all_group_targets)
    supplemental_set = set(supplemental)
    declared_validation = {
        name
        for name in make_targets
        if (name.startswith("validate-") or name == "agent-check-tests")
        and name not in _AGGREGATES
        and name not in _ALIASES
    }
    expected = classified | supplemental_set
    missing = sorted(declared_validation - expected)
    stale = sorted(expected - set(make_targets))
    if missing:
        raise ValueError(f"unclassified validation targets: {', '.join(missing)}")
    if stale:
        raise ValueError(f"inventory references missing Makefile targets: {', '.join(stale)}")

    for group in groups.values():
        for raw_path in group["scope_paths"]:
            if not (repo_root / raw_path).exists():
                raise ValueError(f"{group['id']} scope path is missing: {raw_path}")

    workflow_steps = _validate_workflow(
        (repo_root / ".github/workflows/validate.yml").read_text(encoding="utf-8")
    )
    if workflow_steps > inventory["policy"]["max_validate_job_named_steps"]:
        raise ValueError("validate workflow named-step budget exceeded")
    return {
        "status": "valid",
        "group_counts": {key: len(groups[key]["targets"]) for key in ("core", "active", "legacy")},
        "grouped_target_count": len(all_group_targets),
        "supplemental_target_count": len(supplemental),
        "validate_job_named_steps": workflow_steps,
        "historical_evidence_retained": inventory["policy"]["historical_evidence_retained"],
    }


def main() -> int:
    print(json.dumps(validate_validator_inventory(), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
