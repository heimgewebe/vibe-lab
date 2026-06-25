#!/usr/bin/env python3
"""validate_model_lab_condition_design.py — Validator for Model-Lab condition-design artifacts.

A condition-design artifact freezes, before execution, the paired condition contrast a future
Model-Lab Run-004 must run. v1 binds the design to immutable historical source byte-snapshots
(source-snapshots/), derives gate requirements by parsing the frozen full gate (no editable
reduced list), enforces a deterministic benchmark+shared+overlay input assembly, and renders the
arm overlays from a single structured workflow source so only the assigned-instruction axis can
differ. It does NOT execute, bind runtime values, allow assessment, or resolve
weak_condition_contrast.

Closed child contracts (schema-validated; a child schema violation is a bundle schema error):
  precondition-snapshot, workflow-instruction-protocol, verification-protocol,
  measurement-protocol, freeze-manifest.

Exit codes: 0 valid · 1 semantic violation · 2 schema/parse/tool error.
Requires: python3 -m pip install pyyaml jsonschema
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    import yaml
    from jsonschema import Draft202012Validator
    from jsonschema.exceptions import SchemaError
    from render_condition_overlays import (
        ROLES, extract_instruction_body, render_arm_overlay, render_shared_condition,
    )
except ImportError as exc:
    print("ERROR: Missing dependencies for model-lab-condition-design validation "
          "(need PyYAML, jsonschema, render_condition_overlays).", file=sys.stderr)
    raise SystemExit(2) from exc


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCHEMA_DIR = REPO_ROOT / "schemas"
SCHEMA_PATH = SCHEMA_DIR / "model-lab-condition-design.v1.schema.json"
CHILD_SCHEMA = {
    "snapshot": SCHEMA_DIR / "model-lab-condition-design-precondition-snapshot.v1.schema.json",
    "workflow": SCHEMA_DIR / "model-lab-condition-design-workflow-instruction-protocol.v1.schema.json",
    "verification": SCHEMA_DIR / "model-lab-condition-design-verification-protocol.v1.schema.json",
    "measurement": SCHEMA_DIR / "model-lab-condition-design-measurement-protocol.v1.schema.json",
    "freeze": SCHEMA_DIR / "model-lab-condition-design-freeze-manifest.v1.schema.json",
}

DESIGN_GLOB = "*/artifacts/*/condition-design.yml"
DESIGN_ARTIFACT_TYPE = "model_lab_condition_design"
GATE_ARTIFACT_TYPE = "model_lab_condition_contrast_design_gate"
READINESS_ARTIFACT_TYPE = "result_assessment_readiness"

EXPECTED_PRIMARY_AXIS = "workflow_protocol"
CONTROL_WP = "direct_implementation"
TREATMENT_WP = "spec_first"
COMPLIANCE_METRIC_ID = "workflow_protocol_compliance"
MANDATORY_TREATMENT_SECTIONS = (
    "endpoint_matrix", "request_response_schemas", "validation_rules", "http_status_codes",
    "error_cases", "edge_cases", "persistence_assumptions", "planned_implementation_order",
)
EFFECT_SEVERITY = {"must_be_reported": 1, "blocks_design": 2}

# --- source role/provenance binding (boundary 1) --------------------------------------------
# Each frozen source must come from its exact canonical historical location, carry the role's
# artifact_type, and share the freeze manifest's source_base_commit_sha. gate/readiness/spec-first
# paths are fixed; the challenge path is derived from challenge_version so a swapped benchmark fails.
SERIES_DIR = "experiments/2026-05-31_model-lab-replication-series"
CHALLENGE_ARTIFACT_TYPE = "benchmark_challenge"
EXPECTED_SOURCE_ROLES = {
    "gate": (f"{SERIES_DIR}/results/condition-contrast-design-gate.yml", GATE_ARTIFACT_TYPE),
    "readiness": (f"{SERIES_DIR}/results/result-assessment-readiness.yml", READINESS_ARTIFACT_TYPE),
    "spec_first": ("instruction-blocks/spec-first.md", "instruction_block"),
}

# --- delivered-prompt blinding (boundary 3) -------------------------------------------------
# The text actually delivered to the agent (shared condition + both overlays) must carry NO
# experiment metadata. These patterns are pure experiment-framing words that have no place in a
# blinded task instruction; they are matched case-insensitively on the editable delivered files.
FORBIDDEN_PROMPT_PATTERNS = tuple(re.compile(p, re.IGNORECASE) for p in (
    r"\bcontrol\b", r"\btreatment\b", r"\barms?\b", r"\bexperiment\w*\b", r"\bhypothes\w*\b",
    r"\baxis\b", r"\baxes\b", r"\bintervention\b", r"\bcontrast\b", r"\bbaseline\b",
    r"\bprimary\b", r"\brun[\s-]?004\b", r"\bmodel[\s-]lab\b", r"\boverlay\b",
    r"\bworkflow[\s-]protocol\b", r"\bcondition\s+design\b", r"\bblind\w*\b",
))
DELIVERED_PROMPT_FILES = ("common-condition.md", "control-workflow-protocol.md",
                          "treatment-workflow-protocol.md")
OPERATIVE_MARKDOWN_FILES = DELIVERED_PROMPT_FILES

# --- control-as-absence (boundary 4) --------------------------------------------------------
# The control overlay must be the ABSENCE of an extra Spec-First requirement, never a negative
# instruction. It must mention no specification at all and carry none of the structured negative
# flags; the treatment overlay must positively require a specification.
CONTROL_FORBIDDEN_NEGATIVE = tuple(re.compile(p, re.IGNORECASE) for p in (
    r"\bspecification\b", r"specification[_\s]+required", r"do\s+not\s+write",
    r"begin\s+implementation\s+immediately", r"implementation_may_begin_immediately",
    r"pre_implementation_specification_required", r"specification_completeness_check_required",
    r"\(none\)", r"\bskip\b", r"\bwithout\b",
))

# --- honest bundled prompt axis (boundary: prompt-scope must not overclaim constancy) --------
# The treatment overlay differs from control in more than abstract "order": it adds a spec
# requirement, length, internal structure, directive strength, efficacy rhetoric, and 8 sections.
# Those are honest BUNDLED-axis components; they must NOT also be claimed held-constant.
PROMPT_ISOLATION_NONCLAIMS = ("individual_prompt_component_effect_isolated",
                              "canonical_spec_first_instruction_effect_isolated")
REQUIRED_BUNDLED_AXIS_COMPONENTS = frozenset({
    "preimplementation_specification_requirement", "prompt_length",
    "overlay_internal_structure", "required_specification_sections",
})
FORBIDDEN_HELD_CONSTANT = frozenset({
    "tone", "quality_rhetoric", "motivation", "outer_structure", "directive_strength",
    "motivational_or_efficacy_rhetoric", "prompt_length", "overlay_internal_structure",
    "required_specification_sections", "preimplementation_specification_requirement",
    "implementation_order_constraint",
})

MANDATORY_DOES_NOT_ESTABLISH = (
    "weak_condition_contrast_resolved", "run_004_execution_allowed", "run_004_executed",
    "execution_environment_bound", "result_assessment_allowed", "comparison_ready",
    "condition_effect", "model_quality", "comparative_superiority", "external_model_independence",
    "external_auditor_comparison_completed", "dependency_risk_remediated", "security_readiness",
    "production_readiness", "single_paired_execution_establishes_condition_effect",
)
FORBIDDEN_SELECTION_NON_CLAIMS = ("primary_intervention_axis_selected", "concrete_condition_selected")

FORBIDDEN_EXECUTION_FILES = frozenset({
    "run.yml", "run_meta.json", "execution.txt", "measurement.yml", "auditor-output.yml",
    "comparability.yml", "evidence-pack.yml", "timing.txt", "package.json", "package-lock.json",
})
FORBIDDEN_EXECUTION_DIRS = frozenset({"implementation", "src", "tests"})
FORBIDDEN_EXECUTION_GLOBS = ("execute-*.py", "verify-*.py")

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
DRIVE_LETTER_RE = re.compile(r"^[A-Za-z]:")
_SCHEMA_CACHE: dict = {}


# --- generic helpers ------------------------------------------------------------------------

def _has_forbidden_codepoint(text: str) -> bool:
    return any(ord(c) <= 0x1F or ord(c) == 0x7F or 0xD800 <= ord(c) <= 0xDFFF for c in text)


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except (OSError, RuntimeError, ValueError, UnicodeError):
        return str(path)


def display_source_path(raw) -> str:
    if not isinstance(raw, str):
        return str(raw)
    out = []
    lead = len(raw) - len(raw.lstrip()); trail = len(raw.rstrip())
    for i, c in enumerate(raw):
        cp = ord(c)
        if c == " " and (i < lead or i >= trail):
            out.append(r"\x20")
        elif cp <= 0x1F or cp == 0x7F:
            out.append({"\t": r"\t", "\n": r"\n", "\r": r"\r"}.get(c, f"\\x{cp:02x}"))
        elif 0xD800 <= cp <= 0xDFFF:
            out.append(f"\\u{cp:04x}")
        else:
            out.append(c)
    return "".join(out)


def load_validator(schema_path: Path) -> Draft202012Validator:
    key = str(schema_path)
    if key in _SCHEMA_CACHE:
        return _SCHEMA_CACHE[key]
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
    except FileNotFoundError as exc:
        raise RuntimeError(f"schema file missing: {display_path(schema_path)}") from exc
    except (json.JSONDecodeError, UnicodeDecodeError, OSError) as exc:
        raise RuntimeError(f"schema unreadable: {display_path(schema_path)}: {exc}") from exc
    except SchemaError as exc:
        raise RuntimeError(f"schema invalid: {display_path(schema_path)}: {exc.message}") from exc
    v = Draft202012Validator(schema)
    _SCHEMA_CACHE[key] = v
    return v


def load_yaml(path: Path) -> dict:
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"file missing: {display_path(path)}") from exc
    except UnicodeDecodeError as exc:
        raise ValueError(f"file is not valid UTF-8: {display_path(path)}") from exc
    except OSError as exc:
        raise ValueError(f"file could not be read: {display_path(path)}: {exc}") from exc
    try:
        loaded = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise ValueError(f"YAML parse error in {display_path(path)}: {exc}") from exc
    if not isinstance(loaded, dict):
        raise ValueError(f"YAML document must be an object: {display_path(path)}")
    return loaded


def schema_errors(validator: Draft202012Validator, data: dict, path: Path, *, label: str = "") -> list[str]:
    out = []
    pfx = f"{label} " if label else ""
    for e in sorted(validator.iter_errors(data), key=lambda i: list(i.absolute_path)):
        loc = ".".join(str(p) for p in e.absolute_path) or "$"
        out.append(f"ERROR {pfx}path={display_path(path)} instance_path={loc}: {e.message}")
    return out


def format_error(rule_id: str, path: Path, message: str) -> str:
    return f"ERROR rule={rule_id} path={display_path(path)}: {message}"


def _inside(candidate: Path, root: Path) -> bool:
    try:
        candidate.relative_to(root)
        return True
    except ValueError:
        return False


def resolve_repo_relative_path(rel_path, repo_root: Path, *, must_exist: bool):
    raw = str(rel_path)
    if _has_forbidden_codepoint(raw) or raw != raw.strip() or not raw:
        return None, "ESCAPE"
    if raw.startswith("/") or DRIVE_LETTER_RE.match(raw) or "\\" in raw:
        return None, "ESCAPE"
    if ".." in PurePosixPath(raw).parts:
        return None, "ESCAPE"
    root = repo_root.resolve()
    candidate = root / raw
    try:
        resolved = candidate.resolve(strict=must_exist)
    except FileNotFoundError:
        try:
            lax = candidate.resolve(strict=False)
        except (OSError, RuntimeError, ValueError, UnicodeError):
            return None, "ESCAPE"
        return (None, "NOT_FOUND") if _inside(lax, root) else (None, "ESCAPE")
    except (OSError, RuntimeError, ValueError, UnicodeError):
        return None, "ESCAPE"
    if not _inside(resolved, root):
        return None, "ESCAPE"
    if must_exist and not resolved.exists():
        return None, "NOT_FOUND"
    return resolved, None


def _sha256_of(path: Path):
    try:
        d = hashlib.sha256()
        with path.open("rb") as h:
            for chunk in iter(lambda: h.read(65536), b""):
                d.update(chunk)
        return d.hexdigest()
    except (OSError, ValueError):
        return None


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class ToolError(Exception):
    """A tool/environment failure that must surface as exit 2 (cannot verify), never as a green
    skip or a semantic exit-1 verdict."""


def read_git_source_bytes(repo_root: Path, commit_sha, source_path):
    """Read the exact bytes of source_path at commit_sha from the git object store.

    Returns (bytes, problem):
      * (b"...", None)  — the blob bytes at <commit>:<path>;
      * (None, "tool")  — git unavailable or the commit object is absent (e.g. a shallow checkout);
                          the caller must fail closed with exit 2 (cannot verify), not skip;
      * (None, "missing") — the path does not exist at that commit (a false provenance claim).
    Never decodes; never reads the working tree; no shell. Diagnostics never include file contents.
    """
    commit = str(commit_sha).strip()
    spath = str(source_path).strip()
    if not re.match(r"^[0-9a-f]{40}$", commit) or not spath:
        return None, "missing"
    try:
        chk = subprocess.run(["git", "cat-file", "-e", f"{commit}^{{commit}}"],
                             cwd=str(repo_root), capture_output=True, check=False)
        if chk.returncode != 0:
            return None, "tool"  # commit object not present -> cannot verify (need full history)
        blob = subprocess.run(["git", "cat-file", "blob", f"{commit}:{spath}"],
                              cwd=str(repo_root), capture_output=True, check=False)
    except (OSError, ValueError):
        return None, "tool"
    if blob.returncode != 0:
        return None, "missing"  # path absent at that commit -> provenance claim is false
    return blob.stdout, None


def _parse_rfc3339(value):
    if not isinstance(value, str):
        return None
    text = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        return _dt.datetime.fromisoformat(text)
    except ValueError:
        return None


def _ids(items):
    return [str(i.get("id", "")).strip() for i in (items or []) if isinstance(i, dict) and str(i.get("id", "")).strip()]


def _duplicates(values):
    seen, dups = set(), set()
    for v in values:
        (dups if v in seen else seen).add(v)
    return sorted(dups, key=str)


def _arms_by_role(arms):
    c = [a for a in arms if isinstance(a, dict) and a.get("role") == "control"]
    t = [a for a in arms if isinstance(a, dict) and a.get("role") == "treatment"]
    return (c[0] if len(c) == 1 else None, t[0] if len(t) == 1 else None)


def _load_bundle_file(ref, bundle_dir: Path, repo_root: Path, *, as_yaml: bool):
    resolved, code = resolve_repo_relative_path(ref, repo_root, must_exist=True)
    if code == "ESCAPE":
        return None, None, "resolves outside the repo root"
    if code == "NOT_FOUND":
        return None, None, "does not exist"
    if resolved is None or not resolved.is_file():
        return None, None, "is not a regular file"
    if not _inside(resolved, bundle_dir):
        return resolved, None, "is outside the design bundle"
    if not as_yaml:
        return resolved, None, None
    try:
        return resolved, load_yaml(resolved), None
    except (FileNotFoundError, ValueError):
        return resolved, None, "is not a readable YAML mapping"


def _child_identity_problems(label, doc, design):
    out = []
    for k in ("design_id", "series_id", "challenge_version"):
        if str(doc.get(k, "")).strip() != str(design.get(k, "")).strip():
            out.append(f"{label}.{k}={doc.get(k)!r} (expected {design.get(k)!r})")
    return out


# --- bundle ref enumeration -----------------------------------------------------------------

def _bundle_refs(data: dict):
    refs = [(str(data.get("design_artifact_path", "")), "design_artifact_path"),
            (str(data.get("precondition_snapshot_ref", "")), "precondition_snapshot_ref"),
            (str(data.get("workflow_instruction_source_ref", "")), "workflow_instruction_source_ref")]
    fr = data.get("freeze") or {}
    if isinstance(fr, dict) and fr.get("freeze_manifest_ref"):
        refs.append((str(fr["freeze_manifest_ref"]), "freeze.freeze_manifest_ref"))
    for blk, lbl in (("verification_surface", "verification_surface.protocol_ref"),
                     ("measurement_surface", "measurement_surface.protocol_ref")):
        b = data.get(blk) or {}
        if isinstance(b, dict) and b.get("protocol_ref"):
            refs.append((str(b["protocol_ref"]), lbl))
    cia = data.get("condition_input_assembly") or {}
    comp = cia.get("components") or {} if isinstance(cia, dict) else {}
    for cname in ("benchmark", "shared_condition"):
        c = comp.get(cname) or {}
        if isinstance(c, dict) and c.get("ref"):
            refs.append((str(c["ref"]), f"condition_input_assembly.components.{cname}.ref"))
    for arm in data.get("arms") or []:
        if isinstance(arm, dict) and arm.get("overlay_ref"):
            refs.append((str(arm["overlay_ref"]), f"arms[{arm.get('id','?')}].overlay_ref"))
        sfb = (arm or {}).get("spec_first_basis") if isinstance(arm, dict) else None
        if isinstance(sfb, dict) and sfb.get("snapshot_ref"):
            refs.append((str(sfb["snapshot_ref"]), f"arms[{arm.get('id','?')}].spec_first_basis.snapshot_ref"))
    return refs


def _freeze_base_commit(data: dict, bundle_dir: Path, repo_root: Path):
    """Return the freeze manifest's source_base_commit_sha (lowercased) or None if unavailable."""
    ref = str((data.get("freeze") or {}).get("freeze_manifest_ref", ""))
    _, manifest, _ = _load_bundle_file(ref, bundle_dir, repo_root, as_yaml=True)
    if not isinstance(manifest, dict):
        return None
    base = str(manifest.get("source_base_commit_sha", "")).strip().lower()
    return base or None


