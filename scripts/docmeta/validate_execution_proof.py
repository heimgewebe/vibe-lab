#!/usr/bin/env python3
"""validate_execution_proof.py — Execution-Proof-Validator.

Prüft die Kopplung zwischen deklariertem Durchführungsgrad und tatsächlichem Artefakt:

1. Für jedes Experiment mit ``execution_status ∈ {executed, replicated}`` muss mindestens
   eine Datei ``artifacts/<run-id>/run_meta.json`` existieren und gegen
   ``schemas/run_meta.schema.json`` valide sein.
2. Das in ``run_meta.json`` angegebene ``test_output_file`` muss als Datei existieren und
   innerhalb des Experiment-Roots liegen (Pfad-Escape-Schutz).
3. Für jedes Experiment mit ``status: adopted`` muss ``adoption_basis`` gesetzt sein.
   Bei ``adoption_basis: reconstructed`` muss ``results/result.md`` die Marker-Zeichenkette
   ``adoption_basis: reconstructed`` enthalten (sichtbare Annotation gem.
   docs/blueprints/blueprint-v2.md Übergangsregel).

Benötigt: python3 -m pip install pyyaml jsonschema rfc3339-validator
"""

import json
import sys
from datetime import date
from pathlib import Path

try:
    import yaml
    from jsonschema import Draft202012Validator, ValidationError, SchemaError
    from jsonschema.validators import validator_for
except ImportError:
    print("ERROR: Missing dependencies. Run: python3 -m pip install pyyaml jsonschema rfc3339-validator")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
RUN_META_SCHEMA = REPO_ROOT / "schemas" / "run_meta.schema.json"

PROOF_REQUIRED_STATUSES: frozenset[str] = frozenset({"executed", "replicated"})
RECONSTRUCTED_MARKER = "adoption_basis: reconstructed"

# Enforcement der Übergangsregel aus docs/blueprints/blueprint-v2.md:
# Reconstructed Adoption ist nur für Altbestand zulässig. Experimente, die NACH
# dem v2-Merge-Datum angelegt wurden, dürfen adoption_basis=reconstructed nicht
# verwenden. Seit Phase 1b: harter Fehler (zuvor Warnung), gemeinsam mit
# Decision-Type-Separation (siehe validate_schema.py::validate_decision_files).
V2_MERGE_DATE = date(2026, 4, 15)

errors: list[str] = []


