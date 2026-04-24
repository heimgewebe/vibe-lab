#!/usr/bin/env python3
"""Regression tests for validate_promotion_readiness.py.

Covers:
  1. executed experiment without falsifiability → not_ready
  2. executed experiment with valid falsifiability → ready
  3. adopted + adoption_basis=executed without falsifiability → not_ready
  4. adopted + adoption_basis=reconstructed without falsifiability → historical_escape
     (non-blocking, not counted as not_ready)
  5. counterevidence_checked=false → counterevidence_not_checked warning
  6. designed/prepared experiments → no trigger, counted ready with notes=[]
  7. Two runs produce identical output (determinism / write_if_changed).
  8. Falsifiability block loaded from the valid/invalid fixtures shows expected structure.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

# Make the validator importable (lives in the same directory).
THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR))

import validate_promotion_readiness as vpr  # noqa: E402


VALID_FALSIFIABILITY = {
    "counter_hypothesis": "Die Verbesserung ist möglicherweise durch Promptlänge erklärbar, nicht durch Spec-First.",
    "falsification_criterion": "Ein längengleicher Nicht-Spec-Prompt liefert vergleichbare Ergebnisse.",
    "counterevidence_checked": True,
}


def make_manifest(
    *,
    status: str,
    execution_status: str,
    adoption_basis: str | None = None,
    falsifiability: dict | None = None,
) -> dict:
    exp: dict = {
        "name": "fixture",
        "hypothesis": "placeholder",
        "status": status,
        "category": "technique",
        "evidence_level": "experimental",
        "execution_status": execution_status,
    }
    if adoption_basis is not None:
        exp["adoption_basis"] = adoption_basis
    if falsifiability is not None:
        exp["falsifiability"] = falsifiability
    return {"schema_version": "0.1.0", "experiment": exp}


class ClassifyAndTriggerTests(unittest.TestCase):
    def test_trigger_executed(self) -> None:
        state = vpr.classify_experiment(
            make_manifest(status="testing", execution_status="executed")
        )
        self.assertTrue(vpr.falsifiability_trigger(state))

    def test_trigger_replicated(self) -> None:
        state = vpr.classify_experiment(
            make_manifest(status="testing", execution_status="replicated")
        )
        self.assertTrue(vpr.falsifiability_trigger(state))

    def test_no_trigger_designed(self) -> None:
        state = vpr.classify_experiment(
            make_manifest(status="designed", execution_status="designed")
        )
        self.assertFalse(vpr.falsifiability_trigger(state))

    def test_no_trigger_prepared(self) -> None:
        state = vpr.classify_experiment(
            make_manifest(status="testing", execution_status="prepared")
        )
        self.assertFalse(vpr.falsifiability_trigger(state))

    def test_trigger_adopted_executed_basis(self) -> None:
        state = vpr.classify_experiment(
            make_manifest(
                status="adopted",
                execution_status="executed",
                adoption_basis="executed",
            )
        )
        self.assertTrue(vpr.falsifiability_trigger(state))

    def test_reconstructed_historical_escape_not_blocking(self) -> None:
        state = vpr.classify_experiment(
            make_manifest(
                status="adopted",
                execution_status="reconstructed",
                adoption_basis="reconstructed",
            )
        )
        # Trigger greift nicht auf reconstructed; zusätzlich markiert als historical escape.
        self.assertFalse(vpr.falsifiability_trigger(state))
        self.assertTrue(vpr.is_historical_escape(state))


class EvaluateFalsifiabilityTests(unittest.TestCase):
    def test_missing_block(self) -> None:
        state = vpr.classify_experiment(
            make_manifest(status="testing", execution_status="executed")
        )
        missing, warnings = vpr.evaluate_falsifiability(state)
        self.assertIn("falsifiability", missing)
        self.assertEqual(warnings, [])

    def test_valid_block(self) -> None:
        state = vpr.classify_experiment(
            make_manifest(
                status="testing",
                execution_status="executed",
                falsifiability=dict(VALID_FALSIFIABILITY),
            )
        )
        missing, warnings = vpr.evaluate_falsifiability(state)
        self.assertEqual(missing, [])
        self.assertEqual(warnings, [])

    def test_counterevidence_false_is_warning_not_missing(self) -> None:
        state = vpr.classify_experiment(
            make_manifest(
                status="testing",
                execution_status="executed",
                falsifiability={
                    **VALID_FALSIFIABILITY,
                    "counterevidence_checked": False,
                },
            )
        )
        missing, warnings = vpr.evaluate_falsifiability(state)
        self.assertEqual(missing, [])
        self.assertIn("counterevidence_not_checked", warnings)

    def test_missing_subfields(self) -> None:
        state = vpr.classify_experiment(
            make_manifest(
                status="testing",
                execution_status="executed",
                falsifiability={"counter_hypothesis": "only this one is present enough"},
            )
        )
        missing, _ = vpr.evaluate_falsifiability(state)
        self.assertIn("falsifiability.falsification_criterion", missing)
        self.assertIn("falsifiability.counterevidence_checked", missing)

    def test_too_short_counter_hypothesis(self) -> None:
        state = vpr.classify_experiment(
            make_manifest(
                status="testing",
                execution_status="executed",
                falsifiability={
                    "counter_hypothesis": "short",
                    "falsification_criterion": "long enough string",
                    "counterevidence_checked": True,
                },
            )
        )
        missing, _ = vpr.evaluate_falsifiability(state)
        self.assertIn("falsifiability.counter_hypothesis_too_short", missing)


class FixtureShapeTests(unittest.TestCase):
    """Structural checks against the committed fixtures."""

    def setUp(self) -> None:
        self.fixture_dir = (
            vpr.REPO_ROOT / "tests" / "fixtures" / "falsifiability"
        )

    def _load(self, name: str) -> dict:
        with open(self.fixture_dir / name) as f:
            return json.load(f)

    def test_valid_fixture_has_all_fields(self) -> None:
        payload = self._load("valid.json")
        fal = payload["falsifiability"]
        for field in vpr.FALSIFIABILITY_FIELDS:
            self.assertIn(field, fal)
        self.assertGreaterEqual(
            len(fal["counter_hypothesis"].strip()), vpr.FALSIFIABILITY_MIN_LEN
        )
        self.assertGreaterEqual(
            len(fal["falsification_criterion"].strip()), vpr.FALSIFIABILITY_MIN_LEN
        )

    def test_invalid_fixture_triggers_missing_entries(self) -> None:
        payload = self._load("invalid.json")
        # Simuliere als Experiment-State und werte aus.
        state = {
            "status": "testing",
            "execution_status": "executed",
            "adoption_basis": "",
            "falsifiability": payload["falsifiability"],
        }
        missing, _ = vpr.evaluate_falsifiability(state)
        self.assertIn("falsifiability.counterevidence_checked", missing)
        self.assertIn("falsifiability.counter_hypothesis_too_short", missing)
        self.assertIn("falsifiability.falsification_criterion_too_short", missing)


class IsolatedRepoScenarios(unittest.TestCase):
    """Run the validator against a synthetic experiments/ tree to assert end-to-end behavior."""

    def _write_manifest(self, path: Path, manifest: dict) -> None:
        import yaml as _yaml
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")

    def _evaluate_dir(self, root: Path) -> list[dict]:
        entries = []
        for sub in sorted(root.iterdir()):
            if not sub.is_dir():
                continue
            entry = vpr.evaluate_experiment(sub)
            if entry is not None:
                entries.append(entry)
        return entries

    def test_full_scenario_matrix(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_manifest(
                root / "exp-executed-no-fal" / "manifest.yml",
                make_manifest(status="testing", execution_status="executed"),
            )
            self._write_manifest(
                root / "exp-executed-with-fal" / "manifest.yml",
                make_manifest(
                    status="testing",
                    execution_status="executed",
                    falsifiability=dict(VALID_FALSIFIABILITY),
                ),
            )
            self._write_manifest(
                root / "exp-adopted-executed-basis" / "manifest.yml",
                make_manifest(
                    status="adopted",
                    execution_status="executed",
                    adoption_basis="executed",
                ),
            )
            self._write_manifest(
                root / "exp-adopted-reconstructed" / "manifest.yml",
                make_manifest(
                    status="adopted",
                    execution_status="reconstructed",
                    adoption_basis="reconstructed",
                ),
            )
            self._write_manifest(
                root / "exp-designed" / "manifest.yml",
                make_manifest(status="designed", execution_status="designed"),
            )

            # Patch evaluate_experiment's REPO_ROOT via relative path — we need the
            # test to evaluate against this temp root, not REPO_ROOT. Work directly
            # with evaluate_experiment by temporarily overriding REPO_ROOT.
            original_root = vpr.REPO_ROOT
            try:
                vpr.REPO_ROOT = root
                entries = self._evaluate_dir(root)
            finally:
                vpr.REPO_ROOT = original_root

            by_name = {Path(e["path"]).name: e for e in entries}

            # 1. executed without falsifiability → not_ready
            self.assertFalse(by_name["exp-executed-no-fal"]["promotion_ready"])
            self.assertIn("falsifiability", by_name["exp-executed-no-fal"]["missing"])

            # 2. executed with valid falsifiability → ready
            self.assertTrue(by_name["exp-executed-with-fal"]["promotion_ready"])

            # 3. adopted + adoption_basis=executed without falsifiability → not_ready
            self.assertFalse(by_name["exp-adopted-executed-basis"]["promotion_ready"])
            self.assertTrue(
                by_name["exp-adopted-executed-basis"]["falsifiability_triggered"]
            )

            # 4. adopted + adoption_basis=reconstructed → historical escape, not blocking
            rec = by_name["exp-adopted-reconstructed"]
            self.assertTrue(rec["historical_escape"])
            self.assertFalse(rec["falsifiability_triggered"])
            self.assertIn("historical_escape", rec["notes"])
            self.assertEqual(rec["missing"], [])

            # 5. designed experiment → trigger not greift → promotion_ready True
            self.assertTrue(by_name["exp-designed"]["promotion_ready"])
            self.assertFalse(by_name["exp-designed"]["falsifiability_triggered"])


class DeterminismTests(unittest.TestCase):
    def test_report_rendering_is_deterministic(self) -> None:
        entry = {
            "path": "experiments/foo",
            "status": "testing",
            "execution_status": "executed",
            "adoption_basis": "",
            "falsifiability_triggered": True,
            "historical_escape": False,
            "promotion_ready": False,
            "missing": ["falsifiability"],
            "warnings": [],
            "notes": [],
        }
        report_a = vpr.build_report([entry])
        report_b = vpr.build_report([dict(entry)])
        self.assertEqual(vpr.render_report(report_a), vpr.render_report(report_b))

    def test_report_has_no_timestamp_key(self) -> None:
        report = vpr.build_report([])
        rendered = vpr.render_report(report)
        # Expliziter Guard gegen accidentelle Einführung von Zeitstempeln.
        self.assertNotIn("timestamp", rendered)
        self.assertNotIn("generated_at", rendered)

    def test_report_shape_has_required_keys(self) -> None:
        report = vpr.build_report([])
        for key in ("schema_version", "mode", "trigger", "summary", "experiments"):
            self.assertIn(key, report)
        self.assertEqual(report["mode"], "dry_run")
        self.assertEqual(report["trigger"], "need_for_reproducibility")


class CrossRuleDocumentationTests(unittest.TestCase):
    """Covers P2 rule expectations at the decision layer.

    The actual enforcement lives in scripts/docmeta/validate_schema.py::validate_decision_files;
    here we just pin the invariants the promotion-readiness validator assumes
    downstream (counterevidence_not_checked is a warning, not a missing field).
    """

    def test_confirms_plus_no_counterevidence_is_warning_not_missing(self) -> None:
        state = vpr.classify_experiment(
            make_manifest(
                status="testing",
                execution_status="executed",
                falsifiability={
                    **VALID_FALSIFIABILITY,
                    "counterevidence_checked": False,
                },
            )
        )
        missing, warnings = vpr.evaluate_falsifiability(state)
        self.assertNotIn("falsifiability.counterevidence_checked", missing)
        self.assertIn("counterevidence_not_checked", warnings)


if __name__ == "__main__":
    unittest.main(verbosity=2)
