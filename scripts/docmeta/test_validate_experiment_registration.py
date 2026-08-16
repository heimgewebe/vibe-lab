from __future__ import annotations

import importlib.util
import json
import tempfile
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("registration_gate", ROOT / "scripts/docmeta/validate_experiment_registration.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
NOW = datetime(2026, 7, 10, tzinfo=timezone.utc)
T005_NOW = datetime(2026, 8, 8, tzinfo=timezone.utc)
# Repository-tree validation clock pinned to the newest registration timestamp; triggered_by:
# conversation:user-request-2026-08-16-outcome-bound-successor-s0;
# github:heimgewebe/vibe-lab#339;
# codex-review:heimgewebe/vibe-lab#340-P1-P2.
REPOSITORY_NOW = datetime(2026, 8, 16, 16, 27, tzinfo=timezone.utc)
DELETE = object()
OUTCOME_OBSERVATION_SCHEMA_PATH = (
    ROOT
    / "experiments/2026-08-16_outcome-bound-operator-loop-p0/contracts/outcome-observation.v0.schema.json"
)
SUBSTANTIVE_OBSERVATION_STATES = (
    "supported",
    "partially_supported",
    "not_supported",
    "contradicted",
)


def _assert_invalid(path: Path, expected: str | None, *, now: datetime) -> None:
    try:
        MODULE.validate_registration(path, now=now)
    except Exception as exc:
        if expected is not None:
            assert expected in str(exc)
        return
    raise AssertionError(f"invalid registration was accepted: {path}")


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


def _valid_v2(directory: Path) -> Path:
    directory.mkdir(parents=True)
    template = (ROOT / "experiments/_template/registration.v2.json").read_text(encoding="utf-8")
    payload = json.loads(template.replace("replace-with", "example"))
    payload["experiment_id"] = directory.name
    payload["registered_at"] = "2026-08-08T00:00:00Z"
    payload["consumer"]["commitment"]["confirmed_at"] = "2026-08-08T00:00:00Z"
    payload["closure"]["archive_path"] = f"experiments/_archive/{directory.name}"
    path = directory / "registration.v2.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _invalid_v2(
    slug: str,
    expected: str,
    keys: tuple[str, ...],
    value: object = DELETE,
) -> None:
    with tempfile.TemporaryDirectory() as raw:
        path = _valid_v2(Path(raw) / f"2026-08-08_{slug}")
        payload = json.loads(path.read_text())
        parent = payload
        for key in keys[:-1]:
            parent = parent[key]
        if value is DELETE:
            parent.pop(keys[-1])
        else:
            parent[keys[-1]] = value
        path.write_text(json.dumps(payload))
        _assert_invalid(path, expected, now=T005_NOW)


def _outcome_observation_schema() -> dict[str, object]:
    return json.loads(OUTCOME_OBSERVATION_SCHEMA_PATH.read_text(encoding="utf-8"))


def _valid_outcome_observation() -> dict[str, object]:
    return {
        "schema_version": "outcome-observation.v0",
        "observation_id": "case-001.observation-001",
        "case_id": "case-001",
        "append_mode": "append_only",
        "observed_at": "2026-08-16T08:00:00Z",
        "spec_binding": {
            "spec_ref": "repo:experiments/case-001/spec.json",
            "case_id": "case-001",
            "spec_sha256": "1" * 64,
        },
        "technical_closeout_refs": ["github:heimgewebe/vibe-lab#329"],
        "assessment": {
            "state": "supported",
            "evidence_refs": ["github:heimgewebe/vibe-lab#329-review"],
            "qualitative_strength": "direct_primary_evidence",
            "confounders": [],
            "claims": {
                "established": ["The frozen desired change occurred in the registered window."],
                "not_established": ["General efficacy is not established."],
            },
            "reviewed_error_taxonomy": {
                "review_status": "not_reviewed",
                "classifications": [],
            },
            "decision": {
                "review_status": "reviewed",
                "decision_ref": "github:heimgewebe/vibe-lab#329-review",
                "disposition": "Close only the bounded observation.",
                "follow_up": "No automatic follow-up.",
            },
        },
        "digest_binding": {
            "algorithm": "sha256",
            "canonicalization": "rfc8785",
            "scope": "record_without_record_sha256",
            "record_sha256": "2" * 64,
            "previous_record_sha256": "3" * 64,
        },
    }


