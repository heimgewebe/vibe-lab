#!/usr/bin/env python3
"""generate_orphans.py — Generiert docs/_generated/orphans.md.

Identifiziert Markdown-Dateien, die von keiner anderen Datei
über Frontmatter-Relationen referenziert werden.

Ausgabe: docs/_generated/orphans.md
"""

import re
import sys
from pathlib import Path

# Gemeinsame Pfad-Logik aus _paths.py
sys.path.insert(0, str(Path(__file__).parent))
from _paths import should_skip, write_if_changed, extract_frontmatter, resolve_relation_target  # noqa: E402

try:
    import yaml as _yaml
except ImportError:
    _yaml = None

POLICY_PATH = ".vibe/orphan-policy.yml"

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT = REPO_ROOT / "docs" / "_generated" / "orphans.md"

# Dokumente, die als Wurzeln behandelt werden und keine eingehenden Referenzen benötigen
ROOT_FILES = {
    "README.md",
    "CONTRIBUTING.md",
    "AGENTS.md",
    "docs/foundations/vision.md",
    "docs/foundations/repo-plan.md",
    "docs/index.md",
    "docs/masterplan.md",
    "docs/policies/privacy-and-ethics.md",
    "benchmarks/challenges/rest-api-v1.md",
    "benchmarks/challenges/kanban-board-v1.md",
    "benchmarks/challenges/legacy-refactoring-v1.md",
}


def collect_unreferenced(repo_root: Path) -> set[str]:
    """Return repo-relative paths of markdown files not referenced by any other file.

    Fragment-suffixes in targets (e.g. ``file.md#section``) are stripped before
    path resolution so that ``target.md`` is counted as referenced, not
    ``target.md#section`` (a non-existent path).
    Root files (README etc.) are excluded from the result.
    """
    all_docs: set[str] = set()
    referenced: set[str] = set()

    for md_file in sorted(repo_root.rglob("*.md")):
        if should_skip(md_file, repo_root, skip_generated=True):
            continue
        if "_template" in md_file.relative_to(repo_root).parts:
            continue

        rel_path = str(md_file.relative_to(repo_root))
        all_docs.add(rel_path)

        fm = extract_frontmatter(md_file)
        if fm is None or "relations" not in fm:
            continue

        for rel in fm.get("relations", []):
            if not isinstance(rel, dict):
                continue
            target = rel.get("target", "")
            if not isinstance(target, str) or target.startswith("#"):  # guard non-string YAML values
                continue
            resolved = resolve_relation_target(md_file, target, repo_root)
            if resolved is None:
                continue
            try:
                ref_path = str(resolved.relative_to(repo_root))
                referenced.add(ref_path)
            except ValueError:
                pass

    return all_docs - referenced - ROOT_FILES


def _path_matches(path: str, pattern: str) -> bool:
    """Match a POSIX repo path against a repo-root-anchored glob pattern.

    Always matches from the start of the repo-relative path (root-anchored via '^').
    This prevents suffix-style false positives where 'experiments/*/CONTEXT.md'
    could match 'tests/fixtures/experiments/run-001/CONTEXT.md'.

      - '*'   matches any sequence within a single path segment (no '/').
      - '**/' matches zero or more path segments each followed by '/':
              'exports/**/*.md' matches 'exports/file.md', 'exports/a/file.md',
              and 'exports/a/b/file.md'.
      - '**'  not followed by '/' matches any remaining content.
    """
    i = 0
    regex = "^"
    while i < len(pattern):
        if pattern[i: i + 2] == "**":
            i += 2
            if i < len(pattern) and pattern[i] == "/":
                regex += r"(?:[^/]+/)*"
                i += 1
            else:
                regex += r".*"
        elif pattern[i] == "*":
            regex += r"[^/]*"
            i += 1
        else:
            regex += re.escape(pattern[i])
            i += 1
    regex += "$"
    return bool(re.match(regex, path))


