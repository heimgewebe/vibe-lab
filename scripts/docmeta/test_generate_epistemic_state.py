#!/usr/bin/env python3
"""Boundary tests for the artifact-only epistemic-state snapshot."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


def _load_module():
    path = Path(__file__).resolve().parent / "generate_epistemic_state.py"
    spec = importlib.util.spec_from_file_location("generate_epistemic_state", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load generate_epistemic_state.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _experiment(
    root: Path,
    *,
    status: str = "testing",
    execution: str = "executed",
    evidence_level: str = "experimental",
    adoption_basis: str = "",
    evidence: str | None = '{"event_type":"observation"}\n',
    budget: bool = False,
    decision: bool = False,
) -> tuple[Path, dict]:
    results = root / "results"
    results.mkdir(parents=True)
    if evidence is not None:
        (results / "evidence.jsonl").write_text(evidence, encoding="utf-8")
    if budget:
        (results / "result.md").write_text(
            "# Result\n\n## Interpretation Budget\n\n- bounded\n", encoding="utf-8"
        )
    if decision:
        (results / "decision.yml").write_text("verdict: adopt\n", encoding="utf-8")
    manifest = {
        "experiment": {
            "status": status,
            "execution_status": execution,
            "evidence_level": evidence_level,
            "adoption_basis": adoption_basis,
        }
    }
    return root, manifest


class EpistemicStateBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = _load_module()

    def test_design_quality_has_three_stable_states(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(self.mod.derive_design_quality(root), "minimal")
            (root / "method.md").write_text("x" * 301, encoding="utf-8")
            self.assertEqual(self.mod.derive_design_quality(root), "partial")
            (root / "failure_modes.md").write_text("x" * 301, encoding="utf-8")
            self.assertEqual(self.mod.derive_design_quality(root), "structured")

    def test_risk_thresholds_remain_low_medium_high(self) -> None:
        cases = [
            ({"status": "adopted", "execution": "executed", "evidence_level": "experimental", "adoption_basis": "executed", "budget": True, "decision": True}, "low"),
            ({"execution": "reconstructed", "evidence_level": "anecdotal"}, "medium"),
            ({"status": "adopted", "execution": "designed", "evidence_level": "anecdotal", "adoption_basis": "executed", "evidence": None}, "high"),
        ]
        for kwargs, expected in cases:
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as tmp:
                exp_dir, manifest = _experiment(Path(tmp), **kwargs)
                self.assertEqual(self.mod.derive_interpretation_risk(exp_dir, manifest), expected)

    def test_single_bad_evidence_signal_stays_low(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            exp_dir, manifest = _experiment(Path(tmp), evidence="not-json\n")
            self.assertEqual(self.mod.derive_interpretation_risk(exp_dir, manifest), "low")

    def test_manifest_loader_rejects_non_mapping_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manifest.yml"
            path.write_text("- not\n- a\n- mapping\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "manifest root must be a mapping"):
                self.mod.load_manifest(path)

    def test_render_marks_snapshot_non_authoritative(self) -> None:
        text = self.mod.render_report(
            [{
                "name": "demo",
                "status": "testing",
                "design_quality": "minimal",
                "execution_state": "designed",
                "evidence_strength": "anecdotal",
                "interpretation_risk": "medium",
            }]
        )
        self.assertIn("keine Wahrheitsquelle", text)
        self.assertIn("| `demo` | testing |", text)


if __name__ == "__main__":
    unittest.main()
