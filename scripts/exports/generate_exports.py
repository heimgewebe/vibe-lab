#!/usr/bin/env python3
"""generate_exports.py — Exportiert instruction-blocks/ nach exports/copilot/ und exports/cursor/.

Jeder Export enthält einen maschinenlesbaren Header, der Herkunft und Generator
dokumentiert. Die Erzeugung ist echt deterministisch: gleiche Quelldateien →
identische Ausgabe, unabhängig vom Ausführungszeitpunkt.

Kein Datum im Header: Ein kalendergebundener Zeitstempel würde bei gleicher Quelle
tägliche Diffs erzeugen und steht im Widerspruch zu deterministic: true im Contract.

Quelle:  instruction-blocks/*.md
Ziele:   exports/copilot/*.md, exports/cursor/*.md
Vertrag: .vibe/generated-artifacts.yml → artifacts[class=generated_projection]
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

# Repo-Root relativ zu diesem Skript: scripts/exports/ → ../../
REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Gemeinsame Hilfsfunktionen aus docmeta
sys.path.insert(0, str(REPO_ROOT / "scripts" / "docmeta"))
from _paths import write_if_changed  # noqa: E402

# Export-Contract: SOURCE_DIR, EXPORT_TARGETS und Namenslogik aus zentraler Quelle.
# Validator und Generator müssen dieselbe Konfiguration sehen.
from export_contract import EXPORT_TARGETS, SOURCE_DIR, expected_export_name  # noqa: E402

GENERATOR_ID = "scripts/exports/generate_exports.py"


def _parse_frontmatter(text: str) -> dict | None:
    """Liest YAML-Frontmatter aus bereits geladenem Markdown-Text.

    Vermeidet ein zweites Dateilesen in _build_export.
    Gibt None zurück, wenn kein Frontmatter vorhanden oder nicht parsebar ist.
    """
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    yaml_block = parts[1]
    try:
        import yaml as _yaml  # noqa: PLC0415 — optional dep, lazy import
        return _yaml.safe_load(yaml_block) or {}
    except Exception:
        pass
    # Fallback ohne pyyaml: unterstützt nur flache "key: value"-Zeilen
    out: dict[str, str] = {}
    for raw_line in yaml_block.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            out[key] = value
    return out or None


def _strip_frontmatter(text: str) -> str:
    """Entfernt YAML-Frontmatter (---...---) vom Markdown-Text."""
    if not text.startswith("---"):
        return text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return text
    return parts[2].lstrip("\n")


def compute_source_hash(content: str) -> str:
    """Berechnet einen deterministischen SHA-256-Hash des Quellinhalts.

    Der Hash ist quellgebunden und laufzeitunabhängig: gleicher Inhalt →
    gleicher Hash, unabhängig von Zeitpunkt oder Ausführungsumgebung.
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _build_header(source_path: str, target_system: str, source_hash: str) -> str:
    """Erzeugt einen einheitlichen, deterministischen Export-Header.

    Kein Datum: Ein kalendergebundener Zeitstempel würde tägliche Diffs ohne
    Quelländerung erzeugen und ist unvereinbar mit deterministic: true im Contract.
    Provenienz ist durch source + generator + source-hash vollständig gegeben.
    """
    return (
        f"<!-- GENERATED FILE — DO NOT EDIT MANUALLY -->\n"
        f"<!-- source: {source_path} -->\n"
        f"<!-- target-system: {target_system} -->\n"
        f"<!-- generator: {GENERATOR_ID} -->\n"
        f"<!-- source-hash: {source_hash} -->\n"
    )


def _build_export(
    source_file: Path,
    target_system: str,
) -> str:
    """Baut den vollständigen Export-Inhalt für eine Quelldatei."""
    text = source_file.read_text(encoding="utf-8")
    fm = _parse_frontmatter(text)
    body = _strip_frontmatter(text)
    title = fm.get("title", source_file.stem) if fm else source_file.stem
    rel_source = source_file.relative_to(REPO_ROOT)
    source_hash = compute_source_hash(text)

    header = _build_header(rel_source.as_posix(), target_system, source_hash)
    return f"{header}\n# {title}\n{body}"


