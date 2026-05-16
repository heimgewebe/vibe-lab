#!/usr/bin/env python3
"""Validate semantic claim-evidence compatibility for run evidence packs."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml
    from jsonschema import Draft202012Validator
    from jsonschema.exceptions import SchemaError
except ImportError as exc:
    print(
        "ERROR: Missing dependencies for claim-evidence validation. Install PyYAML and jsonschema.",
        file=sys.stderr,
    )
    raise SystemExit(2) from exc


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCHEMA_PATH = REPO_ROOT / "schemas" / "run-evidence-pack.v1.schema.json"

STRONG_EVIDENCE_STATUSES = {
    "repo_local",
    "ci_artifact",
    "external_verified",
    "derived_from_auditor_output",
}

MISSING_EVIDENCE_ALLOWED_VERDICTS = {
    "MISSING_EVIDENCE",
    "CLAIM_NOT_PROVEN",
}

TEST_OUTPUT_HINTS = (
    "test-output.txt",
    "test_output.txt",
    "pytest",
    "jest",
)

MAKE_VALIDATE_PATH_HINTS = (
    "make-validate.txt",
    "make_validate.txt",
    "make-validate-output",
    "make_validate_output",
)

CI_PATH_HINTS = (
    "ci-output.txt",
    "workflow",
    "job-log",
)

TESTCOUNT_PATTERN = re.compile(
    r"\b\d+/\d+\s+tests?\s+(?:bestanden|passed)\b",
    re.IGNORECASE,
)
CI_TEXT_PATTERN = re.compile(r"\b(?:ci workflow passed|ci bestanden)\b", re.IGNORECASE)


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def load_schema_validator() -> Draft202012Validator:
    try:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeError(f"schema file missing: {display_path(SCHEMA_PATH)}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"schema file invalid JSON: {display_path(SCHEMA_PATH)}: {exc}") from exc

    try:
        return Draft202012Validator(
            schema,
            format_checker=Draft202012Validator.FORMAT_CHECKER,
        )
    except SchemaError as exc:
        raise RuntimeError(f"schema invalid: {display_path(SCHEMA_PATH)}: {exc.message}") from exc


def load_yaml(path: Path) -> dict:
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"fixture missing: {display_path(path)}") from exc
    except yaml.YAMLError as exc:
        raise ValueError(f"YAML parse error in {display_path(path)}: {exc}") from exc

    if not isinstance(loaded, dict):
        raise ValueError(f"YAML document must be an object: {display_path(path)}")
    return loaded


def validate_schema(validator: Draft202012Validator, data: dict, path: Path) -> list[str]:
    errors: list[str] = []
    for error in sorted(validator.iter_errors(data), key=lambda item: list(item.absolute_path)):
        location = ".".join(str(part) for part in error.absolute_path) or "$"
        errors.append(
            f"ERROR path={display_path(path)} instance_path={location}: {error.message}"
        )
    return errors


def evidence_paths(claim: dict) -> list[str]:
    return [str(entry.get("path", "")).lower() for entry in claim.get("evidence", [])]


def evidence_statuses(claim: dict) -> list[str]:
    return [str(entry.get("status", "")).lower() for entry in claim.get("evidence", [])]


def is_make_validate_claim(claim: dict) -> bool:
    claim_type = str(claim.get("type", "")).lower()
    text = str(claim.get("text", "")).lower()
    return "make validate" in text or ("make" in claim_type and "validate" in claim_type)


def is_testcount_claim(claim: dict) -> bool:
    claim_type = str(claim.get("type", "")).lower()
    text = str(claim.get("text", ""))
    return claim_type == "test_result" and bool(TESTCOUNT_PATTERN.search(text))


def is_ci_claim(claim: dict) -> bool:
    claim_type = str(claim.get("type", "")).lower()
    text = str(claim.get("text", ""))
    return claim_type == "ci_result" or bool(CI_TEXT_PATTERN.search(text))


def format_error(rule_id: str, claim_id: str, path: Path, message: str) -> str:
    return f"ERROR claim_id={claim_id} rule={rule_id} path={display_path(path)}: {message}"


def has_non_empty_source(entry: dict) -> bool:
    if "source" not in entry:
        return False

    source = entry["source"]
    if isinstance(source, str):
        return bool(source.strip())
    if isinstance(source, dict):
        return bool(source)
    return False


def repo_local_existence_errors(claim: dict, path: Path, repo_root: Path) -> list[str]:
    """Emit REPO_LOCAL_EVIDENCE_PATH_NOT_FOUND for every repo_local evidence entry
    whose path does not resolve to an existing file under repo_root.

    Fires for PASS and non-PASS claims alike — repo_local is an existence claim.
    Path-escape attempts (resolved path outside repo_root) are silently skipped;
    other validators enforce path boundaries.
    """
    claim_id = str(claim.get("claim_id", "<missing>"))
    errors: list[str] = []
    for entry in claim.get("evidence", []):
        if not isinstance(entry, dict):
            continue
        if entry.get("status") != "repo_local":
            continue
        ev_path_str = str(entry.get("path", "")).strip()
        if not ev_path_str:
            continue
        try:
            candidate = (repo_root / ev_path_str).resolve()
            candidate.relative_to(repo_root.resolve())
        except (ValueError, OSError):
            continue  # path escape — boundary validators handle this
        if not candidate.is_file():
            errors.append(
                format_error(
                    "REPO_LOCAL_EVIDENCE_PATH_NOT_FOUND",
                    claim_id,
                    path,
                    f"repo_local evidence path '{ev_path_str}' does not exist under repo root.",
                )
            )
    return errors


def external_verified_errors(claim: dict, path: Path) -> list[str]:
    claim_id = str(claim.get("claim_id", "<missing>"))
    errors: list[str] = []

    for entry in claim.get("evidence", []):
        if entry.get("status") != "external_verified":
            continue

        if not has_non_empty_source(entry) or not entry.get("sha256"):
            errors.append(
                format_error(
                    "EXTERNAL_VERIFIED_WITHOUT_SOURCE_OR_SHA256",
                    claim_id,
                    path,
                    "external_verified evidence requires source and sha256.",
                )
            )

    return errors


def semantic_errors_for_claim(claim: dict, path: Path, repo_root: Path | None = None) -> list[str]:
    claim_id = str(claim.get("claim_id", "<missing>"))
    verdict = str(claim.get("verdict", ""))
    statuses = evidence_statuses(claim)
    paths = evidence_paths(claim)
    evidence = claim.get("evidence", [])
    errors: list[str] = []

    has_missing_evidence = any(status == "missing_evidence" for status in statuses) or any(
        ".missing_evidence." in evidence_path for evidence_path in paths
    )
    has_strong_evidence = any(status in STRONG_EVIDENCE_STATUSES for status in statuses)

    if verdict == "PASS" and not has_strong_evidence and not has_missing_evidence:
        errors.append(
            format_error(
                "PASS_WITHOUT_STRONG_EVIDENCE",
                claim_id,
                path,
                "PASS requires at least one strong evidence status: repo_local, ci_artifact, external_verified, or derived_from_auditor_output.",
            )
        )

    if has_missing_evidence and verdict == "PASS":
        errors.append(
            format_error(
                "PASS_WITH_MISSING_EVIDENCE",
                claim_id,
                path,
                "Missing-evidence entries or *.MISSING_EVIDENCE.* paths cannot support PASS; use MISSING_EVIDENCE or CLAIM_NOT_PROVEN.",
            )
        )

    elif has_missing_evidence and verdict not in MISSING_EVIDENCE_ALLOWED_VERDICTS:
        errors.append(
            format_error(
                "MISSING_EVIDENCE_WITH_INVALID_VERDICT",
                claim_id,
                path,
                "Missing-evidence entries require verdict MISSING_EVIDENCE or CLAIM_NOT_PROVEN.",
            )
        )

    errors.extend(external_verified_errors(claim, path))

    if repo_root is not None:
        errors.extend(repo_local_existence_errors(claim, path, repo_root))

    if verdict == "PASS" and statuses and set(statuses) == {"external_unverified"}:
        errors.append(
            format_error(
                "PASS_WITH_EXTERNAL_UNVERIFIED_ONLY",
                claim_id,
                path,
                "external_unverified evidence alone cannot justify PASS.",
            )
        )

    if is_testcount_claim(claim) and not any(any(hint in evidence_path for hint in TEST_OUTPUT_HINTS) for evidence_path in paths):
        errors.append(
            format_error(
                "TESTCOUNT_WITHOUT_TEST_OUTPUT",
                claim_id,
                path,
                "Quantitative test-result claims require evidence paths that point to test output artifacts.",
            )
        )

    if is_make_validate_claim(claim):
        has_command_output_path = any(any(hint in evidence_path for hint in MAKE_VALIDATE_PATH_HINTS) for evidence_path in paths)
        commands = [str(entry.get("command", "")) for entry in evidence]
        has_make_validate_command = any("make validate" in command.lower() for command in commands if command)

        if not has_command_output_path:
            errors.append(
                format_error(
                    "MAKE_VALIDATE_WITHOUT_COMMAND_OUTPUT",
                    claim_id,
                    path,
                    "make validate claims require a make-validate output artifact path.",
                )
            )
        elif commands and not has_make_validate_command:
            errors.append(
                format_error(
                    "MAKE_VALIDATE_WITH_COMMAND_MISMATCH",
                    claim_id,
                    path,
                    "Evidence command metadata is present but does not contain 'make validate'.",
                )
            )

        if verdict == "PASS" and not any(entry.get("exit_code") == 0 for entry in evidence):
            errors.append(
                format_error(
                    "MAKE_VALIDATE_PASS_WITHOUT_EXIT_ZERO",
                    claim_id,
                    path,
                    "PASS make validate claims require evidence with exit_code: 0.",
                )
            )

    if is_ci_claim(claim) and verdict == "PASS":
        has_ci_status = any(status in {"ci_artifact", "external_verified"} for status in statuses)
        has_ci_path = any(any(hint in evidence_path for hint in CI_PATH_HINTS) for evidence_path in paths)
        if not (has_ci_status or has_ci_path):
            errors.append(
                format_error(
                    "CI_PASS_WITHOUT_CI_EVIDENCE",
                    claim_id,
                    path,
                    "PASS CI claims require CI-native evidence such as ci_artifact, external_verified, or CI output paths.",
                )
            )

    return errors


def validate_file(path: Path, validator: Draft202012Validator, repo_root: Path | None = None) -> tuple[int, list[str]]:
    effective_root = repo_root if repo_root is not None else REPO_ROOT
    try:
        data = load_yaml(path)
    except (FileNotFoundError, ValueError) as exc:
        return 2, [f"ERROR path={display_path(path)}: {exc}"]

    schema_errors = validate_schema(validator, data, path)
    if schema_errors:
        return 2, schema_errors

    errors: list[str] = []
    for claim in data.get("claims", []):
        errors.extend(semantic_errors_for_claim(claim, path, repo_root=effective_root))

    if errors:
        return 1, errors
    return 0, []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate semantic claim-evidence rules for run evidence packs")
    parser.add_argument("paths", nargs="+", help="YAML files to validate")
    args = parser.parse_args(argv)

    try:
        validator = load_schema_validator()
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        return 2

    highest_exit_code = 0
    for raw_path in args.paths:
        path = Path(raw_path)
        if not path.is_absolute():
            path = (REPO_ROOT / path).resolve()

        exit_code, errors = validate_file(path, validator)
        highest_exit_code = max(highest_exit_code, exit_code)
        for error in errors:
            print(error)

    return highest_exit_code


if __name__ == "__main__":
    sys.exit(main())