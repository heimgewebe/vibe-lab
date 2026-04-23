---
title: "Experiment-Ergebnis: Generated Artifact Contract Validation"
status: draft
canonicality: operative
triggered_by: user-request-2026-04-23-complete-result-assessment
relations:
  - type: references
    target: evidence.jsonl
  - type: references
    target: cross-run-assessment.md
  - type: references
    target: decision.yml
  - type: informs
    target: cross-run-assessment.md
---

# result.md — Experiment-Ergebnis

## Condensed Findings

- Ergebnisurteil: `result_assessment = mixed` (operatives Mapping: `partial`).
- Sechs Runs liegen mit Artefakten vor (`run-001-pr58` bis `run-006-pr67`).
- Stabile Beobachtung: strukturelle Konsolidierungsfriktion (`stale docs/_generated/system-map.md`) tritt in `run-003` bis `run-006` wiederkehrend auf.
- Stabile Beobachtung: semantische Schemafriktion (fehlender required key `context`) ist reproduzierbar injizierbar und schnell lokalisierbar (`run-004`, `run-005`).
- Clean initial run ist belegt (`run-003`), aber nicht stabil der Regelfall.

## Explicit Trade-offs

- Gewinn:
  - Fehler sind typisiert und schneller zuordbar (semantic vs structural).
  - Diagnosepfade sind klar und auditierbar.
- Kosten:
  - Wiederkehrende strukturelle Nacharbeit bei Artifact-Konsolidierung.
  - Zusätzliche Fix-Commits in mehreren Runs trotz kleiner Scopes.

## Apply vs Avoid

### Wann anwenden
- Wenn Nachvollziehbarkeit und klare Fehlerklassifikation wichtiger sind als minimale Commit-Anzahl.
- Wenn Evidence strikt schemakonform erfasst wird und canonical regeneration als fester Konsolidierungsschritt eingeplant ist.

### Wann vermeiden
- Wenn das Ziel primär "so wenig CI-/Fix-Zyklen wie möglich" ist und der Konsolidierungspfad nicht automatisiert ist.
- Wenn Runs ohne harmonisierte Messfelder direkt gegeneinander als harte Effizienzvergleiche genutzt werden sollen.

## Evidence Links

- Rohdaten: `results/evidence.jsonl`
- Run-Artefakte: `artifacts/run-001-pr58/execution.txt` bis `artifacts/run-006-pr67/execution.txt`
- Aggregation und Muster: `results/cross-run-assessment.md`
- Entscheidungsartefakt: `results/decision.yml`

## Hypothesis Status

```yaml
hypothesis_status:
  confirmed:
    - "clarifies friction"
  falsified:
    - "reduces friction (robust overall)"
  unresolved:
    - "workflow vs architecture contribution to stale-system-map"
```

## Schluss

Dieses Experiment ist auf Ergebnisebene abgeschlossen als `mixed/partial`: Klarheit steigt, Gesamtreduktion der Friktion bleibt offen.
