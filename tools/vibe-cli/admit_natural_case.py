#!/usr/bin/env python3
"""Seal one registration-bound natural case before planning.

Legacy registrations admit caller-supplied conditions. When registration.v2
contains the frozen stratified assignment contract, this writer allocates the
condition under the same create-only cohort lock before planning.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import tempfile
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker, ValidationError


ROOT = Path(__file__).resolve().parents[2]
REGISTRATION_SCHEMA = ROOT / "schemas/experiment.registration.v2.schema.json"
ADMISSION_SCHEMA = ROOT / "schemas/natural-case-admission.v1.schema.json"
DEFAULT_EXPERIMENT = ROOT / "experiments/2026-07-13_chronik-history-brief-effect"
DEFAULT_REGISTRATION = DEFAULT_EXPERIMENT / "registration.v2.json"
DEFAULT_ADMISSIONS = DEFAULT_EXPERIMENT / "artifacts/admissions"
SUPPORTED_EXPERIMENT_ID = DEFAULT_EXPERIMENT.name
CASE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
MANUAL_NON_CLAIMS = [
    "automatic_assignment",
    "assignment_fairness",
    "external_eligibility_truth",
    "case_execution",
    "independent_review_completion",
    "condition_effect",
    "routing_queue_or_runtime_authority",
]
AUTO_NON_CLAIMS = [
    "external_eligibility_truth",
    "case_execution",
    "independent_review_completion",
    "condition_effect",
    "randomization_or_causal_identification",
    "routing_queue_or_runtime_authority",
]


class AdmissionError(RuntimeError):
    pass


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode(
        "utf-8"
    )


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def load_object(path: Path, label: str) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise AdmissionError(f"{label} must be a regular non-symlink file")
    if path.stat().st_size > 1_000_000:
        raise AdmissionError(f"{label} exceeds 1 MiB")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AdmissionError(f"{label} must contain UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise AdmissionError(f"{label} must contain an object")
    return value


def load_schema(path: Path) -> dict[str, Any]:
    return load_object(path, f"schema {path.name}")


def validator(schema: dict[str, Any]) -> Draft202012Validator:
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def validate(value: dict[str, Any], schema: dict[str, Any], label: str) -> None:
    try:
        validator(schema).validate(value)
    except ValidationError as exc:
        location = ".".join(str(item) for item in exc.absolute_path)
        suffix = f" at {location}" if location else ""
        raise AdmissionError(f"{label} is invalid{suffix}: {exc.message}") from exc


def utc_timestamp(value: str, label: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise AdmissionError(f"{label} must be an RFC3339 timestamp") from exc
    if parsed.tzinfo is None:
        raise AdmissionError(f"{label} must include a timezone")
    normalized = parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if value != normalized:
        raise AdmissionError(f"{label} must be canonical UTC-Z")
    return parsed.astimezone(timezone.utc)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def format_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def experiment_start(experiment_id: str) -> datetime:
    try:
        return datetime.fromisoformat(experiment_id[:10]).replace(tzinfo=timezone.utc)
    except ValueError as exc:
        raise AdmissionError("experiment_id has no valid date prefix") from exc


def validate_registration(registration: dict[str, Any], registration_path: Path) -> None:
    validate(registration, load_schema(REGISTRATION_SCHEMA), "registration")
    if registration.get("schema_version") != "experiment.registration.v2":
        raise AdmissionError("natural-case admission requires registration.v2")
    if registration.get("experiment_id") != registration_path.parent.name:
        raise AdmissionError("registration experiment_id must match its directory")
    if registration["experiment_id"] != SUPPORTED_EXPERIMENT_ID:
        raise AdmissionError("this admission writer is limited to the registered Chronik experiment")
    if registration["boundary"] != {
        "experiment_only": True,
        "no_auto_policy": True,
        "no_auto_routing": True,
        "no_queue_authority": True,
        "no_runtime_authority": True,
    }:
        raise AdmissionError("registration authority boundary is not closed")
    assignment = registration.get("assignment")
    if assignment is not None:
        prior_registration = dict(registration)
        prior_registration.pop("assignment", None)
        if assignment["prior_registration_sha256"] != sha256_json(prior_registration):
            raise AdmissionError("assignment prior registration digest is invalid")


def request_schema(admission_schema: dict[str, Any]) -> dict[str, Any]:
    schema = admission_schema.get("$defs", {}).get("request")
    if not isinstance(schema, dict):
        raise AdmissionError("admission schema is missing $defs.request")
    return {
        "$schema": admission_schema["$schema"],
        **schema,
        "$defs": admission_schema["$defs"],
    }


def validate_request_semantics(
    request: dict[str, Any], registration: dict[str, Any], admitted: datetime
) -> None:
    case_id = request["case_id"]
    if CASE_ID_RE.fullmatch(case_id) is None:
        raise AdmissionError("case_id is not path-safe")

    eligibility = request["eligibility"]
    retrospective_signals = {
        "planning_started": eligibility["planning_started"],
        "execution_started": eligibility["execution_started"],
        "outcome_known": eligibility["outcome_known"],
        "prior_observation": eligibility["prior_observation"],
    }
    if any(retrospective_signals.values()):
        names = sorted(name for name, enabled in retrospective_signals.items() if enabled)
        raise AdmissionError("retrospective or backfill admission refused: " + ", ".join(names))
    if eligibility["natural_case"] is not True or eligibility["within_registered_scope"] is not True:
        raise AdmissionError("case is not attested as a natural in-scope case")
    if request["assignment"]["recorded_before_planning"] is not True:
        raise AdmissionError("assignment must be recorded before planning")

    opened = utc_timestamp(request["case_opened_at"], "case_opened_at")
    evidence_captured = utc_timestamp(
        request["eligibility_evidence"]["captured_at"], "eligibility_evidence.captured_at"
    )
    start = experiment_start(registration["experiment_id"])
    expiry = utc_timestamp(registration["expires_at"], "registration.expires_at")
    if admitted < start:
        raise AdmissionError("admission predates the registered experiment")
    if admitted >= expiry:
        raise AdmissionError("experiment is expired; admission refused")
    if opened < start:
        raise AdmissionError("case predates the registered experiment; backfill refused")
    if opened > admitted:
        raise AdmissionError("case_opened_at is after admission")
    if evidence_captured < opened or evidence_captured > admitted:
        raise AdmissionError("eligibility evidence must be captured between case opening and admission")

    assignment_contract = registration.get("assignment")
    assignment = request["assignment"]
    if assignment_contract is None:
        conditions = {
            registration["control_condition"]["id"],
            registration["treatment_condition"]["id"],
        }
        if assignment.get("condition") not in conditions:
            raise AdmissionError("assignment condition is not registered")
    else:
        if assignment != {"mode": "registered_automatic", "recorded_before_planning": True}:
            raise AdmissionError("registered automatic assignment is required by the current registration")
        assignment_registered = utc_timestamp(assignment_contract["registered_at"], "assignment.registered_at")
        if admitted < assignment_registered:
            raise AdmissionError("admission predates the prospective assignment revision")
        if opened < assignment_registered:
            raise AdmissionError("case predates the prospective assignment revision")


def _assignment_stratum(request: dict[str, Any]) -> dict[str, str]:
    comparability = request["comparability"]
    return {
        "task_class": comparability["task_class"],
        "risk_band": comparability["risk_band"],
        "repository_familiarity_band": comparability["repository_familiarity_band"],
    }


def _automatic_assignment_for_index(registration: dict[str, Any], stratum: dict[str, str], sequence_index: int) -> dict[str, Any]:
    contract = registration["assignment"]
    block_index = sequence_index // 2
    block_position = sequence_index % 2
    block_order_sha = sha256_json({
        "schema_version": contract["schema_version"],
        "seed_sha256": contract["seed_sha256"],
        "stratum": stratum,
        "block_index": block_index,
    })
    arms = [registration["control_condition"]["id"], registration["treatment_condition"]["id"]]
    if int(block_order_sha[-1], 16) % 2:
        arms.reverse()
    return {
        "condition": arms[block_position],
        "mode": "stratified_permuted_blocks.v1",
        "automatic": True,
        "fairness_claim": "registration_bound_stratum_balance_only",
        "registration_rule_status": "frozen_prospective_assignment",
        "sequence_index": sequence_index,
        "block_index": block_index,
        "block_position": block_position,
        "stratum": stratum,
        "stratum_sha256": sha256_json(stratum),
        "seed_sha256": contract["seed_sha256"],
        "block_order_sha256": block_order_sha,
        "balance_invariant": "arm_count_difference_at_most_one_per_partial_or_complete_two_case_block",
    }


def _automatic_assignment(request: dict[str, Any], registration: dict[str, Any], records: list[tuple[Path, dict[str, Any]]]) -> dict[str, Any]:
    contract = registration["assignment"]
    if contract["schema_version"] != "stratified_permuted_blocks.v1" or contract["block_size"] != 2:
        raise AdmissionError("assignment registration contract is unsupported")
    stratum = _assignment_stratum(request)
    stratum_sha = sha256_json(stratum)
    matching = []
    for _path, existing in records:
        evidence = existing["assignment_evidence"]
        if evidence.get("automatic") is not True:
            continue
        if existing["registration_sha256"] != sha256_json(registration):
            continue
        if evidence.get("seed_sha256") != contract["seed_sha256"]:
            raise AdmissionError("existing automatic admission seed binding drifted")
        if evidence.get("stratum_sha256") == stratum_sha:
            matching.append(evidence)
    matching.sort(key=lambda item: item["sequence_index"])
    for expected_index, evidence in enumerate(matching):
        if evidence["sequence_index"] != expected_index:
            raise AdmissionError("automatic admission sequence is not contiguous")
        expected = _automatic_assignment_for_index(registration, stratum, expected_index)
        if any(evidence.get(key) != expected.get(key) for key in expected):
            raise AdmissionError("existing automatic admission does not match the frozen assignment contract")
    return _automatic_assignment_for_index(registration, stratum, len(matching))


def build_record(request: dict[str, Any], registration: dict[str, Any], admitted: datetime, assignment_evidence: dict[str, Any]) -> dict[str, Any]:
    registration_digest = sha256_json(registration)
    request_digest = sha256_json(request)
    comparability_digest = sha256_json(request["comparability"])
    blinded_case_id = sha256_json(
        {
            "schema_version": 1,
            "experiment_id": registration["experiment_id"],
            "case_id": request["case_id"],
            "eligibility_evidence_sha256": request["eligibility_evidence"]["sha256"],
            "comparability_sha256": comparability_digest,
        }
    )
    admission_id = sha256_json(
        {
            "schema_version": 1,
            "experiment_id": registration["experiment_id"],
            "registration_sha256": registration_digest,
            "request_sha256": request_digest,
            "assignment_evidence": assignment_evidence,
        }
    )
    return {
        "schema_version": "natural-case-admission.v1",
        "experiment_id": registration["experiment_id"],
        "registration_sha256": registration_digest,
        "admission_id": admission_id,
        "admitted_at": format_utc(admitted),
        "request_sha256": request_digest,
        "frozen_request": request,
        "comparability_sha256": comparability_digest,
        "assignment_evidence": assignment_evidence,
        "review_preparation": {
            "status": "pending_independent_review",
            "blinded_case_id": blinded_case_id,
            "blinding_required": True,
            "condition_disclosure": "after_score_seal",
            "independent_observation_required": registration["evidence_sources"][
                "independent_observation_required"
            ],
            "measurement_sha256": sha256_json(registration["measurement"]),
            "allowed_evidence_sources": registration["evidence_sources"]["allowed"],
            "minimum_control": registration["comparison"]["minimum_control"],
            "minimum_treatment": registration["comparison"]["minimum_treatment"],
            "review_at": registration["review_at"],
        },
        "boundary": dict(registration["boundary"]),
        "traceability": {
            "triggered_by": request["triggered_by"],
            "policy": ("registration.v2.json assignment + method.md" if assignment_evidence.get("automatic") is True else "registration.v2.json + method.md"),
            "action": "prospective_natural_case_admission",
            "outcome": ("registered_automatic_assignment_sealed" if assignment_evidence.get("automatic") is True else "explicit_condition_assignment_sealed"),
        },
        "non_claims": list(AUTO_NON_CLAIMS if assignment_evidence.get("automatic") is True else MANUAL_NON_CLAIMS),
    }


def _secure_lock_root() -> Path:
    runtime = os.environ.get("XDG_RUNTIME_DIR")
    candidates = []
    if runtime:
        candidates.append(Path(runtime) / f"vibe-lab-admission-locks-{os.getuid()}")
    candidates.append(Path(tempfile.gettempdir()) / f"vibe-lab-admission-locks-{os.getuid()}")
    failures: list[str] = []
    for candidate in candidates:
        try:
            candidate.mkdir(mode=0o700, parents=True, exist_ok=True)
            info = candidate.lstat()
        except OSError as exc:
            failures.append(f"{candidate}: {exc}")
            continue
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            failures.append(f"{candidate}: not a real directory")
            continue
        if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) & 0o077:
            failures.append(f"{candidate}: unsafe ownership or permissions")
            continue
        return candidate
    raise AdmissionError("cannot prepare a private admission lock directory: " + "; ".join(failures))


def _lock_fd(admissions_root: Path) -> int:
    lock_name = hashlib.sha256(os.fsencode(str(admissions_root.resolve(strict=False)))).hexdigest()
    flags = os.O_RDWR | os.O_CREAT
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(_secure_lock_root() / f"{lock_name}.lock", flags, 0o600)
    info = os.fstat(fd)
    if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid():
        os.close(fd)
        raise AdmissionError("admission lock is not a safe regular file")
    return fd


def _fsync_directory(path: Path) -> None:
    flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    fd = os.open(path, flags)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def publish_create_only(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(mode=0o700, parents=False, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    published = False
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(canonical_json_bytes(value))
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, 0o444)
        try:
            os.link(temporary, path, follow_symlinks=False)
        except FileExistsError as exc:
            raise AdmissionError("admission already exists") from exc
        published = True
        _fsync_directory(path.parent)
    finally:
        temporary.unlink(missing_ok=True)
        if published:
            _fsync_directory(path.parent)


def safe_admissions_root(registration_path: Path, admissions_dir: Path) -> Path:
    if registration_path.is_symlink():
        raise AdmissionError("registration path must not be a symlink")
    experiment_root = registration_path.resolve().parent
    artifacts = experiment_root / "artifacts"
    if artifacts.is_symlink():
        raise AdmissionError("experiment artifacts directory must not be a symlink")
    expected = artifacts / "admissions"
    if admissions_dir.is_symlink():
        raise AdmissionError("admissions directory must not be a symlink")
    if admissions_dir.resolve(strict=False) != expected.resolve(strict=False):
        raise AdmissionError("admissions directory must be the registered experiment artifacts/admissions path")
    artifacts.mkdir(parents=False, exist_ok=True)
    admissions_dir.mkdir(mode=0o700, parents=False, exist_ok=True)
    if admissions_dir.is_symlink() or not admissions_dir.is_dir():
        raise AdmissionError("admissions directory is unsafe")
    return admissions_dir


def existing_records(root: Path, schema: dict[str, Any]) -> list[tuple[Path, dict[str, Any]]]:
    records: list[tuple[Path, dict[str, Any]]] = []
    for case_dir in sorted(root.iterdir()):
        if case_dir.is_symlink() or not case_dir.is_dir():
            raise AdmissionError("unexpected non-directory entry in admissions root")
        entries = list(case_dir.iterdir())
        if len(entries) != 1 or entries[0].name != "admission.json":
            raise AdmissionError("admission case directory must contain only admission.json")
        path = entries[0]
        value = load_object(path, "existing admission")
        validate(value, schema, "existing admission")
        if value["frozen_request"]["case_id"] != case_dir.name:
            raise AdmissionError("existing admission case_id does not match its directory")
        records.append((path, value))
    return records


def admit(
    registration_path: Path,
    request_path: Path,
    admissions_dir: Path,
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    registration = load_object(registration_path, "registration")
    validate_registration(registration, registration_path)
    admission_schema = load_schema(ADMISSION_SCHEMA)
    request = load_object(request_path, "admission request")
    validate(request, request_schema(admission_schema), "admission request")
    admitted = (now or now_utc()).astimezone(timezone.utc)
    validate_request_semantics(request, registration, admitted)
    registration_digest = sha256_json(registration)
    request_digest = sha256_json(request)

    root = safe_admissions_root(registration_path, admissions_dir)
    lock_fd = _lock_fd(root)
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
        records = existing_records(root, admission_schema)
        case_id = request["case_id"]
        for path, existing in records:
            if existing["frozen_request"]["case_id"] != case_id:
                continue
            if existing["request_sha256"] == request_digest and existing["registration_sha256"] == registration_digest:
                return {
                    "status": "already_admitted",
                    "idempotent": True,
                    "admission_id": existing["admission_id"],
                    "case_id": case_id,
                    "condition": existing["assignment_evidence"]["condition"],
                    "automatic_assignment": existing["assignment_evidence"].get("automatic") is True,
                    "path": str(path),
                }
            raise AdmissionError("case_id already has an immutable conflicting admission")

        source = request["eligibility_evidence"]
        assignment = request["assignment"]
        for _path, existing in records:
            existing_source = existing["frozen_request"]["eligibility_evidence"]
            if source["ref"] == existing_source["ref"] or source["sha256"] == existing_source["sha256"]:
                raise AdmissionError("eligibility evidence is already bound to another case")
            existing_assignment = existing["frozen_request"]["assignment"]
            if "evidence_ref" in assignment and "evidence_ref" in existing_assignment and (assignment["evidence_ref"] == existing_assignment["evidence_ref"] or assignment["evidence_sha256"] == existing_assignment["evidence_sha256"]):
                raise AdmissionError("assignment evidence is already bound to another case")

        if registration.get("assignment") is None:
            assignment_evidence = {
                "condition": assignment["condition"],
                "mode": "explicit_preplanning_assignment",
                "automatic": False,
                "fairness_claim": "not_established_by_registration_v2",
                "registration_rule_status": "automatic_assignment_not_frozen",
            }
        else:
            assignment_evidence = _automatic_assignment(request, registration, records)
        record = build_record(request, registration, admitted, assignment_evidence)
        validate(record, admission_schema, "admission record")

        case_dir = root / case_id
        if case_dir.exists() or case_dir.is_symlink():
            raise AdmissionError("case admission directory already exists")
        case_dir.mkdir(mode=0o700)
        try:
            path = case_dir / "admission.json"
            publish_create_only(path, record)
        except Exception:
            try:
                case_dir.rmdir()
            except OSError:
                pass
            raise
        _fsync_directory(root)
        return {
            "status": "admitted",
            "idempotent": False,
            "admission_id": record["admission_id"],
            "case_id": case_id,
            "condition": record["assignment_evidence"]["condition"],
            "automatic_assignment": record["assignment_evidence"].get("automatic") is True,
            "path": str(path),
        }
    finally:
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
        finally:
            os.close(lock_fd)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registration", type=Path, default=DEFAULT_REGISTRATION)
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--admissions-dir", type=Path, default=DEFAULT_ADMISSIONS)
    args = parser.parse_args(argv)
    try:
        result = admit(args.registration, args.request, args.admissions_dir)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (AdmissionError, OSError, ValueError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