def load_schema(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def load_yaml(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f) or {}


def validate_run_meta_for_experiment(exp_dir: Path, validator: Draft202012Validator) -> None:
    """Prüft, dass mindestens eine valide run_meta.json vorhanden ist."""
    artifacts_dir = exp_dir / "artifacts"
    rel = exp_dir.relative_to(REPO_ROOT)

    if not artifacts_dir.is_dir():
        errors.append(
            f"  ❌ {rel}: artifacts/ fehlt, aber execution_status verlangt run_meta.json"
        )
        return

    run_metas = list(artifacts_dir.glob("*/run_meta.json"))
    if not run_metas:
        errors.append(
            f"  ❌ {rel}: keine artifacts/<run-id>/run_meta.json gefunden, "
            f"aber execution_status ∈ {{executed, replicated}}"
        )
        return

    valid_count = 0
    for run_meta in run_metas:
        try:
            data = json.loads(run_meta.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            errors.append(f"  ❌ {run_meta.relative_to(REPO_ROOT)}: invalid JSON — {e}")
            continue

        try:
            validator.validate(data)
        except ValidationError as e:
            errors.append(f"  ❌ {run_meta.relative_to(REPO_ROOT)}: {e.message}")
            continue

        # run_id muss mit Ordnername übereinstimmen
        declared_run_id = data.get("run_id")
        actual_run_id = run_meta.parent.name
        if declared_run_id != actual_run_id:
            errors.append(
                f"  ❌ {run_meta.relative_to(REPO_ROOT)}: "
                f"run_id '{declared_run_id}' stimmt nicht mit Ordnername '{actual_run_id}' überein"
            )
            continue

        # test_output_file muss existieren und innerhalb des Experiment-Roots liegen
        test_output_file = data.get("test_output_file", "")
        try:
            output_path = (exp_dir / test_output_file).resolve()
            output_path.relative_to(exp_dir.resolve())
        except ValueError:
            errors.append(
                f"  ❌ {run_meta.relative_to(REPO_ROOT)}: "
                f"test_output_file '{test_output_file}' verlässt Experiment-Root"
            )
            continue

        if not output_path.is_file():
            errors.append(
                f"  ❌ {run_meta.relative_to(REPO_ROOT)}: "
                f"test_output_file '{test_output_file}' existiert nicht oder ist keine Datei"
            )
            continue

        print(f"  ✅ {run_meta.relative_to(REPO_ROOT)}")
        valid_count += 1

    if valid_count == 0:
        errors.append(
            f"  ❌ {rel}: keine valide run_meta.json unter artifacts/ gefunden"
        )


def validate_adoption_basis(exp_dir: Path, manifest: dict) -> None:
    """Prüft adoption_basis-Pflicht bei status: adopted und Marker bei reconstructed."""
    experiment = manifest.get("experiment", {})
    status = experiment.get("status", "")
    if status != "adopted":
        return

    rel = exp_dir.relative_to(REPO_ROOT)
    adoption_basis = experiment.get("adoption_basis")
    if not adoption_basis:
        errors.append(
            f"  ❌ {rel}: status=adopted, aber adoption_basis fehlt"
        )
        return

    if adoption_basis == "reconstructed":
        result_md = exp_dir / "results" / "result.md"
        if not result_md.is_file():
            errors.append(
                f"  ❌ {rel}: adoption_basis=reconstructed, aber results/result.md fehlt "
                f"(sichtbare Annotation erforderlich)"
            )
            return

        content = result_md.read_text(encoding="utf-8")
        if RECONSTRUCTED_MARKER not in content:
            errors.append(
                f"  ❌ {result_md.relative_to(REPO_ROOT)}: "
                f"adoption_basis=reconstructed, aber Marker-Zeichenkette "
                f"'{RECONSTRUCTED_MARKER}' fehlt im result.md "
                f"(Pflicht gem. blueprint-v2 Übergangsregel)"
            )
            return

        # Übergangsregel: created-Datum gegen V2-Merge-Datum prüfen (hartes Enforcement seit Phase 1b).
        # created wird strikt als ISO-8601 YYYY-MM-DD geparst, damit der Vergleich nicht
        # auf lexikographischer String-Ordnung beruht (z.B. "2026-4-9" würde sonst falsch
        # einsortiert). Fehlendes/ungültiges Datum ist ein eigener Fehler.
        created_raw = experiment.get("created")
        if created_raw is None or created_raw == "":
            errors.append(
                f"  ❌ {rel}: adoption_basis=reconstructed, aber created-Feld fehlt im Manifest "
                f"(Pflicht für Übergangsregel-Prüfung gem. blueprint-v2)."
            )
            return

        created_str = str(created_raw)
        try:
            created_date = date.fromisoformat(created_str)
        except ValueError:
            errors.append(
                f"  ❌ {rel}: created='{created_str}' ist kein ISO-8601-Datum (YYYY-MM-DD). "
                f"Pflicht für Übergangsregel-Prüfung bei adoption_basis=reconstructed."
            )
            return

        if created_date >= V2_MERGE_DATE:
            errors.append(
                f"  ❌ {rel}: adoption_basis=reconstructed bei created={created_date.isoformat()} "
                f"(≥ v2-Merge-Datum {V2_MERGE_DATE.isoformat()}). "
                f"Reconstructed Adoption ist nur für Altbestand zulässig — "
                f"neue Adoptionen müssen adoption_basis ∈ {{executed, replicated}} "
                f"tragen (siehe docs/blueprints/blueprint-v2.md Übergangsregel)."
            )
            return

        print(f"  ✅ {rel}: adoption_basis=reconstructed mit sichtbarer Annotation")
    else:
        print(f"  ✅ {rel}: adoption_basis={adoption_basis}")


def main() -> None:
    print("🔍 Execution-Proof Validation")
    print()

    if not RUN_META_SCHEMA.exists():
        print(f"ERROR: schema not found: {RUN_META_SCHEMA}")
        sys.exit(1)

    schema = load_schema(RUN_META_SCHEMA)

    # Schema einmalig selbst validieren, damit ein kaputtes Schema nicht
    # pro Experiment neu zu Folgefehlern führt.
    validator_cls = validator_for(schema, default=Draft202012Validator)
    try:
        validator_cls.check_schema(schema)
    except SchemaError as e:
        print(f"ERROR: run_meta schema itself invalid: {e.message}")
        sys.exit(2)

    # format_checker erzwingt "format": "date-time" u.a. (sonst nur informativ)
    validator = validator_cls(schema, format_checker=validator_cls.FORMAT_CHECKER)

    experiments_dir = REPO_ROOT / "experiments"

    print("run_meta.json proofs:")
    proof_checked = 0
    for manifest_path in sorted(experiments_dir.glob("*/manifest.yml")):
        exp_dir = manifest_path.parent
        if exp_dir.name.startswith("_"):
            continue  # Skip _template, _archive

        try:
            manifest = load_yaml(manifest_path)
        except Exception as e:
            errors.append(f"  ❌ {manifest_path.relative_to(REPO_ROOT)}: YAML-Fehler — {e}")
            continue

        exec_status = manifest.get("experiment", {}).get("execution_status")
        if exec_status in PROOF_REQUIRED_STATUSES:
            proof_checked += 1
            validate_run_meta_for_experiment(exp_dir, validator)

    if proof_checked == 0:
        print("  (kein Experiment mit execution_status ∈ {executed, replicated})")

    print()
    print("adoption_basis:")
    adoption_checked = 0
    for manifest_path in sorted(experiments_dir.glob("*/manifest.yml")):
        exp_dir = manifest_path.parent
        if exp_dir.name.startswith("_"):
            continue

        try:
            manifest = load_yaml(manifest_path)
        except Exception as e:
            errors.append(f"  ❌ {manifest_path.relative_to(REPO_ROOT)}: YAML-Fehler — {e}")
            continue

        if manifest.get("experiment", {}).get("status") == "adopted":
            adoption_checked += 1
            validate_adoption_basis(exp_dir, manifest)

    if adoption_checked == 0:
        print("  (kein Experiment mit status=adopted)")

    print()
    if errors:
        print("❌ Execution-Proof FAILED:")
        for err in errors:
            print(err)
        sys.exit(1)
    else:
        print("✅ All execution-proof checks passed.")


if __name__ == "__main__":
    main()
