#!/usr/bin/env python3
"""validate_outcome_evidence_replication_series.py — Gate validator for the
Outcome-Evidence-Replication-Series.

Reads all run artifacts under experiments/*/artifacts/run-*/ that belong to
the outcome-evidence-replication-series and enforces structural coherence rules
from the playbook at:
  docs/playbooks/outcome-evidence-replication-series-gate.md

Rules enforced:
  G1  All 8 required artifacts must be present per run.
  G2  A run with comparability.yml verdict=not_comparable must have
      outcome_upgrade_allowed=false and effect_claim_allowed=false.
  G3  task_class=validator_test_hardening only contributes real task diversity
      if changed-files.txt contains at least one real code path under
      scripts/, tests/, .github/workflows/, or Makefile.
      If no real code paths exist, outcome_upgrade_allowed must be false.
  G4  No run may claim outcome_upgrade_allowed=true unless the series has at
      least 4 comparable runs (verdict != not_comparable).
  G5  A negative_control run may only be counted when run.yml
      verdict.outcome == CLAIM_NOT_PROVEN.
  G6  If provenance.level == self_reported, independence_status cannot be
      full_independence — only partial_independence is permitted.

Exit code:
  0  All checks passed.
  1  One or more blocking violations found.

Benötigt: python3 -m pip install pyyaml
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("ERROR: Missing dependency. Run: python3 -m pip install pyyaml")
    sys.exit(1)


REPO_ROOT = Path(__file__).resolve().parent.parent.parent

SERIES_NAME = "outcome-evidence-replication-series"

REQUIRED_RUN_ARTIFACTS = [
    "run.yml",
    "measurement.yml",
    "auditor-output.yml",
    "evidence-pack.yml",
    "comparability.yml",
    "changed-files.txt",
    "timing.txt",
    "make-validate.txt",
]

# Path prefixes that count as real code/test contributions
REAL_CODE_PREFIXES = (
    "scripts/",
    "tests/",
    ".github/workflows/",
)

REAL_CODE_EXACT = {"Makefile"}

GATE_MIN_COMPARABLE_RUNS = 4


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def _changed_files_has_real_code(path: Path) -> bool:
    """Return True if changed-files.txt has at least one real code/test path."""
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t", 1)
            file_path = (parts[1].strip() if len(parts) > 1 else parts[0].strip())
            if file_path in REAL_CODE_EXACT:
                return True
            if any(file_path.startswith(p) for p in REAL_CODE_PREFIXES):
                return True
        return False
    except Exception:
        return False


def validate_run(run_dir: Path) -> list[str]:
    """Validate one run directory. Returns blocking error messages."""
    errors: list[str] = []
    name = run_dir.name

    # G1 — required artifacts
    for artifact in REQUIRED_RUN_ARTIFACTS:
        if not (run_dir / artifact).exists():
            errors.append(f"[{name}] G1: missing required artifact: {artifact}")

    # Load comparability.yml (tolerate absence — G1 already flagged it)
    comp: dict[str, Any] = {}
    comp_path = run_dir / "comparability.yml"
    if comp_path.exists():
        comp = _load_yaml(comp_path)

    verdict = comp.get("verdict", "")
    task_class = comp.get("task_class", "")
    outcome_upgrade_allowed = bool(comp.get("outcome_upgrade_allowed", False))
    effect_claim_allowed = bool(comp.get("effect_claim_allowed", False))
    negative_control = bool(comp.get("negative_control", False))

    # G2 — not_comparable must not claim upgrades
    if verdict == "not_comparable":
        if outcome_upgrade_allowed:
            errors.append(
                f"[{name}] G2: verdict=not_comparable but outcome_upgrade_allowed=true"
            )
        if effect_claim_allowed:
            errors.append(
                f"[{name}] G2: verdict=not_comparable but effect_claim_allowed=true"
            )

    # G3 — validator_test_hardening without real code paths cannot claim upgrade
    if task_class == "validator_test_hardening":
        changed_files = run_dir / "changed-files.txt"
        if not _changed_files_has_real_code(changed_files) and outcome_upgrade_allowed:
            errors.append(
                f"[{name}] G3: task_class=validator_test_hardening with no real code paths "
                f"in changed-files.txt, but outcome_upgrade_allowed=true"
            )

    # G5 — negative_control requires CLAIM_NOT_PROVEN outcome in run.yml
    if negative_control:
        run_path = run_dir / "run.yml"
        if run_path.exists():
            run_data = _load_yaml(run_path)
            outcome = (run_data.get("verdict") or {}).get("outcome", "")
            if outcome and outcome != "CLAIM_NOT_PROVEN":
                errors.append(
                    f"[{name}] G5: negative_control=true but run.yml verdict.outcome="
                    f"'{outcome}' (expected CLAIM_NOT_PROVEN)"
                )

    # G6 — self_reported provenance cannot claim full independence
    run_path = run_dir / "run.yml"
    if run_path.exists():
        run_data = _load_yaml(run_path)
        provenance_level = (run_data.get("provenance") or {}).get("level", "")
        if provenance_level == "self_reported":
            meas_path = run_dir / "measurement.yml"
            if meas_path.exists():
                meas = _load_yaml(meas_path)
                independence = (meas.get("extensions") or {}).get("independence_status", "")
                if independence in ("full_independence", "full"):
                    errors.append(
                        f"[{name}] G6: provenance=self_reported cannot claim "
                        f"independence_status={independence}"
                    )

    return errors


def validate_series(series_dir: Path) -> list[str]:
    """Validate all runs in one series directory."""
    errors: list[str] = []

    artifacts_dir = series_dir / "artifacts"
    if not artifacts_dir.is_dir():
        return [f"[series:{series_dir.name}] no artifacts/ directory found"]

    run_dirs = sorted(
        d for d in artifacts_dir.iterdir()
        if d.is_dir() and d.name.startswith("run-")
    )
    if not run_dirs:
        return []

    # Per-run checks
    comparable_count = 0
    for run_dir in run_dirs:
        errors.extend(validate_run(run_dir))
        comp_path = run_dir / "comparability.yml"
        if comp_path.exists():
            comp = _load_yaml(comp_path)
            if comp.get("verdict", "") != "not_comparable":
                comparable_count += 1

    # G4 — no premature upgrade claims at series level
    for run_dir in run_dirs:
        comp_path = run_dir / "comparability.yml"
        if not comp_path.exists():
            continue
        comp = _load_yaml(comp_path)
        if comp.get("outcome_upgrade_allowed", False) and comparable_count < GATE_MIN_COMPARABLE_RUNS:
            errors.append(
                f"[{run_dir.name}] G4: outcome_upgrade_allowed=true but series has only "
                f"{comparable_count} comparable run(s) (minimum {GATE_MIN_COMPARABLE_RUNS} required)"
            )

    return errors


def validate_repo(repo_root: Path | None = None) -> list[str]:
    """Discover and validate all outcome-evidence-replication-series experiments."""
    if repo_root is None:
        repo_root = REPO_ROOT

    experiments_dir = repo_root / "experiments"
    if not experiments_dir.is_dir():
        return []

    errors: list[str] = []
    for exp_dir in sorted(experiments_dir.iterdir()):
        if exp_dir.is_dir() and SERIES_NAME in exp_dir.name:
            errors.extend(validate_series(exp_dir))

    return errors


def main() -> None:
    errors = validate_repo()
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    print("OK: outcome-evidence-replication-series gate checks passed.")


if __name__ == "__main__":
    main()
