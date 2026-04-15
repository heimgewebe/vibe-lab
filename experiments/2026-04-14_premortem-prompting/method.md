---
title: "Methode: Pre-Mortem Prompting"
status: testing
canonicality: operative
---

# method.md — Experiment-Methode

## Hypothese

Ein vorgeschalteter Pre-Mortem-Schritt reduziert Rework und verbessert die Vollständigkeit gegenüber direkter Implementierung ohne Voranalyse.

## Zusatzhypothese (Mechanismus)

Pre-Mortem wirkt primär als **Bias-Shaper des Suchraums**: antizipierbare Fehlpfade werden früher adressiert, unbekannte Fehlklassen jedoch nur begrenzt.

## Run-Typen

1. Holdout-Paarlauf (`run-007/008`)
2. Failure-Injection-Paarlauf (`run-009/010`)
3. Failure-Learning-Loop (`run-011/012`)
4. Cross-Session-Replikation + Exotic Injection (`run-013/014`)
5. Extended-Pre-Mortem-Run (`run-015`) für micro_price/range bounds

## Metriken (operationalisiert)

- `test_pass_rate`
- `edge_case_failures`
- `discovery_failures_unknown`
- `learning_gain`
- `replication_consistency`
- `time_to_first_pass_seconds`
- `economics_ratio_steps_per_gain`
- `exotic_blindspot_count`

## Erfolgskriterien

Vorläufige Unterstützung nur, wenn:
- Failure-Learning reproduzierbar bleibt,
- Unknowns durch Injection sichtbar und dann reduzierbar werden,
- und Ökonomie bei steigender Komplexität tragfähig bleibt.

## Risiken und Einschränkungen

- N bleibt klein.
- Eine Challenge-Familie dominiert.
- Noch kein Adoption-Signal.
