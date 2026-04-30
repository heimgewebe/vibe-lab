# Phase F — RRG-03 Locator Drift (Planning)

Status: planning-only

## Ziel
RRG-03 real ausführen: kontrollierte partielle Mutation und Re-Resolution gegen denselben Locator.

## Scope und Grenzen
- Keine Runtime-, Schema-, Validator- oder CI-Änderung in diesem Planungsschritt.
- Kein Runner-Patch.
- Kein Schema-Patch.
- Kein Validator-Patch.
- Kein CI-Gate.

## Proof Status
- Proof status: NOT_PROVEN
- Patch-Gate: NOT_TRIGGERED

## Geplanter kontrollierter Ablauf
1. Baseline-Resolution (C1) des Locators aus Step B gegen unveränderte Arbeitskopie.
2. Reale Anwendung von Step A auf Temp-Arbeitskopie (C2).
3. Re-Resolution desselben Step-B-Locators gegen mutierten Stand (C3).
4. Klassifikation: stable | drifted | ambiguous | not_found (C4).
5. Dry-Run-Abgleich: Baseline, kein Orakel für mutierten Zustand (C5).

## Fixtures
Siehe:
- artifacts/run-phase-f-rrg03/fixtures/before.md
- artifacts/run-phase-f-rrg03/fixtures/step-a.json
- artifacts/run-phase-f-rrg03/fixtures/step-b.json
- artifacts/run-phase-f-rrg03/fixtures/expected.json

## Real Execution Result

- run_id: run-phase-f-rrg03-real
- classification: drifted
- patch-gate: TRIGGERED
- evidence artifact: artifacts/run-phase-f-rrg03/observed.json
- execution log: artifacts/run-phase-f-rrg03/execution-real.txt

Interpretation:
Diese kontrollierte Fixture zeigt Locator-Drift nach realer partieller Mutation und anschliessender Re-Resolution.
Der Befund ist fixture-gebunden und kein allgemeiner Runner- oder Locator-Beweis.
