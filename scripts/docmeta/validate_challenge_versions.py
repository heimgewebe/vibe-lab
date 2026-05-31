#!/usr/bin/env python3
"""validate_challenge_versions.py — AP-2 challenge-version validator pre-stage.

This validator makes benchmark challenges machine-readable version anchors and
checks that *explicitly comparative* Model-Lab decisions reference a known
challenge version. It is deliberately a pre-stage, not global enforcement:

* Challenge files under ``benchmarks/challenges/*.md`` must carry standardized
  frontmatter (``challenge_id``, ``version``, ``task_family``,
  ``expected_outputs``, ``evaluation_criteria``, ``known_confounders``) and the
  combined ``<challenge_id>-<version>`` id must match the filename.
* ``decision.yml`` files are only enforced when they explicitly opt in as
  Model-Lab / comparative decisions. Historical decisions without that opt-in
  are ignored so legacy experiments are never broken by this check.

No global ``challenge_version`` requirement is introduced for all decisions, and
``schemas/decision.schema.json`` is intentionally left untouched.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - tooling guard
    print("ERROR: pyyaml is required (pip install pyyaml).", file=sys.stderr)
    raise SystemExit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BENCHMARK_CHALLENGES = REPO_ROOT / "benchmarks" / "challenges"
EXPERIMENTS_ROOT = REPO_ROOT / "experiments"

FRONTMATTER_DELIM = "---"

# Required challenge frontmatter fields.
REQUIRED_CHALLENGE_FIELDS: tuple[str, ...] = (
    "title",
    "status",
    "canonicality",
    "challenge_id",
    "version",
    "task_family",
    "expected_outputs",
    "evaluation_criteria",
    "known_confounders",
)

# Non-empty string fields within the challenge frontmatter.
CHALLENGE_STRING_FIELDS: tuple[str, ...] = (
    "title",
    "status",
    "canonicality",
    "challenge_id",
    "version",
    "task_family",
)

# Non-empty list-of-non-empty-strings fields within the challenge frontmatter.
CHALLENGE_LIST_FIELDS: tuple[str, ...] = (
    "expected_outputs",
    "evaluation_criteria",
    "known_confounders",
)


@dataclass(frozen=True)
class ChallengeRegistry:
    """Index of known challenge versions discovered in the scanned paths."""

    versions: dict[str, Path]
    challenge_ids: dict[str, list[str]]
    errors: tuple[str, ...]


@dataclass(frozen=True)
class ValidationResult:
    checked_challenges: int
    checked_decisions: int
    activated_decisions: int
    errors: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.errors


def parse_frontmatter(path: Path) -> tuple[dict[str, object], str]:
    """Return (frontmatter_dict, body) for a Markdown file.

    Mirrors the lightweight frontmatter parsing used by sibling docmeta scripts.
    A missing or malformed frontmatter block yields an empty dict.
    """
    text = path.read_text(encoding="utf-8")
    if not text.startswith(FRONTMATTER_DELIM):
        return {}, text
    end = text.find(f"\n{FRONTMATTER_DELIM}", len(FRONTMATTER_DELIM))
    if end == -1:
        return {}, text
    raw = text[len(FRONTMATTER_DELIM):end]
    body = text[end + 1 + len(FRONTMATTER_DELIM):]
    data = yaml.safe_load(raw) or {}
    if not isinstance(data, dict):
        return {}, body
    return data, body


def load_yaml_file(path: Path) -> dict[str, object]:
    """Load a YAML/JSON document, returning {} when the top level is not a mapping."""
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def build_challenge_registry(paths: Iterable[Path]) -> ChallengeRegistry:
    """Build a registry of ``<challenge_id>-<version>`` ids from challenge files.

    Files that cannot form a combined id (missing/empty challenge_id or version)
    are skipped here; their detailed errors surface via ``validate_challenge_file``.
    """
    versions: dict[str, Path] = {}
    challenge_ids: dict[str, list[str]] = {}
    errors: list[str] = []

    for path in paths:
        try:
            data, _ = parse_frontmatter(path)
        except (OSError, yaml.YAMLError) as exc:
            errors.append(f"{path}: cannot parse challenge frontmatter: {exc}")
            continue

        challenge_id = data.get("challenge_id")
        version = data.get("version")
        if not (
            isinstance(challenge_id, str)
            and challenge_id.strip()
            and isinstance(version, str)
            and version.strip()
        ):
            continue

        challenge_id = challenge_id.strip()
        combined = f"{challenge_id}-{version.strip()}"
        if combined in versions and versions[combined] != path:
            errors.append(
                f"duplicate challenge version '{combined}': "
                f"{versions[combined]} and {path}"
            )
            continue
        versions[combined] = path
        challenge_ids.setdefault(challenge_id, []).append(combined)

    return ChallengeRegistry(
        versions=versions,
        challenge_ids=challenge_ids,
        errors=tuple(errors),
    )


def validate_challenge_file(path: Path) -> list[str]:
    """Validate a single benchmark challenge file's frontmatter."""
    errors: list[str] = []
    try:
        data, _ = parse_frontmatter(path)
    except (OSError, yaml.YAMLError) as exc:
        return [f"{path}: cannot parse challenge frontmatter: {exc}"]

    if not data:
        return [f"{path}: missing or empty frontmatter"]

    for field in REQUIRED_CHALLENGE_FIELDS:
        if field not in data:
            errors.append(f"{path}: missing required challenge field: {field}")

    for field in CHALLENGE_STRING_FIELDS:
        if field in data:
            value = data.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{path}: field '{field}' must be a non-empty string")

    for field in CHALLENGE_LIST_FIELDS:
        if field in data:
            value = data.get(field)
            if not isinstance(value, list) or not value:
                errors.append(
                    f"{path}: field '{field}' must be a non-empty list of strings"
                )
            elif any(not isinstance(item, str) or not item.strip() for item in value):
                errors.append(
                    f"{path}: field '{field}' entries must be non-empty strings"
                )

    challenge_id = data.get("challenge_id")
    version = data.get("version")
    if (
        isinstance(challenge_id, str)
        and challenge_id.strip()
        and isinstance(version, str)
        and version.strip()
    ):
        combined = f"{challenge_id.strip()}-{version.strip()}"
        if combined != path.stem:
            errors.append(
                f"{path}: combined challenge id '{combined}' does not match "
                f"filename stem '{path.stem}'"
            )

    return errors


