#!/usr/bin/env python3
"""Regressionstests für generate_epistemic_state.py.

Fokus: Kalibrierung der interpretation_risk-Heuristik.
Testet die epistemisch wichtigen Grenzfälle, nicht nur Syntax.
"""

from __future__ import annotations

import importlib.util
import json
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


def _write_evidence(exp_dir: Path, entries: int) -> None:
    """Schreibt n syntaktisch gültige evidence.jsonl-Einträge."""
    results_dir = exp_dir / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    evidence_path = results_dir / "evidence.jsonl"
    lines = []
    for i in range(entries):
        lines.append(json.dumps({
            "event_type": "observation",
            "timestamp": f"2026-04-14T10:{i:02d}:00Z",
            "iteration": 1,
            "metric": "test",
            "value": str(i),
            "context": f"test entry {i}",
        }))
    evidence_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_result_with_budget(exp_dir: Path) -> None:
    """Schreibt eine result.md mit Interpretation Budget Block."""
    results_dir = exp_dir / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    (results_dir / "result.md").write_text(
        "# Result\n\n## Interpretation Budget\n\n"
        "### Allowed Claims\n- Spec-First reduces rework.\n\n"
        "### Disallowed Claims\n- Spec-First is universally better.\n",
        encoding="utf-8",
    )


def _write_result_without_budget(exp_dir: Path) -> None:
    """Schreibt eine result.md ohne Interpretation Budget Block."""
    results_dir = exp_dir / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    (results_dir / "result.md").write_text(
        "# Result\n\nSome findings here.\n",
        encoding="utf-8",
    )


