#!/usr/bin/env python3
"""Summarize and validate Operator-Lab run-card metrics.

This is intentionally narrower than a full run-card schema validator. It checks
the metrics that are useful for Operator-Lab trend reading and catches semantic
mismatches around skipped Steuerboard probes changing decisions.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_REL = Path("experiments/2026-07-01_operator-lab-loop/artifacts")

COUNT_METRICS = (
    "scope_drift_count",
    "unsupported_claim_count",
    "missing_locator_count",
    "validation_gap_count",
    "review_friction_count",
    "rework_count",
    "false_block_count",
)
REQUIRED_METRICS = COUNT_METRICS + ("task_completion_time_observed",)


def _repo_rel(path: Path, *, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _run_cards(repo_root: Path) -> list[Path]:
    artifacts = repo_root / ARTIFACTS_REL
    return sorted(artifacts.glob("run-*/run-card.yml")) if artifacts.exists() else []


def _mentions_not_run(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    collapsed = re.sub(r"[^a-z0-9]+", "", value.casefold())
    return "notrun" in collapsed


def collect_operator_lab_metrics(repo_root: Path = ROOT) -> dict[str, Any]:
    totals = {name: 0 for name in COUNT_METRICS}
    task_completion_not_measured = 0
    errors: list[str] = []
    steering_mismatches: list[str] = []

    cards = _run_cards(repo_root)
    for card_path in cards:
        rel = _repo_rel(card_path, root=repo_root)
        card = _load_yaml(card_path)

        metrics = card.get("metrics")
        if not isinstance(metrics, dict):
            errors.append(f"{rel}: metrics must be a mapping with required fields")
            metrics = {}

        missing = [name for name in REQUIRED_METRICS if name not in metrics]
        if missing:
            errors.append(f"{rel}: metrics missing required fields: {', '.join(missing)}")

        for name in COUNT_METRICS:
            if name not in metrics:
                continue
            value = metrics[name]
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                errors.append(f"{rel}: metrics.{name} must be a non-negative integer")
                continue
            totals[name] += value

        if metrics.get("task_completion_time_observed") == "not_measured":
            task_completion_not_measured += 1

        probe = card.get("steuerboard_probe")
        if isinstance(probe, dict):
            useful_signal = probe.get("useful_signal")
            changed_decision = probe.get("changed_decision")
            if changed_decision is not None and changed_decision not in {"yes", "no"}:
                errors.append(
                    f"{rel}: steuerboard_probe.changed_decision must be yes or no"
                )
            if _mentions_not_run(useful_signal) and changed_decision == "yes":
                steering_mismatches.append(
                    f"{rel}: useful_signal records not_run but changed_decision is yes"
                )

    return {
        "run_card_count": len(cards),
        "metrics": totals,
        "task_completion_time_not_measured": task_completion_not_measured,
        "steering_mismatches": steering_mismatches,
        "errors": errors,
    }


def render_report(report: dict[str, Any]) -> str:
    lines = [
        "Operator-Lab metrics summary",
        f"run_card_count: {report['run_card_count']}",
    ]
    for name, value in report["metrics"].items():
        lines.append(f"{name}: {value}")
    lines.append(
        f"task_completion_time_not_measured: "
        f"{report['task_completion_time_not_measured']}"
    )
    if report["steering_mismatches"]:
        lines.append("")
        lines.append("Steuerboard metric mismatches:")
        lines.extend(f"  - {item}" for item in report["steering_mismatches"])
    if report["errors"]:
        lines.append("")
        lines.append("Metric shape errors:")
        lines.extend(f"  - {item}" for item in report["errors"])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    report = collect_operator_lab_metrics()
    if "--json" in argv:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(render_report(report))
    return 1 if report["errors"] or report["steering_mismatches"] else 0


if __name__ == "__main__":
    sys.exit(main())