def _rel_path(p: Path) -> str:
    try:
        return str(p.relative_to(REPO_ROOT))
    except ValueError:
        return str(p)


def detect_collisions(source_files: list[Path]) -> list[tuple[str, list[Path]]]:
    """Prüft, ob zwei Quelldateien denselben Ziel-Dateinamen erzeugen würden.

    Das aktuelle Mapping ist 1:1 (src.name → target/src.name), aber diese
    Funktion ist zukunftssicher: falls SOURCE_DIR je auf Subverzeichnisse
    ausgeweitet wird, würden gleichnamige Dateien in verschiedenen Unterordnern
    kollidieren. Kollisionen werden vor jeder Dateiänderung gemeldet.

    Returns:
        Liste von (ziel_name, [konfligierende_quelldateien]) für alle Kollisionen.
        Leer, wenn keine Kollision vorliegt.
    """
    seen: dict[str, list[Path]] = {}
    for src in source_files:
        target_name = expected_export_name(src)
        seen.setdefault(target_name, []).append(src)
    return [(name, srcs) for name, srcs in seen.items() if len(srcs) > 1]


def generate_exports() -> dict[str, int]:
    """Hauptlogik: liest instruction-blocks/, schreibt nach exports/.

    Bricht mit SystemExit(1) ab, wenn zwei Quelldateien denselben
    Ziel-Dateinamen erzeugen würden (Kollisions-Gate).

    Returns:
        dict mit target_system → Anzahl exportierter Dateien.
    """
    source_files = sorted(SOURCE_DIR.glob("*.md"))

    collisions = detect_collisions(source_files)
    if collisions:
        print("ERROR: Export-Kollision erkannt — Build abgebrochen.", file=sys.stderr)
        for target_name, conflicting in collisions:
            paths = ", ".join(_rel_path(p) for p in conflicting)
            print(f"  Kollision: '{target_name}' ← [{paths}]", file=sys.stderr)
        print(
            "Lösung: Quelldateien umbenennen, sodass jede einen eindeutigen Ziel-Dateinamen ergibt.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    stats: dict[str, int] = {}

    for target_system, target_dir in sorted(EXPORT_TARGETS.items()):
        target_dir.mkdir(parents=True, exist_ok=True)

        # Entferne .gitkeep falls vorhanden — Exporte ersetzen den Platzhalter.
        # Dieser Seiteneffekt ist durch den Export-Contract in
        # .vibe/generated-artifacts.yml gedeckt (triggered_by: generate-exports).
        gitkeep = target_dir / ".gitkeep"
        if gitkeep.exists():
            gitkeep.unlink()

        exported_names: set[str] = set()

        for src in source_files:
            content = _build_export(src, target_system)
            out_file = target_dir / expected_export_name(src)
            write_if_changed(out_file, content)
            exported_names.add(expected_export_name(src))

        # Entferne veraltete *.md-Exporte ohne entsprechende Quelldatei.
        # Scope auf *.md: non-md-Dateien (z.B. aus anderen Prozessen) werden
        # nicht berührt — konsistent mit der Orphan-Policy des Validators.
        for existing in target_dir.glob("*.md"):
            if existing.name not in exported_names:
                existing.unlink()

        stats[target_system] = len(source_files)

    return stats


def main() -> int:
    if not SOURCE_DIR.exists():
        print(f"ERROR: Source directory not found: {SOURCE_DIR}", file=sys.stderr)
        return 1

    stats = generate_exports()

    source_files = sorted(SOURCE_DIR.glob("*.md"))
    if not source_files:
        print(f"WARNING: No *.md files found in {SOURCE_DIR} — export directories cleared", file=sys.stderr)
        return 0

    for target, count in sorted(stats.items()):
        print(f"✅ Exported {count} instruction-blocks to exports/{target}/")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
