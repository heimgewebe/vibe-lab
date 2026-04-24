---
title: "Methode: Phase 1 Drift Injection"
status: draft
canonicality: operative
created: "2026-04-23"
updated: "2026-04-24"
author: "GPT-5.3-Codex"
relations:
  - type: references
    target: ../../schemas/agent.handoff.schema.json
---

# Phase 1: Drift Injection — Contract-Reality Method

> Scope: nur `agent_handoff` nach `schemas/agent.handoff.schema.json`.
> Status: Design-only (`designed`), keine Ausführung in diesem PR.

## Ziel

Phase 1 testet gezielte Drift-Mutationen gegen reale HANDOFF-Felder aus
`tests/fixtures/agent_handoff/pass-minimal.json`, um belegbar zu prüfen, ob
der aktuelle Validator erwartbar klassifiziert (accept vs reject).

## Reale Feldbasis

Die Phase-1-Mutationen verwenden ausschließlich reale Felder:

- `locator`
- `target_files`
- `change_type`
- `handoff.hash` (sha256, 64-hex)

Nicht verwendet werden Fantasiefelder wie `handoff_target.locator`,
`state.target_files` oder `version`.

## Kanonische Fallliste (genau 6)

### A1: Locator Drift (invalid path)
- Mutation: `locator`
- Erwartung: `reject`

### A2: Locator Drift (fragment probe)
- Mutation: `locator`
- Erwartung: `probe` (klassifizieren, nicht vorwegnehmen)

### B1: Hash Drift (vollständig geändert)
- Mutation: `handoff.hash`
- Erwartung: `reject`

### B2: Hash Drift (1 nibble geändert)
- Mutation: `handoff.hash`
- Erwartung: `reject`

### C1: target_files Drift (ungültiger Zielpfad)
- Mutation: `target_files[0]`
- Erwartung: `reject`

### D1: change_type Drift (unerlaubter Enum-Wert)
- Mutation: `change_type`
- Erwartung: `reject`

## Ausführungsmethode Für Den Späteren Execution-PR

1. Baseline-Guard:

```bash
make validate
```

2. Sechs mutierte JSON-Fixtures in einem Staging-Verzeichnis erzeugen
   (z. B. `artifacts/staging/phase-1-agent-handoff/`).

3. Genau dieses Staging-Verzeichnis gegen den realen Validator prüfen:

```bash
python3 scripts/docmeta/validate_agent_handoff.py \
  --fixtures artifacts/staging/phase-1-agent-handoff \
  --mode strict
```

Hinweis: `make validate` validiert standardmäßig das Repo-Fixture-Set unter
`tests/fixtures/agent_handoff/`, nicht automatisch ein temporäres Staging-Verzeichnis.

4. Für jeden der 6 Fälle Ergebnis klassifizieren und in `results/evidence.jsonl`
   mit repo-konformen Schlüsseln dokumentieren.

5. Für den ersten realen Lauf `artifacts/run-template.md` als Protokollgerüst
  verwenden und die Diagnose-First Baseline-Ausgaben in
  `artifacts/<run-id>/execution.txt` sichern.

## Stop-Regel

- success: alle 6 Fälle liefern klassifiziertes Validator-Verhalten und es gibt
  keinen False-Positive-Befund.
- patch_needed: mindestens ein Fall zeigt belegte Lücke (insb. false positive).
- inconclusive: Klassifikation für mindestens einen Fall bleibt unklar.

## Patch-Gate (nur falls `patch_needed`)

Kontrastpaar ist nur dort Pflicht, wo tatsächlich ein positiver Referenzfall für
dieselbe Driftklasse definiert werden kann. Keine formale Kontrastpflicht für
Einzelfälle ohne sinnvollen Gegenfall.
