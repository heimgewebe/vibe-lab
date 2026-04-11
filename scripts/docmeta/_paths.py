#!/usr/bin/env python3
"""_paths.py — Gemeinsame Pfad-Hilfsfunktionen für docmeta-Skripte.

Zentrale Logik für:
- should_skip(): Welche Verzeichnisse werden übersprungen?
- write_if_changed(): Datei nur schreiben, wenn sich der Inhalt geändert hat (Idempotenz).
- extract_frontmatter(): YAML-Frontmatter aus Markdown-Dateien lesen.

Hinweis: .vibe/ ist operative Wahrheit und wird NICHT übersprungen.
         .github/, .cursor/ dagegen schon.
"""

from pathlib import Path

try:
    import yaml as _yaml
except ImportError:
    import sys
    print("ERROR: Missing dependency. Run: pip install pyyaml")
    sys.exit(1)

# Verzeichnisse, die in allen Skripten konsistent übersprungen werden
SKIP_DIR_NAMES: frozenset[str] = frozenset({
    ".git",
    ".github",
    ".cursor",
    "node_modules",
    "__pycache__",
    "_archive",
})


def should_skip(path: Path, repo_root: Path, skip_generated: bool = True) -> bool:
    """Gibt True zurück, wenn der Pfad übersprungen werden soll.

    Überspringt: .git/, .github/, .cursor/, node_modules/, __pycache__/, _archive/, raw-vibes/
    Inkludiert:  .vibe/ (operative Wahrheit gemäß Truth Model)
    """
    parts = path.relative_to(repo_root).parts
    for p in parts:
        if p in SKIP_DIR_NAMES:
            return True
    if skip_generated and "_generated" in parts:
        return True
    if "raw-vibes" in parts:
        return True
    return False


def write_if_changed(output_path: Path, content: str) -> bool:
    """Schreibt content in output_path, nur wenn sich der Inhalt geändert hat.

    Gibt True zurück wenn geschrieben wurde, False wenn unverändert.
    Gewährleistet Idempotenz der Generatoren: zweimaliges make generate → kein git diff.
    """
    if output_path.exists() and output_path.read_text(encoding="utf-8") == content:
        return False
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    return True


def extract_frontmatter(path: Path) -> dict | None:
    """Liest YAML-Frontmatter aus einer Markdown-Datei.

    Gibt None zurück, wenn kein Frontmatter vorhanden oder nicht parsebar ist.
    """
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    try:
        return _yaml.safe_load(parts[1]) or {}
    except _yaml.YAMLError:
        return None
