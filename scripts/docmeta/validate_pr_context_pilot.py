#!/usr/bin/env python3
"""Validate the frozen B-vs-D PR-context pilot contract.

The validator distinguishes structural validity from execution readiness.
A prepared-but-blocked pilot is valid by default. ``--require-ready`` turns the
open bindings into a non-zero exit so an operator can use the same contract as
an execution preflight.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT_REL = Path("experiments/2026-06-10_pr-agent-context-comparison-series")
DEFAULT_PILOT = REPO_ROOT / EXPERIMENT_REL / "pilot-v1.yml"
EXPECTED_CONDITIONS = {"B", "D"}
EXPECTED_TASK_CLASSES = {
    "documentation_policy",
    "validator_test",
    "implementation_ci",
}
EXPECTED_METRICS = {
    "scope_drift_count",
    "unsupported_claim_count",
    "missing_locator_count",
    "validation_gap_count",
    "review_friction_count",
    "rework_count",
    "false_block_count",
    "task_completion_time_observed",
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("pilot artifact must be a YAML object")
    return data


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _resolve_inside(base: Path, raw_path: object) -> Path | None:
    if not isinstance(raw_path, str) or not raw_path:
        return None
    candidate = (base / raw_path).resolve()
    try:
        candidate.relative_to(base.resolve())
    except ValueError:
        return None
    return candidate


def _derived_blockers(data: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    pairing = data.get("pairing")
    pairs = pairing.get("pairs", []) if isinstance(pairing, dict) else []
    task_refs_missing = False
    task_refs: list[str] = []
    for pair in pairs if isinstance(pairs, list) else []:
        if not isinstance(pair, dict):
            task_refs_missing = True
            continue
        refs = pair.get("task_refs")
        if not isinstance(refs, list) or len(refs) != 2 or any(
            not isinstance(ref, str) or not ref.strip() for ref in refs
        ):
            task_refs_missing = True
            continue
        task_refs.extend(ref.strip() for ref in refs)
    if task_refs_missing:
        blockers.append("tasks_not_bound")
    elif len(task_refs) != len(set(task_refs)):
        blockers.append("task_refs_not_unique")

    role_names = ("executor", "reviewer", "auditor")
    roles = data.get("role_bindings")
    if not isinstance(roles, dict) or any(
        not isinstance(roles.get(role), str) or not roles.get(role, "").strip()
        for role in role_names
    ):
        blockers.append("role_bindings_missing")
    else:
        role_bindings = [roles[role].strip() for role in role_names]
        if len(role_bindings) != len(set(role_bindings)):
            blockers.append("role_bindings_not_distinct")
    return blockers


def validate_pilot(
    pilot_path: Path = DEFAULT_PILOT,
    *,
    repo_root: Path = REPO_ROOT,
) -> tuple[list[str], list[str], dict[str, Any]]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        data = _load_yaml(pilot_path)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        return [f"cannot load pilot artifact: {exc}"], warnings, {}

    experiment_dir = pilot_path.parent
    if data.get("schema_version") != "1.0.0":
        errors.append("schema_version must equal '1.0.0'")
    if data.get("contract") != "pr_context_comparison_pilot":
        errors.append("contract must equal 'pr_context_comparison_pilot'")
    if data.get("status") not in {"prepared", "running", "completed", "stopped"}:
        errors.append("status must be prepared, running, completed, or stopped")
    if not isinstance(data.get("triggered_by"), str) or not data["triggered_by"].strip():
        errors.append("triggered_by must be a non-empty string")

    conditions = data.get("conditions")
    if not isinstance(conditions, dict):
        errors.append("conditions must be an object")
    elif set(conditions) != EXPECTED_CONDITIONS:
        errors.append("conditions must contain exactly B and D")
    else:
        for condition_id in sorted(EXPECTED_CONDITIONS):
            condition = conditions[condition_id]
            if not isinstance(condition, dict):
                errors.append(f"conditions.{condition_id} must be an object")
                continue
            target = _resolve_inside(experiment_dir, condition.get("path"))
            if target is None:
                errors.append(
                    f"conditions.{condition_id}.path must resolve inside the experiment"
                )
                continue
            if not target.is_file():
                errors.append(f"conditions.{condition_id}.path does not exist: {target}")
                continue
            declared_hash = condition.get("sha256")
            if not isinstance(declared_hash, str) or not SHA256_RE.fullmatch(declared_hash):
                errors.append(f"conditions.{condition_id}.sha256 must be lowercase SHA-256")
            elif _sha256(target) != declared_hash:
                errors.append(f"conditions.{condition_id}.sha256 does not match frozen bytes")

    pairing = data.get("pairing")
    if not isinstance(pairing, dict):
        errors.append("pairing must be an object")
    else:
        if pairing.get("strategy") != "blocked_randomization":
            errors.append("pairing.strategy must equal 'blocked_randomization'")
        pairs = pairing.get("pairs")
        if pairing.get("pair_count") != 3:
            errors.append("pairing.pair_count must equal 3")
        if not isinstance(pairs, list) or len(pairs) != 3:
            errors.append("pairing.pairs must contain exactly three pairs")
        else:
            pair_ids: set[str] = set()
            task_classes: set[str] = set()
            for index, pair in enumerate(pairs, start=1):
                prefix = f"pairing.pairs[{index - 1}]"
                if not isinstance(pair, dict):
                    errors.append(f"{prefix} must be an object")
                    continue
                pair_id = pair.get("pair_id")
                if not isinstance(pair_id, str) or not pair_id:
                    errors.append(f"{prefix}.pair_id must be non-empty")
                elif pair_id in pair_ids:
                    errors.append(f"duplicate pair_id: {pair_id}")
                else:
                    pair_ids.add(pair_id)
                task_class = pair.get("task_class")
                if task_class not in EXPECTED_TASK_CLASSES:
                    errors.append(f"{prefix}.task_class is not an expected pilot class")
                else:
                    task_classes.add(task_class)
                order = pair.get("assignment_order")
                if not isinstance(order, list) or len(order) != 2 or set(order) != EXPECTED_CONDITIONS:
                    errors.append(f"{prefix}.assignment_order must contain B and D exactly once")
                refs = pair.get("task_refs")
                if not isinstance(refs, list) or len(refs) != 2:
                    errors.append(f"{prefix}.task_refs must contain two slots")
            if task_classes != EXPECTED_TASK_CLASSES:
                errors.append("pilot must cover documentation_policy, validator_test, and implementation_ci")

    metrics = data.get("required_metrics")
    if not isinstance(metrics, list) or set(metrics) != EXPECTED_METRICS or len(metrics) != len(EXPECTED_METRICS):
        errors.append("required_metrics must contain the eight canonical metrics exactly once")

    stop_rules = data.get("stop_rules")
    if not isinstance(stop_rules, list) or len(stop_rules) < 3 or any(
        not isinstance(item, str) or not item.strip() for item in stop_rules
    ):
        errors.append("stop_rules must contain at least three non-empty rules")

    declared_blockers = data.get("blockers")
    derived_blockers = _derived_blockers(data)
    if not isinstance(declared_blockers, list) or any(
        not isinstance(item, str) or not item for item in declared_blockers
    ):
        errors.append("blockers must be a list of non-empty strings")
        declared_blockers = []
    if sorted(declared_blockers) != sorted(derived_blockers):
        errors.append(
            "blockers must equal the blockers derived from task and role bindings "
            f"(expected {derived_blockers!r})"
        )

    execution_allowed = data.get("execution_allowed")
    if not isinstance(execution_allowed, bool):
        errors.append("execution_allowed must be boolean")
    elif execution_allowed != (not derived_blockers):
        errors.append("execution_allowed must be true exactly when no derived blockers remain")

    if derived_blockers and not errors:
        warnings.append("pilot is structurally valid but execution-blocked: " + ", ".join(derived_blockers))

    try:
        pilot_path.resolve().relative_to(repo_root.resolve())
    except ValueError:
        errors.append("pilot artifact must remain inside the repository")

    return errors, warnings, data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", type=Path, default=DEFAULT_PILOT)
    parser.add_argument("--require-ready", action="store_true")
    parser.add_argument("--json", action="store_true", dest="emit_json")
    args = parser.parse_args(argv)

    errors, warnings, data = validate_pilot(args.pilot)
    ready = not errors and bool(data.get("execution_allowed"))
    payload = {
        "status": "error" if errors else ("ready" if ready else "blocked"),
        "pilot": str(args.pilot),
        "execution_allowed": ready,
        "errors": errors,
        "warnings": warnings,
    }
    if args.emit_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        for warning in warnings:
            print(f"⚠️  {warning}")
        for error in errors:
            print(f"❌ {error}")
        if not errors:
            state = "ready" if ready else "blocked"
            print(f"✅ PR-context pilot contract valid ({state}).")

    if errors:
        return 1
    if args.require_ready and not ready:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
