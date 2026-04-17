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

> **Zweck:** Dokumentation der semantischen Bedeutung von Manifest-Feldern.
> Das technische Schema liegt unter `schemas/experiment.manifest.schema.json`.
> Dieses Dokument ist in drei Ebenen gegliedert: aktueller Schema-Stand, ergänzende
> Arbeitssemantik für Grenzfälle, und geplante Erweiterungen.

---

## Ebene 1: Aktueller Schema-Stand

Felder, die das Schema heute tatsächlich trägt und validiert.

### iteration

```yaml
iteration:
  type: integer
  minimum: 1
```

Im Schema: Integer ohne inhaltliche Einschränkung.
Semantik ist im aktuellen Repo noch nicht vollständig formalisiert — siehe Ebene 2.

### execution_status

```yaml
execution_status:
  type: string
  enum: [designed, prepared, executed, replicated, reconstructed]
```

Im Schema: Enum mit 5 Werten. Schema-Constraints:
- `executed` und `replicated` erfordern `execution_refs` mit mindestens einem Eintrag
- `evidence_level = replicated` schließt `designed` und `prepared` aus

Operative Regel (vgl. AGENTS.md):
- Manifest-Felder müssen den tatsächlichen Ist-Zustand widerspiegeln

| Wert            | Schema-Constraint                                   |
| --------------- | --------------------------------------------------- |
| `designed`      | Keine zusätzliche Pflicht                           |
| `prepared`      | Keine zusätzliche Pflicht                           |
| `executed`      | `execution_refs` mit ≥1 nicht-leerem Eintrag        |
| `replicated`    | `execution_refs` mit ≥1 nicht-leerem Eintrag        |
| `reconstructed` | Nur für Altbestand zulässig                         |

### execution_refs

```yaml
execution_refs:
  type: array
  items:
    type: string
    minLength: 1
```

Pflicht bei `execution_status ∈ {executed, replicated}` (Schema erzwingt `minItems: 1`
auf Array-Ebene und `minLength: 1` auf Item-Ebene — mindestens ein nicht-leerer Eintrag).
Typische Inhalte: Pfade zu `evidence.jsonl`, `artifacts/<run-id>/run_meta.json`, Logs.

### evidence_level

```yaml
evidence_level:
  type: string
  enum: [anecdotal, experimental, replicated]
```

- `anecdotal`: einzelne Beobachtung
- `experimental`: kontrollierter Test
- `replicated`: unabhängig reproduziert — erfordert `replicated_from`

### adoption_basis

```yaml
adoption_basis:
  type: string
  enum: [executed, replicated, reconstructed]
```

Pflicht bei `status: adopted`. Schema erzwingt Konsistenz mit `execution_status`.
`reconstructed` nur für Altbestand mit expliziter Legacy-Begründung.

---

## Ebene 2: Ergänzende Arbeitssemantik

Lesarten, die bei Grenzfällen helfen, aber aktuell nicht schema-erzwungen sind.

### iteration — empfohlene Lesart

Im aktuellen Arbeitsgebrauch sollte `iteration` als die aktuell vorbereitete
Iterationsstufe gelesen werden. Das heißt: `iteration` kann erhöht werden, ohne dass
eine Ausführung stattgefunden hat. `iteration` allein sagt nichts über den
Ausführungszustand aus.

### execution_status — Grenzfall-Lesart

Im Grenzfall kann `execution_status` sinnvoll auf den letzten evidenztragenden Stand
bezogen gelesen werden, wenn `iteration` zwischenzeitlich erhöht wurde.
Diese Lesart ist derzeit noch nicht vollständig formalisiert.

### prepared — konzeptuelle Einordnung

`prepared` ist im Schema-Enum vorhanden, aber in `execution-bound-epistemics.md`
noch nicht vollständig operationalisiert. Das engere Kernmodell dort arbeitet mit
`designed`, `executed`, `replicated`, `reconstructed`. `prepared` sollte als
strukturelle Zwischenstufe gelesen werden: Setup angelegt, aber kein evidenzgetragener
Run vorhanden.

---

## Ebene 3: Geplante Felder

Konzeptuelle Arbeitskategorien, die noch **nicht im Schema** vorhanden sind.
Keine aktuelle Validator-Wahrheit — nur konzeptuelle Vorstufe.

### last_evidenced_iteration (geplant, Klasse B)

```yaml
# GEPLANT — nicht im aktuellen Schema
last_evidenced_iteration:
  type: integer
  minimum: 1
```

Letzte Iteration, für die gültige Ausführung und Evidenz vorliegt.
Wenn `last_evidenced_iteration < iteration`, ist der Ausführungsstand der aktuellen
Iteration nicht evidenzgetragen.
Siehe [Konzept §1](../concepts/experiment-ontology.md#1-iteration)

### execution_scope (geplant, Klasse B)

```yaml
# GEPLANT — nicht im aktuellen Schema
execution_scope:
  type: string
  # mögliche Werte: current_iteration_only | historical_execution | mixed
```

Zeitlicher Bezug der Ausführung. Kategorien sind konzeptuelle Vorschläge.
Siehe [Konzept §4](../concepts/experiment-ontology.md#4-execution-scope)

---

## Validierungsregeln

Die folgenden Regeln werden heute durch `make validate` geprüft:

| Regel                                                            | Validator                       | Schwere  |
| ---------------------------------------------------------------- | ------------------------------- | -------- |
| `execution_status ∈ {executed, replicated}` → `execution_refs` nicht leer | `validate_schema.py`           | FAIL     |
| `evidence_level = replicated` → `replicated_from` vorhanden     | `validate_schema.py`            | FAIL     |
| `status = adopted` → `adoption_basis` vorhanden                 | `validate_schema.py`            | FAIL     |
| `execution_status ∈ {executed, replicated}` → `run_meta.json` vorhanden | `validate_execution_proof.py` | FAIL     |

### Geplante Validierungsregeln (Klasse C)

Für eine spätere Einführung vorgesehen — zunächst als Warnungen, nicht als harte Fehler:

| Regel                                                                   | Schwere (geplant) |
| ----------------------------------------------------------------------- | ------------------ |
| `iteration > last_evidenced_iteration` → Hinweis                        | WARN               |
| `execution_status = executed` ohne passende `evidence.jsonl`            | FAIL               |
