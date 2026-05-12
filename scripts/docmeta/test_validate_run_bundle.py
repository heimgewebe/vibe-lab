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
import validate_run_bundle as _vrb  # noqa: E402  (for last_warnings access after reload)


REPO_ROOT = THIS_DIR.parent.parent
PROJECT_SCHEMAS = REPO_ROOT / "schemas"

# Schema filenames expected under <tempdir>/schemas/
_BUNDLE_SCHEMA = "experiment-run-bundle.v1.schema.json"
_AUDITOR_SCHEMA = "auditor-output.v1.schema.json"
_MEASUREMENT_SCHEMA = "measurement-run.v1.schema.json"
_EVIDENCE_PACK_SCHEMA = "run-evidence-pack.v1.schema.json"
_REVIEW_EVENTS_SCHEMA = "review-events.v1.schema.json"
_LEGACY_EVIDENCE_PACK_BASELINE = "run-bundle-evidence-pack-legacy.yml"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_repo_skeleton(base: Path) -> Path:
    """Creates base/schemas/ with all five bundle schemas, and base/experiments/.

    Tests run validate_repo(base) — schemas are loaded from base/schemas/, NOT
    from the real REPO_ROOT. This proves schema-path isolation.
    """
    schemas = base / "schemas"
    schemas.mkdir(parents=True, exist_ok=True)
    for name in (
        _BUNDLE_SCHEMA,
        _AUDITOR_SCHEMA,
        _MEASUREMENT_SCHEMA,
        _EVIDENCE_PACK_SCHEMA,
        _REVIEW_EVENTS_SCHEMA,
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


def _write_legacy_allowlist(base: Path, paths: list[str]) -> None:
    lines = [
        'schema_version: "1.0.0"',
        "allowed_missing_evidence_pack:",
    ]
    if paths:
        for p in paths:
            lines.append(f'  - path: "{p}"')
            lines.append('    reason: "legacy bundle predates PR-6 evidence-pack coupling"')
    else:
        lines[-1] = "allowed_missing_evidence_pack: []"

    _write(
        base / ".vibe" / _LEGACY_EVIDENCE_PACK_BASELINE,
        "\n".join(lines) + "\n",
    )


def _valid_manifest(
    execution_status: str = "executed",
    extra_refs: list[str] | None = None,
    *,
    run_id: str = "run-001",
) -> str:
    base_refs = [
        "results/evidence.jsonl",
        f"artifacts/{run_id}/run.yml",
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


def _valid_run_yml(
    run_id: str = "run-001",
    *,
    experiment_path: str = "experiments/exp-fixture",
    created_at: str = "2026-05-01T12:00:00Z",
    sequence: int | None = 1,
) -> str:
    sequence_block = ""
    if sequence is not None:
        sequence_block = f"\n      sequence: {sequence}"

    return f"""
    schema_version: "1.0.0"
    contract: "experiment_run_bundle"
    run:
      id: "{run_id}"
      experiment_path: "{experiment_path}"
      created_at: "{created_at}"{sequence_block}
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
      run_meta:
        path: "run_meta.json"
        contract: "run_meta"
        canonical: false
        compatibility: true
    verdict:
      outcome: "MISSING_EVIDENCE"
      effect_claim_allowed: false
    """


def _valid_run_meta_json(run_id: str = "run-001") -> str:
    return json.dumps({
        "schema_version": "0.1.0",
        "run_id": run_id,
        "generated_at": "2026-05-01T12:00:00Z",
        "executor": "local:test",
        "outcome": "MISSING_EVIDENCE",
    })


def _valid_auditor_yml(run_id: str = "run-001") -> str:
    return f"""
    schema_version: "1.0.0"
    contract: "auditor_output"
    run_id: "{run_id}"
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
    run_id: str = "run-001",
    auditor_verdict: str = "MISSING_EVIDENCE",
    unsupported: int = 2,
    val_gap: int = 2,
    scope_drift_value: object = 0,
    scope_drift_evidence_status: str = "external_unverified",
    scope_drift_notes: str | None = "scope drift note",
    missing_evidence_items: list[tuple[str, str]] | None = None,
) -> str:
    lines = [
        'schema_version: "1.0.0"',
        'contract: "measurement_run"',
        f'run_id: "{run_id}"',
        f'auditor_verdict: "{auditor_verdict}"',
        'auditor_ref: "auditor-output.yml"',
        'metrics:',
        '  scope_drift_count:',
        f'    value: {json.dumps(scope_drift_value)}',
        f'    evidence_status: "{scope_drift_evidence_status}"',
    ]
    if scope_drift_notes is not None:
        lines.append(f'    notes: {json.dumps(scope_drift_notes)}')
    lines.extend([
        '  unsupported_claim_count:',
        f'    value: {unsupported}',
        '    evidence_status: "derived_from_auditor_output"',
        '  missing_locator_count:',
        '    value: 0',
        '    evidence_status: "external_unverified"',
        '  validation_gap_count:',
        f'    value: {val_gap}',
        '    evidence_status: "derived_from_auditor_output"',
        '  review_friction_count:',
        '    value: 0',
        '    evidence_status: "external_unverified"',
        '  rework_count:',
        '    value: 0',
        '    evidence_status: "external_unverified"',
        '  false_block_count:',
        '    value: 0',
        '    evidence_status: "external_unverified"',
        '  task_completion_time_observed:',
        '    value: "n/a"',
        '    evidence_status: "external_unverified"',
    ])
    if missing_evidence_items:
        lines.append('missing_evidence:')
        for item, detail in missing_evidence_items:
            lines.append(f'  - item: {json.dumps(item)}')
            lines.append(f'    detail: {json.dumps(detail)}')
    lines.append('')
    return "\n".join(lines)


def _valid_comparability_yml(
    *,
    run_id: str = "run-001",
    verdict: str = "comparable",
    changed_files_artifact: str | None = "changed-files.txt",
    compared_against: str | None = "run-000",
    missing_changed_files_reason: str | None = None,
) -> str:
    lines = [
        'schema_version: "1.0.0"',
        'contract: "run_comparability_assessment"',
        f'run_id: "{run_id}"',
        'assessed_at: "2026-05-08"',
        '',
        f"compared_against: {json.dumps(compared_against)}" if compared_against is not None else 'compared_against: null',
        '',
        'same_experiment_path: true',
        'same_metric_structure: true',
        'same_claim_evidence_discipline: true',
        '',
        'independent_task_or_pr_ref: "PR#test"',
        '',
        f"changed_files_artifact: {json.dumps(changed_files_artifact)}" if changed_files_artifact is not None else 'changed_files_artifact: null',
        '',
        f'verdict: "{verdict}"',
    ]
    if missing_changed_files_reason is not None:
        lines.append(
            f"missing_changed_files_reason: {json.dumps(missing_changed_files_reason)}"
        )
    lines.extend([
        '',
        'notes: "fixture comparability"',
        '',
    ])
    return "\n".join(lines)


def _run_yml_repo_path(exp_name: str, run_id: str) -> str:
    return f"experiments/{exp_name}/artifacts/{run_id}/run.yml"


def _write_changed_files_artifact(run_dir: Path, name: str = "changed-files.txt") -> None:
    _write(
        run_dir / name,
        """
        # Changed Files
        measurement.yml [modify]
        comparability.yml [modify]
        """,
    )


def _build_valid_bundle(
    base: Path,
    *,
    exp_name: str = "exp-fixture",
    run_id: str = "run-001",
    run_created_at: str = "2026-05-01T12:00:00Z",
    sequence: int | None = 1,
    measurement_text: str | None = None,
    comparability_text: str | None = None,
) -> Path:
    """Writes a fully valid bundle; returns the experiment directory."""
    exp = _exp_dir(base, exp_name)
    _write(exp / "manifest.yml", _valid_manifest(run_id=run_id))
    _write(
        exp / "results" / "evidence.jsonl",
        _valid_evidence_run(artifact_ref=f"artifacts/{run_id}/measurement.yml"),
    )
    run_dir = exp / "artifacts" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    _write(
        run_dir / "run.yml",
        _valid_run_yml(
            run_id=run_id,
            experiment_path=f"experiments/{exp_name}",
            created_at=run_created_at,
            sequence=sequence,
        ),
    )
    _write(run_dir / "auditor-output.yml", _valid_auditor_yml(run_id=run_id))
    _write(
        run_dir / "measurement.yml",
        measurement_text or _valid_measurement_yml(run_id=run_id),
    )
    if comparability_text is not None:
        _write(run_dir / "comparability.yml", comparability_text)
    (run_dir / "run_meta.json").write_text(_valid_run_meta_json(run_id=run_id), encoding="utf-8")
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
        _write_legacy_allowlist(self.base, ["experiments/exp-fixture/artifacts/run-001/run.yml"])
        self.assertEqual(validate_repo(self.base), [])

    def test_canonical_false_md_present_but_unreferenced_passes(self) -> None:
        exp = _build_valid_bundle(self.base)
        _write_legacy_allowlist(self.base, ["experiments/exp-fixture/artifacts/run-001/run.yml"])
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

    def test_not_comparable_without_changed_files_passes_with_reason(self) -> None:
        _build_valid_bundle(
            self.base,
            measurement_text=_valid_measurement_yml(
                scope_drift_value=None,
                scope_drift_evidence_status="missing_evidence",
                scope_drift_notes="Changed-files artifact deliberately not archived.",
            ),
            comparability_text=_valid_comparability_yml(
                verdict="not_comparable",
                changed_files_artifact=None,
                missing_changed_files_reason="Candidate run without archived changed-files evidence.",
            ),
        )
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        self.assertEqual(validate_repo(self.base), [])

    def test_comparable_with_existing_changed_files_artifact_passes(self) -> None:
        exp = _build_valid_bundle(
            self.base,
            comparability_text=_valid_comparability_yml(
                verdict="comparable",
                changed_files_artifact="changed-files.txt",
            ),
        )
        _write_changed_files_artifact(exp / "artifacts" / "run-001")
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        self.assertEqual(validate_repo(self.base), [])

    def test_comparable_with_experiment_relative_changed_files_artifact_passes(self) -> None:
        exp = _build_valid_bundle(
            self.base,
            comparability_text=_valid_comparability_yml(
                verdict="comparable",
                changed_files_artifact="artifacts/run-001/changed-files.txt",
            ),
        )
        _write_changed_files_artifact(exp / "artifacts" / "run-001")
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        self.assertEqual(validate_repo(self.base), [])

    def test_grandfathered_run_002_reference_only_without_changed_files_and_scope_drift_claim_passes(self) -> None:
        exp_name = "2026-05-01_agent-skill-minimal-layer-instrumentation"
        run_id = "run-002-controlled-agent-skill-run"
        _build_valid_bundle(
            self.base,
            exp_name=exp_name,
            run_id=run_id,
            run_created_at="2026-05-06T12:00:00Z",
            sequence=2,
            measurement_text=_valid_measurement_yml(
                run_id=run_id,
                scope_drift_value=0,
                scope_drift_evidence_status="repo_local",
            ),
            comparability_text=_valid_comparability_yml(
                run_id=run_id,
                verdict="reference_only",
                changed_files_artifact=None,
                compared_against=None,
            ),
        )
        _write_legacy_allowlist(self.base, [_run_yml_repo_path(exp_name, run_id)])
        self.assertEqual(validate_repo(self.base), [])

    def test_grandfathered_run_002_comparable_without_changed_files_fails(self) -> None:
        exp_name = "2026-05-01_agent-skill-minimal-layer-instrumentation"
        run_id = "run-002-controlled-agent-skill-run"
        _build_valid_bundle(
            self.base,
            exp_name=exp_name,
            run_id=run_id,
            run_created_at="2026-05-06T12:00:00Z",
            sequence=2,
            comparability_text=_valid_comparability_yml(
                run_id=run_id,
                verdict="comparable",
                changed_files_artifact=None,
                compared_against=None,
            ),
        )
        _write_legacy_allowlist(self.base, [_run_yml_repo_path(exp_name, run_id)])
        errs = validate_repo(self.base)
        self.assertTrue(any("verdict='comparable'" in e for e in errs), errs)

    def test_run_created_after_changed_files_contract_without_comparability_fails(self) -> None:
        run_id = "run-post-contract"
        _build_valid_bundle(
            self.base,
            run_id=run_id,
            run_created_at="2026-05-08T00:00:00Z",
            sequence=1,
        )
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", run_id)])
        errs = validate_repo(self.base)
        self.assertTrue(any("Comparability-Bewertung benötigt" in e for e in errs), errs)

    def test_not_comparable_without_reason_fails(self) -> None:
        _build_valid_bundle(
            self.base,
            measurement_text=_valid_measurement_yml(
                scope_drift_value=None,
                scope_drift_evidence_status="missing_evidence",
                scope_drift_notes="Changed-files artifact deliberately not archived.",
            ),
            comparability_text=_valid_comparability_yml(
                verdict="not_comparable",
                changed_files_artifact=None,
                missing_changed_files_reason=None,
            ),
        )
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertTrue(any("missing_changed_files_reason" in e for e in errs), errs)

    def test_comparable_without_changed_files_artifact_fails(self) -> None:
        _build_valid_bundle(
            self.base,
            comparability_text=_valid_comparability_yml(
                verdict="comparable",
                changed_files_artifact=None,
            ),
        )
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertTrue(any("verdict='comparable'" in e for e in errs), errs)

    def test_reference_only_without_changed_files_artifact_fails_for_non_grandfathered_run(self) -> None:
        run_id = "run-003-controlled-agent-skill-run"
        _build_valid_bundle(
            self.base,
            run_id=run_id,
            comparability_text=_valid_comparability_yml(
                run_id=run_id,
                verdict="reference_only",
                changed_files_artifact=None,
            ),
        )
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", run_id)])
        errs = validate_repo(self.base)
        self.assertTrue(any("verdict='reference_only'" in e for e in errs), errs)

    def test_sequence_three_run_without_comparability_fails(self) -> None:
        exp_name = "2026-05-01_agent-skill-minimal-layer-instrumentation"
        run_id = "run-003-controlled-agent-skill-run"
        _build_valid_bundle(
            self.base,
            exp_name=exp_name,
            run_id=run_id,
            run_created_at="2026-05-07T12:00:00Z",
            sequence=3,
        )
        _write_legacy_allowlist(self.base, [_run_yml_repo_path(exp_name, run_id)])
        errs = validate_repo(self.base)
        self.assertTrue(any("Comparability-Bewertung benötigt" in e for e in errs), errs)

    def test_scope_drift_value_zero_without_changed_files_artifact_fails(self) -> None:
        _build_valid_bundle(
            self.base,
            comparability_text=_valid_comparability_yml(
                verdict="comparable",
                changed_files_artifact=None,
            ),
        )
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertTrue(any("scope_drift_count.value=0" in e for e in errs), errs)

    def test_scope_drift_repo_local_without_changed_files_artifact_fails(self) -> None:
        _build_valid_bundle(
            self.base,
            measurement_text=_valid_measurement_yml(
                scope_drift_value=0,
                scope_drift_evidence_status="repo_local",
            ),
            comparability_text=_valid_comparability_yml(
                verdict="comparable",
                changed_files_artifact=None,
            ),
        )
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertTrue(any("evidence_status=repo_local" in e for e in errs), errs)

    def test_scope_drift_null_with_wrong_evidence_status_fails(self) -> None:
        _build_valid_bundle(
            self.base,
            measurement_text=_valid_measurement_yml(
                scope_drift_value=None,
                scope_drift_evidence_status="external_unverified",
                scope_drift_notes="Reason is present but evidence_status is wrong.",
            ),
            comparability_text=_valid_comparability_yml(
                verdict="not_comparable",
                changed_files_artifact=None,
                missing_changed_files_reason="Candidate run without archived changed-files evidence.",
            ),
        )
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertTrue(any("evidence_status=missing_evidence" in e for e in errs), errs)

    def test_missing_changed_files_artifact_target_fails(self) -> None:
        _build_valid_bundle(
            self.base,
            comparability_text=_valid_comparability_yml(
                verdict="comparable",
                changed_files_artifact="ghost.txt",
            ),
        )
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertTrue(any("ghost.txt" in e and "existierende Datei" in e for e in errs), errs)

    def test_changed_files_artifact_pointing_to_other_run_fails(self) -> None:
        exp = _build_valid_bundle(
            self.base,
            comparability_text=_valid_comparability_yml(
                verdict="comparable",
                changed_files_artifact="artifacts/other-run/changed-files.txt",
            ),
        )
        _write_changed_files_artifact(exp / "artifacts" / "other-run")
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertTrue(any("muss run-lokal oder experiment-relativ auf dieses Run-Verzeichnis zeigen" in e for e in errs), errs)

    def test_changed_files_artifact_pointing_to_previous_run_directory_fails(self) -> None:
        # Regression: run-006 comparability.yml must not reference run-005's
        # changed-files.txt even when that file physically exists in the repo.
        current_run = "run-006-controlled-agent-skill-run"
        previous_run = "run-005-controlled-agent-skill-run"
        exp = _build_valid_bundle(
            self.base,
            run_id=current_run,
            comparability_text=_valid_comparability_yml(
                run_id=current_run,
                verdict="comparable",
                changed_files_artifact=f"artifacts/{previous_run}/changed-files.txt",
            ),
        )
        _write_changed_files_artifact(exp / "artifacts" / previous_run)
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", current_run)])
        errs = validate_repo(self.base)
        self.assertTrue(any("muss run-lokal oder experiment-relativ auf dieses Run-Verzeichnis zeigen" in e for e in errs), errs)

    def test_changed_files_artifact_parent_escape_fails(self) -> None:
        _build_valid_bundle(
            self.base,
            comparability_text=_valid_comparability_yml(
                verdict="comparable",
                changed_files_artifact="../ghost.txt",
            ),
        )
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertTrue(
          any(
            "muss run-lokal oder experiment-relativ auf dieses Run-Verzeichnis zeigen"
            in e
            for e in errs
          ),
          errs,
        )

    def test_changed_files_artifact_absolute_path_fails(self) -> None:
        _build_valid_bundle(
            self.base,
            comparability_text=_valid_comparability_yml(
                verdict="comparable",
                changed_files_artifact="/tmp/changed-files.txt",
            ),
        )
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertTrue(any("kein absoluter Pfad" in e for e in errs), errs)

    def test_changed_files_artifact_windows_absolute_path_fails(self) -> None:
        _build_valid_bundle(
            self.base,
            comparability_text=_valid_comparability_yml(
                verdict="comparable",
                changed_files_artifact="C:/temp/changed-files.txt",
            ),
        )
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertTrue(any("kein absoluter Pfad" in e for e in errs), errs)

    def test_changed_files_artifact_empty_string_fails(self) -> None:
        _build_valid_bundle(
            self.base,
            comparability_text=_valid_comparability_yml(
                verdict="comparable",
                changed_files_artifact="",
            ),
        )
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertTrue(any("leerer String" in e for e in errs), errs)

    def test_invalid_comparability_yaml_does_not_emit_missing_message(self) -> None:
        exp = _build_valid_bundle(self.base)
        _write(exp / "artifacts" / "run-001" / "comparability.yml", "verdict: [\n")
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertTrue(any("comparability.yml: YAML-Fehler" in e for e in errs), errs)
        self.assertFalse(any("comparability.yml: fehlt" in e for e in errs), errs)

    def test_invalid_comparability_yaml_with_repo_local_scope_drift_emits_no_missing_hint(self) -> None:
        exp = _build_valid_bundle(
            self.base,
            measurement_text=_valid_measurement_yml(
                scope_drift_value=0,
                scope_drift_evidence_status="repo_local",
            ),
        )
        _write(exp / "artifacts" / "run-001" / "comparability.yml", "verdict: [\n")
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertTrue(any("comparability.yml: YAML-Fehler" in e for e in errs), errs)
        self.assertFalse(
            any(
                "scope_drift_count.evidence_status=repo_local erfordert comparability.yml mit gültigem changed_files_artifact"
                in e
                for e in errs
            ),
            errs,
        )

    def test_non_object_comparability_yaml_does_not_emit_missing_message(self) -> None:
        exp = _build_valid_bundle(self.base)
        _write(exp / "artifacts" / "run-001" / "comparability.yml", "- comparable\n")
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertTrue(any("Datei muss ein YAML-Objekt sein" in e for e in errs), errs)
        self.assertFalse(any("comparability.yml: fehlt" in e for e in errs), errs)

    def test_missing_evidence_fixture_yaml_remains_valid(self) -> None:
        _build_valid_bundle(
            self.base,
            measurement_text=_valid_measurement_yml(
                scope_drift_value=None,
                scope_drift_evidence_status="missing_evidence",
                scope_drift_notes=None,
                missing_evidence_items=[("scope_drift_count", "No changed-files artifact archived.")],
            ),
            comparability_text=_valid_comparability_yml(
                verdict="not_comparable",
                changed_files_artifact=None,
                missing_changed_files_reason="Candidate run without archived changed-files evidence.",
            ),
        )
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        self.assertEqual(validate_repo(self.base), [])

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
            any("does-not-exist.yml" in e and ("existiert nicht" in e or "Datei" in e) for e in errs),
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
                contract: "auditor_output"
                canonical: true
              measurement:
                path: "measurement.yml"
                contract: "measurement_run"
                canonical: true
              run_meta:
                path: "run_meta.json"
                contract: "run_meta"
                canonical: false
                compatibility: true
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
        # Delete run_meta.json so the artifact ref in run.yml points to a missing file.
        (run_dir / "run_meta.json").unlink()
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
        # Schema const enforces auditor_ref="auditor-output.yml"; any other value is schema-invalid.
        self.assertTrue(any("measurement.yml" in e for e in errs), errs)

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

    # --- Phase 3: required bundle members (schema-enforced) ---

    def test_run_yml_missing_required_run_meta_artifact_fails(self) -> None:
        """run.yml without run_meta in artifacts is schema-invalid (required: [auditor_output, measurement, run_meta])."""
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
                path: "measurement.yml"
                canonical: true
            verdict:
              outcome: "MISSING_EVIDENCE"
              effect_claim_allowed: false
            """,
        )
        errs = validate_repo(self.base)
        self.assertTrue(any("schema-invalid" in e for e in errs), errs)

    # --- Phase 3: run_id cross-checks ---

    def test_auditor_run_id_mismatch_fails(self) -> None:
        """auditor-output.yml run_id must match run.yml run.id."""
        exp = _build_valid_bundle(self.base)
        run_dir = exp / "artifacts" / "run-001"
        _write(
            run_dir / "auditor-output.yml",
            """
            schema_version: "1.0.0"
            contract: "auditor_output"
            run_id: "wrong-run-id"
            auditor: "test-auditor"
            overall_verdict: "MISSING_EVIDENCE"
            claims:
              - id: "c-1"
                text: "claim"
                type: "file_changed"
                verdict: "MISSING_EVIDENCE"
                evidence: []
            """,
        )
        _write(run_dir / "measurement.yml", _valid_measurement_yml(unsupported=1, val_gap=0))
        errs = validate_repo(self.base)
        self.assertTrue(
            any("auditor-output.yml" in e and "run_id" in e and "wrong-run-id" in e for e in errs),
            errs,
        )

    def test_measurement_run_id_mismatch_fails(self) -> None:
        """measurement.yml run_id must match run.yml run.id."""
        exp = _build_valid_bundle(self.base)
        run_dir = exp / "artifacts" / "run-001"
        _write(
            run_dir / "measurement.yml",
            """
            schema_version: "1.0.0"
            contract: "measurement_run"
            run_id: "wrong-run-id"
            auditor_verdict: "MISSING_EVIDENCE"
            auditor_ref: "auditor-output.yml"
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
        self.assertTrue(
            any("measurement.yml" in e and "run_id" in e and "wrong-run-id" in e for e in errs),
            errs,
        )

    def test_run_meta_run_id_mismatch_fails(self) -> None:
        """run_meta.json run_id must match run.yml run.id."""
        exp = _build_valid_bundle(self.base)
        run_dir = exp / "artifacts" / "run-001"
        (run_dir / "run_meta.json").write_text(
            json.dumps({"schema_version": "0.1.0", "run_id": "wrong-run-id"}),
            encoding="utf-8",
        )
        errs = validate_repo(self.base)
        self.assertTrue(
            any("run_meta.json" in e and "run_id" in e and "wrong-run-id" in e for e in errs),
            errs,
        )

    # --- Phase 3: verdict cross-check ---

    def test_bundle_verdict_mismatch_with_auditor_fails(self) -> None:
        """run.yml verdict.outcome must match auditor-output.yml overall_verdict."""
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
                contract: "auditor_output"
                canonical: true
              measurement:
                path: "measurement.yml"
                contract: "measurement_run"
                canonical: true
              run_meta:
                path: "run_meta.json"
                contract: "run_meta"
                canonical: false
                compatibility: true
            verdict:
              outcome: "PASS"
              effect_claim_allowed: false
            """,
        )
        errs = validate_repo(self.base)
        self.assertTrue(
            any("verdict.outcome" in e and "PASS" in e for e in errs),
            errs,
        )

    # --- Phase 3: additionalProperties:false (schema-enforced) ---

    def test_unknown_field_in_auditor_output_fails(self) -> None:
        """Unknown top-level field in auditor-output.yml is rejected (additionalProperties:false)."""
        exp = _build_valid_bundle(self.base)
        run_dir = exp / "artifacts" / "run-001"
        _write(
            run_dir / "auditor-output.yml",
            """
            schema_version: "1.0.0"
            contract: "auditor_output"
            run_id: "run-001"
            auditor: "test-auditor"
            overall_verdict: "MISSING_EVIDENCE"
            unknown_drift_field: "should be rejected"
            claims:
              - id: "c-1"
                text: "claim"
                type: "file_changed"
                verdict: "MISSING_EVIDENCE"
                evidence: []
            """,
        )
        errs = validate_repo(self.base)
        self.assertTrue(any("schema-invalid" in e for e in errs), errs)

    def test_unknown_field_in_measurement_fails(self) -> None:
        """Unknown top-level field in measurement.yml is rejected (additionalProperties:false)."""
        exp = _build_valid_bundle(self.base)
        run_dir = exp / "artifacts" / "run-001"
        _write(
            run_dir / "measurement.yml",
            """
            schema_version: "1.0.0"
            contract: "measurement_run"
            run_id: "run-001"
            auditor_verdict: "MISSING_EVIDENCE"
            auditor_ref: "auditor-output.yml"
            unknown_drift_field: "should be rejected"
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
        self.assertTrue(any("schema-invalid" in e for e in errs), errs)

    # --- Hardening v1: missing mandatory artifacts ---

    def test_run_yml_missing_required_auditor_output_artifact_fails(self) -> None:
        """run.yml without auditor_output is schema-invalid (required field)."""
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
              measurement:
                path: "measurement.yml"
                contract: "measurement_run"
                canonical: true
              run_meta:
                path: "run_meta.json"
                contract: "run_meta"
                canonical: false
                compatibility: true
            verdict:
              outcome: "MISSING_EVIDENCE"
              effect_claim_allowed: false
            """,
        )
        errs = validate_repo(self.base)
        self.assertTrue(any("schema-invalid" in e for e in errs), errs)

    def test_run_yml_missing_required_measurement_artifact_fails(self) -> None:
        """run.yml without measurement is schema-invalid (required field)."""
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
                contract: "auditor_output"
                canonical: true
              run_meta:
                path: "run_meta.json"
                contract: "run_meta"
                canonical: false
                compatibility: true
            verdict:
              outcome: "MISSING_EVIDENCE"
              effect_claim_allowed: false
            """,
        )
        errs = validate_repo(self.base)
        self.assertTrue(any("schema-invalid" in e for e in errs), errs)

    # --- Hardening v1: no unknown artifact keys allowed ---

    def test_run_yml_extra_artifact_key_fails(self) -> None:
        """additionalProperties:false on artifacts rejects any unknown artifact key."""
        exp = _build_valid_bundle(self.base)
        run_dir = exp / "artifacts" / "run-001"
        _write(run_dir / "extra.yml", "schema_version: '1.0.0'\n")
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
                contract: "auditor_output"
                canonical: true
              measurement:
                path: "measurement.yml"
                contract: "measurement_run"
                canonical: true
              run_meta:
                path: "run_meta.json"
                contract: "run_meta"
                canonical: false
                compatibility: true
              extra_artifact:
                path: "extra.yml"
                canonical: false
            verdict:
              outcome: "MISSING_EVIDENCE"
              effect_claim_allowed: false
            """,
        )
        errs = validate_repo(self.base)
        self.assertTrue(any("schema-invalid" in e for e in errs), errs)

    # --- Hardening v1: markdown_projection role + path constraints ---

    def test_run_yml_markdown_projection_wrong_role_fails(self) -> None:
        """markdown_projection.role must be 'human_projection' (const-enforced)."""
        exp = _build_valid_bundle(self.base)
        run_dir = exp / "artifacts" / "run-001"
        _write(run_dir / "projection.md", "# projection\n")
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
                contract: "auditor_output"
                canonical: true
              measurement:
                path: "measurement.yml"
                contract: "measurement_run"
                canonical: true
              run_meta:
                path: "run_meta.json"
                contract: "run_meta"
                canonical: false
                compatibility: true
              markdown_projection:
                path: "projection.md"
                canonical: false
                role: "summary"
            verdict:
              outcome: "MISSING_EVIDENCE"
              effect_claim_allowed: false
            """,
        )
        errs = validate_repo(self.base)
        self.assertTrue(any("schema-invalid" in e for e in errs), errs)

    def test_run_yml_markdown_projection_non_md_path_fails(self) -> None:
        """markdown_projection.path must match .*\\.md$ pattern (schema-enforced)."""
        exp = _build_valid_bundle(self.base)
        run_dir = exp / "artifacts" / "run-001"
        _write(run_dir / "projection.html", "<p>projection</p>\n")
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
                contract: "auditor_output"
                canonical: true
              measurement:
                path: "measurement.yml"
                contract: "measurement_run"
                canonical: true
              run_meta:
                path: "run_meta.json"
                contract: "run_meta"
                canonical: false
                compatibility: true
              markdown_projection:
                path: "projection.html"
                canonical: false
                role: "human_projection"
            verdict:
              outcome: "MISSING_EVIDENCE"
              effect_claim_allowed: false
            """,
        )
        errs = validate_repo(self.base)
        self.assertTrue(any("schema-invalid" in e for e in errs), errs)

    # --- Hardening v1: artifact path run_dir containment ---

    def test_run_yml_markdown_projection_path_escaping_run_dir_fails(self) -> None:
        """markdown_projection.path cannot reference files outside the run directory."""
        exp = _build_valid_bundle(self.base)
        run_dir = exp / "artifacts" / "run-001"
        # Create a .md target outside run_dir (still within artifacts/) so path resolves.
        outside_md = exp / "artifacts" / "outside.md"
        outside_md.write_text("# outside run dir\n", encoding="utf-8")
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
                contract: "auditor_output"
                canonical: true
              measurement:
                path: "measurement.yml"
                contract: "measurement_run"
                canonical: true
              run_meta:
                path: "run_meta.json"
                contract: "run_meta"
                canonical: false
                compatibility: true
              markdown_projection:
                path: "../outside.md"
                canonical: false
                role: "human_projection"
            verdict:
              outcome: "MISSING_EVIDENCE"
              effect_claim_allowed: false
            """,
        )
        errs = validate_repo(self.base)
        self.assertTrue(
            any("verlässt das Run-Verzeichnis" in e for e in errs),
            errs,
        )

    # --- Fix 1: all-PASS auditor semantics ---

    def test_auditor_all_claims_pass_but_overall_non_pass_fails(self) -> None:
        """_check_auditor_semantics must reject overall_verdict != PASS when all claims are PASS."""
        auditor = {
            "overall_verdict": "MISSING_EVIDENCE",
            "claims": [
                {"verdict": "PASS"},
                {"verdict": "PASS"},
            ],
        }
        errs = _check_auditor_semantics(auditor)
        self.assertTrue(
            any("overall_verdict" in e and "PASS" in e for e in errs),
            errs,
        )

    def test_auditor_all_claims_pass_and_overall_pass_accepted(self) -> None:
        """_check_auditor_semantics must accept overall_verdict=PASS when all claims are PASS."""
        auditor = {
            "overall_verdict": "PASS",
            "claims": [
                {"verdict": "PASS"},
                {"verdict": "PASS"},
            ],
        }
        self.assertEqual(_check_auditor_semantics(auditor), [])

    # --- Fix 2: legacy run_dir without run.yml is ignored ---

    def test_legacy_run_dir_without_run_yml_ignores_auditor_and_measurement_yml(self) -> None:
        """_validate_run_dir must ignore a directory that has no run.yml,
        even if auditor-output.yml and measurement.yml are present and invalid."""
        exp = _exp_dir(self.base, "exp-legacy-gate")
        _write(
            exp / "manifest.yml",
            """
            schema_version: "0.1.0"
            experiment:
              name: "legacy-gate"
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
        _write(
            exp / "results" / "evidence.jsonl",
            '{"event_type":"run","timestamp":"2026-05-01T00:00:00Z","iteration":1,'
            '"metric":"x","value":true,"context":"c",'
            '"artifact_ref":"artifacts/legacy-run/measurement.yml"}\n',
        )
        legacy_run = exp / "artifacts" / "legacy-run"
        legacy_run.mkdir(parents=True, exist_ok=True)
        # Intentionally invalid YAML to prove these files are NOT validated.
        (legacy_run / "auditor-output.yml").write_text(
            "THIS IS INTENTIONALLY INVALID YAML: }{", encoding="utf-8"
        )
        (legacy_run / "measurement.yml").write_text("!!invalid", encoding="utf-8")
        # No run.yml in legacy_run → legacy directory, must be skipped entirely.
        errs = validate_repo(self.base)
        self.assertEqual(errs, [], errs)

    # --- Fix 3: execution_ref exact match for results/evidence.jsonl ---

    def test_execution_ref_nested_results_evidence_jsonl_does_not_satisfy_required_ref(
        self,
    ) -> None:
        """foo/results/evidence.jsonl must NOT satisfy the required evidence.jsonl ref."""
        exp = _exp_dir(self.base, "exp-nested-ref")
        # Create the canonical evidence file so the validator triggers the check.
        _write(
            exp / "results" / "evidence.jsonl",
            '{"event_type":"observation","timestamp":"2026-05-01T00:00:00Z",'
            '"metric":"x","value":true,"context":"c"}\n',
        )
        _write(
            exp / "manifest.yml",
            """
            schema_version: "0.1.0"
            experiment:
              name: "nested-ref"
              hypothesis: "h"
              status: testing
              category: workflow
              execution_status: executed
              execution_refs:
                - foo/results/evidence.jsonl
              created: "2026-05-01"
              updated: "2026-05-01"
              author: "test"
              iteration: 1
              evidence_level: anecdotal
            """,
        )
        # Create foo/results/evidence.jsonl so the ref resolves as existing.
        nested = exp / "foo" / "results"
        nested.mkdir(parents=True, exist_ok=True)
        (nested / "evidence.jsonl").write_text(
            '{"event_type":"observation","timestamp":"2026-05-01T00:00:00Z",'
            '"metric":"x","value":true,"context":"c"}\n',
            encoding="utf-8",
        )
        errs = validate_repo(self.base)
        # foo/results/evidence.jsonl must NOT satisfy canonical results/evidence.jsonl.
        self.assertTrue(
            any("results/evidence.jsonl" in e for e in errs),
            errs,
        )

    def test_execution_ref_dot_slash_results_evidence_jsonl_is_accepted(self) -> None:
        """./results/evidence.jsonl must be accepted as equivalent to results/evidence.jsonl."""
        exp = _build_valid_bundle(self.base)
        _write_legacy_allowlist(self.base, ["experiments/exp-fixture/artifacts/run-001/run.yml"])
        # Replace manifest with a dot-slash prefixed evidence ref.
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
                - ./results/evidence.jsonl
                - artifacts/run-001/run.yml
              created: "2026-05-01"
              updated: "2026-05-01"
              author: "test"
              iteration: 1
              evidence_level: anecdotal
            """,
        )
        errs = validate_repo(self.base)
        self.assertEqual(errs, [], errs)

    def test_execution_ref_dot_slash_run_yml_is_accepted(self) -> None:
        """./artifacts/run-001/run.yml must be accepted as equivalent to artifacts/run-001/run.yml."""
        exp = _build_valid_bundle(self.base)
        _write_legacy_allowlist(self.base, ["experiments/exp-fixture/artifacts/run-001/run.yml"])
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
                - ./artifacts/run-001/run.yml
              created: "2026-05-01"
              updated: "2026-05-01"
              author: "test"
              iteration: 1
              evidence_level: anecdotal
            """,
        )
        errs = validate_repo(self.base)
        self.assertEqual(errs, [], errs)

    def test_execution_ref_pointing_to_directory_fails(self) -> None:
        """R3: execution_ref that resolves to a directory must be rejected."""
        exp = _build_valid_bundle(self.base)
        dir_ref = exp / "artifacts" / "run-001" / "dir-ref"
        dir_ref.mkdir(parents=True, exist_ok=True)
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
                - artifacts/run-001/dir-ref
              created: "2026-05-01"
              updated: "2026-05-01"
              author: "test"
              iteration: 1
              evidence_level: anecdotal
            """,
        )
        errs = validate_repo(self.base)
        self.assertTrue(
            any("dir-ref" in e and ("Datei" in e or "existiert" in e) for e in errs),
            errs,
        )

    def test_non_string_execution_ref_does_not_crash(self) -> None:
        """R8: a list value inside execution_refs must not cause a TypeError."""
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
                - []
              created: "2026-05-01"
              updated: "2026-05-01"
              author: "test"
              iteration: 1
              evidence_level: anecdotal
            """,
        )
        errs = validate_repo(self.base)
        self.assertTrue(any("Nicht-String" in e for e in errs), errs)

    # --- PR 6: Evidence-Pack Coupling ---

    def test_valid_run_with_evidence_pack_passes(self) -> None:
        """Valid run.yml with valid artifacts.evidence_pack → no errors."""
        exp = _build_valid_bundle(self.base)
        run_dir = exp / "artifacts" / "run-001"
        
        # Add evidence_pack to run.yml
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
                contract: "auditor_output"
                canonical: true
              measurement:
                path: "measurement.yml"
                contract: "measurement_run"
                canonical: true
              run_meta:
                path: "run_meta.json"
                contract: "run_meta"
                canonical: false
                compatibility: true
              evidence_pack:
                path: "evidence-pack.yml"
                contract: "run-evidence-pack.v1"
                canonical: true
            verdict:
              outcome: "MISSING_EVIDENCE"
              effect_claim_allowed: false
            """,
        )
        
        # Create valid evidence-pack.yml.
        # repo_local evidence paths must be repo-root-relative, not run-local.
        # run_bundle_evidence_pack_reference must not be self-only.
        _write(
            run_dir / "evidence-pack.yml",
            """
            schema_version: "1.0.0"
            run_id: "run-001"
            claims:
              - claim_id: "ep-001"
                text: "Evidence pack exists"
                type: "run_bundle_evidence_pack_reference"
                verdict: "PASS"
                evidence:
                  - path: "experiments/exp-fixture/artifacts/run-001/run.yml"
                    status: "repo_local"
                  - path: "experiments/exp-fixture/artifacts/run-001/evidence-pack.yml"
                    status: "repo_local"
            """,
        )

        _write_legacy_allowlist(self.base, [])

        errs = validate_repo(self.base)
        self.assertEqual(errs, [], errs)

    def test_missing_evidence_pack_generates_warning_no_error(self) -> None:
        """Missing artifacts.evidence_pack → warning, but no error (legacy)."""
        _build_valid_bundle(self.base)
        _write_legacy_allowlist(self.base, ["experiments/exp-fixture/artifacts/run-001/run.yml"])
        # Valid bundle without evidence_pack — should warn, not error.
        errs = validate_repo(self.base)
        self.assertEqual(errs, [])
        # Check warnings
        self.assertTrue(any("run_bundle_without_evidence_pack" in w for w in _vrb.last_warnings), _vrb.last_warnings)

    def test_missing_evidence_pack_without_allowlist_fails(self) -> None:
        """Missing artifacts.evidence_pack must fail for non-allowlisted runs."""
        _build_valid_bundle(self.base)
        _write_legacy_allowlist(self.base, [])

        errs = validate_repo(self.base)
        self.assertTrue(
            any("run_bundle_missing_evidence_pack_not_allowlisted" in e for e in errs),
            errs,
        )

    def test_allowlist_entry_pointing_to_missing_run_yml_fails(self) -> None:
        """Allowlist entries must point to existing run.yml files."""
        _write_legacy_allowlist(
            self.base,
            ["experiments/ghost-exp/artifacts/run-999/run.yml"],
        )
        errs = validate_repo(self.base)
        self.assertTrue(any("zeigt nicht auf eine existierende Datei" in e for e in errs), errs)

    def test_stale_allowlist_entry_for_run_with_evidence_pack_fails(self) -> None:
        """Allowlist entries become stale when run.yml already contains artifacts.evidence_pack."""
        exp = _build_valid_bundle(self.base)
        _write_legacy_allowlist(self.base, ["experiments/exp-fixture/artifacts/run-001/run.yml"])
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
                contract: "auditor_output"
                canonical: true
              measurement:
                path: "measurement.yml"
                contract: "measurement_run"
                canonical: true
              run_meta:
                path: "run_meta.json"
                contract: "run_meta"
                canonical: false
                compatibility: true
              evidence_pack:
                path: "evidence-pack.yml"
                contract: "run-evidence-pack.v1"
                canonical: true
            verdict:
              outcome: "MISSING_EVIDENCE"
              effect_claim_allowed: false
            """,
        )

        _write(
            run_dir / "evidence-pack.yml",
            """
            schema_version: "1.0.0"
            run_id: "run-001"
            claims:
              - claim_id: "ep-001"
                text: "coupled"
                type: "run_bundle_evidence_pack_reference"
                verdict: "PASS"
                evidence:
                  - path: "experiments/exp-fixture/artifacts/run-001/run.yml"
                    status: "repo_local"
                  - path: "experiments/exp-fixture/artifacts/run-001/evidence-pack.yml"
                    status: "repo_local"
            """,
        )

        errs = validate_repo(self.base)
        self.assertTrue(any("Stale Allowlist-Eintrag" in e for e in errs), errs)

    def test_evidence_pack_wrong_contract_fails(self) -> None:
        """evidence_pack.contract must be exactly 'run-evidence-pack.v1' (schema-enforced)."""
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
                contract: "auditor_output"
                canonical: true
              measurement:
                path: "measurement.yml"
                contract: "measurement_run"
                canonical: true
              run_meta:
                path: "run_meta.json"
                contract: "run_meta"
                canonical: false
                compatibility: true
              evidence_pack:
                path: "evidence-pack.yml"
                contract: "wrong-contract"
                canonical: true
            verdict:
              outcome: "MISSING_EVIDENCE"
              effect_claim_allowed: false
            """,
        )
        
        errs = validate_repo(self.base)
        # Schema rejects const violation, so error is schema-invalid
        self.assertTrue(any("schema-invalid" in e for e in errs), errs)

    def test_evidence_pack_canonical_false_fails(self) -> None:
        """evidence_pack.canonical must be exactly true (schema-enforced)."""
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
                contract: "auditor_output"
                canonical: true
              measurement:
                path: "measurement.yml"
                contract: "measurement_run"
                canonical: true
              run_meta:
                path: "run_meta.json"
                contract: "run_meta"
                canonical: false
                compatibility: true
              evidence_pack:
                path: "evidence-pack.yml"
                contract: "run-evidence-pack.v1"
                canonical: false
            verdict:
              outcome: "MISSING_EVIDENCE"
              effect_claim_allowed: false
            """,
        )
        
        errs = validate_repo(self.base)
        # Schema rejects const violation
        self.assertTrue(any("schema-invalid" in e for e in errs), errs)

    def test_evidence_pack_path_escape_fails(self) -> None:
        """evidence_pack.path with .. must be rejected (schema regex + path validation)."""
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
                contract: "auditor_output"
                canonical: true
              measurement:
                path: "measurement.yml"
                contract: "measurement_run"
                canonical: true
              run_meta:
                path: "run_meta.json"
                contract: "run_meta"
                canonical: false
                compatibility: true
              evidence_pack:
                path: "../evidence-pack.yml"
                contract: "run-evidence-pack.v1"
                canonical: true
            verdict:
              outcome: "MISSING_EVIDENCE"
              effect_claim_allowed: false
            """,
        )
        
        errs = validate_repo(self.base)
        # Schema regex rejects .. in path pattern
        self.assertTrue(any("schema-invalid" in e for e in errs), errs)

    def test_evidence_pack_file_missing_fails(self) -> None:
        """evidence_pack.path pointing to non-existent file → error."""
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
                contract: "auditor_output"
                canonical: true
              measurement:
                path: "measurement.yml"
                contract: "measurement_run"
                canonical: true
              run_meta:
                path: "run_meta.json"
                contract: "run_meta"
                canonical: false
                compatibility: true
              evidence_pack:
                path: "ghost-evidence-pack.yml"
                contract: "run-evidence-pack.v1"
                canonical: true
            verdict:
              outcome: "MISSING_EVIDENCE"
              effect_claim_allowed: false
            """,
        )
        
        errs = validate_repo(self.base)
        self.assertTrue(any("ghost-evidence-pack" in e and "existiert nicht" in e for e in errs), errs)

    def test_evidence_pack_schema_invalid_fails(self) -> None:
        """evidence-pack.yml with invalid schema → error."""
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
                contract: "auditor_output"
                canonical: true
              measurement:
                path: "measurement.yml"
                contract: "measurement_run"
                canonical: true
              run_meta:
                path: "run_meta.json"
                contract: "run_meta"
                canonical: false
                compatibility: true
              evidence_pack:
                path: "evidence-pack.yml"
                contract: "run-evidence-pack.v1"
                canonical: true
            verdict:
              outcome: "MISSING_EVIDENCE"
              effect_claim_allowed: false
            """,
        )
        
        # Invalid: missing required 'claims' field
        _write(
            run_dir / "evidence-pack.yml",
            """
            schema_version: "1.0.0"
            run_id: "run-001"
            """,
        )
        
        errs = validate_repo(self.base)
        self.assertTrue(any("schema-invalid" in e for e in errs), errs)

    def test_evidence_pack_run_id_mismatch_fails(self) -> None:
        """evidence-pack.yml run_id must match run.yml run.id."""
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
                contract: "auditor_output"
                canonical: true
              measurement:
                path: "measurement.yml"
                contract: "measurement_run"
                canonical: true
              run_meta:
                path: "run_meta.json"
                contract: "run_meta"
                canonical: false
                compatibility: true
              evidence_pack:
                path: "evidence-pack.yml"
                contract: "run-evidence-pack.v1"
                canonical: true
            verdict:
              outcome: "MISSING_EVIDENCE"
              effect_claim_allowed: false
            """,
        )
        
        _write(
            run_dir / "evidence-pack.yml",
            """
            schema_version: "1.0.0"
            run_id: "wrong-run-id"
            claims:
              - claim_id: "ep-001"
                text: "Evidence pack exists"
                type: "run_bundle_evidence_pack_reference"
                verdict: "PASS"
                evidence:
                  - path: "artifacts/run-001/evidence-pack.yml"
                    status: "repo_local"
            """,
        )
        
        errs = validate_repo(self.base)
        self.assertTrue(any("run_id" in e and "wrong-run-id" in e for e in errs), errs)

    def test_evidence_pack_repo_local_evidence_missing_fails(self) -> None:
        """evidence-pack claims with repo_local evidence must point to existing files."""
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
                contract: "auditor_output"
                canonical: true
              measurement:
                path: "measurement.yml"
                contract: "measurement_run"
                canonical: true
              run_meta:
                path: "run_meta.json"
                contract: "run_meta"
                canonical: false
                compatibility: true
              evidence_pack:
                path: "evidence-pack.yml"
                contract: "run-evidence-pack.v1"
                canonical: true
            verdict:
              outcome: "MISSING_EVIDENCE"
              effect_claim_allowed: false
            """,
        )
        
        _write(
            run_dir / "evidence-pack.yml",
            """
            schema_version: "1.0.0"
            run_id: "run-001"
            claims:
              - claim_id: "ep-001"
                text: "Evidence pack exists"
                type: "run_bundle_evidence_pack_reference"
                verdict: "PASS"
                evidence:
                  - path: "ghost-file.txt"
                    status: "repo_local"
            """,
        )
        
        errs = validate_repo(self.base)
        self.assertTrue(any("repo_local" in e and "existiert nicht" in e for e in errs), errs)

    def test_evidence_pack_repo_local_evidence_escape_fails(self) -> None:
        """evidence-pack repo_local evidence paths with .. are rejected (schema regex)."""
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
                contract: "auditor_output"
                canonical: true
              measurement:
                path: "measurement.yml"
                contract: "measurement_run"
                canonical: true
              run_meta:
                path: "run_meta.json"
                contract: "run_meta"
                canonical: false
                compatibility: true
              evidence_pack:
                path: "evidence-pack.yml"
                contract: "run-evidence-pack.v1"
                canonical: true
            verdict:
              outcome: "MISSING_EVIDENCE"
              effect_claim_allowed: false
            """,
        )
        
        _write(
            run_dir / "evidence-pack.yml",
            """
            schema_version: "1.0.0"
            run_id: "run-001"
            claims:
              - claim_id: "ep-001"
                text: "Evidence pack exists"
                type: "run_bundle_evidence_pack_reference"
                verdict: "PASS"
                evidence:
                  - path: "../../../../etc/passwd"
                    status: "repo_local"
            """,
        )
        
        errs = validate_repo(self.base)
        # Schema regex rejects .. pattern in evidence paths
        self.assertTrue(any("schema-invalid" in e for e in errs), errs)

    def test_evidence_pack_self_observation_pass_fails(self) -> None:
        """PASS claims that only reference the evidence-pack itself are rejected."""
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
                contract: "auditor_output"
                canonical: true
              measurement:
                path: "measurement.yml"
                contract: "measurement_run"
                canonical: true
              run_meta:
                path: "run_meta.json"
                contract: "run_meta"
                canonical: false
                compatibility: true
              evidence_pack:
                path: "evidence-pack.yml"
                contract: "run-evidence-pack.v1"
                canonical: true
            verdict:
              outcome: "MISSING_EVIDENCE"
              effect_claim_allowed: false
            """,
        )
        
        # PASS claim of type "agent_effectiveness" that only references evidence-pack.yml itself
        _write(
            run_dir / "evidence-pack.yml",
            """
            schema_version: "1.0.0"
            run_id: "run-001"
            claims:
              - claim_id: "ep-self"
                text: "Agent works"
                type: "agent_effectiveness"
                verdict: "PASS"
                evidence:
                  - path: "experiments/exp-fixture/artifacts/run-001/evidence-pack.yml"
                    status: "repo_local"
            """,
        )
        
        errs = validate_repo(self.base)
        self.assertTrue(
            any("Self-Observation" in e for e in errs),
            f"Expected Self-Observation error, got: {errs}",
        )

    def test_evidence_pack_reference_type_self_only_fails(self) -> None:
        """run_bundle_evidence_pack_reference PASS must include non-self evidence (e.g. run.yml)."""
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
                contract: "auditor_output"
                canonical: true
              measurement:
                path: "measurement.yml"
                contract: "measurement_run"
                canonical: true
              run_meta:
                path: "run_meta.json"
                contract: "run_meta"
                canonical: false
                compatibility: true
              evidence_pack:
                path: "evidence-pack.yml"
                contract: "run-evidence-pack.v1"
                canonical: true
            verdict:
              outcome: "MISSING_EVIDENCE"
              effect_claim_allowed: false
            """,
        )

        _write(
            run_dir / "evidence-pack.yml",
            """
            schema_version: "1.0.0"
            run_id: "run-001"
            claims:
              - claim_id: "ep-self-only"
                text: "Pack references itself only"
                type: "run_bundle_evidence_pack_reference"
                verdict: "PASS"
                evidence:
                  - path: "experiments/exp-fixture/artifacts/run-001/evidence-pack.yml"
                    status: "repo_local"
            """,
        )

        errs = validate_repo(self.base)
        self.assertTrue(any("Self-Observation" in e for e in errs), errs)

    def test_self_observation_not_bypassed_by_external_unverified(self) -> None:
        """Weak non-self evidence (external_unverified) must not bypass self-observation checks."""
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
                contract: "auditor_output"
                canonical: true
              measurement:
                path: "measurement.yml"
                contract: "measurement_run"
                canonical: true
              run_meta:
                path: "run_meta.json"
                contract: "run_meta"
                canonical: false
                compatibility: true
              evidence_pack:
                path: "evidence-pack.yml"
                contract: "run-evidence-pack.v1"
                canonical: true
            verdict:
              outcome: "MISSING_EVIDENCE"
              effect_claim_allowed: false
            """,
        )

        _write(
            run_dir / "evidence-pack.yml",
            """
            schema_version: "1.0.0"
            run_id: "run-001"
            claims:
              - claim_id: "ep-weak-001"
                text: "Weak non-self must not pass"
                type: "run_bundle_evidence_pack_reference"
                verdict: "PASS"
                evidence:
                  - path: "experiments/exp-fixture/artifacts/run-001/evidence-pack.yml"
                    status: "repo_local"
                  - path: "https://example.invalid/proof"
                    status: "external_unverified"
            """,
        )

        _write_legacy_allowlist(self.base, [])

        errs = validate_repo(self.base)
        self.assertTrue(any("Self-Observation" in e for e in errs), errs)

    def test_self_observation_not_bypassed_by_missing_evidence(self) -> None:
        """Weak non-self evidence (missing_evidence) must not bypass self-observation checks."""
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
                contract: "auditor_output"
                canonical: true
              measurement:
                path: "measurement.yml"
                contract: "measurement_run"
                canonical: true
              run_meta:
                path: "run_meta.json"
                contract: "run_meta"
                canonical: false
                compatibility: true
              evidence_pack:
                path: "evidence-pack.yml"
                contract: "run-evidence-pack.v1"
                canonical: true
            verdict:
              outcome: "MISSING_EVIDENCE"
              effect_claim_allowed: false
            """,
        )

        _write(
            run_dir / "evidence-pack.yml",
            """
            schema_version: "1.0.0"
            run_id: "run-001"
            claims:
              - claim_id: "ep-weak-002"
                text: "Missing evidence must not pass"
                type: "run_bundle_evidence_pack_reference"
                verdict: "PASS"
                evidence:
                  - path: "experiments/exp-fixture/artifacts/run-001/evidence-pack.yml"
                    status: "repo_local"
                  - path: "experiments/exp-fixture/results/missing-cmd.log"
                    status: "missing_evidence"
            """,
        )

        _write_legacy_allowlist(self.base, [])

        errs = validate_repo(self.base)
        self.assertTrue(any("Self-Observation" in e for e in errs), errs)


