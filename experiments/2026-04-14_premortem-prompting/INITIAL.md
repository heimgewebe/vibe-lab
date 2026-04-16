---
title: "Initial: Pre-Mortem Prompting"
status: testing
canonicality: operative
document_role: experiment
---

# INITIAL.md — Initiale Situation

## Initialer Prompt / Setup

Kontrollbedingung (ohne Pre-Mortem):

```text
Implementiere die angeforderte Funktionalität für die Challenge direkt. 
Arbeite iterativ und liefere lauffähigen Code mit Tests.
```

Treatment-Bedingung (mit Pre-Mortem):

```text
Bevor du implementierst, erstelle ein Pre-Mortem mit 5 wahrscheinlichen Failure Modes
(inkl. Trigger, Symptom, Mitigation). Leite daraus eine kurze Implementierungs-Checkliste ab.
Implementiere dann die Funktionalität und referenziere die Checkliste explizit.
```

## Systemkonfiguration

- Gleiches Modell, gleicher Task, gleiche Zeitbox pro Run.
- Gleiche Ausgangs-Repository-Struktur.
- Keine zusätzlichen Plugins zwischen Kontrolle und Treatment.

## Erwartete Baseline

Ohne Pre-Mortem wird vermutlich schneller mit Code gestartet, aber mit höherem Risiko für nachträgliche Fixes bei Randfällen und Fehlerpfaden.
