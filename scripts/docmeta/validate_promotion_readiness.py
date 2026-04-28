#!/usr/bin/env python3
"""validate_promotion_readiness.py — Dry-Run Promotion-Readiness Gate (Phase 1).

Trigger: need_for_reproducibility.

Zweck:
  Erzeugt einen deterministischen Diagnose-Report unter
  ``docs/_generated/promotion-readiness.json``. Der Report markiert
  Experimente, denen explizite Falsifizierbarkeitsstruktur fehlt, obwohl
  ihr Zustand (executed / replicated / adopted-auf-executed-Basis) eine
  Begründungspflicht triggern würde.

Leitthese:
  Nicht Wahrheit quantifizieren, sondern Bestätigung verteuern.

Falsifizierbarkeits-Formate (Phase 1):
  Legacy-Format (rückwärtskompatibel):
    experiment.falsifiability:
      counter_hypothesis: "<string>"
      falsification_criterion: "<string>"
      counterevidence_checked: <bool>

  Structured-Format v1 (bevorzugt für neue Manifeste):
    experiment.falsifiability:
      version: 1
      falsification_criterion: "<string>"
      counter_hypotheses:
        - id: "<slug>"
          statement: "<string>"
          assessment:
            status: documented | pending | partially_checked | checked | blocked | not_applicable
            outcome: not_checked | inconclusive | supports_primary | supports_counterhypothesis | mixed | not_applicable
            evidence_refs: [{path, section}]
            pending_checks: [<string>]
            limitations: [<string>]
            confidence: low | medium | high

  Erkennung: Wenn 'version' oder 'counter_hypotheses' Key vorhanden → Structured-Intent → v1.
  Sonst → legacy. Legacy bleibt dauerhaft akzeptiert, aber deprecated für neue Manifeste.

Structured-Format Semantik-Gate:
  Blocking (→ missing[], → promotion_ready=false):
    - assessment.status ∈ {documented, pending}: Gegenhypothese noch nicht geprüft.
    - assessment.status ∈ {partially_checked, checked} + outcome ∈ {inconclusive, mixed}
      + pending_checks non-empty: Ausstehende Checks blockieren.
    - assessment.status == checked + outcome == supports_primary + pending_checks non-empty:
      Blocking pending checks trotz positiver Richtung.
    - assessment.outcome == supports_counterhypothesis: Gegenhypothese gestützt.
    - assessment.status == blocked: Prüfung blockiert.

  Non-blocking (→ warnings[]):
    - status ∈ {partially_checked, checked} + outcome ∈ {inconclusive, mixed}
      + pending_checks leer: inconclusive, aber alle Checks abgeschlossen.
    - status ∈ {partially_checked, checked} + keine evidence_refs.

Nicht-Ziele (Phase 1):
  * Kein Hard-Fail. Exit-Code ist immer 0, außer das Script crasht selbst.
  * Kein Auto-Move experiments/* → catalog/*.
  * Kein truth_confidence-Score.
  * Kein Bruch für adoption_basis=reconstructed (historischer Escape,
    siehe docs/blueprints/blueprint-v2.md Übergangsregel) — solche
    Experimente werden als ``historical_escape`` markiert, nie blockiert.

Aktuelle Phasen:
  * Phase 1 (Default): Dry-run-Report, exit=0 bei not_ready.
  * Phase 2 (--ratchet): Hard-Fail für neue nicht eingefrorene Verstöße
    gegen die Freeze-Baseline.
  * Phase 3: globaler Hard-Fail ohne Freeze-Baseline (zukünftige Option).

Determinismus:
  * Keine Timestamps im Output.
  * Stabile Sortierung (Pfade, Listen).
  * write_if_changed() → zweimaliger Lauf erzeugt kein git diff.
  * Keine absoluten Maschinenpfade, keine PII.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

# Gemeinsame Pfad-Logik
sys.path.insert(0, str(Path(__file__).parent))
from _paths import write_if_changed  # noqa: E402

try:
    import yaml
except ImportError:
    print(
        "ERROR: Missing dependency 'pyyaml'. "
        "Run: python3 -m pip install pyyaml",
        file=sys.stderr,
    )
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REPORT_PATH = REPO_ROOT / "docs" / "_generated" / "promotion-readiness.json"
FREEZE_PATH = REPO_ROOT / ".vibe" / "promotion-readiness-freeze.yml"
REPORT_SCHEMA_VERSION = "0.1.0"
REPORT_MODE = "dry_run"
REPORT_TRIGGER = "need_for_reproducibility"

# Zustände, in denen Falsifizierbarkeit als Begründungspflicht getriggert wird.
EXECUTED_STATUSES: frozenset[str] = frozenset({"executed", "replicated"})

# Legacy-Format Pflichtfelder (wenn kein counter_hypotheses-Key vorhanden).
FALSIFIABILITY_FIELDS: tuple[str, ...] = (
    "counter_hypothesis",
    "falsification_criterion",
    "counterevidence_checked",
)

# Mindestlänge wie im Schema.
FALSIFIABILITY_MIN_LEN = 10

# Structured-Format v1: erlaubte Werte für assessment-Felder.
STRUCTURED_STATUSES: frozenset[str] = frozenset({
    "documented", "pending", "partially_checked", "checked", "blocked", "not_applicable",
})
STRUCTURED_OUTCOMES: frozenset[str] = frozenset({
    "not_checked", "inconclusive", "supports_primary",
    "supports_counterhypothesis", "mixed", "not_applicable",
})

# Statuses, bei denen die Gegenhypothese noch nicht geprüft wurde (blocking).
_NOT_CHECKED_STATUSES: frozenset[str] = frozenset({"documented", "pending"})
# Outcomes, die Unentschlossenheit ausdrücken.
_INCONCLUSIVE_OUTCOMES: frozenset[str] = frozenset({"inconclusive", "mixed"})


def load_manifest(path: Path) -> dict[str, Any] | None:
    """Lädt ein manifest.yml oder gibt None zurück bei Parse-Fehler."""
    try:
        with open(path) as f:
            data = yaml.safe_load(f) or {}
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    return data


def classify_experiment(manifest: dict[str, Any]) -> dict[str, Any]:
    """Bestimmt Zustandsmerkmale für ein Experiment aus dem Manifest."""
    exp = manifest.get("experiment", {}) or {}
    return {
        "status": exp.get("status", "") or "",
        "execution_status": exp.get("execution_status", "") or "",
        "adoption_basis": exp.get("adoption_basis", "") or "",
        "falsifiability": exp.get("falsifiability"),
    }


def falsifiability_trigger(state: dict[str, Any]) -> bool:
    """Greift die Falsifizierbarkeits-Pflicht für dieses Experiment?

    Trigger (P1 aus Plan):
      * execution_status ∈ {executed, replicated}, ODER
      * status = adopted UND adoption_basis ∈ {executed, replicated}.

    Ausdrücklich NICHT getriggert:
      * designed / prepared Experimente.
      * Adoption auf 'reconstructed'-Basis (historischer Escape).
    """
    if state["execution_status"] in EXECUTED_STATUSES:
        return True
    if state["status"] == "adopted" and state["adoption_basis"] in EXECUTED_STATUSES:
        return True
    return False


def is_historical_escape(state: dict[str, Any]) -> bool:
    """Markiert Experimente, die nur über den reconstructed-Pfad adoptiert sind.

    Diese werden nicht blockiert und nicht als 'not ready' gewertet;
    sie erhalten im Report das Flag ``historical_escape``.
    """
    return state["status"] == "adopted" and state["adoption_basis"] == "reconstructed"


def _is_structured(fal: dict) -> bool:
    """True wenn der Block Structured-Intent hat: 'version' oder 'counter_hypotheses' Key vorhanden.

    Structured-Intent: Block wird als v1 evaluiert, auch wenn er malformed ist.
    Ungültige oder fehlende version ist ein blocking Structured-Signal, kein Legacy-Fallback.
    """
    return "version" in fal or "counter_hypotheses" in fal


def evaluate_falsifiability_structured(fal: dict) -> tuple[list[str], list[str]]:
    """Bewertet ein structured-Format-v1-Falsifiability-Objekt.

    Gibt (missing, warnings) zurück. ``missing`` enthält blocking Signale,
    die promotion_ready verhindern. ``warnings`` sind nicht-blockierende Hinweise.

    Strukturelle Blocking-Regeln (Enum/Version-Validierung):
      - version fehlt oder ist nicht 1 → version_invalid_or_missing
      - counter_hypotheses fehlt, kein Array oder leer → counter_hypotheses_empty
      - Item in counter_hypotheses kein Dict → counter_hypothesis_invalid
      - assessment fehlt oder kein Dict → assessment_missing
      - status fehlt oder nicht in STRUCTURED_STATUSES → assessment_invalid_status
      - outcome fehlt oder nicht in STRUCTURED_OUTCOMES → assessment_invalid_outcome
      Ungültige status/outcome-Werte dürfen NICHT in die semantische Logik fallen.

    Semantische Blocking-Regeln (nur für valide status/outcome):
      - assessment.status ∈ {documented, pending} → assessment_not_checked
      - status ∈ {partially_checked, checked} + outcome ∈ {inconclusive, mixed}
        + pending_checks non-empty → assessment_pending_blocking
      - status == checked + outcome == supports_primary + pending_checks non-empty
        → assessment_pending_blocking
      - outcome == supports_counterhypothesis → assessment_counterhypothesis_supported
      - status == blocked → assessment_blocked

    Non-blocking (→ warnings[]):
      - outcome ∈ {inconclusive, mixed} + pending_checks leer → falsifiability_assessment_inconclusive
      - status ∈ {partially_checked, checked} + keine evidence_refs → evidence_refs_missing
    """
    missing: list[str] = []
    warnings: list[str] = []

    # Version: muss 1 sein.
    version = fal.get("version")
    if version != 1:
        missing.append("falsifiability.version_invalid_or_missing")

    fc = fal.get("falsification_criterion")
    if not isinstance(fc, str) or len(fc.strip()) < FALSIFIABILITY_MIN_LEN:
        missing.append("falsifiability.falsification_criterion_missing_or_short")

    chs = fal.get("counter_hypotheses")
    if not isinstance(chs, list) or len(chs) == 0:
        missing.append("falsifiability.counter_hypotheses_empty")
        return missing, warnings

    any_invalid_hypothesis = False
    any_missing_assessment = False
    any_invalid_status = False
    any_invalid_outcome = False
    any_not_checked = False
    any_pending_blocking = False
    any_counterhypothesis_supported = False
    any_blocked = False
    any_inconclusive_no_pending = False
    any_evidence_refs_missing = False
    any_evidence_refs_invalid = False

    for ch in chs:
        if not isinstance(ch, dict):
            any_invalid_hypothesis = True
            continue

        assessment = ch.get("assessment")
        if not isinstance(assessment, dict):
            any_missing_assessment = True
            continue

        status = assessment.get("status")
        outcome = assessment.get("outcome")

        status_valid = isinstance(status, str) and status in STRUCTURED_STATUSES
        outcome_valid = isinstance(outcome, str) and outcome in STRUCTURED_OUTCOMES

        if not status_valid:
            any_invalid_status = True
        if not outcome_valid:
            any_invalid_outcome = True

        # Invalid status/outcome must not fall through into semantic logic.
        if not status_valid or not outcome_valid:
            continue
        pending = assessment.get("pending_checks") or []

        # Deep-validate evidence_refs if present.
        raw_refs = assessment.get("evidence_refs")
        this_refs_invalid = False
        if raw_refs is not None:
            if not isinstance(raw_refs, list):
                this_refs_invalid = True
            else:
                for ref in raw_refs:
                    if not isinstance(ref, dict) or not ref.get("path"):
                        this_refs_invalid = True
                        break
        if this_refs_invalid:
            any_evidence_refs_invalid = True
        evidence_refs = raw_refs if isinstance(raw_refs, list) else []

        if status in _NOT_CHECKED_STATUSES:
            any_not_checked = True
            continue

        if status == "blocked":
            any_blocked = True
            continue

        # outcome check (independent of status)
        if outcome == "supports_counterhypothesis":
            any_counterhypothesis_supported = True

        # inconclusive/mixed outcomes for partially_checked or checked
        if status in ("partially_checked", "checked") and outcome in _INCONCLUSIVE_OUTCOMES:
            if pending:
                any_pending_blocking = True
            else:
                any_inconclusive_no_pending = True

        # checked + supports_primary but pending checks remain → blocking
        if status == "checked" and outcome == "supports_primary" and pending:
            any_pending_blocking = True

        # evidence_refs recommended for partially_checked/checked;
        # suppress if refs were present-but-invalid (different signal).
        if status in ("partially_checked", "checked") and not evidence_refs and not this_refs_invalid:
            any_evidence_refs_missing = True

    # Structural blocking signals (enum/format violations).
    if any_invalid_hypothesis:
        missing.append("falsifiability.counter_hypothesis_invalid")
    if any_missing_assessment:
        missing.append("falsifiability.assessment_missing")
    if any_invalid_status:
        missing.append("falsifiability.assessment_invalid_status")
    if any_invalid_outcome:
        missing.append("falsifiability.assessment_invalid_outcome")

    # Semantic blocking signals (only reached for valid status/outcome).
    if any_not_checked:
        missing.append("falsifiability.assessment_not_checked")
    if any_pending_blocking:
        missing.append("falsifiability.assessment_pending_blocking")
    if any_counterhypothesis_supported:
        missing.append("falsifiability.assessment_counterhypothesis_supported")
    if any_blocked:
        missing.append("falsifiability.assessment_blocked")

    # Non-blocking signals.
    if any_inconclusive_no_pending:
        warnings.append("falsifiability_assessment_inconclusive")
    if any_evidence_refs_missing:
        warnings.append("falsifiability.evidence_refs_missing")
    if any_evidence_refs_invalid:
        warnings.append("falsifiability.evidence_refs_invalid")

    return missing, warnings


def evaluate_falsifiability(state: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Bewertet das falsifiability-Objekt.

    Routed zu structured (v1) oder legacy Evaluierung je nach Block-Form:
      - Structured-Intent: ``version`` oder ``counter_hypotheses`` Key vorhanden
        → evaluate_falsifiability_structured() (auch bei malformed Blöcken).
        Ungültige/fehlende version erzeugt blocking Signal, kein Legacy-Fallback.
      - Legacy: kein ``version``- und kein ``counter_hypotheses``-Key
        → counter_hypothesis + falsification_criterion + counterevidence_checked

    Legacy bleibt dauerhaft akzeptiert (rückwärtskompatibel). Für neue Manifeste
    ist das structured v1-Format bevorzugt.

    Gibt (missing, warnings) zurück. ``missing`` listet strukturelle
    Defizite, die die Promotion-Reife blockieren würden. ``warnings`` sind
    Hinweise, die nicht blockierend sind.
    """
    missing: list[str] = []
    warnings: list[str] = []

    fal = state["falsifiability"]
    if not isinstance(fal, dict):
        missing.append("falsifiability")
        return missing, warnings

    if _is_structured(fal):
        return evaluate_falsifiability_structured(fal)

    # Legacy-Format: counter_hypothesis + falsification_criterion + counterevidence_checked
    for field in FALSIFIABILITY_FIELDS:
        if field not in fal:
            missing.append(f"falsifiability.{field}")

    # String-Felder: strukturelle Mindestlänge; Nicht-String-Werte explizit erkennen
    for field in ("counter_hypothesis", "falsification_criterion"):
        val = fal.get(field)
        if field not in fal:
            continue
        if not isinstance(val, str):
            missing.append(f"falsifiability.{field}_not_string")
            continue
        if len(val.strip()) < FALSIFIABILITY_MIN_LEN:
            missing.append(f"falsifiability.{field}_too_short")

    # Soft-Hinweis: counterevidence_checked=false ist nicht strukturell
    # fehlerhaft, aber epistemisch signalpflichtig.
    cev = fal.get("counterevidence_checked")
    if cev is False:
        warnings.append("counterevidence_not_checked")

    return missing, warnings


