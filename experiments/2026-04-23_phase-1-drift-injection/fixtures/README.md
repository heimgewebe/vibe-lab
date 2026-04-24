---
title: "Fixtures: Phase 1 Drift Injection"
status: draft
canonicality: operative
created: "2026-04-23"
updated: "2026-04-24"
author: "GPT-5.3-Codex"
relations:
  - type: references
    target: ../../../schemas/agent.handoff.schema.json
---

# Phase 1 Fixtures Specification

> Dieses Dokument ist eine **Spezifikation**.
> Es ist nicht die operative Wahrheit der Ausführung.
> Konkrete JSON-Fixtures entstehen erst im Execution-PR und werden dort
> über `results/evidence.jsonl` belegt.

---

## Schema-Kontext

- Zielschema: `schemas/agent.handoff.schema.json`
- Baseline: `tests/fixtures/agent_handoff/pass-minimal.json`

## Struktur

Jede Fallspezifikation enthält:
- `case_id`: Case identifier (A1, A2, B1, etc.)
- `category`: Equivalence class (locator, hash, normalization, etc.)
- `base_fixture`: Which valid fixture is being mutated
- `mutation`: Description of the change
- `expected_validator_behavior`: What should happen
- `artifact`: nur als Platzhalter beschrieben, nicht als ausgeführter Befund

---

## Kanonische Fallliste (genau 6)

## A1: Locator Drift (invalid path)

```yaml
case_id: A1
category: locator_drift
base_fixture: tests/fixtures/agent_handoff/pass-minimal.json
mutation:
  field: locator
  change: "schemas/agent.handoff.schema.json" -> "schemas/agent.INVALID.schema.json"
  rationale: "Ungültiger Locator-Pfad"
expected_validator_behavior: REJECTED
expected_error_type: "locator_mismatch or similar"
contrast_pair: A2
notes: "Kontrast mit A2 vorhanden"
```

## A2: Locator Drift (fragment probe)

```yaml
case_id: A2
category: locator_drift
base_fixture: tests/fixtures/agent_handoff/pass-minimal.json
mutation:
  field: locator
  change: "schemas/agent.handoff.schema.json" -> "schemas/agent.handoff.schema.json#L1"
  rationale: "Probe für Fragment-Behandlung"
expected_validator_behavior: "? (probe — result will determine)"
expected_error_type: null
contrast_pair: A1
notes: "Kontrast zu A1"
```

## B1: Hash Drift (vollständig geändert)

```yaml
case_id: B1
category: hash_drift
base_fixture: tests/fixtures/agent_handoff/pass-minimal.json
mutation:
  field: handoff.hash
  change: "28b6bdd9a176ee782cfd69cc8a7fb7da17c5fd154cda67faadf3402d79cf33e2" -> "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
  rationale: "64-hex bleibt formal gültig, soll aber Hash-Mismatch auslösen"
expected_validator_behavior: REJECTED
expected_error_type: "hash_mismatch or validation_error"
contrast_pair: B2
notes: "Kontrast mit B2 vorhanden"
```

## B2: Hash Drift (1 nibble geändert)

```yaml
case_id: B2
category: hash_drift
base_fixture: tests/fixtures/agent_handoff/pass-minimal.json
mutation:
  field: handoff.hash
  change: "28b6bdd9a176ee782cfd69cc8a7fb7da17c5fd154cda67faadf3402d79cf33e2" -> "18b6bdd9a176ee782cfd69cc8a7fb7da17c5fd154cda67faadf3402d79cf33e2"
  rationale: "Minimale Änderung bei weiter formal gültigem 64-hex"
expected_validator_behavior: REJECTED
expected_error_type: "hash_mismatch"
contrast_pair: B1
notes: "Kontrast zu B1"
```

## C1: target_files Drift (ungültiger Zielpfad)

```yaml
case_id: C1
category: target_files_drift
base_fixture: tests/fixtures/agent_handoff/pass-minimal.json
mutation:
  field: target_files[0]
  change: "schemas/agent.handoff.schema.json" -> "schemas/agent.handoff.schema.json.backup"
  rationale: "Soll gegen erwarteten Contract-Pfad fehlschlagen"
expected_validator_behavior: REJECTED
expected_error_type: "hash_mismatch or contract_invalid"
contrast_pair: null
notes: "Einzelfall ohne belastbaren positiven Gegenfall in Phase 1"
```

## D1: change_type Drift (ungültiger Enum-Wert)

```yaml
case_id: D1
category: change_type_drift
base_fixture: tests/fixtures/agent_handoff/pass-minimal.json
mutation:
  field: change_type
  change: "add" -> "rename"
  rationale: "Nicht im Enum {add, modify, remove, replace}"
expected_validator_behavior: REJECTED
expected_error_type: "contract_invalid"
contrast_pair: null
notes: "Einzelfall ohne belastbaren positiven Gegenfall in Phase 1"
```

---

## Übergabe In Den Execution-PR

1. Die 6 Spezifikationen als echte JSON-Fixtures materialisieren.
2. Fixtures in ein Staging-Verzeichnis legen und explizit mit
  `python3 scripts/docmeta/validate_agent_handoff.py --fixtures <staging_dir> --mode strict`
  prüfen.
3. Ergebnisse ausschließlich im Execution-PR entscheiden (success / patch_needed / inconclusive).

---

## Hinweise

- Dieses Dokument ist absichtlich nicht normativ für Ergebnisbehauptungen.
- Ergebnisclaims entstehen erst durch Laufspuren im Execution-PR.
- Kontrastpaare werden nur dort verwendet, wo ein sinnvoller Gegenfall existiert.
