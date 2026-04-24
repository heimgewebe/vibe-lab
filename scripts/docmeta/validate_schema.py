#!/usr/bin/env python3
"""validate_schema.py — Validiert Artefakte gegen JSON-Schemas.

Prüft:
- experiments/*/manifest.yml gegen schemas/experiment.manifest.schema.json
- catalog/**/*.md Frontmatter gegen schemas/catalog.entry.schema.json
- catalog/combos/**/*.md Frontmatter gegen schemas/combo.schema.json
- experiments/*/results/evidence.jsonl auf Struktur und Taxonomie
- experiments/*/results/decision.yml gegen schemas/decision.schema.json,
  plus cross-file Regel: decision_type=adoption_assessment erfordert
  execution_status ∈ {executed, replicated} im Geschwister-manifest.yml
  (gem. docs/concepts/execution-bound-epistemics.md §10.2)

Benötigt: python3 -m pip install pyyaml jsonschema rfc3339-validator
"""

import json
import re
import sys
from pathlib import Path

# Gemeinsame Pfad-Logik aus _paths.py
sys.path.insert(0, str(Path(__file__).parent))
from _paths import extract_frontmatter  # noqa: E402

try:
    import yaml
    from jsonschema import Draft202012Validator, ValidationError, SchemaError
    from jsonschema.validators import validator_for
except ImportError:
    print("ERROR: Missing dependencies. Run: python3 -m pip install pyyaml jsonschema rfc3339-validator")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

SCHEMA_MAP = {
    "experiment_manifest": REPO_ROOT / "schemas" / "experiment.manifest.schema.json",
    "catalog_entry": REPO_ROOT / "schemas" / "catalog.entry.schema.json",
    "combo": REPO_ROOT / "schemas" / "combo.schema.json",
    "decision": REPO_ROOT / "schemas" / "decision.schema.json",
}

# Erlaubte execution_status-Werte für decision_type=adoption_assessment
# (gem. docs/concepts/execution-bound-epistemics.md §10.2)
ADOPTION_ALLOWED_EXECUTION_STATUSES: frozenset[str] = frozenset({"executed", "replicated"})

# Pflichtfelder für jede Zeile in evidence.jsonl
EVIDENCE_REQUIRED_KEYS: frozenset[str] = frozenset({
    "event_type", "timestamp", "iteration", "metric", "value", "context"
})

# Erlaubte Werte für event_type
EVIDENCE_EVENT_TYPES: frozenset[str] = frozenset({"observation", "measurement", "decision", "run"})

# Muster für Template-Platzhalter in failure_modes.md (case-insensitive, whitespace-tolerant)
FAILURE_MODES_PLACEHOLDER_RE = re.compile(r"-\s*\[\s*\]\s*TODO", re.IGNORECASE)

# Statuses, die eine ausgefüllte failure_modes.md erfordern
# Hinweis: Nur bei adopted/Promotion Pflicht. Für testing ist failure_modes.md
# empfohlen, aber nicht erzwungen (siehe CONTRIBUTING.md, quality-gates.yml).
FAILURE_MODES_REQUIRED_STATUSES: frozenset[str] = frozenset({"adopted"})

# Pfad zum docmeta-Kanonicalschema (contracts/, nicht schemas/)
DOCMETA_SCHEMA_PATH = REPO_ROOT / "contracts" / "docmeta.schema.json"

errors = []


def load_schema(schema_path: Path) -> dict:
    with open(schema_path) as f:
        return json.load(f)


def load_yaml(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f) or {}


def build_validator(schema: dict) -> Draft202012Validator:
    """Erzeugt einen Validator mit aktivem format_checker.

    ``jsonschema.validate()`` prüft ``format`` per Default NICHT. Ohne diesen
    Helper würden Felder wie ``date`` (manifest.yml, decision.yml, combo.md,
    catalog entries) nur syntaktisch als String akzeptiert, selbst wenn
    ``"format": "date"`` im Schema steht. Siehe auch
    ``validate_execution_proof.py``, das denselben Pattern für ``run_meta.json``
    verwendet.
    """
    validator_cls = validator_for(schema, default=Draft202012Validator)
    validator_cls.check_schema(schema)
    return validator_cls(schema, format_checker=validator_cls.FORMAT_CHECKER)