def decision_requires_challenge_version(data: dict[str, object]) -> bool:
    """Return True only when a decision explicitly opts in as Model-Lab/comparative.

    Activation is intentionally narrow (exact values, not mere key presence) so
    historical decisions — including those that merely carry an unrelated
    ``comparability_scope`` string — are not retroactively enforced.
    """
    if not isinstance(data, dict):
        return False
    if data.get("model_lab_control") is True:
        return True
    if data.get("comparability_scope") == "model_lab":
        return True
    if data.get("decision_type") == "model_lab_comparison":
        return True
    if data.get("challenge_version_required") is True:
        return True
    return False


def _validate_activated_decision(
    path: Path, data: dict[str, object], registry: ChallengeRegistry
) -> list[str]:
    errors: list[str] = []

    challenge_version = data.get("challenge_version")
    if not isinstance(challenge_version, str) or not challenge_version.strip():
        errors.append(
            f"{path}: activated Model-Lab decision must set a non-empty "
            f"challenge_version"
        )
        return errors

    challenge_version = challenge_version.strip()
    if challenge_version not in registry.versions:
        known = ", ".join(sorted(registry.versions)) or "(none in scope)"
        errors.append(
            f"{path}: challenge_version '{challenge_version}' is not a known "
            f"challenge version (known: {known})"
        )
        return errors

    challenge_id = data.get("challenge_id")
    if isinstance(challenge_id, str) and challenge_id.strip():
        challenge_id = challenge_id.strip()
        belongs = challenge_version in registry.challenge_ids.get(challenge_id, [])
        if not (challenge_version.startswith(f"{challenge_id}-") or belongs):
            errors.append(
                f"{path}: challenge_version '{challenge_version}' does not match "
                f"challenge_id '{challenge_id}'"
            )

    return errors


