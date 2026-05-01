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
    from jsonschema import Draft202012Validator, ValidationError, SchemaError
    from jsonschema.validators import validator_for
except ImportError:
    print(
        "ERROR: Missing dependencies. Run: "
        "python3 -m pip install pyyaml jsonschema rfc3339-validator"
    )
    sys.exit(1)


REPO_ROOT = Path(__file__).resolve().parent.parent.parent

SCHEMAS_DIR = REPO_ROOT / "schemas"
RUN_BUNDLE_SCHEMA = SCHEMAS_DIR / "experiment-run-bundle.v1.schema.json"
AUDITOR_OUTPUT_SCHEMA = SCHEMAS_DIR / "auditor-output.v1.schema.json"
MEASUREMENT_SCHEMA = SCHEMAS_DIR / "measurement-run.v1.schema.json"

EXPERIMENTS_DIR = REPO_ROOT / "experiments"

PASS = "PASS"

# Höher = strenger. Werte mit gleicher Stufe sind in dieser Tabelle nicht erlaubt;
# das Validator-Pattern wählt das Maximum. Werte, die nicht im Mapping stehen,
# zählen als 0 (also gleich PASS) und blockieren entsprechende PASS-Regel.
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


def _has_run_event(evidence_file: Path) -> bool:
    return bool(_read_evidence_run_artifacts(evidence_file))


def _is_canonical_false_markdown(path: Path) -> bool:
    """True, wenn die Markdown-Datei explizit canonical:false oder
    source_of_truth:false im YAML-Frontmatter trägt."""
    if not path.is_file() or path.suffix.lower() != ".md":
        return False
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return False
    if not text.startswith("---"):
        return False
    parts = text.split("---", 2)
    if len(parts) < 3:
        return False
    try:
        fm = yaml.safe_load(parts[1]) or {}
    except Exception:
        return False
    if not isinstance(fm, dict):
        return False
    if fm.get("canonical") is False:
        return True
    if fm.get("source_of_truth") is False:
        return True
    return False


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

    Gibt eine Liste menschlich lesbarer Fehlermeldungen zurück. Eine leere
    Liste bedeutet: alle Cross-File-Regeln passen.
    """
    errors: list[str] = []
    experiments_dir = repo_root / "experiments"
    if not experiments_dir.is_dir():
        return errors

    bundle_validator = _build_validator(RUN_BUNDLE_SCHEMA)
    auditor_validator = _build_validator(AUDITOR_OUTPUT_SCHEMA)
    measurement_validator = _build_validator(MEASUREMENT_SCHEMA)

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
                    if not target.exists():
                        errors.append(
                            f"  ❌ {rel_exp}: execution_ref '{ref}' existiert nicht."
                        )
                        continue
                    if ref.endswith("results/evidence.jsonl") or ref == "results/evidence.jsonl":
                        evidence_ref_present = True
                if not evidence_ref_present and evidence_file.is_file():
                    # Soft-Hinweis: Falls evidence.jsonl da ist, sollte sie auch verlinkt sein.
                    errors.append(
                        f"  ❌ {rel_exp}: execution_refs verweist nicht auf "
                        f"results/evidence.jsonl, obwohl die Datei existiert."
                    )

        # R4: artifact_refs aus evidence.jsonl
        for lineno, ref in run_events:
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
                continue
            if _is_canonical_false_markdown(target):
                errors.append(
                    f"  ❌ {rel_exp}/results/evidence.jsonl:{lineno}: "
                    f"artifact_ref '{ref}' zeigt auf eine non-canonical Markdown-Projektion. "
                    f"Verweise auf maschinelle Wahrheitsquellen (YAML/JSONL/JSON) statt auf "
                    f"Lesefläche."
                )

        # R5–R7: Run-Bundles unter artifacts/run-*/
        artifacts_dir = exp_dir / "artifacts"
        if artifacts_dir.is_dir():
            for run_dir in sorted(p for p in artifacts_dir.iterdir() if p.is_dir()):
                _validate_run_dir(
                    repo_root=repo_root,
                    exp_dir=exp_dir,
                    run_dir=run_dir,
                    bundle_validator=bundle_validator,
                    auditor_validator=auditor_validator,
                    measurement_validator=measurement_validator,
                    errors=errors,
                )

    return errors


def _validate_run_dir(
    *,
    repo_root: Path,
    exp_dir: Path,
    run_dir: Path,
    bundle_validator: Draft202012Validator,
    auditor_validator: Draft202012Validator,
    measurement_validator: Draft202012Validator,
    errors: list[str],
) -> None:
    """Validiert ein einzelnes artifacts/<run-id>/-Verzeichnis."""
    rel_run = run_dir.relative_to(repo_root)
    run_yml = run_dir / "run.yml"
    auditor_yml = run_dir / "auditor-output.yml"
    measurement_yml = run_dir / "measurement.yml"

    bundle: dict | None = None

    # R5: run.yml
    if run_yml.is_file():
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
                if not isinstance(artifact, dict):
                    continue
                path_str = artifact.get("path")
                if not isinstance(path_str, str) or not path_str:
                    errors.append(
                        f"  ❌ {rel_run}/run.yml: artifacts.{key}.path fehlt."
                    )
                    continue
                target = _resolve_within(exp_dir, str((run_dir.relative_to(exp_dir) / path_str)))
                if target is None:
                    errors.append(
                        f"  ❌ {rel_run}/run.yml: artifacts.{key}.path '{path_str}' "
                        f"verlässt das Experiment-Root."
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

        # auditor_output-Referenz auflösen
        ref = (measurement.get("source_artifacts") or {}).get("auditor_output")
        if not ref:
            ref = measurement.get("auditor_ref")
        if not ref:
            errors.append(
                f"  ❌ {rel_run}/measurement.yml: weder source_artifacts.auditor_output "
                f"noch auditor_ref ist gesetzt."
            )
            return

        ref_target = _resolve_within(exp_dir, str((run_dir.relative_to(exp_dir) / ref)))
        if ref_target is None:
            errors.append(
                f"  ❌ {rel_run}/measurement.yml: auditor-Referenz '{ref}' "
                f"verlässt das Experiment-Root."
            )
            return
        if not ref_target.is_file():
            errors.append(
                f"  ❌ {rel_run}/measurement.yml: auditor-Referenz '{ref}' "
                f"zeigt auf nicht existierende Datei."
            )
            return

        # Wenn die Referenz auf den passenden Auditor zeigt, Konsistenz prüfen.
        if auditor_data is not None and ref_target.resolve() == auditor_yml.resolve():
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
    print("✅ All run bundles consistent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