def _read_text_strict(path: Path):
    """Return (text, problem). problem is a normalization message: invalid UTF-8, CR present, or
    no final newline. Never uses errors='replace', so corruption is surfaced, not masked."""
    try:
        raw = path.read_bytes()
    except OSError as exc:
        return None, f"could not be read ({exc})"
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return None, "is not valid UTF-8"
    if b"\r" in raw:
        return text, "contains a carriage return (LF-only required)"
    if not raw.endswith(b"\n"):
        return text, "has no final newline"
    return text, None


def _prompt_exposure_errors(bundle_dir: Path, path: Path):
    """Boundary 3+4+§15: the delivered prompt files must be UTF-8/LF/final-newline normalized, carry
    no experiment metadata, and model control as the ABSENCE (not a negation) of a spec requirement."""
    norm, blind, absence = [], [], []
    texts = {}
    for name in OPERATIVE_MARKDOWN_FILES:
        fp = bundle_dir / name
        if not fp.is_file():
            continue
        text, prob = _read_text_strict(fp)
        if prob is not None:
            norm.append(f"{name} {prob}")
        if text is None:
            continue
        texts[name] = text
        for pat in FORBIDDEN_PROMPT_PATTERNS:
            m = pat.search(text)
            if m:
                blind.append(f"{name} contains forbidden experiment token {m.group(0)!r}")
                break
    ctrl = texts.get("control-workflow-protocol.md")
    treat = texts.get("treatment-workflow-protocol.md")
    if ctrl is not None:
        for pat in CONTROL_FORBIDDEN_NEGATIVE:
            m = pat.search(ctrl)
            if m:
                absence.append(f"control overlay must state no specification requirement (found {m.group(0)!r})")
                break
    if treat is not None and not re.search(r"\bspecification\b", treat, re.IGNORECASE):
        absence.append("treatment overlay must positively require a specification")
    out = []
    if norm:
        out.append(format_error("CONDITION_DESIGN_REQUIRES_TEXT_NORMALIZATION", path,
            "every delivered prompt file must be UTF-8, LF-only, with a final newline; " + "; ".join(norm)))
    if blind:
        out.append(format_error("CONDITION_DESIGN_REQUIRES_BLINDED_PROMPT", path,
            "the delivered prompt must carry no role/axis/experiment metadata; " + "; ".join(blind)))
    if absence:
        out.append(format_error("CONDITION_DESIGN_REQUIRES_CONTROL_ABSENCE", path,
            "control must be the ABSENCE of an extra Spec-First requirement (never a negative "
            "instruction) while treatment positively requires a specification; " + "; ".join(absence)))
    return out


