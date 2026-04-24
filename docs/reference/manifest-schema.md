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
updated: "2026-04-24"
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

### falsifiability (Phase-1 Dry-Run Gate)

```yaml
falsifiability:
  type: object
  properties:
    counter_hypothesis: { type: string, minLength: 10 }
    falsification_criterion: { type: string, minLength: 10 }
    counterevidence_checked: { type: boolean }
  required: [counter_hypothesis, falsification_criterion, counterevidence_checked]
  additionalProperties: false
```

Im Schema **optional** und strukturell definiert: wenn der Block vorhanden ist,
müssen alle drei Felder gesetzt sein. Die **konditionale Pflicht** ist bewusst
*nicht* im JSON-Schema kodiert, sondern in der Dry-Run-Diagnose
`scripts/docmeta/validate_promotion_readiness.py`:

| Experimentzustand                                              | Falsifiability-Pflicht |
| -------------------------------------------------------------- | ---------------------- |
| `execution_status ∈ {executed, replicated}`                    | getriggert             |
| `status=adopted` **und** `adoption_basis ∈ {executed, replicated}` | getriggert         |
| `status=adopted` **und** `adoption_basis=reconstructed`        | **nicht** getriggert (historical escape) |
| `execution_status ∈ {designed, prepared}`                      | nicht getriggert       |

**Leitregel:** *Bestätigung verteuern, nicht Wahrheit quantifizieren.* Der Block
zwingt dazu, eine Gegenhypothese und ein Falsifikationskriterium explizit
auszuformulieren — nicht dazu, eine Zahl für „Wahrheit“ zu erfinden.

**Phasen-Rollout** (siehe `docs/blueprints/blueprint-v2-roadmap.md`):

- **Phase 1 (dieser PR):** Dry-Run. Report unter
  `docs/_generated/promotion-readiness.json`, `make validate` bleibt grün,
  CI-Step `continue-on-error: true`.
- **Phase 2 (separat):** Hard-Fail für *neue* Experimente via freeze-list
  (Stichtags-Mechanismus, noch zu designen).
- **Phase 3 (optional):** globaler Hard-Fail.

**Explizit nicht aktiviert:** `docs/concepts/execution-bound-epistemics.md` bleibt
dormant; dieser PR referenziert es nur. Kein `truth_confidence`-Score. Kein
Auto-Move `experiments/* → catalog/*`.

### Gekoppelte Decision-Felder (result_assessment)

Zwei neue Felder in `decision.yml` (für `decision_type=result_assessment`):

| Feld                           | Typ       | Kopplungsregel                                                                 |
| ------------------------------ | --------- | ------------------------------------------------------------------------------ |
| `counterevidence_checked`      | boolean   | Wenn `false` **und** `verdict=confirms` → harter Schema-Validator-Fehler.      |
| `counter_hypothesis_outcome`   | enum      | Wenn `found_and_confirming` **und** `verdict=confirms` → harter Fehler.        |

Die Regeln werden in `scripts/docmeta/validate_schema.py` in
`validate_decision_files()` geprüft. Sie greifen nur, wenn die Felder explizit
gesetzt sind — kein allgemeiner Zwang zu `counterevidence_checked=true`.
Entscheidungen, die die Felder weglassen, bleiben gültig; der neue Promotion-
Readiness-Report markiert sie lediglich als „nicht abgedeckt“.

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