# ---------------------------------------------------------------------------
# Review/Rework Artifact Contract tests (review-rework-artifact.contract.md v0.1)
# ---------------------------------------------------------------------------

class ReviewReworkArtifactTests(unittest.TestCase):
    """Tests for null-value discipline and review_evidence_artifact coupling.

    See .vibe/review-rework-artifact.contract.md for the full contract.
    """

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)
        _make_repo_skeleton(self.base)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    # ----- null-value discipline: passing cases --------------------------------

    def test_review_friction_null_with_notes_reason_passes(self) -> None:
        """review_friction_count=null + missing_evidence + notes reason → PASS."""
        exp = _build_valid_bundle(self.base)
        run_dir = exp / "artifacts" / "run-001"
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        # Write a custom measurement that has null review metrics with reasons, using
        # auditor_verdict matching the default auditor fixture (MISSING_EVIDENCE, 2 gaps).
        _write(
            run_dir / "measurement.yml",
            textwrap.dedent("""\
                schema_version: "1.0.0"
                contract: "measurement_run"
                run_id: "run-001"
                auditor_verdict: "MISSING_EVIDENCE"
                auditor_ref: "auditor-output.yml"
                metrics:
                  scope_drift_count:
                    value: null
                    evidence_status: "missing_evidence"
                    notes: "no changed-files artifact"
                  unsupported_claim_count:
                    value: 2
                    evidence_status: "derived_from_auditor_output"
                  missing_locator_count:
                    value: 0
                    evidence_status: "external_unverified"
                  validation_gap_count:
                    value: 2
                    evidence_status: "derived_from_auditor_output"
                  review_friction_count:
                    value: null
                    evidence_status: "missing_evidence"
                    notes: "No review comment artifact archived."
                  rework_count:
                    value: null
                    evidence_status: "missing_evidence"
                    notes: "No rework artifact archived."
                  false_block_count:
                    value: 0
                    evidence_status: "external_unverified"
                  task_completion_time_observed:
                    value: "n/a"
                    evidence_status: "external_unverified"
                missing_evidence:
                  - item: "scope_drift_count"
                    detail: "no changed-files artifact"
            """),
        )
        errs = validate_repo(self.base)
        self.assertEqual(errs, [], errs)

    def test_review_friction_null_with_missing_evidence_list_reason_passes(self) -> None:
        """review_friction_count=null + missing_evidence + reason in missing_evidence list → PASS."""
        exp = _build_valid_bundle(
            self.base,
            comparability_text=_valid_comparability_yml(
                verdict="comparable",
                changed_files_artifact="changed-files.txt",
            ),
        )
        _write_changed_files_artifact(exp / "artifacts" / "run-001")
        run_dir = exp / "artifacts" / "run-001"
        _write(
            run_dir / "measurement.yml",
            textwrap.dedent("""\
                schema_version: "1.0.0"
                contract: "measurement_run"
                run_id: "run-001"
                auditor_verdict: "MISSING_EVIDENCE"
                auditor_ref: "auditor-output.yml"
                metrics:
                  scope_drift_count:
                    value: null
                    evidence_status: "missing_evidence"
                    notes: "no changed-files artifact"
                  unsupported_claim_count:
                    value: 2
                    evidence_status: "derived_from_auditor_output"
                  missing_locator_count:
                    value: 0
                    evidence_status: "external_unverified"
                  validation_gap_count:
                    value: 2
                    evidence_status: "derived_from_auditor_output"
                  review_friction_count:
                    value: null
                    evidence_status: "missing_evidence"
                  rework_count:
                    value: null
                    evidence_status: "missing_evidence"
                  false_block_count:
                    value: 0
                    evidence_status: "external_unverified"
                  task_completion_time_observed:
                    value: "n/a"
                    evidence_status: "external_unverified"
                missing_evidence:
                  - item: "review_friction_count"
                    detail: "No review comment artifact archived for this run."
                  - item: "rework_count"
                    detail: "No rework artifact archived for this run."
                  - item: "scope_drift_count"
                    detail: "No changed-files artifact."
            """),
        )
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertEqual(errs, [], errs)

    # ----- null-value discipline: failing cases --------------------------------

    def test_review_friction_null_wrong_evidence_status_fails(self) -> None:
        """review_friction_count=null with evidence_status != missing_evidence → error."""
        exp = _build_valid_bundle(
            self.base,
            comparability_text=_valid_comparability_yml(
                verdict="comparable",
                changed_files_artifact="changed-files.txt",
            ),
        )
        _write_changed_files_artifact(exp / "artifacts" / "run-001")
        run_dir = exp / "artifacts" / "run-001"
        _write(
            run_dir / "measurement.yml",
            textwrap.dedent("""\
                schema_version: "1.0.0"
                contract: "measurement_run"
                run_id: "run-001"
                auditor_verdict: "PASS"
                auditor_ref: "auditor-output.yml"
                metrics:
                  scope_drift_count:
                    value: 0
                    evidence_status: "repo_local"
                    notes: "scope contained"
                  unsupported_claim_count:
                    value: 0
                    evidence_status: "derived_from_auditor_output"
                  missing_locator_count:
                    value: 0
                    evidence_status: "external_unverified"
                  validation_gap_count:
                    value: 0
                    evidence_status: "derived_from_auditor_output"
                  review_friction_count:
                    value: null
                    evidence_status: "self_reported"
                  rework_count:
                    value: 0
                    evidence_status: "external_unverified"
                  false_block_count:
                    value: 0
                    evidence_status: "external_unverified"
                  task_completion_time_observed:
                    value: "n/a"
                    evidence_status: "external_unverified"
            """),
        )
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertTrue(
            any("review_friction_count.value=null" in e and "missing_evidence" in e for e in errs),
            errs,
        )

    def test_review_friction_null_missing_evidence_without_reason_fails(self) -> None:
        """review_friction_count=null + missing_evidence but no notes and no missing_evidence entry → error."""
        exp = _build_valid_bundle(
            self.base,
            comparability_text=_valid_comparability_yml(
                verdict="comparable",
                changed_files_artifact="changed-files.txt",
            ),
        )
        _write_changed_files_artifact(exp / "artifacts" / "run-001")
        run_dir = exp / "artifacts" / "run-001"
        _write(
            run_dir / "measurement.yml",
            textwrap.dedent("""\
                schema_version: "1.0.0"
                contract: "measurement_run"
                run_id: "run-001"
                auditor_verdict: "PASS"
                auditor_ref: "auditor-output.yml"
                metrics:
                  scope_drift_count:
                    value: 0
                    evidence_status: "repo_local"
                    notes: "scope contained"
                  unsupported_claim_count:
                    value: 0
                    evidence_status: "derived_from_auditor_output"
                  missing_locator_count:
                    value: 0
                    evidence_status: "external_unverified"
                  validation_gap_count:
                    value: 0
                    evidence_status: "derived_from_auditor_output"
                  review_friction_count:
                    value: null
                    evidence_status: "missing_evidence"
                  rework_count:
                    value: 0
                    evidence_status: "external_unverified"
                  false_block_count:
                    value: 0
                    evidence_status: "external_unverified"
                  task_completion_time_observed:
                    value: "n/a"
                    evidence_status: "external_unverified"
            """),
        )
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertTrue(
            any("review_friction_count.value=null" in e and "Begründung" in e for e in errs),
            errs,
        )

    def test_rework_count_null_missing_evidence_without_reason_fails(self) -> None:
        """rework_count=null + missing_evidence but no notes and no missing_evidence entry → error."""
        exp = _build_valid_bundle(
            self.base,
            comparability_text=_valid_comparability_yml(
                verdict="comparable",
                changed_files_artifact="changed-files.txt",
            ),
        )
        _write_changed_files_artifact(exp / "artifacts" / "run-001")
        run_dir = exp / "artifacts" / "run-001"
        _write(
            run_dir / "measurement.yml",
            textwrap.dedent("""\
                schema_version: "1.0.0"
                contract: "measurement_run"
                run_id: "run-001"
                auditor_verdict: "PASS"
                auditor_ref: "auditor-output.yml"
                metrics:
                  scope_drift_count:
                    value: 0
                    evidence_status: "repo_local"
                    notes: "scope contained"
                  unsupported_claim_count:
                    value: 0
                    evidence_status: "derived_from_auditor_output"
                  missing_locator_count:
                    value: 0
                    evidence_status: "external_unverified"
                  validation_gap_count:
                    value: 0
                    evidence_status: "derived_from_auditor_output"
                  review_friction_count:
                    value: 0
                    evidence_status: "external_unverified"
                  rework_count:
                    value: null
                    evidence_status: "missing_evidence"
                  false_block_count:
                    value: 0
                    evidence_status: "external_unverified"
                  task_completion_time_observed:
                    value: "n/a"
                    evidence_status: "external_unverified"
            """),
        )
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertTrue(
            any("rework_count.value=null" in e and "Begründung" in e for e in errs),
            errs,
        )

    # ----- review_evidence_artifact: passing cases ----------------------------

    def _write_review_events(self, run_dir: Path, name: str = "review-events.yml") -> None:
        _write(
            run_dir / name,
            textwrap.dedent("""\
                schema_version: "1.0.0"
                contract: "review_events"
                run_id: "run-001"
                pr_ref: "github:test/test/pull/1"
                review_friction_count: 2
                rework_count: 1
                captured_at: "2026-05-11T12:00:00Z"
                evidence_status: "external_verified"
                review_thread_refs:
                  - "https://github.com/test/test/pull/1#issuecomment-1001"
                notes: "fixture review events"
            """),
        )

    def test_review_friction_repo_local_with_valid_review_evidence_artifact_passes(self) -> None:
        """review_friction_count.evidence_status=repo_local + valid review_evidence_artifact → PASS."""
        exp = _build_valid_bundle(
            self.base,
            comparability_text=_valid_comparability_yml(
                verdict="comparable",
                changed_files_artifact="changed-files.txt",
            ),
        )
        run_dir = exp / "artifacts" / "run-001"
        _write_changed_files_artifact(run_dir)
        self._write_review_events(run_dir)
        # Write an all-PASS auditor so the measurement can use auditor_verdict=PASS.
        _write(
            run_dir / "auditor-output.yml",
            textwrap.dedent("""\
                schema_version: "1.0.0"
                contract: "auditor_output"
                run_id: "run-001"
                pr_ref: "github:test/test/pull/1"
                auditor: "test-auditor"
                overall_verdict: "PASS"
                claims:
                  - id: "c-1"
                    text: "all passing"
                    type: "file_changed"
                    verdict: "PASS"
                    evidence: []
            """),
        )
        # Append review_evidence_artifact to comparability.yml
        comp_path = run_dir / "comparability.yml"
        comp_path.write_text(
            comp_path.read_text(encoding="utf-8")
            + '\nreview_evidence_artifact: "review-events.yml"\n',
            encoding="utf-8",
        )
        _write(
            run_dir / "measurement.yml",
            textwrap.dedent("""\
                schema_version: "1.0.0"
                contract: "measurement_run"
                run_id: "run-001"
                auditor_verdict: "PASS"
                auditor_ref: "auditor-output.yml"
                metrics:
                  scope_drift_count:
                    value: 0
                    evidence_status: "repo_local"
                    notes: "scope contained"
                  unsupported_claim_count:
                    value: 0
                    evidence_status: "derived_from_auditor_output"
                  missing_locator_count:
                    value: 0
                    evidence_status: "external_unverified"
                  validation_gap_count:
                    value: 0
                    evidence_status: "derived_from_auditor_output"
                  review_friction_count:
                    value: 2
                    evidence_status: "repo_local"
                    notes: "review-events.yml archived"
                  rework_count:
                    value: 1
                    evidence_status: "repo_local"
                    notes: "review-events.yml archived"
                  false_block_count:
                    value: 0
                    evidence_status: "external_unverified"
                  task_completion_time_observed:
                    value: "n/a"
                    evidence_status: "external_unverified"
            """),
        )
        # Also update run.yml verdict to PASS to match auditor
        _write(
            run_dir / "run.yml",
            _valid_run_yml(run_id="run-001").replace(
                'outcome: "MISSING_EVIDENCE"', 'outcome: "PASS"'
            ),
        )
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertEqual(errs, [], errs)

    def test_review_friction_repo_local_without_review_evidence_artifact_fails(self) -> None:
        """review_friction_count.evidence_status=repo_local without review_evidence_artifact → error."""
        exp = _build_valid_bundle(
            self.base,
            comparability_text=_valid_comparability_yml(
                verdict="comparable",
                changed_files_artifact="changed-files.txt",
            ),
        )
        run_dir = exp / "artifacts" / "run-001"
        _write_changed_files_artifact(run_dir)
        _write(
            run_dir / "measurement.yml",
            textwrap.dedent("""\
                schema_version: "1.0.0"
                contract: "measurement_run"
                run_id: "run-001"
                auditor_verdict: "PASS"
                auditor_ref: "auditor-output.yml"
                metrics:
                  scope_drift_count:
                    value: 0
                    evidence_status: "repo_local"
                    notes: "scope contained"
                  unsupported_claim_count:
                    value: 0
                    evidence_status: "derived_from_auditor_output"
                  missing_locator_count:
                    value: 0
                    evidence_status: "external_unverified"
                  validation_gap_count:
                    value: 0
                    evidence_status: "derived_from_auditor_output"
                  review_friction_count:
                    value: 2
                    evidence_status: "repo_local"
                  rework_count:
                    value: 0
                    evidence_status: "external_unverified"
                  false_block_count:
                    value: 0
                    evidence_status: "external_unverified"
                  task_completion_time_observed:
                    value: "n/a"
                    evidence_status: "external_unverified"
            """),
        )
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertTrue(
            any("review_friction_count.evidence_status=repo_local" in e
                and "review_evidence_artifact" in e for e in errs),
            errs,
        )

    def test_rework_count_repo_local_without_review_evidence_artifact_fails(self) -> None:
        """rework_count.evidence_status=repo_local without review_evidence_artifact → error."""
        exp = _build_valid_bundle(
            self.base,
            comparability_text=_valid_comparability_yml(
                verdict="comparable",
                changed_files_artifact="changed-files.txt",
            ),
        )
        run_dir = exp / "artifacts" / "run-001"
        _write_changed_files_artifact(run_dir)
        _write(
            run_dir / "measurement.yml",
            textwrap.dedent("""\
                schema_version: "1.0.0"
                contract: "measurement_run"
                run_id: "run-001"
                auditor_verdict: "PASS"
                auditor_ref: "auditor-output.yml"
                metrics:
                  scope_drift_count:
                    value: 0
                    evidence_status: "repo_local"
                    notes: "scope contained"
                  unsupported_claim_count:
                    value: 0
                    evidence_status: "derived_from_auditor_output"
                  missing_locator_count:
                    value: 0
                    evidence_status: "external_unverified"
                  validation_gap_count:
                    value: 0
                    evidence_status: "derived_from_auditor_output"
                  review_friction_count:
                    value: 0
                    evidence_status: "external_unverified"
                  rework_count:
                    value: 1
                    evidence_status: "repo_local"
                  false_block_count:
                    value: 0
                    evidence_status: "external_unverified"
                  task_completion_time_observed:
                    value: "n/a"
                    evidence_status: "external_unverified"
            """),
        )
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertTrue(
            any("rework_count.evidence_status=repo_local" in e
                and "review_evidence_artifact" in e for e in errs),
            errs,
        )

    # ----- review_evidence_artifact: ref validation ---------------------------

    def test_review_evidence_artifact_nonexistent_file_fails(self) -> None:
        """review_evidence_artifact pointing to non-existent file → error."""
        exp = _build_valid_bundle(
            self.base,
            comparability_text=_valid_comparability_yml(
                verdict="comparable",
                changed_files_artifact="changed-files.txt",
            ),
        )
        run_dir = exp / "artifacts" / "run-001"
        _write_changed_files_artifact(run_dir)
        comp_path = run_dir / "comparability.yml"
        comp_path.write_text(
            comp_path.read_text(encoding="utf-8")
            + '\nreview_evidence_artifact: "ghost-review-events.yml"\n',
            encoding="utf-8",
        )
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertTrue(
            any("ghost-review-events.yml" in e and "existierende Datei" in e for e in errs),
            errs,
        )

    def test_review_evidence_artifact_absolute_path_fails(self) -> None:
        """review_evidence_artifact with absolute path → error."""
        exp = _build_valid_bundle(
            self.base,
            comparability_text=_valid_comparability_yml(
                verdict="comparable",
                changed_files_artifact="changed-files.txt",
            ),
        )
        run_dir = exp / "artifacts" / "run-001"
        _write_changed_files_artifact(run_dir)
        comp_path = run_dir / "comparability.yml"
        comp_path.write_text(
            comp_path.read_text(encoding="utf-8")
            + '\nreview_evidence_artifact: "/tmp/review-events.yml"\n',
            encoding="utf-8",
        )
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertTrue(
            any("review_evidence_artifact" in e and "absoluter Pfad" in e for e in errs),
            errs,
        )

    def test_review_evidence_artifact_pointing_to_other_run_fails(self) -> None:
        """review_evidence_artifact referencing a different run directory → error."""
        exp = _build_valid_bundle(
            self.base,
            comparability_text=_valid_comparability_yml(
                verdict="comparable",
                changed_files_artifact="changed-files.txt",
            ),
        )
        run_dir = exp / "artifacts" / "run-001"
        _write_changed_files_artifact(run_dir)
        # Create the file in a different run directory.
        other_run = exp / "artifacts" / "run-000"
        self._write_review_events(other_run, "review-events.yml")
        comp_path = run_dir / "comparability.yml"
        comp_path.write_text(
            comp_path.read_text(encoding="utf-8")
            + '\nreview_evidence_artifact: "artifacts/run-000/review-events.yml"\n',
            encoding="utf-8",
        )
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertTrue(
            any("review_evidence_artifact" in e
                and "run-lokal oder experiment-relativ auf dieses Run-Verzeichnis zeigen" in e
                for e in errs),
            errs,
        )

    def test_review_evidence_artifact_experiment_relative_passes(self) -> None:
        """review_evidence_artifact as experiment-relative path (artifacts/run-id/...) → PASS."""
        exp = _build_valid_bundle(
            self.base,
            comparability_text=_valid_comparability_yml(
                verdict="comparable",
                changed_files_artifact="changed-files.txt",
            ),
        )
        run_dir = exp / "artifacts" / "run-001"
        _write_changed_files_artifact(run_dir)
        self._write_review_events(run_dir)
        comp_path = run_dir / "comparability.yml"
        comp_path.write_text(
            comp_path.read_text(encoding="utf-8")
            + '\nreview_evidence_artifact: "artifacts/run-001/review-events.yml"\n',
            encoding="utf-8",
        )
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertEqual(errs, [], errs)


