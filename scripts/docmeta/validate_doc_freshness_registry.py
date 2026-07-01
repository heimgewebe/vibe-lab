#!/usr/bin/env python3
"""Validate docs/doc-freshness-registry.yml.

This is a small Vibe-Lab-local surface check. It mirrors the parts of the
Lenskit doc-freshness registry contract that Vibe-Lab needs before a fresh dump
or claim-evidence map is generated:

- structural registry fields are present;
- tracked docs and evidence paths do not escape the repository;
- cited files exist;
- text/absent_text evidence resolves against current file contents.

It does not generate Lenskit artifacts and does not prove that registered claims
are true beyond their declared evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any

try:
    import yaml
except ModuleNotFoundError as exc:  # pragma: no cover - dependency guard
    raise SystemExit("PyYAML is required for doc-freshness registry validation") from exc

KIND = "lenskit.doc_freshness_registry"
VERSION = "1.0"
ALLOWED_TOP_LEVEL = {"kind", "version", "authority", "risk_class", "does_not_prove", "entries"}
ALLOWED_ENTRY_FIELDS = {
    "id",
    "doc",
    "locator",
    "claim",
    "status",
    "normative",
    "owner",
    "last_verified",
    "evidence",
    "notes",
}
ALLOWED_EVIDENCE_FIELDS = {"kind", "target", "implies"}
ALLOWED_STATUSES = {"none", "partial", "done", "stale", "historical"}
ALLOWED_EVIDENCE_KINDS = {"symbol", "file", "text", "absent_text", "proof", "test"}
ALLOWED_IMPLIES = {"done", "open"}


@dataclass(frozen=True)
class ValidationResult:
    errors: list[str]
    warnings: list[str]
    entries_checked: int

    @property
    def ok(self) -> bool:
        return not self.errors


def repo_root_from_here() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"registry must be a YAML mapping: {path}")
    return data


def _secure_path(repo_root: Path, raw: str) -> Path | None:
    if not isinstance(raw, str) or not raw.strip():
        return None
    candidate = (repo_root / raw.strip()).resolve()
    try:
        candidate.relative_to(repo_root)
    except ValueError:
        return None
    return candidate


def _split_target(target: str) -> tuple[str, str | None]:
    if "::" not in target:
        return target.strip(), None
    path, _, needle = target.partition("::")
    return path.strip(), needle


def _has_symbol(path: Path, needle: str) -> bool:
    text = path.read_text(encoding="utf-8", errors="replace")
    if path.suffix == ".py":
        import ast

        wanted = needle.split(".")[-1]
        try:
            tree = ast.parse(text)
        except SyntaxError:
            return wanted in text
        for node in ast.walk(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == wanted:
                    return True
    return needle in text


def _validate_top_level(data: dict[str, Any], errors: list[str]) -> None:
    unknown = sorted(set(data) - ALLOWED_TOP_LEVEL)
    for key in unknown:
        errors.append(f"<root>: unknown field: {key}")
    if data.get("kind") != KIND:
        errors.append(f"kind must be {KIND!r}")
    if str(data.get("version")) != VERSION:
        errors.append(f"version must be {VERSION!r}")
    if "entries" not in data:
        errors.append("entries is required")
    elif not isinstance(data["entries"], list):
        errors.append("entries must be a list")
    if "does_not_prove" in data:
        values = data["does_not_prove"]
        if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
            errors.append("does_not_prove must be a list of strings")


def _validate_evidence(repo_root: Path, entry_path: str, item: Any, errors: list[str]) -> None:
    if not isinstance(item, dict):
        errors.append(f"{entry_path}: evidence item must be a mapping")
        return
    for key in sorted(set(item) - ALLOWED_EVIDENCE_FIELDS):
        errors.append(f"{entry_path}: unknown evidence field: {key}")

    kind = item.get("kind")
    target = item.get("target")
    implies = item.get("implies")
    if kind not in ALLOWED_EVIDENCE_KINDS:
        errors.append(f"{entry_path}: invalid evidence kind: {kind!r}")
        return
    if not isinstance(target, str) or not target:
        errors.append(f"{entry_path}: target must be a non-empty string")
        return
    if implies is not None and implies not in ALLOWED_IMPLIES:
        errors.append(f"{entry_path}: invalid implies value: {implies!r}")

    rel, needle = _split_target(target)
    path = _secure_path(repo_root, rel)
    if path is None:
        errors.append(f"{entry_path}: target escapes repository root: {target}")
        return

    if kind in {"file", "proof", "test"}:
        if not path.is_file():
            errors.append(f"{entry_path}: missing file evidence: {rel}")
        return

    if kind in {"text", "absent_text", "symbol"} and not path.is_file():
        errors.append(f"{entry_path}: missing file for {kind} evidence: {rel}")
        return

    if kind in {"text", "absent_text", "symbol"} and needle is None:
        errors.append(f"{entry_path}: {kind} evidence requires '<path>::<needle>'")
        return

    assert needle is not None
    if kind == "symbol":
        if not _has_symbol(path, needle):
            errors.append(f"{entry_path}: symbol not found: {needle} in {rel}")
        return

    text = path.read_text(encoding="utf-8", errors="replace")
    present = needle in text
    if kind == "text" and not present:
        errors.append(f"{entry_path}: required text not found in {rel}: {needle!r}")
    elif kind == "absent_text" and present:
        errors.append(f"{entry_path}: forbidden text still present in {rel}: {needle!r}")


def validate_registry(repo_root: Path | None = None, registry_path: Path | None = None) -> ValidationResult:
    repo_root = (repo_root or repo_root_from_here()).resolve()
    registry_path = registry_path or repo_root / "docs" / "doc-freshness-registry.yml"
    errors: list[str] = []
    warnings: list[str] = []

    if not registry_path.is_file():
        return ValidationResult([f"registry missing: {registry_path}"], warnings, 0)

    try:
        data = _load_yaml(registry_path)
    except Exception as exc:
        return ValidationResult([f"failed to load registry: {exc}"], warnings, 0)

    _validate_top_level(data, errors)
    entries = data.get("entries") if isinstance(data.get("entries"), list) else []

    seen_ids: set[str] = set()
    for index, entry in enumerate(entries):
        entry_path = f"entries[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{entry_path}: entry must be a mapping")
            continue
        for key in sorted(set(entry) - ALLOWED_ENTRY_FIELDS):
            errors.append(f"{entry_path}: unknown field: {key}")
        for field in ("id", "doc", "claim", "status", "owner", "last_verified", "evidence"):
            if field not in entry:
                errors.append(f"{entry_path}: missing required field: {field}")

        entry_id = entry.get("id")
        if isinstance(entry_id, str):
            if entry_id in seen_ids:
                errors.append(f"{entry_path}: duplicate id: {entry_id}")
            seen_ids.add(entry_id)
        else:
            errors.append(f"{entry_path}: id must be a string")

        status = entry.get("status")
        if status not in ALLOWED_STATUSES:
            errors.append(f"{entry_path}: invalid status: {status!r}")
        if "normative" in entry and not isinstance(entry["normative"], bool):
            errors.append(f"{entry_path}: normative must be boolean when present")

        doc = entry.get("doc")
        if isinstance(doc, str):
            doc_path = _secure_path(repo_root, doc)
            if doc_path is None:
                errors.append(f"{entry_path}: doc path escapes repository root: {doc}")
            elif not doc_path.is_file():
                errors.append(f"{entry_path}: doc path missing: {doc}")
        elif "doc" in entry:
            errors.append(f"{entry_path}: doc must be a string")

        evidence = entry.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"{entry_path}: evidence must be a non-empty list")
            continue
        for evidence_index, item in enumerate(evidence):
            _validate_evidence(repo_root, f"{entry_path}.evidence[{evidence_index}]", item, errors)

    return ValidationResult(errors, warnings, len(entries))


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    repo_root = Path(argv[0]).resolve() if argv else repo_root_from_here()
    result = validate_registry(repo_root=repo_root)
    for warning in result.warnings:
        print(f"WARNING: {warning}")
    if result.errors:
        for error in result.errors:
            print(f"ERROR: {error}")
        print(f"❌ doc-freshness registry validation failed ({len(result.errors)} error(s)).")
        return 1
    print(f"✅ doc-freshness registry validation passed ({result.entries_checked} entrie(s)).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
