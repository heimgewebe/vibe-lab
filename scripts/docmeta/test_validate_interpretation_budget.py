#!/usr/bin/env python3
"""Kleine Regression-Tests für validate_interpretation_budget.py.

Fokus: Scope-Fix — Claim-Extraktion darf nur innerhalb des
`## Interpretation Budget`-Blocks stattfinden.
"""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


def _load_module():
    script_path = Path(__file__).resolve().parent / "validate_interpretation_budget.py"
    spec = importlib.util.spec_from_file_location("validate_interpretation_budget", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load validate_interpretation_budget.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class InterpretationBudgetScopeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = _load_module()

    def test_claims_outside_budget_block_are_not_counted(self) -> None:
        text = """
# result.md

## Interpretation Budget

### Allowed Claims
- ...

### Disallowed Claims
- ...

## Nächste Schritte

### Allowed Claims
- must-not-count

### Disallowed Claims
- must-not-count-either
"""
        budget_section = self.mod._extract_budget_section(text)
        self.assertIsNotNone(budget_section)

        allowed_match = self.mod.ALLOWED_CLAIMS_PATTERN.search(budget_section)
        disallowed_match = self.mod.DISALLOWED_CLAIMS_PATTERN.search(budget_section)

        allowed_claims = self.mod._extract_claims(allowed_match.group(1)) if allowed_match else []
        disallowed_claims = self.mod._extract_claims(disallowed_match.group(1)) if disallowed_match else []

        self.assertEqual(allowed_claims, [])
        self.assertEqual(disallowed_claims, [])


if __name__ == "__main__":
    unittest.main()