# ---------------------------------------------------------------------------
# Content-validation tests for review-events.yml
# (review-rework-artifact.contract.md v0.1, follow-up to PR #178)
# ---------------------------------------------------------------------------

def _setup_review_evidence_base(base: Path) -> tuple[Path, Path]:
    """Build a valid bundle with comparability + changed-files, return (exp_dir, run_dir).

    Caller should write review-events.yml and append review_evidence_artifact
    to comparability.yml before running validate_repo().
    """
    exp = _build_valid_bundle(
        base,
        comparability_text=_valid_comparability_yml(
            verdict="comparable",
            changed_files_artifact="changed-files.txt",
        ),
    )
    run_dir = exp / "artifacts" / "run-001"
    _write_changed_files_artifact(run_dir)
    return exp, run_dir


def _append_review_evidence_artifact(run_dir: Path, ref: str = "review-events.yml") -> None:
    comp_path = run_dir / "comparability.yml"
    comp_path.write_text(
        comp_path.read_text(encoding="utf-8")
        + f'\nreview_evidence_artifact: "{ref}"\n',
        encoding="utf-8",
    )


def _valid_review_events(run_id: str = "run-001") -> str:
    return textwrap.dedent(f"""\
        schema_version: "1.0.0"
        contract: "review_events"
        run_id: "{run_id}"
        pr_ref: "github:test/test/pull/1"
        review_friction_count: 2
        rework_count: 1
        captured_at: "2026-05-11T12:00:00Z"
        evidence_status: "external_verified"
        review_thread_refs:
          - "https://github.com/test/test/pull/1#issuecomment-1001"
        notes: "fixture review events"
    """)


