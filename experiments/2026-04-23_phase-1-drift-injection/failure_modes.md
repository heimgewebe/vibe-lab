---
title: "Failure Modes: Phase 1 Drift Injection"
status: draft
canonicality: operative
created: "2026-04-23"
updated: "2026-04-24"
author: "GPT-5.3-Codex"
relations:
  - type: references
    target: ../../schemas/agent.handoff.schema.json
---

# Phase 1 Failure Modes

> Status: Design-Stand. Fokus nur auf Risiken, die Phase 1 direkt betreffen.

## Kernrisiken

### 1) Alibi-Fixtures statt Klassenabdeckung

Risiko:
- Ein einzelner Driftfall wird als "abgedeckt" behandelt.

Gegenmaßnahme:
- Kontrastpaar-Regel erzwingen (negativer Fall + naher Gegenfall).

### 2) Overhardening nach Einzelbefund

Risiko:
- Ein Grenzfall führt sofort zu zu strikten Validator-Regeln.

Gegenmaßnahme:
- Patch nur bei belegter Lücke,
- Patch-Entwurf bleibt separat reviewpflichtig,
- keine automatische Übernahme in Phase 1.

### 3) Scope Creep während Ausführung

Risiko:
- Zusätzliche Ideen werden während Phase 1 eingeschoben.

Gegenmaßnahme:
- Phase 1 bleibt bei den 6 definierten Fällen,
- neue Ideen als Backlog für spätere Phasen markieren.

### 4) Null-Ergebnis falsch gedeutet

Risiko:
- "Keine Lücke gefunden" wird als "Validator vollständig robust" interpretiert.

Gegenmaßnahme:
- Ergebnis auf Scope begrenzen: nur Driftklasse von Phase 1 bewertet.

### 5) designed/executed-Verwischung

Risiko:
- Designartefakte werden wie Ausführungsartefakte gelesen.

Gegenmaßnahme:
- Laufbefunde erst im Execution-PR in `results/evidence.jsonl` dokumentieren,
- bis dahin keine Ausführungsclaims in Tatsachenform.

## Out Of Scope Für Phase 1

- Cross-Contract-Validierung,
- Command-Chain-Sequenzen,
- semantische Qualitätsbewertung.

## Minimaler Entscheidungsrahmen

- **success:** 6/6 Fälle ausgeführt, evidence vollständig, kein unbelegter Drift.
- **patch_needed:** belegte Lücke + separater Patchvorschlag mit Kontrastpaar.
- **inconclusive:** unklare oder unvollständige Befundlage.
