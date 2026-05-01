---
title: "Agent/Skill Minimal Layer v0.1 — Methode"
status: draft
canonicality: operative
---

# method.md — Experiment-Methode

## Hypothese

> The measurement scaffold can capture comparable PR-level data for the Agent/Skill Minimal Layer without making an effect claim.

## Methode

### Ansatz

**Feldinstrumentierung** — keine Labor-Simulation, keine Kontrollgruppe in dieser Phase.

Jeder PR, der mit der Agent/Skill Minimal Layer v0.1 (experiment-critic + evidence-reconciliation-auditor) durchgeführt wird, wird als Beobachtungseinheit erfasst. Die Instrumentierung startet mit diesem Experimentgerüst; reale PR-Daten werden nachgeführt, sobald verfügbar.

### Vorgehen

1. Für jeden relevanten PR: Auditor-Output und experiment-critic-Output sichern.
2. Metriken pro PR aus den Artefakten erheben und in `results/evidence.jsonl` eintragen.
3. Nach mindestens drei vergleichbaren PRs: Zwischenauswertung in `results/result.md` aktualisieren.
4. Kein Wirkungsvotum vor Erreichen der Mindestanzahl vergleichbarer PRs.

### Metriken

| Metrik | Beschreibung |
|---|---|
| `scope_drift_count` | Anzahl Änderungen außerhalb des deklarierten Scope im PR |
| `unsupported_claim_count` | Anzahl Behauptungen ohne belegbaren Artefakt-Rückverweis |
| `missing_locator_count` | Anzahl fehlender Lokalisierungsangaben (Datei + Zielstelle) in Aufgaben |
| `validation_gap_count` | Anzahl Validierungsschritte, die ausgelassen oder nicht belegt wurden |
| `review_friction_count` | Anzahl Review-Kommentare, die auf methodische Mängel hinweisen |
| `rework_count` | Anzahl Iterationen/Korrekturen nach initialem PR-Submit |
| `false_block_count` | Anzahl Fälle, in denen Auditor oder Critic einen PR ungerechtfertigt blockiert hat |
| `task_completion_time_observed` | Beobachtete Bearbeitungsdauer (deskriptiv, kein Kausalwert) |

### Erfolgskriterien

**Erfolg:** Ein vollständiger PR-Datensatz (alle acht Metriken) kann ohne Kausalclaim erfasst werden.

**Nicht-Erfolg:**
- Auditor wird beim PR nicht tatsächlich genutzt
- Metriken bleiben uneindeutig oder widersprüchlich definiert
- Evidence fehlt oder ist nicht nachvollziehbar
- PRs sind nicht vergleichbar (unterschiedliche Aufgabentypen, unterschiedliche Modelle ohne Annotation)

## Epistemische Grenzen

- **Keine Kausalitätsbehauptung** ohne vergleichbare Kontroll-PRs.
- **Kein Verdict** vor mindestens drei vergleichbaren PRs.
- `task_completion_time_observed` ist eine deskriptive Beobachtung — keine Kausalaussage über die Wirkung der Agent-Schicht auf Bearbeitungsdauer.

## Risiken und Einschränkungen

- Kleine Stichprobe: Frühe PRs können durch Lernkurveneffekte verzerrt sein.
- Kein unabhängiger Reviewer für Metrik-Erhebung in dieser Phase.
- Auditor-Nutzung ist nicht erzwungen — fehlende Nutzung ist selbst ein Datenpunkt (false_block_count = 0 ist kein Erfolg, wenn Auditor gar nicht genutzt wurde).