def _assert_outcome_observation_invalid(payload: dict[str, object]) -> None:
    validator = Draft202012Validator(_outcome_observation_schema())
    errors = list(validator.iter_errors(payload))
    assert errors, "invalid outcome observation was accepted"


def test_valid_registration() -> None:
    with tempfile.TemporaryDirectory() as raw:
        path = _valid(Path(raw) / "2026-07-09_repobrief-workbench-usefulness-eval")
        payload = MODULE.validate_registration(path, now=NOW)
        assert payload["boundary"]["no_runtime_authority"] is True


def test_missing_consumer_fails() -> None:
    with tempfile.TemporaryDirectory() as raw:
        path = _valid(Path(raw) / "2026-07-09_repobrief-workbench-usefulness-eval")
        payload = json.loads(path.read_text())
        del payload["consumer"]
        path.write_text(json.dumps(payload))
        _assert_invalid(path, None, now=NOW)


def test_archive_path_must_match_directory() -> None:
    with tempfile.TemporaryDirectory() as raw:
        path = _valid(Path(raw) / "2026-07-09_repobrief-workbench-usefulness-eval")
        payload = json.loads(path.read_text())
        payload["closure"]["archive_path"] = "experiments/_archive/other"
        path.write_text(json.dumps(payload))
        _assert_invalid(path, "archive_path", now=NOW)


def test_repository_historical_experiments_are_grandfathered() -> None:
    result = MODULE.validate_all(now=REPOSITORY_NOW)
    assert result["status"] == "valid"
    assert result["grandfathered"] >= 1


def test_v2_registration_binds_comparison_and_threshold() -> None:
    with tempfile.TemporaryDirectory() as raw:
        path = _valid_v2(Path(raw) / "2026-08-08_effect-evaluator")
        result = MODULE.validate_registration(path, now=T005_NOW)
        assert result["schema_version"] == "experiment.registration.v2"
        assert result["measurement"]["minimum_material_effect"] == 1
        assert result["closure"]["outcome_by_result"]["expired"] == "archive"


def test_outcome_observation_schema_is_valid_draft_2020_12() -> None:
    Draft202012Validator.check_schema(_outcome_observation_schema())


def test_substantive_outcome_state_requires_evidence() -> None:
    for state in SUBSTANTIVE_OBSERVATION_STATES:
        payload = _valid_outcome_observation()
        payload["assessment"]["state"] = state
        payload["assessment"]["evidence_refs"] = []
        _assert_outcome_observation_invalid(payload)


def test_substantive_outcome_state_rejects_insufficient_strength() -> None:
    for state in SUBSTANTIVE_OBSERVATION_STATES:
        payload = _valid_outcome_observation()
        payload["assessment"]["state"] = state
        payload["assessment"]["qualitative_strength"] = "insufficient"
        _assert_outcome_observation_invalid(payload)


def test_substantive_outcome_state_requires_established_claim() -> None:
    for state in SUBSTANTIVE_OBSERVATION_STATES:
        payload = _valid_outcome_observation()
        payload["assessment"]["state"] = state
        payload["assessment"]["claims"]["established"] = []
        _assert_outcome_observation_invalid(payload)


def test_compliant_substantive_outcome_states_pass() -> None:
    validator = Draft202012Validator(_outcome_observation_schema())
    for state in SUBSTANTIVE_OBSERVATION_STATES:
        payload = _valid_outcome_observation()
        payload["assessment"]["state"] = state
        validator.validate(payload)


def test_pending_outcome_state_rejects_established_claim() -> None:
    payload = _valid_outcome_observation()
    payload["assessment"]["state"] = "pending"
    payload["assessment"]["evidence_refs"] = []
    payload["assessment"]["qualitative_strength"] = "insufficient"
    _assert_outcome_observation_invalid(payload)


