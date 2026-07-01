#!/usr/bin/env python3
"""Stage timing and review evidence for the B-vs-D PR-context pilot."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/2026-06-10_pr-agent-context-comparison-series"
PILOT = EXPERIMENT / "pilot-v1.yml"
VALIDATOR = ROOT / "scripts/docmeta/validate_pr_context_pilot.py"
WORK = ROOT / ".tmp/pr-context-runs"
PHASES = ("preparation", "execution", "validation", "review", "rework")
RUN_ID = re.compile(r"^run-[a-z0-9][a-z0-9-]*$")
SHA = re.compile(r"^[0-9a-f]{7,64}$")


class CaptureError(RuntimeError):
    pass


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def yaml_object(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CaptureError(f"{path} must contain an object")
    return value


def pilot_repo_root(pilot_path: Path) -> Path:
    experiment_dir = pilot_path.resolve().parent
    if experiment_dir.name == EXPERIMENT.name and experiment_dir.parent.name == "experiments":
        return experiment_dir.parent.parent
    return ROOT


def validate_pilot_preflight(pilot_path: Path) -> dict[str, Any]:
    try:
        spec = importlib.util.spec_from_file_location(
            "validate_pr_context_pilot",
            VALIDATOR,
        )
        if spec is None or spec.loader is None:
            raise CaptureError("cannot load pilot validator")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        validator = getattr(module, "validate_pilot")
        errors, _warnings, pilot = validator(
            pilot_path,
            repo_root=pilot_repo_root(pilot_path),
        )
    except CaptureError:
        raise
    except Exception as exc:
        raise CaptureError(f"pilot validator preflight failed: {exc}") from exc

    if errors:
        raise CaptureError("pilot validator preflight failed: " + "; ".join(errors))
    if not isinstance(pilot, dict):
        raise CaptureError("pilot validator returned malformed data")
    if pilot.get("execution_allowed") is not True:
        raise CaptureError("pilot execution is blocked")
    return pilot


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def run_dir(root: Path, run_id: str) -> Path:
    if not RUN_ID.fullmatch(run_id):
        raise CaptureError("invalid run id")
    return root / run_id


def state(directory: Path) -> dict[str, Any]:
    path = directory / "collector-state.json"
    if not path.is_file():
        raise CaptureError("collector state missing")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CaptureError("collector state malformed")
    return value


def save(directory: Path, value: dict[str, Any]) -> None:
    value["updated_at"] = now()
    atomic_json(directory / "collector-state.json", value)


def prepare(run_id: str, pair_id: str, slot: int, executor: str, base_commit: str,
            *, pilot_path: Path = PILOT, work_root: Path = WORK) -> Path:
    if slot not in {1, 2} or not executor.strip() or not SHA.fullmatch(base_commit):
        raise CaptureError("invalid slot, executor, or base commit")
    pilot = validate_pilot_preflight(pilot_path)
    pair = next((item for item in pilot["pairing"]["pairs"]
                 if item.get("pair_id") == pair_id), None)
    if not isinstance(pair, dict):
        raise CaptureError("unknown pair")
    condition = pair["assignment_order"][slot - 1]
    task_ref = pair["task_refs"][slot - 1]
    if not isinstance(task_ref, str) or not task_ref.strip():
        raise CaptureError("task slot is not bound")
    spec = pilot["conditions"][condition]
    source = (pilot_path.parent / spec["path"]).resolve()
    try:
        source.relative_to(pilot_path.parent.resolve())
    except ValueError as exc:
        raise CaptureError("condition path escapes experiment") from exc
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if digest != spec["sha256"]:
        raise CaptureError("condition hash drift")
    directory = run_dir(work_root, run_id)
    if directory.exists():
        raise CaptureError("run already exists")
    directory.mkdir(parents=True)
    (directory / "condition-input.md").write_bytes(source.read_bytes())
    created = now()
    save(directory, {
        "run_id": run_id, "pair_id": pair_id, "slot": slot,
        "task_class": pair["task_class"], "task_ref": task_ref,
        "condition": condition, "condition_sha256": digest,
        "executor": executor.strip(), "base_commit": base_commit,
        "created_at": created, "active_phase": None,
        "phase_events": [], "status": "prepared",
    })
    return directory


def start(directory: Path, phase: str, *, clock: float | None = None) -> None:
    value = state(directory)
    if phase not in PHASES or value.get("active_phase") is not None:
        raise CaptureError("invalid or overlapping phase")
    value["active_phase"] = {
        "name": phase, "started_at": now(),
        "started_unix": time.time() if clock is None else clock,
    }
    value["status"] = "running"
    save(directory, value)


def stop(directory: Path, *, clock: float | None = None) -> dict[str, Any]:
    value = state(directory)
    active = value.get("active_phase")
    if not isinstance(active, dict):
        raise CaptureError("no active phase")
    finished = time.time() if clock is None else clock
    if finished < active["started_unix"]:
        raise CaptureError("clock moved backwards")
    event = {
        "name": active["name"], "started_at": active["started_at"],
        "finished_at": now(),
        "duration_seconds": round(finished - active["started_unix"], 6),
    }
    value["phase_events"].append(event)
    value["active_phase"] = None
    save(directory, value)
    return event


def review(directory: Path, pr_ref: str, rounds: int, commits: list[str]) -> Path:
    value = state(directory)
    if not pr_ref.strip() or rounds < 0 or len(commits) != len(set(commits)):
        raise CaptureError("invalid review evidence")
    if any(not SHA.fullmatch(commit) for commit in commits):
        raise CaptureError("invalid rework commit")
    artifact = {
        "schema_version": "1.0.0", "contract": "review_events",
        "run_id": value["run_id"], "pr_ref": pr_ref,
        "review_friction_count": rounds, "rework_count": len(commits),
        "captured_at": now(), "evidence_status": "repo_local",
        "notes": "Semantic review rounds and causal rework were classified explicitly.",
    }
    if commits:
        artifact["rework_commit_refs"] = commits
    path = directory / "review-events.yml"
    path.write_text(yaml.safe_dump(artifact, sort_keys=False), encoding="utf-8")
    return path


def finalize(directory: Path) -> dict[str, Any]:
    value = state(directory)
    if value.get("active_phase") is not None:
        raise CaptureError("active phase not stopped")
    events = value.get("phase_events", [])
    observed = {event.get("name") for event in events}
    missing = [phase for phase in PHASES if phase not in observed]
    if missing:
        raise CaptureError("missing phases: " + ", ".join(missing))
    required = ("agent-output.md", "review-events.yml")
    if any(not (directory / name).is_file() for name in required):
        raise CaptureError("required evidence missing")
    validation = (directory / "targeted-tests.txt").is_file() or (directory / "diagnostic-checks.txt").is_file()
    changes = (directory / "changed-files.txt").is_file() or (directory / "no-changes.txt").is_file()
    if not validation or not changes:
        raise CaptureError("validation or changed-file evidence missing")
    totals = {phase: 0.0 for phase in PHASES}
    for event in events:
        totals[event["name"]] += float(event["duration_seconds"])
    total = sum(totals.values())
    lines = [f"duration_seconds: {total:.6f}", 'capture_mode: "repo_local_phase_clock"', "phases:"]
    lines.extend(f"  {phase}_seconds: {totals[phase]:.6f}" for phase in PHASES)
    lines.extend(["limitation_note: >", "  Active captured intervals only; queue time is excluded."])
    (directory / "timing.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    review_data = yaml_object(directory / "review-events.yml")
    summary = {
        "run_id": value["run_id"], "condition": value["condition"],
        "task_completion_time_observed": total,
        "review_friction_count": review_data["review_friction_count"],
        "rework_count": review_data["rework_count"],
        "does_not_establish": ["condition superiority", "causal usefulness", "adoption readiness"],
    }
    atomic_json(directory / "collector-summary.json", summary)
    value["status"] = "finalized"
    save(directory, value)
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-root", type=Path, default=WORK)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare_parser = commands.add_parser("prepare")
    for name in ("run-id", "pair-id", "executor", "base-commit"):
        prepare_parser.add_argument(f"--{name}", required=True)
    prepare_parser.add_argument("--slot", type=int, choices=(1, 2), required=True)
    start_parser = commands.add_parser("start")
    start_parser.add_argument("--run-id", required=True)
    start_parser.add_argument("--phase", choices=PHASES, required=True)
    stop_parser = commands.add_parser("stop")
    stop_parser.add_argument("--run-id", required=True)
    review_parser = commands.add_parser("review")
    review_parser.add_argument("--run-id", required=True)
    review_parser.add_argument("--pr-ref", required=True)
    review_parser.add_argument("--rounds", type=int, required=True)
    review_parser.add_argument("--rework-commit", action="append", default=[])
    finish_parser = commands.add_parser("finalize")
    finish_parser.add_argument("--run-id", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "prepare":
            result: Any = prepare(args.run_id, args.pair_id, args.slot, args.executor, args.base_commit, work_root=args.work_root)
        else:
            directory = run_dir(args.work_root, args.run_id)
            if args.command == "start":
                start(directory, args.phase); result = {"started": args.phase}
            elif args.command == "stop":
                result = stop(directory)
            elif args.command == "review":
                result = review(directory, args.pr_ref, args.rounds, args.rework_commit)
            else:
                result = finalize(directory)
        print(result if isinstance(result, Path) else json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (CaptureError, OSError, ValueError, KeyError, json.JSONDecodeError, yaml.YAMLError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
