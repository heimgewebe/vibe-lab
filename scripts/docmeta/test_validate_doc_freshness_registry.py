#!/usr/bin/env python3
"""Regression tests for validate_doc_freshness_registry.py."""
from __future__ import annotations

from pathlib import Path
import tempfile

from validate_doc_freshness_registry import validate_registry


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _base_registry(entry_extra: str = "") -> str:
    return f"""kind: lenskit.doc_freshness_registry
version: "1.0"
authority: diagnostic_signal
risk_class: diagnostic
does_not_prove:
  - "green does not mean complete"
entries:
  - id: active-doc-claim
    doc: docs/policy.md
    locator: "frontmatter.status"
    claim: "The policy is active."
    status: done
    normative: true
    owner: heimgewebe
    last_verified: "2026-07-01"
    evidence:
      - kind: file
        target: docs/policy.md
      - kind: text
        target: "docs/policy.md::status: active"
        implies: done
{entry_extra}"""


def test_valid_registry_passes() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root / "docs" / "policy.md", "---\nstatus: active\n---\n# Policy\n")
        _write(root / "docs" / "doc-freshness-registry.yml", _base_registry())
        result = validate_registry(root)
        assert result.ok, result.errors
        assert result.entries_checked == 1


def test_missing_doc_is_error() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root / "docs" / "doc-freshness-registry.yml", _base_registry())
        result = validate_registry(root)
        assert not result.ok
        assert any("doc path missing" in error for error in result.errors)


def test_missing_required_text_is_error() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root / "docs" / "policy.md", "---\nstatus: draft\n---\n# Policy\n")
        _write(root / "docs" / "doc-freshness-registry.yml", _base_registry())
        result = validate_registry(root)
        assert not result.ok
        assert any("required text not found" in error for error in result.errors)


def test_path_escape_is_error() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root / "docs" / "policy.md", "---\nstatus: active\n---\n# Policy\n")
        _write(
            root / "docs" / "doc-freshness-registry.yml",
            _base_registry(
                """  - id: escape
    doc: ../outside.md
    claim: "Escape."
    status: done
    owner: heimgewebe
    last_verified: "2026-07-01"
    evidence:
      - kind: file
        target: ../outside.md
"""
            ),
        )
        result = validate_registry(root)
        assert not result.ok
        assert any("escapes repository root" in error for error in result.errors)


if __name__ == "__main__":
    test_valid_registry_passes()
    test_missing_doc_is_error()
    test_missing_required_text_is_error()
    test_path_escape_is_error()
    print("✅ doc-freshness registry validator tests passed")
