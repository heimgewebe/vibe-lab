#!/usr/bin/env python3
"""promote.py — Adoption-Completeness-Validator.

Prüft, ob jedes Experiment mit ``status: adopted`` die erwarteten
Katalog-Artefakte erzeugt hat. Fehlende Artefakte werden als Fehler
gemeldet; CI schlägt fehl, wenn adoptierte Erkenntnisse nicht in die
Bibliothek verdichtet wurden.

Erwartete Extraktion pro adopted Experiment:
  - ≥1 Technique  (catalog/techniques/)
  - ≥1 Prompt     (prompts/adopted/)
  - ≥1 Anti-Pattern (catalog/anti-patterns/) — sofern failure_modes.md
    Substanz enthält

Optionale Extraktion (kein harter Fehler, aber Warnung):
  - Combo          (catalog/combos/)
  - Workflow        (catalog/workflows/)

Gate-Logik:
  - Nur ``status: adopted`` Experimente werden geprüft.
  - Artefakt-Zuordnung erfolgt über ``evidence_source`` im Frontmatter
    des Katalog-Eintrags ODER über ``relations[].target`` Rück-Verweise.

Benötigt: pip install pyyaml
"""

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: Missing dependency. Run: pip install pyyaml")
    sys.exit(1)

# Pfade auf _paths.py-Konventionen (write_if_changed etc.) verzichten —
# dieser Validator schreibt nichts, er liest und meldet nur.
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
EXPERIMENTS_DIR = REPO_ROOT / "experiments"
CATALOG_DIR = REPO_ROOT / "catalog"
PROMPTS_DIR = REPO_ROOT / "prompts" / "adopted"
INSTRUCTION_BLOCKS_DIR = REPO_ROOT / "instruction-blocks"

# Mindestgröße für failure_modes.md "mit Substanz"
_CONTENT_THRESHOLD = 300


def _load_manifest(path: Path) -> dict:
    """Lädt manifest.yml; wirft bei Fehler."""
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"manifest root must be a mapping, got {type(data).__name__}")
    return data


def _extract_frontmatter(path: Path) -> dict | None:
    """Liest YAML-Frontmatter aus Markdown-Datei."""
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return None
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    try:
        return yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return None


def _find_catalog_references(experiment_path: str) -> dict[str, list[str]]:
    """Durchsucht Katalog und Prompts nach Referenzen auf ein Experiment.

    Gibt ein Dict zurück: { category: [dateiname, ...] }
    category ∈ {technique, anti-pattern, prompt, combo, workflow, style, instruction-block}
    """
    refs: dict[str, list[str]] = {
        "technique": [],
        "anti-pattern": [],
        "prompt": [],
        "combo": [],
        "workflow": [],
        "style": [],
        "instruction-block": [],
    }

    # Experiment-Pfad normalisieren: z.B. "experiments/2026-04-08_spec-first/"
    exp_slug = experiment_path.rstrip("/")

    # 1. catalog/ durchsuchen
    search_dirs: list[tuple[Path, str]] = [
        (CATALOG_DIR / "techniques", "technique"),
        (CATALOG_DIR / "anti-patterns", "anti-pattern"),
        (CATALOG_DIR / "combos", "combo"),
        (CATALOG_DIR / "workflows", "workflow"),
        (CATALOG_DIR / "styles", "style"),
    ]

    for search_dir, category in search_dirs:
        if not search_dir.exists():
            continue
        for md_file in sorted(search_dir.glob("*.md")):
            fm = _extract_frontmatter(md_file)
            if fm is None:
                continue
            # Prüfe evidence_source
            evidence_source = fm.get("evidence_source", "")
            if exp_slug in str(evidence_source):
                refs[category].append(md_file.name)
                continue
            # Prüfe relations
            for rel in fm.get("relations", []) or []:
                target = rel.get("target", "")
                if exp_slug in str(target):
                    refs[category].append(md_file.name)
                    break

    # 2. prompts/adopted/ durchsuchen
    if PROMPTS_DIR.exists():
        for md_file in sorted(PROMPTS_DIR.glob("*.md")):
            fm = _extract_frontmatter(md_file)
            if fm is None:
                continue
            for rel in fm.get("relations", []) or []:
                target = rel.get("target", "")
                if exp_slug in str(target):
                    refs["prompt"].append(md_file.name)
                    break

    # 3. instruction-blocks/ durchsuchen
    if INSTRUCTION_BLOCKS_DIR.exists():
        for md_file in sorted(INSTRUCTION_BLOCKS_DIR.glob("*.md")):
            fm = _extract_frontmatter(md_file)
            if fm is None:
                continue
            evidence_source = fm.get("evidence_source", "")
            if exp_slug in str(evidence_source):
                refs["instruction-block"].append(md_file.name)
                continue
            for rel in fm.get("relations", []) or []:
                target = rel.get("target", "")
                if exp_slug in str(target):
                    refs["instruction-block"].append(md_file.name)
                    break

    return refs


