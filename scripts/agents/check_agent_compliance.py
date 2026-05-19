#!/usr/bin/env python3
"""Fast agent compliance guard.

Two rules, < 2 s runtime, designed as a pre-commit / pre-push companion to
the full ``make validate`` pipeline.

Rule 1 — Canonical-source protection
    The four canonical control documents are hand-maintained. An agent that
    touches them without an explicit override is in violation of
    ``AGENTS.md`` and ``.vibe/constraints.yml:canonical-sources-immutable-by-agents``.

Rule 2 — Generated-artifact protection
    Paths declared in ``.vibe/generated-artifacts.yml`` carry
    ``enforcement: [..., no_manual_edit]``. Manual edits violate
    ``AGENTS.md`` and ``.vibe/constraints.yml:no-manual-edit-generated``.

The script reads protected paths from canonical sources so it stays in
sync without duplicating policy. It is intentionally additive and never
modifies repo state.

Exit codes
    0 — no violations (or only violations explicitly allowed via flags)
    1 — at least one violation
    2 — invocation / environment error
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

try:
    import yaml
except ImportError:  # pragma: no cover - dependency surface
    print(
        "error: PyYAML is required. Install with: python3 -m pip install pyyaml",
        file=sys.stderr,
    )
    sys.exit(2)


REPO_ROOT = Path(__file__).resolve().parents[2]

# Canonical control documents. Source: AGENTS.md → "Handgepflegte
# Steuerungsdokumente"; agent-policy.yaml → canonical_sources.
CANONICAL_PATHS: frozenset[str] = frozenset(
    {
        "repo.meta.yaml",
        "AGENTS.md",
        "agent-policy.yaml",
        ".vibe/pr-scope-policy.yml",
    }
)


@dataclass(frozen=True)
class Violation:
    """A single rule violation with rule-grounded context."""

    path: str
    rule: str
    message: str
    reference: str

    def format(self) -> str:
        return (
            f"  - [{self.rule}] {self.path}\n"
            f"      {self.message}\n"
            f"      ref: {self.reference}"
        )


def load_generated_paths(repo_root: Path) -> list[str]:
    """Return the path patterns of all generated artifacts.

    Combines two canonical sources:
        - ``.vibe/generated-artifacts.yml`` (v2 contract, per-artifact entries)
        - ``agent-policy.yaml`` (``generated_artifacts.paths`` glob list)

    Falls back to the three top-level prefixes documented in ``AGENTS.md``
    if both files are missing — we never want this guard to silently let
    everything through.
    """
    fallback = [
        "docs/_generated/",
        "exports/",
        ".cursor/rules/",
    ]
    paths: list[str] = []

    contract = repo_root / ".vibe" / "generated-artifacts.yml"
    if contract.is_file():
        data = yaml.safe_load(contract.read_text(encoding="utf-8")) or {}
        for entry in data.get("artifacts") or []:
            if isinstance(entry, dict):
                path = entry.get("path")
                if isinstance(path, str) and path:
                    paths.append(path)

    policy = repo_root / "agent-policy.yaml"
    if policy.is_file():
        data = yaml.safe_load(policy.read_text(encoding="utf-8")) or {}
        for glob in (data.get("generated_artifacts") or {}).get("paths") or []:
            if isinstance(glob, str) and glob:
                # Normalize trailing /* → directory prefix.
                normalized = glob.rstrip("*").rstrip("/")
                if normalized:
                    paths.append(normalized + "/")

    if not paths:
        return fallback
    return _dedup(paths)


def changed_files(base: str | None, staged: bool) -> list[str]:
    """Return the list of files changed against ``base`` or the index."""
    if staged:
        cmd = ["git", "diff", "--name-only", "--cached"]
    elif base:
        cmd = ["git", "diff", "--name-only", base]
    else:
        # Default: everything that differs from HEAD (staged + unstaged +
        # untracked tracked-by-rename). Include untracked separately.
        tracked = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.splitlines()
        untracked = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.splitlines()
        return _dedup([line.strip() for line in (*tracked, *untracked) if line.strip()])

    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return _dedup(
        [line.strip() for line in result.stdout.splitlines() if line.strip()]
    )


def _dedup(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for v in values:
        if v not in seen:
            seen.add(v)
            out.append(v)
    return out


def _path_matches(file_path: str, pattern: str) -> bool:
    """Match a changed file against a contract path pattern.

    Patterns may be a literal file path (``repo.meta.yaml``) or a directory
    prefix (``docs/_generated/``).
    """
    if pattern.endswith("/"):
        return file_path == pattern.rstrip("/") or file_path.startswith(pattern)
    return file_path == pattern


def check_canonical(
    paths: Iterable[str], allowed: bool
) -> list[Violation]:
    if allowed:
        return []
    violations: list[Violation] = []
    for p in paths:
        if p in CANONICAL_PATHS:
            violations.append(
                Violation(
                    path=p,
                    rule="canonical-source",
                    message=(
                        "Canonical control document — hand-maintained by "
                        "maintainers only. Agent edits are forbidden."
                    ),
                    reference=(
                        "AGENTS.md → 'Handgepflegte Steuerungsdokumente'; "
                        ".vibe/constraints.yml#canonical-sources-immutable-by-agents"
                    ),
                )
            )
    return violations


def check_generated(
    paths: Iterable[str],
    generated_patterns: Iterable[str],
    allowed: bool,
) -> list[Violation]:
    if allowed:
        return []
    patterns = list(generated_patterns)
    violations: list[Violation] = []
    for p in paths:
        for pattern in patterns:
            if _path_matches(p, pattern):
                violations.append(
                    Violation(
                        path=p,
                        rule="generated-artifact",
                        message=(
                            "Generated artifact — must be produced by its "
                            "generator (see .vibe/generated-artifacts.yml). "
                            "Re-run 'make generate' instead of editing manually."
                        ),
                        reference=(
                            "AGENTS.md → 'Generierte Artefakte'; "
                            ".vibe/constraints.yml#no-manual-edit-generated"
                        ),
                    )
                )
                break
    return violations


def run_checks(
    *,
    repo_root: Path,
    paths: list[str],
    allow_canonical: bool,
    allow_generated: bool,
) -> list[Violation]:
    generated_patterns = load_generated_paths(repo_root)
    return [
        *check_canonical(paths, allowed=allow_canonical),
        *check_generated(paths, generated_patterns, allowed=allow_generated),
    ]


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Fast agent compliance guard. Detects edits to canonical "
            "control documents and generated artifacts."
        ),
    )
    parser.add_argument(
        "--base",
        default=None,
        help=(
            "Git ref to diff against (e.g. 'origin/main'). "
            "Default: working tree vs HEAD (staged + unstaged + untracked)."
        ),
    )
    parser.add_argument(
        "--staged",
        action="store_true",
        help="Check only files staged for commit.",
    )
    parser.add_argument(
        "--paths",
        nargs="+",
        default=None,
        help="Explicit list of paths to check (overrides git diff).",
    )
    parser.add_argument(
        "--allow-canonical",
        action="store_true",
        help=(
            "Allow changes to canonical control documents. "
            "Maintainers only — agents must NOT pass this flag."
        ),
    )
    parser.add_argument(
        "--allow-generated",
        action="store_true",
        help=(
            "Allow changes to generated artifacts. Use only when the change "
            "is the legitimate output of running its generator."
        ),
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress success message (still prints violations).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    if args.paths is not None:
        paths = _dedup([p.strip() for p in args.paths if p and p.strip()])
    else:
        try:
            paths = changed_files(args.base, args.staged)
        except subprocess.CalledProcessError as exc:
            print(f"error: git diff failed: {exc}", file=sys.stderr)
            return 2

    violations = run_checks(
        repo_root=REPO_ROOT,
        paths=paths,
        allow_canonical=args.allow_canonical,
        allow_generated=args.allow_generated,
    )

    if violations:
        print("agent-check: FAILED", file=sys.stderr)
        print(f"  scope: {len(paths)} file(s) inspected", file=sys.stderr)
        print(f"  violations: {len(violations)}", file=sys.stderr)
        for v in violations:
            print(v.format(), file=sys.stderr)
        print(
            "\nIf this change is legitimate (e.g. running a generator), "
            "use the matching --allow-* flag. Otherwise: STOP and report "
            "the conflict per agent-policy.yaml#conflict_resolution.",
            file=sys.stderr,
        )
        return 1

    if not args.quiet:
        print(f"agent-check: OK ({len(paths)} file(s) inspected)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
