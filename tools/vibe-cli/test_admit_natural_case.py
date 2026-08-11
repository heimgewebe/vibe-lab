#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import importlib.util
import json
import multiprocessing
from pathlib import Path
import tempfile
import unittest

from jsonschema import Draft202012Validator, FormatChecker


SCRIPT = Path(__file__).with_name("admit_natural_case.py")
ROOT = SCRIPT.parents[2]
FIXTURES = ROOT / "tests/fixtures/natural_case_admission"
SPEC = importlib.util.spec_from_file_location("admit_natural_case", SCRIPT)
assert SPEC and SPEC.loader
ADMISSION = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ADMISSION)
FIXED_NOW = datetime(2026, 8, 11, 6, 49, tzinfo=timezone.utc)


def _process_admit(
    registration: Path,
    request: Path,
    admissions: Path,
    output: multiprocessing.Queue,
) -> None:
    try:
        output.put(("ok", ADMISSION.admit(registration, request, admissions, now=FIXED_NOW)))
    except Exception as exc:  # pragma: no cover - returned to the parent for assertion
        output.put(("error", f"{type(exc).__name__}: {exc}"))


class NaturalCaseAdmissionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.experiment = self.root / "experiments/2026-07-13_chronik-history-brief-effect"
        self.experiment.mkdir(parents=True)
        self.registration = self.experiment / "registration.v2.json"
        self.registration.write_bytes(ADMISSION.DEFAULT_REGISTRATION.read_bytes())
        self.admissions = self.experiment / "artifacts/admissions"

    def request(self, *, case_id: str = "chronik-natural-001") -> dict:
        value = json.loads((FIXTURES / "valid-control-request.json").read_text(encoding="utf-8"))
        value["case_id"] = case_id
        return value

    def write_request(self, value: dict, name: str = "request.json") -> Path:
        path = self.root / name
        path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
        return path

    def admit(self, value: dict, *, now: datetime = FIXED_NOW) -> dict:
        return ADMISSION.admit(
            self.registration,
            self.write_request(value),
            self.admissions,
            now=now,
        )

    def record_path(self, case_id: str = "chronik-natural-001") -> Path:
        return self.admissions / case_id / "admission.json"

    def test_admission_freezes_registration_comparability_assignment_and_review(self) -> None:
        result = self.admit(self.request())
        record = json.loads(self.record_path().read_text(encoding="utf-8"))
        schema = json.loads(ADMISSION.ADMISSION_SCHEMA.read_text(encoding="utf-8"))
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(record)

        registration = json.loads(self.registration.read_text(encoding="utf-8"))
        self.assertEqual(result["status"], "admitted")
        self.assertTrue(result["automatic_assignment"])
        self.assertEqual(record["registration_sha256"], ADMISSION.sha256_json(registration))
        self.assertEqual(
            record["comparability_sha256"],
            ADMISSION.sha256_json(record["frozen_request"]["comparability"]),
        )
        self.assertIn(record["assignment_evidence"]["condition"], {"live_preflight_only", "live_preflight_plus_history"})
        self.assertTrue(record["assignment_evidence"]["automatic"])
        self.assertEqual(record["assignment_evidence"]["fairness_claim"], "registration_bound_stratum_balance_only")
        self.assertEqual(record["assignment_evidence"]["sequence_index"], 0)
        self.assertEqual(record["review_preparation"]["status"], "pending_independent_review")
        self.assertTrue(record["review_preparation"]["blinding_required"])
        self.assertEqual(record["review_preparation"]["minimum_control"], 3)
        self.assertEqual(record["review_preparation"]["minimum_treatment"], 3)
        self.assertEqual(record["review_preparation"]["review_at"], "2026-08-15T00:00:00Z")
        self.assertEqual(record["traceability"]["triggered_by"], "natural-coding-case-receipt-001")
        self.assertEqual(self.record_path().stat().st_mode & 0o777, 0o444)

    def test_identical_retry_is_idempotent_and_preserves_original_bytes(self) -> None:
        request = self.request()
        first = self.admit(request)
        before = self.record_path().read_bytes()
        second = self.admit(request, now=FIXED_NOW + timedelta(hours=1))
        self.assertFalse(first["idempotent"])
        self.assertTrue(second["idempotent"])
        self.assertEqual(second["status"], "already_admitted")
        self.assertEqual(self.record_path().read_bytes(), before)

    def test_conflicting_retry_is_refused_without_mutation(self) -> None:
        request = self.request()
        self.admit(request)
        before = self.record_path().read_bytes()
        request["comparability"]["task_difficulty_band"] = "medium"
        with self.assertRaisesRegex(ADMISSION.AdmissionError, "immutable conflicting admission"):
            self.admit(request)
        self.assertEqual(self.record_path().read_bytes(), before)

    def test_duplicate_case_evidence_is_refused_across_case_ids(self) -> None:
        self.admit(self.request())
        duplicate = self.request(case_id="chronik-natural-002")
        with self.assertRaisesRegex(ADMISSION.AdmissionError, "eligibility evidence is already bound"):
            self.admit(duplicate)
        self.assertFalse(self.record_path("chronik-natural-002").exists())

    def test_registration_drift_is_refused_for_existing_case(self) -> None:
        request = self.request()
        self.admit(request)
        before = self.record_path().read_bytes()
        registration = json.loads(self.registration.read_text(encoding="utf-8"))
        registration["decision_target"]["question"] = "Does a changed question invalidate the frozen admission binding?"
        prior = dict(registration)
        prior.pop("assignment", None)
        registration["assignment"]["prior_registration_sha256"] = ADMISSION.sha256_json(prior)
        self.registration.write_text(json.dumps(registration), encoding="utf-8")
        with self.assertRaisesRegex(ADMISSION.AdmissionError, "immutable conflicting admission"):
            self.admit(request)
        self.assertEqual(self.record_path().read_bytes(), before)

    def test_planning_started_fixture_is_refused_before_creation(self) -> None:
        request_path = FIXTURES / "invalid-backfill-request.json"
        with self.assertRaisesRegex(ADMISSION.AdmissionError, "planning_started"):
            ADMISSION.admit(self.registration, request_path, self.admissions, now=FIXED_NOW)
        self.assertFalse(self.admissions.exists())

    def test_pre_registration_case_is_refused_as_backfill(self) -> None:
        request = self.request()
        request["case_opened_at"] = "2026-07-12T23:59:00Z"
        request["eligibility_evidence"]["captured_at"] = "2026-07-12T23:59:30Z"
        with self.assertRaisesRegex(ADMISSION.AdmissionError, "backfill refused"):
            self.admit(request)
        self.assertFalse(self.admissions.exists())

    def test_post_expiry_admission_is_refused(self) -> None:
        with self.assertRaisesRegex(ADMISSION.AdmissionError, "expired"):
            self.admit(self.request(), now=datetime(2026, 9, 1, tzinfo=timezone.utc))
        self.assertFalse(self.admissions.exists())

    def test_manual_condition_is_rejected_after_assignment_revision(self) -> None:
        request = self.request()
        request["assignment"] = {"condition": "live_preflight_only", "assigned_by": "operator:manual", "evidence_ref": "receipt:manual-assignment", "evidence_sha256": "a" * 64, "recorded_before_planning": True}
        with self.assertRaisesRegex(ADMISSION.AdmissionError, "registered automatic assignment"):
            self.admit(request)
        self.assertFalse(self.admissions.exists())

    def test_two_cases_in_same_stratum_are_balanced(self) -> None:
        first = self.request(case_id="chronik-natural-001")
        second = self.request(case_id="chronik-natural-002")
        second["eligibility_evidence"] = {"ref": "receipt:natural-case-002", "sha256": "3" * 64, "captured_at": "2026-08-11T06:48:41Z"}
        second["triggered_by"] = "natural-coding-case-receipt-002"
        one = self.admit(first); two = self.admit(second)
        self.assertNotEqual(one["condition"], two["condition"])
        record = json.loads(self.record_path("chronik-natural-002").read_text())
        self.assertEqual(record["assignment_evidence"]["sequence_index"], 1)
        self.assertEqual(record["assignment_evidence"]["block_index"], 0)
        self.assertEqual(record["assignment_evidence"]["block_position"], 1)

    def test_different_strata_start_independent_sequences(self) -> None:
        first = self.request(case_id="chronik-natural-001")
        second = self.request(case_id="chronik-natural-002")
        second["eligibility_evidence"] = {"ref": "receipt:natural-case-002", "sha256": "4" * 64, "captured_at": "2026-08-11T06:48:41Z"}
        second["comparability"]["risk_band"] = "R2"
        self.admit(first); self.admit(second)
        record = json.loads(self.record_path("chronik-natural-002").read_text())
        self.assertEqual(record["assignment_evidence"]["sequence_index"], 0)

    def test_case_opened_before_assignment_revision_is_refused(self) -> None:
        request = self.request()
        request["case_opened_at"] = "2026-08-11T06:47:59Z"
        request["eligibility_evidence"]["captured_at"] = "2026-08-11T06:48:40Z"
        with self.assertRaisesRegex(ADMISSION.AdmissionError, "case predates the prospective assignment revision"):
            self.admit(request)
        self.assertFalse(self.admissions.exists())

    def test_older_registration_digest_does_not_advance_new_sequence(self) -> None:
        first = self.request(case_id="chronik-old-digest-001")
        self.admit(first)
        old_path = self.record_path("chronik-old-digest-001")
        old_path.chmod(0o600)
        old = json.loads(old_path.read_text())
        old["registration_sha256"] = "0" * 64
        old_path.write_text(json.dumps(old, indent=2) + "\n")
        old_path.chmod(0o444)
        second = self.request(case_id="chronik-current-001")
        second["eligibility_evidence"] = {"ref": "receipt:current-001", "sha256": "5" * 64, "captured_at": "2026-08-11T06:48:41Z"}
        second["triggered_by"] = "natural-coding-case-current-001"
        self.admit(second)
        current = json.loads(self.record_path("chronik-current-001").read_text())
        self.assertEqual(current["assignment_evidence"]["sequence_index"], 0)

    def test_two_concurrent_distinct_cases_get_one_block_each_position(self) -> None:
        one = self.request(case_id="concurrent-distinct-001")
        two = self.request(case_id="concurrent-distinct-002")
        two["eligibility_evidence"] = {"ref": "receipt:concurrent-distinct-002", "sha256": "6" * 64, "captured_at": "2026-08-11T06:48:41Z"}
        two["triggered_by"] = "natural-coding-case-concurrent-002"
        paths = [self.write_request(one, "concurrent-one.json"), self.write_request(two, "concurrent-two.json")]
        context = multiprocessing.get_context("fork")
        output = context.Queue()
        processes = [context.Process(target=_process_admit, args=(self.registration, request, self.admissions, output)) for request in paths]
        for process in processes:
            process.start()
        for process in processes:
            process.join(timeout=20)
        results = [output.get(timeout=5) for _ in processes]
        self.assertEqual([process.exitcode for process in processes], [0, 0], results)
        self.assertEqual([status for status, _payload in results], ["ok", "ok"], results)
        records = [json.loads(self.record_path(case_id).read_text()) for case_id in ("concurrent-distinct-001", "concurrent-distinct-002")]
        self.assertEqual({record["assignment_evidence"]["sequence_index"] for record in records}, {0, 1})
        self.assertEqual({record["assignment_evidence"]["block_position"] for record in records}, {0, 1})
        self.assertEqual(len({record["assignment_evidence"]["condition"] for record in records}), 2)

    def test_writer_is_not_a_generic_runtime_admission_service(self) -> None:
        other = self.root / "experiments/2026-07-13_other-experiment"
        other.mkdir()
        registration = json.loads(self.registration.read_text(encoding="utf-8"))
        registration["experiment_id"] = other.name
        registration["closure"]["archive_path"] = f"experiments/_archive/{other.name}"
        registration_path = other / "registration.v2.json"
        registration_path.write_text(json.dumps(registration), encoding="utf-8")
        with self.assertRaisesRegex(ADMISSION.AdmissionError, "limited to the registered Chronik"):
            ADMISSION.admit(
                registration_path,
                self.write_request(self.request()),
                other / "artifacts/admissions",
                now=FIXED_NOW,
            )
        self.assertFalse((other / "artifacts").exists())

    def test_target_outside_experiment_admissions_is_refused(self) -> None:
        outside = self.root / "outside-admissions"
        with self.assertRaisesRegex(ADMISSION.AdmissionError, "must be the registered experiment"):
            ADMISSION.admit(
                self.registration,
                self.write_request(self.request()),
                outside,
                now=FIXED_NOW,
            )
        self.assertFalse(outside.exists())

    def test_symlink_admissions_root_is_refused(self) -> None:
        victim = self.root / "victim"
        victim.mkdir()
        (self.experiment / "artifacts").mkdir()
        self.admissions.symlink_to(victim, target_is_directory=True)
        with self.assertRaisesRegex(ADMISSION.AdmissionError, "must not be a symlink"):
            self.admit(self.request())
        self.assertEqual(list(victim.iterdir()), [])

    def test_two_processes_preserve_one_create_only_record(self) -> None:
        request = self.request(case_id="concurrent-natural-001")
        request_path = self.write_request(request, "concurrent-request.json")
        context = multiprocessing.get_context("fork")
        output = context.Queue()
        processes = [
            context.Process(
                target=_process_admit,
                args=(self.registration, request_path, self.admissions, output),
            )
            for _ in range(2)
        ]
        for process in processes:
            process.start()
        for process in processes:
            process.join(timeout=20)
        results = [output.get(timeout=5) for _ in processes]
        self.assertEqual([process.exitcode for process in processes], [0, 0], results)
        self.assertEqual([status for status, _payload in results], ["ok", "ok"], results)
        payloads = [payload for _status, payload in results]
        self.assertEqual({payload["status"] for payload in payloads}, {"admitted", "already_admitted"})
        record = self.admissions / request["case_id"] / "admission.json"
        self.assertTrue(record.is_file())
        self.assertEqual(len(list(self.admissions.rglob("admission.json"))), 1)


if __name__ == "__main__":
    unittest.main()
