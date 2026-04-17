---
title: "Konzept: Iteration, Execution Scope und Reconciliation"
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
  - concept
  - iteration
  - execution
  - reconciliation
---

# Konzept: Iteration, Execution Scope und Reconciliation

> **Zweck:** Ergänzende Begriffsklärung für offene semantische Kanten im Vibe-Lab.
> Dieses Dokument präzisiert Begriffe, die im aktuellen Repo-Zustand noch nicht
> vollständig schema-formalisiert sind oder im Arbeitsgebrauch häufig zu Mehrdeutigkeiten
> führen. Es ergänzt `execution-bound-epistemics.md` und ist **kein neues Grundgesetz**.

---

## 1. Iteration

Im hier vorgeschlagenen Arbeitsverständnis bezeichnet **`iteration`** die aktuell vorbereitete
Iterationsstufe des Experiments. Das Repo modelliert diese Bedeutung derzeit noch nicht
vollständig explizit — `iteration` ist im Schema ein Integer ohne semantische Einschränkung.

Eine Iteration ist eine diskrete Stufe in der Entwicklung eines Experiments.
Sie wird im Manifest als Integer geführt und bei jeder strukturellen Weiterentwicklung erhöht.

**Wichtig:** Eine Iteration kann vorbereitet sein, ohne dass sie ausgeführt wurde.
`iteration` allein sagt nichts über den Ausführungszustand aus.

**last_evidenced_iteration** = letzte Iteration mit gültiger Ausführung und Evidenz.

> *Dieses Feld existiert aktuell nicht im Schema.* Es wird hier als konzeptuelle Arbeitskategorie
> eingeführt und soll in einem späteren Schema-Update formalisiert werden (Klasse B — erst
> dokumentieren, dann validieren).

### Zusammenhang

| Feld                        | Bedeutung (Arbeitsverständnis)                 | Schema-Status     |
| --------------------------- | ---------------------------------------------- | ----------------- |
| `iteration`                 | Aktuell vorbereitete Iteration                 | vorhanden (Integer, keine Semantik-Einschränkung) |
| `last_evidenced_iteration`  | Letzte evidenzgetragene Iteration              | geplant (Klasse B)|

---

## 2. Execution-Zustände

Der `execution_status` beschreibt den Durchführungsgrad eines Experiments.
Er ist orthogonal zu `status` (Lebenszyklus) und `evidence_level` (epistemisches Niveau).

Das aktuelle Schema kennt die folgenden Werte:

| Zustand         | Bedeutung                                                                 |
| --------------- | ------------------------------------------------------------------------- |
| `designed`      | Nur Entwurf vorhanden, keine Vorbereitung                                |
| `prepared`      | Setup angelegt (Dateien, Struktur), aber kein tatsächlicher Run           |
| `executed`      | Tatsächlicher Run mit Spur in `execution_refs`                            |
| `replicated`    | Belastbar und unabhängig wiederholt                                       |
| `reconstructed` | Historische Einstufung — nur für Altbestand zulässig (vgl. §11.1 in execution-bound-epistemics.md) |

> **Hinweis zu `prepared`:** Dieser Wert ist im Schema-Enum vorhanden, aber in
> `execution-bound-epistemics.md` noch nicht vollständig operationalisiert. Das engere
> Kernmodell dort orientiert sich an `designed`, `executed`, `replicated`, `reconstructed`.
> `prepared` sollte sinnvoll als Zwischenstufe gelesen werden, bis seine Semantik
> vollständig formalisiert ist.

---

## 3. Prepared vs Executed (wichtige Grenzfallunterscheidung)

Diese Unterscheidung ist für Reconciliation-Situationen relevant.

### prepared (konzeptuelle Arbeitskategorie)

- Experiment ist strukturell vorhanden (manifest.yml, method.md, etc.)
- **Keine Evidenz** vorhanden oder Evidenz passt nicht zur aktuellen Iteration
- `execution_refs` sollte leer sein
- `evidence.jsonl` ist leer oder nicht vorhanden
- Keine Execution-Claims zulässig

### executed

- `evidence.jsonl` vorhanden **und** inhaltlich konsistent mit dem Experiment
- Mindestens ein Eintrag in `execution_refs`
- Execution-Claims sind durch Artefakte belegt

### Grenzfall

Wenn `iteration` erhöht wurde, aber keine neue Evidenz vorliegt:
→ der dokumentierte Ausführungsstand der aktuellen Iteration muss klar von
evidenzgetragenem Stand früherer Iterationen getrennt sein.

---

## 4. Execution Scope

Der Execution Scope beschreibt, auf welchen Zeitraum sich die Ausführung eines Experiments bezieht.
Dies ist eine **konzeptuelle Arbeitskategorie** — kein aktuelles Schema-Feld.

| Scope                      | Bedeutung                                                         |
| -------------------------- | ----------------------------------------------------------------- |
| `current_iteration_only`   | Evidenz bezieht sich ausschließlich auf die aktuelle Iteration    |
| `historical_execution`     | Evidenz stammt aus früheren Iterationen                           |
| `mixed`                    | Evidenz aus verschiedenen Iterationen vorhanden                   |