class ReviewEventsContentValidationTests(unittest.TestCase):
    """Tests for _validate_review_events_content().

    Each test builds a bundle where comparability.yml sets review_evidence_artifact;
    the review-events.yml content varies per case.
    """

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)
        _make_repo_skeleton(self.base)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    # ----- passing case -------------------------------------------------------

    def test_valid_review_events_passes(self) -> None:
        """A fully valid review-events.yml with all required fields passes."""
        exp, run_dir = _setup_review_evidence_base(self.base)
        _write(run_dir / "review-events.yml", _valid_review_events())
        _append_review_evidence_artifact(run_dir)
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertEqual(errs, [], errs)

    def test_valid_review_events_repo_local_evidence_status_passes(self) -> None:
        """evidence_status=repo_local does not require review_thread_refs/rework_commit_refs."""
        exp, run_dir = _setup_review_evidence_base(self.base)
        _write(
            run_dir / "review-events.yml",
            textwrap.dedent("""\
                schema_version: "1.0.0"
                contract: "review_events"
                run_id: "run-001"
                pr_ref: "github:test/test/pull/1"
                review_friction_count: 0
                rework_count: 0
                captured_at: "2026-05-11T00:00:00Z"
                evidence_status: "repo_local"
            """),
        )
        _append_review_evidence_artifact(run_dir)
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertEqual(errs, [], errs)

    # ----- empty / non-dict ---------------------------------------------------

    def test_empty_review_events_file_fails(self) -> None:
        """An empty YAML file (parsed as empty dict) fails with missing-field errors."""
        exp, run_dir = _setup_review_evidence_base(self.base)
        (run_dir / "review-events.yml").write_text("", encoding="utf-8")
        _append_review_evidence_artifact(run_dir)
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        # An empty YAML dict has no required fields: contract, run_id, counts, etc. must all fail.
        review_errs = [e for e in errs if "review-events.yml" in e]
        self.assertGreater(len(review_errs), 0, errs)

    def test_list_review_events_file_fails(self) -> None:
        """A YAML list (not a mapping) fails."""
        exp, run_dir = _setup_review_evidence_base(self.base)
        _write(run_dir / "review-events.yml", "- entry1\n- entry2\n")
        _append_review_evidence_artifact(run_dir)
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertTrue(
            any("review-events.yml" in e and "YAML-Objekt" in e for e in errs),
            errs,
        )

    # ----- contract -----------------------------------------------------------

    def test_wrong_contract_fails(self) -> None:
        """contract != 'review_events' is rejected."""
        exp, run_dir = _setup_review_evidence_base(self.base)
        _write(
            run_dir / "review-events.yml",
            _valid_review_events().replace(
                'contract: "review_events"', 'contract: "measurement_run"'
            ),
        )
        _append_review_evidence_artifact(run_dir)
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        # Schema catches const violation; message contains "contract" and "review_events".
        self.assertTrue(
            any("review-events.yml" in e and "contract" in e and "review_events" in e
                for e in errs),
            errs,
        )

    def test_missing_contract_fails(self) -> None:
        """A review-events.yml without a contract field is rejected."""
        exp, run_dir = _setup_review_evidence_base(self.base)
        content = _valid_review_events()
        # Remove the contract line
        lines = [ln for ln in content.splitlines() if not ln.startswith("contract:")]
        _write(run_dir / "review-events.yml", "\n".join(lines) + "\n")
        _append_review_evidence_artifact(run_dir)
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        # Schema catches missing required property; message contains "contract".
        self.assertTrue(
            any("review-events.yml" in e and "contract" in e for e in errs),
            errs,
        )

    # ----- run_id mismatch ----------------------------------------------------

    def test_run_id_mismatch_fails(self) -> None:
        """run_id in review-events.yml that doesn't match the run directory is rejected."""
        exp, run_dir = _setup_review_evidence_base(self.base)
        _write(
            run_dir / "review-events.yml",
            _valid_review_events(run_id="run-999-wrong"),
        )
        _append_review_evidence_artifact(run_dir)
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertTrue(
            any("review-events.yml" in e and "run_id=" in e and "run-999-wrong" in e
                for e in errs),
            errs,
        )

    # ----- negative counts ----------------------------------------------------

    def test_negative_review_friction_count_fails(self) -> None:
        """review_friction_count < 0 is rejected."""
        exp, run_dir = _setup_review_evidence_base(self.base)
        _write(
            run_dir / "review-events.yml",
            _valid_review_events().replace(
                "review_friction_count: 2", "review_friction_count: -1"
            ),
        )
        _append_review_evidence_artifact(run_dir)
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertTrue(
            any("review-events.yml" in e and "review_friction_count" in e for e in errs),
            errs,
        )

    def test_negative_rework_count_fails(self) -> None:
        """rework_count < 0 is rejected."""
        exp, run_dir = _setup_review_evidence_base(self.base)
        _write(
            run_dir / "review-events.yml",
            _valid_review_events().replace("rework_count: 1", "rework_count: -3"),
        )
        _append_review_evidence_artifact(run_dir)
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertTrue(
            any("review-events.yml" in e and "rework_count" in e for e in errs),
            errs,
        )

    def test_string_review_friction_count_fails(self) -> None:
        """review_friction_count that is a string, not integer, is rejected."""
        exp, run_dir = _setup_review_evidence_base(self.base)
        _write(
            run_dir / "review-events.yml",
            _valid_review_events().replace(
                "review_friction_count: 2", 'review_friction_count: "two"'
            ),
        )
        _append_review_evidence_artifact(run_dir)
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertTrue(
            any("review-events.yml" in e and "review_friction_count" in e for e in errs),
            errs,
        )

    # ----- external_verified without refs -------------------------------------

    def test_external_verified_without_refs_fails(self) -> None:
        """evidence_status=external_verified without any ref list is rejected."""
        exp, run_dir = _setup_review_evidence_base(self.base)
        _write(
            run_dir / "review-events.yml",
            textwrap.dedent("""\
                schema_version: "1.0.0"
                contract: "review_events"
                run_id: "run-001"
                pr_ref: "github:test/test/pull/1"
                review_friction_count: 1
                rework_count: 0
                captured_at: "2026-05-11T00:00:00Z"
                evidence_status: "external_verified"
            """),
        )
        _append_review_evidence_artifact(run_dir)
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertTrue(
            any("review-events.yml" in e and "external_verified" in e
                and "review_thread_refs" in e for e in errs),
            errs,
        )

    def test_external_verified_empty_thread_refs_list_fails(self) -> None:
        """evidence_status=external_verified with an empty review_thread_refs list is rejected."""
        exp, run_dir = _setup_review_evidence_base(self.base)
        _write(
            run_dir / "review-events.yml",
            textwrap.dedent("""\
                schema_version: "1.0.0"
                contract: "review_events"
                run_id: "run-001"
                pr_ref: "github:test/test/pull/1"
                review_friction_count: 1
                rework_count: 0
                captured_at: "2026-05-11T00:00:00Z"
                evidence_status: "external_verified"
                review_thread_refs: []
            """),
        )
        _append_review_evidence_artifact(run_dir)
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertTrue(
            any("review-events.yml" in e and "external_verified" in e for e in errs),
            errs,
        )

    def test_external_verified_with_rework_commit_refs_passes(self) -> None:
        """evidence_status=external_verified with rework_commit_refs (not thread_refs) → PASS."""
        exp, run_dir = _setup_review_evidence_base(self.base)
        _write(
            run_dir / "review-events.yml",
            textwrap.dedent("""\
                schema_version: "1.0.0"
                contract: "review_events"
                run_id: "run-001"
                pr_ref: "github:test/test/pull/1"
                review_friction_count: 1
                rework_count: 1
                captured_at: "2026-05-11T00:00:00Z"
                evidence_status: "external_verified"
                rework_commit_refs:
                  - sha: "abc123"
                    description: "Fix reviewer comment"
            """),
        )
        _append_review_evidence_artifact(run_dir)
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertEqual(errs, [], errs)

    # ----- missing required fields -------------------------------------------

    def test_missing_captured_at_fails(self) -> None:
        """captured_at missing → error."""
        exp, run_dir = _setup_review_evidence_base(self.base)
        lines = [
            ln for ln in _valid_review_events().splitlines()
            if not ln.startswith("captured_at:")
        ]
        _write(run_dir / "review-events.yml", "\n".join(lines) + "\n")
        _append_review_evidence_artifact(run_dir)
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertTrue(
            any("review-events.yml" in e and "captured_at" in e for e in errs),
            errs,
        )

    def test_missing_pr_ref_fails(self) -> None:
        """pr_ref missing → error."""
        exp, run_dir = _setup_review_evidence_base(self.base)
        lines = [
            ln for ln in _valid_review_events().splitlines()
            if not ln.startswith("pr_ref:")
        ]
        _write(run_dir / "review-events.yml", "\n".join(lines) + "\n")
        _append_review_evidence_artifact(run_dir)
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertTrue(
            any("review-events.yml" in e and "pr_ref" in e for e in errs),
            errs,
        )

    def test_invalid_evidence_status_fails(self) -> None:
        """evidence_status with an unrecognised value is rejected."""
        exp, run_dir = _setup_review_evidence_base(self.base)
        _write(
            run_dir / "review-events.yml",
            _valid_review_events().replace(
                'evidence_status: "external_verified"',
                'evidence_status: "self_reported"',
            ),
        )
        _append_review_evidence_artifact(run_dir)
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        # Schema catches enum violation; message contains "evidence_status".
        self.assertTrue(
            any("review-events.yml" in e and "evidence_status" in e for e in errs),
            errs,
        )

    def test_external_verified_rework_commit_refs_empty_sha_fails(self) -> None:
        """evidence_status=external_verified with rework_commit_refs containing only empty sha fails."""
        exp, run_dir = _setup_review_evidence_base(self.base)
        _write(
            run_dir / "review-events.yml",
            textwrap.dedent("""\
                schema_version: "1.0.0"
                contract: "review_events"
                run_id: "run-001"
                pr_ref: "github:test/test/pull/1"
                review_friction_count: 1
                rework_count: 1
                captured_at: "2026-05-11T00:00:00Z"
                evidence_status: "external_verified"
                rework_commit_refs:
                  - sha: ""
                    description: "empty sha should not count"
            """),
        )
        _append_review_evidence_artifact(run_dir)
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        # Schema catches empty sha (minLength:1 on sha); review-events.yml fails validation.
        self.assertTrue(
            any("review-events.yml" in e for e in errs),
            errs,
        )

    # ----- evidence_status type safety ----------------------------------------

    def test_evidence_status_list_does_not_crash_gives_error(self) -> None:
        """evidence_status as a YAML list must produce a validator error, not a TypeError."""
        exp, run_dir = _setup_review_evidence_base(self.base)
        _write(
            run_dir / "review-events.yml",
            textwrap.dedent("""\
                schema_version: "1.0.0"
                contract: "review_events"
                run_id: "run-001"
                pr_ref: "github:test/test/pull/1"
                review_friction_count: 1
                rework_count: 0
                captured_at: "2026-05-11T12:00:00Z"
                evidence_status:
                  - repo_local
                  - ci_artifact
                review_thread_refs:
                  - "https://github.com/test/test/pull/1#issuecomment-1001"
            """),
        )
        _append_review_evidence_artifact(run_dir)
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertTrue(
            any("review-events.yml" in e and "evidence_status" in e for e in errs),
            errs,
        )

    def test_evidence_status_dict_does_not_crash_gives_error(self) -> None:
        """evidence_status as a YAML mapping must produce a validator error, not a TypeError."""
        exp, run_dir = _setup_review_evidence_base(self.base)
        _write(
            run_dir / "review-events.yml",
            textwrap.dedent("""\
                schema_version: "1.0.0"
                contract: "review_events"
                run_id: "run-001"
                pr_ref: "github:test/test/pull/1"
                review_friction_count: 1
                rework_count: 0
                captured_at: "2026-05-11T12:00:00Z"
                evidence_status:
                  type: repo_local
                review_thread_refs:
                  - "https://github.com/test/test/pull/1#issuecomment-1001"
            """),
        )
        _append_review_evidence_artifact(run_dir)
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertTrue(
            any("review-events.yml" in e and "evidence_status" in e for e in errs),
            errs,
        )

    # ----- captured_at ISO-8601 validation ------------------------------------

    def test_captured_at_invalid_string_fails(self) -> None:
        """captured_at: "yesterday" (non-ISO string) fails with a timestamp error."""
        exp, run_dir = _setup_review_evidence_base(self.base)
        _write(
            run_dir / "review-events.yml",
            _valid_review_events().replace(
                'captured_at: "2026-05-11T12:00:00Z"',
                'captured_at: "yesterday"',
            ),
        )
        _append_review_evidence_artifact(run_dir)
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertTrue(
            any(
                "review-events.yml" in e
                and "captured_at" in e
                and "ISO-8601" in e
                for e in errs
            ),
            errs,
        )

    def test_captured_at_date_only_fails(self) -> None:
        """captured_at: "2026-05-11" must fail (date-only is not a timestamp)."""
        exp, run_dir = _setup_review_evidence_base(self.base)
        _write(
            run_dir / "review-events.yml",
            _valid_review_events().replace(
                'captured_at: "2026-05-11T12:00:00Z"',
                'captured_at: "2026-05-11"',
            ),
        )
        _append_review_evidence_artifact(run_dir)
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertTrue(
            any("review-events.yml" in e and "captured_at" in e for e in errs),
            errs,
        )

    def test_captured_at_valid_timestamp_passes(self) -> None:
        """captured_at: "2026-05-11T12:00:00Z" is a valid ISO-8601 timestamp and passes."""
        exp, run_dir = _setup_review_evidence_base(self.base)
        _write(run_dir / "review-events.yml", _valid_review_events())
        _append_review_evidence_artifact(run_dir)
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertEqual(errs, [], errs)

    # ----- diagnostic path for subdir artifacts --------------------------------

    def test_subdir_artifact_invalid_content_error_contains_subdir(self) -> None:
        """An artifact in a subdir of run_dir shows the subdir path in the error message."""
        exp, run_dir = _setup_review_evidence_base(self.base)
        subdir = run_dir / "meta"
        subdir.mkdir()
        _write(
            subdir / "review-events.yml",
            textwrap.dedent("""\
                schema_version: "1.0.0"
                contract: "wrong_contract"
                run_id: "run-001"
                pr_ref: "github:test/test/pull/1"
                review_friction_count: 1
                rework_count: 0
                captured_at: "2026-05-11T12:00:00Z"
                evidence_status: "repo_local"
            """),
        )
        _append_review_evidence_artifact(run_dir, ref="meta/review-events.yml")
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        # Error message must include the subdir component so it is findable on disk.
        # Schema catches the contract const violation; message contains "contract".
        self.assertTrue(
            any("meta" in e and "review-events.yml" in e and "contract" in e for e in errs),
            errs,
        )