def _operative_distinctness_errors(data: dict, bundle_dir: Path, repo_root: Path, path: Path):
    """Boundary 2/§7: the operative (non-snapshot, non-freeze) bundle files must be pairwise distinct."""
    comp = (data.get("condition_input_assembly") or {}).get("components") or {}
    refs = [
        (str(data.get("design_artifact_path", "")), "condition-design.yml"),
        (str(data.get("precondition_snapshot_ref", "")), "precondition-snapshot.yml"),
        (str(data.get("workflow_instruction_source_ref", "")), "workflow-instruction-protocol.yml"),
        (str((data.get("verification_surface") or {}).get("protocol_ref", "")), "verification-protocol.yml"),
        (str((data.get("measurement_surface") or {}).get("protocol_ref", "")), "measurement-protocol.yml"),
        (str((comp.get("shared_condition") or {}).get("ref", "")), "common-condition.md"),
    ]
    for arm in data.get("arms") or []:
        if isinstance(arm, dict):
            refs.append((str(arm.get("overlay_ref", "")), f"{arm.get('role', '?')} overlay"))
    digests, dups = {}, []
    for ref, label in refs:
        resolved, code = resolve_repo_relative_path(ref, repo_root, must_exist=True)
        if code is not None or resolved is None or not resolved.is_file():
            continue
        h = _sha256_of(resolved)
        if h is None:
            continue
        if h in digests:
            dups.append(f"{label} is byte-identical to {digests[h]}")
        else:
            digests[h] = label
    if dups:
        return [format_error("CONDITION_DESIGN_REQUIRES_OPERATIVE_FILE_DISTINCTNESS", path,
            "operative bundle files must be pairwise distinct; " + "; ".join(dups))]
    return []


def _prompt_scope_errors(data: dict, path: Path):
    """§13: prompt_scope must honestly separate held-constant features from the bundled axis and
    must not claim isolation of any single prompt component or of the canonical Spec-First text."""
    ps = data.get("prompt_scope") or {}
    held = {str(x).strip() for x in (ps.get("held_constant_across_arms") or [])}
    bundled = {str(x).strip() for x in (ps.get("bundled_axis_components") or [])}
    declared_nonclaims = {str(x).strip() for x in (data.get("does_not_establish") or [])}
    probs = []
    overlap = held & bundled
    if overlap:
        probs.append("held_constant_across_arms and bundled_axis_components overlap: " + ", ".join(sorted(overlap)))
    dishonest = held & FORBIDDEN_HELD_CONSTANT
    if dishonest:
        probs.append("features that vary between arms must not be held_constant: " + ", ".join(sorted(dishonest)))
    missing_bundled = REQUIRED_BUNDLED_AXIS_COMPONENTS - bundled
    if missing_bundled:
        probs.append("bundled_axis_components must include the actually-varying classes: " + ", ".join(sorted(missing_bundled)))
    missing_nonclaims = [n for n in PROMPT_ISOLATION_NONCLAIMS if n not in declared_nonclaims]
    if missing_nonclaims:
        probs.append("does_not_establish must include: " + ", ".join(missing_nonclaims))
    if probs:
        return [format_error("CONDITION_DESIGN_REQUIRES_HONEST_PROMPT_SCOPE", path,
            "the bundled prompt axis must be described honestly; " + "; ".join(probs))]
    return []