def evaluate_experiment(exp_dir: Path) -> dict[str, Any] | None:
    """Bewertet ein einzelnes Experiment und gibt den Report-Eintrag zurück.

    Gibt None zurück, wenn das Experiment übersprungen wird (Template,
    Archive, fehlendes/invalides Manifest).
    """
    if exp_dir.name.startswith("_"):
        return None

    manifest_path = exp_dir / "manifest.yml"
    if not manifest_path.is_file():
        return None

    manifest = load_manifest(manifest_path)
    if manifest is None:
        # Ungültiges YAML — wird von validate_schema.py bereits gemeldet,
        # hier nicht doppelt erzeugen. Report überspringt den Eintrag.
        return None

    state = classify_experiment(manifest)
    rel_path = exp_dir.relative_to(REPO_ROOT).as_posix()

    triggered = falsifiability_trigger(state)
    historical = is_historical_escape(state)

    missing: list[str] = []
    warnings: list[str] = []
    notes: list[str] = []

    if historical:
        notes.append("historical_escape")
        notes.append("adoption_basis_reconstructed")

    if triggered and not historical:
        m, w = evaluate_falsifiability(state)
        missing.extend(m)
        warnings.extend(w)
    elif state["falsifiability"] is not None and isinstance(state["falsifiability"], dict):
        # Falsifizierbarkeits-Block ist freiwillig präsent (z. B. Retrofit für
        # reconstructed oder designed). Strukturprüfung läuft, aber Ergebnis
        # beeinflusst promotion_ready nicht.
        _, w = evaluate_falsifiability(state)
        warnings.extend(w)
        notes.append("falsifiability_voluntary")

    promotion_ready = (len(missing) == 0)
    # Historischer Escape ist definitorisch nicht "ready" im neuen Sinn,
    # aber auch nicht "not_ready" — er wird gesondert markiert.
    if historical:
        promotion_ready = False
        notes.append("not_counted_against_promotion_readiness")

    return {
        "path": rel_path,
        "status": state["status"],
        "execution_status": state["execution_status"],
        "adoption_basis": state["adoption_basis"],
        "falsifiability_triggered": triggered,
        "historical_escape": historical,
        "promotion_ready": promotion_ready,
        "missing": sorted(missing),
        "warnings": sorted(warnings),
        "notes": sorted(notes),
    }


