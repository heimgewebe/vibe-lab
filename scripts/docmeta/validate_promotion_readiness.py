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

  Erkennung: Wenn falsifiability.counter_hypotheses vorhanden → structured v1.
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

Zukünftige Phasen (nicht in diesem PR):
  * Phase 2: Hard-Fail nur für NEUE Experimente via freeze-list.
  * Phase 3: globaler Hard-Fail.

Determinismus:
  * Keine Timestamps im Output.
  * Stabile Sortierung (Pfade, Listen).
  * write_if_changed() → zweimaliger Lauf erzeugt kein git diff.
  * Keine absoluten Maschinenpfade, keine PII.
"""

from __future__ import annotations

import json
import sys
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
    """True wenn der Block das structured v1-Format verwendet (counter_hypotheses-Key)."""
    return "counter_hypotheses" in fal


def evaluate_falsifiability_structured(fal: dict) -> tuple[list[str], list[str]]:
    """Bewertet ein structured-Format-v1-Falsifiability-Objekt.

    Gibt (missing, warnings) zurück. ``missing`` enthält blocking Signale,
    die promotion_ready verhindern. ``warnings`` sind nicht-blockierende Hinweise.

    Blocking-Regeln:
      - assessment.status ∈ {documented, pending} → assessment_not_checked
      - status ∈ {partially_checked, checked} + outcome ∈ {inconclusive, mixed}
        + pending_checks non-empty → assessment_pending_blocking
      - status == checked + outcome == supports_primary + pending_checks non-empty
        → assessment_pending_blocking
      - outcome == supports_counterhypothesis → assessment_counterhypothesis_supported
      - status == blocked → assessment_blocked

    Non-blocking:
      - outcome ∈ {inconclusive, mixed} + pending_checks leer → warning inconclusive
      - status ∈ {partially_checked, checked} + keine evidence_refs → warning
    """
    missing: list[str] = []
    warnings: list[str] = []

    fc = fal.get("falsification_criterion")
    if not isinstance(fc, str) or len(fc.strip()) < FALSIFIABILITY_MIN_LEN:
        missing.append("falsifiability.falsification_criterion_missing_or_short")

    chs = fal.get("counter_hypotheses")
    if not isinstance(chs, list) or len(chs) == 0:
        missing.append("falsifiability.counter_hypotheses_empty")
        return missing, warnings

    any_not_checked = False
    any_pending_blocking = False
    any_counterhypothesis_supported = False
    any_blocked = False
    any_inconclusive_no_pending = False
    any_evidence_refs_missing = False

    for ch in chs:
        if not isinstance(ch, dict):
            any_not_checked = True
            continue

        assessment = ch.get("assessment")
        if not isinstance(assessment, dict):
            any_not_checked = True
            continue

        status = assessment.get("status", "")
        outcome = assessment.get("outcome", "")
        pending = assessment.get("pending_checks") or []
        evidence_refs = assessment.get("evidence_refs") or []

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

        # evidence_refs recommended for partially_checked/checked
        if status in ("partially_checked", "checked") and not evidence_refs:
            any_evidence_refs_missing = True

    if any_not_checked:
        missing.append("falsifiability.assessment_not_checked")
    if any_pending_blocking:
        missing.append("falsifiability.assessment_pending_blocking")
    if any_counterhypothesis_supported:
        missing.append("falsifiability.assessment_counterhypothesis_supported")
    if any_blocked:
        missing.append("falsifiability.assessment_blocked")
    if any_inconclusive_no_pending:
        warnings.append("falsifiability_assessment_inconclusive")
    if any_evidence_refs_missing:
        warnings.append("falsifiability.evidence_refs_missing")

    return missing, warnings


def evaluate_falsifiability(state: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Bewertet das falsifiability-Objekt.

    Routed zu structured (v1) oder legacy Evaluierung je nach Block-Form:
      - Structured: ``counter_hypotheses`` Key vorhanden → evaluate_falsifiability_structured()
      - Legacy: ``counter_hypothesis`` + ``falsification_criterion`` + ``counterevidence_checked``

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


def main() -> int:
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
    print()
    print("  (dry-run: exit=0 by design; see scripts/docmeta/validate_promotion_readiness.py)")

    # Dry-Run: exit=0 auch bei not_ready.
    return 0


if __name__ == "__main__":
    sys.exit(main())
