---
title: "Phase 3 - Chain Integrity Stress (Phasen-Ergebnisbericht)"
status: draft
canonicality: operative
created: "2026-04-29"
updated: "2026-04-29"
author: "Copilot Agent (GPT-5.x)"
relations:
  - type: references
    target: result.md
  - type: references
    target: decision.yml
  - type: references
    target: ../method.md
---

# Phase 3 - Chain Integrity Stress (Phasen-Ergebnisbericht)

> Dieser Bericht dokumentiert Phase 3 der Reihe Agent Failure Surface Mapping.
> Der kumulative Serienbericht ist `results/result.md`;
> die maßgebliche Entscheidung ist `results/decision.yml`.

---

## Outcome

**Phase 3 abgeschlossen - keine neue tolerierte Chain-Integrity-Luecke
in den geprueften Kandidaten.** Alle Phase-3-Probekandidaten wurden vom
bestehenden `validate_chain`-Stack bereits erkannt oder liegen
nachweislich ausserhalb des v0.1-Validator-Scopes. Konsequenz nach
`method.md` Patch-Gate: **No-Patch-Pfad**.

## Diagnose (Ist-Zustand vor Probe)

`scripts/docmeta/validate_command_chain.py` deckt zum Zeitpunkt von
Phase 3 folgende Chain-Fehlerklassen ab:

- `_validate_individual`: `contract_invalid`
- `_validate_sequence`: `command_sequence_invalid`
- `_validate_version_consistency`: `command_sequence_invalid`
- `_validate_target_files_continuity`: `target_files_mismatch`
- `_validate_locator_continuity`: `locator_continuity_violation`
- `_validate_semantic_anti_invariants`: `semantic_contradiction`
- `_validate_error_check_binding`: `validate_error_unbindable`
- `_validate_validate_result_seam`: `validate_without_write`, `validate_targets_out_of_scope`

## Probe-Kandidaten (direkter `validate_chain(...)`-Lauf)

```text
A_two_writes:                                   ['command_sequence_invalid']
B_no_write:                                     ['command_sequence_invalid', 'validate_without_write']
C_mixed_versions:                               ['command_sequence_invalid', 'contract_invalid']
D_validate_before_write:                        ['command_sequence_invalid', 'validate_without_write']
E_target_outside_read:                          ['target_files_mismatch']
F_add_then_remove:                              ['command_sequence_invalid']
G_validate_empty_checks_after_write_no_targets: ['contract_invalid', 'validate_targets_out_of_scope']
```

Toleranz-Rate: **0/7**.

## Kandidatenmatrix

| # | Kandidat | Observed error codes | Bewertung |
| - | -------- | -------------------- | --------- |
| A | `read->write->write->validate` | `command_sequence_invalid` | `already_detected` |
| B | `read->validate` (kein write) | `command_sequence_invalid`, `validate_without_write` | `already_detected` |
| C | gemischte Versionen v0.1/v0.2 | `command_sequence_invalid`, `contract_invalid` | `already_detected` |
| D | `validate->read->write` | `command_sequence_invalid`, `validate_without_write` | `already_detected` |
| E | `write.target_files` nicht in `read.target_files` | `target_files_mismatch` | `already_detected` |
| F | `add` dann `remove` | `command_sequence_invalid` | `already_detected` |
| G | `write.target_files=[]` vor `validate(checks)` | `contract_invalid`, `validate_targets_out_of_scope` | `already_detected` |
| - | `validate_change.locator B abweichend` | n/a | `outside_scope` |

## Hypothesen (Bewertung)

- **Leithypothese (Phase 3):** refuted fuer die geprueften Kandidaten.
- **Antithese:** confirmed - bestehende Chain-Validatoren greifen bei allen konstruierten Transitions.

## Verifikation

| Schritt | Ergebnis |
| ------- | -------- |
| Probe Kandidaten A-G | 0/7 toleriert |
| `test_validate_command_chain.py` | `Ran 39 tests, OK` |
| `test_cross_contract_chain.py` | `Ran 16 tests, OK` |
| `test_fixture_matrix_audit_surface.py` | `Ran 1 test, OK` |
| `test_fixture_matrix_known_gaps_audit.py` | `Ran 1 test, OK` |
| `test_promotion_readiness.py` | `Ran 99 tests, OK` |
| `validate_promotion_readiness.py` | dry-run, exit=0 |
| `make validate` | `Validation passed` |

Vollstaendige Konsolen-Ausgabe: `artifacts/run-phase3/execution.txt`.

## Geltungsgrenzen

- Negativ-Aussage strikt auf den geprueften Kandidatenraum begrenzt.
- Die v0.1-Sequenz-Strenge ist der Hauptgrund, warum viele Phase-3-Permutationen automatisch `command_sequence_invalid` ausloesen.
- Bei v0.2-Lockerung muss Phase 3 mit erweitertem Kandidatenraum erneut geprueft werden.

## Entscheidung

**Phase 3 abgeschlossen, No-Patch.** Die Nicht-Aenderungsentscheidung ist mit Kandidatenmatrix und Testausgabe belegt.