def build_report(experiment_entries: list[dict[str, Any]]) -> dict[str, Any]:
    """Baut den finalen Report mit deterministischer Sortierung."""
    entries_sorted = sorted(experiment_entries, key=lambda e: e["path"])

    checked = len(entries_sorted)
    ready = sum(1 for e in entries_sorted if e["promotion_ready"])
    historical = sum(1 for e in entries_sorted if e["historical_escape"])
    not_ready = sum(
        1 for e in entries_sorted
        if not e["promotion_ready"] and not e["historical_escape"]
    )
    warnings_total = sum(len(e["warnings"]) for e in entries_sorted)

    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "mode": REPORT_MODE,
        "trigger": REPORT_TRIGGER,
        "summary": {
            "experiments_checked": checked,
            "ready": ready,
            "not_ready": not_ready,
            "historical_escape": historical,
            "warnings": warnings_total,
        },
        "experiments": entries_sorted,
    }


def collect_experiments(experiments_dir: Path) -> list[dict[str, Any]]:
    """Sammelt Report-Einträge für alle Experimente (ohne _template/_archive)."""
    entries: list[dict[str, Any]] = []
    for sub in sorted(experiments_dir.iterdir()):
        if not sub.is_dir():
            continue
        entry = evaluate_experiment(sub)
        if entry is not None:
            entries.append(entry)
    return entries


