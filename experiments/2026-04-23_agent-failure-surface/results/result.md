---
title: "Result: Agent Failure Surface Mapping — Serienbericht (Phase 2 + 3 + 4 + 5)"
status: draft
canonicality: operative
created: "2026-04-29"
updated: "2026-04-30"
author: "Copilot Agent (GPT-5.x)"
relations:
  - type: references
    target: ../method.md
  - type: references
    target: ../../../contracts/command-semantics.md
  - type: references
    target: ../../../docs/reference/agent-operability-fixture-matrix.md
  - type: references
    target: phase2-semantic-contradiction.md
  - type: references
    target: phase3-chain-integrity-stress.md
  - type: references
    target: phase5-adversarial-agent-simulation.md
  - type: references
    target: decision.yml
  - type: references
    target: replay-gap-candidates.md
---

# result.md — Serienbericht (Phase 2 + 3 + 4)

Dieser Bericht ist der kumulative Ergebnisstand der Reihe
*Agent Failure Surface Mapping*. Jede Phase hat einen eigenen
Phasen-Ergebnisbericht unter `results/`:

- Phase 2 — Semantic Contradiction: `results/phase2-semantic-contradiction.md`
- Phase 3 — Chain Integrity Stress: `results/phase3-chain-integrity-stress.md`
- Phase 4 — Replay Reality Gap: `results/replay-gap-candidates.md`

Die Entscheidung für die aktuell abgeschlossenen Phasen ist in
`results/decision.yml` (kumulativ, `verdict: mixed`).

---

## Gesamtstatus der Serie

| Phase | Leithypothese | Ergebnis | Strukturkonsequenz |
| ----- | ------------- | -------- | ------------------ |
| 1 — Drift Injection | Kleine Drifts (Off-by-one, Trailing-Slash) werden nicht erkannt | (in eigenem PR — nicht Gegenstand dieser Artefakte) | — |
| **2 — Semantic Contradiction** | Formal gültige, semantisch vakuume `exact_*`-Zustände werden toleriert | **confirms** — Klasse SEM-EMPTY-ASSERTED belegt | Validator-Erweiterung, 3 Negativ-Fixtures, 2 Cross-Contract-Fixtures, 6 Tests |
| **3 — Chain Integrity Stress** | Valide Einzelcommands können in falscher Reihenfolge/Kombination als Chain ungültig sein, ohne dass bestehende Validatoren das melden | **refutes** (im geprüften Kandidatenraum) — alle 7 Kandidaten erkannt, Toleranz-Rate 0/7 | No-Patch — kein Fixture, kein Validator-Eingriff |
| **4 — Replay Reality Gap** | Replay-Dry-Run kann realen Mutations-/Side-Effect-Status verfehlen | **qualitative_inventory** (no_patch) | Kandidateninventur dokumentiert; bewusst keine Validator-/Schema-/Fixture-Änderung |
| 5 — Adversarial Agent Simulation | (folgt) | — | — |

---

## Phase 2 — Semantic Contradiction: confirms

**Kurzfassung** (Vollbericht: `results/phase2-semantic-contradiction.md`):

Eine bislang tolerierte semantische Widerspruchsklasse —
*"empty asserted state"* (`exact_*` auf der semantisch geforderten Seite
gesetzt, aber leer `""`) — wurde reproduzierbar belegt und strukturell
verankert. Initiale Probe: 6/6 Kandidaten toleriert, davon A–D zur Klasse
H1/SEM-EMPTY-ASSERTED. Nach Patch: 0/4 H1-Kandidaten korrekt abgewiesen;
H2/H3 bleiben outside_scope.

### Strukturkonsequenz Phase 2

- `scripts/docmeta/validate_command_chain.py` —
  `_validate_semantic_anti_invariants` um Klasse *empty asserted state*
  erweitert.
- **Fixtures (Negativ):** `tests/fixtures/command_chains/invalid-empty-asserted-state.json` (add),
  `tests/fixtures/command_chains/invalid-empty-asserted-state-remove.json` (remove),
  `tests/fixtures/command_chains/invalid-empty-asserted-state-modify.json` (modify);
  `cross_contract/invalid/empty_change_state.json`.
- **Fixture (Positiv-Kontrast):** `cross_contract/valid/minimal_chain_add.json`.
- **Tests:** 4 neue Methoden in `test_validate_command_chain.py`, 2 in
  `test_cross_contract_chain.py`.
