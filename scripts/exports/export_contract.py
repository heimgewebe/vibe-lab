"""export_contract.py — Single source of truth für Export-Pfade und Namenslogik.

Importiert von generate_exports.py und validate_export_parity.py.
Änderungen an Pfaden oder Namenslogik nur hier vornehmen; Generator und Validator
nicht separat anpassen, da Änderungen hier auf beide wirken.
"""

from __future__ import annotations

from pathlib import Path

# Repo-Root relativ zu diesem Skript: scripts/exports/ → ../../
REPO_ROOT = Path(__file__).resolve().parent.parent.parent

SOURCE_DIR: Path = REPO_ROOT / "instruction-blocks"

EXPORT_TARGETS: dict[str, Path] = {
    "copilot": REPO_ROOT / "exports" / "copilot",
    "cursor": REPO_ROOT / "exports" / "cursor",
}


def expected_export_name(src: Path) -> str:
    """Gibt den erwarteten Ziel-Dateinamen für eine Quelldatei zurück.

    Aktuelles Mapping: flaches 1:1 (src.name → target/src.name).
    Beide, Generator und Validator, müssen diese Funktion nutzen —
    niemals die Namenlogik inline duplizieren.
    """
    return src.name
