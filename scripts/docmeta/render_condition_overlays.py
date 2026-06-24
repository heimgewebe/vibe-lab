#!/usr/bin/env python3
"""render_condition_overlays.py — deterministic renderer for the BLINDED Run-004 delivered prompt.

The text actually delivered to a future agent (the shared condition and the two per-arm overlays)
is NOT free-form prose and carries NO experiment metadata (no role names, axis names, hypothesis,
or "control"/"treatment" framing). It is rendered deterministically from the single structured
workflow-instruction source's *delivered_* fields only; the non-delivered `control_metadata` block
is ignored here. The validator re-renders and asserts byte equality, so neither a hidden second
axis nor a metadata leak can be hand-edited into the delivered prompt.

Blinding (boundary 3) and control-as-absence (boundary 4) are encoded structurally:
  * the shared condition and the overlay baseline are identical, neutral task text for both arms;
  * the CONTROL overlay is exactly the neutral baseline — the ABSENCE of any further requirement,
    never a negative instruction ("do not write a specification", "begin immediately", …);
  * the TREATMENT overlay is the same baseline PLUS a positive Spec-First requirement whose body
    is the frozen Spec-First instruction snapshot embedded verbatim, so the treatment requirement
    is grounded byte-for-byte in `instruction-blocks/spec-first.md` as frozen.

Pure functions only; importable by the validator and by the one-time generator.
"""

from __future__ import annotations

ROLES = ("control", "treatment")
SHARED_CONDITION_HEADING = "# Task"
OVERLAY_HEADING = "# Procedure"
TREATMENT_SECTIONS_INTRO = "The specification must cover:"


def extract_instruction_body(text: str) -> str:
    """Return the instruction body of a snapshot, stripping a leading YAML frontmatter block.

    Frontmatter is a leading line ``---`` terminated by the next line ``---``. The returned body
    has surrounding blank lines removed; interior structure is preserved verbatim so the embedded
    requirement is byte-identical to the frozen source.
    """
    lines = text.split("\n")
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                lines = lines[i + 1:]
                break
    return "\n".join(lines).strip("\n")


def _doc(lines: list[str]) -> str:
    return "\n".join(lines) + "\n"


def render_shared_condition(protocol: dict) -> str:
    """Render the blinded shared task condition delivered identically to BOTH arms."""
    ds = protocol.get("delivered_shared_instructions") or {}
    body = list(ds.get("shared_condition_lines") or [])
    lines = [SHARED_CONDITION_HEADING, ""]
    lines.extend(body)
    return _doc(lines)


def render_arm_overlay(protocol: dict, role: str, spec_first_basis: str | None = None) -> str:
    """Render the blinded per-arm overlay actually delivered to the agent.

    control   -> the neutral overlay baseline only (absence of any further requirement);
    treatment -> the same baseline + the positive Spec-First requirement, whose body is
                 ``spec_first_basis`` (the frozen Spec-First snapshot body) embedded verbatim,
                 followed by the required specification sections.
    """
    if role not in ROLES:
        raise ValueError(f"unknown role: {role!r}")
    ds = protocol.get("delivered_shared_instructions") or {}
    baseline = list(ds.get("overlay_baseline_lines") or [])
    lines = [OVERLAY_HEADING, ""]
    lines.extend(baseline)
    if role == "treatment":
        addendum = protocol.get("delivered_treatment_addendum") or {}
        if addendum.get("embed_spec_first_basis"):
            if not isinstance(spec_first_basis, str) or not spec_first_basis.strip():
                raise ValueError("treatment overlay requires the frozen spec-first basis text")
            lines.append("")
            lines.extend(extract_instruction_body(spec_first_basis).split("\n"))
        sections = list(addendum.get("required_specification_sections") or [])
        if sections:
            lines.append("")
            lines.append(TREATMENT_SECTIONS_INTRO)
            for section in sections:
                lines.append(f"- {section}")
    return _doc(lines)


if __name__ == "__main__":
    import sys
    from pathlib import Path

    import yaml  # type: ignore

    protocol_path = Path(sys.argv[1])
    out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else protocol_path.parent
    spec_first_path = Path(sys.argv[3]) if len(sys.argv) > 3 else (out_dir / "source-snapshots" / "spec-first.snapshot")
    protocol = yaml.safe_load(protocol_path.read_text(encoding="utf-8"))
    spec_first_basis = spec_first_path.read_text(encoding="utf-8")

    shared = out_dir / "common-condition.md"
    shared.write_bytes(render_shared_condition(protocol).encode("utf-8"))
    print(f"rendered {shared}")
    for role in ROLES:
        target = out_dir / f"{role}-workflow-protocol.md"
        basis = spec_first_basis if role == "treatment" else None
        target.write_bytes(render_arm_overlay(protocol, role, basis).encode("utf-8"))
        print(f"rendered {target}")
