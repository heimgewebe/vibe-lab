from pathlib import Path
import json
import yaml
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

def load_jsonl(path: Path):
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows

def main():
    errors = []

    for manifest_path in (REPO_ROOT / "experiments").glob("*/manifest.yml"):
        if manifest_path.parent.name.startswith("_"):
            continue

        try:
            data = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
        except Exception as e:
            errors.append(f"{manifest_path.relative_to(REPO_ROOT)}: Invalid YAML - {e}")
            continue

        exp = data.get("experiment", {})
        execution_status = exp.get("execution_status")

        results_dir = manifest_path.parent / "results"
        decision_path = results_dir / "decision.yml"
        evidence_path = results_dir / "evidence.jsonl"

        if execution_status in {"executed", "replicated"}:
            if not evidence_path.exists():
                errors.append(f"{manifest_path.relative_to(REPO_ROOT)}: execution_status={execution_status} but no evidence.jsonl")
                continue

            try:
                rows = load_jsonl(evidence_path)
            except Exception as e:
                errors.append(f"{evidence_path.relative_to(REPO_ROOT)}: Invalid JSONL - {e}")
                continue

            run_events = [r for r in rows if r.get("event_type") == "run"]
            if not run_events:
                errors.append(f"{manifest_path.relative_to(REPO_ROOT)}: execution_status={execution_status} but no 'run' event found in evidence.jsonl")

            for i, r in enumerate(run_events):
                artifact_ref = r.get("artifact_ref")
                if not artifact_ref:
                    errors.append(f"{evidence_path.relative_to(REPO_ROOT)}: run event at index {i} missing artifact_ref")
                    continue
                artifact_path = manifest_path.parent / artifact_ref
                if not artifact_path.exists():
                    errors.append(f"{evidence_path.relative_to(REPO_ROOT)}: artifact_ref does not exist: {artifact_ref}")

        if decision_path.exists() and execution_status == "designed":
            errors.append(f"{manifest_path.relative_to(REPO_ROOT)}: decision.yml exists but execution_status is 'designed'")

    if errors:
        print("❌ Execution proof validation FAILED")
        for e in errors:
            print(" -", e)
        sys.exit(1)

    print("✅ Execution proof validation passed.")

if __name__ == "__main__":
    main()