- **Doku:** `contracts/command-semantics.md` §Anti-Invariants um *Empty
  asserted state* ergänzt; `docs/reference/agent-operability-fixture-matrix.md`
  Klasse `SEM-EMPTY-ASSERTED`.

### Verifikation Phase 2

| Schritt | Ergebnis |
| ------- | -------- |
| Kandidat A vor Patch (`add` + `exact_after=""`) | `[]` — toleriert |
| Kandidat A nach Patch | `["semantic_contradiction"]` |
| Positiv-Kontrast (non-empty `exact_after`) | `[]` — gültig |
| `test_validate_command_chain.py` | `Ran 39 tests, OK` |
| `test_cross_contract_chain.py` | `Ran 16 tests, OK` |
| `test_validate_agent_handoff.py` | `Ran 13 tests, OK` |

Laufartefakt: `artifacts/run-phase2/run_meta.json`,
`artifacts/run-phase2/execution.txt`.

---

## Phase 3 — Chain Integrity Stress: refutes (im geprüften Kandidatenraum)

**Kurzfassung** (Vollbericht: `results/phase3-chain-integrity-stress.md`):

Sieben konstruierte Transition-Kandidaten (falsche Reihenfolge, Mehrfach-Write,
gemischte Versionen, fehlender `write_change`, `target_files`-Mismatch) wurden
direkt gegen `validate_chain` geprüft. Alle sieben lösen mindestens einen
dokumentierten Fehlercode aus. Die Phase-3-Antithese
(„bestehende Chain-Validatoren decken diese Fehler bereits ab") wurde bestätigt;
die Leithypothese im geprüften Kandidatenraum widerlegt.

### Kandidatenmatrix Phase 3 (Kurzform)

| # | Kandidat | Observed codes | Bewertung |
| - | -------- | -------------- | --------- |
| A | `read→write→write→validate` | `command_sequence_invalid` | already_detected |
| B | `read→validate` (kein write) | `command_sequence_invalid`, `validate_without_write` | already_detected |
| C | gemischte Versionen v0.1/v0.2 | `command_sequence_invalid`, `contract_invalid` | already_detected |
| D | `validate→read→write` | `command_sequence_invalid`, `validate_without_write` | already_detected |
| E | `write.target_files` ⊄ `read.target_files` | `target_files_mismatch` | already_detected |
| F | `add` dann `remove` (zwei writes) | `command_sequence_invalid` | already_detected |
| G | `write.target_files=[]` vor `validate(checks)` | `contract_invalid`, `validate_targets_out_of_scope` | already_detected |
| – | `validate_change.locator B abweichend` | n/a | outside_scope |

Toleranz-Rate: **0/7**.

### Strukturkonsequenz Phase 3

**No-Patch.** `method.md` §"Patch-Gate" greift nicht (kein
`tolerated_but_wrong`). Mindestschärfe über belegte
Nicht-Änderungsentscheidung mit Kandidatenmatrix + Testausgabe erfüllt.

### Verifikation Phase 3

| Schritt | Ergebnis |
| ------- | -------- |
| Probe Kandidaten A–G | 0/7 toleriert |
| `test_validate_command_chain.py` | `Ran 39 tests, OK` |
| `test_cross_contract_chain.py` | `Ran 16 tests, OK` |
| `test_fixture_matrix_audit_surface.py` | `Ran 1 test, OK` |
| `test_fixture_matrix_known_gaps_audit.py` | `Ran 1 test, OK` |
| `test_promotion_readiness.py` | `Ran 99 tests, OK` |
| `validate_promotion_readiness.py` | dry-run, exit=0 |
| `make validate` | ✅ Validation passed |

Laufartefakt: `artifacts/run-phase3/run_meta.json`,
`artifacts/run-phase3/execution.txt`.

---

## Phase 4 — Replay Reality Gap: qualitative_inventory (no_patch)

**Vollbericht:** `results/replay-gap-candidates.md`

Phase 4 ergänzt die vorhandene Serienhistorie (Phase 2 + 3), ersetzt sie
nicht. Sie dokumentiert eine qualitative Kandidateninventur zur Lücke zwischen
Replay-Dry-Run und realer Ausführungswahrheit:

Priorisierte Kandidaten für Phase F:

- RRG-03 — Locator-Drift-After-Partial-Apply
- RRG-01 — Disk-State-Apply-Delta
- RRG-02 — Git-Working-Tree-Index-Effects

Ergänzend dokumentiert, aber aktuell nicht priorisiert:

- RRG-04 — Post-Mutation-Validation-Semantics

Scope-Entscheidung in Phase 4: **No-Patch** (diagnosis-first). Keine Änderung
an Validatoren, Schemas, Fixtures oder CI-Härtung; nur Inventur und Evidenz.

---

## Phase 5 — Adversarial Agent Simulation: out_of_scope_documented

**Vollbericht:** `results/phase5-adversarial-agent-simulation.md`

Phase 5 ergänzt die vorhandene Serienhistorie (Phase 2 + 3 + 4), ersetzt sie nicht.
Sie prüft, ob formal gültige, epistemisch leere Agent-Outputs den bestehenden
Validator-Stack passieren.

### Simulationsmatrix Phase 5

| Simulation | Beschreibung | Klassifikation |
| ---------- | ------------ | -------------- |
| P5-A | `read_context.extracted_facts: ["ok"]` — triviale Strings, schema-konform | `passed_but_out_of_scope` |
| P5-B | `write_change.exact_after: "\n"` (Whitespace), Handoff `scope` behauptet Substanzarbeit | `passed_but_out_of_scope` |
| P5-C | `validate_change.checks: ["css-audit", "design-review"]` für Python-Datei | `passed_but_out_of_scope` |
| P5-D | `write_change change_type=modify`, kein `exact_before`, kein `exact_after` | `passed_but_out_of_scope` |

Toleranz-Rate: **4/4** (alle Simulationen passieren den Validator-Stack).
Patch-Gate: **nicht ausgelöst** (kein `passed_but_wrong`-Fall).

### Strukturkonsequenz Phase 5

**Out-of-Scope-Documented** (kein Patch):

- `decisions/process/p5-validator-scope-boundary.yml` — formale Dokumentation
  der vier identifizierten Scope-Grenzen.
- `docs/reference/agent-operability-fixture-matrix.md` — Known Gaps §5.5 bis §5.8
  um P5-A bis P5-D erweitert.

### Ergebnis Phase 5 (Vorhypothese vs. Antithese)

- **Vorhypothese** bestätigt: Der Stack kann von epistemisch leeren, formal
  gültigen Outputs getäuscht werden.
- **Antithese** widerlegt (partiell): Der Stack verhindert form-ungültige und
  strukturell inkonsistente Outputs, ist aber kein Inhaltsrichter.
- **Präzisierung**: Die vier identifizierten „Lücken" sind keine Validator-Fehler
  innerhalb des deklarierten Scopes — sie sind bewusste v0.1-Architekturentscheidungen.

### Verifikation Phase 5

| Schritt | Ergebnis |
| ------- | -------- |
| P5-A (validate_agent_commands + chain) | exit 0 — `passed_but_out_of_scope` |
| P5-B (validate_agent_handoff + cross-contract) | exit 0 — `passed_but_out_of_scope` |
| P5-C (validate_command_chain) | exit 0 — `passed_but_out_of_scope` |
| P5-D (validate_command_chain) | exit 0 — `passed_but_out_of_scope` |
| `make validate` | ✅ Validation passed |

Laufartefakt: `artifacts/run-phase5/run_meta.json`, `artifacts/run-phase5/execution.txt`.

---

## Serienstatus (nach Abschluss Phase 5)

| Phase | Leithypothese | Ergebnis | Strukturkonsequenz |
| ----- | ------------- | -------- | ------------------ |
| 1 — Drift Injection | Kleine Drifts werden nicht erkannt | (eigenem PR) | — |
| **2 — Semantic Contradiction** | Leere asserted states toleriert | **confirms** | Validator + Fixtures + Tests |
| **3 — Chain Integrity Stress** | Transitions-Fehler unerkannt | **refutes** (No-Patch) | — |
| **4 — Replay Reality Gap** | Replay bildet reale Mutationen nicht ab | **qualitative_inventory** (No-Patch) | Kandidateninventur |
| **5 — Adversarial Agent Simulation** | Stack kann durch epistemisch leere Outputs getäuscht werden | **confirms** (out_of_scope_documented) | Scope-Grenze dokumentiert |

Nächster Schritt: **Phase F** (reale Mutationsausführung) für RRG-01, RRG-02, RRG-03.
