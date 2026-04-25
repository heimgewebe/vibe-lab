#!/usr/bin/env python3
"""generate_artifact_taxonomy.py — Diagnostic global artifact taxonomy report.

Reads .vibe/artifact-taxonomy.yml and classifies every tracked file in the
repository. Writes:
  - docs/_generated/artifact-taxonomy.md
  - docs/_generated/artifact-taxonomy.json

Output is deterministic (sorted, no timestamps) and idempotent
(write_if_changed). The report is non-blocking by design: unknown or
ambiguous files do not cause a hard failure. Only an invalid taxonomy
config aborts the script.
"""

from __future__ import annotations

import fnmatch
import json
import subprocess
import sys
from pathlib import Path
from typing import Callable

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required.", file=sys.stderr)
    raise SystemExit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TAXONOMY_FILE = REPO_ROOT / ".vibe" / "artifact-taxonomy.yml"
GENERATED_CONTRACT = REPO_ROOT / ".vibe" / "generated-artifacts.yml"
OUTPUT_MD = REPO_ROOT / "docs" / "_generated" / "artifact-taxonomy.md"
OUTPUT_JSON = REPO_ROOT / "docs" / "_generated" / "artifact-taxonomy.json"

# Reuse the docmeta path helpers
sys.path.insert(0, str(REPO_ROOT / "scripts" / "docmeta"))
from _paths import write_if_changed  # noqa: E402

SKIP_DIRS = frozenset({".git", ".cursor", ".venv", "venv", "node_modules", "__pycache__", "_archive"})

CLASSIFIED = "classified"
UNKNOWN = "unknown"
AMBIGUOUS = "ambiguous"
CONFLICT = "conflict"


