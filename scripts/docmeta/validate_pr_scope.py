#!/usr/bin/env python3
"""validate_pr_scope.py — PR-Scope / Artifact-Boundary Guard.

Checks artifact paths under configured artifact_roots (repo scan) or against
a newline-separated list of changed files (changed-files mode) for:
  - forbidden file patterns (full diffs, raw dumps, transcripts, screenshots)
  - oversized repo-local evidence artefacts
  - evidence-pack self-observation (PASS verdict citing itself as sole evidence)

Exit codes:
  0 — no violations
  1 — scope/artifact rule violated
  2 — tool/parse/policy error
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError as exc:
    print(
        "ERROR: Missing PyYAML. Install with: pip install pyyaml",
        file=sys.stderr,
    )
    raise SystemExit(2) from exc

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_POLICY_PATH = REPO_ROOT / ".vibe" / "pr-scope-policy.yml"

EVIDENCE_PACK_NAMES = {"evidence-pack.yml", "evidence-pack.yaml"}

# Patterns whose content implies a diff/patch rule rather than a raw-dump rule.
_DIFF_MARKERS = ["diff", "patch"]


def _is_diff_pattern(pattern: str) -> bool:
    return any(m in pattern for m in _DIFF_MARKERS)


def _rule_id_for_forbidden(pattern: str) -> str:
    return "FORBIDDEN_FULL_DIFF_ARTIFACT" if _is_diff_pattern(pattern) else "FORBIDDEN_RAW_DUMP_ARTIFACT"


def _display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _is_under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


# ---------------------------------------------------------------------------
# Policy loading and validation
# ---------------------------------------------------------------------------

def _policy_err(msg: str, policy_path: Path) -> None:
    print(f"POLICY_PARSE_ERROR: {msg} in {policy_path}", file=sys.stderr)
    raise SystemExit(2)


def load_policy(policy_path: Path) -> dict:
    try:
        text = policy_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"POLICY_PARSE_ERROR: policy file not found: {policy_path}", file=sys.stderr)
        raise SystemExit(2)
    try:
        policy = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        print(f"POLICY_PARSE_ERROR: invalid YAML in {policy_path}: {exc}", file=sys.stderr)
        raise SystemExit(2)
    if not isinstance(policy, dict):
        print(
            f"POLICY_PARSE_ERROR: policy must be a YAML mapping, got {type(policy).__name__}",
            file=sys.stderr,
        )
        raise SystemExit(2)
    _validate_policy_types(policy, policy_path)
    return policy


def _validate_policy_types(policy: dict, policy_path: Path) -> None:
    scope = policy.get("scope", {})
    if not isinstance(scope, dict):
        _policy_err(f"scope must be a mapping, got {type(scope).__name__}", policy_path)

    artifact_roots = scope.get("artifact_roots", [])
    if not isinstance(artifact_roots, list):
        _policy_err(
            f"scope.artifact_roots must be a list, got {type(artifact_roots).__name__}",
            policy_path,
        )
    for i, root in enumerate(artifact_roots):
        if not isinstance(root, str):
            _policy_err(
                f"scope.artifact_roots[{i}] must be a string, got {type(root).__name__}",
                policy_path,
            )

    patterns = policy.get("forbidden_path_patterns", [])
    if not isinstance(patterns, list):
        _policy_err(
            f"forbidden_path_patterns must be a list, got {type(patterns).__name__}",
            policy_path,
        )
    for i, pat in enumerate(patterns):
        if not isinstance(pat, str):
            _policy_err(
                f"forbidden_path_patterns[{i}] must be a string, got {type(pat).__name__}",
                policy_path,
            )

    limits = policy.get("limits", {})
    if not isinstance(limits, dict):
        _policy_err(f"limits must be a mapping, got {type(limits).__name__}", policy_path)
    raw_limit = limits.get("max_repo_local_evidence_bytes", 262144)
    try:
        int(raw_limit)
    except (ValueError, TypeError):
        _policy_err(
            f"limits.max_repo_local_evidence_bytes must be an integer, got {raw_limit!r}",
            policy_path,
        )


def _compile_patterns(patterns: list) -> list[tuple[re.Pattern, str]]:
    compiled = []
    for pat in patterns:
        try:
            compiled.append((re.compile(pat, re.IGNORECASE), pat))
        except re.error as exc:
            print(f"POLICY_PARSE_ERROR: invalid regex '{pat}': {exc}", file=sys.stderr)
            raise SystemExit(2)
    return compiled


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def _norm(path: Path) -> str:
    return str(path).replace("\\", "/")


def check_forbidden(
    path: Path,
    compiled_forbidden: list[tuple[re.Pattern, str]],
) -> list[tuple[str, str]]:
    path_str = _norm(path)
    for pattern, raw_pat in compiled_forbidden:
        if pattern.search(path_str):
            rule_id = _rule_id_for_forbidden(raw_pat)
            return [(rule_id, f"{rule_id}: {_display(path)} (matched '{raw_pat}')")]
    return []


def check_size(path: Path, max_bytes: int) -> list[tuple[str, str]]:
    # File name does not exempt from the size limit; only the limit matters.
    try:
        size = path.stat().st_size
    except OSError:
        return []
    if size > max_bytes:
        msg = f"ARTIFACT_TOO_LARGE: {_display(path)} ({size} bytes > {max_bytes} limit)"
        return [("ARTIFACT_TOO_LARGE", msg)]
    return []


def check_self_observation(pack_path: Path) -> list[tuple[str, str]]:
    """Block any PASS claim in an evidence pack that references only itself as repo_local evidence.

    Checks the canonical run-evidence-pack.v1 structure: claims[].verdict + claims[].evidence.
    Relative evidence paths are resolved against pack_path.parent first, then REPO_ROOT,
    so evidence-pack.yml and ./evidence-pack.yml are correctly identified as self-references.
    """
    try:
        data = yaml.safe_load(pack_path.read_text(encoding="utf-8"))
    except Exception:
        return []
    if not isinstance(data, dict):
        return []
    claims = data.get("claims", [])
    if not isinstance(claims, list):
        return []
    pack_abs = pack_path.resolve()
    violations: list[tuple[str, str]] = []
    for claim in claims:
        if not isinstance(claim, dict) or claim.get("verdict") != "PASS":
            continue
        evidence_list = claim.get("evidence", [])
        if not isinstance(evidence_list, list) or not evidence_list:
            continue
        self_refs: list[str] = []
        other_refs: list[str] = []
        for item in evidence_list:
            if not isinstance(item, dict):
                continue
            raw_path = item.get("path", "")
            status = item.get("status", "")
            if not raw_path:
                continue
            is_self = _resolves_to(raw_path, pack_path, pack_abs)
            if is_self and status == "repo_local":
                self_refs.append(raw_path)
            else:
                other_refs.append(raw_path)
        if self_refs and not other_refs:
            claim_id = claim.get("claim_id", "<unknown>")
            violations.append(
                (
                    "EVIDENCE_SELF_OBSERVATION",
                    f"EVIDENCE_SELF_OBSERVATION: {_display(pack_path)} "
                    f"claim '{claim_id}' has PASS verdict with only self-referencing repo_local evidence",
                )
            )
    return violations


def _resolves_to(raw_path: str, pack_path: Path, pack_abs: Path) -> bool:
    """Return True if raw_path resolves to the same file as pack_abs.

    Tries pack_path.parent first (handles evidence-pack.yml, ./evidence-pack.yml),
    then REPO_ROOT (handles repo-relative paths like experiments/.../evidence-pack.yml).
    """
    candidate = Path(raw_path)
    if candidate.is_absolute():
        return candidate.resolve() == pack_abs
    # Relative: try parent directory of the pack first
    if (pack_path.parent / candidate).resolve() == pack_abs:
        return True
    # Fallback: repo-root-relative
    return (REPO_ROOT / candidate).resolve() == pack_abs


# ---------------------------------------------------------------------------
# Path collection
# ---------------------------------------------------------------------------

def _artifact_root_dirs(policy: dict) -> list[Path]:
    roots = policy.get("scope", {}).get("artifact_roots", [])
    return [REPO_ROOT / r for r in roots if isinstance(r, str)]


def _collect_repo_scan(policy: dict) -> list[Path]:
    paths: list[Path] = []
    for root_dir in _artifact_root_dirs(policy):
        if root_dir.is_dir():
            for p in root_dir.rglob("*"):
                if p.is_file():
                    paths.append(p)
    return sorted(paths)


def _collect_changed_files(changed_files_path: Path, artifact_root_dirs: list[Path]) -> list[Path]:
    """Return changed files that exist and fall under one of the artifact_roots."""
    try:
        text = changed_files_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"POLICY_PARSE_ERROR: cannot read changed-files '{changed_files_path}': {exc}", file=sys.stderr)
        raise SystemExit(2)
    paths: list[Path] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        p = Path(line)
        if not p.is_absolute():
            p = REPO_ROOT / p
        if not p.is_file():
            continue
        if artifact_root_dirs and not any(_is_under(p, root) for root in artifact_root_dirs):
            continue
        paths.append(p)
    return paths


# ---------------------------------------------------------------------------
# Main validation pass
# ---------------------------------------------------------------------------

def validate(paths: list[Path], policy: dict) -> list[tuple[str, str]]:
    forbidden_raw = policy.get("forbidden_path_patterns", [])
    limits = policy.get("limits", {})
    max_bytes = int(limits.get("max_repo_local_evidence_bytes", 262144))
    self_obs_cfg = policy.get("self_observation", {})
    forbid_self_obs = self_obs_cfg.get("forbid_pass_claim_referencing_same_evidence_pack", True)

    compiled_forbidden = _compile_patterns(forbidden_raw)

    violations: list[tuple[str, str]] = []
    seen: set[Path] = set()

    for path in paths:
        abs_path = path.resolve()
        if abs_path in seen:
            continue
        seen.add(abs_path)

        violations.extend(check_forbidden(path, compiled_forbidden))
        violations.extend(check_size(path, max_bytes))

        if forbid_self_obs and path.name in EVIDENCE_PACK_NAMES:
            violations.extend(check_self_observation(path))

    return violations


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="PR-Scope / Artifact-Boundary Guard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--policy",
        type=Path,
        default=DEFAULT_POLICY_PATH,
        metavar="PATH",
        help="Path to pr-scope-policy.yml (default: .vibe/pr-scope-policy.yml)",
    )
    parser.add_argument(
        "--changed-files",
        type=Path,
        default=None,
        dest="changed_files",
        metavar="PATH",
        help="File with newline-separated paths to check (changed-files mode; only artifact_roots are scanned)",
    )
    args = parser.parse_args()

    policy = load_policy(args.policy)

    if args.changed_files is not None:
        paths = _collect_changed_files(args.changed_files, _artifact_root_dirs(policy))
    else:
        paths = _collect_repo_scan(policy)

    violations = validate(paths, policy)

    for _, msg in violations:
        print(msg)

    if violations:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
