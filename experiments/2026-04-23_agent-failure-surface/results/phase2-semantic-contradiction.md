---
title: "Phase 2 - Semantic Contradiction (Phasenfassung)"
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

# Phase 2 - Semantic Contradiction (Phasenfassung)

> Diese Datei stabilisiert den Phase-2-Ergebnisbericht als eigene Phasenfassung.
> Sie basiert auf dem ehemaligen `results/result.md` nach Abschluss von Phase 2
> und wurde mit Frontmatter-Relationen versehen. Der kumulative Serienbericht
> ist `results/result.md`; die maßgebliche Entscheidung ist `results/decision.yml`.

---

## Stabilisiertes Phase-2-Ergebnis

## Outcome

**Phase 2 abgeschlossen.** Eine bislang tolerierte semantische
Widerspruchsklasse - *"empty asserted state"* - wurde reproduzierbar belegt
und ueber Negativ-Fixture, Positiv-Kontrast, Test und minimale
Validator-Erweiterung verankert. Keine weitere Phase-2-Nacharbeit erforderlich;
die Gesamtserie bleibt offen und Phase 3 folgt in eigenem PR.

## Diagnose (Ist-Zustand vor Patch)

`_validate_semantic_anti_invariants`
in `scripts/docmeta/validate_command_chain.py` deckte bereits ab:

- `change_type=remove` + `exact_after is not None`
- `change_type=add` + `exact_before is not None`
- `exact_before == exact_after`
- duplicate `target_files` in `write_change`/`read_context`

Die Regeln pruefen jeweils nur die verbotene Seite des Zustands. Die
geforderte Seite - der `exact_*`-Wert, der laut `change_type` einen echten
Pre-/Post-State tragen soll - wird nur dann angefasst, wenn sie identisch
zur anderen Seite ist. Das Schema laesst `exact_before`/`exact_after` als
beliebige Strings zu, inklusive `""`.

## Hypothesen

- **H1 - empty asserted state (operationalisiert):** Wenn ein `exact_*`
  auf der vom `change_type` semantisch geforderten Seite gesetzt, aber
  leer (`""`) ist, ist die Zustandsbehauptung vakuum. Die Klasse ist
  reproduzierbar ohne file-IO/NLP.
- **H2 - `read_context.extracted_facts` widerspricht `write_change`:**
  verworfen. v0.1 dokumentiert explizit, dass eine maschinelle Pruefung
  Datei-I/O oder strukturierte Facts erfordern wuerde.
- **H3 - locator-Pfad != `target_files`:** verworfen. `locator` ist per
  Contract opakes Anchor-/Headingstring-Material; eine Pfadextraktion waere
  Heuristik ausserhalb des v0.1-Scopes.

## Live-Probe (vor Patch)

Sechs Kandidaten direkt gegen `vcc.validate_cross_contract` getestet - alle
sechs liefern leere Fehlerlisten (Toleranz-Rate 6/6):

```text
A_add_empty_after:        []
B_modify_empty_before:    []
C_modify_empty_after:     []
D_replace_empty_before:   []
E_facts_contradict_before:[]
F_locator_path_mismatch:  []
```

H1 deckt A-D mit einer einzigen, scharf bezeichneten Regel ab.

## Strukturkonsequenz

### Validator-Erweiterung

`scripts/docmeta/validate_command_chain.py` -
`_validate_semantic_anti_invariants` um Klasse *empty asserted state*
ergaenzt. Symmetrisch zu den bestehenden Regeln; nur eine zusaetzliche
Code-Klasse: `semantic_contradiction`.

### Fixtures (Kontrastpaar gem. method.md)

**Chain-Direktbeweis:**

- **Negativ (add)** - `tests/fixtures/command_chains/invalid-empty-asserted-state.json`
- **Negativ (remove)** - `tests/fixtures/command_chains/invalid-empty-asserted-state-remove.json`
- **Negativ (modify)** - `tests/fixtures/command_chains/invalid-empty-asserted-state-modify.json`

**Cross-Contract-Ebene:**

- **Negativ** - `tests/fixtures/cross_contract/invalid/empty_change_state.json`
- **Positiv-Kontrast** - `tests/fixtures/cross_contract/valid/minimal_chain_add.json`

### Test

Neue Methoden in `scripts/docmeta/test_validate_command_chain.py`:

- `test_semantic_contradiction_empty_asserted_state`
- `test_no_false_positive_add_with_nonempty_exact_after`
- `test_semantic_contradiction_empty_asserted_state_remove`
- `test_semantic_contradiction_empty_asserted_state_modify`

Neue Methoden in `tests/contracts/test_cross_contract_chain.py`:

- `test_minimal_chain_add_is_accepted`
- `test_empty_change_state_fails`

### Doku

- `contracts/command-semantics.md` um *Empty asserted state* ergaenzt.
- `docs/reference/agent-operability-fixture-matrix.md`: neue Klasse `SEM-EMPTY-ASSERTED`.

## Verifikation (Signalwechsel)

| Schritt | Ergebnis |
| ------- | -------- |
| Kandidat A vor Patch (`add` + `exact_after=""`) | `[]` - toleriert |
| Kandidat A nach Patch | `["semantic_contradiction"]` |
| Positiv-Kontrast (non-empty `exact_after`) | `[]` - gueltig |
| `test_validate_command_chain.py` | `Ran 39 tests, OK` |
| `test_cross_contract_chain.py` | `Ran 16 tests, OK` |
| `test_validate_agent_handoff.py` | `Ran 13 tests, OK` |

## Geltungsgrenzen

- Klasse erfasst nur den leeren-String-Fall (`""`).
- Fehlende Felder bleiben weiter tolerant.
- Klasse ersetzt H2/H3 nicht; diese verbleiben ausserhalb des
  v0.1-Validator-Zustaendigkeitsbereichs.

## Entscheidung

**Phase 2 abgeschlossen.** Strukturkonsequenz erfuellt die Mindestschärfe über
benannte Aequivalenzklasse plus Kontrastfaelle.