#!/usr/bin/env python3
"""Atomically capture one evidence-bound observation for an effect experiment."""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import importlib.util
import json
import math
import os
import stat
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
OBSERVATIONS_SCHEMA = ROOT / "schemas/effect-evaluation.observations.v2.schema.json"
ADMISSION_SCHEMA = ROOT / "schemas/natural-case-admission.v1.schema.json"
REGISTRATION_GATE_PATH = ROOT / "scripts/docmeta/validate_experiment_registration.py"


def _load_registration_gate() -> Any:
    spec = importlib.util.spec_from_file_location("vibe_registration_gate_capture", REGISTRATION_GATE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load registration gate from {REGISTRATION_GATE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


REGISTRATION_GATE = _load_registration_gate()


class CaptureError(RuntimeError):
    pass


def validate_registration_contract(path: Path) -> dict[str, Any]:
    try:
        return REGISTRATION_GATE.validate_registration(path)
    except Exception as exc:
        raise CaptureError(f"registration contract invalid: {exc}") from exc


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def admission_registration_sha256(value: Any) -> str:
    raw = (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def sha256_file(path: Path) -> str:
    if path.is_symlink():
        raise CaptureError("evidence file must not be a symlink")
    flags = os.O_RDONLY
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise CaptureError(f"cannot open evidence file {path}: {exc}") from exc
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise CaptureError("evidence file is not a regular file")
        digest = hashlib.sha256()
        while True:
            block = os.read(descriptor, 1024 * 1024)
            if not block:
                break
            digest.update(block)
        after = os.fstat(descriptor)
        identity = (
            before.st_dev,
            before.st_ino,
            before.st_size,
            before.st_mtime_ns,
            before.st_ctime_ns,
        )
        if identity != (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_mtime_ns,
            after.st_ctime_ns,
        ):
            raise CaptureError("evidence file changed while hashing")
        return digest.hexdigest()
    finally:
        os.close(descriptor)


def load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CaptureError(f"cannot read JSON object {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise CaptureError(f"{path}: root must be object")
    return value


def validate_schema(value: dict[str, Any], schema_path: Path) -> None:
    schema = load_object(schema_path)
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(value),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        first = errors[0]
        location = "/".join(str(part) for part in first.absolute_path) or "<root>"
        raise CaptureError(f"schema validation failed at {location}: {first.message}")


def parse_timestamp(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise CaptureError(f"invalid timestamp: {value}") from exc
    if parsed.tzinfo is None:
        raise CaptureError("timestamp must include timezone")
    return parsed.astimezone(timezone.utc)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _secure_lock_root() -> Path:
    base = Path(os.environ.get("XDG_RUNTIME_DIR") or tempfile.gettempdir())
    root = base / f"vibe-lab-effect-observation-locks-{os.getuid()}"
    try:
        root.mkdir(mode=0o700, parents=True, exist_ok=True)
        metadata = root.lstat()
    except OSError as exc:
        raise CaptureError(f"cannot prepare observation lock directory {root}: {exc}") from exc
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
        raise CaptureError("observation lock root must be a real directory")
    if metadata.st_uid != os.getuid() or stat.S_IMODE(metadata.st_mode) & 0o077:
        raise CaptureError("observation lock root ownership or permissions are unsafe")
    return root


def _scorecard_weights(registration: dict[str, Any]) -> dict[str, float] | None:
    scorecard = registration["measurement"].get("scorecard")
    if scorecard is None:
        return None
    components = scorecard["components"]
    weights = {component["id"]: float(component["weight"]) for component in components}
    if len(weights) != len(components):
        raise CaptureError("scorecard component ids must be unique")
    return weights


def validate_observation_semantics(
    observation: dict[str, Any],
    registration: dict[str, Any],
) -> None:
    if not math.isfinite(float(observation["value"])):
        raise CaptureError("observation value must be finite")
    effort = float(observation["effort_seconds"])
    if not math.isfinite(effort) or effort < 0:
        raise CaptureError("effort_seconds must be finite and non-negative")
    if observation["condition"] not in {
        registration["control_condition"]["id"],
        registration["treatment_condition"]["id"],
    }:
        raise CaptureError("condition is not registered")
    weights = _scorecard_weights(registration)
    components = observation.get("score_components")
    if weights is None and components is not None:
        raise CaptureError("score_components are not registered for this metric")
    if weights is not None:
        if not isinstance(components, dict) or set(components) != set(weights):
            raise CaptureError("score_components must match the registered scorecard exactly")
        expected = sum(weights[key] * int(components[key]) for key in weights)
        if not math.isclose(float(observation["value"]), expected, rel_tol=0.0, abs_tol=1e-12):
            raise CaptureError("observation value does not match registered scorecard")
    if (
        registration["evidence_sources"]["independent_observation_required"]
        and observation["observer_ref"] == observation["decision_maker_ref"]
    ):
        raise CaptureError("independent scorer must differ from decision maker")
    captured_at = parse_timestamp(observation["captured_at"])
    if not REGISTRATION_GATE.is_pre_t005_experiment(registration["experiment_id"]):
        if captured_at < parse_timestamp(registration["registered_at"]):
            raise CaptureError("observation was captured before experiment registration")
    if captured_at > parse_timestamp(registration["expires_at"]):
        raise CaptureError("observation was captured after experiment expiry")


def validate_pair_semantics(
    observations: list[dict[str, Any]],
    registration: dict[str, Any],
) -> None:
    if registration["comparison"]["mode"] != "paired":
        return
    control_id = registration["control_condition"]["id"]
    treatment_id = registration["treatment_condition"]["id"]
    by_pair: dict[str, dict[str, dict[str, Any]]] = {}
    for row in observations:
        pair_id = row.get("pair_id")
        if not pair_id:
            continue
        bucket = by_pair.setdefault(pair_id, {})
        if row["condition"] in bucket:
            raise CaptureError("duplicate condition within pair")
        bucket[row["condition"]] = row
    for bucket in by_pair.values():
        if control_id in bucket and treatment_id in bucket:
            if bucket[control_id]["decision_maker_ref"] == bucket[treatment_id]["decision_maker_ref"]:
                raise CaptureError("paired conditions require distinct decision_maker_ref values")


def _safe_lock_fd(path: Path) -> int:
    flags = os.O_RDWR | os.O_CREAT
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        return os.open(path, flags, 0o600)
    except OSError as exc:
        raise CaptureError(f"cannot open observation lock {path}: {exc}") from exc


def _fsync_directory(directory: Path) -> None:
    flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    descriptor = os.open(directory, flags)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise CaptureError("observations path must not be a symlink")
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    temporary = Path(temporary_name)
    published = False
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        published = True
        _fsync_directory(path.parent)
    finally:
        if not published:
            temporary.unlink(missing_ok=True)


def initial_document(registration: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "effect-evaluation.observations.v2",
        "experiment_id": registration["experiment_id"],
        "registration_sha256": sha256_json(registration),
        "metric": registration["measurement"]["primary_metric"],
        "observations": [],
    }


def validate_binding(document: dict[str, Any], registration: dict[str, Any]) -> None:
    if document.get("experiment_id") != registration["experiment_id"]:
        raise CaptureError("experiment_id mismatch")
    if document.get("metric") != registration["measurement"]["primary_metric"]:
        raise CaptureError("primary metric mismatch")
    if document.get("registration_sha256") != sha256_json(registration):
        raise CaptureError("registration digest mismatch; observations are bound to another registration")


def _bind_admission(admission_path: Path | None, registration_path: Path, registration: dict[str, Any], observation: dict[str, Any]) -> None:
    if registration.get("assignment") is None:
        if admission_path is not None:
            raise CaptureError("admission binding is only valid for a registration with prospective assignment")
        return
    if admission_path is None:
        raise CaptureError("prospectively assigned experiment requires --admission")
    if admission_path.is_symlink() or not admission_path.is_file():
        raise CaptureError("admission must be a regular non-symlink file")
    experiment_root = registration_path.resolve().parent
    admissions_root = (experiment_root / "artifacts" / "admissions").resolve()
    resolved = admission_path.resolve()
    try:
        relative = resolved.relative_to(admissions_root)
    except ValueError as exc:
        raise CaptureError("admission must be inside the registered experiment admissions directory") from exc
    if len(relative.parts) != 2 or relative.parts[1] != "admission.json":
        raise CaptureError("admission path must be artifacts/admissions/<case-id>/admission.json")
    admission = load_object(admission_path)
    validate_schema(admission, ADMISSION_SCHEMA)
    if admission["experiment_id"] != registration["experiment_id"]:
        raise CaptureError("admission experiment_id mismatch")
    if admission["registration_sha256"] != admission_registration_sha256(registration):
        raise CaptureError("admission registration digest mismatch")
    if admission["frozen_request"]["case_id"] != relative.parts[0]:
        raise CaptureError("admission case id does not match its directory")
    if observation["condition"] != admission["assignment_evidence"]["condition"]:
        raise CaptureError("observation condition does not match prospective admission")
    if observation["comparison_key"] != admission["frozen_request"]["comparability"]["comparison_key"]:
        raise CaptureError("observation comparison_key does not match prospective admission")
    blinded_case_id = admission["review_preparation"]["blinded_case_id"]
    if observation["observation_id"] != blinded_case_id:
        raise CaptureError("observation_id must equal the admission blinded_case_id")
    if observation["scoring_blinded"] is not True:
        raise CaptureError("prospective Chronik observation requires blinded scoring")
    if observation["independent"] is not True:
        raise CaptureError("prospective Chronik observation requires independent scoring")
    observation["admission_binding"] = {
        "case_id": relative.parts[0],
        "admission_id": admission["admission_id"],
        "admission_sha256": sha256_file(admission_path),
        "blinded_case_id": blinded_case_id,
    }


def capture(
    registration_path: Path,
    observations_path: Path,
    observation: dict[str, Any],
    *,
    admission_path: Path | None = None,
) -> dict[str, Any]:
    registration = validate_registration_contract(registration_path)
    observation = dict(observation)
    _bind_admission(admission_path, registration_path, registration, observation)
    validate_schema(
        {
            **initial_document(registration),
            "observations": [observation],
        },
        OBSERVATIONS_SCHEMA,
    )
    validate_observation_semantics(observation, registration)

    if observations_path.is_symlink():
        raise CaptureError("observations path must not be a symlink")
    experiment_root = registration_path.resolve().parent
    results_path = experiment_root / "results"
    if results_path.is_symlink():
        raise CaptureError("experiment results directory must not be a symlink")
    results_root = results_path.resolve()
    try:
        results_root.relative_to(experiment_root)
    except ValueError as exc:
        raise CaptureError("experiment results directory escapes the experiment") from exc
    target = observations_path.resolve(strict=False)
    try:
        target.relative_to(results_root)
    except ValueError as exc:
        raise CaptureError("observations path must be inside the registered experiment results directory") from exc

    observations_path.parent.mkdir(parents=True, exist_ok=True)
    lock_name = hashlib.sha256(os.fsencode(str(target))).hexdigest() + ".lock"
    lock_fd = _safe_lock_fd(_secure_lock_root() / lock_name)
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
        if observations_path.is_symlink():
            raise CaptureError("observations path must not be a symlink")
        if observations_path.exists():
            document = load_object(observations_path)
            validate_schema(document, OBSERVATIONS_SCHEMA)
            validate_binding(document, registration)
        else:
            document = initial_document(registration)

        rows = document["observations"]
        if any(row["observation_id"] == observation["observation_id"] for row in rows):
            raise CaptureError("duplicate observation_id")
        if any(row["evidence_ref"] == observation["evidence_ref"] for row in rows):
            raise CaptureError("duplicate evidence_ref")
        if any(row["evidence_sha256"] == observation["evidence_sha256"] for row in rows):
            raise CaptureError("duplicate evidence_sha256")

        rows.append(observation)
        rows.sort(key=lambda row: row["observation_id"])
        for row in rows:
            validate_observation_semantics(row, registration)
        validate_pair_semantics(rows, registration)
        validate_schema(document, OBSERVATIONS_SCHEMA)
        atomic_json(observations_path, document)
        return {
            "experiment_id": document["experiment_id"],
            "registration_sha256": document["registration_sha256"],
            "observation_id": observation["observation_id"],
            "evidence_sha256": observation["evidence_sha256"],
            "observation_count": len(rows),
            "observations_path": str(observations_path),
        }
    finally:
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
        finally:
            os.close(lock_fd)


def build_observation(args: argparse.Namespace, registration: dict[str, Any]) -> dict[str, Any]:
    evidence_digest = args.evidence_sha256
    if args.evidence_file is not None:
        if not args.evidence_file.is_file():
            raise CaptureError("evidence file does not exist or is not a regular file")
        computed = sha256_file(args.evidence_file)
        if evidence_digest is not None and evidence_digest != computed:
            raise CaptureError("supplied evidence SHA-256 does not match evidence file")
        evidence_digest = computed
    if evidence_digest is None:
        raise CaptureError("provide --evidence-file or --evidence-sha256")
    if args.independent is None:
        raise CaptureError("state independence explicitly with --independent or --no-independent")
    if args.scoring_blinded is None:
        raise CaptureError("state scoring blinding explicitly with --scoring-blinded or --no-scoring-blinded")
    effort_seconds = float(args.effort_seconds)
    if not math.isfinite(effort_seconds) or effort_seconds < 0:
        raise CaptureError("effort_seconds must be finite and non-negative")
    weights = _scorecard_weights(registration)
    score_components: dict[str, int] | None = None
    if weights is None:
        if args.value is None:
            raise CaptureError("--value is required when no scorecard is registered")
        if args.score_component:
            raise CaptureError("--score-component requires a registered scorecard")
        value = float(args.value)
    else:
        if args.value is not None:
            raise CaptureError("--value is forbidden when a scorecard is registered")
        score_components = {}
        for item in args.score_component:
            key, separator, raw_value = item.partition("=")
            if not separator or raw_value not in {"0", "1"} or key in score_components:
                raise CaptureError("score components must be unique NAME=0 or NAME=1 values")
            score_components[key] = int(raw_value)
        if set(score_components) != set(weights):
            raise CaptureError("score components must match the registered scorecard exactly")
        value = sum(weights[key] * score_components[key] for key in weights)
    if not math.isfinite(value):
        raise CaptureError("observation value must be finite")
    observation: dict[str, Any] = {
        "observation_id": args.observation_id,
        "condition": args.condition,
        "value": value,
        "effort_seconds": effort_seconds,
        "scoring_blinded": args.scoring_blinded,
        "comparison_key": args.comparison_key,
        "evidence_ref": args.evidence_ref,
        "evidence_sha256": evidence_digest,
        "decision_maker_ref": args.decision_maker_ref,
        "observer_ref": args.observer_ref,
        "independent": args.independent,
        "captured_at": args.captured_at or utc_now(),
    }
    if args.pair_id:
        observation["pair_id"] = args.pair_id
    if score_components is not None:
        observation["score_components"] = score_components
    return observation


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registration", required=True, type=Path)
    parser.add_argument("--observations", required=True, type=Path)
    parser.add_argument("--admission", type=Path)
    parser.add_argument("--observation-id", required=True)
    parser.add_argument("--condition", required=True)
    parser.add_argument("--value")
    parser.add_argument("--score-component", action="append", default=[])
    parser.add_argument("--effort-seconds", required=True)
    parser.add_argument(
        "--scoring-blinded",
        action=argparse.BooleanOptionalAction,
        default=None,
    )
    parser.add_argument("--comparison-key", required=True)
    parser.add_argument("--pair-id")
    parser.add_argument("--evidence-ref", required=True)
    evidence = parser.add_mutually_exclusive_group(required=True)
    evidence.add_argument("--evidence-file", type=Path)
    evidence.add_argument("--evidence-sha256")
    parser.add_argument("--decision-maker-ref", required=True)
    parser.add_argument("--observer-ref", required=True)
    parser.add_argument(
        "--independent",
        action=argparse.BooleanOptionalAction,
        default=None,
    )
    parser.add_argument("--captured-at")
    args = parser.parse_args(argv)
    try:
        registration = load_object(args.registration)
        result = capture(
            args.registration,
            args.observations,
            build_observation(args, registration),
            admission_path=args.admission,
        )
    except (CaptureError, KeyError, OSError, ValueError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
