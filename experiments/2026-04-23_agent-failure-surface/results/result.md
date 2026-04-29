---
title: "Result: Phase 3 — Chain Integrity Stress"
status: draft
canonicality: operative
created: "2026-04-29"
updated: "2026-04-29"
author: "Copilot Agent (GPT-5.x)"
relations:
  - type: references
    target: ../method.md
  - type: references
    target: ../../../contracts/command-semantics.md
  - type: references
    target: ../../../docs/reference/agent-operability-fixture-matrix.md
  - type: references
    target: ../../../scripts/docmeta/validate_command_chain.py
---

# result.md — Phase 3 (Chain Integrity Stress)

## Outcome

**Phase 3 abgeschlossen — keine neue tolerierte Chain-Integrity-Lücke
in den geprüften Kandidaten.** Alle Phase-3-Probekandidaten wurden vom
bestehenden `validate_chain`-Stack bereits erkannt oder liegen
nachweislich außerhalb des v0.1-Validator-Scopes. Konsequenz nach
`method.md` §"Patch-Gate": **No-Patch-Pfad** — kein neues Fixture, kein
Validator-Eingriff, keine Doku-Erweiterung. Phase-3 wird als
belegte Negativ-Entscheidung mit Kandidatenmatrix verankert.

Der vorhergehende Phase-2-Stand (Klasse `SEM-EMPTY-ASSERTED`,
verankert über `_validate_semantic_anti_invariants`,
`tests/fixtures/command_chains/invalid-empty-asserted-state*.json` und
`tests/fixtures/cross_contract/{invalid/empty_change_state.json,
valid/minimal_chain_add.json}`) bleibt unverändert und wird in Phase 3
weder erweitert noch widerlegt; die Phase-2-Verifikation ist über
`results/evidence.jsonl` (Einträge `validator_signal_before_patch`,
`validator_signal_after_patch`, `branch_coverage_extended`) und
`artifacts/run-phase2/` historisch nachvollziehbar.

## Diagnose (Ist-Zustand vor Probe)

`scripts/docmeta/validate_command_chain.py` deckt zum Zeitpunkt von
Phase 3 folgende Chain-Fehlerklassen ab (alle relevanten Schichten):

| Schicht                            | Funktion                                   | Erfasste Klassen                                                                                                                                                          |
| ---------------------------------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Einzelrecord-Schema                | `_validate_individual` (Z. 161-214)        | `contract_invalid` (unbekanntes Command, fehlendes Pflichtfeld, Schemaverletzung)                                                                                         |
| Sequenz                            | `_validate_sequence` (Z. 217-243)          | `command_sequence_invalid` (jede Abweichung von `read_context → write_change → validate_change`, inkl. Mehrfach-Commands, Vertauschungen, fehlendem `write_change`)        |
| Versionen                          | `_validate_version_consistency` (Z. 246-276) | `command_sequence_invalid` (gemischte Versionen)                                                                                                                          |
| Target-Files-Kontinuität           | `_validate_target_files_continuity` (Z. 279-325) | `target_files_mismatch` (`write_change.target_files` ⊄ `read_context.target_files`)                                                                                       |
| Locator-Kontinuität                | `_validate_locator_continuity` (Z. 328-370) | `locator_continuity_violation` (leerer/whitespace-only `write_change.locator`)                                                                                            |
| Semantische Anti-Invarianten       | `_validate_semantic_anti_invariants` (Z. 373-476) | `semantic_contradiction` (remove+`exact_after`, add+`exact_before`, `exact_before == exact_after`, *empty asserted state* (Phase-2), Duplikate in `target_files`)         |
| Error-Bindung                      | `_validate_error_check_binding` (Z. 479-538) | `validate_error_unbindable`                                                                                                                                               |
| Validate-Result-Seam               | `_validate_validate_result_seam` (Z. 541-621) | `validate_without_write`, `validate_targets_out_of_scope`                                                                                                                 |

**Transition-Fehler** (also Übergänge zwischen Records, nicht
Einzelrecords) sind in den Schichten *Sequenz*, *Versionen*,
*Target-Files-Kontinuität* und *Validate-Result-Seam* abgedeckt; die
Schicht *Einzelrecord-Schema* schlägt zusätzlich an, sobald ein
Übergang Records mit unzulässiger Form erzwingt (z. B. v0.2-Record im
v0.1-Chain).

