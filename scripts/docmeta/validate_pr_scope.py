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


# ---------------------------------------------------------------------------
# Policy loading
# ---------------------------------------------------------------------------

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
    return policy


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


def check_size(
    path: Path,
    max_bytes: int,
    compiled_allowed_small: list[tuple[re.Pattern, str]],
) -> list[tuple[str, str]]:
    path_str = _norm(path)
    for pattern, _ in compiled_allowed_small:
        if pattern.search(path_str):
            return []
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
    A claim is a violation when verdict==PASS and every evidence entry with status repo_local
    resolves to the same file as the pack itself, with no other evidence entries present.
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
            candidate = Path(raw_path)
            if not candidate.is_absolute():
                candidate = REPO_ROOT / candidate
            if candidate.resolve() == pack_abs and status == "repo_local":
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


# ---------------------------------------------------------------------------
# Path collection
# ---------------------------------------------------------------------------

def _collect_repo_scan(policy: dict) -> list[Path]:
    artifact_roots = policy.get("scope", {}).get("artifact_roots", [])
    paths: list[Path] = []
    for root_name in artifact_roots:
        root_dir = REPO_ROOT / root_name
        if root_dir.is_dir():
            for p in root_dir.rglob("*"):
                if p.is_file():
                    paths.append(p)
    return paths


def _collect_changed_files(changed_files_path: Path) -> list[Path]:
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
        if p.is_file():
            paths.append(p)
    return paths


# ---------------------------------------------------------------------------
# Main validation pass
# ---------------------------------------------------------------------------

def validate(paths: list[Path], policy: dict) -> list[tuple[str, str]]:
    forbidden_raw = policy.get("forbidden_path_patterns", [])
    allowed_small_raw = policy.get("allowed_small_evidence_patterns", [])
    limits = policy.get("limits", {})
    max_bytes = int(limits.get("max_repo_local_evidence_bytes", 262144))
    self_obs_cfg = policy.get("self_observation", {})
    forbid_self_obs = self_obs_cfg.get("forbid_pass_claim_referencing_same_evidence_pack", True)

    compiled_forbidden = _compile_patterns(forbidden_raw)
    compiled_allowed_small = _compile_patterns(allowed_small_raw)

    violations: list[tuple[str, str]] = []
    seen: set[Path] = set()

    for path in paths:
        abs_path = path.resolve()
        if abs_path in seen:
            continue
        seen.add(abs_path)

        violations.extend(check_forbidden(path, compiled_forbidden))
        violations.extend(check_size(path, max_bytes, compiled_allowed_small))

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
        help="File with newline-separated paths to check (changed-files mode)",
    )
    args = parser.parse_args()

    policy = load_policy(args.policy)

    if args.changed_files is not None:
        paths = _collect_changed_files(args.changed_files)
    else:
        paths = _collect_repo_scan(policy)

    violations = validate(paths, policy)

    for _, msg in violations:
        print(msg)

    if violations:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
