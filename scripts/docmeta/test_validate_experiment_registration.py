from __future__ import annotations

import importlib.util
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("registration_gate", ROOT / "scripts/docmeta/validate_experiment_registration.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
NOW = datetime(2026, 7, 10, tzinfo=timezone.utc)


def _valid(directory: Path) -> Path:
    directory.mkdir(parents=True)
    payload = json.loads((ROOT / "experiments/_template/registration.v1.json").read_text(encoding="utf-8"))
    payload["experiment_id"] = directory.name
    payload["consumer"] = {"organ": "grabowski", "use": "Use the measured result to review one operator workflow decision."}
    payload["decision_target"] = {"question": "Should the workflow practice be promoted?", "owner": "bureau"}
    payload["measurement"] = {
        "metric": "review_defect_rate",
        "method": "Compare equivalent task sets with and without the practice.",
        "success": "At least 15 percent lower.",
        "falsification": "No reduction or a higher rate."
    }
    payload["expires_at"] = "2026-10-10T00:00:00Z"
    payload["closure"]["review_at"] = "2026-09-10T00:00:00Z"
    payload["closure"]["archive_path"] = f"experiments/_archive/{directory.name}"
    path = directory / "registration.v1.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_valid_registration() -> None:
    with tempfile.TemporaryDirectory() as raw:
        path = _valid(Path(raw) / "2026-07-10_consumer-gate")
        payload = MODULE.validate_registration(path, now=NOW)
        assert payload["boundary"]["no_runtime_authority"] is True


def test_missing_consumer_fails() -> None:
    with tempfile.TemporaryDirectory() as raw:
        path = _valid(Path(raw) / "2026-07-10_missing-consumer")
        payload = json.loads(path.read_text())
        del payload["consumer"]
        path.write_text(json.dumps(payload))
        try:
            MODULE.validate_registration(path, now=NOW)
        except Exception:
            return
        raise AssertionError("missing consumer was accepted")


def test_archive_path_must_match_directory() -> None:
    with tempfile.TemporaryDirectory() as raw:
        path = _valid(Path(raw) / "2026-07-10_archive-boundary")
        payload = json.loads(path.read_text())
        payload["closure"]["archive_path"] = "experiments/_archive/other"
        path.write_text(json.dumps(payload))
        try:
            MODULE.validate_registration(path, now=NOW)
        except ValueError as exc:
            assert "archive_path" in str(exc)
            return
        raise AssertionError("wrong archive path was accepted")


def test_repository_historical_experiments_are_grandfathered() -> None:
    result = MODULE.validate_all(now=NOW)
    assert result["status"] == "valid"
    assert result["grandfathered"] >= 1
