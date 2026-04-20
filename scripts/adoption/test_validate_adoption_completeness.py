#!/usr/bin/env python3
"""Regression-Tests für validate_adoption_completeness.py.

Fokus: Korrekte Pfad-Match-Logik — kein Substring-Match bei ähnlich
benannten Experimenten (z.B. upfront-structuring vs. upfront-structuring-replication).
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


def _load_module():
    script_path = Path(__file__).resolve().parent / "validate_adoption_completeness.py"
    spec = importlib.util.spec_from_file_location(
        "validate_adoption_completeness", script_path
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load validate_adoption_completeness.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content), encoding="utf-8")


class MatchesExperimentTests(unittest.TestCase):
    """Unit-Tests für _matches_experiment() — exakter Pfad-Vergleich."""

    def setUp(self) -> None:
        self.mod = _load_module()

    def test_exact_evidence_source_repo_root_relative_matches(self) -> None:
        """evidence_source mit exaktem Repo-Pfad trifft korrekt (via REPO_ROOT als base)."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            exp_dir = tmp_path / "experiments" / "2026-04-14_spec-first"
            exp_dir.mkdir(parents=True)

            # evidence_source ist repo-root-relativ: "experiments/2026-04-14_spec-first/"
            value = "experiments/2026-04-14_spec-first/"
            # base_dir = tmp_path (simuliert REPO_ROOT)
            result = self.mod._matches_experiment(value, tmp_path, exp_dir)
            self.assertTrue(result, "Repo-root-relativer evidence_source-Pfad soll matchen")

    def test_prefix_collision_does_not_match(self) -> None:
        """Längerer Experiment-Name darf nicht als Treffer für kürzeren gelten."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            # Basis-Experiment
            exp_dir = tmp_path / "experiments" / "2026-04-14_upfront-structuring"
            exp_dir.mkdir(parents=True)

            # Replikations-Experiment mit längerem Namen (Präfix-Überschneidung)
            replication_dir = (
                tmp_path / "experiments" / "2026-04-14_upfront-structuring-replication"
            )
            replication_dir.mkdir(parents=True)

            # evidence_source zeigt auf replication, aber exp_dir ist das Basis-Experiment
            value = "experiments/2026-04-14_upfront-structuring-replication/"
            result = self.mod._matches_experiment(value, tmp_path, exp_dir)
            self.assertFalse(
                result,
                "Replikations-Experiment darf nicht als Treffer für Basis-Experiment gelten",
            )

    def test_relative_target_resolves_to_experiment(self) -> None:
        """Relativer relations[].target-Pfad wird korrekt zu exp_dir aufgelöst."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            exp_dir = tmp_path / "experiments" / "2026-04-14_spec-first"
            result_md = exp_dir / "results" / "result.md"
            result_md.parent.mkdir(parents=True)
            result_md.touch()

            catalog_dir = tmp_path / "catalog" / "techniques"
            catalog_dir.mkdir(parents=True)
            catalog_file = catalog_dir / "spec-first.md"
            catalog_file.touch()

            # Relativer Pfad vom Catalog-Eintrag zum result.md
            # base_dir = catalog_file.parent (datei-relativ)
            relative_target = "../../experiments/2026-04-14_spec-first/results/result.md"
            result = self.mod._matches_experiment(relative_target, catalog_file.parent, exp_dir)
            self.assertTrue(result, "Relativer Pfad innerhalb des Experiments soll matchen")

    def test_relative_target_of_sibling_experiment_does_not_match(self) -> None:
        """Relativer Pfad zu anderem Experiment darf nicht matchen."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            exp_dir = tmp_path / "experiments" / "2026-04-14_spec-first"
            exp_dir.mkdir(parents=True)

            other_exp = tmp_path / "experiments" / "2026-04-14_yolo"
            other_result = other_exp / "results" / "result.md"
            other_result.parent.mkdir(parents=True)
            other_result.touch()

            catalog_dir = tmp_path / "catalog" / "techniques"
            catalog_dir.mkdir(parents=True)
            catalog_file = catalog_dir / "yolo.md"
            catalog_file.touch()

            # Relativer Pfad zum anderen Experiment; base = catalog_file.parent
            relative_target = "../../experiments/2026-04-14_yolo/results/result.md"
            result = self.mod._matches_experiment(relative_target, catalog_file.parent, exp_dir)
            self.assertFalse(result, "Anderes Experiment darf nicht matchen")

    def test_empty_value_does_not_match(self) -> None:
        """Leerer Wert soll False zurückgeben."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            exp_dir = tmp_path / "experiments" / "2026-04-14_spec-first"
            exp_dir.mkdir(parents=True)

            result = self.mod._matches_experiment("", tmp_path, exp_dir)
            self.assertFalse(result)


