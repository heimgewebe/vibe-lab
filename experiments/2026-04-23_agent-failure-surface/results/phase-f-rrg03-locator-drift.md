# Phase F — RRG-03 Locator Drift (Real Execution Evidence)

Status: real-execution-evidence

## Ziel

RRG-03 unter kontrollierten Bedingungen real pruefen: partielle Mutation anwenden und denselben Locator danach erneut aufloesen.

## Scope und Grenzen

- Keine Runtime-, Schema-, Validator- oder CI-Aenderung in diesem Evidence-PR.
- Kein Runner-Patch.
- Kein Schema-Patch.
- Kein Validator-Patch.
- Kein CI-Gate.

## Proof Status

- Proof status: PROVEN_FOR_FIXTURE
- Patch-Gate: TRIGGERED

## Fixtures

Siehe:

- artifacts/run-phase-f-rrg03/fixtures/before.md
- artifacts/run-phase-f-rrg03/fixtures/step-a.json
- artifacts/run-phase-f-rrg03/fixtures/step-b.json
- artifacts/run-phase-f-rrg03/fixtures/expected.json

## Befund

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
