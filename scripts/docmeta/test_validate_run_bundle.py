#!/usr/bin/env python3
"""Regression tests for validate_run_bundle.py.

Each test builds a tiny experiment fixture under a temporary directory that
mimics the real repo layout (with real schema files copied/symlinked from
the project) and runs validate_repo() against it.

Run:
    python3 scripts/docmeta/test_validate_run_bundle.py
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR))

from validate_run_bundle import (  # noqa: E402
    _check_auditor_semantics,
    _check_measurement_semantics,
    _compute_max_severity,
    validate_repo,
)


REPO_ROOT = THIS_DIR.parent.parent
PROJECT_SCHEMAS = REPO_ROOT / "schemas"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_repo_skeleton(base: Path) -> Path:
    """Erzeugt unter base/ ein minimales Repo-Skelett mit den drei
    Bundle-Schemas, sodass validate_repo(base) ohne echtes Repo läuft."""
    schemas = base / "schemas"
    schemas.mkdir(parents=True, exist_ok=True)
    for name in (
        "experiment-run-bundle.v1.schema.json",
        "auditor-output.v1.schema.json",
        "measurement-run.v1.schema.json",
    ):
        shutil.copy(PROJECT_SCHEMAS / name, schemas / name)
    (base / "experiments").mkdir(exist_ok=True)
    return base


def _exp_dir(base: Path, name: str = "exp-fixture") -> Path:
    d = base / "experiments" / name
    (d / "results").mkdir(parents=True, exist_ok=True)
    (d / "artifacts").mkdir(parents=True, exist_ok=True)
    return d


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip("\n"), encoding="utf-8")


def _valid_manifest(execution_status: str = "executed") -> str:
    return f"""
    schema_version: "0.1.0"
    experiment:
      name: "fixture"
      hypothesis: "h"
      status: testing
      category: workflow
      execution_status: {execution_status}
      execution_refs:
        - results/evidence.jsonl
        - artifacts/run-001/run.yml
      created: "2026-05-01"
      updated: "2026-05-01"
      author: "test"
      iteration: 1
      evidence_level: anecdotal
    """


def _valid_evidence_run() -> str:
    return (
        '{"event_type":"run","timestamp":"2026-05-01T00:00:00Z","iteration":1,'
        '"metric":"x","value":true,"context":"c",'
        '"artifact_ref":"artifacts/run-001/measurement.yml"}\n'
    )


def _valid_run_yml() -> str:
    return """
    schema_version: "1.0.0"
    contract: "experiment_run_bundle"
    run:
      id: "run-001"
      experiment_path: "experiments/exp-fixture"
      created_at: "2026-05-01T12:00:00Z"
      sequence: 1
    provenance:
      level: "self_reported"
      executor: "local:test"
    artifacts:
      auditor_output:
        path: "auditor-output.yml"
        contract: "auditor_output"
        canonical: true
      measurement:
        path: "measurement.yml"
        contract: "measurement_run"
        canonical: true
    verdict:
      outcome: "MISSING_EVIDENCE"
      effect_claim_allowed: false
    """


def _valid_auditor_yml() -> str:
    return """
    schema_version: "1.0.0"
    contract: "auditor_output"
    run_id: "run-001"
    pr_ref: "github:test/test/pull/1"
    auditor: "test-auditor"
    overall_verdict: "MISSING_EVIDENCE"
    claims:
      - id: "c-1"
        text: "passing claim"
        type: "file_changed"
        verdict: "PASS"
        evidence: []
      - id: "c-2"
        text: "missing test log"
        type: "validator_succeeded"
        verdict: "MISSING_EVIDENCE"
        evidence: []
      - id: "c-3"
        text: "missing make output"
        type: "command_succeeded"
        verdict: "MISSING_EVIDENCE"
        evidence: []
    """


def _valid_measurement_yml(
    *,
    auditor_verdict: str = "MISSING_EVIDENCE",
    unsupported: int = 2,
    val_gap: int = 2,
) -> str:
    return f"""
    schema_version: "1.0.0"
    contract: "measurement_run"
    run_id: "run-001"
    auditor_verdict: "{auditor_verdict}"
    auditor_ref: "auditor-output.yml"
    metrics:
      scope_drift_count:
        value: 0
        evidence_status: "external_unverified"
      unsupported_claim_count:
        value: {unsupported}
        evidence_status: "derived_from_auditor_output"
      missing_locator_count:
        value: 0
        evidence_status: "external_unverified"
      validation_gap_count:
        value: {val_gap}
        evidence_status: "derived_from_auditor_output"
      review_friction_count:
        value: 0
        evidence_status: "external_unverified"
      rework_count:
        value: 0
        evidence_status: "external_unverified"
      false_block_count:
        value: 0
        evidence_status: "external_unverified"
      task_completion_time_observed:
        value: "n/a"
        evidence_status: "external_unverified"
    """


def _build_valid_bundle(base: Path) -> Path:
    """Schreibt ein vollständig valides Bundle und gibt das Experiment-Verzeichnis zurück."""
    exp = _exp_dir(base)
    _write(exp / "manifest.yml", _valid_manifest())
    _write(exp / "results" / "evidence.jsonl", _valid_evidence_run())
    run_dir = exp / "artifacts" / "run-001"
    run_dir.mkdir(parents=True, exist_ok=True)
    _write(run_dir / "run.yml", _valid_run_yml())
    _write(run_dir / "auditor-output.yml", _valid_auditor_yml())
    _write(run_dir / "measurement.yml", _valid_measurement_yml())
    return exp


# ---------------------------------------------------------------------------
# Pure-function tests
# ---------------------------------------------------------------------------

class SeverityPrecedenceTests(unittest.TestCase):
    def test_pass_only(self) -> None:
        self.assertEqual(_compute_max_severity(["PASS", "PASS"]), "PASS")

    def test_missing_evidence_dominates_claim_not_proven(self) -> None:
        self.assertEqual(
            _compute_max_severity(["CLAIM_NOT_PROVEN", "MISSING_EVIDENCE"]),
            "MISSING_EVIDENCE",
        )

    def test_contradiction_dominates_all(self) -> None:
        self.assertEqual(
            _compute_max_severity(
                ["MISSING_EVIDENCE", "OUT_OF_SCOPE", "CONTRADICTION", "NOT_REPRODUCIBLE"]
            ),
            "CONTRADICTION",
        )


class AuditorSemanticsTests(unittest.TestCase):
    def test_pass_with_non_pass_claim_rejected(self) -> None:
        auditor = {
            "overall_verdict": "PASS",
            "claims": [
                {"verdict": "PASS"},
                {"verdict": "MISSING_EVIDENCE"},
            ],
        }
        errs = _check_auditor_semantics(auditor)
        self.assertTrue(any("PASS" in e and "non-PASS" in e for e in errs), errs)

    def test_severity_mismatch_rejected(self) -> None:
        auditor = {
            "overall_verdict": "MISSING_EVIDENCE",
            "claims": [{"verdict": "CONTRADICTION"}],
        }
        errs = _check_auditor_semantics(auditor)
        self.assertTrue(any("Severity-Precedence" in e for e in errs), errs)

    def test_consistent_passes(self) -> None:
        auditor = {
            "overall_verdict": "MISSING_EVIDENCE",
            "claims": [
                {"verdict": "PASS"},
                {"verdict": "MISSING_EVIDENCE"},
            ],
        }
        self.assertEqual(_check_auditor_semantics(auditor), [])


class MeasurementSemanticsTests(unittest.TestCase):
    def test_verdict_mismatch_rejected(self) -> None:
        auditor = {"overall_verdict": "MISSING_EVIDENCE", "claims": []}
        meas = {
            "auditor_verdict": "PASS",
            "metrics": {},
        }
        errs = _check_measurement_semantics(meas, auditor)
        self.assertTrue(any("auditor_verdict" in e for e in errs), errs)

    def test_unsupported_count_mismatch_rejected(self) -> None:
        auditor = {
            "overall_verdict": "MISSING_EVIDENCE",
            "claims": [
                {"verdict": "PASS"},
                {"verdict": "MISSING_EVIDENCE", "type": "validator_succeeded"},
            ],
        }
        meas = {
            "auditor_verdict": "MISSING_EVIDENCE",
            "metrics": {
                "unsupported_claim_count": {"value": 0, "evidence_status": "self_reported"},
                "validation_gap_count": {"value": 1, "evidence_status": "self_reported"},
            },
        }
        errs = _check_measurement_semantics(meas, auditor)
        self.assertTrue(any("unsupported_claim_count" in e for e in errs), errs)

    def test_validation_gap_count_mismatch_rejected(self) -> None:
        auditor = {
            "overall_verdict": "MISSING_EVIDENCE",
            "claims": [
                {"verdict": "MISSING_EVIDENCE", "type": "validator_succeeded"},
                {"verdict": "MISSING_EVIDENCE", "type": "agent_usage"},
            ],
        }
        meas = {
            "auditor_verdict": "MISSING_EVIDENCE",
            "metrics": {
                "unsupported_claim_count": {"value": 2, "evidence_status": "self_reported"},
                "validation_gap_count": {"value": 2, "evidence_status": "self_reported"},
            },
        }
        errs = _check_measurement_semantics(meas, auditor)
        self.assertTrue(any("validation_gap_count" in e for e in errs), errs)


# ---------------------------------------------------------------------------
# End-to-end fixture tests
# ---------------------------------------------------------------------------

class RepoLevelTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)
        _make_repo_skeleton(self.base)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_valid_executed_bundle_passes(self) -> None:
        _build_valid_bundle(self.base)
        self.assertEqual(validate_repo(self.base), [])

    def test_run_event_with_prepared_status_fails(self) -> None:
        exp = _build_valid_bundle(self.base)
        # Manifest auf prepared zurücksetzen
        _write(exp / "manifest.yml", _valid_manifest(execution_status="prepared"))
        # execution_refs ist bei prepared optional → Schema bleibt gültig.
        errs = validate_repo(self.base)
        self.assertTrue(any("prepared" in e for e in errs), errs)

    def test_executed_with_empty_execution_refs_fails(self) -> None:
        exp = _build_valid_bundle(self.base)
        _write(
            exp / "manifest.yml",
            """
            schema_version: "0.1.0"
            experiment:
              name: "fixture"
              hypothesis: "h"
              status: testing
              category: workflow
              execution_status: executed
              execution_refs: []
              created: "2026-05-01"
              updated: "2026-05-01"
              author: "test"
              iteration: 1
              evidence_level: anecdotal
            """,
        )
        errs = validate_repo(self.base)
        self.assertTrue(any("execution_refs" in e for e in errs), errs)

    def test_missing_execution_ref_fails(self) -> None:
        exp = _build_valid_bundle(self.base)
        _write(
            exp / "manifest.yml",
            """
            schema_version: "0.1.0"
            experiment:
              name: "fixture"
              hypothesis: "h"
              status: testing
              category: workflow
              execution_status: executed
              execution_refs:
                - results/evidence.jsonl
                - artifacts/run-001/does-not-exist.yml
              created: "2026-05-01"
              updated: "2026-05-01"
              author: "test"
              iteration: 1
              evidence_level: anecdotal
            """,
        )
        errs = validate_repo(self.base)
        self.assertTrue(
            any("does-not-exist.yml" in e and "existiert nicht" in e for e in errs),
            errs,
        )

    def test_evidence_artifact_ref_missing_fails(self) -> None:
        exp = _build_valid_bundle(self.base)
        _write(
            exp / "results" / "evidence.jsonl",
            '{"event_type":"run","timestamp":"2026-05-01T00:00:00Z","iteration":1,'
            '"metric":"x","value":true,"context":"c",'
            '"artifact_ref":"artifacts/run-001/ghost.yml"}\n',
        )
        errs = validate_repo(self.base)
        self.assertTrue(any("ghost.yml" in e for e in errs), errs)

    def test_evidence_artifact_ref_to_canonical_false_md_fails(self) -> None:
        exp = _build_valid_bundle(self.base)
        run_dir = exp / "artifacts" / "run-001"
        _write(
            run_dir / "auditor-output.md",
            """
            ---
            canonical: false
            source_of_truth: false
            ---

            non-canonical projection.
            """,
        )
        _write(
            exp / "results" / "evidence.jsonl",
            '{"event_type":"run","timestamp":"2026-05-01T00:00:00Z","iteration":1,'
            '"metric":"x","value":true,"context":"c",'
            '"artifact_ref":"artifacts/run-001/auditor-output.md"}\n',
        )
        errs = validate_repo(self.base)
        self.assertTrue(any("non-canonical Markdown-Projektion" in e for e in errs), errs)

    def test_canonical_false_md_present_but_unreferenced_passes(self) -> None:
        exp = _build_valid_bundle(self.base)
        run_dir = exp / "artifacts" / "run-001"
        _write(
            run_dir / "auditor-output.md",
            """
            ---
            canonical: false
            source_of_truth: false
            ---

            non-canonical projection.
            """,
        )
        # evidence.jsonl bleibt unverändert, referenziert measurement.yml.
        self.assertEqual(validate_repo(self.base), [])

    def test_run_yml_canonical_md_artifact_rejected(self) -> None:
        exp = _build_valid_bundle(self.base)
        run_dir = exp / "artifacts" / "run-001"
        _write(
            run_dir / "auditor-output.md",
            """
            ---
            canonical: false
            ---
            projection
            """,
        )
        # run.yml deklariert die Markdown-Projektion fälschlich als canonical=true
        _write(
            run_dir / "run.yml",
            """
            schema_version: "1.0.0"
            contract: "experiment_run_bundle"
            run:
              id: "run-001"
              experiment_path: "experiments/exp-fixture"
              created_at: "2026-05-01T12:00:00Z"
            provenance:
              level: "self_reported"
            artifacts:
              auditor_output:
                path: "auditor-output.yml"
                canonical: true
              measurement:
                path: "measurement.yml"
                canonical: true
              markdown_projection:
                path: "auditor-output.md"
                canonical: true
                role: "human_projection"
            verdict:
              outcome: "MISSING_EVIDENCE"
              effect_claim_allowed: false
            """,
        )
        errs = validate_repo(self.base)
        self.assertTrue(
            any("Markdown-Projektion" in e and "canonical" in e for e in errs),
            errs,
        )

    def test_auditor_pass_with_non_pass_claim_fails(self) -> None:
        exp = _build_valid_bundle(self.base)
        run_dir = exp / "artifacts" / "run-001"
        _write(
            run_dir / "auditor-output.yml",
            """
            schema_version: "1.0.0"
            contract: "auditor_output"
            run_id: "run-001"
            pr_ref: "github:test/test/pull/1"
            auditor: "x"
            overall_verdict: "PASS"
            claims:
              - id: c-1
                text: "x"
                type: "file_changed"
                verdict: "PASS"
                evidence: []
              - id: c-2
                text: "y"
                type: "validator_succeeded"
                verdict: "MISSING_EVIDENCE"
                evidence: []
            """,
        )
        # measurement zur Konsistenz halten, sonst mehrere Sekundärfehler.
        _write(
            run_dir / "measurement.yml",
            _valid_measurement_yml(auditor_verdict="PASS", unsupported=1, val_gap=1),
        )
        errs = validate_repo(self.base)
        self.assertTrue(any("PASS verlangt" in e for e in errs), errs)

    def test_auditor_severity_precedence_fail(self) -> None:
        exp = _build_valid_bundle(self.base)
        run_dir = exp / "artifacts" / "run-001"
        _write(
            run_dir / "auditor-output.yml",
            """
            schema_version: "1.0.0"
            contract: "auditor_output"
            run_id: "run-001"
            pr_ref: "github:test/test/pull/1"
            auditor: "x"
            overall_verdict: "MISSING_EVIDENCE"
            claims:
              - id: c-1
                text: "x"
                type: "file_changed"
                verdict: "CONTRADICTION"
                evidence: []
            """,
        )
        _write(
            run_dir / "measurement.yml",
            _valid_measurement_yml(auditor_verdict="MISSING_EVIDENCE", unsupported=1, val_gap=0),
        )
        errs = validate_repo(self.base)
        self.assertTrue(any("Severity-Precedence" in e for e in errs), errs)

    def test_measurement_unsupported_count_mismatch_fails(self) -> None:
        exp = _build_valid_bundle(self.base)
        run_dir = exp / "artifacts" / "run-001"
        # Auditor hat 2 non-PASS-Claims, measurement behauptet 5.
        _write(
            run_dir / "measurement.yml",
            _valid_measurement_yml(unsupported=5, val_gap=2),
        )
        errs = validate_repo(self.base)
        self.assertTrue(any("unsupported_claim_count" in e for e in errs), errs)

    def test_measurement_validation_gap_mismatch_fails(self) -> None:
        exp = _build_valid_bundle(self.base)
        run_dir = exp / "artifacts" / "run-001"
        # Auditor hat 2 validation gaps, measurement behauptet 0.
        _write(
            run_dir / "measurement.yml",
            _valid_measurement_yml(unsupported=2, val_gap=0),
        )
        errs = validate_repo(self.base)
        self.assertTrue(any("validation_gap_count" in e for e in errs), errs)

    def test_measurement_auditor_ref_missing_fails(self) -> None:
        exp = _build_valid_bundle(self.base)
        run_dir = exp / "artifacts" / "run-001"
        _write(
            run_dir / "measurement.yml",
            """
            schema_version: "1.0.0"
            contract: "measurement_run"
            run_id: "run-001"
            auditor_verdict: "MISSING_EVIDENCE"
            auditor_ref: "ghost.yml"
            metrics:
              scope_drift_count: { value: 0, evidence_status: "external_unverified" }
              unsupported_claim_count: { value: 2, evidence_status: "derived_from_auditor_output" }
              missing_locator_count: { value: 0, evidence_status: "external_unverified" }
              validation_gap_count: { value: 2, evidence_status: "derived_from_auditor_output" }
              review_friction_count: { value: 0, evidence_status: "external_unverified" }
              rework_count: { value: 0, evidence_status: "external_unverified" }
              false_block_count: { value: 0, evidence_status: "external_unverified" }
              task_completion_time_observed: { value: "n/a", evidence_status: "external_unverified" }
            """,
        )
        errs = validate_repo(self.base)
        self.assertTrue(any("ghost.yml" in e for e in errs), errs)

    def test_measurement_verdict_disagrees_with_auditor_fails(self) -> None:
        exp = _build_valid_bundle(self.base)
        run_dir = exp / "artifacts" / "run-001"
        _write(
            run_dir / "measurement.yml",
            _valid_measurement_yml(auditor_verdict="PASS", unsupported=2, val_gap=2),
        )
        errs = validate_repo(self.base)
        self.assertTrue(
            any("auditor_verdict" in e and "weicht" in e for e in errs),
            errs,
        )

    def test_run_yml_id_mismatch_fails(self) -> None:
        exp = _build_valid_bundle(self.base)
        run_dir = exp / "artifacts" / "run-001"
        _write(
            run_dir / "run.yml",
            """
            schema_version: "1.0.0"
            contract: "experiment_run_bundle"
            run:
              id: "run-002"
              experiment_path: "experiments/exp-fixture"
              created_at: "2026-05-01T12:00:00Z"
            provenance:
              level: "self_reported"
            artifacts:
              auditor_output:
                path: "auditor-output.yml"
                canonical: true
              measurement:
                path: "measurement.yml"
                canonical: true
            verdict:
              outcome: "MISSING_EVIDENCE"
              effect_claim_allowed: false
            """,
        )
        errs = validate_repo(self.base)
        self.assertTrue(any("run.id" in e for e in errs), errs)

    def test_run_yml_artifact_path_missing_fails(self) -> None:
        exp = _build_valid_bundle(self.base)
        run_dir = exp / "artifacts" / "run-001"
        _write(
            run_dir / "run.yml",
            """
            schema_version: "1.0.0"
            contract: "experiment_run_bundle"
            run:
              id: "run-001"
              experiment_path: "experiments/exp-fixture"
              created_at: "2026-05-01T12:00:00Z"
            provenance:
              level: "self_reported"
            artifacts:
              auditor_output:
                path: "auditor-output.yml"
                canonical: true
              measurement:
                path: "ghost-measurement.yml"
                canonical: true
            verdict:
              outcome: "MISSING_EVIDENCE"
              effect_claim_allowed: false
            """,
        )
        errs = validate_repo(self.base)
        self.assertTrue(any("ghost-measurement.yml" in e for e in errs), errs)


if __name__ == "__main__":
    unittest.main()
