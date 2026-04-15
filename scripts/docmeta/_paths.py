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
import importlib.util

_YAML_SPEC = importlib.util.find_spec("yaml")
if _YAML_SPEC is not None:
    import yaml as _yaml
else:
    _yaml = None

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
    yaml_block = parts[1]
    if _yaml is not None:
        try:
            return _yaml.safe_load(yaml_block) or {}
        except Exception:
            return None

    # Fallback ohne pyyaml: unterstützt nur flache "key: value"-Zeilen.
    # Reicht für Navigation/Diagnose-Generatoren und hält make generate lauffähig.
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