# ---------------------------------------------------------------------------
# Schema-backed enforcement tests for review-events.yml
# (new in v0.2 — these tests required schemas/review-events.v1.schema.json)
# ---------------------------------------------------------------------------

class ReviewEventsSchemaBackedTests(unittest.TestCase):
    """Tests that specifically verify schema-backed enforcement not possible before v0.2.

    Each test documents WHY it was not deterministically testable before the schema:
    - additionalProperties: false — the semantic validator ignored unknown fields
    - schema_version const — the semantic validator never checked this field
    - schema isolation — validate_repo() must raise when schema file is absent

    Path-escape test for review_evidence_artifact is also here since it verifies
    the containment guard works for review-events specifically.
    """

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)
        _make_repo_skeleton(self.base)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_unknown_additional_field_rejected_by_schema(self) -> None:
        """additionalProperties:false — an unknown field in review-events.yml fails.

        Before schemas/review-events.v1.schema.json existed, the semantic validator
        silently ignored unknown fields. This test is only deterministic with a schema.
        """
        exp, run_dir = _setup_review_evidence_base(self.base)
        _write(
            run_dir / "review-events.yml",
            textwrap.dedent("""\
                schema_version: "1.0.0"
                contract: "review_events"
                run_id: "run-001"
                pr_ref: "github:test/test/pull/1"
                review_friction_count: 1
                rework_count: 0
                captured_at: "2026-05-11T12:00:00Z"
                evidence_status: "repo_local"
                unknown_extra_field: "this should be rejected"
            """),
        )
        _append_review_evidence_artifact(run_dir)
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertTrue(
            any("review-events.yml" in e and "schema-invalid" in e for e in errs),
            errs,
        )

    def test_repo_local_metrics_with_schema_invalid_review_events_are_blocked(self) -> None:
        """repo_local review/rework metrics require content-valid review-events.yml, not just an existing path."""
        exp = _build_valid_bundle(
            self.base,
            comparability_text=_valid_comparability_yml(
                verdict="comparable",
                changed_files_artifact="changed-files.txt",
            ),
            measurement_text=textwrap.dedent("""\
                schema_version: "1.0.0"
                contract: "measurement_run"
                run_id: "run-001"
                auditor_verdict: "MISSING_EVIDENCE"
                auditor_ref: "auditor-output.yml"
                metrics:
                  scope_drift_count:
                    value: 0
                    evidence_status: "external_unverified"
                  unsupported_claim_count:
                    value: 2
                    evidence_status: "derived_from_auditor_output"
                  missing_locator_count:
                    value: 0
                    evidence_status: "external_unverified"
                  validation_gap_count:
                    value: 2
                    evidence_status: "derived_from_auditor_output"
                  review_friction_count:
                    value: 2
                    evidence_status: "repo_local"
                  rework_count:
                    value: 1
                    evidence_status: "repo_local"
                  false_block_count:
                    value: 0
                    evidence_status: "external_unverified"
                  task_completion_time_observed:
                    value: "n/a"
                    evidence_status: "external_unverified"
            """),
        )
        run_dir = exp / "artifacts" / "run-001"
        _write_changed_files_artifact(run_dir)
        _write(
            run_dir / "review-events.yml",
            textwrap.dedent("""\
                schema_version: "0.9.0"
                contract: "review_events"
                run_id: "run-001"
                pr_ref: "github:test/test/pull/1"
                review_friction_count: 2
                rework_count: 1
                captured_at: "2026-05-11T12:00:00Z"
                evidence_status: "repo_local"
            """),
        )
        _append_review_evidence_artifact(run_dir)
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertTrue(
            any("review-events.yml" in e and "schema-invalid" in e for e in errs),
            errs,
        )
        self.assertTrue(
            any(
                "review_friction_count.evidence_status=repo_local" in e
                and "gültiges review_evidence_artifact" in e
                for e in errs
            ),
            errs,
        )
        self.assertTrue(
            any(
                "rework_count.evidence_status=repo_local" in e
                and "gültiges review_evidence_artifact" in e
                for e in errs
            ),
            errs,
        )

    def test_wrong_schema_version_rejected_by_schema(self) -> None:
        """schema_version != '1.0.0' fails.

        Before the schema existed, the semantic validator never checked schema_version.
        Only the schema const enforcement catches this deterministically.
        """
        exp, run_dir = _setup_review_evidence_base(self.base)
        _write(
            run_dir / "review-events.yml",
            textwrap.dedent("""\
                schema_version: "0.9.0"
                contract: "review_events"
                run_id: "run-001"
                pr_ref: "github:test/test/pull/1"
                review_friction_count: 1
                rework_count: 0
                captured_at: "2026-05-11T12:00:00Z"
                evidence_status: "repo_local"
            """),
        )
        _append_review_evidence_artifact(run_dir)
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertTrue(
            any("review-events.yml" in e and "schema-invalid" in e and "schema_version" in e
                for e in errs),
            errs,
        )

    def test_captured_at_without_timezone_fails(self) -> None:
        """captured_at without Z/offset must fail even if datetime.fromisoformat can parse it."""
        exp, run_dir = _setup_review_evidence_base(self.base)
        _write(
            run_dir / "review-events.yml",
            _valid_review_events().replace(
                'captured_at: "2026-05-11T12:00:00Z"',
                'captured_at: "2026-05-11T12:00:00"',
            ),
        )
        _append_review_evidence_artifact(run_dir)
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertTrue(
            any("review-events.yml" in e and "captured_at" in e and "Zeitzone" in e for e in errs)
            or any("review-events.yml" in e and "captured_at" in e and "timezone-aware" in e for e in errs),
            errs,
        )

    def test_schema_isolation_missing_review_events_schema_raises(self) -> None:
        """validate_repo() must raise FileNotFoundError when review-events schema is absent."""
        exp, run_dir = _setup_review_evidence_base(self.base)
        _write(run_dir / "review-events.yml", _valid_review_events())
        _append_review_evidence_artifact(run_dir)
        (self.base / "schemas" / _REVIEW_EVENTS_SCHEMA).unlink()
        with self.assertRaises(FileNotFoundError):
            validate_repo(self.base)

    def test_review_evidence_artifact_parent_escape_fails(self) -> None:
        """review_evidence_artifact: '../review-events.yml' (path escape) → error.

        Mirrors test_changed_files_artifact_parent_escape_fails for the review-events
        artifact reference. The containment guard in _load_comparability_run_artifact_ref
        must reject traversal outside the run directory.
        """
        exp = _build_valid_bundle(
            self.base,
            comparability_text=_valid_comparability_yml(
                verdict="comparable",
                changed_files_artifact="changed-files.txt",
            ),
        )
        run_dir = exp / "artifacts" / "run-001"
        _write_changed_files_artifact(run_dir)
        comp_path = run_dir / "comparability.yml"
        comp_path.write_text(
            comp_path.read_text(encoding="utf-8")
            + '\nreview_evidence_artifact: "../review-events.yml"\n',
            encoding="utf-8",
        )
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertTrue(
            any(
                "review_evidence_artifact" in e
                and "run-lokal oder experiment-relativ auf dieses Run-Verzeichnis zeigen" in e
                for e in errs
            ),
            errs,
        )

    def test_repo_local_review_rework_with_valid_schema_backed_artifact_passes(self) -> None:
        """PASS: repo_local review/rework metrics with a schema-valid review-events.yml.

        This is the canonical happy-path: review-events.yml passes both schema and semantic
        checks, enabling repo_local evidence_status for both metrics. This test verifies the
        complete chain from contract to schema to semantic to measurement validation.
        """
        exp = _build_valid_bundle(
            self.base,
            comparability_text=_valid_comparability_yml(
                verdict="comparable",
                changed_files_artifact="changed-files.txt",
            ),
            measurement_text=textwrap.dedent("""\
                schema_version: "1.0.0"
                contract: "measurement_run"
                run_id: "run-001"
                auditor_verdict: "MISSING_EVIDENCE"
                auditor_ref: "auditor-output.yml"
                metrics:
                  scope_drift_count:
                    value: 0
                    evidence_status: "external_unverified"
                  unsupported_claim_count:
                    value: 2
                    evidence_status: "derived_from_auditor_output"
                  missing_locator_count:
                    value: 0
                    evidence_status: "external_unverified"
                  validation_gap_count:
                    value: 2
                    evidence_status: "derived_from_auditor_output"
                  review_friction_count:
                    value: 2
                    evidence_status: "repo_local"
                  rework_count:
                    value: 1
                    evidence_status: "repo_local"
                  false_block_count:
                    value: 0
                    evidence_status: "external_unverified"
                  task_completion_time_observed:
                    value: "n/a"
                    evidence_status: "external_unverified"
            """),
        )
        run_dir = exp / "artifacts" / "run-001"
        _write_changed_files_artifact(run_dir)
        _write(
            run_dir / "review-events.yml",
            textwrap.dedent("""\
                schema_version: "1.0.0"
                contract: "review_events"
                run_id: "run-001"
                pr_ref: "github:test/test/pull/1"
                review_friction_count: 2
                rework_count: 1
                captured_at: "2026-05-11T12:00:00Z"
                evidence_status: "repo_local"
                notes: "schema-backed repo_local evidence"
            """),
        )
        comp_path = run_dir / "comparability.yml"
        comp_path.write_text(
            comp_path.read_text(encoding="utf-8")
            + '\nreview_evidence_artifact: "review-events.yml"\n',
            encoding="utf-8",
        )
        _write_legacy_allowlist(self.base, [_run_yml_repo_path("exp-fixture", "run-001")])
        errs = validate_repo(self.base)
        self.assertEqual(errs, [], errs)


if __name__ == "__main__":
    unittest.main()
