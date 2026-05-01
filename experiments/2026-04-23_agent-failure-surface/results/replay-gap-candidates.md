---
title: "Phase 4 - Replay Reality Gap (Kandidateninventur)"
status: draft
canonicality: operative
created: "2026-04-29"
updated: "2026-05-01"
author: "Copilot Agent"
relations:
  - type: references
    target: result.md
  - type: references
    target: decision.yml
  - type: references
    target: ../method.md
---

## Phase 4 - Replay Reality Gap (Kandidateninventur)

## Outcome

Phase 4 liefert eine qualitative Kandidateninventur für blinde Stellen zwischen Dry-Run-Replay und realer Mutation. Es wurde kein Validator-, Schema-, Fixture- oder CI-Patch vorgenommen.

## Diagnose

Belegter Ist-Zustand aus Replay-Code, Tests und Schema:

1. `replay_minimal.py` simuliert eine Chain deterministisch und non-mutativ.

```python
# tools/vibe-cli/replay_minimal.py
step["would_mutate"] = False
...
"mode": "dry_run",
"would_mutate": False,
"summary": {"non_mutation_guarantee": True, ...}
```

1. Der CLI-Text grenzt den Scope explizit ein: keine echte Ausführung.

```python
# tools/vibe-cli/replay_minimal.py
"Never reads or writes target_files content - no execution, no planning, no retries."
```

1. Das v0.2-Schema erlaubt nur Dry-Run-Semantik und erzwingt `would_mutate: false`.

```json
// schemas/replay.trace.schema.json
"mode": { "const": "dry_run" },
"would_mutate": { "const": false },
"summary": {
  "properties": {
    "non_mutation_guarantee": { "const": true }
  }
}
```

1. Tests sichern Determinismus, Schema-Konformität und Nicht-Mutation, nicht reale Mutationseffekte.

```python
# tools/vibe-cli/test_replay_minimal.py
self.assertEqual(payload["mutations"], [])
self.assertFalse(trace[0]["would_mutate"])
```

```python
# tools/vibe-cli/test_replay_trace_contract.py
self.assertFalse(payload["would_mutate"])
self.assertEqual(payload["mode"], "dry_run")
self.validator.validate(payload)
```

Ableitung für Phase 4: Der aktuelle Replay-Mechanismus beweist Dry-Run-Konsistenz, aber nicht die Folgen realer Dateisystem- und Git-Zustandsänderungen.

## Hypothesen

- H1: Der Dry-Run modelliert keine echte Disk-State-Veränderung.
- H2: Der Dry-Run modelliert keine Git-Index-/Working-Tree-Folgen.
- H3: Der Dry-Run modelliert keine Locator-Drift nach partieller oder vorheriger Mutation.

## Kandidatenmatrix

| Name | Beschreibung | Betroffene Achse | Konkreter Bezug zu Replay-Code/Test/Schema | Warum Dry-Run das nicht beweisen kann | Risiko | Empfohlene spätere Prüfform | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RRG-01 Disk-State-Apply-Delta | Reale `write_change`-Anwendung kann Disk-Inhalt verändern (z. B. line endings, normalization, conflict markers), Dry-Run meldet weiter `would_mutate: false`. | Disk-State, Idempotenz vs. Nicht-Idempotenz, Validierung nach Mutation | `replay_minimal.py` setzt für `write_change` immer `would_mutate=False`; Schema erzwingt `would_mutate=false`; Tests prüfen nur diese Konstante. | Es gibt keine echte Datei-I/O auf `target_files`; nur Projektion/Simulation. | Mittel bis hoch: falsches Sicherheitsgefühl bei realem Apply-Layer. | Phase F Runner-Probe mit realem Temp-Workspace: apply -> validate -> diff -> replay-compare. | fixture_proven (was candidate_for_phase_f) |
| RRG-02 Git-Working-Tree-Index-Effects | Reale Mutationen können untracked/modified/indexed Nebenwirkungen haben; Dry-Run bildet Git-Zustand nicht ab. | Git-Index / Working Tree, Reihenfolge realer Mutationen | `replay_minimal.py` kennt keine `git`-Operationen; vorhandene Replay-Tests validieren JSON-Vertrag, nicht `git status`; `make validate-replay-mutation-guard` prüft nur dieses Tool auf Nicht-Mutation in sauberem Tree. | Replay erzeugt Trace-Objekt, aber kein Modell für staged/unstaged oder Folgeeffekte mehrerer realer Writes. | Mittel: Integrationsrisiko bei realen Runner-Ketten. | Phase F Integrationslauf mit kontrolliertem Repo-Snapshot und Git-State-Assertions pro Step. | fixture_proven (was intentional_gap) |
| RRG-03 Locator-Drift-After-Partial-Apply | Nach partieller Mutation kann derselbe Locator auf andere Stelle zeigen; Dry-Run nutzt Locator nur deklarativ. | Locator-Drift, partielle Anwendung, Reihenfolge realer Mutationen | In v0.2-Step wird `locator` nur übernommen/redacted; keine Auflösung gegen realen Dateistand. Tests prüfen Redaction und Schema, nicht Re-Resolution. | Ohne echte Mutation und Re-Read gibt es keinen Drift-Nachweis über mehrere Schritte. | Hoch: Folgekommandos können semantisch falsch adressieren. | Phase F Szenario: apply step A, dann locator-resolve für step B gegen mutierten Stand, mit erwarteter Drift-Klassifikation. | fixture_proven (was candidate_for_phase_f) |
| RRG-04 Post-Mutation-Validation-Semantics | `validate_change` im Dry-Run bleibt struktur-/contract-nah; reale post-mutation Checks (lint/test/docs) können divergieren. | Validierung nach Mutation, Reihenfolge realer Mutationen | `replay_minimal.py` führt keine realen Checks aus; Schema erlaubt `checks`/`errors` nur als deklarative Trace-Daten; Tests sichern Form, nicht reale Toolausführung. | Kein echter Tool-Run nach Mutation, daher keine Evidenz über reale Semantikdelta. | Mittel: Phase-5-Adversarialfälle können falsch eingeordnet werden. | Phase 5 oder Phase F: kontrollierter End-to-End-Run mit echter Check-Ausführung gegen mutierten Zustand. | outside_scope |