class PrefixCollisionIntegrationTests(unittest.TestCase):
    """Integrations-Test: validate_experiment() mit ähnlich benanntem Experiment."""

    def setUp(self) -> None:
        self.mod = _load_module()

    def test_artifact_of_replication_does_not_satisfy_base_experiment(self) -> None:
        """Katalog-Eintrag des Replikations-Experiments darf das Basis-Experiment nicht sättigen.

        Szenario:
          - Zwei Experimente: base und base-replication
          - Ein Technique-Eintrag referenziert explizit base-replication
          - validate_experiment(base) soll trotzdem FEHLER ausgeben (kein Technique)
        """
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)

            # Basis-Experiment (adopted, mit failure_modes.md ohne Substanz)
            base_dir = tmp_path / "experiments" / "2026-04-14_base"
            base_dir.mkdir(parents=True)
            _write(
                base_dir / "manifest.yml",
                """\
                experiment:
                  status: adopted
                  execution_status: executed
                  evidence_level: experimental
                  adoption_basis: executed
                """,
            )

            # Replikations-Experiment
            repl_dir = tmp_path / "experiments" / "2026-04-14_base-replication"
            repl_dir.mkdir(parents=True)

            # Technique-Eintrag: zeigt auf REPLICATION, nicht auf base
            tech_dir = tmp_path / "catalog" / "techniques"
            tech_dir.mkdir(parents=True)
            _write(
                tech_dir / "spec-first.md",
                f"""\
                ---
                schema_version: "0.1.0"
                title: "Spec-First"
                status: adopted
                category: technique
                evidence_source: "experiments/2026-04-14_base-replication/"
                relations:
                  - type: validated_by
                    target: {repl_dir}/results/result.md
                ---
                # Spec-First
                """,
            )

            # Patche Modulkonstanten auf tmp-Verzeichnisse
            original_catalog = self.mod.CATALOG_DIR
            original_prompts = self.mod.PROMPTS_DIR
            original_iblocks = self.mod.INSTRUCTION_BLOCKS_DIR
            original_repo_root = self.mod.REPO_ROOT
            try:
                self.mod.CATALOG_DIR = tmp_path / "catalog"
                self.mod.PROMPTS_DIR = tmp_path / "prompts" / "adopted"
                self.mod.INSTRUCTION_BLOCKS_DIR = tmp_path / "instruction-blocks"
                self.mod.REPO_ROOT = tmp_path  # evidence_source resolves against tmp_path

                errors, warnings = self.mod.validate_experiment(base_dir)
            finally:
                self.mod.CATALOG_DIR = original_catalog
                self.mod.PROMPTS_DIR = original_prompts
                self.mod.INSTRUCTION_BLOCKS_DIR = original_iblocks
                self.mod.REPO_ROOT = original_repo_root

            # Basis-Experiment hat keinen Technique-Eintrag → muss Fehler ausgeben
            technique_errors = [e for e in errors if "Technique" in e]
            self.assertTrue(
                technique_errors,
                "validate_experiment soll Fehler melden, da Technique nur für Replikation existiert, "
                f"nicht für Basis-Experiment. Errors: {errors}",
            )


if __name__ == "__main__":
    unittest.main()
