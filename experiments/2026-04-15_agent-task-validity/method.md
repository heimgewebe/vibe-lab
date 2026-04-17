---
title: "Methodik: Agent Task Validity Experiment"
status: draft
canonicality: operative
---

# Ziel

Untersuchen, ob ein explizites Task-Protokoll die Qualität von agent-generierten Änderungen verbessert.

## Kritische Vorbedingung (neu)

Vor dem eigentlichen Control-vs-Treatment-Vergleich wird **M0 (Task Validity)** gemessen:

- **Definition M0:** `ausführbare Tasks / Gesamt-Tasks`
- Ein Task ist nur ausführbar, wenn er mindestens enthält:
  - Ziel-Datei(en)
  - Zielstelle (`target_lines` / Locator)
  - Änderungsart (`change_type`)

Ohne ausreichend hohes M0 ist die Kernhypothese **nicht testbar**.
Iteration 2 validiert nur Testbarkeit und Aufgabenqualität, nicht die Kernhypothese selbst.


## Task-Sets nach Iteration

- `tasks.jsonl`: dokumentiert das für Iteration 2 operationalisierte Set (M0-Gate-Nachweis).
- `tasks.iteration3.jsonl`: frisches Vergleichs-Set für den echten Control-vs-Treatment-Run in Iteration 3.
- `tasks.iteration4.jsonl`: erweitertes Set für Iteration 4 mit höherer Komplexität (Logic-Level-Edits).

## Versuchsaufbau

Zwei Gruppen:

- **Kontrollgruppe:** normale Agentenarbeit
- **Treatment-Gruppe:** Agent nutzt Task-Protokoll vor jeder Änderung

## Task-Auswahl

- 6–10 reale Tasks aus dem Repo
- Typen:
  - Refactoring
  - Dead-Code Removal
  - Dokumentationsfixes
  - Schema-/CI-Anpassungen

**Wichtig:** Tasks dürfen nicht vereinfacht, nachträglich angepasst oder umdefiniert werden.

## Ablauf

0. Task-Operationalisierung prüfen (M0)
1. Tasks definieren (identisch für beide Gruppen)
2. Randomisierte Zuordnung zu Gruppen
3. Durchführung durch Agent
4. PR erstellen
5. Blind-Review durchführen
6. Metriken erfassen

## Task-Protokoll (nur Treatment)

Vor jeder Änderung muss der Agent deklarieren:

- Ziel
- Scope (Dateien + Muster)
- Was als Nutzung zählt
- Was nicht zählt
- Erwartete Änderungen
- Verbotene Änderungen
- Bedarf externer Informationen

## Messung

### M0 — Task Validity
Anteil ausführbarer, operationalisierter Tasks.

### Scope Drift
Änderungen außerhalb der erwarteten Änderungen.

### Independent Changes
Änderungen, die als eigene PR gelten würden.

### Review Friction
Anzahl Rückfragen/Missverständnisse im Review.

### Rework
Zusätzliche Commits nach Review.

### Abort Rate
Wie oft der Agent wegen Stop-Regeln abbricht.

### Execution Time
Bearbeitungszeit pro Task in Minuten.

## Erfolgskriterien

- **Gate:** M0 muss ausreichend hoch sein (praktisch: alle Tasks operationalisiert)
- Scope Drift in Treatment **≥ 30% niedriger** als in der Kontrollgruppe
- Weniger unabhängige Änderungen pro PR
- Weniger Review-Rückfragen
- Kein signifikanter Anstieg der Bearbeitungszeit (>25%)

## Entscheidungslogik

- **Adopted:** klare Verbesserung bei Scope Drift und Review-Reibung
- **Rejected:** kein Unterschied oder schlechter
- **Inconclusive:** gemischte Ergebnisse / unzureichende Datengrundlage

## Variablen

| Variable | Beschreibung | Kontrolle / Treatment |
| --- | --- | --- |
| task_validity | Operationalisierungsgrad der Tasks (M0) | identisch |
| prompt_mode | Arbeitsmodus des Agenten | normal / protocol |
| task_set | Aufgabenpool | identisch |
| reviewer_blinding | Reviewer kennt Gruppenzugehörigkeit nicht | aktiv |
| constraints | Task-Änderungsverbot & Stop-Regeln | nur Treatment explizit |

## Risiken und Einschränkungen

- Overhead durch Protokollierung kann Durchlaufzeit erhöhen
- Strikte Stop-Regeln können Abbruchrate erhöhen
- Reviewer-Varianz kann Friction-Metrik beeinflussen
- Niedriges M0 macht die Kernhypothese untestbar

## Iteration 4 — Erweitertes Design

### Änderungen gegenüber Iteration 3

1. **Task-Komplexität ↑**: Logic-Level-Edits in Python-Validierungsskripten und CI-Workflow
   statt atomarer Text-Replacements. Jeder Task hat mehrere plausible Umsetzungspfade,
   sodass Drift erstmals realistisch möglich wird.

2. **Externes Blind-Review (verpflichtend, ausstehend)**: Reviewer ist nicht der Executor.
   Reviewer kennt weder Control/Treatment-Zugehörigkeit noch Task-Protokoll-Existenz.
   Erfasst: review_comments, qualitative Friction, geforderte Änderungen.

3. **Replikation (verpflichtend, ausstehend)**: Mindestens ein zweiter Run mit anderem
   Executor oder anderer Session. Getrennte Artefakte.

### Task-Komplexitätskriterien

Geeignet:
- Validator-Edgecases (Typprüfung, Leerstring-Guards)
- CI-Workflow-Korrekturen mit Nebenbedingungen
- Variable-Shadowing-Fixes mit Downstream-Auswirkung
- Defensive Checks mit Entscheidungen über Fehlerbehandlung

Nicht geeignet:
- Reine Wortlautänderungen
- Kosmetische Änderungen
- Trivial deterministische Edits (1:1 String-Swap)

### Stop-Kriterien (hart)

PR darf nicht gemerged werden, wenn:
- kein externes Blind-Review durchgeführt wurde
- keine Replikation vorhanden ist
- Tasks wieder trivial sind
- Evidence nicht zwischen Control/Treatment trennt
- Iteration 3 und 4 nicht klar separiert sind
