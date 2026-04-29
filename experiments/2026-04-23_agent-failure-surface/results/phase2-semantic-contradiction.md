# Phase 2 — Semantic Contradiction (Archiv-Kopie)

> Diese Datei archiviert den Phase-2-Ergebnisbericht im Originalzustand.
> Sie ist eine Abschrift des ehemaligen `results/result.md` nach Abschluss
> von Phase 2. Der kumulative Serienbericht ist `results/result.md`;
> die maßgebliche Entscheidung ist `results/decision.yml`.

---

# result.md — Phase 2 (Semantic Contradiction)

## Outcome

**Phase 2 abgeschlossen.** Eine bislang tolerierte semantische
Widerspruchsklasse — *"empty asserted state"* — wurde reproduzierbar belegt
und über Negativ-Fixture, Positiv-Kontrast, Test und minimale
Validator-Erweiterung verankert. Keine weitere Phase-2-Nacharbeit erforderlich;
die Gesamtserie bleibt offen und Phase 3 folgt in eigenem PR.

## Diagnose (Ist-Zustand vor Patch)

`_validate_semantic_anti_invariants`
in `scripts/docmeta/validate_command_chain.py` (Funktion vor Patch ca. Z. 373-444; nach Patch um die unten beschriebene Klasse erweitert) deckte bereits ab:

- `change_type=remove` + `exact_after is not None` (Z. 386-397)
- `change_type=add` + `exact_before is not None` (Z. 398-409)
- `exact_before == exact_after` (Z. 410-422)
- duplicate `target_files` in `write_change`/`read_context` (Z. 423-443)

Die Regeln prüfen jeweils nur die *verbotene* Seite des Zustands. Die
*geforderte* Seite — der `exact_*`-Wert, der laut `change_type` einen echten
Pre-/Post-State tragen soll — wird nur dann angefasst, wenn sie identisch
zur anderen Seite ist. Schema lässt `exact_before`/`exact_after` als
beliebige Strings zu (`schemas/command.write_change.schema.json:33-37`),
inklusive `""`.

## Hypothesen

- **H1 — empty asserted state (operationalisiert)**: Wenn ein `exact_*`
  auf der vom `change_type` semantisch geforderten Seite gesetzt, aber
  leer (`""`) ist, ist die Zustandsbehauptung vakuum. Die Klasse ist
  reproduzierbar ohne file-IO/NLP.
- **H2 — `read_context.extracted_facts` widerspricht `write_change`**:
  verworfen. v0.1 dokumentiert explizit, dass eine maschinelle Prüfung
  Datei-I/O oder strukturierte Facts erfordern würde
  (`contracts/command-semantics.md:160-162`).
- **H3 — locator-Pfad ≠ `target_files`**: verworfen. `locator` ist per
  Contract opakes Anchor-/Headingstring-Material; eine Pfadextraktion wäre
  Heuristik außerhalb des v0.1-Scopes.

## Live-Probe (vor Patch)

Sechs Kandidaten direkt gegen `vcc.validate_cross_contract` getestet — alle
sechs liefern leere Fehlerlisten (Toleranz-Rate 6/6):

```
A_add_empty_after:        []
B_modify_empty_before:    []
C_modify_empty_after:     []
D_replace_empty_before:   []
E_facts_contradict_before:[]
F_locator_path_mismatch:  []
```

H1 deckt A–D mit einer einzigen, scharf bezeichneten Regel ab.

## Strukturkonsequenz

### Validator-Erweiterung

`scripts/docmeta/validate_command_chain.py` —
`_validate_semantic_anti_invariants` um Klasse *empty asserted state*
ergänzt. Symmetrisch zu den bestehenden Regeln; nur eine zusätzliche
Code-Klasse: `semantic_contradiction`. Mapping:

| `change_type` | Asserted-Side(n)               |
| ------------- | ------------------------------- |
| `add`         | `exact_after`                   |
| `remove`      | `exact_before`                  |
| `modify`      | `exact_before`, `exact_after`   |
| `replace`     | `exact_before`, `exact_after`   |

