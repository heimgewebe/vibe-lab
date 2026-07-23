#!/usr/bin/env python3
"""Aggregate-only readiness audit for the Grabowski task store.

This experiment-local tool opens SQLite read-only and emits no raw argv,
prompt, transcript, note, or private payload content.
"""
from __future__ import annotations

import argparse
import collections
import json
import sqlite3
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    db_uri = f"file:{Path(args.db).resolve()}?mode=ro"
    conn = sqlite3.connect(db_uri, uri=True)
    columns = [row[1] for row in conn.execute("PRAGMA table_info(tasks)")]
    rows = conn.execute(
        "SELECT state, argv_json, acceptance_json, chronik_context_json, "
        "request_id, origin_ref, external_run_id, terminalization_sha256, "
        "lifecycle_receipt_sha256 FROM tasks"
    ).fetchall()

    states: collections.Counter[str] = collections.Counter()
    harnesses: collections.Counter[str] = collections.Counter()
    explicit_models: collections.Counter[str] = collections.Counter()
    chronik_keys: collections.Counter[str] = collections.Counter()
    counters = collections.Counter({
        "acceptance_nonempty": 0,
        "chronik_context_nonnull": 0,
        "explicit_model_argument_tasks": 0,
        "request_id_nonnull": 0,
        "origin_ref_nonnull": 0,
        "external_run_id_nonnull": 0,
        "terminalization_nonnull": 0,
        "lifecycle_receipt_nonnull": 0,
    })

    for state, argv_raw, acceptance_raw, chronik_raw, request_id, origin_ref, external_run_id, terminalization, lifecycle_receipt in rows:
        states[state] += 1
        try:
            argv = json.loads(argv_raw)
        except (TypeError, json.JSONDecodeError):
            argv = []
        if isinstance(argv, list) and argv:
            harnesses[Path(str(argv[0])).name] += 1
            if "--model" in argv:
                idx = argv.index("--model")
                if idx + 1 < len(argv):
                    explicit_models[str(argv[idx + 1])] += 1
                    counters["explicit_model_argument_tasks"] += 1

        if acceptance_raw and acceptance_raw != "[]":
            counters["acceptance_nonempty"] += 1
        if chronik_raw:
            counters["chronik_context_nonnull"] += 1
            try:
                obj = json.loads(chronik_raw)
            except (TypeError, json.JSONDecodeError):
                obj = None
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
        & {"route_id", "route_decision_id", "model_id", "harness_id", "routing_decision_sha256"}
    )
    report = {
        "schema_version": "operator-routing-ml-readiness-audit.v1",
        "source": {
            "store": "Grabowski tasks SQLite",
            "mode": "read_only",
            "raw_payload_exported": False,
        },
        "task_count": len(rows),
        "state_counts": dict(sorted(states.items())),
        "structured_coverage": dict(sorted(counters.items())),
        "direct_semantic_outcome_columns": direct_semantic_columns,
        "direct_canonical_route_columns": direct_route_columns,
        "direct_complete_route_plus_semantic_outcome_training_label_available": bool(direct_semantic_columns and direct_route_columns),
        "chronik_context_keys": dict(sorted(chronik_keys.items())),
        "diagnostic_only": {
            "top_argv_harnesses": harnesses.most_common(20),
            "explicit_model_argument_counts": explicit_models.most_common(30),
            "warning": "argv-derived harness/model values are diagnostic only and are not canonical routing-decision evidence",
        },
        "interpretation": {
            "task_state_is_process_lifecycle_not_semantic_correctness": True,
            "ready_for_supervised_routing_training_from_task_store_alone": False,
            "required_next_evidence": [
                "canonical route identity",
                "independently reviewed semantic outcome",
                "primary evidence references",
                "prospective shadow cohort",
            ],
        },
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"task_count": len(rows), "ready": False, "output": str(out)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
