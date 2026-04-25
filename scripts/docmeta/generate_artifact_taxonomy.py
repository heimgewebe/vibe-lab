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
import sys
from pathlib import Path

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

SKIP_DIRS = frozenset({".git", ".github", ".cursor", ".venv", "venv", "node_modules", "__pycache__", "_archive"})

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


def load_generated_contract_paths() -> set[str]:
    if not GENERATED_CONTRACT.exists():
        return set()
    try:
        data = yaml.safe_load(GENERATED_CONTRACT.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return set()
    out: set[str] = set()
    for art in data.get("artifacts") or []:
        if isinstance(art, dict):
            p = art.get("path")
            if isinstance(p, str):
                out.add(p)
    return out


def iter_repo_files(repo_root: Path) -> list[str]:
    files: list[str] = []
    for path in repo_root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(repo_root)
        parts = rel.parts
        if any(p in SKIP_DIRS for p in parts):
            continue
        files.append(str(rel).replace("\\", "/"))
    return sorted(files)


def match_rules(rel_path: str, rules: list[dict]) -> list[dict]:
    matched = []
    for rule in rules:
        pattern = rule.get("pattern")
        if not isinstance(pattern, str):
            continue
        if fnmatch.fnmatchcase(rel_path, pattern):
            matched.append(rule)
    return matched


def classify_file(rel_path: str, rules: list[dict]) -> dict:
    matches = match_rules(rel_path, rules)
    if not matches:
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
        }

    primary = matches[0]
    distinct = {
        (m.get("layer"), m.get("kind"), m.get("authority"))
        for m in matches
    }

    status = CLASSIFIED
    if len(matches) > 1:
        # Ambiguous = multiple rules with identical classification semantics.
        # Conflict = multiple rules with diverging classification.
        if len(distinct) == 1:
            status = AMBIGUOUS
        else:
            status = CONFLICT

    return {
        "path": rel_path,
        "status": status,
        "layer": primary.get("layer"),
        "kind": primary.get("kind"),
        "authority": primary.get("authority", "unknown"),
        "lifecycle": primary.get("lifecycle"),
        "enforcement": list(primary.get("enforcement") or []),
        "origin": primary.get("origin"),
        "matched_patterns": [m.get("pattern") for m in matches],
    }


def _bucket_count(items: list[dict], key: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for item in items:
        val = item.get(key) or "<none>"
        out[str(val)] = out.get(str(val), 0) + 1
    return dict(sorted(out.items()))


def _enforcement_count(items: list[dict]) -> dict[str, int]:
    out: dict[str, int] = {}
    for item in items:
        for tag in item.get("enforcement") or []:
            out[tag] = out.get(tag, 0) + 1
    return dict(sorted(out.items()))


def build_report(classifications: list[dict], generated_paths: set[str]) -> dict:
    classified = [c for c in classifications if c["status"] != UNKNOWN]
    unknown = [c for c in classifications if c["status"] == UNKNOWN]
    ambiguous = [c for c in classifications if c["status"] == AMBIGUOUS]
    conflict = [c for c in classifications if c["status"] == CONFLICT]

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
    for path in sorted(generated_paths):
        match = next(
            (c for c in classifications if c["path"] == path or c["path"].startswith(path)),
            None,
        )
        cross.append(
            {
                "generated_artifact_path": path,
                "matched_in_taxonomy": match is not None,
                "taxonomy_layer": (match or {}).get("layer"),
                "taxonomy_authority": (match or {}).get("authority"),
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
            "unknown": len(unknown),
            "ambiguous": len(ambiguous),
            "conflict": len(conflict),
            "by_layer": _bucket_count(classifications, "layer"),
            "by_authority": _bucket_count(classifications, "authority"),
            "by_lifecycle": _bucket_count(classifications, "lifecycle"),
            "by_enforcement": _enforcement_count(classifications),
        },
        "unknown_artifacts": [c["path"] for c in sorted(unknown, key=lambda x: x["path"])],
        "ambiguous_artifacts": [c["path"] for c in sorted(ambiguous, key=lambda x: x["path"])],
        "conflict_artifacts": [c["path"] for c in sorted(conflict, key=lambda x: x["path"])],
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
    _list("High-risk artifacts", report["high_risk_artifacts"])

    lines.append("## Generated artifacts cross-check")
    lines.append("")
    cross = report["generated_artifacts_cross_check"]
    if not cross:
        lines.append("_none_")
        lines.append("")
    else:
        lines.append("| generated artifact | in taxonomy | layer | authority |")
        lines.append("| --- | :---: | --- | --- |")
        for row in cross:
            lines.append(
                f"| `{row['generated_artifact_path']}` | "
                f"{'✅' if row['matched_in_taxonomy'] else '❌'} | "
                f"{row['taxonomy_layer'] or '-'} | "
                f"{row['taxonomy_authority'] or '-'} |"
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
    generated_paths = load_generated_contract_paths()

    files = iter_repo_files(REPO_ROOT)
    classifications = [classify_file(f, rules) for f in files]
    report = build_report(classifications, generated_paths)

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
