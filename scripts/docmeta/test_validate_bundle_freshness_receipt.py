#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import tempfile

from validate_bundle_freshness_receipt import DEFAULT_MARKERS, validate


def test_valid_markers_pass() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "bundle.md"
        path.write_text("\n".join(DEFAULT_MARKERS), encoding="utf-8")
        assert validate(path, list(DEFAULT_MARKERS)) == []


def test_missing_marker_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "bundle.md"
        path.write_text("docs/policies/agent-reading-protocol.md\n", encoding="utf-8")
        assert validate(path, list(DEFAULT_MARKERS))


if __name__ == "__main__":
    test_valid_markers_pass()
    test_missing_marker_fails()
    print("bundle freshness receipt tests passed")
