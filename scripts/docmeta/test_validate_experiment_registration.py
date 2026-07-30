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


def test_v2_registration_binds_comparison_and_threshold() -> None:
    with tempfile.TemporaryDirectory() as raw:
        directory = Path(raw) / "2026-07-12_effect-evaluator"
        directory.mkdir(parents=True)
        payload = json.loads((ROOT / "experiments/_template/registration.v2.json").read_text(encoding="utf-8"))
        payload["experiment_id"] = directory.name
        payload["consumer"].update(
            {
                "organ": "bureau",
                "use": "Use the result to decide whether the evaluator remains active.",
                "evidence_ref": "bureau-task:TEST-T001",
            }
        )
        payload["decision_target"] = {"question": "Should the evaluator remain active after real pilots?", "owner": "bureau"}
        payload["intervention"] = {"name": "effect_report", "description": "Provide one deterministic effect report to the reviewer."}
        payload["measurement"]["primary_metric"] = "decision_value_score"
        payload["measurement"]["method"] = "Compare paired independent review decisions over frozen evidence."
        payload["measurement"]["success"] = "Material improvement."
        payload["measurement"]["falsification"] = "No improvement or harm."
        payload["review_at"] = "2026-09-01T00:00:00Z"
        payload["expires_at"] = "2026-10-01T00:00:00Z"
        payload["closure"]["archive_path"] = f"experiments/_archive/{directory.name}"
        path = directory / "registration.v2.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        result = MODULE.validate_registration(path, now=datetime(2026, 7, 12, tzinfo=timezone.utc))
        assert result["schema_version"] == "experiment.registration.v2"
        assert result["measurement"]["minimum_material_effect"] == 1


def test_v2_scorecard_component_ids_must_be_unique() -> None:
    with tempfile.TemporaryDirectory() as raw:
        directory = Path(raw) / "2026-07-12_scorecard-ids"
        directory.mkdir(parents=True)
        payload = json.loads((ROOT / "experiments/_template/registration.v2.json").read_text(encoding="utf-8"))
        payload["experiment_id"] = directory.name
        payload["consumer"].update(
            {
                "organ": "bureau",
                "use": "Use the result to decide whether the evaluator remains active.",
                "evidence_ref": "bureau-task:TEST-T001",
            }
        )
        payload["decision_target"] = {"question": "Should the evaluator remain active after real pilots?", "owner": "bureau"}
        payload["intervention"] = {"name": "effect_report", "description": "Provide one deterministic effect report to the reviewer."}
        payload["measurement"]["primary_metric"] = "decision_value_score"
        payload["measurement"]["method"] = "Compare paired independent review decisions over frozen evidence."
        payload["measurement"]["success"] = "Material improvement."
        payload["measurement"]["falsification"] = "No improvement or harm."
        payload["measurement"]["scorecard"] = {
            "schema_version": "additive-binary-scorecard.v1",
            "components": [
                {"id": "aligned", "weight": 1, "criterion": "Decision aligns with adjudication."},
                {"id": "aligned", "weight": 2, "criterion": "Decision preserves uncertainty."},
            ],
        }
        payload["review_at"] = "2026-09-01T00:00:00Z"
        payload["expires_at"] = "2026-10-01T00:00:00Z"
        payload["closure"]["archive_path"] = f"experiments/_archive/{directory.name}"
        path = directory / "registration.v2.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        try:
            MODULE.validate_registration(path, now=datetime(2026, 7, 12, tzinfo=timezone.utc))
        except ValueError as exc:
            assert "scorecard component ids must be unique" in str(exc)
            return
        raise AssertionError("duplicate scorecard component ids were accepted")


def _valid_v2(directory: Path) -> Path:
    directory.mkdir(parents=True)
    payload = json.loads(
        (ROOT / "experiments/_template/registration.v2.json").read_text(encoding="utf-8")
    )
    payload["experiment_id"] = directory.name
    payload["consumer"].update(
        {
            "organ": "bureau",
            "use": "Use the result to decide whether the evaluator remains active.",
            "evidence_ref": "bureau-task:TEST-T001",
        }
    )
    payload["decision_target"] = {
        "question": "Should the evaluator remain active after real pilots?",
        "owner": "bureau",
    }
    payload["intervention"] = {
        "name": "effect_report",
        "description": "Provide one deterministic effect report to the reviewer.",
    }
    payload["measurement"]["primary_metric"] = "decision_value_score"
    payload["measurement"]["method"] = (
        "Compare paired independent review decisions over frozen evidence."
    )
    payload["measurement"]["success"] = "Material improvement."
    payload["measurement"]["falsification"] = "No improvement or harm."
    payload["review_at"] = "2026-09-01T00:00:00Z"
    payload["expires_at"] = "2026-10-01T00:00:00Z"
    payload["closure"]["archive_path"] = f"experiments/_archive/{directory.name}"
    path = directory / "registration.v2.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_v2_consumer_must_be_external() -> None:
    with tempfile.TemporaryDirectory() as raw:
        path = _valid_v2(Path(raw) / "2026-07-12_internal-consumer")
        payload = json.loads(path.read_text())
        payload["consumer"]["organ"] = "Vibe-Lab"
        path.write_text(json.dumps(payload))
        try:
            MODULE.validate_registration(
                path, now=datetime(2026, 7, 12, tzinfo=timezone.utc)
            )
        except ValueError as exc:
            assert "external to Vibe-Lab" in str(exc)
            return
        raise AssertionError("internal Vibe-Lab consumer was accepted")


def test_v2_positive_surface_requires_reviewed_exception() -> None:
    with tempfile.TemporaryDirectory() as raw:
        path = _valid_v2(Path(raw) / "2026-07-12_surface-budget")
        payload = json.loads(path.read_text())
        payload["surface_budget"]["durable_units_added"] = ["new runtime adapter"]
        path.write_text(json.dumps(payload))
        try:
            MODULE.validate_registration(
                path, now=datetime(2026, 7, 12, tzinfo=timezone.utc)
            )
        except ValueError as exc:
            assert "non_positive surface budget" in str(exc)
            return
        raise AssertionError("positive durable surface without exception was accepted")


def test_v2_reviewed_surface_exception_is_bound_and_past() -> None:
    with tempfile.TemporaryDirectory() as raw:
        path = _valid_v2(Path(raw) / "2026-07-12_surface-exception")
        payload = json.loads(path.read_text())
        payload["surface_budget"] = {
            "durable_units_added": ["new runtime adapter"],
            "durable_units_removed_or_replaced": [],
            "balance": "reviewed_exception",
            "exception": {
                "status": "reviewed",
                "reviewer": "operator",
                "reviewed_at": "2026-07-11T00:00:00Z",
                "rationale": (
                    "The named consumer needs one bounded adapter before a replacement exists."
                ),
                "evidence_ref": "decision:surface-budget-test",
            },
        }
        path.write_text(json.dumps(payload))
        result = MODULE.validate_registration(
            path, now=datetime(2026, 7, 12, tzinfo=timezone.utc)
        )
        assert result["surface_budget"]["balance"] == "reviewed_exception"


def test_repository_v2_count_matches_current_experiment_tree() -> None:
    result = MODULE.validate_all(now=datetime(2026, 7, 12, tzinfo=timezone.utc))
    expected_v2 = sum(
        (directory / "registration.v2.json").is_file()
        for directory in (ROOT / "experiments").iterdir()
        if directory.is_dir() and not directory.name.startswith("_")
    )
    assert result["checked_v2"] == expected_v2

def _run_all_tests() -> None:
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
    print(f"registration tests passed: {len(tests)}")


if __name__ == "__main__":
    _run_all_tests()
