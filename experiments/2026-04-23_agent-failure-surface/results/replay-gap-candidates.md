---
title: "Phase 4 - Replay Reality Gap (Kandidateninventur)"
status: draft
canonicality: operative
created: "2026-04-29"
updated: "2026-04-29"
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

Phase 4 liefert eine qualitative Kandidateninventur fuer blinde Stellen zwischen Dry-Run-Replay und realer Mutation. Es wurde kein Validator-, Schema-, Fixture- oder CI-Patch vorgenommen.

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

1. Der CLI-Text grenzt den Scope explizit ein: keine echte Ausfuehrung.

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

1. Tests sichern Determinismus, Schema-Konformitaet und Nicht-Mutation, nicht reale Mutationseffekte.

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

Ableitung fuer Phase 4: Der aktuelle Replay-Mechanismus beweist Dry-Run-Konsistenz, aber nicht die Folgen realer Dateisystem- und Git-Zustandsaenderungen.

## Hypothesen

- H1: Der Dry-Run modelliert keine echte Disk-State-Veraenderung.
- H2: Der Dry-Run modelliert keine Git-Index-/Working-Tree-Folgen.
- H3: Der Dry-Run modelliert keine Locator-Drift nach partieller oder vorheriger Mutation.

## Kandidatenmatrix

| Name | Beschreibung | Betroffene Achse | Konkreter Bezug zu Replay-Code/Test/Schema | Warum Dry-Run das nicht beweisen kann | Risiko | Empfohlene spaetere Pruefform | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RRG-01 Disk-State-Apply-Delta | Reale `write_change`-Anwendung kann Disk-Inhalt veraendern (z. B. line endings, normalization, conflict markers), Dry-Run meldet weiter `would_mutate: false`. | Disk-State, Idempotenz vs. Nicht-Idempotenz, Validierung nach Mutation | `replay_minimal.py` setzt fuer `write_change` immer `would_mutate=False`; Schema erzwingt `would_mutate=false`; Tests pruefen nur diese Konstante. | Es gibt keine echte Datei-I/O auf `target_files`; nur Projektion/Simulation. | Mittel bis hoch: falsches Sicherheitsgefuehl bei realem Apply-Layer. | Phase F Runner-Probe mit realem Temp-Workspace: apply -> validate -> diff -> replay-compare. | candidate_for_phase_f |
| RRG-02 Git-Working-Tree-Index-Effects | Reale Mutationen koennen untracked/modified/indexed Nebenwirkungen haben; Dry-Run bildet Git-Zustand nicht ab. | Git-Index / Working Tree, Reihenfolge realer Mutationen | `replay_minimal.py` kennt keine `git`-Operationen; vorhandene Replay-Tests validieren JSON-Vertrag, nicht `git status`; `make validate-replay-mutation-guard` prueft nur dieses Tool auf Nicht-Mutation in sauberem Tree. | Replay erzeugt Trace-Objekt, aber kein Modell fuer staged/unstaged oder Folgeeffekte mehrerer realer Writes. | Mittel: Integrationsrisiko bei realen Runner-Ketten. | Phase F Integrationslauf mit kontrolliertem Repo-Snapshot und Git-State-Assertions pro Step. | intentional_gap |
| RRG-03 Locator-Drift-After-Partial-Apply | Nach partieller Mutation kann derselbe Locator auf andere Stelle zeigen; Dry-Run nutzt Locator nur deklarativ. | Locator-Drift, partielle Anwendung, Reihenfolge realer Mutationen | In v0.2-Step wird `locator` nur uebernommen/redacted; keine Aufloesung gegen realen Dateistand. Tests pruefen Redaction und Schema, nicht Re-Resolution. | Ohne echte Mutation und Re-Read gibt es keinen Drift-Nachweis ueber mehrere Schritte. | Hoch: Folgekommandos koennen semantisch falsch adressieren. | Phase F Szenario: apply step A, dann locator-resolve fuer step B gegen mutierten Stand, mit erwarteter Drift-Klassifikation. | candidate_for_phase_f |
| RRG-04 Post-Mutation-Validation-Semantics | `validate_change` im Dry-Run bleibt struktur-/contract-nah; reale post-mutation Checks (lint/test/docs) koennen divergieren. | Validierung nach Mutation, Reihenfolge realer Mutationen | `replay_minimal.py` fuehrt keine realen Checks aus; Schema erlaubt `checks`/`errors` nur als deklarative Trace-Daten; Tests sichern Form, nicht reale Toolausfuehrung. | Kein echter Tool-Run nach Mutation, daher keine Evidenz ueber reale Semantikdelta. | Mittel: Phase-5-Adversarialfaelle koennen falsch eingeordnet werden. | Phase 5 oder Phase F: kontrollierter End-to-End-Run mit echter Check-Ausfuehrung gegen mutierten Zustand. | outside_scope |

## Geltungsgrenzen

- Diese Phase ist qualitativ und argumentativ, nicht quantitativ.
- Die Inventur beweist keine Replay-Sicherheit.
- Ohne echten Runner bleibt die Aussage auf Kandidatenebene.

## Warum kein Validator-/Fixture-Patch erfolgt

- `method.md` definiert Phase 4 explizit als qualitative Kandidateninventur.
- Der Ist-Zustand zeigt keine direkt testbare, bereits reproduzierte neue Fehlklasse im bestehenden Dry-Run-Vertrag.
- Ein Hardening-Patch ohne realen Mutationsbeleg waere spekulativ und verletzt diagnose-first.

## Konsequenz fuer Phase 5 / Phase F

- Phase 5 bleibt adversarial auf vorhandener Validator-Welt.
- Phase F sollte die oben priorisierten Kandidaten mit realer Mutation und Git-State-Beobachtung pruefen.
- Prioritaet fuer Phase F: RRG-03, danach RRG-01, dann RRG-02.

## Entscheidung

Phase 4 wird als `qualitative_inventory` mit `no_patch` abgeschlossen. Ergebnis ist eine kartierte Blindstellenliste fuer spaetere reale Replay-Runner-Pruefung.