def _expected_bundle_files(data: dict, snapshot, bundle_dir: Path, repo_root: Path):
    """The closed set of files the contract says belong in the bundle, as resolved paths."""
    expected = set()
    for raw, _ in _bundle_refs(data):
        r, _c = resolve_repo_relative_path(raw, repo_root, must_exist=False)
        if r is not None and _inside(r, bundle_dir):
            expected.add(r)
    man = str((data.get("freeze") or {}).get("freeze_manifest_ref", ""))
    r, _c = resolve_repo_relative_path(man, repo_root, must_exist=False)
    if r is not None and _inside(r, bundle_dir):
        expected.add(r)
    if isinstance(snapshot, dict):
        for src in (snapshot.get("sources") or {}).values():
            if isinstance(src, dict) and src.get("snapshot_path"):
                r, _c = resolve_repo_relative_path(str(src["snapshot_path"]), repo_root, must_exist=False)
                if r is not None and _inside(r, bundle_dir):
                    expected.add(r)
    return expected


def _closed_bundle_errors(data: dict, snapshot, bundle_dir: Path, repo_root: Path, path: Path):
    """§12: the bundle is a closed set — actual regular files == contract-referenced files, no
    symlinks or escapes, and the freeze covers exactly the expected set minus the manifest itself."""
    bdir = bundle_dir.resolve()
    if not bdir.is_dir():
        return []
    expected = _expected_bundle_files(data, snapshot, bdir, repo_root)

    def rel(p):
        try:
            return p.resolve().relative_to(bdir).as_posix()
        except (ValueError, OSError):
            return str(p)

    problems, actual = [], set()
    for entry in sorted(bdir.rglob("*")):
        r = rel(entry)
        if entry.is_symlink():
            problems.append(f"symlink not allowed in bundle: {r}")
            continue
        if entry.is_dir():
            continue
        if not entry.is_file():
            problems.append(f"not a regular file: {r}")
            continue
        resolved = entry.resolve()
        if not _inside(resolved, bdir):
            problems.append(f"file escapes the bundle: {r}")
            continue
        actual.add(resolved)
    for p in sorted(actual - expected):
        problems.append(f"unexpected file not referenced by any contract: {rel(p)}")
    for p in sorted(expected - actual):
        problems.append(f"expected contract file missing from bundle: {rel(p)}")
    # freeze hash set must equal the expected set minus the manifest (which never self-hashes)
    man_rel = str((data.get("freeze") or {}).get("freeze_manifest_ref", ""))
    man_resolved, _c = resolve_repo_relative_path(man_rel, repo_root, must_exist=False)
    _, manifest, _p = _load_bundle_file(man_rel, bundle_dir, repo_root, as_yaml=True)
    if isinstance(manifest, dict):
        hashed = set()
        for e in manifest.get("hashes") or []:
            if isinstance(e, dict):
                r, _c = resolve_repo_relative_path(str(e.get("path", "")), repo_root, must_exist=False)
                if r is not None:
                    hashed.add(r)
        expected_hashed = expected - ({man_resolved} if man_resolved else set())
        for p in sorted(expected_hashed - hashed):
            problems.append(f"expected file not covered by freeze: {rel(p)}")
        for p in sorted(hashed - expected_hashed):
            problems.append(f"freeze hashes a path outside the expected set: {rel(p)}")
    if problems:
        return [format_error("CONDITION_DESIGN_REQUIRES_CLOSED_BUNDLE", path,
            "the design bundle must be a closed set (actual regular files == contract-referenced "
            "files; no symlinks/escapes; freeze covers exactly the expected set minus the manifest); "
            + "; ".join(problems))]
    return []


def _covered_bundle_files(data: dict, snapshot: dict | None):
    out = {r for r, _ in _bundle_refs(data) if r}
    out.discard(str((data.get("freeze") or {}).get("freeze_manifest_ref", "")))  # manifest never self-covers
    if isinstance(snapshot, dict):
        for src in (snapshot.get("sources") or {}).values():
            if isinstance(src, dict) and src.get("snapshot_path"):
                out.add(str(src["snapshot_path"]))
    return sorted(out)


def _execution_artifact_problems(bundle_dir: Path):
    problems = set()
    try:
        if not bundle_dir.is_dir():
            return []
        for e in bundle_dir.rglob("*"):
            try:
                rel = e.relative_to(bundle_dir).as_posix()
                if e.is_dir() and e.name in FORBIDDEN_EXECUTION_DIRS:
                    problems.add(rel + "/")
                elif e.is_file() and (e.name in FORBIDDEN_EXECUTION_FILES or any(e.match(g) for g in FORBIDDEN_EXECUTION_GLOBS)):
                    problems.add(rel)
            except OSError:
                continue
    except OSError:
        return []
    return sorted(problems)


# --- child schema phase (exit 2) ------------------------------------------------------------

def child_schema_errors(data: dict, path: Path, repo_root: Path):
    bundle_dir = path.resolve().parent
    errors = []
    specs = [
        ("snapshot", str(data.get("precondition_snapshot_ref", "")), CHILD_SCHEMA["snapshot"]),
        ("workflow", str(data.get("workflow_instruction_source_ref", "")), CHILD_SCHEMA["workflow"]),
        ("verification", str((data.get("verification_surface") or {}).get("protocol_ref", "")), CHILD_SCHEMA["verification"]),
        ("measurement", str((data.get("measurement_surface") or {}).get("protocol_ref", "")), CHILD_SCHEMA["measurement"]),
        ("freeze", str((data.get("freeze") or {}).get("freeze_manifest_ref", "")), CHILD_SCHEMA["freeze"]),
    ]
    for label, ref, schema_path in specs:
        resolved, doc, prob = _load_bundle_file(ref, bundle_dir, repo_root, as_yaml=True)
        if doc is None:
            continue  # missing/unsafe/unreadable -> reported as a semantic path/boundary violation
        errors.extend(schema_errors(load_validator(schema_path), doc, resolved, label=f"child={label}"))
    return errors


# --- semantic phase (exit 1) ----------------------------------------------------------------

