---
title: "Referenz: Manifest-Schema-Semantik"
status: active
canonicality: operative
relations:
  - type: references
    target: ../../schemas/experiment.manifest.schema.json
  - type: informed_by
    target: ../concepts/experiment-ontology.md
schema_version: "0.1.0"
created: "2026-04-17"
updated: "2026-04-17"
author: "heimgewebe"
tags:
  - reference
  - manifest
  - schema
---

# Referenz: Manifest-Schema-Semantik

> **Zweck:** Dokumentation der semantischen Bedeutung von Manifest-Feldern,
> die über die reine Schema-Validierung hinausgeht.
> Das technische Schema liegt unter `schemas/experiment.manifest.schema.json`.
> Dieses Dokument beschreibt die **Bedeutung** und **Verwendungsregeln** der Felder.

---

## Kernfelder

### iteration

```yaml
iteration:
  type: integer
  minimum: 1
```

**Semantik:** Aktuell vorbereitete Iteration des Experiments.

- Wird bei jeder strukturellen Weiterentwicklung erhöht
- Sagt **nichts** über den Ausführungszustand aus
- Eine Iteration kann `prepared` sein, ohne je ausgeführt worden zu sein
- Siehe [Experiment-Ontologie §1](../concepts/experiment-ontology.md#1-iteration)

### execution_status

```yaml
execution_status:
  type: string
  enum: [designed, prepared, executed, replicated, reconstructed]
```

**Semantik:** Durchführungsgrad der letzten evidenztragenden Iteration.

- Orthogonal zu `status` (Lebenszyklus) und `evidence_level` (epistemisches Niveau)
- `executed` und `replicated` erfordern `execution_refs` mit mindestens einem Eintrag
- `reconstructed` ist nur für Altbestand zulässig
- Muss den **tatsächlichen Ist-Zustand** widerspiegeln (vgl. AGENTS.md)

| Wert            | Voraussetzung                                       |
| --------------- | --------------------------------------------------- |
| `designed`      | Nur Entwurf vorhanden                               |
| `prepared`      | Setup angelegt, aber kein tatsächlicher Run          |
| `executed`      | Run mit Spur in `execution_refs`                    |
| `replicated`    | Unabhängig wiederholt, belastbar                    |
| `reconstructed` | Historisch — nur für Altbestand                     |

### execution_refs

```yaml
execution_refs:
  type: array
  items:
    type: string
    minLength: 1
```

**Semantik:** Spurverweise auf Ausführungsartefakte.

- Pflicht bei `execution_status ∈ {executed, replicated}` (Schema erzwingt `minItems: 1` auf Array-Ebene und `minLength: 1` auf Item-Ebene — d.h. mindestens ein nicht-leerer Eintrag)
- Typische Einträge: Pfade zu `evidence.jsonl`, `artifacts/<run-id>/run_meta.json`, Logs
- Sollte bei `designed` oder `prepared` leer bleiben

### evidence_level

```yaml
evidence_level:
  type: string
  enum: [anecdotal, experimental, replicated]
```

**Semantik:** Epistemisches Niveau der vorliegenden Evidenz.

- `anecdotal`: einzelne Beobachtung
- `experimental`: kontrollierter Test
- `replicated`: unabhängig reproduziert (erfordert `replicated_from`)

### adoption_basis

```yaml
adoption_basis:
  type: string
  enum: [executed, replicated, reconstructed]
```

**Semantik:** Execution-Grundlage, auf der eine Adoption fußt.

- Pflicht bei `status: adopted`
- Muss konsistent mit `execution_status` sein (Schema erzwingt Gleichheit)
- `reconstructed` nur für Altbestand mit expliziter Legacy-Begründung

---

## Geplante Felder (Klasse B — erst dokumentieren, dann validieren)

Die folgenden Felder sind konzeptuell definiert, aber noch nicht im Schema formalisiert.

### last_evidenced_iteration (geplant)

```yaml
last_evidenced_iteration:
  type: integer
  minimum: 1
```

**Semantik:** Letzte Iteration, für die gültige Ausführung und Evidenz vorliegt.

- Darf nie größer als `iteration` sein
- Wenn `last_evidenced_iteration < iteration`, ist die aktuelle Iteration `prepared`
- Siehe [Experiment-Ontologie §1](../concepts/experiment-ontology.md#1-iteration)

### execution_scope (geplant)

```yaml
execution_scope:
  type: string
  enum: [current_iteration_only, historical_execution, mixed]
```

**Semantik:** Zeitlicher Bezug der Ausführung.

- `current_iteration_only`: Evidenz bezieht sich auf die aktuelle Iteration
- `historical_execution`: Evidenz stammt aus früheren Iterationen
- `mixed`: Evidenz aus verschiedenen Iterationen
- Siehe [Experiment-Ontologie §4](../concepts/experiment-ontology.md#4-execution-scope)

---

## Validierungsregeln

Die folgenden Regeln werden durch `make validate` geprüft:

| Regel                                                            | Validator                       | Schwere  |
| ---------------------------------------------------------------- | ------------------------------- | -------- |
| `execution_status ∈ {executed, replicated}` → `execution_refs` nicht leer | `validate_schema.py`           | FAIL     |
| `evidence_level = replicated` → `replicated_from` vorhanden     | `validate_schema.py`            | FAIL     |
| `status = adopted` → `adoption_basis` vorhanden                 | `validate_schema.py`            | FAIL     |
| `execution_status ∈ {executed, replicated}` → `run_meta.json` vorhanden | `validate_execution_proof.py` | FAIL     |

### Geplante Validierungsregeln (Klasse C — Vorbereitung)

Die folgenden Regeln sind für eine spätere Einführung vorgesehen.
Sie sollen zunächst als Warnungen, nicht als harte Fehler implementiert werden:

| Regel                                                                   | Schwere (geplant) |
| ----------------------------------------------------------------------- | ------------------ |
| `iteration > last_evidenced_iteration` → Warnung                        | WARN               |
| `execution_status = executed` ohne passende `evidence.jsonl`            | FAIL               |
| `experiment_reconciliation` PR mit neuer Execution                      | FAIL               |
