from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import yaml

from validate_repobrief_workbench_run_series import (  # noqa: E402
    DEFAULT_RUN_SERIES,
    validate_run_series,
)


class RepoBriefWorkbenchRunSeriesValidationTest(unittest.TestCase):
    def load_series(self) -> dict:
        return yaml.safe_load(DEFAULT_RUN_SERIES.read_text(encoding="utf-8"))

    def write_series(self, data: dict) -> Path:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        path = Path(temp.name) / "run-series.yml"
        path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
        return path

    def test_canonical_run_series_is_valid(self) -> None:
        self.assertEqual(validate_run_series(), [])

    def test_three_runs_are_required(self) -> None:
        data = self.load_series()
        data["runs"] = data["runs"][:2]
        data["aggregate"]["comparable_run_count"] = 2
        errors = validate_run_series(self.write_series(data))
        self.assertTrue(any("at least three runs" in error for error in errors))

    def test_external_ci_and_merge_observations_are_required(self) -> None:
        data = self.load_series()
        data["runs"][0]["external_observations"] = []
        errors = validate_run_series(self.write_series(data))
        self.assertTrue(any("external_observations omits" in error for error in errors))

    def test_limited_series_cannot_promote_default_condition(self) -> None:
        data = self.load_series()
        data["final_decisions"]["context_pack"] = "promote"
        errors = validate_run_series(self.write_series(data))
        self.assertIn("limited run series must not promote a default condition", errors)


if __name__ == "__main__":
    unittest.main()
