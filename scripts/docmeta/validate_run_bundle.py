#!/usr/bin/env python3
"""validate_run_bundle.py — Cross-File Validator für Experiment-Run-Bundles.

Verklammert die Bestandteile eines Experiment-Runs zu einer geprüften Einheit:

  manifest.yml ↔ results/evidence.jsonl ↔ artifacts/<run-id>/{run.yml,
                  auditor-output.yml, measurement.yml, run_meta.json}

Was hier geprüft wird (über die Form-Schemas hinaus):

R1  Wenn results/evidence.jsonl einen event_type=run enthält, darf
    manifest.experiment.execution_status nicht "prepared" sein.
R2  Bei execution_status ∈ {executed, replicated} muss execution_refs
    nicht leer sein und mindestens auf results/evidence.jsonl zeigen.
R3  Jeder Eintrag in execution_refs muss als Datei existieren.
R4  In evidence.jsonl referenzierte artifact_refs müssen existieren
    und innerhalb des Experiment-Roots liegen (zusätzlich zu der bereits
    in validate_schema.py durchgesetzten Regel — hier als Defense-in-Depth).
    Jede artifact_ref mit Dateiendung .md ist verboten — run events dürfen
    nur auf maschinell autorative YAML/JSON/JSONL-Artefakte verweisen.
R5  Wenn artifacts/<run-id>/run.yml existiert: gegen
    schemas/experiment-run-bundle.v1.schema.json validieren, jede
    artifacts.*-Pfadangabe muss existieren, canonical:true ist auf
    Markdown-Projektionen verboten.
R6  Wenn artifacts/<run-id>/auditor-output.yml existiert: gegen
    schemas/auditor-output.v1.schema.json validieren; PASS-Konsistenz
    und Severity-Precedence prüfen.
R7  Wenn artifacts/<run-id>/measurement.yml existiert: gegen
    schemas/measurement-run.v1.schema.json validieren; auditor_verdict
    muss zum Auditor-Output passen; unsupported_claim_count und
    validation_gap_count müssen aus den Auditor-Claims abgeleitet
    konsistent sein.
R8  Wenn ein Experiment execution_status ∈ {executed, replicated} hat und
    artifacts/<run-id>/run.yml existiert, muss jedes solche run.yml
    in manifest.execution_refs aufgeführt sein.

Legacy-Politik:
  Bestandsläufe ohne run.yml werden NICHT erzwungen. Der Validator
  arbeitet additiv: Er fasst nur die Bundles an, deren run.yml existiert,
  und die auditor-/measurement-YAMLs, die tatsächlich vorliegen. Bestehende
  Verträge (run_meta.json via validate_execution_proof.py, evidence.jsonl
  via validate_schema.py) bleiben unverändert.

Severity-Precedence (höher → strenger):
  CONTRADICTION > OUT_OF_SCOPE > MISSING_EVIDENCE > NOT_REPRODUCIBLE > CLAIM_NOT_PROVEN

Benötigt: python3 -m pip install pyyaml jsonschema rfc3339-validator
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Iterable

try:
    import yaml
    from jsonschema import Draft202012Validator, ValidationError
    from jsonschema.validators import validator_for
except ImportError:
    print(
        "ERROR: Missing dependencies. Run: "
        "python3 -m pip install pyyaml jsonschema rfc3339-validator"
    )
    sys.exit(1)


# Global constant used only by the CLI entry-point (main).
# validate_repo() receives repo_root as a parameter and loads schemas from
# repo_root/schemas/ — never from this module-level constant.
REPO_ROOT = Path(__file__).resolve().parent.parent.parent

PASS = "PASS"

# Höher = strenger.
SEVERITY: dict[str, int] = {
    "PASS": 0,
    "CLAIM_NOT_PROVEN": 1,
    "NOT_REPRODUCIBLE": 2,
    "MISSING_EVIDENCE": 3,
    "OUT_OF_SCOPE": 4,
    "CONTRADICTION": 5,
}

# Claim-Types, deren MISSING_EVIDENCE als validation_gap zählt.
VALIDATION_GAP_TYPES: frozenset[str] = frozenset({"command_succeeded", "validator_succeeded"})

# Schema-Dateinamen (relativ zu repo_root/schemas/).
_BUNDLE_SCHEMA_NAME = "experiment-run-bundle.v1.schema.json"
_AUDITOR_SCHEMA_NAME = "auditor-output.v1.schema.json"
_MEASUREMENT_SCHEMA_NAME = "measurement-run.v1.schema.json"
_EVIDENCE_PACK_SCHEMA_NAME = "run-evidence-pack.v1.schema.json"
_LEGACY_EVIDENCE_PACK_BASELINE = "run-bundle-evidence-pack-legacy.yml"
_CHANGED_FILES_CONTRACT_DATE = "2026-05-08"
_CHANGED_FILES_GUARD_EXPERIMENT = Path(
    "experiments/2026-05-01_agent-skill-minimal-layer-instrumentation"
)
_GRANDFATHERED_CHANGED_FILES_RUN = (
    _CHANGED_FILES_GUARD_EXPERIMENT / "artifacts" / "run-002-controlled-agent-skill-run"
)
# Historical exception for the canonical run-002 baseline: this run may keep
# reference_only comparability without changed_files_artifact and may also retain
# an existing non-null scope_drift_count claim without changed-files evidence.
# The exception is intentionally path-exact and must not generalize.

_MISSING = object()

# Modul-level Warnliste — wird zu Beginn jedes validate_repo()-Aufrufs zurückgesetzt.
# Allows tests to inspect warnings without modifying the return type of validate_repo().
last_warnings: list[str] = []

_DEFAULT_STRONG_EVIDENCE_STATUSES = frozenset(
    {"repo_local", "ci_artifact", "external_verified", "derived_from_auditor_output"}
)

try:
    import validate_claim_evidence as _claim_evidence  # type: ignore
except ImportError as _semantic_import_error:
    validate_claim_evidence_file = None  # type: ignore[assignment]
    STRONG_EVIDENCE_STATUSES = _DEFAULT_STRONG_EVIDENCE_STATUSES
    _SEMANTIC_IMPORT_ERROR = _semantic_import_error
else:
    validate_claim_evidence_file = getattr(_claim_evidence, "validate_file", None)
    strong_statuses = getattr(
        _claim_evidence,
        "STRONG_EVIDENCE_STATUSES",
        _DEFAULT_STRONG_EVIDENCE_STATUSES,
    )
    if isinstance(strong_statuses, (set, frozenset, list, tuple)):
        STRONG_EVIDENCE_STATUSES = frozenset(str(s) for s in strong_statuses)
    else:
        STRONG_EVIDENCE_STATUSES = _DEFAULT_STRONG_EVIDENCE_STATUSES
    _SEMANTIC_IMPORT_ERROR = None


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------

def _load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _build_validator(schema_path: Path) -> Draft202012Validator:
    schema = _load_json(schema_path)
    cls = validator_for(schema, default=Draft202012Validator)
    cls.check_schema(schema)
    return cls(schema, format_checker=cls.FORMAT_CHECKER)


def _read_evidence_run_artifacts(evidence_file: Path) -> list[tuple[int, str]]:
    """Liest event_type=run-Einträge aus evidence.jsonl.

    Gibt eine Liste von (lineno, artifact_ref) zurück. Defekte Zeilen
    werden hier nicht gemeldet — das ist Aufgabe von validate_schema.py.
    """
    out: list[tuple[int, str]] = []
    if not evidence_file.is_file():
        return out
    for lineno, line in enumerate(evidence_file.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(entry, dict):
            continue
        if entry.get("event_type") == "run":
            ref = entry.get("artifact_ref")
            if isinstance(ref, str):
                out.append((lineno, ref))
    return out


def _resolve_within_run_dir(run_dir: Path, ref: str) -> Path | None:
    """Resolved ref relativ zu run_dir; gibt None zurück, wenn das Ergebnis
    run_dir verlässt (Path-Escape-Schutz für Run-lokale Artefaktpfade)."""
    try:
        candidate = (run_dir / ref).resolve()
        candidate.relative_to(run_dir.resolve())
    except (ValueError, OSError):
        return None
    return candidate


def _resolve_within(base: Path, ref: str) -> Path | None:
    """Resolved ref relativ zu base; gibt None zurück, wenn das Ergebnis
    base verlässt (Path-Escape-Schutz)."""
    try:
        candidate = (base / ref).resolve()
        candidate.relative_to(base.resolve())
    except (ValueError, OSError):
        return None
    return candidate


def _is_absolute_path_str(ref: str) -> bool:
    return Path(ref).is_absolute() or (len(ref) >= 2 and ref[1] == ":")


def _resolve_changed_files_artifact_ref(
    *,
    exp_dir: Path,
    run_dir: Path,
    ref: str,
) -> Path | None:
    """Resolve changed_files_artifact in exactly two accepted forms.

    Accepted forms:
      - run-local: ``changed-files.txt`` or ``subdir/changed-files.txt``
      - experiment-relative contract style: ``artifacts/<run-id>/changed-files.txt``

    Both forms must still resolve into the current run_dir.
    """
    if ref.startswith("artifacts/"):
        candidate = _resolve_within(exp_dir, ref)
    else:
        candidate = _resolve_within_run_dir(run_dir, ref)

    if candidate is None:
        return None

    try:
        candidate.relative_to(run_dir.resolve())
    except (ValueError, OSError):
        return None
    return candidate


def _is_grandfathered_changed_files_run(rel_run: Path) -> bool:
    return rel_run == _GRANDFATHERED_CHANGED_FILES_RUN


def _load_comparability_run_artifact_ref(
    *,
    field_name: str,
    comparability: dict | None,
    exp_dir: Path,
    run_dir: Path,
    rel_run: Path,
    errors: list[str],
) -> tuple[bool, bool]:
    """Validates an optional run-local artifact ref field in a comparability dict.

    Generic helper for any ``comparability.yml`` field that points to a run-local
    artifact (e.g. ``review_evidence_artifact``).  Uses the same two-form resolution
    rules as ``changed_files_artifact``:

      - run-local:               ``review-events.yml`` or ``subdir/review-events.yml``
      - experiment-relative:     ``artifacts/<run-id>/review-events.yml``

    Both forms must still resolve into the current run_dir.

    Returns ``(artifact_valid, artifact_missing)``:
      ``(True, False)``  — field present, non-null, file exists and is run-local
      ``(False, True)``  — field absent or null (no error)
      ``(False, False)`` — field present but invalid (error already appended)
    """
    if comparability is None:
        return False, True

    raw_ref = comparability.get(field_name, _MISSING)
    if raw_ref is _MISSING or raw_ref is None:
        return False, True

    if not isinstance(raw_ref, str):
        errors.append(
            f"  ❌ {rel_run}/comparability.yml: {field_name} muss ein String oder null sein."
        )
        return False, False

    ref = raw_ref.strip()
    if not ref:
        errors.append(
            f"  ❌ {rel_run}/comparability.yml: {field_name} darf kein leerer String sein."
        )
        return False, False

    if _is_absolute_path_str(ref):
        errors.append(
            f"  ❌ {rel_run}/comparability.yml: {field_name} '{ref}' darf kein absoluter Pfad sein."
        )
        return False, False

    target = _resolve_changed_files_artifact_ref(exp_dir=exp_dir, run_dir=run_dir, ref=ref)
    if target is None:
        errors.append(
            f"  ❌ {rel_run}/comparability.yml: {field_name} '{ref}' muss "
            f"run-lokal oder experiment-relativ auf dieses Run-Verzeichnis zeigen."
        )
        return False, False

    if not target.is_file():
        errors.append(
            f"  ❌ {rel_run}/comparability.yml: {field_name} '{ref}' zeigt nicht auf eine existierende Datei."
        )
        return False, False

    return True, False


def _requires_changed_files_comparability(bundle: dict | None, rel_exp: Path) -> bool:
    if not isinstance(bundle, dict):
        return False

    run_block = bundle.get("run") or {}
    created_at = run_block.get("created_at")
    if isinstance(created_at, str) and created_at[:10] >= _CHANGED_FILES_CONTRACT_DATE:
        return True

    sequence = run_block.get("sequence")
    return rel_exp == _CHANGED_FILES_GUARD_EXPERIMENT and isinstance(sequence, int) and sequence >= 3


def _has_metric_missing_evidence_reason(measurement: dict, metric_name: str) -> bool:
    metrics = measurement.get("metrics") or {}
    metric = metrics.get(metric_name) or {}
    if isinstance(metric, dict):
        notes = metric.get("notes")
        if isinstance(notes, str) and notes.strip():
            return True

    missing_evidence = measurement.get("missing_evidence") or []
    if not isinstance(missing_evidence, list):
        return False

    for entry in missing_evidence:
        if not isinstance(entry, dict):
            continue
        if entry.get("item") != metric_name:
            continue
        for key in ("detail", "reason", "notes"):
            value = entry.get(key)
            if isinstance(value, str) and value.strip():
                return True
    return False


def _load_comparability_assessment(
    *,
    exp_dir: Path,
    run_dir: Path,
    rel_run: Path,
    errors: list[str],
) -> tuple[dict | None, bool, bool, bool]:
    comparability_yml = run_dir / "comparability.yml"
    if not comparability_yml.is_file():
        return None, False, False, True

    try:
        comparability = _load_yaml(comparability_yml)
    except Exception as e:
        errors.append(f"  ❌ {rel_run}/comparability.yml: YAML-Fehler — {e}")
        return None, True, False, False

    if not isinstance(comparability, dict):
        errors.append(
            f"  ❌ {rel_run}/comparability.yml: Datei muss ein YAML-Objekt sein."
        )
        return None, True, False, False

    raw_ref = comparability.get("changed_files_artifact", _MISSING)
    if raw_ref is _MISSING or raw_ref is None:
        return comparability, True, False, True

    if not isinstance(raw_ref, str):
        errors.append(
            f"  ❌ {rel_run}/comparability.yml: changed_files_artifact muss ein String oder null sein."
        )
        return comparability, True, False, False

    ref = raw_ref.strip()
    if not ref:
        errors.append(
            f"  ❌ {rel_run}/comparability.yml: changed_files_artifact darf kein leerer String sein."
        )
        return comparability, True, False, False

    if _is_absolute_path_str(ref):
        errors.append(
            f"  ❌ {rel_run}/comparability.yml: changed_files_artifact '{ref}' darf kein absoluter Pfad sein."
        )
        return comparability, True, False, False

    target = _resolve_changed_files_artifact_ref(exp_dir=exp_dir, run_dir=run_dir, ref=ref)
    if target is None:
        errors.append(
            f"  ❌ {rel_run}/comparability.yml: changed_files_artifact '{ref}' muss "
            f"run-lokal oder experiment-relativ auf dieses Run-Verzeichnis zeigen."
        )
        return comparability, True, False, False

    if not target.is_file():
        errors.append(
            f"  ❌ {rel_run}/comparability.yml: changed_files_artifact '{ref}' zeigt nicht auf eine existierende Datei."
        )
        return comparability, True, False, False

    return comparability, True, True, False


def _compute_max_severity(verdicts: Iterable[str]) -> str:
    """Gibt das Verdict mit der höchsten Severity aus verdicts zurück;
    bei leerer Liste 'PASS'."""
    best = "PASS"
    best_score = SEVERITY["PASS"]
    for v in verdicts:
        score = SEVERITY.get(v, -1)
        if score > best_score:
            best_score = score
            best = v
    return best


def _load_missing_evidence_pack_allowlist(repo_root: Path) -> tuple[set[str], list[str]]:
    """Lädt und validiert die Legacy-Allowlist für fehlende evidence_pack-Referenzen.

    Rückgabe:
      - erlaubte run.yml Pfade (repo-root-relativ)
      - Validierungsfehler der Allowlist (duplikate, stale, missing targets, ...)
    """
    path = repo_root / ".vibe" / _LEGACY_EVIDENCE_PACK_BASELINE
    if not path.is_file():
        return set(), []

    try:
        data = _load_yaml(path)
    except Exception as e:
        return set(), [f"  ❌ {path.relative_to(repo_root)}: YAML-Fehler — {e}"]

    errors: list[str] = []
    if not isinstance(data, dict):
        return set(), [
            f"  ❌ {path.relative_to(repo_root)}: Datei muss ein YAML-Objekt sein."
        ]

    top_level_keys = set(data.keys())
    allowed_top_level_keys = {"schema_version", "allowed_missing_evidence_pack"}
    unexpected_top_level = sorted(top_level_keys - allowed_top_level_keys)
    if unexpected_top_level:
        return set(), [
            f"  ❌ {path.relative_to(repo_root)}: Unbekannte Top-Level-Felder: {', '.join(unexpected_top_level)}."
        ]

    schema_version = data.get("schema_version")
    if schema_version != "1.0.0":
        return set(), [
            f"  ❌ {path.relative_to(repo_root)}: schema_version muss exakt '1.0.0' sein."
        ]

    entries = data.get("allowed_missing_evidence_pack", [])
    if not isinstance(entries, list):
        return set(), [
            f"  ❌ {path.relative_to(repo_root)}: allowed_missing_evidence_pack muss eine Liste sein."
        ]

    allowed: set[str] = set()
    for idx, entry in enumerate(entries, 1):
        if not isinstance(entry, dict):
            errors.append(
                f"  ❌ {path.relative_to(repo_root)}: Eintrag #{idx} muss ein Objekt sein."
            )
            continue

        entry_keys = set(entry.keys())
        allowed_entry_keys = {"path", "reason"}
        unexpected_entry = sorted(entry_keys - allowed_entry_keys)
        if unexpected_entry:
            errors.append(
                f"  ❌ {path.relative_to(repo_root)}: Eintrag #{idx} enthält unbekannte Felder: {', '.join(unexpected_entry)}."
            )
            continue

        raw_ref = entry.get("path")
        if not isinstance(raw_ref, str) or not raw_ref.strip():
            errors.append(
                f"  ❌ {path.relative_to(repo_root)}: Eintrag #{idx} hat ungültiges 'path'."
            )
            continue

        reason = entry.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            errors.append(
                f"  ❌ {path.relative_to(repo_root)}: Eintrag #{idx} hat ungültiges 'reason'."
            )
            continue

        target = _resolve_within(repo_root, raw_ref)
        if target is None:
            errors.append(
                f"  ❌ {path.relative_to(repo_root)}: Eintrag #{idx} path='{raw_ref}' verlässt das Repo."
            )
            continue
        if not target.is_file():
            errors.append(
                f"  ❌ {path.relative_to(repo_root)}: Eintrag #{idx} path='{raw_ref}' zeigt nicht auf eine existierende Datei."
            )
            continue
        if target.name != "run.yml":
            errors.append(
                f"  ❌ {path.relative_to(repo_root)}: Eintrag #{idx} path='{raw_ref}' muss auf run.yml zeigen."
            )
            continue

        rel_target = str(target.relative_to(repo_root))
        if rel_target in allowed:
            errors.append(
                f"  ❌ {path.relative_to(repo_root)}: Duplikat-Eintrag für '{rel_target}'."
            )
            continue

        # Ratchet: stale Allowlist-Einträge sind nicht erlaubt.
        try:
            run_data = _load_yaml(target)
        except Exception as e:
            errors.append(
                f"  ❌ {path.relative_to(repo_root)}: Eintrag '{rel_target}' ist nicht lesbar — {e}."
            )
            continue
        artifacts = run_data.get("artifacts", {}) if isinstance(run_data, dict) else {}
        if isinstance(artifacts, dict) and "evidence_pack" in artifacts:
            errors.append(
                f"  ❌ {path.relative_to(repo_root)}: Stale Allowlist-Eintrag '{rel_target}' — run.yml enthält bereits artifacts.evidence_pack."
            )
            continue

        allowed.add(rel_target)

    return allowed, errors


# ---------------------------------------------------------------------------
# Kern-Validierung als pure Funktion (für Tests einfach aufrufbar)
# ---------------------------------------------------------------------------

def validate_repo(repo_root: Path) -> list[str]:
    """Validiert alle Experiment-Run-Bundles unter repo_root/experiments.

    Schemas werden aus repo_root/schemas/ geladen — nie aus dem globalen
    REPO_ROOT-Constant. Das erlaubt Tests mit Tempdir-Fixtures ohne
    Abhängigkeit auf das echte Repo.

    Gibt eine Liste menschlich lesbarer Fehlermeldungen zurück. Eine leere
    Liste bedeutet: alle Cross-File-Regeln passen.

    Warnungen (kein Fehler) werden zusätzlich in das Modul-Attribut
    last_warnings geschrieben. Dieses wird zu Beginn jedes Aufrufs
    zurückgesetzt — auch beim Early Return.
    """
    global last_warnings
    last_warnings = []

    errors: list[str] = []
    experiments_dir = repo_root / "experiments"
    if not experiments_dir.is_dir():
        return errors

    # Schemas immer aus dem übergebenen repo_root laden.
    schemas_dir = repo_root / "schemas"
    bundle_validator = _build_validator(schemas_dir / _BUNDLE_SCHEMA_NAME)
    auditor_validator = _build_validator(schemas_dir / _AUDITOR_SCHEMA_NAME)
    measurement_validator = _build_validator(schemas_dir / _MEASUREMENT_SCHEMA_NAME)
    evidence_pack_validator = _build_validator(schemas_dir / _EVIDENCE_PACK_SCHEMA_NAME)
    missing_ep_allowlist, allowlist_errors = _load_missing_evidence_pack_allowlist(repo_root)
    errors.extend(allowlist_errors)

    for manifest_path in sorted(experiments_dir.glob("*/manifest.yml")):
        exp_dir = manifest_path.parent
        if exp_dir.name.startswith("_"):
            continue  # _archive, _template

        rel_exp = exp_dir.relative_to(repo_root)
        try:
            manifest = _load_yaml(manifest_path)
        except Exception as e:
            errors.append(f"  ❌ {rel_exp}/manifest.yml: YAML-Fehler — {e}")
            continue

        experiment = manifest.get("experiment", {}) or {}
        execution_status = experiment.get("execution_status")
        execution_refs = experiment.get("execution_refs") or []

        evidence_file = exp_dir / "results" / "evidence.jsonl"
        run_events = _read_evidence_run_artifacts(evidence_file)

        # R1: Run-Event vs. prepared
        if run_events and execution_status == "prepared":
            errors.append(
                f"  ❌ {rel_exp}: results/evidence.jsonl enthält event_type=run "
                f"(Zeile {run_events[0][0]}), aber manifest.execution_status=prepared. "
                f"Setze execution_status auf executed/replicated oder entferne den Run-Event."
            )

        # R2 + R3: execution_refs bei executed/replicated
        if execution_status in {"executed", "replicated"}:
            if not execution_refs:
                errors.append(
                    f"  ❌ {rel_exp}: execution_status={execution_status}, "
                    f"aber execution_refs ist leer."
                )
            else:
                evidence_ref_present = False
                for ref in execution_refs:
                    if not isinstance(ref, str):
                        errors.append(
                            f"  ❌ {rel_exp}: execution_refs enthält Nicht-String-Eintrag {ref!r}."
                        )
                        continue
                    target = _resolve_within(exp_dir, ref)
                    if target is None:
                        errors.append(
                            f"  ❌ {rel_exp}: execution_ref '{ref}' verlässt das Experiment-Root."
                        )
                        continue
                    if not target.is_file():
                        errors.append(
                            f"  ❌ {rel_exp}: execution_ref '{ref}' ist keine existierende Datei."
                        )
                        continue
                    normalized_ref = ref[2:] if ref.startswith("./") else ref
                    if normalized_ref == "results/evidence.jsonl":
                        evidence_ref_present = True
                if not evidence_ref_present and evidence_file.is_file():
                    errors.append(
                        f"  ❌ {rel_exp}: execution_refs verweist nicht auf "
                        f"results/evidence.jsonl, obwohl die Datei existiert."
                    )

        # R4: artifact_refs aus evidence.jsonl.
        # Die strikte .md-Sperre gilt nur für Experimente, die ins Run-Bundle-
        # Contract opted haben (d. h. mindestens ein direktes artifacts/<run-id>/run.yml existiert).
        # Legacy-Experimente ohne run.yml bleiben unberührt.
        artifacts_dir_for_r4 = exp_dir / "artifacts"
        experiment_has_run_yml = (
            artifacts_dir_for_r4.is_dir()
            and any(artifacts_dir_for_r4.glob("*/run.yml"))
        )
        for lineno, ref in run_events:
            if experiment_has_run_yml and Path(ref).suffix.lower() == ".md":
                errors.append(
                    f"  ❌ {rel_exp}/results/evidence.jsonl:{lineno}: "
                    f"artifact_ref '{ref}' zeigt auf Markdown-Projektion. "
                    f"Verwende einen kanonischen YAML/JSON/JSONL-Artefakt."
                )
                continue
            target = _resolve_within(exp_dir, ref)
            if target is None:
                errors.append(
                    f"  ❌ {rel_exp}/results/evidence.jsonl:{lineno}: "
                    f"artifact_ref '{ref}' verlässt das Experiment-Root."
                )
                continue
            if not target.is_file():
                errors.append(
                    f"  ❌ {rel_exp}/results/evidence.jsonl:{lineno}: "
                    f"artifact_ref '{ref}' existiert nicht."
                )

        # R5–R8: Run-Bundles unter artifacts/run-*/
        artifacts_dir = exp_dir / "artifacts"
        if artifacts_dir.is_dir():
            for run_dir in sorted(p for p in artifacts_dir.iterdir() if p.is_dir()):
                _validate_run_dir(
                    repo_root=repo_root,
                    exp_dir=exp_dir,
                    run_dir=run_dir,
                    execution_status=execution_status,
                    execution_refs=execution_refs,
                    bundle_validator=bundle_validator,
                    auditor_validator=auditor_validator,
                    measurement_validator=measurement_validator,
                    evidence_pack_validator=evidence_pack_validator,
                    missing_ep_allowlist=missing_ep_allowlist,
                    errors=errors,
                )

    return errors


def _validate_evidence_pack(
    *,
    repo_root: Path,
    run_dir: Path,
    run_id: str | None,
    ep_artifact: dict | None,
    evidence_pack_validator: Draft202012Validator,
    missing_ep_allowlist: set[str],
    errors: list[str],
    rel_run: Path,
) -> None:
    """Evidence-Pack-Kopplung: PR-6-Regel.

        Wenn artifacts.evidence_pack fehlt:
            - warnen, falls run.yml in der Legacy-Allowlist steht
            - Fehler, falls run.yml nicht allowlisted ist
    Wenn vorhanden → vollständige Validierung:
    - Pflichtfelder (contract, canonical) strukturell
    - path-Escape-Schutz
    - Datei-Existenz
    - Schema-Validierung gegen run-evidence-pack.v1.schema.json
    - run_id-Übereinstimmung
    - repo_local Evidence-Pfade existieren und verlassen nicht das Repo
    - PASS nicht mit missing_evidence/external_unverified/self_reported
    - Kein Self-Observation-PASS (EP beweist nur sich selbst)
    """
    global last_warnings

    if ep_artifact is None:
        run_yml_rel = str((run_dir / "run.yml").relative_to(repo_root))
        if run_yml_rel in missing_ep_allowlist:
            last_warnings.append(
                f"  ⚠️  {rel_run}/run.yml: artifacts.evidence_pack fehlt "
                f"(run_bundle_without_evidence_pack). Legacy-Allowlist greift."
            )
        else:
            errors.append(
                f"  ❌ {rel_run}/run.yml: artifacts.evidence_pack fehlt "
                f"(run_bundle_missing_evidence_pack_not_allowlisted)."
            )
        return

    if not isinstance(ep_artifact, dict):
        errors.append(
            f"  ❌ {rel_run}/run.yml: artifacts.evidence_pack muss ein Objekt sein."
        )
        return

    # Pflichtfelder prüfen (strukturell, vor Datei-Zugriff)
    contract = ep_artifact.get("contract")
    canonical = ep_artifact.get("canonical")
    path_str = ep_artifact.get("path")

    if contract != "run-evidence-pack.v1":
        errors.append(
            f"  ❌ {rel_run}/run.yml: artifacts.evidence_pack.contract='{contract}' "
            f"muss exakt 'run-evidence-pack.v1' sein."
        )
        return

    if canonical is not True:
        errors.append(
            f"  ❌ {rel_run}/run.yml: artifacts.evidence_pack.canonical={canonical!r} "
            f"muss exakt true sein."
        )
        return

    if not isinstance(path_str, str) or not path_str:
        errors.append(
            f"  ❌ {rel_run}/run.yml: artifacts.evidence_pack.path fehlt."
        )
        return

    # Pfad-Escape-Schutz: kein absoluter Pfad, kein .., kein Backslash
    import re as _re
    _BAD_PATH_PATTERN = _re.compile(
        r"^(?:/|[A-Za-z]:)|(?:(?:^|/)\.\.(?:/|$))|\\",
        _re.MULTILINE,
    )
    if _BAD_PATH_PATTERN.search(path_str):
        errors.append(
            f"  ❌ {rel_run}/run.yml: artifacts.evidence_pack.path '{path_str}' "
            f"ist unzulässig (absoluter Pfad, ..-Escape oder Backslash)."
        )
        return

    ep_path = _resolve_within_run_dir(run_dir, path_str)
    if ep_path is None:
        errors.append(
            f"  ❌ {rel_run}/run.yml: artifacts.evidence_pack.path '{path_str}' "
            f"verlässt das Run-Verzeichnis."
        )
        return

    if not ep_path.is_file():
        errors.append(
            f"  ❌ {rel_run}/run.yml: artifacts.evidence_pack.path '{path_str}' "
            f"existiert nicht (erwartet unter {ep_path.relative_to(repo_root)})."
        )
        return

    # Evidence-Pack laden und gegen Schema validieren.
    try:
        ep_data = _load_yaml(ep_path)
    except Exception as e:
        errors.append(f"  ❌ {ep_path.relative_to(repo_root)}: YAML-Fehler — {e}")
        return

    try:
        evidence_pack_validator.validate(ep_data)
    except ValidationError as e:
        errors.append(
            f"  ❌ {ep_path.relative_to(repo_root)}: schema-invalid — {e.message} "
            f"(at {'/'.join(str(p) for p in e.absolute_path) or '<root>'})"
        )
        return

    # run_id-Übereinstimmung
    ep_run_id = ep_data.get("run_id")
    if run_id and ep_run_id and ep_run_id != run_id:
        errors.append(
            f"  ❌ {ep_path.relative_to(repo_root)}: run_id='{ep_run_id}' "
            f"stimmt nicht mit run.yml run.id='{run_id}' überein."
        )
        return

    # repo_local Evidence-Pfade: müssen unter repo_root existieren und dort bleiben.
    for claim in ep_data.get("claims", []):
        claim_id = claim.get("claim_id", "<missing>")
        for ev_entry in claim.get("evidence", []):
            if not isinstance(ev_entry, dict):
                continue
            if ev_entry.get("status") != "repo_local":
                continue
            ev_path_str = ev_entry.get("path", "")
            if not ev_path_str:
                continue
            # Escape-Check (repo_local Pfade sind repo-root-relativ)
            ev_target = _resolve_within(repo_root, ev_path_str)
            if ev_target is None:
                errors.append(
                    f"  ❌ {ep_path.relative_to(repo_root)}: claim '{claim_id}' "
                    f"repo_local Evidence-Pfad '{ev_path_str}' verlässt das Repo."
                )
                continue
            if not ev_target.is_file():
                errors.append(
                    f"  ❌ {ep_path.relative_to(repo_root)}: claim '{claim_id}' "
                    f"repo_local Evidence-Pfad '{ev_path_str}' existiert nicht."
                )

    # Self-Observation-Check: PASS-Claim darf nicht ausschließlich auf das
    # Evidence-Pack selbst verweisen. Auch run_bundle_evidence_pack_reference
    # benötigt mindestens ein weiteres, von ep_path verschiedenes Artefakt.
    ep_resolved = ep_path.resolve()
    for claim in ep_data.get("claims", []):
        if str(claim.get("verdict", "")) != "PASS":
            continue
        claim_type = str(claim.get("type", ""))
        ev_entries = [ev for ev in claim.get("evidence", []) if isinstance(ev, dict)]
        ev_paths_in_claim = [str(ev.get("path", "")) for ev in ev_entries]
        if not ev_paths_in_claim:
            continue

        has_strong_non_self_reference = False
        for ev in ev_entries:
            status = str(ev.get("status", ""))
            if status not in STRONG_EVIDENCE_STATUSES:
                continue
            p = str(ev.get("path", ""))
            if not p:
                continue
            try:
                resolved_ev = (repo_root / p).resolve()
            except (ValueError, OSError):
                continue
            if resolved_ev != ep_resolved:
                has_strong_non_self_reference = True
                break

        if not has_strong_non_self_reference:
            errors.append(
                f"  ❌ {ep_path.relative_to(repo_root)}: claim '{claim.get('claim_id')}' "
                f"PASS-Claim vom Typ '{claim_type}' basiert ausschließlich auf dem "
                f"Evidence-Pack selbst oder auf schwacher non-self Evidence (Self-Observation)."
            )

    # Semantische Claim-Evidence-Prüfung via vollständiger Validator-Delegation.
    # Dadurch folgen file-level und claim-level Regeln konsistent validate_claim_evidence.py.
    if validate_claim_evidence_file is None:
        errors.append(
            f"  ❌ {ep_path.relative_to(repo_root)}: Semantische Claim-Evidence-Prüfung "
            f"nicht verfügbar (ImportError: {_SEMANTIC_IMPORT_ERROR})."
        )
        return
    sem_exit_code, sem_errors = validate_claim_evidence_file(ep_path, evidence_pack_validator)
    if sem_exit_code != 0:
        for sem_err in sem_errors:
            errors.append(f"  ❌ {ep_path.relative_to(repo_root)}: {sem_err}")
        return


def _validate_run_dir(
    *,
    repo_root: Path,
    exp_dir: Path,
    run_dir: Path,
    execution_status: str | None,
    execution_refs: list,
    bundle_validator: Draft202012Validator,
    auditor_validator: Draft202012Validator,
    measurement_validator: Draft202012Validator,
    evidence_pack_validator: Draft202012Validator,
    missing_ep_allowlist: set[str],
    errors: list[str],
) -> None:
    """Validiert ein einzelnes artifacts/<run-id>/-Verzeichnis."""
    rel_exp = exp_dir.relative_to(repo_root)
    rel_run = run_dir.relative_to(repo_root)
    run_yml = run_dir / "run.yml"
    auditor_yml = run_dir / "auditor-output.yml"
    measurement_yml = run_dir / "measurement.yml"

    # Legacy-Politik: kein run.yml → kein Bundle-Contract → nichts prüfen.
    if not run_yml.is_file():
        return

    bundle: dict | None = None

    # R5: run.yml
    if run_yml.is_file():
        # R8: run.yml muss in execution_refs stehen (bei executed/replicated)
        if execution_status in {"executed", "replicated"}:
            run_yml_ref = str(run_yml.relative_to(exp_dir))
            normalized_execution_refs = {
                ref[2:] if ref.startswith("./") else ref
                for ref in execution_refs
                if isinstance(ref, str)
            }
            if run_yml_ref not in normalized_execution_refs:
                errors.append(
                    f"  ❌ {rel_run}/run.yml: execution_status={execution_status}, "
                    f"aber '{run_yml_ref}' fehlt in manifest.execution_refs. "
                    f"Jedes run.yml muss in execution_refs aufgeführt sein."
                )

        try:
            bundle = _load_yaml(run_yml)
        except Exception as e:
            errors.append(f"  ❌ {rel_run}/run.yml: YAML-Fehler — {e}")
            bundle = None
        if bundle is not None:
            try:
                bundle_validator.validate(bundle)
            except ValidationError as e:
                errors.append(
                    f"  ❌ {rel_run}/run.yml: schema-invalid — {e.message} "
                    f"(at {'/'.join(str(p) for p in e.absolute_path) or '<root>'})"
                )
                bundle = None
        if bundle is not None:
            run_block = bundle.get("run", {}) or {}
            if run_block.get("id") != run_dir.name:
                errors.append(
                    f"  ❌ {rel_run}/run.yml: run.id='{run_block.get('id')}' "
                    f"stimmt nicht mit Verzeichnisnamen '{run_dir.name}' überein."
                )
            exp_path = run_block.get("experiment_path")
            if exp_path and (repo_root / exp_path).resolve() != exp_dir.resolve():
                errors.append(
                    f"  ❌ {rel_run}/run.yml: run.experiment_path='{exp_path}' "
                    f"zeigt nicht auf {exp_dir.relative_to(repo_root)}."
                )
            artifacts = bundle.get("artifacts", {}) or {}
            for key, artifact in artifacts.items():
                # evidence_pack wird separat nach diesem Loop behandelt — kein Doppelfehler.
                if key == "evidence_pack":
                    continue
                if not isinstance(artifact, dict):
                    continue
                path_str = artifact.get("path")
                if not isinstance(path_str, str) or not path_str:
                    errors.append(
                        f"  ❌ {rel_run}/run.yml: artifacts.{key}.path fehlt."
                    )
                    continue
                target = _resolve_within_run_dir(run_dir, path_str)
                if target is None:
                    errors.append(
                        f"  ❌ {rel_run}/run.yml: artifacts.{key}.path '{path_str}' "
                        f"verlässt das Run-Verzeichnis."
                    )
                    continue
                if not target.is_file():
                    errors.append(
                        f"  ❌ {rel_run}/run.yml: artifacts.{key}.path '{path_str}' "
                        f"existiert nicht (erwartet unter {target.relative_to(repo_root)})."
                    )
                    continue
                # canonical:true auf Markdown-Projektion ist verboten.
                canonical = artifact.get("canonical")
                if canonical is True and target.suffix.lower() == ".md":
                    errors.append(
                        f"  ❌ {rel_run}/run.yml: artifacts.{key} markiert eine Markdown-"
                        f"Projektion ('{path_str}') als canonical=true. Markdown ist "
                        f"Projektion, nicht maschinelle Wahrheit."
                    )

            # Evidence-Pack-Kopplung (PR 6)
            ep_artifact = artifacts.get("evidence_pack")
            run_id_for_ep = (bundle.get("run", {}) or {}).get("id")
            _validate_evidence_pack(
                repo_root=repo_root,
                run_dir=run_dir,
                run_id=run_id_for_ep,
                ep_artifact=ep_artifact,
                evidence_pack_validator=evidence_pack_validator,
                missing_ep_allowlist=missing_ep_allowlist,
                errors=errors,
                rel_run=rel_run,
            )

    # R6: auditor-output.yml
    auditor_data: dict | None = None
    if auditor_yml.is_file():
        try:
            auditor_data = _load_yaml(auditor_yml)
        except Exception as e:
            errors.append(f"  ❌ {rel_run}/auditor-output.yml: YAML-Fehler — {e}")
            auditor_data = None
        if auditor_data is not None:
            try:
                auditor_validator.validate(auditor_data)
            except ValidationError as e:
                errors.append(
                    f"  ❌ {rel_run}/auditor-output.yml: schema-invalid — {e.message} "
                    f"(at {'/'.join(str(p) for p in e.absolute_path) or '<root>'})"
                )
                auditor_data = None
        if auditor_data is not None:
            for sem_err in _check_auditor_semantics(auditor_data):
                errors.append(f"  ❌ {rel_run}/auditor-output.yml: {sem_err}")

    # Cross-checks zwischen run.yml und auditor-output.yml
    if bundle is not None and auditor_data is not None:
        run_id_expected = (bundle.get("run") or {}).get("id")
        auditor_run_id = auditor_data.get("run_id")
        if run_id_expected and auditor_run_id and auditor_run_id != run_id_expected:
            errors.append(
                f"  ❌ {rel_run}/auditor-output.yml: run_id='{auditor_run_id}' "
                f"stimmt nicht mit run.yml run.id='{run_id_expected}' überein."
            )
        bundle_outcome = (bundle.get("verdict") or {}).get("outcome")
        auditor_overall = auditor_data.get("overall_verdict")
        if bundle_outcome and auditor_overall and bundle_outcome != auditor_overall:
            errors.append(
                f"  ❌ {rel_run}/run.yml: verdict.outcome='{bundle_outcome}' "
                f"stimmt nicht mit auditor-output.yml overall_verdict='{auditor_overall}' überein."
            )

    # run_meta.json run_id cross-check (unabhängig von measurement.yml)
    run_meta_json = run_dir / "run_meta.json"
    if run_meta_json.is_file() and bundle is not None:
        try:
            run_meta = _load_json(run_meta_json)
        except Exception as e:
            errors.append(f"  ❌ {rel_run}/run_meta.json: JSON-Fehler — {e}")
        else:
            run_id_expected = (bundle.get("run") or {}).get("id")
            meta_run_id = run_meta.get("run_id")
            if run_id_expected and meta_run_id and meta_run_id != run_id_expected:
                errors.append(
                    f"  ❌ {rel_run}/run_meta.json: run_id='{meta_run_id}' "
                    f"stimmt nicht mit run.yml run.id='{run_id_expected}' überein."
                )

    grandfathered_changed_files_run = _is_grandfathered_changed_files_run(rel_run)
    requires_comparability = _requires_changed_files_comparability(bundle, rel_exp)
    comparability, comparability_present, changed_files_artifact_valid, changed_files_artifact_missing = (
        _load_comparability_assessment(
            exp_dir=exp_dir,
            run_dir=run_dir,
            rel_run=rel_run,
            errors=errors,
        )
    )

    if not comparability_present:
        if requires_comparability:
            errors.append(
                f"  ❌ {rel_run}/comparability.yml: fehlt, obwohl dieser Run nach dem "
                f"Changed-Files-Contract eine Comparability-Bewertung benötigt."
            )
    elif comparability is not None:
        verdict = comparability.get("verdict")
        grandfathered_reference_only_without_changed_files = (
            grandfathered_changed_files_run
            and verdict == "reference_only"
            and changed_files_artifact_missing
        )
        if verdict == "not_comparable":
            if changed_files_artifact_missing:
                missing_reason = comparability.get("missing_changed_files_reason")
                if not isinstance(missing_reason, str) or not missing_reason.strip():
                    errors.append(
                        f"  ❌ {rel_run}/comparability.yml: verdict=not_comparable mit "
                        f"changed_files_artifact=null oder fehlend erfordert missing_changed_files_reason."
                    )
        elif changed_files_artifact_missing and not grandfathered_reference_only_without_changed_files:
            errors.append(
                f"  ❌ {rel_run}/comparability.yml: verdict='{verdict}' erfordert ein "
                f"gültiges changed_files_artifact."
            )

    # Load review_evidence_artifact from comparability (review-rework-artifact.contract.md v0.1).
    # The field is optional; when present it enables repo_local evidence_status for
    # review_friction_count and rework_count in measurement.yml.
    review_evidence_artifact_valid, _review_ev_missing = _load_comparability_run_artifact_ref(
        field_name="review_evidence_artifact",
        comparability=comparability if comparability_present else None,
        exp_dir=exp_dir,
        run_dir=run_dir,
        rel_run=rel_run,
        errors=errors,
    )

    # R7: measurement.yml
    measurement: dict | None = None
    if measurement_yml.is_file():
        try:
            measurement = _load_yaml(measurement_yml)
        except Exception as e:
            errors.append(f"  ❌ {rel_run}/measurement.yml: YAML-Fehler — {e}")
            return
        try:
            measurement_validator.validate(measurement)
        except ValidationError as e:
            errors.append(
                f"  ❌ {rel_run}/measurement.yml: schema-invalid — {e.message} "
                f"(at {'/'.join(str(p) for p in e.absolute_path) or '<root>'})"
            )
            return

        # run_id cross-check
        if bundle is not None:
            run_id_expected = (bundle.get("run") or {}).get("id")
            meas_run_id = measurement.get("run_id")
            if run_id_expected and meas_run_id and meas_run_id != run_id_expected:
                errors.append(
                    f"  ❌ {rel_run}/measurement.yml: run_id='{meas_run_id}' "
                    f"stimmt nicht mit run.yml run.id='{run_id_expected}' überein."
                )

        # auditor_ref auflösen (const "auditor-output.yml" ist schema-erzwungen)
        ref = measurement.get("auditor_ref")
        if not ref:
            errors.append(
                f"  ❌ {rel_run}/measurement.yml: auditor_ref ist nicht gesetzt."
            )
            return

        ref_target = _resolve_within_run_dir(run_dir, ref)
        if ref_target is None:
            errors.append(
                f"  ❌ {rel_run}/measurement.yml: auditor-Referenz '{ref}' "
                f"verlässt das Run-Verzeichnis."
            )
            return
        if not ref_target.is_file():
            errors.append(
                f"  ❌ {rel_run}/measurement.yml: auditor-Referenz '{ref}' "
                f"zeigt auf nicht existierende Datei."
            )
            return

        # Bypass-Schutz: auditor_ref muss auf run_dir/auditor-output.yml zeigen.
        if ref_target.resolve() != auditor_yml.resolve():
            errors.append(
                f"  ❌ {rel_run}/measurement.yml: auditor_ref '{ref}' zeigt nicht auf "
                f"auditor-output.yml in diesem Run-Verzeichnis."
            )
            return

        # Semantik-Konsistenz mit dem Auditor
        if auditor_data is not None:
            for sem_err in _check_measurement_semantics(measurement, auditor_data):
                errors.append(f"  ❌ {rel_run}/measurement.yml: {sem_err}")

        scope_drift = (measurement.get("metrics") or {}).get("scope_drift_count") or {}
        if isinstance(scope_drift, dict):
            scope_value = scope_drift.get("value")
            scope_evidence_status = scope_drift.get("evidence_status")

            if scope_value is None:
                if scope_evidence_status != "missing_evidence":
                    errors.append(
                        f"  ❌ {rel_run}/measurement.yml: scope_drift_count.value=null "
                        f"erfordert evidence_status=missing_evidence."
                    )
                elif not _has_metric_missing_evidence_reason(measurement, "scope_drift_count"):
                    errors.append(
                        f"  ❌ {rel_run}/measurement.yml: scope_drift_count.value=null "
                        f"erfordert eine Begründung in notes oder missing_evidence."
                    )
            elif not grandfathered_changed_files_run:
                # Historical bundles before the changed-files contract may lack
                # comparability.yml. New bundles are guarded via
                # _requires_changed_files_comparability().
                if scope_evidence_status == "repo_local":
                    if not comparability_present:
                        errors.append(
                            f"  ❌ {rel_run}/measurement.yml: scope_drift_count.evidence_status=repo_local "
                            f"erfordert comparability.yml mit gültigem changed_files_artifact."
                        )
                    elif comparability is None:
                        pass
                    elif not changed_files_artifact_valid:
                        errors.append(
                            f"  ❌ {rel_run}/measurement.yml: scope_drift_count.evidence_status=repo_local "
                            f"erfordert ein gültiges changed_files_artifact."
                        )
                elif comparability is not None and not changed_files_artifact_valid:
                    errors.append(
                        f"  ❌ {rel_run}/measurement.yml: scope_drift_count.value={scope_value!r} "
                        f"erfordert ein gültiges changed_files_artifact."
                    )

        # Review/rework metrics: null-discipline and optional review_evidence_artifact coupling.
        # See .vibe/review-rework-artifact.contract.md for the full contract.
        for metric_name in ("review_friction_count", "rework_count"):
            metric = (measurement.get("metrics") or {}).get(metric_name) or {}
            if not isinstance(metric, dict):
                continue
            metric_value = metric.get("value")
            metric_status = metric.get("evidence_status")
            if metric_value is None:
                if metric_status != "missing_evidence":
                    errors.append(
                        f"  ❌ {rel_run}/measurement.yml: {metric_name}.value=null "
                        f"erfordert evidence_status=missing_evidence."
                    )
                elif not _has_metric_missing_evidence_reason(measurement, metric_name):
                    errors.append(
                        f"  ❌ {rel_run}/measurement.yml: {metric_name}.value=null "
                        f"erfordert eine Begründung in notes oder missing_evidence."
                    )
            elif metric_status == "repo_local":
                if not review_evidence_artifact_valid:
                    errors.append(
                        f"  ❌ {rel_run}/measurement.yml: {metric_name}.evidence_status=repo_local "
                        f"erfordert ein gültiges review_evidence_artifact in comparability.yml."
                    )

def _check_auditor_semantics(auditor: dict) -> list[str]:
    """Severity-Precedence + PASS-Konsistenz."""
    out: list[str] = []
    overall = auditor.get("overall_verdict")
    claims = auditor.get("claims") or []
    if not isinstance(claims, list):
        return out  # Schema-Fehler — bereits gemeldet.

    claim_verdicts = [c.get("verdict") for c in claims if isinstance(c, dict)]
    non_pass = [v for v in claim_verdicts if v != PASS]

    if overall == PASS and non_pass:
        out.append(
            f"overall_verdict=PASS, aber {len(non_pass)} Claim(s) sind non-PASS "
            f"(verdicts: {sorted(set(non_pass))}). PASS verlangt, dass jeder Claim PASS ist."
        )
        return out

    if not non_pass and overall != PASS:
        out.append(
            f"overall_verdict='{overall}', aber alle Auditor-Claims sind PASS. "
            f"overall_verdict muss PASS sein, wenn alle Claims PASS sind."
        )
        return out

    if non_pass:
        expected = _compute_max_severity(non_pass)
        if overall != expected:
            out.append(
                f"overall_verdict='{overall}' verletzt Severity-Precedence: "
                f"höchste Claim-Severity ist '{expected}' (aus {sorted(set(non_pass))}). "
                f"Severity-Reihenfolge: CONTRADICTION > OUT_OF_SCOPE > MISSING_EVIDENCE > "
                f"NOT_REPRODUCIBLE > CLAIM_NOT_PROVEN."
            )

    return out


def _check_measurement_semantics(measurement: dict, auditor: dict) -> list[str]:
    """auditor_verdict-Konsistenz + abgeleitete Zähler."""
    out: list[str] = []

    aud_overall = auditor.get("overall_verdict")
    meas_verdict = measurement.get("auditor_verdict")
    if aud_overall and meas_verdict and aud_overall != meas_verdict:
        out.append(
            f"auditor_verdict='{meas_verdict}' weicht von auditor.overall_verdict="
            f"'{aud_overall}' ab."
        )

    claims = auditor.get("claims") or []
    if not isinstance(claims, list):
        return out

    non_pass_count = sum(
        1 for c in claims if isinstance(c, dict) and c.get("verdict") != PASS
    )
    validation_gap_count = sum(
        1
        for c in claims
        if isinstance(c, dict)
        and c.get("verdict") == "MISSING_EVIDENCE"
        and c.get("type") in VALIDATION_GAP_TYPES
    )

    metrics = measurement.get("metrics") or {}
    unsupported = (metrics.get("unsupported_claim_count") or {}).get("value")
    val_gap = (metrics.get("validation_gap_count") or {}).get("value")

    if unsupported is not None and unsupported != non_pass_count:
        out.append(
            f"unsupported_claim_count.value={unsupported} ≠ Anzahl non-PASS-Claims "
            f"im Auditor ({non_pass_count}). Diese Metrik wird aus dem Auditor-Output "
            f"abgeleitet."
        )
    if val_gap is not None and val_gap != validation_gap_count:
        out.append(
            f"validation_gap_count.value={val_gap} ≠ Anzahl MISSING_EVIDENCE-Claims "
            f"mit type ∈ {{command_succeeded, validator_succeeded}} im Auditor "
            f"({validation_gap_count})."
        )

    return out


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    print("🧷 Validating experiment run bundles...")
    errors = validate_repo(REPO_ROOT)
    if last_warnings:
        for warning in last_warnings:
            print(warning)
    if errors:
        print("❌ Run-Bundle validation FAILED:")
        for err in errors:
            print(err)
        return 1
    print("✅ All run bundles consistent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