def validate_experiment_manifests():
    schema_path = SCHEMA_MAP["experiment_manifest"]
    if not schema_path.exists():
        errors.append(f"  Schema not found: {schema_path}")
        return

    schema = load_schema(schema_path)
    try:
        validator = build_validator(schema)
    except SchemaError as e:
        errors.append(f"  ❌ Schema error ({schema_path.name}): {e.message}")
        return

    experiments_dir = REPO_ROOT / "experiments"

    for manifest in experiments_dir.glob("*/manifest.yml"):
        if manifest.parent.name.startswith("_"):
            continue  # Skip _template, _archive
        try:
            data = load_yaml(manifest)
            validator.validate(data)
            print(f"  ✅ {manifest.relative_to(REPO_ROOT)}")
        except ValidationError as e:
            errors.append(f"  ❌ {manifest.relative_to(REPO_ROOT)}: {e.message}")


def validate_catalog_entries():
    schema_path = SCHEMA_MAP["catalog_entry"]
    combo_schema_path = SCHEMA_MAP["combo"]
    if not schema_path.exists():
        errors.append(f"  Schema not found: {schema_path}")
        return

    schema = load_schema(schema_path)
    combo_schema = load_schema(combo_schema_path) if combo_schema_path.exists() else None
    try:
        entry_validator = build_validator(schema)
        combo_validator = build_validator(combo_schema) if combo_schema else None
    except SchemaError as e:
        errors.append(f"  ❌ Schema error: {e.message}")
        return

    catalog_dir = REPO_ROOT / "catalog"
    for md_file in catalog_dir.rglob("*.md"):
        fm = extract_frontmatter(md_file)
        if fm is None:
            continue  # No frontmatter, skip

        # Use combo schema for combos/ entries
        is_combo = "combos" in md_file.relative_to(catalog_dir).parts
        active_validator = combo_validator if (is_combo and combo_validator) else entry_validator

        try:
            active_validator.validate(fm)
            print(f"  ✅ {md_file.relative_to(REPO_ROOT)}")
        except ValidationError as e:
            errors.append(f"  ❌ {md_file.relative_to(REPO_ROOT)}: {e.message}")


