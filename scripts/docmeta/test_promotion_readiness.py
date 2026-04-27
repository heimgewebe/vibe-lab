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

    def test_non_string_fields_are_flagged(self) -> None:
        state = vpr.classify_experiment(
            make_manifest(
                status="testing",
                execution_status="executed",
                falsifiability={
                    "counter_hypothesis": 123,
                    "falsification_criterion": {"bad": True},
                    "counterevidence_checked": True,
                },
            )
        )
        missing, _ = vpr.evaluate_falsifiability(state)
        self.assertIn("falsifiability.counter_hypothesis_not_string", missing)
        self.assertIn("falsifiability.falsification_criterion_not_string", missing)


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


def make_structured_falsifiability(
    *,
    falsification_criterion: str = "Wenn Kontrollarm gleiche Ergebnisse zeigt wie Behandlungsarm, ist der Effekt nicht kausal.",
    counter_hypotheses: list | None = None,
) -> dict:
    """Helper: builds a minimal valid structured v1 falsifiability block."""
    if counter_hypotheses is None:
        counter_hypotheses = [
            {
                "id": "ceiling_effect",
                "statement": "Der Effekt entsteht durch Ceiling-Effekt, nicht durch die Intervention.",
                "assessment": {
                    "status": "checked",
                    "outcome": "supports_primary",
                    "evidence_refs": [{"path": "results/evidence.jsonl"}],
                    "pending_checks": [],
                    "limitations": [],
                    "confidence": "medium",
                },
            }
        ]
    return {
        "version": 1,
        "falsification_criterion": falsification_criterion,
        "counter_hypotheses": counter_hypotheses,
    }