> *Dieses Feld existiert aktuell nicht im Schema.* Es wird hier als konzeptuelle
> Arbeitskategorie eingeführt und soll bei Bedarf in einem späteren Schema-Update
> formalisiert werden (Klasse B).

Die oben genannten Werte sind als sinnvolle Kategorisierung gedacht; sie sind noch keine
schema-erzwungene Einschränkung.

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

Pull Requests im Experiment-Kontext lassen sich in drei operative Kategorien einteilen:

| PR-Typ                        | Zweck                                                  | Evidenz-Erwartung          |
| ----------------------------- | ------------------------------------------------------ | -------------------------- |
| `experiment_run`              | Neue Ausführung oder Iteration eines Experiments       | Neue `evidence.jsonl`-Einträge erwartet |
| `experiment_review`           | Redaktionelle, analytische oder strukturierende Änderungen ohne neue Ausführung | Keine neue Evidenz erforderlich |
| `experiment_reconciliation`   | Reparatur inkonsistenter Zustände                      | Keine neue Evidenz; bestehende darf nicht entfernt werden |

### Regeln

- Ein PR sollte nur **einen** Typ haben
- Der Typ wird im PR-Template deklariert
- Bei `experiment_reconciliation` gelten die Reconciliation-Regeln (siehe Abschnitt 5)

---

## 7. Epistemische Ableitungsebenen

Das Repository unterscheidet drei Schichten epistemischer Information:

| Schicht | Was | Quelle | Beispiel |
| ------- | --- | ------ | -------- |
| **Daten (Evidence)** | Beobachtungen und Messungen | `evidence.jsonl` | `{"event_type":"observation", "metric":"rework_lines", "value":"23"}` |
| **Bewertung (Interpretation Risk)** | Wo sollte das Repo seinen Claims misstrauen? | Abgeleitet in `epistemic-state.md` | `low` / `medium` / `high` / `unknown` |
| **Zustand (Reconciliation)** | Ist das Experiment intern konsistent? | Abgeleitet in `epistemic-state.md` | `none` / `active` / `inferred` |

### Interpretation Risk

Interpretation Risk wird *heuristisch abgeleitet* — nicht manuell gesetzt. Die Ableitung
kombiniert mehrere bereits im Repo vorhandene epistemische Signale:

- **Evidence Sufficiency** — Existenz und Dichte von `evidence.jsonl`
- **Execution Quality** — `execution_status` (`reconstructed` ist epistemisch schwächer
  als `executed`/`replicated`)
- **Evidence Level** — `evidence_level` (`anecdotal` erhöht Risiko)
- **Adoption Basis** — bei `adopted`: `adoption_basis: reconstructed` erhöht Risiko
- **Interpretation Budget** — bei `adopted`: Fehlen des Budget-Blocks in `result.md`
  erhöht Risiko

Die Stufen (`low`, `medium`, `high`, `unknown`) sind im
[Epistemic State Report](../_generated/epistemic-state.md) dokumentiert.

**Wichtig:** Interpretation Risk ist *indikativ* — es zeigt, wo genauer hingeschaut
werden sollte, nicht wo ein Fehler *ist*. Die Heuristik kann falsch-positive und
falsch-negative Ergebnisse produzieren.

### Unterschied zu Interpretation Budget

- **Interpretation Budget** (→ `result.md`) ist ein *manuell verfasstes* Feld:
  es dokumentiert, welche Claims erlaubt sind und welche nicht.
  Es ist claim-/deutungsnah.
- **Interpretation Risk** ist ein *abgeleitetes* Feld:
  es bewertet, wo strukturelle Schwächen auf epistemische Vorsicht hindeuten.
  Es ist status-/artefaktnah.

Beide sind komplementär: Budget setzt Grenzen, Risk zeigt Schwächen.
Ein Experiment kann ein sauberes Budget haben und trotzdem `medium` Risk tragen
(z.B. weil `reconstructed`). Umgekehrt kann ein Experiment ohne Budget `low` Risk
haben, wenn es nicht `adopted` ist — dort greift das Budget-Signal nicht.

### Mögliche zukünftige Trennung

Die aktuelle Heuristik kombiniert daten-/artefaktnahe Signale (Evidence Sufficiency)
mit status-/claimnahen Signalen (Execution Quality, Adoption Basis) in einem
einzigen Feld. Eine spätere Trennung in zwei Felder (z.B. *Evidence Sufficiency* +
*Interpretation Risk*) ist als Designoption dokumentiert, aber nicht Teil des
aktuellen Standes.

---

## 8. Offene epistemische Frage

> Soll `iteration` ein Planungsobjekt oder ein Messobjekt sein?

Diese Frage ist bewusst offen gelassen. Sie entscheidet darüber, ob `iteration`
langfristig im Schema verbleibt oder durch rein evidenzbasierte Zählung ersetzt wird.

Das Arbeitsverständnis dieses Dokuments (Planungsobjekt) ist eine sinnvolle Auflösung
der Ambiguität, aber keine bereits repo-kanonisierte Entscheidung.