def validate_evidence_files():
    """Minimaler struktureller Check für evidence.jsonl Dateien.

    Prüft:
    - Jede Zeile ist gültiges JSON
    - Pflichtfelder (event_type, timestamp, iteration, metric, value, context) vorhanden
    - event_type ist in der erlaubten Taxonomie (observation, measurement, decision, run)
    - Wenn event_type == "run":
      - artifact_ref muss vorhanden sein
      - artifact_ref muss ein String sein
      - Der aufgelöste Pfad muss innerhalb des Experiment-Roots bleiben
      - Die referenzierte Datei muss als Datei existieren (is_file())
    """
    experiments_dir = REPO_ROOT / "experiments"
    found = 0
    for evidence_file in experiments_dir.glob("*/results/evidence.jsonl"):
        if evidence_file.parent.parent.name.startswith("_"):
            continue  # Skip _template, _archive
        found += 1
        lines = evidence_file.read_text(encoding="utf-8").strip().splitlines()
        for lineno, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError as e:
                errors.append(
                    f"  ❌ {evidence_file.relative_to(REPO_ROOT)}:{lineno}: invalid JSON — {e}"
                )
                continue

            if not isinstance(entry, dict):
                errors.append(
                    f"  ❌ {evidence_file.relative_to(REPO_ROOT)}:{lineno}: "
                    f"expected JSON object, got {type(entry).__name__}"
                )
                continue

            missing = EVIDENCE_REQUIRED_KEYS - entry.keys()
            if missing:
                errors.append(
                    f"  ❌ {evidence_file.relative_to(REPO_ROOT)}:{lineno}: "
                    f"missing required keys: {sorted(missing)}"
                )
                continue

            event_type = entry.get("event_type")
            if event_type not in EVIDENCE_EVENT_TYPES:
                errors.append(
                    f"  ❌ {evidence_file.relative_to(REPO_ROOT)}:{lineno}: "
                    f"event_type '{event_type}' not in allowlist {sorted(EVIDENCE_EVENT_TYPES)}"
                )
                continue

            if event_type == "run":
                artifact_ref = entry.get("artifact_ref")
                if not artifact_ref:
                    errors.append(
                        f"  ❌ {evidence_file.relative_to(REPO_ROOT)}:{lineno}: "
                        f"event_type 'run' requires 'artifact_ref'"
                    )
                    continue

                if not isinstance(artifact_ref, str):
                    errors.append(
                        f"  ❌ {evidence_file.relative_to(REPO_ROOT)}:{lineno}: "
                        f"artifact_ref must be a string, got {type(artifact_ref).__name__}"
                    )
                    continue

                exp_root = evidence_file.parent.parent
                try:
                    artifact_path = (exp_root / artifact_ref).resolve()
                    artifact_path.relative_to(exp_root.resolve())
                except ValueError:
                    errors.append(
                        f"  ❌ {evidence_file.relative_to(REPO_ROOT)}:{lineno}: "
                        f"artifact_ref '{artifact_ref}' escapes experiment root"
                    )
                    continue
                except Exception as e:
                    errors.append(
                        f"  ❌ {evidence_file.relative_to(REPO_ROOT)}:{lineno}: "
                        f"invalid artifact_ref path '{artifact_ref}' — {e}"
                    )
                    continue

                if not artifact_path.is_file():
                    errors.append(
                        f"  ❌ {evidence_file.relative_to(REPO_ROOT)}:{lineno}: "
                        f"artifact_ref '{artifact_ref}' does not exist or is not a file"
                    )
                    continue

            print(f"  ✅ {evidence_file.relative_to(REPO_ROOT)}:{lineno} ({event_type})")

    if found == 0:
        print("  (no evidence.jsonl files found outside _template/_archive)")


