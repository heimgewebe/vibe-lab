#!/usr/bin/env python3
"""validate_export_parity.py — Prüft Export-Parität zwischen instruction-blocks/ und exports/.

Läuft als eigenständiger CI-Validator (blocking), unabhängig von der Testsuite.
Mutiert KEINE Dateien — liest ausschließlich den committed Repo-Zustand.

Prüfungen:
  1. Kollision   — zwei Quelldateien würden denselben Ziel-Dateinamen erzeugen
  2. Orphan      — Export existiert, aber die Quelldatei fehlt
  3. Missing     — Quelldatei existiert, aber der Export fehlt

Exit-Codes:
  0  — alle Prüfungen bestanden
  1  — mindestens ein Fehler gefunden
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SOURCE_DIR = REPO_ROOT / "instruction-blocks"
EXPORT_TARGETS: dict[str, Path] = {
    "copilot": REPO_ROOT / "exports" / "copilot",
    "cursor": REPO_ROOT / "exports" / "cursor",
}


def _source_names(source_dir: Path) -> dict[str, list[Path]]:
    """Gibt ein Mapping name → [quelldateien] zurück."""
    result: dict[str, list[Path]] = {}
    for f in sorted(source_dir.glob("*.md")):
        result.setdefault(f.name, []).append(f)
    return result


def _rel(p: Path) -> str:
    try:
        return str(p.relative_to(REPO_ROOT))
    except ValueError:
        return str(p)


def check_collisions(name_map: dict[str, list[Path]]) -> list[str]:
    errors: list[str] = []
    for name, srcs in name_map.items():
        if len(srcs) > 1:
            paths = ", ".join(_rel(p) for p in srcs)
            errors.append(f"Kollision: '{name}' ← [{paths}]")
    return errors


def check_orphans(name_map: dict[str, list[Path]], target_system: str, target_dir: Path) -> list[str]:
    if not target_dir.exists():
        return []
    source_names = set(name_map.keys())
    errors: list[str] = []
    for export_file in sorted(target_dir.iterdir()):
        if export_file.name not in source_names:
            errors.append(f"Orphan in exports/{target_system}/: '{export_file.name}' hat keine Quelle in instruction-blocks/")
    return errors


def check_missing(name_map: dict[str, list[Path]], target_system: str, target_dir: Path) -> list[str]:
    export_names = {f.name for f in target_dir.iterdir()} if target_dir.exists() else set()
    errors: list[str] = []
    for name in sorted(name_map.keys()):
        if name not in export_names:
            errors.append(f"Fehlender Export in exports/{target_system}/: '{name}' wurde nicht generiert")
    return errors


def validate(
    source_dir: Path = SOURCE_DIR,
    export_targets: dict[str, Path] | None = None,
) -> list[str]:
    """Führt alle Paritätsprüfungen durch. Gibt Fehlerliste zurück (leer = OK)."""
    if export_targets is None:
        export_targets = EXPORT_TARGETS

    name_map = _source_names(source_dir)
    all_errors: list[str] = []

    all_errors.extend(check_collisions(name_map))

    for target_system, target_dir in sorted(export_targets.items()):
        all_errors.extend(check_orphans(name_map, target_system, target_dir))
        all_errors.extend(check_missing(name_map, target_system, target_dir))

    return all_errors


def main() -> int:
    if not SOURCE_DIR.exists():
        print(f"ERROR: Source directory not found: {SOURCE_DIR}", file=sys.stderr)
        return 1

    errors = validate()

    if errors:
        print("❌ Export-Parität verletzt:", file=sys.stderr)
        for err in errors:
            print(f"  • {err}", file=sys.stderr)
        print(
            "\nLösung: 'make generate-exports' ausführen und Änderungen committen.",
            file=sys.stderr,
        )
        return 1

    print(f"✅ Export-Parität OK ({len(list(SOURCE_DIR.glob('*.md')))} Quelldatei(en), "
          f"{len(EXPORT_TARGETS)} Ziel(e))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
