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

# Modul-level Warnliste — wird zu Beginn jedes validate_repo()-Aufrufs zurückgesetzt.
# Allows tests to inspect warnings without modifying the return type of validate_repo().
last_warnings: list[str] = []

try:
    from validate_claim_evidence import semantic_errors_for_claim  # type: ignore
except ImportError as _semantic_import_error:
    semantic_errors_for_claim = None  # type: ignore[assignment]
    _SEMANTIC_IMPORT_ERROR = _semantic_import_error
else:
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
    errors: list[str],
    rel_run: Path,
) -> None:
    """Evidence-Pack-Kopplung: PR-6-Regel.

    Wenn artifacts.evidence_pack fehlt → Warnung, kein Fehler (Legacy-Kompatibilität).
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
        # Kein evidence_pack → Warnung, aber kein Fehler.
        last_warnings.append(
            f"  ⚠️  {rel_run}/run.yml: artifacts.evidence_pack fehlt "
            f"(run_bundle_without_evidence_pack). Legacy-Bundle — kein Fehler."
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

    # Semantische Claim-Evidence-Prüfung (wiederverwendet validate_claim_evidence Logik)
    if semantic_errors_for_claim is None:
        errors.append(
            f"  ❌ {ep_path.relative_to(repo_root)}: Semantische Claim-Evidence-Prüfung "
            f"nicht verfügbar (ImportError: {_SEMANTIC_IMPORT_ERROR})."
        )
        return
    for claim in ep_data.get("claims", []):
        for sem_err in semantic_errors_for_claim(claim, ep_path):
            errors.append(f"  ❌ {ep_path.relative_to(repo_root)}: {sem_err}")

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

        has_non_self_reference = False
        for ev in ev_entries:
            p = str(ev.get("path", ""))
            if not p:
                continue
            try:
                resolved_ev = (repo_root / p).resolve()
            except (ValueError, OSError):
                has_non_self_reference = True
                break
            if resolved_ev != ep_resolved:
                has_non_self_reference = True
                break

        if not has_non_self_reference:
            errors.append(
                f"  ❌ {ep_path.relative_to(repo_root)}: claim '{claim.get('claim_id')}' "
                f"PASS-Claim vom Typ '{claim_type}' basiert ausschließlich auf dem "
                f"Evidence-Pack selbst (Self-Observation)."
            )


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
    errors: list[str],
) -> None:
    """Validiert ein einzelnes artifacts/<run-id>/-Verzeichnis."""
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

    # R7: measurement.yml
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
    if errors:
        print("❌ Run-Bundle validation FAILED:")
        for err in errors:
            print(err)
        return 1
    # Output any warnings that were collected during validation
    if last_warnings:
        for warning in last_warnings:
            print(warning)
    print("✅ All run bundles consistent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