class InterpretationRiskCalibrationTests(unittest.TestCase):
    """Tests für die mehrdimensionale interpretation_risk-Heuristik."""

    def setUp(self) -> None:
        self.mod = _load_module()
        self._tmpdir = tempfile.mkdtemp()
        self.exp_dir = Path(self._tmpdir) / "test-experiment"
        self.exp_dir.mkdir()

    def tearDown(self) -> None:
        import shutil
        shutil.rmtree(self._tmpdir, ignore_errors=True)

    def test_no_experiment_block_returns_unknown(self) -> None:
        result = self.mod.derive_interpretation_risk(self.exp_dir, {})
        self.assertEqual(result, "unknown")

    def test_no_evidence_returns_high(self) -> None:
        """Kein evidence.jsonl → high, unabhängig von anderen Feldern."""
        exp = {"execution_status": "executed", "evidence_level": "experimental"}
        result = self.mod.derive_interpretation_risk(self.exp_dir, exp)
        self.assertEqual(result, "high")

    def test_empty_evidence_returns_high(self) -> None:
        """Leere evidence.jsonl → high."""
        _write_evidence(self.exp_dir, 0)
        exp = {"execution_status": "executed", "evidence_level": "experimental"}
        result = self.mod.derive_interpretation_risk(self.exp_dir, exp)
        self.assertEqual(result, "high")

    # --- Kernfälle: Reconstructed darf nicht low sein ---

    def test_reconstructed_execution_not_low(self) -> None:
        """execution_status=reconstructed darf nicht low sein, auch mit viel Evidenz."""
        _write_evidence(self.exp_dir, 10)
        exp = {
            "execution_status": "reconstructed",
            "evidence_level": "experimental",
        }
        result = self.mod.derive_interpretation_risk(self.exp_dir, exp)
        self.assertIn(result, ("medium", "high"),
                      "reconstructed execution must not yield low risk")

    def test_adopted_reconstructed_not_low(self) -> None:
        """status=adopted + adoption_basis=reconstructed darf nicht low sein."""
        _write_evidence(self.exp_dir, 10)
        _write_result_with_budget(self.exp_dir)
        exp = {
            "status": "adopted",
            "execution_status": "reconstructed",
            "evidence_level": "experimental",
            "adoption_basis": "reconstructed",
        }
        result = self.mod.derive_interpretation_risk(self.exp_dir, exp)
        self.assertIn(result, ("medium", "high"),
                      "adopted+reconstructed must not yield low risk")

    # --- Kernfälle: Anecdotal darf nicht low sein ---

    def test_anecdotal_evidence_not_low(self) -> None:
        """evidence_level=anecdotal darf nicht low sein, auch mit vielen Einträgen."""
        _write_evidence(self.exp_dir, 25)
        exp = {
            "execution_status": "executed",
            "evidence_level": "anecdotal",
        }
        result = self.mod.derive_interpretation_risk(self.exp_dir, exp)
        self.assertIn(result, ("medium", "high"),
                      "anecdotal evidence_level must not yield low risk")

    # --- Kernfälle: Adopted ohne Budget ---

    def test_adopted_without_budget_not_low(self) -> None:
        """adopted ohne Interpretation Budget darf nicht low sein."""
        _write_evidence(self.exp_dir, 10)
        _write_result_without_budget(self.exp_dir)
        exp = {
            "status": "adopted",
            "execution_status": "executed",
            "evidence_level": "experimental",
            "adoption_basis": "executed",
        }
        result = self.mod.derive_interpretation_risk(self.exp_dir, exp)
        self.assertIn(result, ("medium", "high"),
                      "adopted without interpretation budget must not yield low risk")

    # --- Positiver Fall: Sauber ausgeführt → low ---

    def test_clean_executed_experimental_is_low(self) -> None:
        """Sauber executed + experimental + ausreichend Evidenz → low."""
        _write_evidence(self.exp_dir, 10)
        exp = {
            "execution_status": "executed",
            "evidence_level": "experimental",
        }
        result = self.mod.derive_interpretation_risk(self.exp_dir, exp)
        self.assertEqual(result, "low")

    def test_adopted_with_budget_executed_is_low(self) -> None:
        """adopted + executed + experimental + Budget vorhanden → low."""
        _write_evidence(self.exp_dir, 10)
        _write_result_with_budget(self.exp_dir)
        exp = {
            "status": "adopted",
            "execution_status": "executed",
            "evidence_level": "experimental",
            "adoption_basis": "executed",
        }
        result = self.mod.derive_interpretation_risk(self.exp_dir, exp)
        self.assertEqual(result, "low")

    # --- Dünn ist medium ---

    def test_thin_evidence_is_medium(self) -> None:
        """Weniger als _EVIDENCE_MIN_ENTRIES Einträge → mindestens medium."""
        _write_evidence(self.exp_dir, 2)
        exp = {
            "execution_status": "executed",
            "evidence_level": "experimental",
        }
        result = self.mod.derive_interpretation_risk(self.exp_dir, exp)
        self.assertIn(result, ("medium", "high"))

    # --- Kumulation: Viele Signale → high ---

    def test_multiple_risk_signals_escalate_to_high(self) -> None:
        """≥ 3 Risiko-Signale → high."""
        _write_evidence(self.exp_dir, 2)  # thin = +1
        _write_result_without_budget(self.exp_dir)
        exp = {
            "status": "adopted",          # adopted without budget = +1
            "execution_status": "reconstructed",  # +1
            "evidence_level": "anecdotal",         # +1
            "adoption_basis": "reconstructed",     # +1
        }
        result = self.mod.derive_interpretation_risk(self.exp_dir, exp)
        self.assertEqual(result, "high",
                         "multiple risk signals should escalate to high")


class ReconciliationStateTests(unittest.TestCase):
    """Tests für derive_reconciliation_state."""

    def setUp(self) -> None:
        self.mod = _load_module()
        self._tmpdir = tempfile.mkdtemp()
        self.exp_dir = Path(self._tmpdir) / "test-experiment"
        self.exp_dir.mkdir()

    def tearDown(self) -> None:
        import shutil
        shutil.rmtree(self._tmpdir, ignore_errors=True)

    def test_no_artifacts_no_inconsistency_returns_none(self) -> None:
        exp = {"execution_status": "executed"}
        result = self.mod.derive_reconciliation_state(self.exp_dir, exp)
        self.assertEqual(result, "none")

    def test_reconciliation_artifact_returns_active(self) -> None:
        artifacts = self.exp_dir / "artifacts"
        artifacts.mkdir()
        (artifacts / "iteration4-reconciliation.md").write_text("# Recon\n")
        exp = {"execution_status": "executed"}
        result = self.mod.derive_reconciliation_state(self.exp_dir, exp)
        self.assertEqual(result, "active")

    def test_designed_with_evidence_returns_inferred(self) -> None:
        _write_evidence(self.exp_dir, 5)
        exp = {"execution_status": "designed"}
        result = self.mod.derive_reconciliation_state(self.exp_dir, exp)
        self.assertEqual(result, "inferred")


if __name__ == "__main__":
    unittest.main()