def test_insufficient_evidence_with_insufficient_strength_passes() -> None:
    payload = _valid_outcome_observation()
    payload["assessment"]["state"] = "insufficient_evidence"
    payload["assessment"]["qualitative_strength"] = "insufficient"
    payload["assessment"]["claims"]["established"] = [
        "The bounded evidence limitation was recorded."
    ]
    Draft202012Validator(_outcome_observation_schema()).validate(payload)


def test_outcome_observation_digest_scope_binds_predecessor_and_metadata() -> None:
    schema = _outcome_observation_schema()
    digest_binding = schema["properties"]["digest_binding"]
    assert set(digest_binding["required"]) == {
        "algorithm",
        "canonicalization",
        "scope",
        "record_sha256",
        "previous_record_sha256",
    }
    scope = digest_binding["properties"]["scope"]
    assert scope["const"] == "record_without_record_sha256"
    assert "/digest_binding/record_sha256" in scope["description"]
    for protected_property in (
        "algorithm",
        "canonicalization",
        "scope",
        "previous_record_sha256",
    ):
        assert f"digest_binding.{protected_property}" in scope["description"]

    validator = Draft202012Validator(schema)
    validator.validate(_valid_outcome_observation())
    legacy_scope = deepcopy(_valid_outcome_observation())
    legacy_scope["digest_binding"]["scope"] = "record_without_digest_binding"
    _assert_outcome_observation_invalid(legacy_scope)


def test_v2_scorecard_component_ids_must_be_unique() -> None:
    with tempfile.TemporaryDirectory() as raw:
        path = _valid_v2(Path(raw) / "2026-08-08_scorecard-ids")
        payload = json.loads(path.read_text())
        payload["measurement"]["scorecard"] = {
            "schema_version": "additive-binary-scorecard.v1",
            "components": [
                {"id": "aligned", "weight": 1, "criterion": "Decision aligns with adjudication."},
                {"id": "aligned", "weight": 2, "criterion": "Decision preserves uncertainty."},
            ],
        }
        path.write_text(json.dumps(payload), encoding="utf-8")
        _assert_invalid(path, "scorecard component ids must be unique", now=T005_NOW)


def test_t005_gate_rejects_bypasses() -> None:
    cases = (
        ("missing-registered-at", "registered_at", ("registered_at",), DELETE),
        ("future-registered-at", "registered_at cannot be in the future", ("registered_at",), "2026-08-09T00:00:00Z"),
        ("consumer-confirmed-after-registration", "consumer commitment must be confirmed by registered_at", ("consumer", "commitment", "confirmed_at"), "2026-08-08T01:00:00Z"),
        ("self-consumer", "external consumer", ("consumer", "organ"), "Vibe-Lab internal team"),
        ("vague-consumer", "external consumer", ("consumer", "organ"), "external team"),
        ("consumer-relationship", "consumer.relationship", ("consumer", "relationship"), DELETE),
        ("consumer-commitment", "consumer.commitment", ("consumer", "commitment"), DELETE),
        ("stale-consumer", "consumer commitment", ("consumer", "commitment", "valid_until"), "2026-08-07T00:00:00Z"),
        ("short-consumer-commitment", "through expires_at", ("consumer", "commitment", "valid_until"), "2026-09-30T00:00:00Z"),
        ("decision-ref", "decision_target.decision_ref", ("decision_target", "decision_ref"), DELETE),
        ("self-decision-owner", "decision owner", ("decision_target", "owner"), "this repository"),
        ("metric-criteria", "measurement.outcome_criteria", ("measurement", "outcome_criteria"), DELETE),
        ("metric-overlap", "must not overlap", ("measurement", "outcome_criteria", "harm_or_falsification_threshold"), 0),
        ("metric-finite", "must be finite", ("measurement", "outcome_criteria", "success_threshold"), float("inf")),
        ("closure-map", "closure.outcome_by_result", ("closure", "outcome_by_result"), DELETE),
        ("stale-review", "review_at must be after registered_at", ("review_at",), "2026-08-07T00:00:00Z"),
        ("surface-budget", "surface_budget", ("surface_budget",), DELETE),
        ("surface-cost", "reviewed surface-budget exception", ("surface_budget", "durable_additions"), ["add:scripts/new_specialist_validator.py"]),
        ("duplicate-offset", "surface refs must be unique", ("surface_budget", "durable_offsets"), ["remove:scripts/legacy.py", "retire:scripts/legacy.py"]),
        ("policy-boundary", "no_auto_policy", ("boundary", "no_auto_policy"), DELETE),
        ("routing-boundary", "no_auto_routing", ("boundary", "no_auto_routing"), DELETE),
        ("queue-boundary", "no_queue_authority", ("boundary", "no_queue_authority"), DELETE),
        ("runtime-boundary", "no_runtime_authority", ("boundary", "no_runtime_authority"), DELETE),
        ("merge-boundary", "boundary.no_merge_authority", ("boundary", "no_merge_authority"), DELETE),
    )
    for case in cases:
        _invalid_v2(*case)


