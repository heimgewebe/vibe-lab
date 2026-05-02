#!/usr/bin/env python3
"""Regression tests for validate_run_bundle.py.

Each test builds a tiny experiment fixture under a temporary directory and
runs validate_repo() against it. Schemas are copied from the real project
into the tempdir so that validate_repo() is fully isolated — it must not
depend on the real REPO_ROOT.

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

# Schema filenames expected under <tempdir>/schemas/
_BUNDLE_SCHEMA = "experiment-run-bundle.v1.schema.json"
_AUDITOR_SCHEMA = "auditor-output.v1.schema.json"
_MEASUREMENT_SCHEMA = "measurement-run.v1.schema.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_repo_skeleton(base: Path) -> Path:
    """Creates base/schemas/ with all three bundle schemas, and base/experiments/.

    Tests run validate_repo(base) — schemas are loaded from base/schemas/, NOT
    from the real REPO_ROOT. This proves schema-path isolation.
    """
    schemas = base / "schemas"
    schemas.mkdir(parents=True, exist_ok=True)
    for name in (_BUNDLE_SCHEMA, _AUDITOR_SCHEMA, _MEASUREMENT_SCHEMA):
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


def _valid_manifest(execution_status: str = "executed", extra_refs: list[str] | None = None) -> str:
    base_refs = [
        "results/evidence.jsonl",
        "artifacts/run-001/run.yml",
    ]
    refs = base_refs + (extra_refs or [])
    ref_lines = "\n".join(f"        - {r}" for r in refs)
    return f"""
    schema_version: "0.1.0"
    experiment:
      name: "fixture"
      hypothesis: "h"
      status: testing
      category: workflow
      execution_status: {execution_status}
      execution_refs:
{ref_lines}
      created: "2026-05-01"
      updated: "2026-05-01"
      author: "test"
      iteration: 1
      evidence_level: anecdotal
    """


def _valid_evidence_run(artifact_ref: str = "artifacts/run-001/measurement.yml") -> str:
    return (
        '{"event_type":"run","timestamp":"2026-05-01T00:00:00Z","iteration":1,'
        f'"metric":"x","value":true,"context":"c",'
        f'"artifact_ref":"{artifact_ref}"}}\n'
    )


def _valid_run_yml(run_id: str = "run-001") -> str:
    return f"""
    schema_version: "1.0.0"
    contract: "experiment_run_bundle"
    run:
      id: "{run_id}"
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
    """Writes a fully valid bundle; returns the experiment directory."""
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

    def test_empty_is_pass(self) -> None:
        self.assertEqual(_compute_max_severity([]), "PASS")


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
        self.assertTrue(any("PASS verlangt" in e for e in errs), errs)

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
        meas = {"auditor_verdict": "PASS", "metrics": {}}
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

    # --- Passing cases ---

    def test_valid_executed_bundle_with_run_yml_in_refs_passes(self) -> None:
        """R2+R3+R8: valid executed run with run.yml listed in execution_refs."""
        _build_valid_bundle(self.base)
        self.assertEqual(validate_repo(self.base), [])

    def test_canonical_false_md_present_but_unreferenced_passes(self) -> None:
        exp = _build_valid_bundle(self.base)
        run_dir = exp / "artifacts" / "run-001"
        _write(
            run_dir / "auditor-output.md",
            "---\ncanonical: false\nsource_of_truth: false\n---\nprojection.\n",
        )
        self.assertEqual(validate_repo(self.base), [])

    def test_experiment_without_run_yml_legacy_md_ref_passes(self) -> None:
        """Legacy: experiments without run.yml may still reference .md artifact_refs.
        R4 Markdown block applies only to experiments with at least one run.yml."""
        exp = _exp_dir(self.base, "legacy-exp")
        _write(
            exp / "manifest.yml",
            """
            schema_version: "0.1.0"
            experiment:
              name: "legacy"
              hypothesis: "h"
              status: testing
              category: workflow
              execution_status: executed
              execution_refs:
                - results/evidence.jsonl
              created: "2026-04-01"
              updated: "2026-04-01"
              author: "test"
              iteration: 1
              evidence_level: anecdotal
            """,
        )
        # Create a .md artifact so the ref resolves.
        _write(exp / "artifacts" / "run-001-control.md", "# legacy artifact\n")
        _write(
            exp / "results" / "evidence.jsonl",
            '{"event_type":"run","timestamp":"2026-04-01T00:00:00Z","iteration":1,'
            '"metric":"x","value":true,"context":"c",'
            '"artifact_ref":"artifacts/run-001-control.md"}\n',
        )
        errs = validate_repo(self.base)
        # No run.yml in artifacts → R4 Markdown check not triggered → legacy OK.
        self.assertEqual(errs, [])

    # --- Schema isolation ---

    def test_schema_isolation_missing_bundle_schema_raises(self) -> None:
        """validate_repo() must load schemas from repo_root/schemas/, not REPO_ROOT.
        Deleting the bundle schema from the tempdir must cause FileNotFoundError."""
        _build_valid_bundle(self.base)
        (self.base / "schemas" / _BUNDLE_SCHEMA).unlink()
        with self.assertRaises(FileNotFoundError):
            validate_repo(self.base)

    def test_schema_isolation_missing_auditor_schema_raises(self) -> None:
        """Same as above for the auditor schema."""
        _build_valid_bundle(self.base)
        (self.base / "schemas" / _AUDITOR_SCHEMA).unlink()
        with self.assertRaises(FileNotFoundError):
            validate_repo(self.base)

    def test_schema_isolation_missing_measurement_schema_raises(self) -> None:
        """Same as above for the measurement schema."""
        _build_valid_bundle(self.base)
        (self.base / "schemas" / _MEASUREMENT_SCHEMA).unlink()
        with self.assertRaises(FileNotFoundError):
            validate_repo(self.base)

    # --- Drift 1 (R1): run event + prepared ---

    def test_run_event_with_prepared_status_fails(self) -> None:
        exp = _build_valid_bundle(self.base)
        _write(exp / "manifest.yml", _valid_manifest(execution_status="prepared"))
        errs = validate_repo(self.base)
        self.assertTrue(any("prepared" in e for e in errs), errs)

    # --- Drift 2 (R2/R3): execution_refs ---

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
        self.assertTrue(any("execution_refs ist leer" in e for e in errs), errs)

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
                - artifacts/run-001/run.yml
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

    # --- R8: run.yml in execution_refs ---

    def test_executed_experiment_with_run_yml_not_in_refs_fails(self) -> None:
        """R8: run.yml must appear in execution_refs."""
        exp = _build_valid_bundle(self.base)
        # Manifest without run.yml in execution_refs.
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
              created: "2026-05-01"
              updated: "2026-05-01"
              author: "test"
              iteration: 1
              evidence_level: anecdotal
            """,
        )
        errs = validate_repo(self.base)
        self.assertTrue(
            any("run.yml" in e and "execution_refs" in e for e in errs),
            errs,
        )

    # --- R4 (Markdown artifact_ref) ---

    def test_evidence_artifact_ref_to_md_without_frontmatter_fails(self) -> None:
        """R4: any .md artifact_ref in evidence.jsonl must fail, even without frontmatter."""
        exp = _build_valid_bundle(self.base)
        run_dir = exp / "artifacts" / "run-001"
        _write(run_dir / "plain.md", "# no frontmatter\n")
        _write(
            exp / "results" / "evidence.jsonl",
            '{"event_type":"run","timestamp":"2026-05-01T00:00:00Z","iteration":1,'
            '"metric":"x","value":true,"context":"c",'
            '"artifact_ref":"artifacts/run-001/plain.md"}\n',
        )
        errs = validate_repo(self.base)
        self.assertTrue(
            any("Markdown-Projektion" in e for e in errs),
            errs,
        )

    def test_evidence_artifact_ref_to_canonical_false_md_fails(self) -> None:
        """R4: .md with canonical:false must also fail (suffix check, not frontmatter check)."""
        exp = _build_valid_bundle(self.base)
        run_dir = exp / "artifacts" / "run-001"
        _write(
            run_dir / "auditor-output.md",
            "---\ncanonical: false\nsource_of_truth: false\n---\nprojection.\n",
        )
        _write(
            exp / "results" / "evidence.jsonl",
            '{"event_type":"run","timestamp":"2026-05-01T00:00:00Z","iteration":1,'
            '"metric":"x","value":true,"context":"c",'
            '"artifact_ref":"artifacts/run-001/auditor-output.md"}\n',
        )
        errs = validate_repo(self.base)
        self.assertTrue(any("Markdown-Projektion" in e for e in errs), errs)

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

    # --- R5: run.yml schema (deterministic artifact paths) ---

    def test_run_yml_wrong_auditor_output_path_fails(self) -> None:
        """R5: auditor_output.path must be exactly 'auditor-output.yml'."""
        exp = _build_valid_bundle(self.base)
        run_dir = exp / "artifacts" / "run-001"
        _write(run_dir / "custom-auditor.yml", "schema_version: '1.0.0'\ncontract: auditor_output\n")
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
                path: "custom-auditor.yml"
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
        self.assertTrue(any("schema-invalid" in e for e in errs), errs)

    def test_run_yml_wrong_measurement_path_fails(self) -> None:
        """R5: measurement.path must be exactly 'measurement.yml'."""
        exp = _build_valid_bundle(self.base)
        run_dir = exp / "artifacts" / "run-001"
        _write(run_dir / "my-measurement.yml", "schema_version: '1.0.0'\ncontract: measurement_run\n")
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
                path: "my-measurement.yml"
                canonical: true
            verdict:
              outcome: "MISSING_EVIDENCE"
              effect_claim_allowed: false
            """,
        )
        errs = validate_repo(self.base)
        self.assertTrue(any("schema-invalid" in e for e in errs), errs)

    def test_run_yml_markdown_projection_without_canonical_false_fails(self) -> None:
        """R5: markdown_projection must have canonical:false (schema-enforced)."""
        exp = _build_valid_bundle(self.base)
        run_dir = exp / "artifacts" / "run-001"
        _write(run_dir / "auditor-output.md", "---\n---\nprojection.\n")
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
                role: "human_projection"
            verdict:
              outcome: "MISSING_EVIDENCE"
              effect_claim_allowed: false
            """,
        )
        errs = validate_repo(self.base)
        # schema-invalid because markdown_projection.canonical is required and must be false.
        self.assertTrue(any("schema-invalid" in e for e in errs), errs)

    def test_run_yml_canonical_md_artifact_rejected(self) -> None:
        """R5: canonical:true on a Markdown file is rejected by the validator."""
        exp = _build_valid_bundle(self.base)
        run_dir = exp / "artifacts" / "run-001"
        _write(run_dir / "auditor-output.md", "---\ncanonical: false\n---\nprojection\n")
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
        # Schema rejects markdown_projection.canonical=true (must be false).
        self.assertTrue(any("schema-invalid" in e for e in errs), errs)

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
        # Overwrite with measurement pointing to a non-existent file.
        # We need to use run_meta since measurement.path is now const-enforced to measurement.yml
        # and that file exists. Use a custom key.
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
              run_meta:
                path: "run_meta.json"
                canonical: false
                compatibility: true
            verdict:
              outcome: "MISSING_EVIDENCE"
              effect_claim_allowed: false
            """,
        )
        # run_meta.json does NOT exist in the run dir.
        errs = validate_repo(self.base)
        self.assertTrue(any("run_meta.json" in e and "existiert nicht" in e for e in errs), errs)

    # --- R6: auditor semantics ---

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

    # --- R7: measurement semantics ---

    def test_measurement_unsupported_count_mismatch_fails(self) -> None:
        exp = _build_valid_bundle(self.base)
        run_dir = exp / "artifacts" / "run-001"
        # Auditor has 2 non-PASS; measurement claims 5.
        _write(run_dir / "measurement.yml", _valid_measurement_yml(unsupported=5, val_gap=2))
        errs = validate_repo(self.base)
        self.assertTrue(any("unsupported_claim_count" in e for e in errs), errs)

    def test_measurement_validation_gap_mismatch_fails(self) -> None:
        exp = _build_valid_bundle(self.base)
        run_dir = exp / "artifacts" / "run-001"
        # Auditor has 2 command/validator gaps; measurement claims 0.
        _write(run_dir / "measurement.yml", _valid_measurement_yml(unsupported=2, val_gap=0))
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

    # --- Real Run 1 integrity ---

    def test_real_run1_remains_structurally_valid(self) -> None:
        """Run 1 of the agent-skill experiment must pass all bundle checks."""
        errs = validate_repo(REPO_ROOT)
        self.assertEqual(
            errs,
            [],
            f"Real Run 1 bundle failed validation:\n" + "\n".join(errs),
        )


if __name__ == "__main__":
    unittest.main()
