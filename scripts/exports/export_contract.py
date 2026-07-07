"""export_contract.py — Single source of truth für Export-Pfade, Namenslogik und Exportfähigkeit.

Importiert von generate_exports.py und validate_export_parity.py.
Änderungen an Pfaden, Namenslogik oder Export-Gating nur hier vornehmen;
Generator und Validator nicht separat anpassen.
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

EXPORTABLE_STATUS = "adopted"


def expected_export_name(src: Path) -> str:
    """Gibt den erwarteten Ziel-Dateinamen für eine Quelldatei zurück.

    Aktuelles Mapping: flaches 1:1 (src.name → target/src.name).
    Beide, Generator und Validator, müssen diese Funktion nutzen —
    niemals die Namenlogik inline duplizieren.
    """
    return src.name


def read_source_status(src: Path) -> str | None:
    """Liest den Frontmatter-Status einer Instruction-Block-Quelldatei.

    Fehlt Frontmatter oder ``status``, ist die Datei nicht exportfähig.
    Das ist absichtlich fail-closed: Tool-Exports sind konsumierbare
    Anweisungsflächen und dürfen keine Drafts oder Kandidaten ausspielen.
    """
    text = src.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None

    parts = text.split("---", 2)
    if len(parts) < 3:
        return None

    for raw_line in parts[1].splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        if key.strip() == "status":
            return value.strip().strip('"').strip("'")
    return None


def is_exportable_source(src: Path) -> bool:
    """Nur adoptierte Instruction-Blocks werden in Tool-Exports projiziert."""
    return read_source_status(src) == EXPORTABLE_STATUS


def exportable_source_files(source_dir: Path = SOURCE_DIR) -> list[Path]:
    """Gibt sortierte, exportfähige Instruction-Block-Quelldateien zurück."""
    return [src for src in sorted(source_dir.glob("*.md")) if is_exportable_source(src)]
