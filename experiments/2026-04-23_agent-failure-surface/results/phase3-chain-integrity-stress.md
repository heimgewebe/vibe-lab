---
title: "Phase 3 — Chain Integrity Stress (Phasen-Ergebnisbericht)"
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

# Phase 3 — Chain Integrity Stress (Phasen-Ergebnisbericht)

> Dieser Bericht dokumentiert Phase 3 der Reihe Agent Failure Surface Mapping.
> Der kumulative Serienbericht ist `results/result.md`;
> die maßgebliche Entscheidung ist `results/decision.yml`.

---

## Outcome

**Phase 3 abgeschlossen — keine neue tolerierte Chain-Integrity-Lücke
in den geprüften Kandidaten.** Alle Phase-3-Probekandidaten wurden vom
bestehenden `validate_chain`-Stack bereits erkannt oder liegen
nachweislich außerhalb des v0.1-Validator-Scopes. Konsequenz nach
`method.md` §"Patch-Gate": **No-Patch-Pfad** — kein neues Fixture, kein
Validator-Eingriff, keine Doku-Erweiterung.

## Diagnose (Ist-Zustand vor Probe)

`scripts/docmeta/validate_command_chain.py` deckt zum Zeitpunkt von
Phase 3 folgende Chain-Fehlerklassen ab:

| Schicht                            | Funktion                                   | Erfasste Klassen                                                                                                                                                          |
| ---------------------------------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Einzelrecord-Schema                | `_validate_individual` (Z. 161-214)        | `contract_invalid`                                                                                                                                                        |
| Sequenz                            | `_validate_sequence` (Z. 217-243)          | `command_sequence_invalid` (jede Abweichung von `read_context → write_change → validate_change`, inkl. Mehrfach-Commands, Vertauschungen, fehlendem `write_change`)        |
| Versionen                          | `_validate_version_consistency` (Z. 246-276) | `command_sequence_invalid` (gemischte Versionen)                                                                                                                          |
| Target-Files-Kontinuität           | `_validate_target_files_continuity` (Z. 279-325) | `target_files_mismatch`                                                                                                                                                   |
| Locator-Kontinuität                | `_validate_locator_continuity` (Z. 328-370) | `locator_continuity_violation`                                                                                                                                            |
| Semantische Anti-Invarianten       | `_validate_semantic_anti_invariants` (Z. 373-476) | `semantic_contradiction` (inkl. SEM-EMPTY-ASSERTED aus Phase 2)                                                                                                           |
| Error-Bindung                      | `_validate_error_check_binding` (Z. 479-538) | `validate_error_unbindable`                                                                                                                                               |
| Validate-Result-Seam               | `_validate_validate_result_seam` (Z. 541-621) | `validate_without_write`, `validate_targets_out_of_scope`                                                                                                                 |

**Transition-relevante Schichten:** `_validate_sequence`, `_validate_version_consistency`, `_validate_target_files_continuity`, `_validate_validate_result_seam`.

## Probe-Kandidaten (direkter `validate_chain(...)`-Lauf)

```
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

| # | Kandidat (Phase-3-Klasse aus `method.md`)                                                              | Erwartete Fehlerklasse                                        | Observed error codes                                          | Bewertung           |
| - | ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------- | ------------------------------------------------------------- | ------------------- |
| A | `read_context → write_change → write_change → validate_change`                                         | `command_sequence_invalid`                                    | `command_sequence_invalid`                                    | `already_detected`  |
| B | `read_context → validate_change` ohne `write_change`                                                   | `command_sequence_invalid`, `validate_without_write`          | `command_sequence_invalid`, `validate_without_write`          | `already_detected`  |
| C | Gemischte Versionen `v0.1 → v0.2 → v0.1`                                                               | `command_sequence_invalid`, `contract_invalid`                | `command_sequence_invalid`, `contract_invalid`                | `already_detected`  |
| D | `validate_change(success=true) → read_context → write_change`                                          | `command_sequence_invalid`, `validate_without_write`          | `command_sequence_invalid`, `validate_without_write`          | `already_detected`  |
| E | `write_change.target_files` enthält Pfad außerhalb `read_context.target_files`                         | `target_files_mismatch`                                       | `target_files_mismatch`                                       | `already_detected`  |
| F | `add` dann `remove` auf gleichem Locator (zwei `write_change`-Records)                                 | `command_sequence_invalid`                                    | `command_sequence_invalid`                                    | `already_detected`  |
| G | `write_change.target_files=[]` vor `validate_change` mit `checks`                                     | `contract_invalid`, `validate_targets_out_of_scope`           | `contract_invalid`, `validate_targets_out_of_scope`           | `already_detected`  |
| – | `validate_change(locator B abweichend)`                                                                | n/a (`validate_change` hat per Schema kein `locator`-Feld)    | —                                                             | `outside_scope`     |

## Hypothesen (Bewertung)

- **Leithypothese (Phase 3):** refuted für die geprüften Kandidaten.
- **Antithese:** confirmed — bestehende Chain-Validatoren greifen bei allen konstruierten Transitions.

## Verifikation

| Schritt                                                              | Ergebnis                              |
| -------------------------------------------------------------------- | ------------------------------------- |
| Probe vor Phase-3-Patchversuch (Kandidaten A–G)                      | jeweils ≥1 Fehlercode (0/7 toleriert) |
| `python3 scripts/docmeta/test_validate_command_chain.py`             | `Ran 39 tests, OK`                    |
| `python3 tests/contracts/test_cross_contract_chain.py`               | `Ran 16 tests, OK`                    |
| `python3 scripts/docmeta/test_fixture_matrix_audit_surface.py`       | `Ran 1 test, OK`                      |
| `python3 scripts/docmeta/test_fixture_matrix_known_gaps_audit.py`    | `Ran 1 test, OK`                      |
| `python3 scripts/docmeta/test_promotion_readiness.py`                | `Ran 99 tests, OK`                    |
| `python3 scripts/docmeta/validate_promotion_readiness.py`            | dry-run, `exit=0`                     |
| `make validate`                                                      | `✅ Validation passed`                |

Vollständige Konsolen-Ausgabe: `artifacts/run-phase3/execution.txt`.

## Geltungsgrenzen

- Negativ-Aussage strikt auf den geprüften Kandidatenraum begrenzt.
- Die v0.1-Sequenz-Strenge (`_validate_sequence` harte Bindung auf 3 Records) ist der Hauptgrund, warum viele Phase-3-Permutationen automatisch `command_sequence_invalid` auslösen. Bei v0.2-Lockerung muss Phase 3 mit erweitertem Kandidatenraum erneut geprüft werden.
- Cross-Contract-Validatoren (Handoff↔Chain) wurden bewusst nicht variiert.

## Entscheidung

**Phase 3 abgeschlossen, No-Patch.** `method.md` §"Mindestschärfe der Strukturkonsequenz" ist über die zweite zulässige Form erfüllt: belegte Nicht-Änderungsentscheidung mit Kandidatenmatrix und Testausgabe.
