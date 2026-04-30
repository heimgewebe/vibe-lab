---
title: "Phase F — RRG-03 Locator Drift (Real Execution Evidence)"
status: draft
canonicality: operative
created: "2026-04-30"
updated: "2026-04-30"
author: "Claude Opus 4.7"
relations:
  - type: references
    target: ../method.md
  - type: references
    target: result.md
  - type: references
    target: replay-gap-candidates.md
  - type: references
    target: evidence.jsonl
  - type: references
    target: ../artifacts/run-phase-f-rrg03/run_meta.json
  - type: references
    target: ../artifacts/run-phase-f-rrg03/execution.txt
  - type: references
    target: ../artifacts/run-phase-f-rrg03-real/run_meta.json
  - type: references
    target: ../artifacts/run-phase-f-rrg03-real/observed.json
  - type: references
    target: ../artifacts/run-phase-f-rrg03-real/execution-real.txt
  - type: references
    target: ../artifacts/run-phase-f-rrg03-real-02/run_meta.json
  - type: references
    target: ../artifacts/run-phase-f-rrg03-real-02/observed.json
  - type: references
    target: ../artifacts/run-phase-f-rrg03-real-02/execution-real.txt
---

## Phase F — RRG-03 Locator Drift (Real Execution Evidence)

Status: real-execution-evidence

## Ziel

RRG-03 unter kontrollierten Bedingungen real pruefen, ohne die historisierte diagnosis-first Planung unsichtbar zu ueberschreiben.

## Scope und Grenzen

- Keine Runtime-, Schema-, Validator- oder CI-Aenderung in diesem Evidence-PR.
- Kein Runner-Patch.
- Kein Schema-Patch.
- Kein Validator-Patch.
- Kein CI-Gate.
- Keine Remediation-Strategieentscheidung.

## Zwei Ebenen derselben Phase

- Planning-Run: `artifacts/run-phase-f-rrg03/`
- Real-Run: `artifacts/run-phase-f-rrg03-real/`

Der Planning-Run bleibt der historisierte diagnosis-first Stand. Er beschreibt die Versuchsanordnung und bleibt:

- Proof status: NOT_PROVEN
- Patch-Gate: NOT_TRIGGERED

Der additive Real-Run dokumentiert die spaeter tatsaechlich ausgefuehrte kontrollierte Mutation und zeigt:

- Proof status: PROVEN_FOR_FIXTURE
- Patch-Gate: TRIGGERED

## Planning-Run

Siehe:

- `../artifacts/run-phase-f-rrg03/run_meta.json`
- `../artifacts/run-phase-f-rrg03/execution.txt`

Dieser Run bleibt diagnosis-first. Er beweist noch keinen Drift, sondern definiert nur Fixture, diagnostisches Vokabular und Patch-Gate-Bedingung.

## Real-Run Befund

Siehe:

- `../artifacts/run-phase-f-rrg03-real/run_meta.json`
- `../artifacts/run-phase-f-rrg03-real/observed.json`
- `../artifacts/run-phase-f-rrg03-real/execution-real.txt`

Beobachteter Ablauf:

- C1: locator "Validate token" matched 2 hits, selected index 0, line 4, byte 33-47.
- C2: "Validate token before session creation." wurde ersetzt durch "Check token before session creation."
- C3: locator "Validate token" matched 1 hit, selected index 0, line 7, byte 81-95.
- Klassifikation: drifted.
- Patch-Gate: TRIGGERED.

## Interpretation

Diese kontrollierte Fixture belegt RRG-03 fuer genau dieses Szenario: Nach realer Step-A-Mutation driftet der Step-B-Locator von C1 Zeile 4 auf C3 Zeile 7.

## Claim Boundary

Der Befund beweist nicht:

- allgemeine Runner-Korrektheit
- allgemeine Locator-Sicherheit
- unmittelbare Notwendigkeit eines Runtime-Patches
- beste Patch-Strategie

## Additional Real-Run 02 — Injection-Before Pattern

Siehe:

- `../artifacts/run-phase-f-rrg03-real-02/run_meta.json`
- `../artifacts/run-phase-f-rrg03-real-02/observed.json`
- `../artifacts/run-phase-f-rrg03-real-02/execution-real.txt`

Fixture: `../artifacts/run-phase-f-rrg03-real-02/fixtures/before.md` — API Gateway Notes,
Locator Step B: `"Process request"` (3 Treffer in Before-Stand).

Beobachteter Ablauf:

- C1: locator "Process request" matched 3 hits, selected index 0, line 7, byte 80-95.
- C2: Step A ersetzte "Validate request before routing." durch
  "Process request before routing.\nValidate request before routing." —
  fuegte oberhalb des C1-Ziels eine neue identische Locator-Zeile ein.
- C3: locator "Process request" matched 4 hits, selected index 0, line 4, byte 30-45
  (der neu eingefuegte Treffer, nicht das originale C1-Ziel).
- Klassifikation: drifted.
- Patch-Gate: TRIGGERED.

Drift-Mechanismus (Run 02 vs. Run 01):

| | Run 01 | Run 02 |
|---|---|---|
| Drift-Muster | Removal-drift: erster Treffer entfernt, zweiter wird erster | Injection-before-drift: neuer Treffer oberhalb eingefuegt, Index-0 zeigt auf Injektion |
| C1 line/byte | line 4, byte 33-47 | line 7, byte 80-95 |
| C3 line/byte | line 7, byte 81-95 | line 4, byte 30-45 |
| match_count C1→C3 | 2→1 | 3→4 |
| Klassifikation | drifted | drifted |
| Patch-Gate | TRIGGERED | TRIGGERED |

Claim Boundary Run 02 (unveraendert gegenueber Run 01):
Beweist nur dieses Fixture-Szenario. Beweist nicht allgemeine Runner-Korrektheit,
allgemeine Locator-Sicherheit oder beste Remediation-Strategie.