def validate_decision_files():
    """Validiert experiments/*/results/decision.yml gegen decision.schema.json.

    Zusätzlich zur Schema-Validierung erzwingt diese Funktion die cross-file Regel
    aus execution-bound-epistemics.md §10.2:

    Wenn ``decision_type == "adoption_assessment"``, muss das Geschwister-Manifest
    (``../manifest.yml``) ``experiment.execution_status ∈ {executed, replicated}``
    tragen. Andere Decision-Typen haben keine execution_status-Bedingung.
    """
    schema_path = SCHEMA_MAP["decision"]
    if not schema_path.exists():
        errors.append(f"  Schema not found: {schema_path}")
        return

    schema = load_schema(schema_path)
    try:
        validator = build_validator(schema)
    except SchemaError as e:
        errors.append(f"  ❌ Schema error ({schema_path.name}): {e.message}")
        return

    experiments_dir = REPO_ROOT / "experiments"

    found = 0
    for decision_path in sorted(experiments_dir.glob("*/results/decision.yml")):
        # Skip _template, _archive (parent.parent ist der Experiment-Ordner)
        if decision_path.parent.parent.name.startswith("_"):
            continue
        found += 1
        rel = decision_path.relative_to(REPO_ROOT)

        try:
            data = load_yaml(decision_path)
        except Exception as e:
            errors.append(f"  ❌ {rel}: YAML-Fehler — {e}")
            continue

        try:
            validator.validate(data)
        except ValidationError as e:
            errors.append(f"  ❌ {rel}: {e.message}")
            continue

        # Anti-Scheinfalsifikation (P2): counterevidence_checked=false + verdict=confirms
        # ist inkonsistent. Nur bei decision_type=result_assessment anwenden.
        # Kein genereller Zwang counterevidence_checked=true einzuführen; nur der
        # inkonsistente Fall wird hart blockiert. Ziel: Bestätigung verteuern,
        # nicht Bürokratie erzwingen.
        decision_type_for_p2 = data.get("decision_type")
        if decision_type_for_p2 == "result_assessment":
            verdict = data.get("verdict")
            cev_checked = data.get("counterevidence_checked")
            if cev_checked is False and verdict == "confirms":
                errors.append(
                    f"  ❌ {rel}: counterevidence_checked=false ist inkonsistent "
                    f"mit verdict=confirms. Entweder counterevidence_checked auf true setzen "
                    f"(mit belegter Gegenprüfung) oder verdict auf mixed/inconclusive/refutes "
                    f"ändern. Leitregel: Bestätigung verlangt Gegenprüfung."
                )
                continue
            # Konsistenz counter_hypothesis_outcome ↔ verdict:
            # 'found_and_confirming' (Gegenhypothese stützt sich selbst)
            # widerspricht verdict=confirms der Ursprungshypothese.
            outcome = data.get("counter_hypothesis_outcome")
            if outcome == "found_and_confirming" and verdict == "confirms":
                errors.append(
                    f"  ❌ {rel}: counter_hypothesis_outcome=found_and_confirming "
                    f"widerspricht verdict=confirms (Gegenhypothese wird gestützt → "
                    f"Ursprungshypothese nicht mehr bestätigt). verdict auf "
                    f"mixed/refutes/inconclusive ändern."
                )
                continue

        # Cross-file Regel: adoption_assessment → execution_status ∈ {executed, replicated}
        decision_type = data.get("decision_type")
        if decision_type == "adoption_assessment":
            manifest_path = decision_path.parent.parent / "manifest.yml"
            if not manifest_path.is_file():
                errors.append(
                    f"  ❌ {rel}: decision_type=adoption_assessment, "
                    f"aber Geschwister-manifest.yml fehlt unter {manifest_path.relative_to(REPO_ROOT)}"
                )
                continue

            try:
                manifest = load_yaml(manifest_path)
            except Exception as e:
                errors.append(
                    f"  ❌ {manifest_path.relative_to(REPO_ROOT)}: YAML-Fehler — {e}"
                )
                continue

            exec_status = manifest.get("experiment", {}).get("execution_status", "")
            if exec_status not in ADOPTION_ALLOWED_EXECUTION_STATUSES:
                errors.append(
                    f"  ❌ {rel}: decision_type=adoption_assessment verlangt "
                    f"execution_status ∈ {sorted(ADOPTION_ALLOWED_EXECUTION_STATUSES)} "
                    f"im zugehörigen manifest.yml, aber execution_status='{exec_status}' "
                    f"(siehe docs/concepts/execution-bound-epistemics.md §10.2)"
                )
                continue

        print(f"  ✅ {rel} ({decision_type})")

    if found == 0:
        print("  (no decision.yml files found outside _template/_archive)")


