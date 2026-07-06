#!/usr/bin/env python3
"""Validate Ecosystem-Organ-Preflight run records.

This guard is intentionally narrow. It does not re-validate the whole
experiment manifest (that is covered by validate_schema.py). It only guards
the specific failure modes of the organ-preflight instrumentation:

1. A run record (results/runs/run-*.yml) must carry every required field,
   valid enum values and at least one existing evidence reference.
2. Metrics must live in the structured run data, not only in the narrative
   result.md.
3. Neither the run records nor results/result.md may claim that the preflight
   *already* improves ecosystem work (efficacy claim from a seed / single run).

TEMPLATE.yml is skipped on purpose.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT_REL = "experiments/2026-07-05_ecosystem-organ-preflight"

REQUIRED_TOP_FIELDS = (
    "task_id",
    "timestamp",
    "repo",
    "active_ball",
    "task_class",
    "perceived_complexity",
    "primary_truth_source",
    "allowed_context_organs",
    "blocked_organs",
    "stop_rules",
    "predicted_primary_organ",
    "actual_primary_organ",
    "evidence_refs",
    "metrics",
    "verdict",
    "interpretation_budget",
)
# pr / issue / slice are required keys but may be null / empty.
REQUIRED_NULLABLE_FIELDS = ("pr", "issue", "slice")

REQUIRED_METRIC_FIELDS = (
    "wrong_organ_corrections",
    "rework_loops",
    "next_step_ambiguity",
    "friction_cost_minutes",
    "safety_value",
)
REQUIRED_BUDGET_FIELDS = ("allowed_claims", "disallowed_claims", "epistemic_gaps")

COMPLEXITY_ENUM = {"low", "medium", "high"}
AMBIGUITY_ENUM = {"none", "low", "medium", "high"}
SAFETY_ENUM = {"none", "low", "medium", "high"}
# Deliberately no efficacy-positive verdict: a run cannot encode "it works".
VERDICT_ENUM = {"usability_only", "instrumentation_only", "inconclusive"}

# Efficacy / improvement claims that a seed or single run must NOT assert.
FORBIDDEN_CLAIM_PATTERNS = [
    re.compile(r"verbessert\s+(bereits\s+)?(die\s+)?(oe|ö)kosystem", re.IGNORECASE),
    re.compile(r"already\s+improves?\s+ecosystem", re.IGNORECASE),
    re.compile(r"improves?\s+ecosystem\s+work", re.IGNORECASE),
    re.compile(r"reduziert\s+nachweislich", re.IGNORECASE),
    re.compile(r"belegt\s+die\s+hypothese", re.IGNORECASE),
    re.compile(r"proven\s+effective", re.IGNORECASE),
    re.compile(r"wirksamkeit\s+(ist\s+)?(be|nach)legt", re.IGNORECASE),
]

# Metric axis tokens used to detect metrics leaking into narrative-only form.
METRIC_TOKENS = (
    "wrong_organ_corrections",
    "rework_loops",
    "next_step_ambiguity",
    "friction_cost_minutes",
    "safety_value",
)


def _repo_rel(path: Path, *, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _is_nonneg_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _is_nonneg_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and value >= 0
    )


def _is_path_ref(ref: str) -> bool:
    """A pathlike evidence ref (must resolve to a file), vs an external ref."""
    if "://" in ref or ref.startswith(("github:", "pr:", "issue:")):
        return False
    return ref.startswith(("results/", "experiments/", "artifacts/", "raw-vibes/"))


def _validate_run_file(run_path: Path, exp_root: Path, root: Path) -> list[str]:
    errors: list[str] = []
    rel = _repo_rel(run_path, root=root)

    try:
        data = _load_yaml(run_path)
    except yaml.YAMLError as exc:  # pragma: no cover - defensive
        return [f"{rel}: invalid YAML — {exc}"]
    if not isinstance(data, dict):
        return [f"{rel}: run record must be a YAML mapping"]

    for field in REQUIRED_TOP_FIELDS:
        if field not in data or data[field] in (None, "", [], {}):
            errors.append(f"{rel}: missing required field '{field}'")
    for field in REQUIRED_NULLABLE_FIELDS:
        if field not in data:
            errors.append(f"{rel}: missing required field '{field}' (may be null)")

    if data.get("perceived_complexity") not in COMPLEXITY_ENUM:
        errors.append(
            f"{rel}: perceived_complexity must be one of {sorted(COMPLEXITY_ENUM)}"
        )
    if data.get("verdict") not in VERDICT_ENUM:
        errors.append(f"{rel}: verdict must be one of {sorted(VERDICT_ENUM)}")

    # metrics block
    metrics = data.get("metrics")
    if not isinstance(metrics, dict):
        errors.append(f"{rel}: metrics must be a mapping with all axes")
    else:
        for field in REQUIRED_METRIC_FIELDS:
            if field not in metrics:
                errors.append(f"{rel}: metrics missing '{field}'")
        if not _is_nonneg_int(metrics.get("wrong_organ_corrections")):
            errors.append(f"{rel}: metrics.wrong_organ_corrections must be int >= 0")
        if not _is_nonneg_int(metrics.get("rework_loops")):
            errors.append(f"{rel}: metrics.rework_loops must be int >= 0")
        if not _is_nonneg_number(metrics.get("friction_cost_minutes")):
            errors.append(f"{rel}: metrics.friction_cost_minutes must be number >= 0")
        if metrics.get("next_step_ambiguity") not in AMBIGUITY_ENUM:
            errors.append(
                f"{rel}: metrics.next_step_ambiguity must be one of {sorted(AMBIGUITY_ENUM)}"
            )
        if metrics.get("safety_value") not in SAFETY_ENUM:
            errors.append(
                f"{rel}: metrics.safety_value must be one of {sorted(SAFETY_ENUM)}"
            )

    # evidence_refs: non-empty, and pathlike refs must exist as files
    refs = data.get("evidence_refs")
    if not isinstance(refs, list) or not refs:
        errors.append(f"{rel}: evidence_refs must be a non-empty list")
    else:
        path_refs = [r for r in refs if isinstance(r, str) and _is_path_ref(r)]
        if not path_refs:
            errors.append(
                f"{rel}: evidence_refs must contain at least one pathlike evidence ref"
            )
        for ref in path_refs:
            if not (exp_root / ref).is_file():
                errors.append(
                    f"{rel}: evidence_ref '{ref}' does not exist under experiment root"
                )

    # interpretation_budget block
    budget = data.get("interpretation_budget")
    if not isinstance(budget, dict):
        errors.append(f"{rel}: interpretation_budget must be a mapping")
    else:
        for field in REQUIRED_BUDGET_FIELDS:
            value = budget.get(field)
            if not isinstance(value, list) or not value:
                errors.append(
                    f"{rel}: interpretation_budget.{field} must be a non-empty list"
                )
        for claim in budget.get("allowed_claims", []) or []:
            if isinstance(claim, str) and _matches_forbidden(claim):
                errors.append(
                    f"{rel}: interpretation_budget.allowed_claims contains a forbidden "
                    f"efficacy claim: {claim!r}"
                )

    return errors


def _matches_forbidden(text: str) -> bool:
    return any(pat.search(text) for pat in FORBIDDEN_CLAIM_PATTERNS)


def _strip_disallowed_section(result_text: str) -> str:
    """Remove the 'Disallowed Claims' subsection.

    Efficacy phrases are legitimate there (they are being disclaimed), so the
    forbidden-claim scan must not treat them as violations.
    """
    lines = result_text.splitlines()
    out: list[str] = []
    skipping = False
    for line in lines:
        heading = re.match(r"^(#{1,6})\s+(.*)$", line)
        if heading:
            title = heading.group(2).strip().lower()
            skipping = "disallowed claims" in title
        if not skipping:
            out.append(line)
    return "\n".join(out)


def _validate_result_md(
    result_path: Path, run_files: list[Path], root: Path
) -> list[str]:
    errors: list[str] = []
    if not result_path.is_file():
        return errors
    rel = _repo_rel(result_path, root=root)
    text = result_path.read_text(encoding="utf-8")

    scan_text = _strip_disallowed_section(text)
    for pat in FORBIDDEN_CLAIM_PATTERNS:
        match = pat.search(scan_text)
        if match:
            errors.append(
                f"{rel}: forbidden efficacy claim in result.md: {match.group(0)!r}"
            )

    # metrics-only-in-narrative guard: if result.md quotes metric axes with a
    # number but no run file carries a metrics block, that is retro-narration.
    mentions_metric_number = any(
        re.search(re.escape(token) + r"\D{0,40}\d", scan_text) for token in METRIC_TOKENS
    )
    has_run_metrics = any(_run_has_metrics(p) for p in run_files)
    if mentions_metric_number and not has_run_metrics:
        errors.append(
            f"{rel}: metrics referenced in result.md but no run record carries a "
            f"metrics block (metrics must originate in run data, not narrative)"
        )
    return errors


def _run_has_metrics(run_path: Path) -> bool:
    try:
        data = _load_yaml(run_path)
    except yaml.YAMLError:
        return False
    return isinstance(data, dict) and isinstance(data.get("metrics"), dict)


def _manifest_execution_status(exp_root: Path) -> str | None:
    manifest = exp_root / "manifest.yml"
    if not manifest.is_file():
        return None
    data = _load_yaml(manifest)
    experiment = data.get("experiment") if isinstance(data, dict) else None
    if isinstance(experiment, dict):
        status = experiment.get("execution_status")
        return status if isinstance(status, str) else None
    return None


def validate_ecosystem_organ_preflight(repo_root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    exp_root = repo_root / EXPERIMENT_REL
    if not exp_root.is_dir():
        # Experiment folder absent (e.g. isolated test root): nothing to check.
        return errors

    runs_dir = exp_root / "results" / "runs"
    run_files = sorted(
        p for p in runs_dir.glob("run-*.yml") if p.name != "TEMPLATE.yml"
    ) if runs_dir.is_dir() else []

    for run_path in run_files:
        errors.extend(_validate_run_file(run_path, exp_root, repo_root))

    # If the manifest claims the experiment was executed, there must be at least
    # one real run record carrying metrics.
    exec_status = _manifest_execution_status(exp_root)
    if exec_status in {"executed", "replicated"}:
        if not any(_run_has_metrics(p) for p in run_files):
            errors.append(
                f"{EXPERIMENT_REL}/manifest.yml: execution_status='{exec_status}' but no "
                f"results/runs/run-*.yml carries a metrics block"
            )

    errors.extend(
        _validate_result_md(exp_root / "results" / "result.md", run_files, repo_root)
    )
    return errors


def main() -> int:
    errors = validate_ecosystem_organ_preflight()
    print("🧭 Validating Ecosystem-Organ-Preflight run records...")
    if errors:
        print("❌ Ecosystem-Organ-Preflight validation FAILED:")
        for error in errors:
            print(f"  ❌ {error}")
        return 1
    print("✅ Ecosystem-Organ-Preflight run records are structured and claim-safe.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