def test_assignment_prior_digest_must_match_registration_without_assignment() -> None:
    with tempfile.TemporaryDirectory() as raw:
        directory = Path(raw) / "2026-07-13_chronik-history-brief-effect"
        directory.mkdir(parents=True)
        payload = json.loads((ROOT / "experiments/2026-07-13_chronik-history-brief-effect/registration.v2.json").read_text())
        payload["assignment"]["prior_registration_sha256"] = "0" * 64
        path = directory / "registration.v2.json"
        path.write_text(json.dumps(payload))
        _assert_invalid(path, "prior_registration_sha256", now=datetime(2026, 8, 11, 7, 0, tzinfo=timezone.utc))


def test_new_work_cannot_use_v1_registration_directly() -> None:
    with tempfile.TemporaryDirectory() as raw:
        path = _valid(Path(raw) / "2026-08-08_v1-bypass")
        _assert_invalid(path, "new experiment requires registration.v2.json", now=T005_NOW)


def test_new_work_cannot_hide_v2_payload_under_v1_filename() -> None:
    with tempfile.TemporaryDirectory() as raw:
        path = _valid_v2(Path(raw) / "2026-08-08_v2-filename-bypass")
        disguised = path.with_name("registration.v1.json")
        path.rename(disguised)
        _assert_invalid(disguised, "new experiment requires registration.v2.json", now=T005_NOW)


def test_v2_registration_remains_valid_after_review_until_expiry() -> None:
    with tempfile.TemporaryDirectory() as raw:
        path = _valid_v2(Path(raw) / "2026-08-08_post-review-validity")
        MODULE.validate_registration(path, now=datetime(2099, 3, 15, tzinfo=timezone.utc))


def test_v2_reviewed_surface_exception_passes() -> None:
    with tempfile.TemporaryDirectory() as raw:
        path = _valid_v2(Path(raw) / "2026-08-08_surface-exception")
        payload = json.loads(path.read_text())
        payload["surface_budget"]["durable_additions"] = [
            "add:scripts/new_specialist_validator.py"
        ]
        payload["surface_budget"]["reviewed_exception"] = {
            "reviewed_by": "Bureau",
            "review_ref": "bureau:OPERATOR-ECOSYSTEM-REDUNDANCY-V1-T005",
            "reviewed_at": "2026-08-08T00:00:00Z",
            "rationale": "The bounded safety gap justifies one net durable surface unit.",
        }
        path.write_text(json.dumps(payload))
        MODULE.validate_registration(path, now=T005_NOW)


def test_backdated_new_directory_cannot_bypass_registration() -> None:
    with tempfile.TemporaryDirectory() as raw:
        experiments = Path(raw) / "experiments"
        (experiments / "2026-07-09_backdated-new-work").mkdir(parents=True)
        original = MODULE.EXPERIMENTS
        MODULE.EXPERIMENTS = experiments
        try:
            try:
                MODULE.validate_all(now=T005_NOW)
            except ValueError as exc:
                assert "new experiment requires registration.v2.json" in str(exc)
                return
            raise AssertionError("backdated new experiment bypassed registration")
        finally:
            MODULE.EXPERIMENTS = original


def test_repository_v2_count_matches_current_experiment_tree() -> None:
    result = MODULE.validate_all(now=REPOSITORY_NOW)
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
