#!/usr/bin/env python3
"""
Audit-Skript: Inkonsistenz zwischen execution_status und evidence.jsonl.

Prüft alle experiments/*/manifest.yml gegen den tatsächlichen Dateizustand.
"""
import json
import sys
from pathlib import Path

import yaml


def count_jsonl_lines(path: Path) -> int:
    """Zählt nicht-leere Zeilen in einer JSONL-Datei."""
    if not path.exists():
        return -1  # -1 = Datei fehlt
    count = 0
    with open(path) as f:
        for line in f:
            if line.strip():
                count += 1
    return count


def audit_experiment(exp_dir: Path) -> dict:
    manifest_path = exp_dir / "manifest.yml"
    evidence_path = exp_dir / "results" / "evidence.jsonl"

    if not manifest_path.exists():
        return {
            "experiment": exp_dir.name,
            "error": "manifest.yml fehlt",
            "inconsistencies": [],
        }

    with open(manifest_path) as f:
        manifest = yaml.safe_load(f)

    exp = manifest.get("experiment", {})
    execution_status = exp.get("execution_status")  # None wenn Feld fehlt
    execution_refs = exp.get("execution_refs", [])
    status = exp.get("status", "unknown")
    evidence_count = count_jsonl_lines(evidence_path)

    inconsistencies = []

    # Regel 1: execution_status fehlt, aber evidence existiert
    if execution_status is None and evidence_count > 0:
        inconsistencies.append(
            f"execution_status fehlt, aber {evidence_count} Evidenzeinträge vorhanden"
        )

    # Regel 2: execution_status=executed, aber keine Evidenz
    if execution_status in ("executed", "replicated") and evidence_count <= 0:
        label = "fehlt" if evidence_count == -1 else "leer"
        inconsistencies.append(
            f"execution_status={execution_status}, aber evidence.jsonl {label}"
        )

    # Regel 3: execution_status=designed/prepared, aber Evidenz vorhanden
    if execution_status in ("designed", "prepared") and evidence_count > 0:
        inconsistencies.append(
            f"execution_status={execution_status}, aber {evidence_count} Evidenzeinträge vorhanden"
        )

    # Regel 4: execution_status=executed, aber execution_refs leer
    if execution_status in ("executed", "replicated") and not execution_refs:
        inconsistencies.append(
            f"execution_status={execution_status}, aber execution_refs ist leer (Schema-Anforderung verletzt)"
        )

    return {
        "experiment": exp_dir.name,
        "status": status,
        "execution_status": execution_status,
        "execution_refs_count": len(execution_refs),
        "evidence_count": evidence_count,
        "inconsistencies": inconsistencies,
    }


def main():
    experiments_dir = Path(__file__).parent.parent.parent
    results = []

    for exp_dir in sorted(experiments_dir.iterdir()):
        if exp_dir.name.startswith("_") or not exp_dir.is_dir():
            continue
        # Dieses Experiment selbst überspringen (noch in Durchführung)
        if exp_dir.name == "2026-04-13_manifest-audit":
            continue
        results.append(audit_experiment(exp_dir))

    print("=== Manifest-Audit ===\n")
    print(f"Geprüfte Experimente: {len(results)}\n")

    for r in results:
        marker = "!" if r["inconsistencies"] else "."
        print(f"[{marker}] {r['experiment']}")
        print(f"     status={r.get('status','?')}  "
              f"execution_status={r.get('execution_status','(fehlt)')}  "
              f"evidence_count={r.get('evidence_count','?')}  "
              f"refs={r.get('execution_refs_count','?')}")
        for inc in r["inconsistencies"]:
            print(f"     >> {inc}")

    all_inconsistencies = [i for r in results for i in r["inconsistencies"]]
    errors = [r for r in results if "error" in r]

    print(f"\n--- Zusammenfassung ---")
    print(f"Experimente:        {len(results)}")
    print(f"Inkonsistenzen:     {len(all_inconsistencies)}")
    print(f"Fehler (kein yaml): {len(errors)}")

    return 0 if not all_inconsistencies else 1


if __name__ == "__main__":
    sys.exit(main())