def validate_decision_file(path: Path, registry: ChallengeRegistry) -> list[str]:
    """Validate a decision file, but only when it explicitly opts in.

    Non-activated decisions return no errors (they are ignored by design).
    """
    data = load_yaml_file(path)
    if not decision_requires_challenge_version(data):
        return []
    return _validate_activated_decision(path, data, registry)


def _is_challenge_path(path: Path) -> bool:
    return path.suffix == ".md" and "challenges" in path.parts


def _is_decision_path(path: Path) -> bool:
    return path.suffix in {".yml", ".yaml"} and (
        path.name in {"decision.yml", "decision.yaml"} or "decisions" in path.parts
    )


def _discover(paths: Iterable[Path]) -> tuple[list[Path], list[Path], list[Path]]:
    """Expand inputs into (challenge_files, decision_files, missing_paths).

    Directories are scanned recursively. Files are classified by location;
    explicitly passed files that don't match a location convention fall back to
    their suffix (``.md`` -> challenge, ``.yml``/``.yaml`` -> decision) so direct
    invocations on a single file work as expected.
    """
    challenges: set[Path] = set()
    decisions: set[Path] = set()
    missing: list[Path] = []

    for path in paths:
        if path.is_dir():
            for child in sorted(path.rglob("*")):
                if not child.is_file():
                    continue
                if _is_challenge_path(child):
                    challenges.add(child)
                elif _is_decision_path(child):
                    decisions.add(child)
        elif path.is_file():
            if _is_challenge_path(path):
                challenges.add(path)
            elif _is_decision_path(path):
                decisions.add(path)
            elif path.suffix == ".md":
                challenges.add(path)
            elif path.suffix in {".yml", ".yaml"}:
                decisions.add(path)
        else:
            missing.append(path)

    return sorted(challenges), sorted(decisions), missing


def validate_paths(paths: Iterable[Path]) -> ValidationResult:
    paths = [Path(p) for p in paths]
    challenges, decisions, missing = _discover(paths)

    errors: list[str] = [f"{path}: path does not exist" for path in missing]

    registry = build_challenge_registry(challenges)
    errors.extend(registry.errors)

    for challenge in challenges:
        errors.extend(validate_challenge_file(challenge))

    activated = 0
    for decision in decisions:
        try:
            data = load_yaml_file(decision)
        except (OSError, yaml.YAMLError) as exc:
            errors.append(f"{decision}: cannot parse decision file: {exc}")
            continue
        if not decision_requires_challenge_version(data):
            continue
        activated += 1
        errors.extend(_validate_activated_decision(decision, data, registry))

    return ValidationResult(
        checked_challenges=len(challenges),
        checked_decisions=len(decisions),
        activated_decisions=activated,
        errors=tuple(errors),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate benchmark challenge version metadata and opt-in Model-Lab "
            "decisions. Only explicitly comparative decisions are enforced."
        )
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help=(
            "Challenge files, decision files, or directories to scan "
            "(default: benchmarks/challenges + experiments/)."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    paths = args.paths or [BENCHMARK_CHALLENGES, EXPERIMENTS_ROOT]
    result = validate_paths(paths)

    for error in result.errors:
        print(f"ERROR: {error}", file=sys.stderr)

    print(
        "Challenge-version check: "
        f"challenges={result.checked_challenges}, "
        f"decisions={result.checked_decisions}, "
        f"activated={result.activated_decisions}, "
        f"errors={len(result.errors)}"
    )
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