def load_taxonomy() -> dict:
    if not TAXONOMY_FILE.exists():
        raise SystemExit(f"ERROR: missing taxonomy file {TAXONOMY_FILE}")
    try:
        data = yaml.safe_load(TAXONOMY_FILE.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise SystemExit(f"ERROR: invalid YAML in {TAXONOMY_FILE}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"ERROR: taxonomy root must be a mapping ({TAXONOMY_FILE})")
    rules = data.get("rules")
    if not isinstance(rules, list) or not rules:
        raise SystemExit(f"ERROR: taxonomy 'rules' must be a non-empty list ({TAXONOMY_FILE})")
    for idx, rule in enumerate(rules):
        if not isinstance(rule, dict) or "pattern" not in rule:
            raise SystemExit(f"ERROR: rules[{idx}] missing 'pattern' ({TAXONOMY_FILE})")
    return data


def load_generated_contract_artifacts() -> list[dict]:
    """Load artifact objects from the generated-artifact contract for cross-check.

    Returns a list of dicts (each has at minimum 'path'; optionally 'authority',
    'class', 'ci_policy'). Failures to load the contract are deliberately
    non-fatal here: the generated-artifact contract has its own blocking validator
    (validate_generated_artifacts_contract.py) which will surface real
    contract-level errors. The taxonomy report stays diagnostic/non-blocking,
    so we degrade gracefully and emit a stderr warning rather than aborting.
    """
    if not GENERATED_CONTRACT.exists():
        return []
    try:
        data = yaml.safe_load(GENERATED_CONTRACT.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        print(
            f"WARNING: could not parse {GENERATED_CONTRACT} for cross-check: {exc}",
            file=sys.stderr,
        )
        return []
    out: list[dict] = []
    for art in data.get("artifacts") or []:
        if isinstance(art, dict) and isinstance(art.get("path"), str):
            out.append(art)
    return out


def iter_repo_files(repo_root: Path) -> list[str]:
    """Return sorted list of repo-relative paths for all tracked files.

    Uses ``git ls-files`` to enumerate only committed/staged files, which
    guarantees determinism and prevents local scratch files or untracked
    dumps from leaking into the generated taxonomy report.
    """
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=repo_root,
            check=True,
            text=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"ERROR: git ls-files failed: {exc.stderr.strip()}") from exc

    files: list[str] = []
    for line in result.stdout.splitlines():
        path = line.strip()
        if not path:
            continue
        parts = Path(path).parts
        if any(p in SKIP_DIRS for p in parts):
            continue
        files.append(path)
    return sorted(files)


def match_rules(rel_path: str, rules: list[dict]) -> list[dict]:
    """Return all rules whose pattern matches rel_path (for diagnostic use).

    Note: `classify_file` uses first-match-wins logic internally and does not
    call this function. It is retained for external callers or future diagnostic
    use (e.g. detecting inadvertent duplicate patterns in the taxonomy).
    """
    matched = []
    for rule in rules:
        pattern = rule.get("pattern")
        if not isinstance(pattern, str):
            continue
        if fnmatch.fnmatchcase(rel_path, pattern):
            matched.append(rule)
    return matched


def _is_catchall_pattern(pattern: str) -> bool:
    """Return True if a pattern is a broad catch-all (ends with /** or /**)."""
    return pattern.endswith("/**") or pattern == "**"


def classify_file(rel_path: str, rules: list[dict]) -> dict:
    """Classify a file using the first matching rule (ordered, first-match-wins).

    Rules in .vibe/artifact-taxonomy.yml are evaluated in order. Placing more
    specific patterns before general wildcards is the author's responsibility.
    No conflict is possible in a first-match-wins system — a later rule that
    also matches is simply shadowed by the earlier, more specific one.

    The returned dict includes `catchall_match: bool` so callers can distinguish
    files classified by a broad catch-all from files with a specific rule.
    """
    for rule in rules:
        pattern = rule.get("pattern")
        if not isinstance(pattern, str):
            continue
        if fnmatch.fnmatchcase(rel_path, pattern):
            return {
                "path": rel_path,
                "status": CLASSIFIED,
                "layer": rule.get("layer"),
                "kind": rule.get("kind"),
                "authority": rule.get("authority", "unknown"),
                "lifecycle": rule.get("lifecycle"),
                "enforcement": list(rule.get("enforcement") or []),
                "origin": rule.get("origin"),
                "matched_patterns": [pattern],
                "catchall_match": _is_catchall_pattern(pattern),
            }
    return {
        "path": rel_path,
        "status": UNKNOWN,
        "layer": None,
        "kind": None,
        "authority": "unknown",
        "lifecycle": None,
        "enforcement": [],
        "origin": None,
        "matched_patterns": [],
        "catchall_match": False,
    }


def _select_fallback_pattern(matched_patterns: list[str]) -> str:
    """Select the most relevant catch-all pattern from matched_patterns.

    Priority:
    1. First pattern that contains '**'
    2. First pattern in the list
    3. '<missing>' when the list is empty
    """
    for p in matched_patterns:
        if "**" in p:
            return p
    if matched_patterns:
        return matched_patterns[0]
    return "<missing>"


def _bucket_count(items: list[dict], key: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for item in items:
        val = item.get(key) or "<none>"
        out[str(val)] = out.get(str(val), 0) + 1
    return dict(sorted(out.items()))


def _bucket_count_by_func(items: list[dict], func: Callable[[dict], str]) -> dict[str, int]:
    """Like _bucket_count but derives the bucket key via an arbitrary function."""
    out: dict[str, int] = {}
    for item in items:
        val = func(item)
        out[val] = out.get(val, 0) + 1
    return dict(sorted(out.items()))


def _top_n(counter: dict[str, int], n: int = 10) -> dict[str, int]:
    """Return the top-n entries by count (descending). Ties are broken by key in ascending order."""
    sorted_items = sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))
    return {k: v for k, v in sorted_items[:n]}


def _build_residual_clusters(fallback_classified: list[dict]) -> list[dict]:
    """Build per-pattern residual cluster diagnostics.

    Expects items that are already filtered to status==classified AND
    catchall_match==True (i.e., the caller is responsible for pre-filtering).
    Groups those items by their selected fallback pattern and produces a
    diagnostic entry for each group with basename/parent-dir frequency data
    to guide future rule creation. Clusters are sorted by:
      1. high_risk_count descending
      2. total descending
      3. matched_pattern ascending
    """
    groups: dict[str, list[dict]] = {}
    for item in fallback_classified:
        pattern = _select_fallback_pattern(item.get("matched_patterns") or [])
        if pattern not in groups:
            groups[pattern] = []
        groups[pattern].append(item)

    clusters = []
    for pattern, items in groups.items():
        basename_counter: dict[str, int] = {}
        parent_counter: dict[str, int] = {}
        high_risk = 0
        for item in items:
            if _is_high_risk_fallback(item):
                high_risk += 1
            path = item["path"]
            basename = Path(path).name
            parent = str(Path(path).parent)
            basename_counter[basename] = basename_counter.get(basename, 0) + 1
            parent_counter[parent] = parent_counter.get(parent, 0) + 1
        clusters.append(
            {
                "matched_pattern": pattern,
                "total": len(items),
                "high_risk_count": high_risk,
                "top_basenames": _top_n(basename_counter),
                "top_parent_dirs": _top_n(parent_counter),
            }
        )
    clusters.sort(key=lambda c: (-c["high_risk_count"], -c["total"], c["matched_pattern"]))
    return clusters


def _enforcement_count(items: list[dict]) -> dict[str, int]:
    out: dict[str, int] = {}
    for item in items:
        for tag in item.get("enforcement") or []:
            out[tag] = out.get(tag, 0) + 1
    return dict(sorted(out.items()))


_FALLBACK_REVIEW_LAYER_PRIORITY = [
    "governance", "contract", "generated", "test", "export", "agent",
    "experiment", "docs", "catalog", "runtime", "capture", "archive",
]
_FALLBACK_REVIEW_AUTHORITY_PRIORITY = [
    "sovereign_source", "normative_contract", "schema_truth", "decision_record",
    "evidence_log", "generated_projection", "procedure_contract", "diagnostic_signal",
    "navigation_surface", "runtime_observation", "raw_capture", "historical_record",
    "unknown",
]


def _is_high_risk_fallback(item: dict) -> bool:
    """Heuristic: a fallback-classified artifact is high-risk when its layer or
    authority indicates governance-critical or immutable content.

    High-risk layers: governance, contract, generated, test, agent
    High-risk authorities: sovereign_source, normative_contract, schema_truth,
        decision_record, evidence_log, generated_projection

    Agent definitions are included because they control operational behaviour,
    not just documentation.
    """
    high_risk_layers = {"governance", "contract", "generated", "test", "agent"}
    high_risk_auths = {
        "sovereign_source",
        "normative_contract",
        "schema_truth",
        "decision_record",
        "evidence_log",
        "generated_projection",
    }
    return item.get("layer") in high_risk_layers or item.get("authority") in high_risk_auths


def fallback_review_sort_key(item: dict) -> tuple:
    """Sort key for the risk-weighted fallback review table.

    Order: high-risk first, then layer priority, then authority priority, then path.
    """
    layer = item.get("layer") or ""
    authority = item.get("authority") or ""
    layer_idx = (
        _FALLBACK_REVIEW_LAYER_PRIORITY.index(layer)
        if layer in _FALLBACK_REVIEW_LAYER_PRIORITY
        else len(_FALLBACK_REVIEW_LAYER_PRIORITY)
    )
    auth_idx = (
        _FALLBACK_REVIEW_AUTHORITY_PRIORITY.index(authority)
        if authority in _FALLBACK_REVIEW_AUTHORITY_PRIORITY
        else len(_FALLBACK_REVIEW_AUTHORITY_PRIORITY)
    )
    # high-risk sorts first: False < True, so negate the boolean
    return (not _is_high_risk_fallback(item), layer_idx, auth_idx, item.get("path", ""))


def build_report(classifications: list[dict], generated_artifacts: list[dict]) -> dict:
    classified = [c for c in classifications if c["status"] == CLASSIFIED]
    unknown = [c for c in classifications if c["status"] == UNKNOWN]
    ambiguous = [c for c in classifications if c["status"] == AMBIGUOUS]
    conflict = [c for c in classifications if c["status"] == CONFLICT]
    # fallback_classified: classified files matched by a broad catch-all (/**) rule.
    # Filtered from `classified` (status == "classified") so that unknown/ambiguous/conflict
    # items with catchall_match=True (theoretically impossible today but guarded against)
    # never inflate the fallback_share metric.
    fallback_classified = [c for c in classified if c.get("catchall_match")]

    # --- fallback share metrics -----------------------------------------------
    classified_total = len(classified)
    fallback_count = len(fallback_classified)
    fallback_share = fallback_count / classified_total if classified_total else 0.0
    fallback_threshold = 0.5
    fallback_threshold_status = "warning" if fallback_share > fallback_threshold else "ok"

    high_risk_authorities = {
        "sovereign_source",
        "normative_contract",
        "schema_truth",
        "evidence_log",
        "decision_record",
    }
    high_risk = sorted(
        (c for c in classifications if c.get("authority") in high_risk_authorities),
        key=lambda c: c["path"],
    )

    cross = []
    for art in sorted(generated_artifacts, key=lambda a: a.get("path", "")):
        path = art["path"]
        contract_authority = art.get("authority")
        match = next(
            (c for c in classifications if c["path"] == path or c["path"].startswith(path)),
            None,
        )
        taxonomy_authority = (match or {}).get("authority")
        authority_mismatch = (
            match is not None
            and contract_authority is not None
            and taxonomy_authority != contract_authority
        )
        cross.append(
            {
                "generated_artifact_path": path,
                "contract_authority": contract_authority,
                "matched_in_taxonomy": match is not None,
                "taxonomy_layer": (match or {}).get("layer"),
                "taxonomy_authority": taxonomy_authority,
                "authority_mismatch": authority_mismatch,
            }
        )

    transition_risks = []
    for c in classifications:
        if c.get("authority") == "evidence_log" and "no_rewrite" not in (c.get("enforcement") or []):
            transition_risks.append(
                {
                    "path": c["path"],
                    "risk": "evidence_log without no_rewrite enforcement",
                }
            )

    return {
        "summary": {
            "total": len(classifications),
            "classified": len(classified),
            "fallback_classified": fallback_count,
            "fallback_share": fallback_share,
            "fallback_threshold": fallback_threshold,
            "fallback_threshold_status": fallback_threshold_status,
            "unknown": len(unknown),
            "ambiguous": len(ambiguous),
            "conflict": len(conflict),
            "by_layer": _bucket_count(classifications, "layer"),
            "by_authority": _bucket_count(classifications, "authority"),
            "by_lifecycle": _bucket_count(classifications, "lifecycle"),
            "by_enforcement": _enforcement_count(classifications),
        },
        "fallback_summary": {
            "by_layer": _bucket_count(fallback_classified, "layer"),
            "by_authority": _bucket_count(fallback_classified, "authority"),
            "by_matched_pattern": _bucket_count_by_func(
                fallback_classified,
                lambda c: _select_fallback_pattern(c.get("matched_patterns") or []),
            ),
            "high_risk_count": sum(1 for c in fallback_classified if _is_high_risk_fallback(c)),
            "residual_clusters": _build_residual_clusters(fallback_classified),
        },
        "unknown_artifacts": [c["path"] for c in sorted(unknown, key=lambda x: x["path"])],
        "ambiguous_artifacts": [c["path"] for c in sorted(ambiguous, key=lambda x: x["path"])],
        "conflict_artifacts": [c["path"] for c in sorted(conflict, key=lambda x: x["path"])],
        "fallback_classified_artifacts": [c["path"] for c in sorted(fallback_classified, key=lambda x: x["path"])],
        "high_risk_artifacts": [c["path"] for c in high_risk],
        "generated_artifacts_cross_check": cross,
        "transition_risk_hints": transition_risks,
        "classifications": sorted(classifications, key=lambda c: c["path"]),
    }


def render_markdown(report: dict) -> str:
    lines: list[str] = []
    lines.append("---")
    lines.append("status: derived")
    lines.append("canonicality: derived")
    lines.append("authority: diagnostic_signal")
    lines.append("note: \"Generated by scripts/docmeta/generate_artifact_taxonomy.py — do not edit manually.\"")
    lines.append("---")
    lines.append("")
    lines.append("# Artifact Taxonomy (Diagnostic)")
    lines.append("")
    lines.append(
        "Diagnostic, non-blocking. Classifies all tracked repository artifacts "
        "according to `.vibe/artifact-taxonomy.yml`."
    )
    lines.append("")

    s = report["summary"]
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- total: {s['total']}")
    lines.append(f"- classified: {s['classified']}")
    lines.append(f"  - of which fallback_classified (catch-all rule): {s['fallback_classified']}")
    classified_total = s["classified"]
    fallback_count = s["fallback_classified"]
    share_pct = s["fallback_share"] * 100
    threshold_pct = s["fallback_threshold"] * 100
    if classified_total == 0:
        share_display = f"{share_pct:.1f}% (0 classified)"
    else:
        share_display = f"{share_pct:.1f}% ({fallback_count} / {classified_total})"
    threshold_display = f"{threshold_pct:.1f}% — {s['fallback_threshold_status']}"
    lines.append(f"  - fallback_share: {share_display}")
    lines.append(f"  - fallback_threshold: {threshold_display}")
    lines.append("")
    lines.append(
        "Fallback classifications come from broad catch-all rules. "
        "They are valid diagnostic classifications, but lower confidence than specific path rules."
    )
    lines.append(f"- unknown: {s['unknown']}")
    lines.append(f"- ambiguous: {s['ambiguous']}")
    lines.append(f"- conflict: {s['conflict']}")
    lines.append("")

    def _table(name: str, mapping: dict[str, int]) -> None:
        lines.append(f"### By {name}")
        lines.append("")
        if not mapping:
            lines.append("_none_")
            lines.append("")
            return
        lines.append(f"| {name} | count |")
        lines.append("| --- | ---: |")
        for k in sorted(mapping):
            lines.append(f"| {k} | {mapping[k]} |")
        lines.append("")

    _table("layer", s["by_layer"])
    _table("authority", s["by_authority"])
    _table("lifecycle", s["by_lifecycle"])
    _table("enforcement", s["by_enforcement"])

    def _list(title: str, items: list[str]) -> None:
        lines.append(f"## {title}")
        lines.append("")
        if not items:
            lines.append("_none_")
        else:
            for item in items:
                lines.append(f"- `{item}`")
        lines.append("")

    _list("Unknown artifacts", report["unknown_artifacts"])
    _list("Ambiguous artifacts", report["ambiguous_artifacts"])
    _list("Conflict artifacts", report["conflict_artifacts"])
    _list("Fallback classified artifacts (catch-all rule, low confidence)", report["fallback_classified_artifacts"])
    _list("High-risk artifacts", report["high_risk_artifacts"])

    # --- Risk-weighted fallback review section ---------------------------------
    fallback_items = [
        c for c in report["classifications"]
        if c.get("status") == "classified" and c.get("catchall_match")
    ]
    fallback_sorted = sorted(fallback_items, key=fallback_review_sort_key)[:20]

    lines.append("## Fallback classified: by matched pattern")
    lines.append("")
    lines.append(
        "Counts fallback-classified artifacts per catch-all pattern. "
        "Shows which broad rules drive the fallback share."
    )
    lines.append("")
    by_pattern = report["fallback_summary"].get("by_matched_pattern", {})
    fallback_total = report["summary"]["fallback_classified"]
    if not by_pattern:
        lines.append("_none_")
        lines.append("")
    else:
        lines.append("| matched_pattern | count | share_of_fallback |")
        lines.append("| --- | ---: | ---: |")
        for pat, cnt in sorted(by_pattern.items(), key=lambda kv: (-kv[1], kv[0])):
            share = cnt / fallback_total if fallback_total else 0.0
            lines.append(f"| `{pat}` | {cnt} | {share:.1%} |")
        lines.append("")

    lines.append("## Residual fallback clusters")
    lines.append("")
    lines.append(
        "Diagnostic breakdown of catch-all fallback buckets (top 5, sorted by high_risk_count desc). "
        "Shows dominant file names and parent directories to guide targeted rule additions in a future PR."
    )
    lines.append("")
    residual_clusters = report["fallback_summary"].get("residual_clusters", [])
    if not residual_clusters:
        lines.append("_none_")
        lines.append("")
    else:
        lines.append("| matched_pattern | total | high_risk_count | top_basenames | top_parent_dirs |")
        lines.append("| --- | ---: | ---: | --- | --- |")
        for cluster in residual_clusters[:5]:
            basenames_str = ", ".join(
                f"{k}={v}" for k, v in cluster.get("top_basenames", {}).items()
            )
            parents_str = ", ".join(
                f"{k}={v}" for k, v in cluster.get("top_parent_dirs", {}).items()
            )
            lines.append(
                f"| `{cluster['matched_pattern']}` | {cluster['total']} | "
                f"{cluster['high_risk_count']} | {basenames_str or '-'} | {parents_str or '-'} |"
            )
        lines.append("")

    lines.append("## Fallback classified artifacts requiring review")
    lines.append("")
    lines.append(
        "Fallback classifications come from broad catch-all rules (low confidence). "
        "High-risk items are shown first. Max 20 rows; sorted by risk, layer, authority, then path."
    )
    lines.append("")
    if not fallback_sorted:
        lines.append("_none_")
        lines.append("")
    else:
        lines.append("| Path | Layer | Kind | Authority | Risk | Matched pattern |")
        lines.append("| ---- | ----- | ---- | --------- | ---- | --------------- |")
        for item in fallback_sorted:
            risk_label = "high" if _is_high_risk_fallback(item) else "low"
            matched = ", ".join(item.get("matched_patterns") or [])
            lines.append(
                f"| `{item['path']}` | {item.get('layer') or '-'} | "
                f"{item.get('kind') or '-'} | {item.get('authority') or '-'} | "
                f"{risk_label} | `{matched}` |"
            )
        lines.append("")

    lines.append("## Generated artifacts cross-check")
    lines.append("")
    cross = report["generated_artifacts_cross_check"]
    if not cross:
        lines.append("_none_")
        lines.append("")
    else:
        lines.append("| generated artifact | in taxonomy | contract authority | taxonomy authority | mismatch |")
        lines.append("| --- | :---: | --- | --- | :---: |")
        for row in cross:
            mismatch_flag = "⚠️" if row.get("authority_mismatch") else ""
            lines.append(
                f"| `{row['generated_artifact_path']}` | "
                f"{'✅' if row['matched_in_taxonomy'] else '❌'} | "
                f"{row.get('contract_authority') or '-'} | "
                f"{row['taxonomy_authority'] or '-'} | "
                f"{mismatch_flag} |"
            )
        lines.append("")

    lines.append("## Transition risk hints")
    lines.append("")
    risks = report["transition_risk_hints"]
    if not risks:
        lines.append("_none_")
    else:
        for risk in risks:
            lines.append(f"- `{risk['path']}`: {risk['risk']}")
    lines.append("")

    return "\n".join(lines) + "\n"


def main() -> int:
    taxonomy = load_taxonomy()
    rules = taxonomy["rules"]
    generated_artifacts = load_generated_contract_artifacts()

    files = iter_repo_files(REPO_ROOT)
    classifications = [classify_file(f, rules) for f in files]
    report = build_report(classifications, generated_artifacts)

    md = render_markdown(report)
    js = json.dumps(report, indent=2, sort_keys=True) + "\n"

    write_if_changed(OUTPUT_MD, md)
    write_if_changed(OUTPUT_JSON, js)

    print(
        f"✅ artifact taxonomy: total={report['summary']['total']}, "
        f"unknown={report['summary']['unknown']}, "
        f"ambiguous={report['summary']['ambiguous']}, "
        f"conflict={report['summary']['conflict']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