## Probe-Kandidaten (direkter `validate_chain(...)`-Lauf)

Sieben Kandidaten gemäß `method.md` §"Phase 3" als minimale Chain-JSON
direkt gegen `validate_chain(chain, label)` getestet (kein Datei-I/O,
keine Fixtures committet). Jeder Kandidat ist auf eine in `method.md`
benannte Phase-3-Klasse zurückführbar.

```
A_two_writes:                                  ['command_sequence_invalid']
B_no_write:                                    ['command_sequence_invalid', 'validate_without_write']
C_mixed_versions:                              ['command_sequence_invalid', 'contract_invalid']
D_validate_before_write:                       ['command_sequence_invalid', 'validate_without_write']
E_target_outside_read:                         ['target_files_mismatch']
F_add_then_remove:                             ['command_sequence_invalid']
G_validate_empty_checks_after_write_no_targets: ['contract_invalid', 'validate_targets_out_of_scope']
```

Toleranz-Rate (im Sinne von `method.md` §"Metriken" und
§"Phase 3 Erfolgssignal"): **0/7**. Keine der konstruierten Transitions
passiert die bestehenden Validatoren still.

## Kandidatenmatrix

| # | Kandidat (Phase-3-Klasse aus `method.md`)                                                              | Erwartete Fehlerklasse                                  | Observed error codes                                          | Bewertung           |
| - | ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------- | ------------------------------------------------------------- | ------------------- |
| A | `read_context → write_change → write_change → validate_change` (Doppel-Write ohne Read dazwischen, Phase-3 #2/#3) | `command_sequence_invalid` (Chain hat 4 Records statt 3) | `command_sequence_invalid`                                   | `already_detected`  |
| B | `read_context → validate_change` ohne `write_change` (Phase-3 #5)                                       | `validate_without_write` + `command_sequence_invalid`   | `command_sequence_invalid`, `validate_without_write`          | `already_detected`  |
| C | Gemischte Versionen `v0.1 → v0.2 → v0.1` (Phase-3 #4)                                                   | `command_sequence_invalid` + `contract_invalid` (Schema-Const)  | `command_sequence_invalid`, `contract_invalid`                | `already_detected`  |
| D | `validate_change(success=true, errors=[]) → read_context → write_change` (Phase-3 #6, Variante "validate vor write") | `command_sequence_invalid` + `validate_without_write`   | `command_sequence_invalid`, `validate_without_write`          | `already_detected`  |
| E | `write_change.target_files` enthält Pfad außerhalb `read_context.target_files` (Phase-3 #1, „locator B implizit/abweichend") | `target_files_mismatch`                                 | `target_files_mismatch`                                       | `already_detected`  |
| F | `add` dann `remove` auf gleichem Locator (Phase-3 #3, Doppel-Write)                                     | `command_sequence_invalid` (zwei `write_change`-Records bricht v0.1-Sequenz) | `command_sequence_invalid`                                   | `already_detected`  |
| G | `write_change.target_files=[]` direkt vor `validate_change` mit `checks` (Phase-3 #6-Variante "validate trotz leerem Scope") | `contract_invalid` (Schema `minItems: 1`) + `validate_targets_out_of_scope` | `contract_invalid`, `validate_targets_out_of_scope`           | `already_detected`  |
| – | `validate_change(locator B abweichend)` (Phase-3 #1, wörtlich)                                          | —                                                       | n/a (`validate_change` hat per Schema kein `locator`-Feld)    | `outside_scope`     |

Kein Kandidat erreicht den Status `tolerated_but_wrong`. Es liegt auch
kein `ambiguous_contract_gap`-Fall vor: in jedem Fall greift mindestens
ein bestehender Validator mit dokumentiertem Fehlercode.

## Hypothesen (Bewertung)

- **Leithypothese (Phase 3):** „Valide Einzelcommands können in
  falscher Reihenfolge oder falscher Kombination als Chain ungültig
  sein, ohne dass die bestehenden Validatoren das melden."
  → **refuted** für die geprüften Kandidaten. Jede konstruierte
  Transition löst mindestens einen dokumentierten Fehlercode aus.
- **Antithese:** „Die bestehenden Chain-Validatoren decken diese
  Fehler bereits ausreichend ab; dann ist keine Validator-Erweiterung
  nötig."
  → **confirmed** im Rahmen der geprüften Kandidaten. Insbesondere
  `_validate_sequence` mit der harten v0.1-Sequenz-Bindung
  (`actual == EXPECTED_SEQUENCE`) wirkt als Generalfänger für jede
  Phase-3-Permutation, die nicht exakt
  `read_context → write_change → validate_change` ist.

Die Bestätigung der Antithese ist auf den geprüften Kandidatenraum
begrenzt; sie ist keine Allaussage über alle denkbaren Transitions.
Sie ist insbesondere nicht so zu lesen, dass die v0.1-Sequenz-Strenge
für künftige v0.2-Erweiterungen ausreichend bliebe.

## Strukturkonsequenz

Keine. `method.md` §"Patch-Gate" greift nur, wenn mindestens ein
Kandidat als `tolerated_but_wrong` belegt ist; das ist hier nicht der
Fall. Daher bleiben unverändert:

- `scripts/docmeta/validate_command_chain.py`
- `scripts/docmeta/test_validate_command_chain.py`
- `tests/fixtures/command_chains/`
- `contracts/command-semantics.md`
- `docs/reference/agent-operability-fixture-matrix.md`

`method.md` §"Mindestschärfe der Strukturkonsequenz" wird über die
zweite zulässige Form erfüllt: *„eine belegte
Nicht-Änderungsentscheidung mit Kandidatenmatrix und Testausgabe"*.
Die Kandidatenmatrix oben und die Testausgabe in
`artifacts/run-phase3/execution.txt` belegen den Stand.

## Verifikation

| Schritt                                                              | Ergebnis                              |
| -------------------------------------------------------------------- | ------------------------------------- |
| Probe vor Phase-3-Patchversuch (Kandidaten A-G)                      | jeweils ≥1 Fehlercode (siehe oben)    |
| `python3 scripts/docmeta/test_validate_command_chain.py`             | `Ran 39 tests, OK`                    |
| `python3 tests/contracts/test_cross_contract_chain.py`               | `Ran 16 tests, OK`                    |
| `python3 scripts/docmeta/test_fixture_matrix_audit_surface.py`       | `Ran 1 test, OK`                      |
| `python3 scripts/docmeta/test_fixture_matrix_known_gaps_audit.py`    | `Ran 1 test, OK`                      |
| `python3 scripts/docmeta/test_promotion_readiness.py`                | `Ran 99 tests, OK`                    |
| `python3 scripts/docmeta/validate_promotion_readiness.py`            | dry-run, `exit=0` (per Design)        |
| `make validate`                                                      | siehe `artifacts/run-phase3/execution.txt` |

Vollständige Konsolen-Ausgabe: `artifacts/run-phase3/execution.txt`
(referenziert über `manifest.yml.experiment.execution_refs`).

## Geltungsgrenzen

- Die geprüften Kandidaten sind die in `method.md` §"Phase 3
  Injektions-Set" benannten Klassen plus eine zusätzliche
  Validate-Targets-Variante (Kandidat G). Andere noch nicht
  benannte Transition-Klassen sind durch diese Phase weder bestätigt
  noch widerlegt.
- Die v0.1-Sequenz ist in `_validate_sequence` strikt auf genau drei
  Records gepinnt. Diese Strenge ist der Hauptgrund, warum viele
  Phase-3-Permutationen *automatisch* `command_sequence_invalid`
  auslösen. Mit Lockerung dieser Constraint (z. B. v0.2 mit
  optionalem Wiederholungs-Read) müsste Phase 3 erneut geprüft werden.
- Die Phase-3-Disziplin betrifft nur Chain-Validatoren; das Verhalten
  von Cross-Contract-Validatoren (Handoff↔Chain) wurde bewusst nicht
  variiert (Scope-Begrenzung).
- Die Probe ist eine Live-Probe ohne committete Fixtures
  (`method.md` §"Diagnosepflicht vor Patch" Punkt 3). Sie ist über die
  oben gelisteten Inputs reproduzierbar; ein Regressions-Fixture wäre
  nur bei `tolerated_but_wrong` indiziert und ist daher bewusst
  ausgelassen.

## Entscheidung

**Phase 3 abgeschlossen, No-Patch.** Die Phase liefert eine belegte
Negativ-Aussage gemäß `method.md` §"Stop-Bedingung Phase 3"
(„sämtliche Fälle werden erkannt"). Die nächste Phase (Phase 4 —
Replay Reality Gap) folgt in eigenem PR und ist nicht Bestandteil
dieser Entscheidung.
