#!/usr/bin/env python3
"""Aggregate-only readiness audit for Grabowski routing-learning inputs.

The audit reads the task SQLite store and, when supplied, Agent Workspace manifests
strictly read-only. It emits aggregate coverage only: no raw argv, prompts,
transcripts, notes, recommendation ids, workspace ids, or private payload content.
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import sqlite3
from pathlib import Path
from typing import Any

MODEL_FLAGS = ("--model", "--model-v2", "--routing-model")


def _normalized_model_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.strip().casefold()).strip("-")


def _explicit_models(argv: list[Any]) -> list[str]:
    values: list[str] = []
    for index, raw in enumerate(argv):
        arg = str(raw)
        for flag in MODEL_FLAGS:
            if arg == flag and index + 1 < len(argv):
                candidate = str(argv[index + 1]).strip()
                if candidate and not candidate.startswith("--"):
                    values.append(_normalized_model_name(candidate))
                break
            prefix = flag + "="
            if arg.startswith(prefix):
                candidate = arg[len(prefix):].strip()
                if candidate:
                    values.append(_normalized_model_name(candidate))
                break
    return list(dict.fromkeys(value for value in values if value))


def _json_nonempty(raw: Any) -> tuple[bool, bool]:
    if raw in (None, ""):
        return False, True
    try:
        value = json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        return False, False
    return bool(value), True


def _workspace_route_coverage(root: Path | None, task_ids: set[str] | None = None) -> dict[str, Any]:
    empty = {
        "source": "Grabowski agent-workspace manifests",
        "source_available": False,
        "manifest_count": 0,
        "route_evidence_present": 0,
        "route_evidence_verified": 0,
        "route_evidence_missing_status": 0,
        "route_evidence_schema_versions": {},
        "verified_percent_of_manifests": 0.0,
        "route_manifests_with_task_references": 0,
        "verified_route_manifests_with_task_references": 0,
        "verified_route_manifests_with_matching_task_rows": 0,
        "verified_route_manifest_task_join_coverage_percent": 0.0,
        "task_reference_join_available": False,
        "usable_as_complete_training_label_without_shadow_capture": False,
    }
    if root is None or not root.is_dir():
        return empty

    manifests = sorted(root.glob("*/manifest.json"))
    versions: collections.Counter[str] = collections.Counter()
    present = 0
    verified = 0
    missing_status = 0
    invalid_json = 0
    route_with_task_refs = 0
    verified_with_task_refs = 0
    verified_with_matching_rows = 0
    known_task_ids = task_ids or set()
    for path in manifests:
        try:
            manifest = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            invalid_json += 1
            continue
        route = manifest.get("route_evidence")
        if not isinstance(route, dict):
            continue
        present += 1
        versions[str(route.get("schema_version"))] += 1
        referenced_task_ids: set[str] = set()
        tasks = manifest.get("tasks")
        if isinstance(tasks, dict):
            for task_value in tasks.values():
                if isinstance(task_value, str) and task_value:
                    referenced_task_ids.add(task_value)
                elif isinstance(task_value, dict):
                    for key in ("task_id", "id"):
                        value = task_value.get(key)
                        if isinstance(value, str) and value:
                            referenced_task_ids.add(value)
        if referenced_task_ids:
            route_with_task_refs += 1
        is_verified = route.get("status") == "verified" and route.get("evidence_complete") is True
        if is_verified:
            verified += 1
            if referenced_task_ids:
                verified_with_task_refs += 1
            if referenced_task_ids & known_task_ids:
                verified_with_matching_rows += 1
        elif route.get("status") == "missing":
            missing_status += 1

    return {
        "source": "Grabowski agent-workspace manifests",
        "source_available": True,
        "manifest_count": len(manifests),
        "manifest_invalid_json": invalid_json,
        "route_evidence_present": present,
        "route_evidence_verified": verified,
        "route_evidence_missing_status": missing_status,
        "route_evidence_schema_versions": dict(sorted(versions.items())),
        "verified_percent_of_manifests": round(100.0 * verified / len(manifests), 2) if manifests else 0.0,
        "route_manifests_with_task_references": route_with_task_refs,
        "verified_route_manifests_with_task_references": verified_with_task_refs,
        "verified_route_manifests_with_matching_task_rows": verified_with_matching_rows,
        "verified_route_manifest_task_join_coverage_percent": round(100.0 * verified_with_matching_rows / verified, 2) if verified else 0.0,
        "task_reference_join_available": verified_with_matching_rows > 0,
        "usable_as_complete_training_label_without_shadow_capture": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--agent-workspace-root")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    db_uri = f"file:{Path(args.db).resolve()}?mode=ro"
    conn = sqlite3.connect(db_uri, uri=True)
    columns = [row[1] for row in conn.execute("PRAGMA table_info(tasks)")]
    task_ids = {str(row[0]) for row in conn.execute("SELECT task_id FROM tasks") if row[0]}
    rows = conn.execute(
        "SELECT task_id, state, argv_json, acceptance_json, chronik_context_json, "
        "request_id, origin_ref, external_run_id, terminalization_sha256, "
        "lifecycle_receipt_sha256 FROM tasks"
    )

    states: collections.Counter[str] = collections.Counter()
    harnesses: collections.Counter[str] = collections.Counter()
    explicit_models: collections.Counter[str] = collections.Counter()
    chronik_keys: collections.Counter[str] = collections.Counter()
    task_count = 0
    counters = collections.Counter({
        "acceptance_invalid_json": 0,
        "acceptance_nonempty": 0,
        "argv_invalid_json": 0,
        "chronik_context_invalid_json": 0,
        "chronik_context_nonnull": 0,
        "explicit_model_argument_tasks": 0,
        "request_id_nonnull": 0,
        "origin_ref_nonnull": 0,
        "external_run_id_nonnull": 0,
        "terminalization_nonnull": 0,
        "lifecycle_receipt_nonnull": 0,
    })

    for task_id, state, argv_raw, acceptance_raw, chronik_raw, request_id, origin_ref, external_run_id, terminalization, lifecycle_receipt in rows:
        task_count += 1
        states[state] += 1
        try:
            argv = json.loads(argv_raw)
        except (TypeError, json.JSONDecodeError):
            argv = []
            counters["argv_invalid_json"] += int(bool(argv_raw))
        if isinstance(argv, list) and argv:
            harnesses[Path(str(argv[0])).name] += 1
            models = _explicit_models(argv)
            if models:
                counters["explicit_model_argument_tasks"] += 1
                explicit_models.update(models)

        acceptance_nonempty, acceptance_valid = _json_nonempty(acceptance_raw)
        counters["acceptance_nonempty"] += int(acceptance_nonempty)
        counters["acceptance_invalid_json"] += int(not acceptance_valid)

        if chronik_raw:
            counters["chronik_context_nonnull"] += 1
            try:
                obj = json.loads(chronik_raw)
            except (TypeError, json.JSONDecodeError):
                obj = None
                counters["chronik_context_invalid_json"] += 1
            if isinstance(obj, dict):
                chronik_keys.update(str(key) for key in obj.keys())
        counters["request_id_nonnull"] += int(bool(request_id))
        counters["origin_ref_nonnull"] += int(bool(origin_ref))
        counters["external_run_id_nonnull"] += int(bool(external_run_id))
        counters["terminalization_nonnull"] += int(bool(terminalization))
        counters["lifecycle_receipt_nonnull"] += int(bool(lifecycle_receipt))

    direct_semantic_columns = sorted(
        set(columns)
        & {"semantic_outcome", "reviewed_outcome", "task_correctness", "merge_quality", "decision_quality"}
    )
    direct_route_columns = sorted(
        set(columns)
        & {"route_id", "route_decision_id", "model_id", "harness_id", "routing_decision_sha256", "route_evidence", "route_evidence_v2"}
    )
    workspace_root = Path(args.agent_workspace_root).resolve() if args.agent_workspace_root else None
    canonical_route_coverage = _workspace_route_coverage(workspace_root, task_ids)
    report = {
        "schema_version": "operator-routing-ml-readiness-audit.v2",
        "sources": {
            "task_store": {
                "store": "Grabowski tasks SQLite",
                "mode": "read_only",
            },
            "agent_workspace_manifests": {
                "store": "Grabowski agent-workspace manifests",
                "mode": "read_only",
                "enabled": workspace_root is not None,
            },
            "raw_payload_exported": False,
        },
        "task_count": task_count,
        "state_counts": dict(sorted(states.items())),
        "structured_coverage": dict(sorted(counters.items())),
        "direct_semantic_outcome_columns": direct_semantic_columns,
        "direct_canonical_route_columns": direct_route_columns,
        "canonical_route_evidence_coverage": canonical_route_coverage,
        "direct_complete_route_plus_semantic_outcome_training_label_available": bool(direct_semantic_columns and direct_route_columns),
        "cross_source_complete_route_plus_semantic_outcome_training_label_available": False,
        "chronik_context_keys": dict(sorted(chronik_keys.items())),
        "diagnostic_only": {
            "top_argv_harnesses": harnesses.most_common(20),
            "explicit_model_argument_counts_normalized": explicit_models.most_common(30),
            "model_argument_flags_checked": list(MODEL_FLAGS),
            "warning": "argv-derived harness/model values are diagnostic only and are not canonical routing-decision evidence",
        },
        "interpretation": {
            "task_state_is_process_lifecycle_not_semantic_correctness": True,
            "task_store_has_direct_canonical_route_column": bool(direct_route_columns),
            "verified_workspace_route_evidence_exists": canonical_route_coverage["route_evidence_verified"] > 0,
            "workspace_route_evidence_has_partial_task_reference_join": canonical_route_coverage["task_reference_join_available"],
            "workspace_route_evidence_has_complete_task_join_coverage": canonical_route_coverage["verified_route_manifest_task_join_coverage_percent"] == 100.0,
            "ready_for_supervised_routing_training_from_current_sources_alone": False,
            "required_next_evidence": [
                "versioned shadow capture joining verified route_evidence to one eligible case identity",
                "independently reviewed semantic outcome or explicit abstention",
                "primary evidence references for every non-abstaining outcome",
                "prospective shadow cohort",
            ],
        },
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"task_count": task_count, "ready": False, "output": str(out)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