def validate_experiment(exp_dir: Path) -> tuple[list[str], list[str]]:
    """Validiert ein adopted Experiment auf Katalog-Completeness.

    Returns:
        (errors, warnings) — hard errors and soft warnings.
    """
    errors: list[str] = []
    warnings: list[str] = []
    exp_name = exp_dir.name

    manifest_path = exp_dir / "manifest.yml"
    if not manifest_path.exists():
        return errors, warnings

    manifest = _load_manifest(manifest_path)
    exp = manifest.get("experiment", {})
    status = exp.get("status", "")
    if status != "adopted":
        return errors, warnings

    # Experiment-Pfad relativ zum Repo
    exp_rel = f"experiments/{exp_name}"
    refs = _find_catalog_references(exp_rel)

    # Hard: ≥1 Technique
    if not refs["technique"]:
        errors.append(
            f"{exp_name}: Kein Technique-Eintrag in catalog/techniques/ referenziert dieses Experiment."
            f" Jedes adopted Experiment muss ≥1 Technique extrahieren."
        )

    # Hard: ≥1 Prompt
    if not refs["prompt"]:
        errors.append(
            f"{exp_name}: Kein Prompt in prompts/adopted/ referenziert dieses Experiment."
            f" Jedes adopted Experiment muss ≥1 Prompt extrahieren."
        )

    # Conditional hard: ≥1 Anti-Pattern wenn failure_modes.md Substanz hat
    fm_path = exp_dir / "failure_modes.md"
    has_substantive_fm = (
        fm_path.is_file() and fm_path.stat().st_size > _CONTENT_THRESHOLD
    )
    if has_substantive_fm and not refs["anti-pattern"]:
        errors.append(
            f"{exp_name}: failure_modes.md hat Substanz, aber kein Anti-Pattern in"
            f" catalog/anti-patterns/ referenziert dieses Experiment."
        )

    # Soft: Combo
    if not refs["combo"]:
        warnings.append(
            f"{exp_name}: Kein Combo-Eintrag referenziert dieses Experiment."
            f" Prüfe, ob eine Kombination mit anderen Techniques sinnvoll wäre."
        )

    # Soft: Instruction-Block
    if not refs["instruction-block"]:
        warnings.append(
            f"{exp_name}: Kein Instruction-Block referenziert dieses Experiment."
            f" Prüfe, ob ein portabler Denkbaustein extrahierbar wäre."
        )

    return errors, warnings


def main() -> None:
    if not EXPERIMENTS_DIR.exists():
        print(f"ERROR: experiments/ Verzeichnis nicht gefunden: {EXPERIMENTS_DIR}")
        sys.exit(1)

    all_errors: list[str] = []
    all_warnings: list[str] = []
    checked = 0

    for entry in sorted(EXPERIMENTS_DIR.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name.startswith("_"):
            continue

        manifest_path = entry / "manifest.yml"
        if not manifest_path.exists():
            continue

        try:
            manifest = _load_manifest(manifest_path)
        except Exception as exc:
            all_errors.append(f"{entry.name}: manifest.yml nicht lesbar: {exc}")
            continue

        if manifest.get("experiment", {}).get("status") != "adopted":
            continue

        checked += 1
        errors, warnings = validate_experiment(entry)
        all_errors.extend(errors)
        all_warnings.extend(warnings)

    # Warnungen ausgeben (nicht-blockierend)
    if all_warnings:
        print("⚠️  Adoption-Completeness Warnungen:\n")
        for w in all_warnings:
            print(f"  ⚠️  {w}")
        print()

    if all_errors:
        print("❌ Adoption-Completeness Validation FAILED:\n")
        for err in all_errors:
            print(f"  ❌ {err}")
        print(
            f"\n{len(all_errors)} Fehler gefunden."
            " Adopted Experimente müssen Katalog-Artefakte extrahieren."
            " Siehe: .vibe/quality-gates.yml → testing-to-adopted"
        )
        sys.exit(1)
    else:
        print(
            f"✅ Adoption-Completeness: {checked} adopted Experiment(e)"
            f" mit vollständiger Katalog-Extraktion."
        )


if __name__ == "__main__":
    main()