def semantic_errors(data: dict, path: Path, repo_root: Path):
    errors = []
    bundle_dir = path.resolve().parent
    arms = data.get("arms") or []
    controlled = data.get("controlled_dimensions") or []
    confounders = data.get("confounder_controls") or []
    primary_axis = data.get("primary_intervention_axis") or {}
    control_arm, treatment_arm = _arms_by_role(arms)

    def load(ref, *, as_yaml=True):
        return _load_bundle_file(ref, bundle_dir, repo_root, as_yaml=as_yaml)

    # design self-identity
    dpath = str(data.get("design_artifact_path", ""))
    resolved_self, code = resolve_repo_relative_path(dpath, repo_root, must_exist=True)
    if code is not None or resolved_self is None or resolved_self != path.resolve():
        errors.append(format_error("CONDITION_DESIGN_REQUIRES_DESIGN_SELF_IDENTITY", path,
            f"design_artifact_path ({display_source_path(dpath)}) must resolve to the validated file ({display_path(path)})."))

    # --- precondition snapshot + frozen source provenance --------------------
    snap_ref = str(data.get("precondition_snapshot_ref", ""))
    _, snapshot, snap_prob = load(snap_ref)
    frozen_gate = frozen_readiness = None
    spec_first_res = None
    base_commit = _freeze_base_commit(data, bundle_dir, repo_root)
    challenge_version = str(data.get("challenge_version", "")).strip()
    expected_paths = dict(EXPECTED_SOURCE_ROLES)
    expected_paths["challenge"] = (f"benchmarks/challenges/{challenge_version}.md", CHALLENGE_ARTIFACT_TYPE)
    snap_problems = []
    role_problems = []
    if snapshot is None:
        snap_problems.append(f"snapshot {display_source_path(snap_ref)} {snap_prob}")
    else:
        snap_problems += _child_identity_problems("snapshot", snapshot, data)
        sources = snapshot.get("sources") or {}
        captured_at = snapshot.get("captured_at")
        if _parse_rfc3339(captured_at) is None:
            snap_problems.append(f"captured_at is not a real RFC-3339 timestamp ({captured_at!r})")
        for sname, want_parse in (("gate", "gate"), ("readiness", "readiness"),
                                  ("challenge", None), ("spec_first", "spec_first")):
            src = sources.get(sname) or {}
            # boundary 1: role/provenance binding (canonical path, role artifact_type, base commit)
            exp_path, exp_type = expected_paths[sname]
            if str(src.get("source_path", "")).strip() != exp_path:
                role_problems.append(f"sources.{sname}.source_path must be {exp_path!r} "
                                     f"(found {display_source_path(str(src.get('source_path','')))})")
            if str(src.get("artifact_type", "")).strip() != exp_type:
                role_problems.append(f"sources.{sname}.artifact_type must be {exp_type!r} "
                                     f"(found {str(src.get('artifact_type',''))!r})")
            if base_commit is not None and str(src.get("source_commit_sha", "")).strip().lower() != base_commit:
                role_problems.append(f"sources.{sname}.source_commit_sha must equal the freeze "
                                     f"source_base_commit_sha ({base_commit})")
            spath = str(src.get("snapshot_path", ""))
            sres, _, sprob = load(spath, as_yaml=False)
            if sprob is not None:
                snap_problems.append(f"sources.{sname}.snapshot_path {display_source_path(spath)} {sprob}")
                continue
            actual = _sha256_of(sres)
            if actual != str(src.get("snapshot_sha256", "")).strip().lower():
                snap_problems.append(f"sources.{sname}.snapshot_sha256 does not match the frozen file")
                continue
            if str(src.get("source_sha256", "")).strip().lower() != str(src.get("snapshot_sha256", "")).strip().lower():
                snap_problems.append(f"sources.{sname}.source_sha256 != snapshot_sha256 (frozen file is not the claimed source)")
                continue
            if want_parse == "gate":
                try:
                    frozen_gate = load_yaml(sres)
                except (FileNotFoundError, ValueError):
                    snap_problems.append("frozen gate snapshot is not readable YAML")
            elif want_parse == "readiness":
                try:
                    frozen_readiness = load_yaml(sres)
                except (FileNotFoundError, ValueError):
                    snap_problems.append("frozen readiness snapshot is not readable YAML")
            elif want_parse == "spec_first":
                spec_first_res = sres
        # derive gate truth from the frozen full gate
        if frozen_gate is not None:
            if str(frozen_gate.get("artifact_type", "")).strip() != GATE_ARTIFACT_TYPE:
                snap_problems.append("frozen gate artifact_type mismatch")
            if frozen_gate.get("gate_status") != "criteria_defined":
                snap_problems.append("frozen gate gate_status must be criteria_defined")
            if frozen_gate.get("run_004_design_allowed") is not True:
                snap_problems.append("frozen gate run_004_design_allowed must be true")
            if frozen_gate.get("run_004_execution_allowed") is not False:
                snap_problems.append("frozen gate run_004_execution_allowed must be false")
            if frozen_gate.get("result_assessment_allowed_after_gate") is not False:
                snap_problems.append("frozen gate result_assessment_allowed_after_gate must be false")
            if frozen_gate.get("comparison_ready_after_gate") is not False:
                snap_problems.append("frozen gate comparison_ready_after_gate must be false")
            if str(frozen_gate.get("target_blocker", "")).strip() != str(data.get("target_blocker", "")).strip():
                snap_problems.append("frozen gate target_blocker mismatch")
            if str(frozen_gate.get("blocker_status_after_gate", "")).strip() != "open":
                snap_problems.append("frozen gate blocker_status_after_gate must be open")
        if frozen_readiness is not None:
            if frozen_readiness.get("readiness_status") != "blocked":
                snap_problems.append("frozen readiness readiness_status must be blocked")
            if frozen_readiness.get("result_assessment_allowed") is not False:
                snap_problems.append("frozen readiness result_assessment_allowed must be false")
            if frozen_readiness.get("comparison_ready") is not False:
                snap_problems.append("frozen readiness comparison_ready must be false")
            blockers = frozen_readiness.get("blockers") or []
            if not any(isinstance(b, dict) and str(b.get("id", "")).strip() == str(data.get("target_blocker", "")).strip()
                       and str(b.get("status", "")).strip() == "open" for b in blockers):
                snap_problems.append("frozen readiness does not list the target_blocker as open")
    if snap_problems:
        errors.append(format_error("CONDITION_DESIGN_REQUIRES_VALID_PRECONDITION_SNAPSHOT", path,
            "the frozen precondition snapshot must verify its source hashes and derive a coherent "
            "gate+readiness precondition; offending: " + "; ".join(snap_problems)))
    if role_problems:
        errors.append(format_error("CONDITION_DESIGN_REQUIRES_SOURCE_ROLE_BINDING", path,
            "every frozen source must come from its exact canonical historical path, carry the role's "
            "artifact_type, and share the freeze source_base_commit_sha; offending: "
            + "; ".join(role_problems)))

    # --- permanent git-object provenance: snapshot bytes == git <commit>:<path> ----
    # source_sha256 == snapshot_sha256 only proves self-consistency; this proves the frozen bytes
    # actually came from the declared commit+path. Reads the git object store only (never the
    # working tree). A missing commit / unavailable git is "cannot verify" -> exit 2 (ToolError).
    if snapshot is not None:
        prov = []
        for sname in ("gate", "readiness", "challenge", "spec_first"):
            src = (snapshot.get("sources") or {}).get(sname) or {}
            commit = str(src.get("source_commit_sha", "")).strip()
            spath = str(src.get("source_path", "")).strip()
            sres, _, sprob = load(str(src.get("snapshot_path", "")), as_yaml=False)
            if sprob is not None:
                continue  # snapshot file already reported as a precondition-snapshot problem
            git_bytes, gprob = read_git_source_bytes(repo_root, commit, spath)
            if gprob == "tool":
                raise ToolError(
                    f"cannot verify git-source provenance for sources.{sname}: commit "
                    f"{commit[:12] or '<none>'} or the git object store is unavailable "
                    f"(the validate job needs full history, e.g. fetch-depth: 0)")
            if gprob == "missing":
                prov.append(f"sources.{sname}: {display_source_path(spath)} does not exist at commit {commit[:12]}")
                continue
            snap_bytes = sres.read_bytes()
            if git_bytes != snap_bytes:
                prov.append(f"sources.{sname}: frozen snapshot bytes differ from git {commit[:12]}:{display_source_path(spath)}")
            elif _sha256_bytes(git_bytes) != str(src.get("source_sha256", "")).strip().lower():
                prov.append(f"sources.{sname}: source_sha256 does not match the git object at {commit[:12]}")
        if prov:
            errors.append(format_error("CONDITION_DESIGN_REQUIRES_GIT_SOURCE_PROVENANCE", path,
                "each frozen source must be byte-identical to the git object at its declared "
                "source_commit_sha:source_path; " + "; ".join(prov)))

    # --- gate requirements derived from the frozen gate (subset) -------------
    if frozen_gate is not None:
        derived_dims = set(_ids(frozen_gate.get("invariant_dimensions")) + _ids(frozen_gate.get("dimensions_to_control_when_not_primary")))
        design_dims = set(_ids(controlled))
        missing = sorted(derived_dims - design_dims)
        sub = []
        if missing:
            sub.append("controlled_dimensions missing gate-required: " + ", ".join(missing))
        design_conf = {str(c.get("id", "")).strip(): str(c.get("effect_if_uncontrolled", "")).strip()
                       for c in confounders if isinstance(c, dict) and str(c.get("id", "")).strip()}
        for gc in frozen_gate.get("confounder_controls") or []:
            if not isinstance(gc, dict):
                continue
            cid = str(gc.get("id", "")).strip()
            geff = str(gc.get("effect_if_uncontrolled", "")).strip()
            if cid not in design_conf:
                sub.append(f"confounder_controls missing gate-required: {cid}")
            elif EFFECT_SEVERITY.get(design_conf[cid], 0) < EFFECT_SEVERITY.get(geff, 0):
                sub.append(f"confounder {cid} weakens gate effect {geff!r} to {design_conf[cid]!r}")
        if sub:
            errors.append(format_error("CONDITION_DESIGN_REQUIRES_GATE_REQUIREMENTS_SUBSET", path,
                "design must control at least the gate-derived dimensions/confounders without weakening "
                "effects; " + "; ".join(sub)))

    # --- arms: exactly two, single axis, primary not controlled --------------
    roles = sorted(str(a.get("role", "")).strip() for a in arms if isinstance(a, dict))
    if roles != ["control", "treatment"]:
        errors.append(format_error("CONDITION_DESIGN_REQUIRES_EXACTLY_TWO_ARMS", path,
            f"arms must be exactly one control and one treatment; found roles {roles}."))
    axis_id = str(primary_axis.get("id", "")).strip() if isinstance(primary_axis, dict) else ""
    if axis_id != EXPECTED_PRIMARY_AXIS:
        errors.append(format_error("CONDITION_DESIGN_REQUIRES_SINGLE_PRIMARY_AXIS", path,
            f"primary_intervention_axis.id must be {EXPECTED_PRIMARY_AXIS!r}; found {axis_id!r}."))
    elif control_arm and treatment_arm and str(control_arm.get("workflow_protocol", "")).strip() == str(treatment_arm.get("workflow_protocol", "")).strip():
        errors.append(format_error("CONDITION_DESIGN_REQUIRES_SINGLE_PRIMARY_AXIS", path,
            "the two arms must take different workflow_protocol values."))
    if EXPECTED_PRIMARY_AXIS in set(_ids(controlled)):
        errors.append(format_error("CONDITION_DESIGN_REQUIRES_PRIMARY_AXIS_NOT_CONTROLLED", path,
            "the primary axis must not also appear in controlled_dimensions."))

    # --- input-assembly component refs (used by render + assembly checks) -----
    cia = data.get("condition_input_assembly") or {}
    comp = cia.get("components") or {}
    cia_arms = cia.get("arms") or {}
    benchmark_ref = str((comp.get("benchmark") or {}).get("ref", ""))
    shared_ref = str((comp.get("shared_condition") or {}).get("ref", ""))

    # --- single-axis + blinded delivery: rendered from one structured source --
    wf_ref = str(data.get("workflow_instruction_source_ref", ""))
    _, wf, wf_prob = load(wf_ref)
    spec_first_basis = None
    if spec_first_res is not None:
        spec_first_basis, _ = _read_text_strict(spec_first_res)
    overlay_text = {}
    render_problems = []
    if wf is None:
        render_problems.append(f"workflow source {display_source_path(wf_ref)} {wf_prob}")
    else:
        render_problems += _child_identity_problems("workflow", wf, data)
        # the shared condition (common-condition.md) is the deterministic render of the delivered surface
        try:
            expected_shared = render_shared_condition(wf)
        except (ValueError, KeyError, TypeError) as exc:
            expected_shared = None
            render_problems.append(f"shared condition could not be rendered: {exc}")
        sc_res, _, sc_prob = load(shared_ref, as_yaml=False)
        if sc_prob is not None:
            render_problems.append(f"shared condition {sc_prob}")
        elif expected_shared is not None:
            actual_shared, _ = _read_text_strict(sc_res)
            if actual_shared != expected_shared:
                render_problems.append("common-condition.md is not byte-equal to render_shared_condition()")
        # the two overlays are rendered from the delivered surface; treatment is grounded in the frozen spec-first body
        for role in ROLES:
            arm = control_arm if role == "control" else treatment_arm
            if not arm:
                continue
            ores, _, oprob = load(str(arm.get("overlay_ref", "")), as_yaml=False)
            if oprob is not None:
                render_problems.append(f"{role} overlay {oprob}")
                continue
            try:
                expected = render_arm_overlay(wf, role, spec_first_basis if role == "treatment" else None)
            except (ValueError, KeyError, TypeError) as exc:
                render_problems.append(f"{role} overlay could not be rendered: {exc}")
                continue
            actual, _ = _read_text_strict(ores)
            if actual != expected:
                render_problems.append(f"{role} overlay is not byte-equal to render_arm_overlay()")
            else:
                overlay_text[role] = actual
        # control = absence: the treatment overlay must be the control overlay plus the appended delta
        if "control" in overlay_text and "treatment" in overlay_text and not overlay_text["treatment"].startswith(overlay_text["control"]):
            render_problems.append("treatment overlay must extend the control overlay (control = absence of the added requirement)")
    if render_problems:
        errors.append(format_error("CONDITION_DESIGN_REQUIRES_SINGLE_AXIS_RENDER", path,
            "the delivered shared condition and arm overlays must be byte-equal to the deterministic "
            "render of the single structured workflow-instruction source (treatment grounded in the "
            "frozen spec-first body); " + "; ".join(render_problems)))

    # --- material contrast (assigned semantics from non-delivered control_metadata) ---
    if wf is not None:
        cm_arms = (wf.get("control_metadata") or {}).get("arms") or {}
        cs = cm_arms.get("control") or {}
        ts = cm_arms.get("treatment") or {}
        sections = {str(x).strip() for x in ((wf.get("delivered_treatment_addendum") or {}).get("required_specification_sections") or [])}
        mat = []
        if cs.get("pre_implementation_specification_required") is not False or cs.get("implementation_may_begin_immediately") is not True or cs.get("specification_completeness_check_required") is not False:
            mat.append("control_metadata.arms.control must carry no assigned upfront-specification requirement")
        if ts.get("pre_implementation_specification_required") is not True or ts.get("implementation_may_begin_immediately") is not False or ts.get("specification_completeness_check_required") is not True:
            mat.append("control_metadata.arms.treatment must require a completeness-checked upfront specification")
        if not all(s in sections for s in MANDATORY_TREATMENT_SECTIONS):
            mat.append("delivered_treatment_addendum.required_specification_sections must cover: " + ", ".join(MANDATORY_TREATMENT_SECTIONS))
        if control_arm and str(control_arm.get("workflow_protocol", "")).strip() != CONTROL_WP:
            mat.append(f"control workflow_protocol must be {CONTROL_WP!r}")
        if treatment_arm and str(treatment_arm.get("workflow_protocol", "")).strip() != TREATMENT_WP:
            mat.append(f"treatment workflow_protocol must be {TREATMENT_WP!r}")
        if mat:
            errors.append(format_error("CONDITION_DESIGN_REQUIRES_MATERIAL_CONTRAST", path,
                "the assigned workflow-instruction contrast must be material and pre-execution observable; " + "; ".join(mat)))

    # --- input assembly: components, fixed order, benchmark + shared binding --
    asm = []
    if snapshot is not None:
        ch_snap = str(((snapshot.get("sources") or {}).get("challenge") or {}).get("snapshot_path", ""))
        if benchmark_ref != ch_snap:
            asm.append("components.benchmark.ref must be the frozen challenge snapshot from the precondition snapshot")
    # shared_condition must bind exactly to the bundle's common-condition.md (boundary 2)
    sc_resolved, sc_code = resolve_repo_relative_path(shared_ref, repo_root, must_exist=True)
    if sc_code is not None or sc_resolved is None or sc_resolved != (bundle_dir / "common-condition.md").resolve():
        asm.append("components.shared_condition.ref must be the bundle's common-condition.md")
    for role, arm in (("control", control_arm), ("treatment", treatment_arm)):
        entry = cia_arms.get(role) or {}
        if str(entry.get("overlay_ref", "")).strip() != str((arm or {}).get("overlay_ref", "")).strip():
            asm.append(f"assembly.arms.{role}.overlay_ref disagrees with arms[{role}].overlay_ref")
        if list(entry.get("composition_order") or []) != ["benchmark", "shared_condition", "arm_overlay"]:
            asm.append(f"assembly.arms.{role}.composition_order must be [benchmark, shared_condition, arm_overlay]")
    if asm:
        errors.append(format_error("CONDITION_DESIGN_REQUIRES_INPUT_ASSEMBLY", path,
            "the input assembly must compose the frozen benchmark, the bundle's shared condition, and the "
            "arm overlay in a fixed identical order; " + "; ".join(asm)))

    # --- prompt-component role binding: spec-first grounding (boundary 2) -----
    grounding = []
    spec_first_snap = str(((snapshot or {}).get("sources") or {}).get("spec_first", {}).get("snapshot_path", "")) if snapshot else ""
    if treatment_arm is not None:
        tref = str((treatment_arm.get("spec_first_basis") or {}).get("snapshot_ref", "")).strip()
        if not tref:
            grounding.append("treatment arm must declare spec_first_basis.snapshot_ref")
        elif spec_first_snap and tref != spec_first_snap:
            grounding.append("treatment spec_first_basis.snapshot_ref must be the frozen spec-first snapshot")
    if control_arm is not None and control_arm.get("spec_first_basis") is not None:
        grounding.append("control arm must NOT carry a spec_first_basis (control = absence of grounding)")
    if grounding:
        errors.append(format_error("CONDITION_DESIGN_REQUIRES_SPEC_FIRST_BASIS", path,
            "only the treatment arm is grounded in the frozen spec-first snapshot; control is not; "
            + "; ".join(grounding)))

    # --- delivered-prompt blinding + control-as-absence + normalization -------
    errors += _prompt_exposure_errors(bundle_dir, path)
    errors += _operative_distinctness_errors(data, bundle_dir, repo_root, path)
    errors += _closed_bundle_errors(data, snapshot, bundle_dir, repo_root, path)
    errors += _prompt_scope_errors(data, path)

    # --- assigned vs observed separation -------------------------------------
    aso = []
    ccr = data.get("condition_compliance_requirements") or {}
    if not (isinstance(ccr, dict) and (ccr.get("required_future_evidence") or [])):
        aso.append("condition_compliance_requirements.required_future_evidence is empty")
    surfaces = data.get("artifact_surfaces") or {}
    arm_proc = (surfaces.get("arm_specific_process_artifacts") or {}) if isinstance(surfaces, dict) else {}
    if "preimplementation_specification" not in [str(x).strip() for x in (arm_proc.get("treatment") or [])]:
        aso.append("treatment arm_specific_process_artifacts must include 'preimplementation_specification'")
    if [str(x).strip() for x in (arm_proc.get("control") or [])]:
        aso.append("control must have no arm-specific process artifacts")
    if aso:
        errors.append(format_error("CONDITION_DESIGN_REQUIRES_ASSIGNED_VS_OBSERVED_SEPARATION", path,
            "assigned condition and observed compliance must be separated; " + "; ".join(aso)))

    # --- measurement semantics (beyond closed schema) ------------------------
    _, meas, meas_prob = load(str((data.get("measurement_surface") or {}).get("protocol_ref", "")))
    mproblems = []
    if meas is None:
        mproblems.append(f"measurement protocol {meas_prob}")
    else:
        mproblems += _child_identity_problems("measurement", meas, data)
        metrics = [m for key in ("primary_metrics", "secondary_metrics") for m in (meas.get(key) or []) if isinstance(m, dict)]
        ids = [str(m.get("id", "")).strip() for m in metrics]
        for dup in _duplicates(ids):
            mproblems.append(f"duplicate metric id: {dup}")
        if COMPLIANCE_METRIC_ID not in ids:
            mproblems.append(f"missing mandatory metric '{COMPLIANCE_METRIC_ID}'")
        for m in metrics:
            mid = str(m.get("id", "")).strip() or "<unnamed>"
            if str(m.get("unit", "")).strip() == "ratio":
                rng = m.get("range") or {}
                if rng.get("minimum") != 0 or rng.get("maximum") != 1:
                    mproblems.append(f"ratio metric {mid} range must be exactly 0..1")
            if mid == "time_to_validated_change_seconds":
                if str(m.get("timer_end", "")).strip() != "shared_verification_first_pass":
                    mproblems.append("time_to_validated_change_seconds must end at shared_verification_first_pass")
                if str(m.get("value_if_aborted_before_pass", "")).strip().lower() != "null":
                    mproblems.append("time_to_validated_change_seconds must be null when aborted before pass")
    if mproblems:
        errors.append(format_error("CONDITION_DESIGN_REQUIRES_SHARED_MEASUREMENT", path,
            "the shared measurement protocol must use 0..1 ratio ranges, unique metric ids, the compliance "
            "metric, and abort-safe timing; " + "; ".join(mproblems)))

    # --- child identity (verification too) -----------------------------------
    cidp = []
    for label, blk in (("verification_surface", data.get("verification_surface")),):
        ref = str((blk or {}).get("protocol_ref", "")) if isinstance(blk, dict) else ""
        _, doc, _ = load(ref)
        if doc is not None:
            cidp += _child_identity_problems(label, doc, data)
    if cidp:
        errors.append(format_error("CONDITION_DESIGN_REQUIRES_CHILD_IDENTITY", path,
            "every child protocol must carry the design identity; " + "; ".join(cidp)))

    # --- bundle boundary -----------------------------------------------------
    boundary = []
    for raw_ref, lbl in _bundle_refs(data):
        resolved, rc = resolve_repo_relative_path(raw_ref, repo_root, must_exist=True)
        if rc is not None or resolved is None:
            continue
        if not resolved.is_file():
            boundary.append(f"{lbl}={display_source_path(raw_ref)}: not a regular file")
        elif not _inside(resolved, bundle_dir):
            boundary.append(f"{lbl}={display_source_path(raw_ref)}: outside the design bundle")
    if boundary:
        errors.append(format_error("CONDITION_DESIGN_REQUIRES_BUNDLE_BOUNDARY", path,
            "every bundle artifact must live inside the design bundle directory; " + "; ".join(boundary)))

    # --- freeze --------------------------------------------------------------
    errors += _freeze_errors(data, snapshot, bundle_dir, repo_root, path)

    # --- recursive execution artifacts ---------------------------------------
    exe = _execution_artifact_problems(bundle_dir)
    if exe:
        errors.append(format_error("CONDITION_DESIGN_FORBIDS_EXECUTION_ARTIFACTS", path,
            "the design bundle must contain no execution artifacts at any depth; offending: " + ", ".join(exe)))

    # --- unique semantic ids -------------------------------------------------
    dupp = []
    for lbl, items in (("arms", arms), ("controlled_dimensions", controlled), ("confounder_controls", confounders)):
        d = _duplicates(_ids(items))
        if d:
            dupp.append(f"{lbl}: " + ", ".join(d))
    if dupp:
        errors.append(format_error("CONDITION_DESIGN_REQUIRES_UNIQUE_SEMANTIC_IDS", path,
            "ids must be unique within each list; " + "; ".join(dupp)))

    # --- mandatory non-claims ------------------------------------------------
    declared = {str(x).strip().lower() for x in (data.get("does_not_establish") or [])}
    missing = [x for x in MANDATORY_DOES_NOT_ESTABLISH if x not in declared]
    wrong = [x for x in FORBIDDEN_SELECTION_NON_CLAIMS if x in declared]
    if missing or wrong:
        detail = []
        if missing:
            detail.append("missing: " + ", ".join(missing))
        if wrong:
            detail.append("must not be listed: " + ", ".join(wrong))
        errors.append(format_error("CONDITION_DESIGN_REQUIRES_MANDATORY_NON_CLAIMS", path,
            "does_not_establish must include all baseline non-claims and deny none of the design's own contribution; " + "; ".join(detail)))

    # --- safe existing paths -------------------------------------------------
    safe = []
    for raw_ref, lbl in _bundle_refs(data):
        _, rc = resolve_repo_relative_path(raw_ref, repo_root, must_exist=True)
        if rc == "ESCAPE":
            safe.append(f"{lbl}={display_source_path(raw_ref)}: resolves outside the repo root")
        elif rc == "NOT_FOUND":
            safe.append(f"{lbl}={display_source_path(raw_ref)}: does not exist")
    for entry in (data.get("source_evidence") or []):
        if not isinstance(entry, dict):
            continue
        raw_ref = str(entry.get("path", ""))
        resolved, rc = resolve_repo_relative_path(raw_ref, repo_root, must_exist=True)
        if rc == "ESCAPE":
            safe.append(f"source_evidence {display_source_path(raw_ref)}: resolves outside the repo root")
        elif rc == "NOT_FOUND":
            safe.append(f"source_evidence {display_source_path(raw_ref)}: does not exist")
        elif resolved is not None and not resolved.is_file():
            safe.append(f"source_evidence {display_source_path(raw_ref)}: not a regular file")
    if safe:
        errors.append(format_error("CONDITION_DESIGN_REQUIRES_SAFE_EXISTING_PATHS", path,
            "every referenced bundle/context path must be a safe, existing, regular file; " + "; ".join(safe)))

    return errors


