#!/usr/bin/env python3
"""Direkte Regressionstests für die P2-Kreuzregel in validate_schema.py.

Die Regel:
  decision_type=result_assessment
    + counterevidence_checked=False + verdict='confirms'  → Fehler
    + counter_hypothesis_outcome='found_and_confirming' + verdict='confirms' → Fehler

Testfälle:
  1. result_assessment + verdict=confirms + counterevidence_checked=false → Fehler
  2. result_assessment + verdict=mixed + counterevidence_checked=false → erlaubt
  3. result_assessment + verdict=confirms + counter_hypothesis_outcome=found_and_confirming → Fehler
  4. result_assessment + verdict=mixed + counter_hypothesis_outcome=found_and_confirming → erlaubt
  5. result_assessment ohne neue Felder (kein counterevidence_checked, kein outcome) → erlaubt
  6. Anderer decision_type (adoption_assessment) → P2-Regel greift nicht
  7. verdict=refutes + counterevidence_checked=false → erlaubt
  8. counterevidence_checked=true + verdict=confirms → erlaubt (Normalfall erfolgreicher Prüfung)
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

# Sicherstellen, dass das Modul importierbar ist (liegt im selben Verzeichnis).
sys.path.insert(0, str(Path(__file__).resolve().parent))

import validate_schema as vs  # noqa: E402


class P2CounterevidenceRuleTests(unittest.TestCase):
    """Direkte Tests von validate_schema.check_counterevidence_rule()."""

    def _rel(self) -> str:
        return "experiments/test/results/decision.yml"

    # ------------------------------------------------------------------
    # Fehler-Fälle
    # ------------------------------------------------------------------

    def test_confirms_plus_counterevidence_false_is_error(self) -> None:
        """Fall 1: verdict=confirms + counterevidence_checked=False → Fehler."""
        data = {
            "decision_type": "result_assessment",
            "verdict": "confirms",
            "counterevidence_checked": False,
        }
        result = vs.check_counterevidence_rule(data, self._rel())
        self.assertIsNotNone(result)
        self.assertIn("counterevidence_checked=false", result)
        self.assertIn("confirms", result)

    def test_confirms_plus_found_and_confirming_is_error(self) -> None:
        """Fall 3: verdict=confirms + counter_hypothesis_outcome=found_and_confirming → Fehler."""
        data = {
            "decision_type": "result_assessment",
            "verdict": "confirms",
            "counter_hypothesis_outcome": "found_and_confirming",
        }
        result = vs.check_counterevidence_rule(data, self._rel())
        self.assertIsNotNone(result)
        self.assertIn("found_and_confirming", result)

    # ------------------------------------------------------------------
    # Erlaubte Fälle
    # ------------------------------------------------------------------

    def test_mixed_plus_counterevidence_false_is_allowed(self) -> None:
        """Fall 2: verdict=mixed + counterevidence_checked=False → erlaubt."""
        data = {
            "decision_type": "result_assessment",
            "verdict": "mixed",
            "counterevidence_checked": False,
        }
        self.assertIsNone(vs.check_counterevidence_rule(data, self._rel()))

    def test_mixed_plus_found_and_confirming_is_allowed(self) -> None:
        """Fall 4: verdict=mixed + counter_hypothesis_outcome=found_and_confirming → erlaubt.

        Semantisch: Gegenhypothese gestützt UND Ursprungshypothese 'mixed' ist konsistent.
        """
        data = {
            "decision_type": "result_assessment",
            "verdict": "mixed",
            "counter_hypothesis_outcome": "found_and_confirming",
        }
        self.assertIsNone(vs.check_counterevidence_rule(data, self._rel()))

    def test_no_new_fields_is_allowed(self) -> None:
        """Fall 5: result_assessment ohne neue Felder → kein Fehler (keine Pflicht)."""
        data = {
            "decision_type": "result_assessment",
            "verdict": "inconclusive",
        }
        self.assertIsNone(vs.check_counterevidence_rule(data, self._rel()))

    def test_other_decision_type_is_not_checked(self) -> None:
        """Fall 6: adoption_assessment → P2-Regel greift nicht, auch wenn Felder gesetzt sind."""
        data = {
            "decision_type": "adoption_assessment",
            "verdict": "confirms",
            "counterevidence_checked": False,
        }
        self.assertIsNone(vs.check_counterevidence_rule(data, self._rel()))

    def test_refutes_plus_counterevidence_false_is_allowed(self) -> None:
        """Fall 7: verdict=refutes + counterevidence_checked=False → erlaubt.

        Widerlegung braucht keine Gegenprüfung der Gegenhypothese.
        """
        data = {
            "decision_type": "result_assessment",
            "verdict": "refutes",
            "counterevidence_checked": False,
        }
        self.assertIsNone(vs.check_counterevidence_rule(data, self._rel()))

    def test_counterevidence_true_plus_confirms_is_allowed(self) -> None:
        """Fall 8: counterevidence_checked=True + verdict=confirms → erlaubt (Normalfall)."""
        data = {
            "decision_type": "result_assessment",
            "verdict": "confirms",
            "counterevidence_checked": True,
        }
        self.assertIsNone(vs.check_counterevidence_rule(data, self._rel()))

    def test_inconclusive_is_always_allowed(self) -> None:
        """Zusatz: inconclusive mit counterevidence_checked=False → erlaubt."""
        data = {
            "decision_type": "result_assessment",
            "verdict": "inconclusive",
            "counterevidence_checked": False,
        }
        self.assertIsNone(vs.check_counterevidence_rule(data, self._rel()))

    # ------------------------------------------------------------------
    # Grenzfälle
    # ------------------------------------------------------------------

    def test_none_verdict_with_counterevidence_false_is_allowed(self) -> None:
        """Kein verdict gesetzt + counterevidence_checked=False → kein Fehler (fehlerhaftes YAML
        würde von JSON-Schema-Validator gemeldet, nicht hier)."""
        data = {
            "decision_type": "result_assessment",
            "counterevidence_checked": False,
        }
        self.assertIsNone(vs.check_counterevidence_rule(data, self._rel()))

    def test_error_message_contains_rel_path(self) -> None:
        """Der Fehlertext enthält den relativen Pfad zur Datei."""
        data = {
            "decision_type": "result_assessment",
            "verdict": "confirms",
            "counterevidence_checked": False,
        }
        rel = "experiments/my-exp/results/decision.yml"
        result = vs.check_counterevidence_rule(data, rel)
        self.assertIsNotNone(result)
        self.assertIn(rel, result)


class CanonicalDecisionPathTests(unittest.TestCase):
    """Regressions for canonical root and one-level phase decision surfaces."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo_root = Path(self.tmp.name)
        self.experiments_dir = self.repo_root / "experiments"
        self.experiments_dir.mkdir()
        vs.errors.clear()

    def tearDown(self) -> None:
        vs.errors.clear()

    def _write(self, relative_path: str, content: str = "verdict: not_executed\n") -> Path:
        path = self.experiments_dir / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def test_discovery_includes_only_root_results_and_numeric_phase_decisions(self) -> None:
        for valid in (
            "foo/results/decision.yml",
            "foo/p1/decision.yml",
            "foo/p12/decision.yml",
        ):
            self._write(valid)
        for excluded in (
            "foo/p/decision.yml",
            "foo/p1x/decision.yml",
            "foo/phase1/decision.yml",
            "foo/p1/nested/decision.yml",
            "foo/nested/p1/decision.yml",
            "_template/p1/decision.yml",
            "_archive/results/decision.yml",
        ):
            self._write(excluded)

        discovered = {
            path.relative_to(self.experiments_dir).as_posix()
            for path in vs.canonical_decision_paths(self.experiments_dir)
        }

        self.assertEqual(
            discovered,
            {
                "foo/results/decision.yml",
                "foo/p1/decision.yml",
                "foo/p12/decision.yml",
            },
        )

    def test_phase_decision_uses_same_schema(self) -> None:
        self._write(
            "foo/p1/decision.yml",
            """\
schema_version: "0.1.0"
decision_type: "execution_assessment"
verdict: "not_executed"
date: "2026-08-16"
rationale: "No phase slot has executed."
""",
        )

        vs.validate_decision_files(
            repo_root=self.repo_root,
            schema_path=vs.SCHEMA_MAP["decision"],
        )

        self.assertTrue(any("reviewer" in error for error in vs.errors), vs.errors)

    def test_phase_adoption_semantics_use_experiment_root_manifest(self) -> None:
        self._write(
            "foo/manifest.yml",
            "experiment:\n  execution_status: executed\n",
        )
        self._write(
            "foo/p12/decision.yml",
            """\
schema_version: "0.1.0"
decision_type: "adoption_assessment"
verdict: "defer"
confidence: "low"
date: "2026-08-16"
reviewer: "test-reviewer"
rationale: "Execution exists, but adoption remains deferred."
evidence_summary:
  observations: 1
""",
        )

        vs.validate_decision_files(
            repo_root=self.repo_root,
            schema_path=vs.SCHEMA_MAP["decision"],
        )

        self.assertEqual(vs.errors, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