## Geltungsgrenzen

- Diese Phase ist qualitativ und argumentativ, nicht quantitativ.
- Die Inventur beweist keine Replay-Sicherheit.
- Ohne echten Runner bleibt die Aussage auf Kandidatenebene.

## Warum kein Validator-/Fixture-Patch erfolgt

- `method.md` definiert Phase 4 explizit als qualitative Kandidateninventur.
- Der Ist-Zustand zeigt keine direkt testbare, bereits reproduzierte neue Fehlklasse im bestehenden Dry-Run-Vertrag.
- Ein Hardening-Patch ohne realen Mutationsbeleg wäre spekulativ und verletzt diagnose-first.

## Konsequenz für Phase 5 / Phase F

- Phase 5 bleibt adversarial auf vorhandener Validator-Welt.
- Phase F sollte die oben priorisierten Kandidaten mit realer Mutation und Git-State-Beobachtung prüfen.
- Priorität für Phase F: RRG-03, danach RRG-01, dann RRG-02.

## Entscheidung

Phase 4 wird als `qualitative_inventory` mit `no_patch` abgeschlossen. Ergebnis ist eine kartierte Blindstellenliste für spätere reale Replay-Runner-Prüfung.

## RRG-01 Real-Run

**Status:** `fixture_proven` (2026-05-01)

**Artefakt:** `artifacts/run-phase-f-rrg01-real/`

**Szenario:** CRLF-to-LF-Normalisierung durch den Apply-Layer.
Das Fixture (`before.md`) wurde mit CRLF-Zeilenenden im Temp-Workspace initialisiert.
Step A (`Load config from file.` → `Load config from disk.`) wurde real über
`read_text` (Universal-Newline-Read, CRLF → LF im Speicher) + expliziter LF-Write (`open(..., newline="\n")`) angewendet.

**Ergebnis Real-Run:**

| Feld | Wert |
|------|------|
| `sha256_before` (CRLF) | `35265e7307dad1afe98c9514f59189db58a80de782fd653878bbbaec9f58e269` |
| `sha256_after` (LF) | `42cccfcc322444cbd34b43b0dda050b6d312e5e120bf509e17e6fe3f7b34c92d` |
| `step_b_exact_before_found` | `false` |
| `classification` | `content_drifted` |
| `patch_gate.triggered` | `true` |

**Failure-Mode bestätigt:** Content-/Snapshot-Drift, nicht Locator-Positionsdrift.
Step B's `exact_before` enthielt `\r\n`; nach Step A ist nur noch `\n` auf Disk.
Der Dry-Run würde diesen Drift nicht erkennen (non-mutating, kein echtes Disk-I/O).

**Epistemische Grenze:** Beweis gilt ausschließlich für diese Fixture (fixture_only).
Keine allgemeine Aussage über Runner-Korrektheit oder beste Remediation-Strategie.

## RRG-02 Real-Run

**Status:** `fixture_proven` (2026-05-01)

**Artefakt:** `artifacts/run-phase-f-rrg02-real/`

**Szenario:** Git-Working-Tree-Index-Drift durch gestufte + nicht-gestufte Mutation.
Das Fixture (`before.md`) wurde in einem echten Temp-Git-Repo committed (sauberer Baseline).
Step A (Mutation 1): `Use safe deployment mode.` → `Use staged deployment mode.` — gemutiert und mit `git add` gestaged.
Step A (Mutation 2): `Validate rollback before release.` → `Validate rollback after release.` — gemutiert OHNE Staging.
Damit entstehen drei unterscheidbare Zustände:
- HEAD = Original (beide Zeilen unverändert)
- Index = nur Mutation 1 gestaged
- Working Tree = Mutation 1 + Mutation 2

**Ergebnis Real-Run:**

| Feld | Wert |
|------|------|
| `git status --short` nach Step A | `MM before.md` |
| `head_file_sha256_after_step_a` | `751ebb6758a0dff93bbfee4410eb946a2e65c16274266cda55ad1da23c7bb1a2` |
| `index_file_sha256_after_step_a` | `1783dc90178f0632dc2f22119ae323becf6f29654146cd9da6a2ae6c55a2d987` |
| `working_tree_file_sha256_after_step_a` | `a6115469675dd4667dc645b6693666233d535aa39ab726098f9de12d4b4e239a` |
| `found_in_head` | `true` |
| `found_in_index` | `true` |
| `found_in_working_tree` | `false` |
| `classification` | `git_state_drifted` |
| `patch_gate.triggered` | `true` |

**Failure-Mode bestätigt:** Git-State-Divergenz über HEAD/Index/Working-Tree.
Step B's `exact_before` (`Validate rollback before release.`) ist in HEAD und Index vorhanden,
aber nicht im Working Tree nach der nicht-gestageten zweiten Mutation.
Der Dry-Run bildet keinen Git-Zustand ab; er kann diese Drei-Wege-Divergenz nicht modellieren.

**Epistemische Grenze:** Beweis gilt ausschließlich für diese Fixture (fixture_only).
Keine allgemeine Aussage über Runner-Korrektheit oder beste Remediation-Strategie.