def validate_adoption_decision_coverage():
    """Symmetrische cross-file Regel: echte Adoption braucht adoption_assessment.

    Ergänzt ``validate_decision_files()`` um die Gegenrichtung. Dort wurde nur
    die Eingangsrichtung erzwungen (``adoption_assessment`` → Manifest muss
    ``execution_status ∈ {executed, replicated}`` tragen). Ohne die hier
    implementierte Gegenrichtung bleibt die Umgehung offen, dass ein Manifest
    Adoption behauptet, während das zugehörige ``decision.yml`` nur
    ``result_assessment`` ist.

    Pflichtregel:
        experiment.status == "adopted"
        und experiment.adoption_basis ∈ {"executed", "replicated"}
        → ``results/decision.yml`` muss existieren und
          ``decision_type == "adoption_assessment"`` tragen.

    Historische Ausnahme:
        experiment.status == "adopted" und adoption_basis == "reconstructed"
        bleibt ohne adoption_assessment zulässig (Altbestand gem.
        docs/blueprints/blueprint-v2.md Übergangsregel). Die sichtbare
        Rekonstruktionsannotation wird separat in
        ``validate_execution_proof.py`` geprüft.

    Hintergrund: docs/concepts/execution-bound-epistemics.md §10.1–10.2.
    """
    experiments_dir = REPO_ROOT / "experiments"
    checked = 0

    for manifest_path in sorted(experiments_dir.glob("*/manifest.yml")):
        if manifest_path.parent.name.startswith("_"):
            continue  # Skip _template, _archive

        try:
            manifest = load_yaml(manifest_path)
        except Exception as e:
            errors.append(f"  ❌ {manifest_path.relative_to(REPO_ROOT)}: YAML-Fehler — {e}")
            continue

        experiment = manifest.get("experiment", {})
        status = experiment.get("status", "")
        adoption_basis = experiment.get("adoption_basis", "")

        if status != "adopted":
            continue
        if adoption_basis not in ADOPTION_ALLOWED_EXECUTION_STATUSES:
            # reconstructed oder leer → Historische Ausnahme, hier nichts zu tun.
            continue

        checked += 1
        exp_dir = manifest_path.parent
        rel_exp = exp_dir.relative_to(REPO_ROOT)
        decision_path = exp_dir / "results" / "decision.yml"

        if not decision_path.is_file():
            errors.append(
                f"  ❌ {rel_exp}: Manifest behauptet Adoption "
                f"(status=adopted, adoption_basis={adoption_basis}), aber "
                f"results/decision.yml fehlt. Echte Adoption verlangt ein "
                f"decision.yml mit decision_type=adoption_assessment "
                f"(siehe docs/concepts/execution-bound-epistemics.md §10.1)."
            )
            continue

        try:
            decision = load_yaml(decision_path)
        except Exception as e:
            # YAML-Fehler meldet validate_decision_files() bereits separat.
            # Hier nichts doppelt loggen.
            continue

        decision_type = decision.get("decision_type")
        if decision_type != "adoption_assessment":
            errors.append(
                f"  ❌ {decision_path.relative_to(REPO_ROOT)}: Manifest behauptet "
                f"Adoption (status=adopted, adoption_basis={adoption_basis}), "
                f"also muss decision_type=adoption_assessment sein, "
                f"gefunden: '{decision_type}'. "
                f"Resultatsbewertung ≠ Adoptionsentscheidung "
                f"(siehe docs/concepts/execution-bound-epistemics.md §10.1)."
            )
            continue

        print(f"  ✅ {rel_exp}: adoption_basis={adoption_basis} ↔ adoption_assessment")

    if checked == 0:
        print("  (kein Experiment mit status=adopted + adoption_basis ∈ {executed, replicated})")


