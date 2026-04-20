#!/usr/bin/env python3
"""Regression-Tests für derive_interpretation_risk() in generate_epistemic_state.py.

Testet die 6-Signal-Heuristik auf alle relevanten Pfade:
  - Low-Risk-Pfad (sauberes adopted Experiment)
  - Medium-Risk-Pfad (rekonstruiertes + anekdotisches Experiment)
  - High-Risk-Pfad (defektes adopted Experiment ohne Artefakte)
  - Signal 4: adoption_basis/execution_status-Mismatch
  - Signal 5: fehlendes Interpretation Budget bei adopted
  - Signal 6: fehlendes decision.yml bei adopted
"""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


def _load_module():
    script_path = Path(__file__).resolve().parent / "generate_epistemic_state.py"
    spec = importlib.util.spec_from_file_location("generate_epistemic_state", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load generate_epistemic_state.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _build_exp_dir(
    tmp_dir: Path,
    *,
    evidence_content: str | None = '{"event_type":"observation","timestamp":"2026-01-01T00:00:00Z","iteration":1,"metric":"test","value":1,"context":"x"}\n',
    result_md_content: str | None = "# Result\n\n## Interpretation Budget\n\n### Allowed Claims\n- claim\n\n### Disallowed Claims\n- no claim\n",
    decision_yml: bool = True,
) -> Path:
    """Erstellt ein minimales Experiment-Verzeichnis im tmp_dir."""
    results = tmp_dir / "results"
    results.mkdir(parents=True)

    if evidence_content is not None:
        (results / "evidence.jsonl").write_text(evidence_content, encoding="utf-8")

    if result_md_content is not None:
        (results / "result.md").write_text(result_md_content, encoding="utf-8")

    if decision_yml:
        (results / "decision.yml").write_text(
            'schema_version: "0.1.0"\ndecision_type: adoption_assessment\nverdict: adopt\n',
            encoding="utf-8",
        )

    return tmp_dir


def _manifest(
    *,
    status: str = "adopted",
    execution_status: str = "executed",
    evidence_level: str = "experimental",
    adoption_basis: str = "executed",
) -> dict:
    return {
        "experiment": {
            "status": status,
            "execution_status": execution_status,
            "evidence_level": evidence_level,
            "adoption_basis": adoption_basis,
        }
    }


class DeriveInterpretationRiskTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = _load_module()

    # ------------------------------------------------------------------
    # Low-risk: sauberes adopted Experiment (0 Signale)
    # ------------------------------------------------------------------
    def test_clean_adopted_experiment_is_low_risk(self) -> None:
        """Vollständiges, sauber ausgeführtes adopted Experiment → low."""
        with tempfile.TemporaryDirectory() as tmp:
            exp_dir = _build_exp_dir(
                Path(tmp),
                decision_yml=True,
            )
            manifest = _manifest(
                status="adopted",
                execution_status="executed",
                evidence_level="experimental",
                adoption_basis="executed",
            )
            result = self.mod.derive_interpretation_risk(exp_dir, manifest)
            self.assertEqual(result, "low", "Clean adopted experiment should be low risk")

    # ------------------------------------------------------------------
    # Low-risk: nicht-adopted Experiment mit guter Ausführung (0 Signale)
    # ------------------------------------------------------------------
    def test_non_adopted_testing_experiment_is_low_risk(self) -> None:
        """Testing-Experiment mit guter Ausführung und Evidenz → low."""
        with tempfile.TemporaryDirectory() as tmp:
            exp_dir = _build_exp_dir(
                Path(tmp),
                result_md_content=None,
                decision_yml=False,
            )
            manifest = _manifest(
                status="testing",
                execution_status="executed",
                evidence_level="experimental",
                adoption_basis="",
            )
            result = self.mod.derive_interpretation_risk(exp_dir, manifest)
            self.assertEqual(result, "low", "Non-adopted experiment with good execution should be low risk")

    # ------------------------------------------------------------------
    # Medium-risk: rekonstruiertes + anekdotisches Experiment (2 Signale)
    # ------------------------------------------------------------------
    def test_reconstructed_anecdotal_is_medium_risk(self) -> None:
        """Rekonstruiertes Experiment mit anekdotischer Evidenz → medium (2 Signale)."""
        with tempfile.TemporaryDirectory() as tmp:
            exp_dir = _build_exp_dir(
                Path(tmp),
                result_md_content=None,  # kein Budget, aber auch kein adopted
                decision_yml=False,
            )
            manifest = _manifest(
                status="testing",
                execution_status="reconstructed",  # Signal 2
                evidence_level="anecdotal",         # Signal 3
                adoption_basis="",
            )
            result = self.mod.derive_interpretation_risk(exp_dir, manifest)
            self.assertEqual(result, "medium", "Reconstructed + anecdotal should be medium risk (2 signals)")

    # ------------------------------------------------------------------
    # Medium-risk: adoption_basis/execution_status-Mismatch (Signal 4)
    # ------------------------------------------------------------------
    def test_adoption_basis_mismatch_raises_risk(self) -> None:
        """adoption_basis=executed aber execution_status=reconstructed → Signal 4 feuert."""
        with tempfile.TemporaryDirectory() as tmp:
            exp_dir = _build_exp_dir(
                Path(tmp),
                result_md_content=None,
                decision_yml=False,
            )
            # Nur Signal 2 (reconstructed) + Signal 4 (mismatch) = 2 → medium
            manifest_mismatch = _manifest(
                status="testing",
                execution_status="reconstructed",  # Signal 2
                evidence_level="experimental",
                adoption_basis="executed",          # Signal 4: executed ≠ reconstructed
            )
            result = self.mod.derive_interpretation_risk(exp_dir, manifest_mismatch)
            self.assertEqual(result, "medium", "adoption_basis mismatch should raise risk to medium")

    # ------------------------------------------------------------------
    # Medium-risk: fehlendes Interpretation Budget + rekonstruiert (Signale 2+5)
    # ------------------------------------------------------------------
    def test_adopted_missing_budget_and_reconstructed_is_medium(self) -> None:
        """Adopted Experiment: kein Interpretation Budget + rekonstruiert → medium (2 Signale)."""
        with tempfile.TemporaryDirectory() as tmp:
            exp_dir = _build_exp_dir(
                Path(tmp),
                # result.md vorhanden aber OHNE Interpretation Budget
                result_md_content="# Result\n\nKeine Budget-Sektion vorhanden.",
                decision_yml=True,
            )
            manifest = _manifest(
                status="adopted",
                execution_status="reconstructed",  # Signal 2
                evidence_level="experimental",
                adoption_basis="reconstructed",    # kein Mismatch
            )
            result = self.mod.derive_interpretation_risk(exp_dir, manifest)
            self.assertEqual(result, "medium", "Missing budget + reconstructed should be medium risk")

    # ------------------------------------------------------------------
    # Medium-risk: `prepared` execution_status triggers Signal 2
    # (was a dead branch with the old, incorrect `not_executed` value)
    # ------------------------------------------------------------------
    def test_prepared_execution_status_triggers_signal_2(self) -> None:
        """execution_status=prepared → Signal 2 feuert (Schema-korrekter Wert)."""
        with tempfile.TemporaryDirectory() as tmp:
            exp_dir = _build_exp_dir(
                Path(tmp),
                result_md_content=None,
                decision_yml=False,
            )
            # Signal 2 (prepared) + Signal 3 (anecdotal) = 2 → medium
            manifest = _manifest(
                status="testing",
                execution_status="prepared",  # Signal 2
                evidence_level="anecdotal",   # Signal 3
                adoption_basis="",
            )
            result = self.mod.derive_interpretation_risk(exp_dir, manifest)
            self.assertEqual(result, "medium", "prepared + anecdotal should be medium risk (signals 2+3)")

    # ------------------------------------------------------------------
    # Signal 1: non-parseable evidence.jsonl triggers risk signal
    # ------------------------------------------------------------------
    def test_non_parseable_evidence_triggers_signal_1(self) -> None:
        """evidence.jsonl enthält nur nicht-parsierbare Zeilen → Signal 1 feuert."""
        with tempfile.TemporaryDirectory() as tmp:
            exp_dir = _build_exp_dir(
                Path(tmp),
                # Datei existiert, aber kein valides JSON
                evidence_content="not valid json at all\n",
                result_md_content=None,
                decision_yml=False,
            )
            manifest = _manifest(
                status="testing",
                execution_status="executed",
                evidence_level="experimental",
                adoption_basis="",
            )
            result = self.mod.derive_interpretation_risk(exp_dir, manifest)
            # Signal 1 (unparseable evidence) only → still low (≤1 signals)
            self.assertEqual(result, "low", "Single non-parseable evidence triggers only signal 1 → low")

    def test_empty_evidence_file_triggers_signal_1(self) -> None:
        """Leeres evidence.jsonl (keine Zeilen) → Signal 1 feuert."""
        with tempfile.TemporaryDirectory() as tmp:
            exp_dir = _build_exp_dir(
                Path(tmp),
                evidence_content="",  # existiert, aber leer
                result_md_content=None,
                decision_yml=False,
            )
            manifest = _manifest(
                status="testing",
                execution_status="executed",
                evidence_level="experimental",
                adoption_basis="",
            )
            result = self.mod.derive_interpretation_risk(exp_dir, manifest)
            self.assertEqual(result, "low", "Empty evidence file triggers only signal 1 → low")


    def test_fully_broken_adopted_is_high_risk(self) -> None:
        """Adopted Experiment ohne Evidenz, designed, anecdotal, Mismatch, kein Budget, kein decision.yml → high."""
        with tempfile.TemporaryDirectory() as tmp:
            exp_dir = _build_exp_dir(
                Path(tmp),
                evidence_content=None,    # Signal 1: kein evidence.jsonl
                result_md_content=None,   # Signal 5: kein result.md → kein Budget
                decision_yml=False,       # Signal 6: kein decision.yml
            )
            manifest = _manifest(
                status="adopted",
                execution_status="designed",   # Signal 2
                evidence_level="anecdotal",    # Signal 3
                adoption_basis="executed",     # Signal 4: executed ≠ designed
            )
            result = self.mod.derive_interpretation_risk(exp_dir, manifest)
            self.assertEqual(result, "high", "Fully broken adopted experiment should be high risk (6 signals)")


if __name__ == "__main__":
    unittest.main()