class StructuredFalsifiabilityTests(unittest.TestCase):
    """Tests for the structured v1 falsifiability evaluation path.

    Tests 1–10 from the contract specification:
      1. documented/not_checked → not_ready (assessment_not_checked in missing)
      2. pending/not_checked → not_ready (assessment_not_checked in missing)
      3. partially_checked/inconclusive + pending_checks → not_ready (assessment_pending_blocking)
      4. checked/supports_primary + evidence_refs + no pending → ready
      5. supports_counterhypothesis → not_ready (assessment_counterhypothesis_supported)
      6. mixed outcome distinct from inconclusive (both produce signals)
      7. blocked → not_ready (assessment_blocked)
      8. multiple counter_hypotheses supported
      9. checked without evidence_refs → warning (non-blocking for supports_primary)
      10. historical_escape with structured format not counted against not_ready
    Plus: legacy and structured routing, falsification_criterion validation.
    """

    def _eval(self, falsifiability: dict) -> tuple[list[str], list[str]]:
        state = vpr.classify_experiment(
            make_manifest(
                status="testing",
                execution_status="executed",
                falsifiability=falsifiability,
            )
        )
        return vpr.evaluate_falsifiability(state)

    # --- Test 1: documented → not_ready ---
    def test_documented_is_not_ready(self) -> None:
        missing, warnings = self._eval(
            make_structured_falsifiability(
                counter_hypotheses=[{
                    "id": "h1",
                    "statement": "Alternativerklärung: der Effekt kommt von einer Drittvariable.",
                    "assessment": {"status": "documented", "outcome": "not_checked"},
                }]
            )
        )
        self.assertIn("falsifiability.assessment_not_checked", missing)
        self.assertNotIn("falsifiability.assessment_pending_blocking", missing)

    # --- Test 2: pending → not_ready ---
    def test_pending_is_not_ready(self) -> None:
        missing, _ = self._eval(
            make_structured_falsifiability(
                counter_hypotheses=[{
                    "id": "h1",
                    "statement": "Alternativerklärung: Reihenfolgeeffekt erklärt alle Ergebnisse.",
                    "assessment": {"status": "pending", "outcome": "not_checked"},
                }]
            )
        )
        self.assertIn("falsifiability.assessment_not_checked", missing)

    # --- Test 3: partially_checked/inconclusive + pending_checks → not_ready ---
    def test_partially_checked_inconclusive_with_pending_is_not_ready(self) -> None:
        missing, warnings = self._eval(
            make_structured_falsifiability(
                counter_hypotheses=[{
                    "id": "ceiling_effect",
                    "statement": "Der 0/0-Drift entsteht durch Ceiling-Effekt, nicht durch das Protokoll.",
                    "assessment": {
                        "status": "partially_checked",
                        "outcome": "inconclusive",
                        "evidence_refs": [{"path": "results/result.md"}],
                        "pending_checks": ["Iteration-4-Ausführung"],
                    },
                }]
            )
        )
        self.assertIn("falsifiability.assessment_pending_blocking", missing)
        self.assertNotIn("falsifiability.assessment_not_checked", missing)

    # --- Test 3b: partially_checked/inconclusive without pending_checks → warning only ---
    def test_partially_checked_inconclusive_no_pending_is_warning_only(self) -> None:
        missing, warnings = self._eval(
            make_structured_falsifiability(
                counter_hypotheses=[{
                    "id": "ceiling_effect",
                    "statement": "Der Effekt entsteht durch Ceiling-Effekt, alle geplanten Checks durchgeführt.",
                    "assessment": {
                        "status": "partially_checked",
                        "outcome": "inconclusive",
                        "evidence_refs": [{"path": "results/result.md"}],
                        "pending_checks": [],
                    },
                }]
            )
        )
        self.assertNotIn("falsifiability.assessment_pending_blocking", missing)
        self.assertNotIn("falsifiability.assessment_not_checked", missing)
        self.assertIn("falsifiability_assessment_inconclusive", warnings)

    # --- Test 4: checked/supports_primary + evidence_refs + no pending → ready ---
    def test_checked_supports_primary_no_pending_is_ready(self) -> None:
        missing, warnings = self._eval(make_structured_falsifiability())
        self.assertEqual(missing, [])
        self.assertEqual(warnings, [])

    # --- Test 5: supports_counterhypothesis → not_ready ---
    def test_supports_counterhypothesis_is_not_ready(self) -> None:
        missing, _ = self._eval(
            make_structured_falsifiability(
                counter_hypotheses=[{
                    "id": "h1",
                    "statement": "Token-Volumen erklärt den Effekt vollständig, nicht Spec-First.",
                    "assessment": {
                        "status": "checked",
                        "outcome": "supports_counterhypothesis",
                        "evidence_refs": [{"path": "results/evidence.jsonl"}],
                    },
                }]
            )
        )
        self.assertIn("falsifiability.assessment_counterhypothesis_supported", missing)

    # --- Test 6: mixed outcome is distinct from inconclusive ---
    def test_mixed_with_pending_is_not_ready(self) -> None:
        missing, _ = self._eval(
            make_structured_falsifiability(
                counter_hypotheses=[{
                    "id": "h1",
                    "statement": "Gemischte Evidenz: einige Runs stützen die Haupthypothese, andere die Gegenhypothese.",
                    "assessment": {
                        "status": "checked",
                        "outcome": "mixed",
                        "evidence_refs": [{"path": "results/evidence.jsonl"}],
                        "pending_checks": ["Weiterer unabhängiger Run"],
                    },
                }]
            )
        )
        self.assertIn("falsifiability.assessment_pending_blocking", missing)

    def test_mixed_no_pending_is_warning_only(self) -> None:
        missing, warnings = self._eval(
            make_structured_falsifiability(
                counter_hypotheses=[{
                    "id": "h1",
                    "statement": "Gemischte Evidenz ohne ausstehende Checks: alle Prüfungen abgeschlossen.",
                    "assessment": {
                        "status": "checked",
                        "outcome": "mixed",
                        "evidence_refs": [{"path": "results/evidence.jsonl"}],
                        "pending_checks": [],
                    },
                }]
            )
        )
        self.assertNotIn("falsifiability.assessment_pending_blocking", missing)
        self.assertIn("falsifiability_assessment_inconclusive", warnings)

    # --- Test 7: blocked → not_ready ---
    def test_blocked_is_not_ready(self) -> None:
        missing, _ = self._eval(
            make_structured_falsifiability(
                counter_hypotheses=[{
                    "id": "h1",
                    "statement": "Externer Review war geplant, konnte aber nicht durchgeführt werden.",
                    "assessment": {"status": "blocked", "outcome": "not_applicable"},
                }]
            )
        )
        self.assertIn("falsifiability.assessment_blocked", missing)

    # --- Test 8: multiple counter_hypotheses ---
    def test_multiple_hypotheses_all_ready(self) -> None:
        missing, warnings = self._eval(
            make_structured_falsifiability(
                counter_hypotheses=[
                    {
                        "id": "h1",
                        "statement": "Erste Gegenhypothese: Effekt durch Promptlänge erklärbar.",
                        "assessment": {
                            "status": "checked",
                            "outcome": "supports_primary",
                            "evidence_refs": [{"path": "results/evidence.jsonl"}],
                            "pending_checks": [],
                        },
                    },
                    {
                        "id": "h2",
                        "statement": "Zweite Gegenhypothese: Effekt durch Executor-Bias erklärbar.",
                        "assessment": {
                            "status": "checked",
                            "outcome": "supports_primary",
                            "evidence_refs": [{"path": "artifacts/review.md"}],
                            "pending_checks": [],
                        },
                    },
                ]
            )
        )
        self.assertEqual(missing, [])

    def test_multiple_hypotheses_one_blocking(self) -> None:
        missing, _ = self._eval(
            make_structured_falsifiability(
                counter_hypotheses=[
                    {
                        "id": "h1",
                        "statement": "Erste Gegenhypothese: geprüft und primäre Hypothese gestützt.",
                        "assessment": {
                            "status": "checked",
                            "outcome": "supports_primary",
                            "evidence_refs": [{"path": "results/evidence.jsonl"}],
                            "pending_checks": [],
                        },
                    },
                    {
                        "id": "h2",
                        "statement": "Zweite Gegenhypothese: noch nicht geprüft, nur dokumentiert.",
                        "assessment": {"status": "documented", "outcome": "not_checked"},
                    },
                ]
            )
        )
        self.assertIn("falsifiability.assessment_not_checked", missing)

    # --- Test 9: checked without evidence_refs → warning (non-blocking for supports_primary) ---
    def test_checked_supports_primary_no_evidence_refs_warns(self) -> None:
        missing, warnings = self._eval(
            make_structured_falsifiability(
                counter_hypotheses=[{
                    "id": "h1",
                    "statement": "Gegenhypothese geprüft ohne explizite Evidenzreferenzen.",
                    "assessment": {
                        "status": "checked",
                        "outcome": "supports_primary",
                        "pending_checks": [],
                    },
                }]
            )
        )
        self.assertEqual(missing, [])
        self.assertIn("falsifiability.evidence_refs_missing", warnings)

    # --- Test 10: historical_escape with structured format → not counted against not_ready ---
    def test_historical_escape_with_structured_format(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            import yaml as _yaml
            root = Path(td)
            exp_dir = root / "exp-historical-structured"
            exp_dir.mkdir()
            manifest = {
                "schema_version": "0.1.0",
                "experiment": {
                    "name": "historical",
                    "hypothesis": "placeholder",
                    "status": "adopted",
                    "category": "technique",
                    "evidence_level": "experimental",
                    "execution_status": "reconstructed",
                    "adoption_basis": "reconstructed",
                    "falsifiability": make_structured_falsifiability(
                        counter_hypotheses=[{
                            "id": "h1",
                            "statement": "Historische Gegenhypothese, noch nicht geprüft.",
                            "assessment": {"status": "documented", "outcome": "not_checked"},
                        }]
                    ),
                },
            }
            (exp_dir / "manifest.yml").write_text(
                _yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8"
            )
            original_root = vpr.REPO_ROOT
            try:
                vpr.REPO_ROOT = root
                entry = vpr.evaluate_experiment(exp_dir)
            finally:
                vpr.REPO_ROOT = original_root

            self.assertIsNotNone(entry)
            self.assertTrue(entry["historical_escape"])
            self.assertIn("historical_escape", entry["notes"])
            self.assertIn("not_counted_against_promotion_readiness", entry["notes"])
            # Blocking signals from structured evaluation are not counted for historical_escape.
            self.assertEqual(entry["missing"], [])

    # --- Structured routing: counter_hypotheses key triggers structured evaluator ---
    def test_structured_routing_detected_by_key(self) -> None:
        fal = make_structured_falsifiability()
        self.assertTrue(vpr._is_structured(fal))
        fal_legacy = {"counter_hypothesis": "x" * 15, "falsification_criterion": "y" * 15, "counterevidence_checked": True}
        self.assertFalse(vpr._is_structured(fal_legacy))

    # --- falsification_criterion required in structured format ---
    def test_structured_missing_falsification_criterion_is_blocking(self) -> None:
        missing, _ = self._eval(
            {
                "version": 1,
                "counter_hypotheses": [{
                    "id": "h1",
                    "statement": "Gegenhypothese ohne übergeordnetes Falsifizierungskriterium.",
                    "assessment": {"status": "checked", "outcome": "supports_primary"},
                }],
            }
        )
        self.assertIn("falsifiability.falsification_criterion_missing_or_short", missing)

    # --- empty counter_hypotheses list is blocking ---
    def test_structured_empty_counter_hypotheses_is_blocking(self) -> None:
        missing, _ = self._eval({"version": 1, "falsification_criterion": "Kriterium lang genug.", "counter_hypotheses": []})
        self.assertIn("falsifiability.counter_hypotheses_empty", missing)

    # --- checked/supports_primary with pending_checks → still blocking ---
    def test_checked_supports_primary_with_pending_is_blocking(self) -> None:
        missing, _ = self._eval(
            make_structured_falsifiability(
                counter_hypotheses=[{
                    "id": "h1",
                    "statement": "Unterstützt primäre Hypothese, aber weitere Checks ausstehend.",
                    "assessment": {
                        "status": "checked",
                        "outcome": "supports_primary",
                        "evidence_refs": [{"path": "results/evidence.jsonl"}],
                        "pending_checks": ["Replikation mit unabhängigem Executor"],
                    },
                }]
            )
        )
        self.assertIn("falsifiability.assessment_pending_blocking", missing)


class MalformedStructuredBlockTests(unittest.TestCase):
    """Regression tests: malformed structured blocks must never produce promotion_ready=true.

    Covers the P1 gap: STRUCTURED_STATUSES/STRUCTURED_OUTCOMES were defined but
    not previously used. Invalid or missing enum values must produce blocking signals
    and must not silently fall through to the semantic ready-logic.
    """

    def _eval(self, falsifiability: dict) -> tuple[list[str], list[str]]:
        state = vpr.classify_experiment(
            make_manifest(
                status="testing",
                execution_status="executed",
                falsifiability=falsifiability,
            )
        )
        return vpr.evaluate_falsifiability(state)

    # --- Invalid status (typo) ---
    def test_invalid_status_typo_is_blocking(self) -> None:
        missing, _ = self._eval(
            make_structured_falsifiability(
                counter_hypotheses=[{
                    "id": "h1",
                    "statement": "Tippfehler im Status: 'cheked' statt 'checked'.",
                    "assessment": {"status": "cheked", "outcome": "supports_primary"},
                }]
            )
        )
        self.assertIn("falsifiability.assessment_invalid_status", missing)
        self.assertNotIn("falsifiability.assessment_not_checked", missing)

    # --- Missing status ---
    def test_missing_status_is_blocking(self) -> None:
        missing, _ = self._eval(
            make_structured_falsifiability(
                counter_hypotheses=[{
                    "id": "h1",
                    "statement": "Kein status-Feld im assessment vorhanden.",
                    "assessment": {"outcome": "supports_primary"},
                }]
            )
        )
        self.assertIn("falsifiability.assessment_invalid_status", missing)

    # --- Invalid outcome (typo) ---
    def test_invalid_outcome_typo_is_blocking(self) -> None:
        missing, _ = self._eval(
            make_structured_falsifiability(
                counter_hypotheses=[{
                    "id": "h1",
                    "statement": "Tippfehler im Outcome: 'supports_prmary' statt 'supports_primary'.",
                    "assessment": {"status": "checked", "outcome": "supports_prmary"},
                }]
            )
        )
        self.assertIn("falsifiability.assessment_invalid_outcome", missing)
        self.assertNotIn("falsifiability.assessment_not_checked", missing)

    # --- Missing outcome ---
    def test_missing_outcome_is_blocking(self) -> None:
        missing, _ = self._eval(
            make_structured_falsifiability(
                counter_hypotheses=[{
                    "id": "h1",
                    "statement": "Kein outcome-Feld im assessment vorhanden.",
                    "assessment": {"status": "checked"},
                }]
            )
        )
        self.assertIn("falsifiability.assessment_invalid_outcome", missing)

    # --- Invalid status/outcome must not silently become ready ---
    def test_invalid_status_cannot_produce_ready(self) -> None:
        missing, _ = self._eval(
            make_structured_falsifiability(
                counter_hypotheses=[{
                    "id": "h1",
                    "statement": "Ungültiger Status soll kein promotion_ready=true erzeugen.",
                    "assessment": {"status": "fully_done", "outcome": "supports_primary"},
                }]
            )
        )
        self.assertIn("falsifiability.assessment_invalid_status", missing)
        # promotion_ready = (len(missing) == 0) → must be False
        self.assertNotEqual(missing, [])

    # --- counter_hypotheses present, version missing → structured path, version_invalid ---
    def test_counter_hypotheses_without_version_is_not_legacy(self) -> None:
        fal = {
            "falsification_criterion": "Kriterium ist lang genug um zu gelten.",
            "counter_hypotheses": [{
                "id": "h1",
                "statement": "Block hat counter_hypotheses aber keine version.",
                "assessment": {"status": "checked", "outcome": "supports_primary"},
            }],
        }
        self.assertTrue(vpr._is_structured(fal))
        missing, _ = self._eval(fal)
        self.assertIn("falsifiability.version_invalid_or_missing", missing)

    # --- version: 2 is not v1 → blocking ---
    def test_version_2_is_blocking(self) -> None:
        fal = {
            "version": 2,
            "falsification_criterion": "Kriterium ist lang genug um zu gelten.",
            "counter_hypotheses": [{
                "id": "h1",
                "statement": "Version 2 ist noch nicht spezifiziert und muss blockieren.",
                "assessment": {"status": "checked", "outcome": "supports_primary"},
            }],
        }
        missing, _ = self._eval(fal)
        self.assertIn("falsifiability.version_invalid_or_missing", missing)

    # --- {version: 1} alone (no counter_hypotheses) → counter_hypotheses_empty ---
    def test_version_only_block_is_not_ready(self) -> None:
        fal = {"version": 1}
        self.assertTrue(vpr._is_structured(fal))
        missing, _ = self._eval(fal)
        self.assertIn("falsifiability.counter_hypotheses_empty", missing)
        self.assertNotEqual(missing, [])

    # --- Legacy block still uses legacy evaluator ---
    def test_legacy_block_still_uses_legacy_evaluator(self) -> None:
        fal = {
            "counter_hypothesis": "Die Verbesserung ist durch Promptlänge erklärbar.",
            "falsification_criterion": "Gleich langer Nicht-Spec-Prompt liefert gleiche Ergebnisse.",
            "counterevidence_checked": True,
        }
        self.assertFalse(vpr._is_structured(fal))
        missing, warnings = self._eval(fal)
        self.assertEqual(missing, [])
        self.assertEqual(warnings, [])

    # --- assessment dict missing → assessment_missing ---
    def test_missing_assessment_dict_is_blocking(self) -> None:
        missing, _ = self._eval(
            make_structured_falsifiability(
                counter_hypotheses=[{
                    "id": "h1",
                    "statement": "Diese Gegenhypothese hat kein assessment-Objekt.",
                }]
            )
        )
        self.assertIn("falsifiability.assessment_missing", missing)


try:
    from jsonschema import Draft202012Validator
    _JSONSCHEMA_AVAILABLE = True
except ImportError:
    _JSONSCHEMA_AVAILABLE = False

SCHEMA_PATH = Path(__file__).resolve().parent.parent.parent / "schemas" / "experiment.manifest.schema.json"


def _make_minimal_manifest(falsifiability: dict) -> dict:
    """Wraps a falsifiability block into the minimal valid manifest envelope."""
    return {
        "schema_version": "0.1.0",
        "experiment": {
            "name": "fixture",
            "hypothesis": "placeholder",
            "status": "testing",
            "category": "technique",
            "evidence_level": "experimental",
            "execution_status": "executed",
            "execution_refs": ["results/evidence.jsonl"],
            "falsifiability": falsifiability,
        },
    }


@unittest.skipUnless(_JSONSCHEMA_AVAILABLE, "jsonschema not installed")
class SchemaFalsifiabilityRegressionTests(unittest.TestCase):
    """Schema-level regression tests for the falsifiability oneOf contract.

    These tests use jsonschema directly and do NOT require rfc3339-validator
    (format checks are disabled via format_checker=None).
    """

    def setUp(self) -> None:
        with open(SCHEMA_PATH) as f:
            import json as _json
            schema = _json.load(f)
        self.validator = Draft202012Validator(schema)

    def _is_valid(self, manifest: dict) -> bool:
        return self.validator.is_valid(manifest)

    def _errors(self, manifest: dict) -> list:
        return list(self.validator.iter_errors(manifest))

    # --- Legacy block validates ---
    def test_legacy_block_is_schema_valid(self) -> None:
        doc = _make_minimal_manifest({
            "counter_hypothesis": "Die Verbesserung ist durch Promptlänge erklärbar.",
            "falsification_criterion": "Gleich langer Nicht-Spec-Prompt liefert gleiche Ergebnisse.",
            "counterevidence_checked": True,
        })
        self.assertTrue(self._is_valid(doc))

    # --- Structured v1 block validates ---
    def test_structured_v1_block_is_schema_valid(self) -> None:
        doc = _make_minimal_manifest({
            "version": 1,
            "falsification_criterion": "Kontrollarm zeigt gleiche Ergebnisse wie Behandlungsarm.",
            "counter_hypotheses": [{
                "id": "h1",
                "statement": "Der Effekt entsteht durch Ceiling-Effekt, nicht durch die Intervention.",
                "assessment": {
                    "status": "checked",
                    "outcome": "supports_primary",
                    "evidence_refs": [{"path": "results/evidence.jsonl"}],
                },
            }],
        })
        self.assertTrue(self._is_valid(doc))

    # --- {version: 1} without counter_hypotheses fails schema ---
    def test_version_only_fails_schema(self) -> None:
        doc = _make_minimal_manifest({"version": 1})
        self.assertFalse(self._is_valid(doc))

    # --- counter_hypotheses without version fails schema ---
    def test_counter_hypotheses_without_version_fails_schema(self) -> None:
        doc = _make_minimal_manifest({
            "falsification_criterion": "Kriterium lang genug.",
            "counter_hypotheses": [{
                "id": "h1",
                "statement": "Gegenhypothese ohne version-Feld.",
                "assessment": {"status": "checked", "outcome": "supports_primary"},
            }],
        })
        self.assertFalse(self._is_valid(doc))

    # --- evidence_refs item without path fails schema ---
    def test_evidence_refs_item_without_path_fails_schema(self) -> None:
        doc = _make_minimal_manifest({
            "version": 1,
            "falsification_criterion": "Kriterium lang genug für die Validierung.",
            "counter_hypotheses": [{
                "id": "h1",
                "statement": "evidence_refs item hat keinen path.",
                "assessment": {
                    "status": "checked",
                    "outcome": "supports_primary",
                    "evidence_refs": [{"section": "Ergebnisse"}],
                },
            }],
        })
        self.assertFalse(self._is_valid(doc))

    # --- Hybrid legacy + structured fields fail schema (neither oneOf branch matches) ---
    def test_hybrid_block_fails_schema(self) -> None:
        doc = _make_minimal_manifest({
            "counter_hypothesis": "Legacy-Feld.",
            "falsification_criterion": "Gemeinsames Feld vorhanden.",
            "counterevidence_checked": True,
            "version": 1,
            "counter_hypotheses": [{
                "id": "h1",
                "statement": "Hybride Blöcke dürfen nicht valid sein.",
                "assessment": {"status": "checked", "outcome": "supports_primary"},
            }],
        })
        self.assertFalse(self._is_valid(doc))

    # --- Invalid status enum fails schema ---
    def test_invalid_status_enum_fails_schema(self) -> None:
        doc = _make_minimal_manifest({
            "version": 1,
            "falsification_criterion": "Kriterium lang genug für die Validierung.",
            "counter_hypotheses": [{
                "id": "h1",
                "statement": "Ungültiger status-Wert soll Schema-Fehler erzeugen.",
                "assessment": {"status": "fully_done", "outcome": "supports_primary"},
            }],
        })
        self.assertFalse(self._is_valid(doc))

    # --- Invalid outcome enum fails schema ---
    def test_invalid_outcome_enum_fails_schema(self) -> None:
        doc = _make_minimal_manifest({
            "version": 1,
            "falsification_criterion": "Kriterium lang genug für die Validierung.",
            "counter_hypotheses": [{
                "id": "h1",
                "statement": "Ungültiger outcome-Wert soll Schema-Fehler erzeugen.",
                "assessment": {"status": "checked", "outcome": "confirmed"},
            }],
        })
        self.assertFalse(self._is_valid(doc))


if __name__ == "__main__":
    unittest.main(verbosity=2)
