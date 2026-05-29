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
  G4  No run may claim upgrade flags=true
      (comparability: outcome/effect/promotion; run verdict: effect/promotion;
      optional measurement extension: outcome_upgrade_allowed)
      unless the series has at least 4 comparable runs (verdict is "comparable").
  G5  A negative_control run may only be counted when run.yml
      verdict.outcome == CLAIM_NOT_PROVEN.
  G6  If provenance.level == self_reported, run-artifact independence_status
      fields (measurement extensions + comparability) cannot claim
      full-independence variants.
  G7  If any run claims upgrade flags=true, the series must satisfy all playbook
      minimum criteria: comparable_count >= 4, at least 3 distinct task classes,
      at least 2 comparable runs with independent review, at least 1 comparable
      run with full_independence, and at least 1 negative_control run.

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
ALLOWED_VERDICTS = {"comparable", "not_comparable", "reference_only"}
STRICT_MAPPING_ARTIFACTS = (
    "run.yml",
    "measurement.yml",
    "comparability.yml",
    "auditor-output.yml",
    "evidence-pack.yml",
)
DISALLOWED_SELF_REPORTED_INDEPENDENCE_VALUES = {
    "full",
    "full_independence",
    "FULL_BY_MODEL_FAMILY",
    "full_by_model_family_for_this_audit",
}

# Independence values that count as "full" for G7 criteria
FULL_INDEPENDENCE_VALUES = {
    "full",
    "full_independence",
    "FULL_BY_MODEL_FAMILY",
}

# Independence values that count as independent review (excludes partial)
INDEPENDENT_REVIEW_VALUES = FULL_INDEPENDENCE_VALUES | {
    "independent",
    "independent_review",
}


def _load_yaml_strict(path: Path, errors: list[str], run_name: str, artifact: str) -> dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
    except Exception as exc:
        errors.append(f"[{run_name}] G1: failed to read {artifact}: {exc}")
        return {}

    try:
        data = yaml.safe_load(raw)
    except Exception as exc:
        errors.append(f"[{run_name}] G1: malformed YAML in {artifact}: {exc}")
        return {}

    if data is None:
        errors.append(f"[{run_name}] G1: empty YAML document in {artifact}")
        return {}
    if not isinstance(data, dict):
        errors.append(f"[{run_name}] G1: {artifact} must be a YAML mapping/object")
        return {}

    return data


def _yaml_bool(
    mapping: dict[str, Any],
    key: str,
    *,
    errors: list[str],
    run_name: str,
    rule: str,
    artifact: str,
    default: bool = False,
) -> bool:
    value = mapping.get(key, default)
    if isinstance(value, bool):
        return value
    errors.append(
        f"[{run_name}] {rule}: {artifact}.{key} must be a YAML boolean (true/false), got {type(value).__name__}"
    )
    return default


def _nested_mapping(
    parent: dict[str, Any],
    key: str,
    *,
    errors: list[str],
    run_name: str,
    rule: str,
    artifact: str,
) -> dict[str, Any]:
    value = parent.get(key, {})
    if isinstance(value, dict):
        return value
    errors.append(f"[{run_name}] {rule}: {artifact}.{key} must be a YAML mapping/object")
    return {}


