#!/usr/bin/env python3
"""validate_generated_artifacts_contract.py — Validate .vibe/generated-artifacts.yml v2.

Blocking validator. Enforces:
  - schema_version == "2.0.0" and contract == "generated_artifacts"
  - No legacy top-level buckets: canonical, derived, gated, exports, ephemeral
  - 'classes' present and complete relative to artifacts[].class
  - 'artifacts' is a non-empty list
  - Every artifact has the v2 required fields
  - Every artifact's enforcement contains 'no_manual_edit' unless explicitly
    justified via 'manual_edit_justification'
  - Every generated_projection has generator, derives_from, target_surface,
    deterministic: true, regenerable: true
  - Every ci_policy: blocking artifact has commit_policy: commit_required
  - No duplicate artifact path
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required.", file=sys.stderr)
    raise SystemExit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONTRACT_FILE = REPO_ROOT / ".vibe" / "generated-artifacts.yml"

LEGACY_BUCKETS = ("canonical", "derived", "gated", "exports", "ephemeral")

REQUIRED_ARTIFACT_FIELDS = (
    "path",
    "class",
    "authority",
    "origin",
    "lifecycle",
    "enforcement",
    "activation",
    "commit_policy",
    "ci_policy",
)

PROJECTION_REQUIRED_FIELDS = ("generator", "derives_from", "target_surface")


def validate(data: dict) -> list[str]:
    errors: list[str] = []

    if not isinstance(data, dict):
        return ["root must be a mapping"]

    if data.get("schema_version") != "2.0.0":
        errors.append(
            f"schema_version must be '2.0.0' (got {data.get('schema_version')!r})"
        )

    if data.get("contract") != "generated_artifacts":
        errors.append(
            f"contract must be 'generated_artifacts' (got {data.get('contract')!r})"
        )

    for bucket in LEGACY_BUCKETS:
        if bucket in data:
            errors.append(
                f"legacy top-level bucket '{bucket}' is not allowed in v2 contract"
            )
    if "generated_artifact_contract" in data:
        errors.append(
            "legacy 'generated_artifact_contract' top-level key is not allowed in v2 contract"
        )

    classes = data.get("classes")
    if not isinstance(classes, dict) or not classes:
        errors.append("'classes' must be a non-empty mapping")
        classes = {}

    artifacts = data.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        errors.append("'artifacts' must be a non-empty list")
        return errors

    seen_paths: set[str] = set()
    used_classes: set[str] = set()

    for idx, art in enumerate(artifacts):
        prefix = f"artifacts[{idx}]"
        if not isinstance(art, dict):
            errors.append(f"{prefix}: must be a mapping")
            continue

        for field in REQUIRED_ARTIFACT_FIELDS:
            if field not in art:
                errors.append(f"{prefix}: missing required field '{field}'")

        path = art.get("path")
        if isinstance(path, str) and path:
            if path in seen_paths:
                errors.append(f"{prefix}: duplicate artifact path '{path}'")
            seen_paths.add(path)
            prefix = f"artifacts[{idx}] (path={path})"

        cls = art.get("class")
        if isinstance(cls, str):
            used_classes.add(cls)
            if cls not in classes:
                errors.append(
                    f"{prefix}: unknown class '{cls}' (not declared in 'classes')"
                )

        enforcement = art.get("enforcement")
        if not isinstance(enforcement, list) or not enforcement:
            errors.append(f"{prefix}: 'enforcement' must be a non-empty list")
        else:
            if "no_manual_edit" not in enforcement and not art.get(
                "manual_edit_justification"
            ):
                errors.append(
                    f"{prefix}: 'enforcement' must include 'no_manual_edit' "
                    "unless 'manual_edit_justification' is provided"
                )

        ci_policy = art.get("ci_policy")
        commit_policy = art.get("commit_policy")
        if ci_policy == "blocking" and commit_policy != "commit_required":
            errors.append(
                f"{prefix}: ci_policy='blocking' requires commit_policy='commit_required' "
                f"(got commit_policy={commit_policy!r})"
            )

        if cls == "generated_projection":
            for field in PROJECTION_REQUIRED_FIELDS:
                if not art.get(field):
                    errors.append(
                        f"{prefix}: generated_projection missing required field '{field}'"
                    )
            if art.get("deterministic") is not True:
                errors.append(
                    f"{prefix}: generated_projection requires deterministic: true"
                )
            if art.get("regenerable") is not True:
                errors.append(
                    f"{prefix}: generated_projection requires regenerable: true"
                )

    return errors


def main() -> int:
    if not CONTRACT_FILE.exists():
        print(f"ERROR: missing contract file {CONTRACT_FILE}", file=sys.stderr)
        return 1
    try:
        data = yaml.safe_load(CONTRACT_FILE.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        print(f"ERROR: invalid YAML in {CONTRACT_FILE}: {exc}", file=sys.stderr)
        return 1

    errors = validate(data)
    if errors:
        print(
            f"❌ Generated-artifact contract validation failed ({CONTRACT_FILE}):",
            file=sys.stderr,
        )
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print(f"✅ Generated-artifact contract valid ({CONTRACT_FILE}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