def validate_failure_modes():
    """Prüft failure_modes.md für Experimente mit Status testing oder adopted.

    Regeln:
    - Datei muss existieren (Pflicht bei status=testing/adopted).
    - Darf keine Template-Platzhalter ('- [ ] TODO:') enthalten.
    """
    experiments_dir = REPO_ROOT / "experiments"
    checked = 0

    for manifest_path in sorted(experiments_dir.glob("*/manifest.yml")):
        if manifest_path.parent.name.startswith("_"):
            continue  # Skip _template, _archive

        try:
            data = load_yaml(manifest_path)
        except Exception as e:
            errors.append(f"  ❌ {manifest_path.relative_to(REPO_ROOT)}: YAML-Fehler — {e}")
            continue

        status = data.get("experiment", {}).get("status", "")
        if status not in FAILURE_MODES_REQUIRED_STATUSES:
            continue

        checked += 1
        exp_dir = manifest_path.parent
        fm_path = exp_dir / "failure_modes.md"

        if not fm_path.exists():
            errors.append(
                f"  ❌ {exp_dir.relative_to(REPO_ROOT)}/failure_modes.md: "
                f"fehlt (Pflicht bei status={status})"
            )
            continue

        content = fm_path.read_text(encoding="utf-8")
        if FAILURE_MODES_PLACEHOLDER_RE.search(content):
            errors.append(
                f"  ❌ {fm_path.relative_to(REPO_ROOT)}: "
                f"enthält Template-Platzhalter (unfilled TODO items). "
                f"Muss vor Promotion ausgefüllt sein."
            )
            continue

        print(f"  ✅ {fm_path.relative_to(REPO_ROOT)} (status={status})")

    if checked == 0:
        print("  (keine Experimente mit Status testing/adopted gefunden)")


def validate_docmeta_frontmatter():
    """Validiert Markdown-Frontmatter gegen contracts/docmeta.schema.json.

    Geprüfte Zonen:
    - docs/**/*.md          (außer docs/_generated/)
    - prompts/**/*.md
    - experiments/*/*.md    (außer _template/, _archive/)
    - experiments/*/results/result.md (außer _template/, _archive/)

    Dateien ohne Frontmatter werden übersprungen (kein Fehler).
    Dateien mit Frontmatter müssen gegen das Schema validieren.
    """
    if not DOCMETA_SCHEMA_PATH.exists():
        errors.append(f"  Schema not found: {DOCMETA_SCHEMA_PATH}")
        return

    schema = load_schema(DOCMETA_SCHEMA_PATH)
    try:
        validator = build_validator(schema)
    except SchemaError as e:
        errors.append(f"  ❌ Schema error (docmeta.schema.json): {e.message}")
        return

    # Sammle alle Dateien (Set zur Deduplizierung)
    candidates: set[Path] = set()

    for md in (REPO_ROOT / "docs").rglob("*.md"):
        if "_generated" not in md.relative_to(REPO_ROOT).parts:
            candidates.add(md)

    for md in (REPO_ROOT / "prompts").rglob("*.md"):
        candidates.add(md)

    for md in (REPO_ROOT / "experiments").glob("*/*.md"):
        if not md.parent.name.startswith("_"):
            candidates.add(md)

    for md in (REPO_ROOT / "experiments").glob("*/results/result.md"):
        if not md.parent.parent.name.startswith("_"):
            candidates.add(md)

    checked = 0
    for md_file in sorted(candidates):
        fm = extract_frontmatter(md_file)
        if fm is None:
            continue  # kein Frontmatter — kein Fehler in dieser Zone

        try:
            validator.validate(fm)
            print(f"  ✅ {md_file.relative_to(REPO_ROOT)}")
            checked += 1
        except ValidationError as e:
            errors.append(f"  ❌ {md_file.relative_to(REPO_ROOT)}: {e.message}")

    if checked == 0:
        print("  (keine Markdown-Dateien mit Frontmatter in den Zielzonen gefunden)")


def main():
    print("🔍 Schema Validation")
    print()
    print("Experiment Manifests:")
    validate_experiment_manifests()
    print()
    print("Catalog Entries:")
    validate_catalog_entries()
    print()
    print("Evidence Files:")
    validate_evidence_files()
    print()
    print("Decision Files:")
    validate_decision_files()
    print()
    print("Adoption ↔ Decision Coverage:")
    validate_adoption_decision_coverage()
    print()
    print("Failure Modes:")
    validate_failure_modes()
    print()
    print("Docmeta Frontmatter:")
    validate_docmeta_frontmatter()
    print()

    if errors:
        print("❌ Validation FAILED:")
        for err in errors:
            print(err)
        sys.exit(1)
    else:
        print("✅ All schema validations passed.")


if __name__ == "__main__":
    main()
