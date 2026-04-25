#!/usr/bin/env python3
"""validate_artifact_taxonomy.py — Structural validator for .vibe/artifact-taxonomy.yml.

Validates that the taxonomy contract is structurally well-formed:
  - schema_version and contract fields present
  - layers is a non-empty list of strings
  - authorities is a non-empty list of strings
  - rules is a non-empty list of well-formed rule mappings
  - every rule has required fields (pattern, layer, kind, authority, lifecycle, enforcement, origin)
  - every rule.layer is in the declared layers list
  - every rule.authority is in the declared authorities list
  - every rule.enforcement is a list

Does NOT enforce that every repo file is classified (unknowns are expected
and are diagnostic/non-blocking). Hard fails only on config-level errors.
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
TAXONOMY_FILE = REPO_ROOT / ".vibe" / "artifact-taxonomy.yml"

REQUIRED_RULE_FIELDS = ("pattern", "layer", "kind", "authority", "lifecycle", "enforcement", "origin")


def validate(data: dict) -> list[str]:
    errors: list[str] = []

    if not isinstance(data, dict):
        return ["root must be a mapping"]

    if not data.get("schema_version"):
        errors.append("missing 'schema_version'")
    if data.get("contract") != "artifact_taxonomy":
        errors.append(
            f"contract must be 'artifact_taxonomy' (got {data.get('contract')!r})"
        )

    layers = data.get("layers")
    if not isinstance(layers, list) or not layers:
        errors.append("'layers' must be a non-empty list")
        valid_layers: set[str] = set()
    else:
        valid_layers = set()
        for i, lyr in enumerate(layers):
            if not isinstance(lyr, str) or not lyr.strip():
                errors.append(f"layers[{i}]: must be a non-empty string (got {lyr!r})")
            else:
                valid_layers.add(lyr)

    authorities = data.get("authorities")
    if not isinstance(authorities, list) or not authorities:
        errors.append("'authorities' must be a non-empty list")
        valid_authorities: set[str] = set()
    else:
        valid_authorities = set()
        for i, auth in enumerate(authorities):
            if not isinstance(auth, str) or not auth.strip():
                errors.append(f"authorities[{i}]: must be a non-empty string (got {auth!r})")
            else:
                valid_authorities.add(auth)

    rules = data.get("rules")
    if not isinstance(rules, list) or not rules:
        errors.append("'rules' must be a non-empty list")
        return errors

    for idx, rule in enumerate(rules):
        prefix = f"rules[{idx}]"
        if not isinstance(rule, dict):
            errors.append(f"{prefix}: must be a mapping")
            continue

        pattern = rule.get("pattern")
        if not isinstance(pattern, str) or not pattern:
            errors.append(f"{prefix}: 'pattern' must be a non-empty string")
        else:
            prefix = f"rules[{idx}] (pattern={pattern})"

        for field in REQUIRED_RULE_FIELDS:
            if field not in rule:
                errors.append(f"{prefix}: missing required field '{field}'")

        layer = rule.get("layer")
        if isinstance(layer, str) and valid_layers and layer not in valid_layers:
            errors.append(
                f"{prefix}: unknown layer {layer!r} (declared layers: {sorted(valid_layers)})"
            )

        authority = rule.get("authority")
        if isinstance(authority, str) and valid_authorities and authority not in valid_authorities:
            errors.append(
                f"{prefix}: unknown authority {authority!r} "
                f"(declared authorities: {sorted(valid_authorities)})"
            )

        enforcement = rule.get("enforcement")
        if enforcement is not None and not isinstance(enforcement, list):
            errors.append(
                f"{prefix}: 'enforcement' must be a list (got {type(enforcement).__name__})"
            )

    return errors


def main() -> int:
    if not TAXONOMY_FILE.exists():
        print(f"ERROR: missing taxonomy file {TAXONOMY_FILE}", file=sys.stderr)
        return 1
    try:
        data = yaml.safe_load(TAXONOMY_FILE.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        print(f"ERROR: invalid YAML in {TAXONOMY_FILE}: {exc}", file=sys.stderr)
        return 1

    errors = validate(data)
    if errors:
        print(
            f"❌ Artifact taxonomy validation failed ({TAXONOMY_FILE}):",
            file=sys.stderr,
        )
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print(f"✅ Artifact taxonomy valid ({TAXONOMY_FILE}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
