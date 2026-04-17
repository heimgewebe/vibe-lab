#!/usr/bin/env python3
"""validate_interpretation_budget.py — Interpretation-Budget-Validator.

Prüft, dass jedes Experiment mit ``status: adopted`` in seiner ``results/result.md``
einen ausgefüllten ``## Interpretation Budget``-Block enthält mit mindestens einem
Eintrag in ``### Allowed Claims`` und ``### Disallowed Claims``.

Gate-Logik:
- Nur Experimente mit status=adopted werden geprüft.
- Alle anderen (testing, inconclusive, designed, …) werden übersprungen.
- Ein Claim-Eintrag gilt als vorhanden, wenn er nicht nur „- ..." oder leer ist.

Fehlerfall: exit(1) mit klarer Fehlermeldung (Experiment-Name + Fehlergrund).

Benötigt: python3 -m pip install pyyaml
"""

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: Missing dependency. Run: python3 -m pip install pyyaml")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
EXPERIMENTS_DIR = REPO_ROOT / "experiments"

# Marker-Strings
BUDGET_SECTION_PATTERN = re.compile(r"^##\s+Interpretation Budget", re.MULTILINE)
BUDGET_SECTION_EXTRACT_PATTERN = re.compile(
    r"^##\s+Interpretation Budget\s*\n(.*?)(?=^##\s+|\Z)",
    re.MULTILINE | re.DOTALL,
)
ALLOWED_CLAIMS_PATTERN = re.compile(
    r"###\s+Allowed Claims\s*\n(.*?)(?=^###\s+|^##\s+|\Z)",
    re.MULTILINE | re.DOTALL,
)
DISALLOWED_CLAIMS_PATTERN = re.compile(
    r"###\s+Disallowed Claims\s*\n(.*?)(?=^###\s+|^##\s+|\Z)",
    re.MULTILINE | re.DOTALL,
)

# Platzhalter-Werte, die als "leer" gelten
PLACEHOLDER_VALUES = frozenset({"- ...", "...", "-"})


def _extract_claims(block_text: str) -> list[str]:
    """Extrahiert nicht-leere, nicht-Platzhalter-Einträge aus einem Claims-Block."""
    claims = []
    for line in block_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- ") or stripped.startswith("* "):
            value = stripped[2:].strip()
            if value and value not in PLACEHOLDER_VALUES and value != "...":
                claims.append(value)
    return claims


def _extract_budget_section(text: str) -> str | None:
    """Extrahiert ausschließlich den Inhalt von ``## Interpretation Budget``."""
    match = BUDGET_SECTION_EXTRACT_PATTERN.search(text)
    if not match:
        return None
    return match.group(1)


def validate_experiment(exp_dir: Path) -> list[str]:
    """Validiert ein einzelnes Experiment. Gibt Liste von Fehlermeldungen zurück."""
    errs: list[str] = []
    exp_name = exp_dir.name

    # manifest.yml lesen
    manifest_path = exp_dir / "manifest.yml"
    if not manifest_path.exists():
        return []  # Kein Manifest → nicht validierbar, kein Fehler

    try:
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as e:
        return [f"{exp_name}: manifest.yml nicht parsebar: {e}"]

    status = manifest.get("experiment", {}).get("status", "")
    if status != "adopted":
        return []  # Nur adopted Experimente werden geprüft

    # result.md prüfen
    result_md = exp_dir / "results" / "result.md"
    if not result_md.exists():
        errs.append(
            f"{exp_name}: status=adopted, aber results/result.md fehlt."
        )
        return errs

    text = result_md.read_text(encoding="utf-8")

    # ## Interpretation Budget Section prüfen
    if not BUDGET_SECTION_PATTERN.search(text):
        errs.append(
            f"{exp_name}: Kein '## Interpretation Budget' Block in results/result.md gefunden."
            f" Pflicht bei status=adopted. Siehe docs/policies/interpretation-budget.md"
        )
        return errs

    budget_section = _extract_budget_section(text)
    if budget_section is None:
        errs.append(
            f"{exp_name}: '## Interpretation Budget' konnte nicht isoliert werden."
            f" Prüfe die Section-Struktur in results/result.md"
        )
        return errs

    # ### Allowed Claims prüfen
    allowed_match = ALLOWED_CLAIMS_PATTERN.search(budget_section)
    if not allowed_match:
        errs.append(f"{exp_name}: '### Allowed Claims' fehlt im Interpretation Budget Block.")
    else:
        claims = _extract_claims(allowed_match.group(1))
        if not claims:
            errs.append(
                f"{exp_name}: '### Allowed Claims' ist leer oder enthält nur Platzhalter."
                f" Mindestens 1 konkreter Eintrag erforderlich."
            )

    # ### Disallowed Claims prüfen
    disallowed_match = DISALLOWED_CLAIMS_PATTERN.search(budget_section)
    if not disallowed_match:
        errs.append(f"{exp_name}: '### Disallowed Claims' fehlt im Interpretation Budget Block.")
    else:
        claims = _extract_claims(disallowed_match.group(1))
        if not claims:
            errs.append(
                f"{exp_name}: '### Disallowed Claims' ist leer oder enthält nur Platzhalter."
                f" Mindestens 1 konkreter Eintrag erforderlich."
            )

    return errs


def main() -> None:
    if not EXPERIMENTS_DIR.exists():
        print(f"ERROR: experiments/ Verzeichnis nicht gefunden: {EXPERIMENTS_DIR}")
        sys.exit(1)

    # Importiere SKIP_DIR_NAMES aus _paths.py
    sys.path.insert(0, str(Path(__file__).parent))
    from _paths import SKIP_DIR_NAMES

    all_errors: list[str] = []
    checked = 0

    for entry in sorted(EXPERIMENTS_DIR.iterdir()):
        if not entry.is_dir():
            continue
        # _template, _archive und andere Skip-Verzeichnisse ignorieren
        if entry.name.startswith("_") or entry.name in SKIP_DIR_NAMES:
            continue

        errs = validate_experiment(entry)
        if errs:
            all_errors.extend(errs)
        else:
            # Nur zählen wenn manifest.yml vorhanden und status=adopted
            manifest_path = entry / "manifest.yml"
            if manifest_path.exists():
                try:
                    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
                    if manifest.get("experiment", {}).get("status") == "adopted":
                        checked += 1
                except yaml.YAMLError:
                    pass

    if all_errors:
        print("❌ Interpretation Budget Validation FAILED:\n")
        for err in all_errors:
            print(f"  • {err}")
        print(
            f"\n{len(all_errors)} Fehler gefunden."
            " Adopted Experimente ohne ausgefüllten Interpretation Budget Block"
            " dürfen nicht promotet werden."
            " Siehe docs/policies/interpretation-budget.md"
        )
        sys.exit(1)
    else:
        print(f"✅ Interpretation Budget: {checked} adopted Experiment(e) valide.")


if __name__ == "__main__":
    main()
