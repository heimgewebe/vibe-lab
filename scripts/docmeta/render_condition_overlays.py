#!/usr/bin/env python3
"""render_condition_overlays.py — deterministic renderer for Run-004 workflow overlays.

The arm overlay markdown files are NOT free-form prose: they are rendered deterministically
from the single structured workflow-instruction source so that the two arms can differ ONLY
along the assigned workflow-instruction spec (the primary axis). The validator re-renders and
asserts byte equality, so a hand-edited overlay (extra tools, examples, motivation, …) cannot
introduce a hidden second axis.

Pure functions only; importable by the validator and by the one-time generator.
"""

from __future__ import annotations

ROLES = ("control", "treatment")
SHARED_SURFACE_KEYS = (
    "language", "tone", "tool_hints", "permissions", "examples", "motivation",
    "quality_rhetoric", "common_constraints",
)
ARM_SPEC_FLAGS = (
    "pre_implementation_specification_required",
    "implementation_may_begin_immediately",
    "specification_completeness_check_required",
)


def render_overlay(protocol: dict, role: str) -> str:
    """Render the deterministic overlay markdown for one arm from the structured source.

    The shared instruction surface is rendered identically for both roles; only the heading
    and the assigned workflow-protocol spec section vary by role.
    """
    if role not in ROLES:
        raise ValueError(f"unknown role: {role!r}")
    sis = protocol.get("shared_instruction_surface") or {}
    spec = (protocol.get("arms") or {}).get(role) or {}

    lines: list[str] = []
    lines.append(f"# Run-004 workflow-instruction overlay — {role}")
    lines.append("")
    lines.append("> Generated deterministically from workflow-instruction-protocol.yml by")
    lines.append("> scripts/docmeta/render_condition_overlays.py. Do not edit by hand; the")
    lines.append("> validator re-renders and asserts byte equality.")
    lines.append("")
    lines.append("## Shared instruction surface (identical for both arms)")
    for key in SHARED_SURFACE_KEYS:
        val = sis.get(key)
        if isinstance(val, list):
            lines.append(f"- {key}:")
            for item in val:
                lines.append(f"  - {item}")
        else:
            lines.append(f"- {key}: {val}")
    lines.append("")
    lines.append(f"## Assigned workflow protocol — {role} (the single primary axis)")
    for flag in ARM_SPEC_FLAGS:
        lines.append(f"- {flag}: {str(spec.get(flag)).lower()}")
    lines.append("- required_specification_sections:")
    sections = spec.get("required_specification_sections") or []
    if sections:
        for section in sections:
            lines.append(f"  - {section}")
    else:
        lines.append("  - (none)")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    import sys
    import yaml  # type: ignore
    from pathlib import Path

    protocol_path = Path(sys.argv[1])
    out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else protocol_path.parent
    protocol = yaml.safe_load(protocol_path.read_text(encoding="utf-8"))
    for role in ROLES:
        target = out_dir / f"{role}-workflow-protocol.md"
        target.write_text(render_overlay(protocol, role), encoding="utf-8")
        print(f"rendered {target}")
