---
title: "Konzept: Experiment-Ontologie"
status: active
canonicality: operative
relations:
  - type: references
    target: execution-bound-epistemics.md
  - type: informs
    target: ../../experiments/README.md
  - type: informs
    target: ../playbooks/reconciliation.md
  - type: informs
    target: ../reference/manifest-schema.md
schema_version: "0.1.0"
created: "2026-04-17"
updated: "2026-04-17"
author: "heimgewebe"
tags:
  - ontology
  - iteration
  - execution
  - reconciliation
---

# Konzept: Experiment-Ontologie

> **Zweck:** Kanonische Begriffsebene für Experimente im Vibe-Lab.
> Dieses Dokument definiert die verbindlichen Begriffe, Zustände und Unterscheidungen,
> die für die Arbeit mit Experimenten gelten. Es ist die Referenz für Agenten, Reviewer
> und Autoren gleichermaßen.

---

## 1. Iteration

**iteration** = aktuell vorbereitete Iteration des Experiments.

Eine Iteration ist eine diskrete Stufe in der Entwicklung eines Experiments.
Sie wird im Manifest als Integer geführt und bei jeder strukturellen Weiterentwicklung erhöht.

**Wichtig:** Eine Iteration kann vorbereitet sein, ohne dass sie ausgeführt wurde.
`iteration` allein sagt nichts über den Ausführungszustand aus.

**last_evidenced_iteration** = letzte Iteration mit gültiger Ausführung und Evidenz.

> *Dieses Feld existiert aktuell nicht im Schema.* Es wird hier als Konzept definiert
> und soll in einem späteren Schema-Update formalisiert werden (Klasse B — erst
> dokumentieren, dann validieren).

### Zusammenhang

| Feld                        | Bedeutung                                      | Schema-Status     |
| --------------------------- | ---------------------------------------------- | ----------------- |
| `iteration`                 | Aktuell vorbereitete Iteration                 | vorhanden         |
| `last_evidenced_iteration`  | Letzte evidenzgetragene Iteration              | geplant (Klasse B)|

---

## 2. Execution-Zustände

Der `execution_status` beschreibt den Durchführungsgrad eines Experiments.
Er ist orthogonal zu `status` (Lebenszyklus) und `evidence_level` (epistemisches Niveau).

| Zustand         | Bedeutung                                                                 |
| --------------- | ------------------------------------------------------------------------- |
| `designed`      | Nur Entwurf vorhanden, keine Vorbereitung                                |
| `prepared`      | Setup angelegt (Dateien, Struktur), aber kein tatsächlicher Run           |
| `executed`      | Tatsächlicher Run mit Spur in `execution_refs`                            |
| `replicated`    | Belastbar und unabhängig wiederholt                                       |
| `reconstructed` | Historische Einstufung — nur für Altbestand zulässig (vgl. §11.1 in execution-bound-epistemics.md) |

---

## 3. Prepared vs Executed (kritische Unterscheidung)

Diese Unterscheidung ist zentral für die epistemische Integrität des Repos.

### prepared

- Experiment ist strukturell vorhanden (manifest.yml, method.md, etc.)
- **Keine Evidenz** vorhanden
- `execution_refs` sollte leer sein
- `evidence.jsonl` ist leer oder nicht vorhanden
- Keine Execution-Claims zulässig

### executed

- `evidence.jsonl` vorhanden **und** inhaltlich konsistent mit dem Experiment
- Mindestens ein Eintrag in `execution_refs`
- Execution-Claims sind durch Artefakte belegt

### Grenzfall

Wenn `iteration` erhöht wurde, aber keine neue Evidenz vorliegt:
→ die aktuelle Iteration ist `prepared`, auch wenn frühere Iterationen `executed` waren.

---

## 4. Execution Scope

Der Execution Scope beschreibt, auf welchen Zeitraum sich die Ausführung eines Experiments bezieht.

| Scope                      | Bedeutung                                                         |
| -------------------------- | ----------------------------------------------------------------- |
| `current_iteration_only`   | Evidenz bezieht sich ausschließlich auf die aktuelle Iteration    |
| `historical_execution`     | Evidenz stammt aus früheren Iterationen                           |
| `mixed`                    | Evidenz aus verschiedenen Iterationen vorhanden                   |

> *Dieses Feld existiert aktuell nicht im Schema.* Es wird hier als Konzept definiert
> und soll bei Bedarf in einem späteren Schema-Update formalisiert werden (Klasse B).

**Regel:** Keine Freitext-Interpretation des Execution Scope. Nur die oben definierten
Werte sind zulässig.

---

## 5. Reconciliation

> **Definition:** Epistemischer Reparaturmodus eines Experiments ohne neue Ausführung.

Reconciliation ist der Prozess, in dem ein inkonsistentes Experiment
wieder in einen kohärenten Zustand gebracht wird — **ohne dass eine neue
Ausführung stattfindet**.

### Wann ist Reconciliation nötig?

- `iteration` wurde erhöht, ohne dass eine neue Ausführung stattfand
- `evidence.jsonl` widerspricht dem Manifest
- `decision.yml` basiert auf einer veralteten Iteration
- Manifest-Felder spiegeln nicht den tatsächlichen Ist-Zustand wider

### Was ist Reconciliation NICHT?

- Keine neue Ausführung
- Keine Verbesserung von Ergebnissen
- Keine nachträgliche Aufwertung epistemischen Status

### Ziel

Konsistenz wiederherstellen — nicht Ergebnisse verbessern.

→ Siehe [Playbook: Reconciliation](../playbooks/reconciliation.md) für operative Anleitung.

---

## 6. PR-Typen

Pull Requests im Experiment-Kontext fallen in drei Kategorien:

| PR-Typ                        | Zweck                                                  | Evidenz-Erwartung          |
| ----------------------------- | ------------------------------------------------------ | -------------------------- |
| `experiment_run`              | Neue Ausführung oder Iteration eines Experiments       | Neue `evidence.jsonl`-Einträge erwartet |
| `experiment_review`           | Review, Korrektur oder Ergänzung ohne neue Ausführung  | Keine neue Evidenz nötig   |
| `experiment_reconciliation`   | Reparatur inkonsistenter Zustände                      | Keine neue Evidenz; bestehende darf nicht entfernt werden |

### Regeln

- Ein PR darf nur **einen** Typ haben
- Der Typ wird im PR-Template deklariert
- Bei `experiment_reconciliation` gelten die Reconciliation-Regeln (siehe Abschnitt 5)

---

## 7. Offene epistemische Frage

> Soll `iteration` ein Planungsobjekt oder ein Messobjekt sein?

Diese Frage ist bewusst offen gelassen. Sie entscheidet darüber, ob `iteration`
langfristig im Schema verbleibt oder durch rein evidenzbasierte Zählung ersetzt wird.

**Aktueller Konsens:** `iteration` bleibt als Planungsobjekt im Schema, wird aber
durch die konzeptuelle Unterscheidung zu `last_evidenced_iteration` epistemisch entschärft.