def _freeze_errors(data, snapshot, bundle_dir, repo_root, path):
    fr = data.get("freeze") or {}
    manifest_rel = str(fr.get("freeze_manifest_ref", ""))
    mres, manifest, prob = _load_bundle_file(manifest_rel, bundle_dir, repo_root, as_yaml=True)
    if manifest is None:
        return [format_error("CONDITION_DESIGN_REQUIRES_VALID_FREEZE", path, f"freeze manifest {display_source_path(manifest_rel)} {prob}")]
    p = _child_identity_problems("freeze", manifest, data)
    captured_at = _parse_rfc3339((snapshot or {}).get("captured_at")) if snapshot else None
    frozen_at = _parse_rfc3339(manifest.get("frozen_at"))
    if frozen_at is None:
        p.append(f"frozen_at is not a real RFC-3339 timestamp ({manifest.get('frozen_at')!r})")
    if captured_at is not None and frozen_at is not None and captured_at > frozen_at:
        p.append("captured_at must be <= frozen_at")
    entries = manifest.get("hashes") or []
    declared_paths, hashed_ok, declared_resolved = [], set(), set()
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        rel = str(entry.get("path", "")); declared = str(entry.get("sha256", "")).strip().lower()
        declared_paths.append(rel)
        resolved, code = resolve_repo_relative_path(rel, repo_root, must_exist=True)
        if code is not None or resolved is None or not resolved.is_file():
            p.append(f"hashed path {display_source_path(rel)} is not a safe existing regular file"); continue
        if not _inside(resolved, bundle_dir):
            p.append(f"hashed path {display_source_path(rel)} is outside the bundle"); continue
        declared_resolved.add(resolved)
        if not SHA256_RE.match(declared):
            p.append(f"hashed path {display_source_path(rel)} has a malformed sha256"); continue
        if _sha256_of(resolved) != declared:
            p.append(f"sha256 mismatch for {display_source_path(rel)}"); continue
        hashed_ok.add(resolved)
    for dup in _duplicates(declared_paths):
        p.append(f"duplicate hashed path: {display_source_path(dup)}")
    if mres is not None and mres in declared_resolved:
        p.append("freeze manifest must not hash itself")
    for rel in _covered_bundle_files(data, snapshot):
        resolved, code = resolve_repo_relative_path(rel, repo_root, must_exist=True)
        if code is None and resolved is not None and resolved not in hashed_ok:
            p.append(f"bundle file not covered by a valid freeze hash: {display_source_path(rel)}")
    if p:
        return [format_error("CONDITION_DESIGN_REQUIRES_VALID_FREEZE", path,
            "the freeze manifest must be identity-matched, real-dated (captured_at<=frozen_at), acyclic, "
            "and cover every bundle file; " + "; ".join(p))]
    return []


