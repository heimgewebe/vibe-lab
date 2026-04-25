#!/usr/bin/env python3
"""resolve_generated_artifact_paths.py — Reads paths from .vibe/generated-artifacts.yml (v2).

The legacy bucket-based contract (canonical/derived/gated/exports/ephemeral)
has been replaced by an object-based v2 contract. Filters operate on artifact
attributes (class, ci_policy, commit_policy, activation, enforcement).

Usage:
  python3 scripts/docmeta/resolve_generated_artifact_paths.py --all
  python3 scripts/docmeta/resolve_generated_artifact_paths.py --class diagnostic_report
  python3 scripts/docmeta/resolve_generated_artifact_paths.py --class generated_projection
  python3 scripts/docmeta/resolve_generated_artifact_paths.py --ci-policy blocking
  python3 scripts/docmeta/resolve_generated_artifact_paths.py --ci-policy non_blocking
  python3 scripts/docmeta/resolve_generated_artifact_paths.py --ci-policy best_effort
  python3 scripts/docmeta/resolve_generated_artifact_paths.py --commit-policy commit_required
  python3 scripts/docmeta/resolve_generated_artifact_paths.py --activation gated
  python3 scripts/docmeta/resolve_generated_artifact_paths.py --enforcement no_manual_edit

Output: one path per line, deterministic and sorted.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print(
        "ERROR: PyYAML is required. Install with: python3 -m pip install PyYAML",
        file=sys.stderr,
    )
    raise SystemExit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONTRACT_FILE = REPO_ROOT / ".vibe" / "generated-artifacts.yml"

LEGACY_GROUPS = {"canonical", "derived", "gated", "exports", "ephemeral"}

KNOWN_CLASSES = {
    "generated_index",
    "diagnostic_report",
    "diagnostic_dry_run",
    "metric_report",
    "generated_projection",
    "ephemeral_trace",
}
KNOWN_CI_POLICIES = {"blocking", "non_blocking", "best_effort"}
KNOWN_COMMIT_POLICIES = {"commit_required", "optional", "do_not_commit"}
KNOWN_ACTIVATIONS = {"always", "gated", "on_demand"}
KNOWN_ENFORCEMENTS = {
    "ci_blocking",
    "non_blocking_diagnostic",
    "best_effort",
    "no_manual_edit",
    "review_required",
}


def _load_contract() -> dict:
    if not CONTRACT_FILE.exists():
        raise FileNotFoundError(f"Missing contract file: {CONTRACT_FILE}")
    data = yaml.safe_load(CONTRACT_FILE.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Invalid YAML root in {CONTRACT_FILE}")
    if data.get("schema_version") != "2.0.0":
        raise ValueError(
            f"Unsupported schema_version in {CONTRACT_FILE}: "
            f"{data.get('schema_version')!r} (expected '2.0.0')"
        )
    if data.get("contract") != "generated_artifacts":
        raise ValueError(
            f"Unexpected contract id in {CONTRACT_FILE}: {data.get('contract')!r}"
        )
    artifacts = data.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise ValueError(f"'artifacts' must be a non-empty list in {CONTRACT_FILE}")
    return data


def _matches(art: dict, args: argparse.Namespace) -> bool:
    if args.cls is not None and art.get("class") != args.cls:
        return False
    if args.ci_policy is not None and art.get("ci_policy") != args.ci_policy:
        return False
    if args.commit_policy is not None and art.get("commit_policy") != args.commit_policy:
        return False
    if args.activation is not None and art.get("activation") != args.activation:
        return False
    if args.enforcement is not None:
        enforcement = art.get("enforcement") or []
        if not isinstance(enforcement, list) or args.enforcement not in enforcement:
            return False
    return True


def _validate_filter_values(args: argparse.Namespace) -> None:
    if args.cls is not None and args.cls not in KNOWN_CLASSES:
        raise ValueError(
            f"Unknown class filter: {args.cls!r}. Known: {sorted(KNOWN_CLASSES)}"
        )
    if args.ci_policy is not None and args.ci_policy not in KNOWN_CI_POLICIES:
        raise ValueError(
            f"Unknown ci-policy filter: {args.ci_policy!r}. "
            f"Known: {sorted(KNOWN_CI_POLICIES)}"
        )
    if args.commit_policy is not None and args.commit_policy not in KNOWN_COMMIT_POLICIES:
        raise ValueError(
            f"Unknown commit-policy filter: {args.commit_policy!r}. "
            f"Known: {sorted(KNOWN_COMMIT_POLICIES)}"
        )
    if args.activation is not None and args.activation not in KNOWN_ACTIVATIONS:
        raise ValueError(
            f"Unknown activation filter: {args.activation!r}. "
            f"Known: {sorted(KNOWN_ACTIVATIONS)}"
        )
    if args.enforcement is not None and args.enforcement not in KNOWN_ENFORCEMENTS:
        raise ValueError(
            f"Unknown enforcement filter: {args.enforcement!r}. "
            f"Known: {sorted(KNOWN_ENFORCEMENTS)}"
        )


def _detect_legacy_positional(argv: list[str]) -> str | None:
    """Detect legacy positional bucket arguments.

    Skips tokens that follow a known flag (so that values like `--activation gated`
    are NOT misclassified as a legacy positional argument). Also skips inline
    flag values such as `--activation=gated`.
    """
    flags_with_value = {
        "--class",
        "--ci-policy",
        "--commit-policy",
        "--activation",
        "--enforcement",
    }
    skip_next = False
    for token in argv:
        if skip_next:
            skip_next = False
            continue
        if token.startswith("--"):
            name = token.split("=", 1)[0]
            if "=" not in token and name in flags_with_value:
                skip_next = True
            continue
        if token in LEGACY_GROUPS:
            return token
    return None


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    legacy = _detect_legacy_positional(argv)
    if legacy is not None:
        print(
            "ERROR: legacy generated artifact groups are no longer supported.\n"
            f"       Got positional argument {legacy!r}.\n"
            "       Use filters such as --class diagnostic_report or "
            "--ci-policy non_blocking.\n"
            "       Run with --help for the full list.",
            file=sys.stderr,
        )
        return 2

    parser = argparse.ArgumentParser(
        description="Resolve generated artifact paths from the v2 contract."
    )
    parser.add_argument("--all", action="store_true", help="List all artifact paths.")
    parser.add_argument("--class", dest="cls", default=None, help="Filter by class.")
    parser.add_argument("--ci-policy", dest="ci_policy", default=None, help="Filter by ci_policy.")
    parser.add_argument(
        "--commit-policy", dest="commit_policy", default=None, help="Filter by commit_policy."
    )
    parser.add_argument("--activation", dest="activation", default=None, help="Filter by activation.")
    parser.add_argument(
        "--enforcement",
        dest="enforcement",
        default=None,
        help="Filter for artifacts whose enforcement list contains the given value.",
    )
    args = parser.parse_args(argv)

    if not (
        args.all
        or args.cls
        or args.ci_policy
        or args.commit_policy
        or args.activation
        or args.enforcement
    ):
        parser.error(
            "no filter provided; use --all or one of "
            "--class/--ci-policy/--commit-policy/--activation/--enforcement"
        )

    try:
        _validate_filter_values(args)
        data = _load_contract()
    except (FileNotFoundError, ValueError, yaml.YAMLError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    artifacts = data["artifacts"]
    paths: list[str] = []
    for art in artifacts:
        if not isinstance(art, dict):
            print(f"ERROR: artifact entry is not a mapping: {art!r}", file=sys.stderr)
            return 1
        if args.all or _matches(art, args):
            path = art.get("path")
            if not isinstance(path, str) or not path:
                print(f"ERROR: artifact missing string 'path': {art!r}", file=sys.stderr)
                return 1
            paths.append(path)

    for path in sorted(set(paths)):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