def _validate_run_and_collect(run_dir: Path) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    name = run_dir.name
    loaded: dict[str, dict[str, Any]] = {}

    for artifact in REQUIRED_RUN_ARTIFACTS:
        artifact_path = run_dir / artifact
        if not artifact_path.exists():
            errors.append(f"[{name}] G1: missing required artifact: {artifact}")
            continue
        if artifact in STRICT_MAPPING_ARTIFACTS:
            loaded[artifact] = _load_yaml_strict(artifact_path, errors, name, artifact)

    comp = loaded.get("comparability.yml", {})
    run_data = loaded.get("run.yml", {})
    measurement = loaded.get("measurement.yml", {})

    verdict = comp.get("verdict", "")
    if not isinstance(verdict, str):
        errors.append(
            f"[{name}] G2: comparability.yml verdict must be a string in {sorted(ALLOWED_VERDICTS)}"
        )
        verdict = ""
    verdict = verdict.strip()
    if verdict not in ALLOWED_VERDICTS:
        errors.append(
            f"[{name}] G2: comparability.yml verdict must be one of {sorted(ALLOWED_VERDICTS)}, got {verdict!r}"
        )

    task_class = comp.get("task_class", "")
    if not isinstance(task_class, str):
        task_class = ""

    outcome_upgrade_allowed = _yaml_bool(
        comp,
        "outcome_upgrade_allowed",
        errors=errors,
        run_name=name,
        rule="G2",
        artifact="comparability.yml",
    )
    comp_effect_claim_allowed = _yaml_bool(
        comp,
        "effect_claim_allowed",
        errors=errors,
        run_name=name,
        rule="G2",
        artifact="comparability.yml",
    )
    comp_promotion_claim_allowed = _yaml_bool(
        comp,
        "promotion_claim_allowed",
        errors=errors,
        run_name=name,
        rule="G2",
        artifact="comparability.yml",
    )
    negative_control = _yaml_bool(
        comp,
        "negative_control",
        errors=errors,
        run_name=name,
        rule="G5",
        artifact="comparability.yml",
    )

    run_verdict = _nested_mapping(
        run_data,
        "verdict",
        errors=errors,
        run_name=name,
        rule="G2",
        artifact="run.yml",
    )
    run_effect_claim_allowed = _yaml_bool(
        run_verdict,
        "effect_claim_allowed",
        errors=errors,
        run_name=name,
        rule="G2",
        artifact="run.yml verdict",
    )
    run_promotion_claim_allowed = _yaml_bool(
        run_verdict,
        "promotion_claim_allowed",
        errors=errors,
        run_name=name,
        rule="G2",
        artifact="run.yml verdict",
    )

    measurement_extensions = _nested_mapping(
        measurement,
        "extensions",
        errors=errors,
        run_name=name,
        rule="G2",
        artifact="measurement.yml",
    )
    meas_outcome_upgrade_present = "outcome_upgrade_allowed" in measurement_extensions
    meas_outcome_upgrade_allowed = False
    if meas_outcome_upgrade_present:
        meas_outcome_upgrade_allowed = _yaml_bool(
            measurement_extensions,
            "outcome_upgrade_allowed",
            errors=errors,
            run_name=name,
            rule="G2",
            artifact="measurement.yml extensions",
        )

    # measurement.yml extensions.outcome_upgrade_allowed is optional in this repo,
    # while comparability/run verdict flags are treated as core gate flags.
    upgrade_flags: list[tuple[str, bool]] = [
        ("comparability.yml outcome_upgrade_allowed", outcome_upgrade_allowed),
        ("comparability.yml effect_claim_allowed", comp_effect_claim_allowed),
        ("comparability.yml promotion_claim_allowed", comp_promotion_claim_allowed),
        ("run.yml verdict.effect_claim_allowed", run_effect_claim_allowed),
        ("run.yml verdict.promotion_claim_allowed", run_promotion_claim_allowed),
    ]
    if meas_outcome_upgrade_present:
        upgrade_flags.append(
            ("measurement.yml extensions.outcome_upgrade_allowed", meas_outcome_upgrade_allowed)
        )

    # G2 — not_comparable must not claim upgrades
    if verdict == "not_comparable":
        for flag_name, flag_value in upgrade_flags:
            if flag_value:
                errors.append(
                    f"[{name}] G2: verdict=not_comparable but {flag_name}=true"
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
        outcome = run_verdict.get("outcome")
        if outcome != "CLAIM_NOT_PROVEN":
            outcome_display = "<missing>" if not outcome else repr(outcome)
            errors.append(
                f"[{name}] G5: negative_control=true but run.yml verdict.outcome="
                f"{outcome_display} (expected 'CLAIM_NOT_PROVEN')"
            )

    # G6 — self_reported provenance cannot claim full independence
    provenance = _nested_mapping(
        run_data,
        "provenance",
        errors=errors,
        run_name=name,
        rule="G6",
        artifact="run.yml",
    )
    provenance_level = provenance.get("level", "")
    if provenance_level == "self_reported":
        measurement_independence = measurement_extensions.get("independence_status")
        comparability_independence = comp.get("independence_status")
        for src, value in (
            ("measurement.yml extensions.independence_status", measurement_independence),
            ("comparability.yml independence_status", comparability_independence),
        ):
            if value in DISALLOWED_SELF_REPORTED_INDEPENDENCE_VALUES:
                errors.append(
                    f"[{name}] G6: provenance=self_reported cannot claim {src}={value!r}"
                )

    return errors, {
        "verdict": verdict if verdict in ALLOWED_VERDICTS else "",
        "task_class": task_class,
        "upgrade_flags": upgrade_flags,
        "negative_control": negative_control,
        "provenance_level": provenance_level,
        "independence_status": comp.get("independence_status", ""),
        "measurement_independence_status": measurement_extensions.get("independence_status", ""),
    }


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
    errors, _ = _validate_run_and_collect(run_dir)
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
    run_infos: list[tuple[Path, dict[str, Any]]] = []
    for run_dir in run_dirs:
        run_errors, run_info = _validate_run_and_collect(run_dir)
        errors.extend(run_errors)
        run_infos.append((run_dir, run_info))
        if run_info.get("verdict") == "comparable":
            comparable_count += 1

    # G4 — no premature upgrade claims at series level
    if comparable_count < GATE_MIN_COMPARABLE_RUNS:
        for run_dir, run_info in run_infos:
            for flag_name, flag_value in run_info.get("upgrade_flags", []):
                if flag_value:
                    errors.append(
                        f"[{run_dir.name}] G4: {flag_name}=true but series has only "
                        f"{comparable_count} comparable run(s) (minimum {GATE_MIN_COMPARABLE_RUNS} required)"
                    )

    # G7 — if any upgrade flag is true, enforce full playbook criteria
    any_upgrade_flag_true = any(
        flag_value
        for _, run_info in run_infos
        for _, flag_value in run_info.get("upgrade_flags", [])
    )

    if any_upgrade_flag_true:
        # Collect data from comparable runs
        comparable_runs = [
            (run_dir, run_info)
            for run_dir, run_info in run_infos
            if run_info.get("verdict") == "comparable"
        ]
        
        if comparable_count < GATE_MIN_COMPARABLE_RUNS:
            errors.append(
                f"[series:{series_dir.name}] G7: upgrade flag(s) true but only "
                f"{comparable_count} comparable run(s) (need {GATE_MIN_COMPARABLE_RUNS})"
            )
        
        # Check distinct task classes
        # For validator_test_hardening, only count if it has real code changes
        distinct_task_classes = set()
        for run_dir, run_info in comparable_runs:
            task_class = run_info.get("task_class", "").strip()
            if not task_class:
                continue
            
            # Validator test runs only count if they have real code changes
            if task_class == "validator_test_hardening":
                changed_files = run_dir / "changed-files.txt"
                if not _changed_files_has_real_code(changed_files):
                    # Skip this run as it doesn't contribute real task diversity
                    continue
            
            distinct_task_classes.add(task_class)
        
        if len(distinct_task_classes) < 3:
            errors.append(
                f"[series:{series_dir.name}] G7: upgrade flag(s) true but only "
                f"{len(distinct_task_classes)} distinct task class(es) among comparable runs "
                f"(need 3): {sorted(distinct_task_classes)}"
            )
        
        # Check for independent review runs (not partial, not self_reported without full)
        independent_review_count = 0
        for _, run_info in comparable_runs:
            independence = run_info.get("independence_status", "")
            measurement_independence = run_info.get("measurement_independence_status", "")
            provenance = run_info.get("provenance_level", "")
            
            # Use measurement independence if available, otherwise use comparability independence
            independence_to_check = measurement_independence or independence
            
            # For self_reported provenance, only full independence counts
            if provenance == "self_reported":
                if independence_to_check in FULL_INDEPENDENCE_VALUES:
                    independent_review_count += 1
            else:
                # For other provenance, use the explicit allowlist of independent values
                if independence_to_check in INDEPENDENT_REVIEW_VALUES:
                    independent_review_count += 1
        
        if independent_review_count < 2:
            errors.append(
                f"[series:{series_dir.name}] G7: upgrade flag(s) true but only "
                f"{independent_review_count} comparable run(s) with independent review "
                f"(need 2)"
            )
        
        # Check for full independence
        full_independence_count = 0
        for _, run_info in comparable_runs:
            independence = run_info.get("independence_status", "")
            measurement_independence = run_info.get("measurement_independence_status", "")
            
            # Use measurement independence if available, otherwise use comparability independence
            independence_to_check = measurement_independence or independence
            
            if independence_to_check in FULL_INDEPENDENCE_VALUES:
                full_independence_count += 1
        
        if full_independence_count < 1:
            errors.append(
                f"[series:{series_dir.name}] G7: upgrade flag(s) true but no comparable run "
                f"with full_independence (need 1)"
            )
        
        # Check for negative control run
        negative_control_count = sum(
            1 for _, run_info in run_infos
            if run_info.get("negative_control", False)
        )
        
        if negative_control_count < 1:
            errors.append(
                f"[series:{series_dir.name}] G7: upgrade flag(s) true but no negative_control run "
                f"(need 1)"
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