def render_report(report: dict[str, Any]) -> str:
    """Rendert den Report deterministisch (sortierte Keys, LF, Newline am Ende)."""
    return json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


# ---------------------------------------------------------------------------
# Ratchet-Modus (Phase 2)
# ---------------------------------------------------------------------------

VALID_ALLOWED_MISSING: frozenset[str] = frozenset({
    "falsifiability",
    "falsifiability.counter_hypothesis",
    "falsifiability.falsification_criterion",
    "falsifiability.counterevidence_checked",
    "falsifiability.counter_hypothesis_not_string",
    "falsifiability.counter_hypothesis_too_short",
    "falsifiability.falsification_criterion_not_string",
    "falsifiability.falsification_criterion_too_short",
    "falsifiability.version_invalid_or_missing",
    "falsifiability.falsification_criterion_missing_or_short",
    "falsifiability.counter_hypotheses_empty",
    "falsifiability.counter_hypothesis_invalid",
    "falsifiability.assessment_missing",
    "falsifiability.assessment_invalid_status",
    "falsifiability.assessment_invalid_outcome",
    "falsifiability.assessment_not_checked",
    "falsifiability.assessment_pending_blocking",
    "falsifiability.assessment_counterhypothesis_supported",
    "falsifiability.assessment_blocked",
})

_ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _is_strict_iso_date(value: str) -> bool:
    if not _ISO_DATE_RE.fullmatch(value):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def load_freeze_config(freeze_path: Path) -> dict[str, Any] | None:
    if not freeze_path.is_file():
        return None
    try:
        with open(freeze_path) as f:
            data = yaml.safe_load(f) or {}
    except Exception as exc:
        return {"_load_error": str(exc)}
    if not isinstance(data, dict):
        return {"_load_error": "root is not a mapping"}
    return data


def validate_freeze_config(freeze_data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if "_load_error" in freeze_data:
        errors.append(f"freeze.load_error: {freeze_data['_load_error']}")
        return errors

    root = freeze_data.get("promotion_readiness_freeze")
    if not isinstance(root, dict):
        errors.append("freeze.missing_root_key: 'promotion_readiness_freeze' must be a mapping")
        return errors

    if root.get("version") != 1:
        errors.append(f"freeze.invalid_version: expected 1, got {root.get('version')!r}")

    reason = root.get("reason")
    if not isinstance(reason, str) or not reason.strip():
        errors.append("freeze.missing_reason: top-level reason must be a non-empty string")

    frozen_at = root.get("frozen_at")
    if not isinstance(frozen_at, str) or not frozen_at.strip():
        errors.append("freeze.missing_frozen_at: frozen_at must be a non-empty string")
    elif not _is_strict_iso_date(frozen_at):
        errors.append(
            "freeze.invalid_frozen_at: frozen_at must be a valid ISO date YYYY-MM-DD "
            f"(got {frozen_at!r})"
        )

    experiments = root.get("experiments")
    if not isinstance(experiments, list):
        errors.append("freeze.experiments_not_a_list: 'experiments' must be a list")
        return errors

    seen_paths: dict[str, int] = {}
    for i, entry in enumerate(experiments):
        prefix = f"freeze.experiments[{i}]"
        if not isinstance(entry, dict):
            errors.append(f"{prefix}: entry must be a mapping")
            continue

        path = entry.get("path")
        if not isinstance(path, str) or not path.strip():
            errors.append(f"{prefix}.path: must be a non-empty string")
        elif path in seen_paths:
            errors.append(
                f"freeze.duplicate_path: {path!r} appears more than once "
                f"(first at index {seen_paths[path]}, again at index {i})"
            )
        else:
            seen_paths[path] = i

        entry_reason = entry.get("reason")
        if not isinstance(entry_reason, str) or not entry_reason.strip():
            errors.append(f"{prefix}.reason: must be a non-empty string")

        allowed_missing = entry.get("allowed_missing")
        if not isinstance(allowed_missing, list) or len(allowed_missing) == 0:
            errors.append(f"{prefix}.allowed_missing: must be a non-empty list")
            continue
        seen_allowed: set[str] = set()
        for val in allowed_missing:
            if not isinstance(val, str):
                errors.append(
                    f"{prefix}.allowed_missing: value must be a string, "
                    f"got {type(val).__name__!r}"
                )
                continue
            if val in seen_allowed:
                errors.append(
                    f"{prefix}.allowed_missing.duplicate_value: {val!r} "
                    "appears more than once in this entry"
                )
            seen_allowed.add(val)
            if val not in VALID_ALLOWED_MISSING:
                errors.append(
                    f"{prefix}.allowed_missing: unknown value {val!r} "
                    "(valid: see VALID_ALLOWED_MISSING in validate_promotion_readiness.py)"
                )
    return errors


def ratchet_check(
    entries: list[dict[str, Any]],
    freeze_config: dict[str, Any],
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    root = freeze_config.get("promotion_readiness_freeze", {})
    frozen_list = root.get("experiments") or []
    frozen_by_path: dict[str, dict] = {}
    for fe in frozen_list:
        if isinstance(fe, dict) and isinstance(fe.get("path"), str):
            frozen_by_path[fe["path"]] = fe
    entry_by_path: dict[str, dict] = {e["path"]: e for e in entries}

    for entry in entries:
        if entry["promotion_ready"] or entry["historical_escape"]:
            continue
        path = entry["path"]
        actual_missing = set(entry["missing"])
        if path not in frozen_by_path:
            errors.append(
                f"ratchet.unregistered_violation: {path!r} is not_ready and not in freeze "
                f"(missing={sorted(actual_missing)})"
            )
            continue
        allowed = set((frozen_by_path[path] or {}).get("allowed_missing") or [])
        uncovered = sorted(actual_missing - allowed)
        excess = sorted(allowed - actual_missing)
        if uncovered:
            errors.append(
                f"ratchet.freeze_insufficient: {path!r} freeze does not cover "
                f"all missing signals (uncovered={uncovered})"
            )
        if excess:
            errors.append(
                f"ratchet.freeze_too_broad: {path!r} freeze allows more than needed "
                f"(excess={excess})"
            )

    for path in frozen_by_path:
        if path not in entry_by_path:
            errors.append(
                f"ratchet.stale_freeze_entry: {path!r} is in freeze but not found "
                "in evaluated experiments (deleted or renamed?)"
            )
            continue
        entry = entry_by_path[path]
        if entry["promotion_ready"]:
            errors.append(
                f"ratchet.obsolete_freeze_entry: {path!r} is now promotion_ready; "
                "remove it from .vibe/promotion-readiness-freeze.yml"
            )
        elif entry["historical_escape"]:
            errors.append(
                f"ratchet.obsolete_freeze_entry: {path!r} is a historical_escape; "
                "historical escapes do not need a freeze entry"
            )

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Promotion-Readiness validator. Default: dry-run (always exit 0). "
            "Use --ratchet for blocking Phase-2 checks."
        )
    )
    parser.add_argument("--ratchet", action="store_true", help="Enable blocking ratchet mode")
    args = parser.parse_args()

    experiments_dir = REPO_ROOT / "experiments"
    if not experiments_dir.is_dir():
        print(
            f"ERROR: experiments directory not found: {experiments_dir}",
            file=sys.stderr,
        )
        return 2

    entries = collect_experiments(experiments_dir)
    report = build_report(entries)
    content = render_report(report)

    changed = write_if_changed(REPORT_PATH, content)
    rel_report = REPORT_PATH.relative_to(REPO_ROOT).as_posix()

    print("🔎 Promotion-Readiness Dry-Run (Phase 1)")
    print(f"  trigger: {REPORT_TRIGGER}")
    print(f"  mode:    {REPORT_MODE}")
    print(f"  report:  {rel_report} ({'updated' if changed else 'unchanged'})")
    print(f"  checked: {report['summary']['experiments_checked']}")
    print(f"  ready:   {report['summary']['ready']}")
    print(f"  not_ready: {report['summary']['not_ready']}")
    print(f"  historical_escape: {report['summary']['historical_escape']}")
    print(f"  warnings: {report['summary']['warnings']}")

    not_ready_entries = [
        e for e in report["experiments"]
        if not e["promotion_ready"] and not e["historical_escape"]
    ]
    if not_ready_entries:
        print()
        print("  Not-ready experiments (dry-run, non-blocking):")
        for e in not_ready_entries:
            missing = ", ".join(e["missing"]) or "(none)"
            print(f"    - {e['path']}: missing={missing}")
    if not args.ratchet:
        print()
        print("  (dry-run: exit=0 by design; see scripts/docmeta/validate_promotion_readiness.py)")
        return 0

    print()
    print("  (Phase-1 dry-run report above is informational; --ratchet below is blocking.)")
    print()
    print("🔒 Ratchet Mode (Phase 2)")
    rel_freeze = FREEZE_PATH.relative_to(REPO_ROOT).as_posix()
    freeze_data = load_freeze_config(FREEZE_PATH)
    if freeze_data is None:
        print(f"  ERROR: --ratchet requires {rel_freeze} to exist.", file=sys.stderr)
        return 1
    config_errors = validate_freeze_config(freeze_data)
    if config_errors:
        print(f"  ERROR: {rel_freeze} is invalid:", file=sys.stderr)
        for err in config_errors:
            print(f"    - {err}", file=sys.stderr)
        return 1

    ratchet_errors, ratchet_warnings = ratchet_check(entries, freeze_data)
    if ratchet_warnings:
        print("  Warnings:")
        for warning in ratchet_warnings:
            print(f"    - {warning}")
    if ratchet_errors:
        print("  RATCHET FAILED — blocking violations found:", file=sys.stderr)
        for err in ratchet_errors:
            print(f"    ❌ {err}", file=sys.stderr)
        print(file=sys.stderr)
        print(
            "  To freeze a legitimate historical not_ready: add an entry with explicit\n"
            f"  reason to {rel_freeze}.",
            file=sys.stderr,
        )
        print(
            "  To add a genuinely new experiment: ensure falsifiability is present\n"
            "  before merging.",
            file=sys.stderr,
        )
        return 1

    frozen_count = len(
        (freeze_data.get("promotion_readiness_freeze") or {}).get("experiments") or []
    )
    print(
        f"  ✅ Ratchet passed: {len(not_ready_entries)} frozen not_ready case(s) tolerated, "
        f"{frozen_count} freeze entries validated."
    )
    print("     No unregistered violations. No stale or over-permissive freeze entries.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
