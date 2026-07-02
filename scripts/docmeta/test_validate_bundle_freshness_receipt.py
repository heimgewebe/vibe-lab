#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import tempfile

from validate_bundle_freshness_receipt import DEFAULT_MARKERS, validate


def _file_section(path: str) -> str:
    return f'<!-- FILE_START path="{path}" content_sha256="dummy" -->\ncontent\n<!-- FILE_END path="{path}" -->'


def test_valid_file_sections_pass() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "bundle.md"
        path.write_text("\n".join(_file_section(marker) for marker in DEFAULT_MARKERS), encoding="utf-8")
        assert validate(path, list(DEFAULT_MARKERS)) == []


def test_plain_path_mentions_do_not_count_as_file_sections() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "bundle.md"
        path.write_text(
            _file_section("other-file.md")
            + "\nThis bundled file mentions docs/policies/agent-reading-protocol.md only as text.\n",
            encoding="utf-8",
        )
        assert validate(path, ["docs/policies/agent-reading-protocol.md"])


def test_missing_marker_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "bundle.md"
        path.write_text(_file_section("docs/policies/agent-reading-protocol.md"), encoding="utf-8")
        assert validate(path, list(DEFAULT_MARKERS))


if __name__ == "__main__":
    test_valid_file_sections_pass()
    test_plain_path_mentions_do_not_count_as_file_sections()
    test_missing_marker_fails()
    print("bundle freshness receipt tests passed")
