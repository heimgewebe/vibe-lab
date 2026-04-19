#!/usr/bin/env python3
"""Validate the Phase-1c experiment-structure fixture corpus.

This checker is intentionally local and deterministic.
It validates the fixture corpus under
`tests/fixtures/experiment_structure_phase1c/` against
`expected-outcomes.json` and supports only three derived states:

- valid
- inconsistent
- insufficient_input

It does not mutate repository state, does not scan `experiments/*`, and does
not participate in the general schema-validation pipeline.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "experiment_structure_phase1c"
EXPECTED_OUTCOMES = "expected-outcomes.json"
REQUIRED_FILES = (
    "manifest.yml",
    "results/evidence.jsonl",
    "results/decision.yml",
    "results/result.md",
)
RESULT_VERDICT_RE = re.compile(
    r"^## Verdict\s*$\n+([\s\S]*?)(?:^##\s+|\Z)", re.MULTILINE
)
STATUS_TOKEN_RE = re.compile(r"\b(adopted|rejected|inconclusive|blocked)\b", re.IGNORECASE)

_YAML_SPEC = importlib.util.find_spec("yaml")
if _YAML_SPEC is not None:
    import yaml  # type: ignore
else:
    yaml = None


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_expected_cases(fixtures_dir: Path) -> dict[str, dict]:
    expected_path = fixtures_dir / EXPECTED_OUTCOMES
    if not expected_path.is_file():
        raise FileNotFoundError(f"MISSING: {display_path(expected_path)}")

    data = load_json(expected_path)
    cases = data.get("cases")
    if not isinstance(cases, dict) or not cases:
        raise ValueError(f"BLOCKED_BY: invalid expected outcomes structure in {display_path(expected_path)}")
    return cases


def _minimal_yaml_parse(text: str) -> dict:
    data: dict[str, object] = {}
    section: str | None = None
    for raw_line in text.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if raw_line.startswith("  ") and section and ":" in raw_line:
            key, value = raw_line.split(":", 1)
            nested = data.setdefault(section, {})
            if isinstance(nested, dict):
                nested[key.strip()] = value.strip().strip('"').strip("'")
            continue
        if ":" not in raw_line:
            continue
        key, value = raw_line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not value:
            section = key
            data.setdefault(key, {})
            continue
        section = None
        data[key] = value.strip('"').strip("'")
    return data


def load_yaml_or_minimal(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if yaml is not None:
        loaded = yaml.safe_load(text)
        return loaded if isinstance(loaded, dict) else {}
    return _minimal_yaml_parse(text)


def read_required_file(case_dir: Path, relative_path: str) -> tuple[Path, str | None, str | None]:
    path = case_dir / relative_path
    if not path.is_file():
        return path, None, "missing"
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return path, text, "empty"
    return path, text, None


def validate_jsonl(path: Path) -> tuple[int, list[str]]:
    valid_entries = 0
    errors: list[str] = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{display_path(path)}:{line_number}: invalid jsonl entry ({exc.msg})")
            continue
        valid_entries += 1
    return valid_entries, errors


def extract_result_status(result_text: str) -> str | None:
    match = RESULT_VERDICT_RE.search(result_text)
    if not match:
        return None
    verdict_block = match.group(1)
    token = STATUS_TOKEN_RE.search(verdict_block)
    if not token:
        return None
    return token.group(1).lower()


def map_decision_verdict_to_status(decision_verdict: str | None) -> str | None:
    mapping = {
        "confirms": "adopted",
        "refutes": "rejected",
        "mixed": "inconclusive",
        "inconclusive": "inconclusive",
    }
    if decision_verdict is None:
        return None
    return mapping.get(decision_verdict.strip().lower())


def compute_confidence(
    all_required_present: bool,
    format_checks_passed: bool,
    no_conflict: bool,
    strong_evidence: bool,
    derived_case: str,
) -> float:
    if derived_case == "insufficient_input":
        return 0.0
    score = 0.0
    if all_required_present:
        score += 0.25
    if format_checks_passed:
        score += 0.25
    if no_conflict:
        score += 0.25
    if strong_evidence:
        score += 0.25
    bounded = min(max(score, 0.0), 1.0)
    if derived_case == "inconsistent":
        return min(bounded, 0.5)
    return bounded


def evaluate_case(case_name: str, case_dir: Path) -> dict:
    missing_or_empty: list[str] = []
    parsing_errors: list[str] = []
    loaded_texts: dict[str, str] = {}

    for relative_path in REQUIRED_FILES:
        file_path, text, state = read_required_file(case_dir, relative_path)
        if state is not None:
            missing_or_empty.append(f"{relative_path}:{state}")
            continue
        loaded_texts[relative_path] = text or ""

    if missing_or_empty:
        return {
            "case_name": case_name,
            "derived_case": "insufficient_input",
            "observed_verdict": "ERROR",
            "observed_status_assessment": None,
            "observed_confidence": 0.0,
            "details": missing_or_empty,
        }

    format_checks_passed = True
    try:
        manifest_data = load_yaml_or_minimal(case_dir / "manifest.yml")
    except Exception as exc:
        parsing_errors.append(f"manifest.yml: unreadable ({exc})")
        manifest_data = {}
        format_checks_passed = False

    try:
        decision_data = load_yaml_or_minimal(case_dir / "results/decision.yml")
    except Exception as exc:
        parsing_errors.append(f"results/decision.yml: unreadable ({exc})")
        decision_data = {}
        format_checks_passed = False

    valid_entries, jsonl_errors = validate_jsonl(case_dir / "results/evidence.jsonl")
    if jsonl_errors:
        parsing_errors.extend(jsonl_errors)
        format_checks_passed = False

    result_status = extract_result_status(loaded_texts["results/result.md"])
    decision_status = map_decision_verdict_to_status(decision_data.get("verdict") if isinstance(decision_data, dict) else None)
    manifest_status = None
    if isinstance(manifest_data, dict):
        experiment = manifest_data.get("experiment")
        if isinstance(experiment, dict):
            raw_status = experiment.get("status")
            if isinstance(raw_status, str):
                manifest_status = raw_status.strip().lower()

    if decision_status is None:
        parsing_errors.append("results/decision.yml: verdict missing or unsupported")
        format_checks_passed = False
    if result_status is None:
        parsing_errors.append("results/result.md: verdict section missing or unsupported")
        format_checks_passed = False

    strong_evidence = valid_entries >= 3
    consistency_conflicts: list[str] = []
    if decision_status and result_status and decision_status != result_status:
        consistency_conflicts.append(
            f"decision/result mismatch decision={decision_status} result={result_status}"
        )

    if manifest_status and decision_status and manifest_status not in {decision_status, "testing"}:
        consistency_conflicts.append(
            f"manifest/decision mismatch manifest={manifest_status} decision={decision_status}"
        )

    if parsing_errors:
        derived_case = "inconsistent"
    elif consistency_conflicts:
        derived_case = "inconsistent"
    else:
        derived_case = "valid"

    observed_verdict = {
        "valid": "VALID",
        "inconsistent": "INCONSISTENT",
        "insufficient_input": "ERROR",
    }[derived_case]
    observed_status_assessment = None if derived_case == "insufficient_input" else decision_status
    observed_confidence = compute_confidence(
        all_required_present=True,
        format_checks_passed=format_checks_passed,
        no_conflict=not consistency_conflicts,
        strong_evidence=strong_evidence,
        derived_case=derived_case,
    )

    details = parsing_errors + consistency_conflicts
    return {
        "case_name": case_name,
        "derived_case": derived_case,
        "observed_verdict": observed_verdict,
        "observed_status_assessment": observed_status_assessment,
        "observed_confidence": observed_confidence,
        "details": details,
    }


def compare_case(case_name: str, observed: dict, expected: dict) -> list[str]:
    mismatches: list[str] = []
    if observed["observed_verdict"] != expected.get("expected_verdict"):
        mismatches.append(
            f"{case_name}: verdict expected={expected.get('expected_verdict')} observed={observed['observed_verdict']}"
        )
    if observed["observed_status_assessment"] != expected.get("expected_status_assessment"):
        mismatches.append(
            f"{case_name}: status expected={expected.get('expected_status_assessment')} observed={observed['observed_status_assessment']}"
        )
    if observed["observed_confidence"] != expected.get("expected_confidence"):
        mismatches.append(
            f"{case_name}: confidence expected={expected.get('expected_confidence')} observed={observed['observed_confidence']}"
        )
    return mismatches


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Phase-1c experiment-structure fixtures")
    parser.add_argument(
        "--fixtures",
        type=Path,
        default=DEFAULT_FIXTURE_DIR,
        help=(
            "Directory containing Phase-1c experiment-structure fixtures "
            "(default: tests/fixtures/experiment_structure_phase1c)"
        ),
    )
    args = parser.parse_args()

    fixtures_dir = (REPO_ROOT / args.fixtures).resolve() if not args.fixtures.is_absolute() else args.fixtures
    if not fixtures_dir.is_dir():
        print(f"ERROR: fixtures directory missing: {display_path(fixtures_dir)}")
        sys.exit(2)

    try:
        expected_cases = load_expected_cases(fixtures_dir)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        sys.exit(2)

    print("🔍 Phase-1c Fixture Validation")

    errors: list[str] = []
    for case_name, expected in expected_cases.items():
        fixture_path_value = expected.get("fixture_path")
        if not isinstance(fixture_path_value, str) or not fixture_path_value.strip():
            errors.append(f"{case_name}: BLOCKED_BY: fixture_path missing in expected outcomes")
            continue

        case_dir = (REPO_ROOT / fixture_path_value).resolve()
        if not case_dir.is_dir():
            errors.append(f"{case_name}: MISSING: fixture directory {display_path(case_dir)}")
            continue

        observed = evaluate_case(case_name, case_dir)
        mismatches = compare_case(case_name, observed, expected)
        if mismatches:
            errors.extend(mismatches)
            for detail in observed["details"]:
                errors.append(f"{case_name}: detail: {detail}")
            continue

        print(f"  ✅ {case_name}")

    if errors:
        print("\n❌ Fixture validation failed:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    print("\n✅ Fixture validation passed.")


if __name__ == "__main__":
    main()