def validate_file(path: Path, validator: Draft202012Validator, repo_root: Path | None = None):
    root = repo_root if repo_root is not None else REPO_ROOT
    try:
        data = load_yaml(path)
    except (FileNotFoundError, ValueError) as exc:
        return 2, [f"ERROR path={display_path(path)}: {exc}"]
    errs = schema_errors(validator, data, path)
    if errs:
        return 2, errs
    child_errs = child_schema_errors(data, path, root)
    if child_errs:
        return 2, child_errs
    try:
        sem = semantic_errors(data, path, root)
    except ToolError as exc:
        return 2, [f"ERROR rule=CONDITION_DESIGN_REQUIRES_GIT_SOURCE_PROVENANCE path={display_path(path)}: {exc}"]
    if sem:
        return 1, sem
    return 0, []


def discover_artifacts(repo_root: Path):
    exp = repo_root / "experiments"
    if not exp.is_dir():
        return []
    # The canonical path pattern IS the identity: every condition-design.yml under
    # experiments/*/artifacts/*/ is a candidate. We deliberately do NOT filter by artifact_type
    # here — a malformed or mistyped artifact must reach the schema (and fail exit 2), never
    # silently vanish from discovery into a green "skipped".
    return sorted(exp.glob(DESIGN_GLOB))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate Model-Lab condition-design artifacts.")
    parser.add_argument("paths", nargs="*")
    args = parser.parse_args(argv)
    try:
        validator = load_validator(SCHEMA_PATH)
        for sp in CHILD_SCHEMA.values():
            load_validator(sp)
    except RuntimeError as exc:
        print(f"ERROR: {exc}"); return 2
    if args.paths:
        paths = [Path(r) if Path(r).is_absolute() else (REPO_ROOT / r) for r in args.paths]
    else:
        paths = discover_artifacts(REPO_ROOT)
        if not paths:
            print("ERROR: no model-lab-condition-design artifact found; the canonical design must "
                  "exist and be discoverable (empty discovery is a failure, not a skip).")
            return 2
    highest, passed = 0, 0
    for p in paths:
        code, errs = validate_file(p, validator)
        highest = max(highest, code)
        for e in errs:
            print(e)
        if code == 0:
            passed += 1; print(f"✅ {display_path(p)}")
    print(f"Model-lab-condition-design artifacts: checked={len(paths)}, passed={passed}, failed={len(paths) - passed}")
    return highest


if __name__ == "__main__":
    sys.exit(main())