def load_orphan_policy(repo_root: Path) -> list[dict]:
    """Load expected-orphan rules from .vibe/orphan-policy.yml.

    Returns an empty list when the policy file does not exist.
    Raises ValueError when the structure is invalid or any entry has a
    missing, empty, or whitespace-only pattern/reason.
    """
    policy_file = repo_root / POLICY_PATH
    if not policy_file.exists():
        return []

    text = policy_file.read_text(encoding="utf-8")
    if _yaml is None:
        raise RuntimeError(f"pyyaml is required to load {POLICY_PATH}")

    try:
        data = _yaml.safe_load(text)
    except _yaml.YAMLError as exc:
        raise ValueError(f"{POLICY_PATH}: invalid YAML: {exc}") from exc
    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise ValueError(f"{POLICY_PATH}: top-level must be a YAML mapping, got {type(data).__name__}")

    version = data.get("schema_version")
    if version is not None and version != "0.1.0":
        raise ValueError(f"{POLICY_PATH}: unsupported schema_version {version!r} (expected '0.1.0')")

    if "expected_orphans" in data:
        rules_raw = data["expected_orphans"]
        if rules_raw is None:
            raise ValueError(f"{POLICY_PATH}: 'expected_orphans' must be a list, got null")
        if not isinstance(rules_raw, list):
            raise ValueError(
                f"{POLICY_PATH}: 'expected_orphans' must be a list, got {type(rules_raw).__name__}"
            )
    else:
        rules_raw = []

    validated: list[dict] = []
    for i, rule in enumerate(rules_raw):
        if not isinstance(rule, dict):
            raise ValueError(f"{POLICY_PATH}: entry {i} is not a mapping")
        pattern = rule.get("pattern", "")
        reason = rule.get("reason", "")
        if not isinstance(pattern, str) or not pattern.strip():
            raise ValueError(f"{POLICY_PATH}: entry {i} missing or empty 'pattern'")
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError(f"{POLICY_PATH}: entry {i} missing or empty 'reason'")
        validated.append({"pattern": pattern.strip(), "reason": reason.strip()})

    return validated


def classify_orphans(
    orphans: list[str], rules: list[dict]
) -> tuple[list[str], list[tuple[str, str]]]:
    """Split orphan paths into unexpected and expected lists.

    First matching rule wins. Both output lists are sorted alphabetically.
    Returns (unexpected_paths, [(path, reason), ...]).
    """
    unexpected: list[str] = []
    expected: list[tuple[str, str]] = []

    for path in sorted(orphans):
        matched_reason: str | None = None
        for rule in rules:
            if _path_matches(path, rule["pattern"]):
                matched_reason = rule["reason"]
                break
        if matched_reason is not None:
            expected.append((path, matched_reason))
        else:
            unexpected.append(path)

    return unexpected, expected


def main():
    try:
        rules = load_orphan_policy(REPO_ROOT)
    except (ValueError, RuntimeError) as exc:
        print(f"ERROR loading orphan policy: {exc}", file=sys.stderr)
        sys.exit(1)

    unexpected, expected = classify_orphans(collect_unreferenced(REPO_ROOT), rules)

    lines = [
        "<!-- GENERATED FILE — DO NOT EDIT MANUALLY -->",
        "<!-- Generated by generate_orphans.py -->",
        "",
        "# Unreferenced Documents",
        "",
        f"Unexpected orphans ({len(unexpected)} found):",
        "",
    ]

    if unexpected:
        for path in unexpected:
            lines.append(f"- `{path}`")
    else:
        lines.append("*No unexpected unreferenced documents found.*")

    lines.append("")
    lines.append(f"Expected orphans ({len(expected)} found):")
    lines.append("")

    if expected:
        for path, reason in expected:
            lines.append(f"- `{path}` — {reason}")
    elif rules:
        lines.append("*No expected unreferenced documents found.*")
    else:
        lines.append("*No orphan policy rules are configured.*")

    lines.append("")
    content = "\n".join(lines)
    written = write_if_changed(OUTPUT, content)
    status_sym = "✅" if written else "✔️ (unchanged)"
    print(
        f"{status_sym} Generated {OUTPUT.relative_to(REPO_ROOT)}"
        f" ({len(unexpected)} unexpected, {len(expected)} expected)"
    )


if __name__ == "__main__":
    main()
