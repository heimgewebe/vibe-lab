#!/usr/bin/env python3
"""Create a deterministic cross-run closeout for the historical Operator-Lab series."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/2026-07-01_operator-lab-loop"
ARTIFACTS = EXPERIMENT / "artifacts"
OUTPUT = EXPERIMENT / "results/cross-run-assessment.v1.json"
COUNT_METRICS = (
    "scope_drift_count",
    "unsupported_claim_count",
    "missing_locator_count",
    "validation_gap_count",
    "review_friction_count",
    "rework_count",
    "false_block_count",
)


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def _load_card(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: run card must be a mapping")
    return value


def build_closeout(repo_root: Path = ROOT) -> dict[str, Any]:
    experiment = repo_root / "experiments/2026-07-01_operator-lab-loop"
    cards = sorted((experiment / "artifacts").glob("run-*/run-card.yml"))
    if not cards:
        raise ValueError("Operator-Lab has no run cards")

    metrics = Counter({name: 0 for name in COUNT_METRICS})
    conditions: Counter[str] = Counter()
    decisions: Counter[str] = Counter()
    changed_decision: Counter[str] = Counter()
    evidence_status: Counter[str] = Counter()
    claim_status: Counter[str] = Counter()
    missing_run_meta: list[str] = []
    missing_timing: list[str] = []
    input_records: list[dict[str, Any]] = []

    for path in cards:
        card = _load_card(path)
        rel = path.relative_to(repo_root).as_posix()
        run_dir = path.parent
        meta_path = run_dir / "run_meta.json"
        meta_exists = meta_path.is_file()
        if not meta_exists:
            missing_run_meta.append(run_dir.relative_to(repo_root).as_posix())

        conditions[str(card.get("condition", "<missing>"))] += 1
        decisions[str(card.get("decision", "<missing>"))] += 1
        probe = card.get("steuerboard_probe")
        changed = probe.get("changed_decision", "<missing>") if isinstance(probe, dict) else "<missing>"
        changed_decision[str(changed)] += 1

        card_metrics = card.get("metrics")
        if not isinstance(card_metrics, dict):
            raise ValueError(f"{rel}: metrics must be a mapping")
        for name in COUNT_METRICS:
            value = card_metrics.get(name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"{rel}: metrics.{name} must be a non-negative integer")
            metrics[name] += value
        if card_metrics.get("task_completion_time_observed") == "not_measured":
            missing_timing.append(run_dir.relative_to(repo_root).as_posix())

        for claim in card.get("claims") or []:
            if not isinstance(claim, dict):
                continue
            claim_status[str(claim.get("status", "<missing>"))] += 1
            for evidence in claim.get("evidence") or []:
                if isinstance(evidence, dict):
                    evidence_status[str(evidence.get("evidence_status", "<missing>"))] += 1

        input_records.append({
            "path": rel,
            "card": card,
            "run_meta_exists": meta_exists,
            "run_meta_sha256": hashlib.sha256(meta_path.read_bytes()).hexdigest() if meta_exists else None,
        })

    repeated_conditions = {
        key: count for key, count in sorted(conditions.items()) if count >= 2
    }
    # Repetition of a label is not comparability. All repeated labels span
    # heterogeneous operations or lack a prospectively bound primary metric.
    comparison_ready_groups: list[dict[str, Any]] = []

    report = {
        "schema_version": "operator-lab.cross-run-assessment.v1",
        "assessment_date": "2026-07-12",
        "experiment_id": "2026-07-01_operator-lab-loop",
        "input_sha256": hashlib.sha256(_canonical(input_records)).hexdigest(),
        "run_card_count": len(cards),
        "complete_run_meta_count": len(cards) - len(missing_run_meta),
        "missing_run_meta_count": len(missing_run_meta),
        "missing_run_meta": missing_run_meta,
        "task_completion_time_measured_count": len(cards) - len(missing_timing),
        "task_completion_time_not_measured_count": len(missing_timing),
        "metrics": dict(sorted(metrics.items())),
        "conditions": dict(sorted(conditions.items())),
        "repeated_condition_labels": repeated_conditions,
        "comparison_ready_groups": comparison_ready_groups,
        "decisions": dict(sorted(decisions.items())),
        "operator_decision_changed": dict(sorted(changed_decision.items())),
        "claim_status": dict(sorted(claim_status.items())),
        "evidence_status": dict(sorted(evidence_status.items())),
        "effect_claim_allowed": False,
        "verdict": "insufficient_evidence",
        "decision": "freeze_anecdotal_series_and_require_prospective_comparison",
        "rationale": [
            "The series contains many real observations but no prospectively bound control/treatment comparison.",
            "All run cards lack measured task completion time, preventing effort-effect evaluation.",
            "Seven run cards lack run_meta.json and are retained as incomplete rather than reconstructed.",
            "Repeated condition labels do not establish comparable task, risk, context, or primary metric.",
            "Aggregated counts describe friction but do not establish that the Operator-Lab process caused an improvement.",
        ],
        "does_not_establish": [
            "operator_lab_effectiveness",
            "condition_superiority",
            "causal_effect",
            "workflow_adoption_readiness",
            "automatic_bureau_task_creation",
        ],
        "next_action": "Use a new prospectively registered experiment for any future operator-process comparison.",
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    report = build_closeout()
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding="utf-8") != rendered:
            raise SystemExit("Operator-Lab closeout is stale; regenerate it")
    else:
        args.output.write_text(rendered, encoding="utf-8")
    print(json.dumps({"status": "valid", "verdict": report["verdict"], "run_card_count": report["run_card_count"], "input_sha256": report["input_sha256"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