Regel feuert nur, wenn das jeweilige Feld *präsent* und gleich `""` ist —
fehlende Felder bleiben weiterhin zulässig (v0.1 hält Felder optional).

### Fixtures (Kontrastpaar gem. method.md §Mindestschärfe)

**Chain-Direktbeweis (validate_command_chain):**

- **Negativ (add)** — `tests/fixtures/command_chains/invalid-empty-asserted-state.json`:
  `change_type=add`, `exact_after=""`. Erwartet: `semantic_contradiction`.
- **Negativ (remove)** — `tests/fixtures/command_chains/invalid-empty-asserted-state-remove.json`:
  `change_type=remove`, `exact_before=""`. Erwartet: `semantic_contradiction`.
- **Negativ (modify)** — `tests/fixtures/command_chains/invalid-empty-asserted-state-modify.json`:
  `change_type=modify`, `exact_before=""`, `exact_after` non-empty. Erwartet: `semantic_contradiction`.

**Cross-Contract-Ebene:**

- **Negativ** — `tests/fixtures/cross_contract/invalid/empty_change_state.json`:
  `change_type=add`, `exact_after=""`. Erwartet: `semantic_contradiction`.
- **Positiv-Kontrast** — `tests/fixtures/cross_contract/valid/minimal_chain_add.json`:
  Identische Form, `exact_after` non-empty. Bleibt gültig.

### Test

Neue Methoden in `scripts/docmeta/test_validate_command_chain.py` (direkter Chain-Beweis):

- `test_semantic_contradiction_empty_asserted_state` (Negativ add; erwartet `semantic_contradiction`)
- `test_no_false_positive_add_with_nonempty_exact_after` (Positiv-Kontrast)
- `test_semantic_contradiction_empty_asserted_state_remove` (Negativ remove; Branch-Coverage)
- `test_semantic_contradiction_empty_asserted_state_modify` (Negativ modify; Branch-Coverage)

Neue Methoden in `tests/contracts/test_cross_contract_chain.py`:

- `test_minimal_chain_add_is_accepted` (Positiv-Kontrast)
- `test_empty_change_state_fails` (Negativ; erwartet `semantic_contradiction`)

### Doku

- `contracts/command-semantics.md` §"Anti-Invariants" um Punkt
  *Empty asserted state* ergänzt.
- `docs/reference/agent-operability-fixture-matrix.md`: neue Klasse
  `SEM-EMPTY-ASSERTED` und Cross-Contract-Audit-Eintrag.

## Verifikation (Signalwechsel)

| Schritt                                                                | Ergebnis |
| ---------------------------------------------------------------------- | -------- |
| Probe vor Patch (Kandidat A: `add` + `exact_after=""`)                 | `[]` — toleriert |
| Probe nach Patch                                                       | `["semantic_contradiction"]` |
| Positiv-Kontrast (`add` + `exact_after` non-empty)                     | `[]` — gültig |
| `python3 tests/contracts/test_cross_contract_chain.py`                 | `Ran 16 tests, OK` |
| `python3 scripts/docmeta/test_validate_command_chain.py`               | `Ran 39 tests, OK` |
| `python3 scripts/docmeta/test_validate_agent_handoff.py`               | `Ran 13 tests, OK` |

## Geltungsgrenzen

- Klasse erfasst nur den **leerer-String**-Fall (`""`). Whitespace-only
  Strings werden bewusst nicht über diese Regel gefangen, weil `exact_*`
  Snapshots sind und Whitespace bedeutungstragend sein kann.
- Felder, die *gar nicht gesetzt* sind, bleiben weiter tolerant — das war
  bereits design-konformer Scope (Optionalität in v0.1).
- Klasse ersetzt **nicht** H2/H3; diese verbleiben außerhalb des
  v0.1-Validator-Zuständigkeitsbereichs (siehe `failure_modes.md`
  §"Validator-Überdehnung").

## Entscheidung

**Phase 2 abgeschlossen.** Strukturkonsequenz erfüllt
`method.md` §"Mindestschärfe der Strukturkonsequenz" (benannte
Äquivalenzklasse + zwei kontrastierende Fälle).
