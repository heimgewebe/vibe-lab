---
title: "Playbook: Reconciliation"
status: active
canonicality: operative
relations:
  - type: informed_by
    target: ../concepts/experiment-ontology.md
  - type: references
    target: ../concepts/execution-bound-epistemics.md
schema_version: "0.1.0"
created: "2026-04-17"
updated: "2026-04-17"
author: "heimgewebe"
tags:
  - playbook
  - reconciliation
  - epistemics
---

# Playbook: Reconciliation

> **Zweck:** Operativer Umgang mit inkonsistenten Experimenten.
> Reconciliation ist der Prozess, in dem ein Experiment ohne neue Ausführung
> wieder in einen konsistenten Zustand gebracht wird.

---

## Wann ist Reconciliation nötig?

Ein Experiment braucht Reconciliation, wenn mindestens eine der folgenden
Bedingungen zutrifft:

- **Iteration ohne Execution:** `iteration` wurde erhöht, ohne dass eine neue
  Ausführung stattfand — der dokumentierte Ausführungsstand deckt die aktuelle
  Iteration nicht ab
- **Evidenz-Manifest-Widerspruch:** `evidence.jsonl` widerspricht den Claims
  im `manifest.yml` (z.B. `execution_status: executed` ohne passende Evidenz)
- **Veraltete Decision:** `decision.yml` basiert auf einer Iteration, die nicht
  mehr dem aktuellen Stand entspricht
- **Status-Drift:** Manifest-Felder spiegeln nicht den tatsächlichen Ist-Zustand
  wider (vgl. AGENTS.md: „Manifest-Felder spiegeln Ist-Zustand“)

---

## Was darf geändert werden?

| Artefakt           | Änderung erlaubt? | Einschränkung                                         |
| ------------------ | ----------------- | ----------------------------------------------------- |
| `manifest.yml`     | ✅ Ja             | Muss Ist-Zustand widerspiegeln                        |
| `decision.yml`     | ✅ Ja             | Nur Korrektur, keine nachträgliche Aufwertung         |
| `result.md`        | ✅ Ja             | Nur Korrektur, keine neuen Claims ohne Evidenz        |
| `evidence.jsonl`   | ⚠️ Nur ergänzen   | Bestehende Einträge dürfen **nicht** entfernt oder verändert werden. Ergänzungen müssen als solche erkennbar sein. |
| `method.md`        | ✅ Ja             | Korrekturen und Präzisierungen erlaubt                |
| `CONTEXT.md`       | ✅ Ja             | Nur redaktionelle Korrekturen                         |

---

## Was darf NICHT passieren?

Diese Regeln sind **harte Constraints** — keine Empfehlungen:

1. **Keine neuen Execution-Claims ohne Evidenz.**
   `execution_status` darf nicht auf `executed` gesetzt werden,
   wenn keine passenden Einträge in `evidence.jsonl` vorliegen.

2. **Keine Evidenz still löschen oder umschreiben.**
   Bestehende Einträge in `evidence.jsonl` sollen nicht entfernt oder verändert werden.
   Korrekturen werden durch ergänzende Einträge oder eine dokumentierte Reconciliation-Spur
   sichtbar gemacht. Falls das Repo künftig explizite Korrekturmarkierungen in JSONL
   einführt, gilt diese Regel entsprechend.

3. **Keine Iteration „nachziehen" ohne Klarstellung.**
   Wenn `iteration` erhöht wird, darf daraus kein unbelegter Execution-Claim entstehen.
   Der dokumentierte Zustand muss klar machen, dass die neue Iteration nicht
   evidenzgetragen ist.

4. **Keine epistemische Aufwertung.**
   Reconciliation darf `evidence_level`, `status` oder `adoption_basis` nicht
   erhöhen. Aufwertung erfordert neue Ausführung.

5. **Keine stillen Änderungen.**
   Jede Reconciliation muss in der PR-Beschreibung als solche deklariert werden
   (PR-Typ: `experiment_reconciliation`).

---

## Reconciliation-Ablauf

### 1. Ist-Zustand erfassen

- Manifest lesen und mit tatsächlichen Artefakten abgleichen
- `evidence.jsonl` auf Konsistenz prüfen
- `decision.yml` auf Aktualität prüfen

### 2. Abweichungen identifizieren

- Welche Felder im Manifest stimmen nicht?
- Fehlt Evidenz für Claims?
- Ist `iteration` > tatsächliche Ausführungen?

### 3. Korrekturen vornehmen

- Manifest-Felder auf Ist-Zustand setzen
- `execution_status` an tatsächliche Ausführung anpassen
- Ggf. `result.md` korrigieren (Claims ohne Evidenz entfernen)
- Ggf. `decision.yml` anpassen (Verdikt an Evidenzlage angleichen)

### 4. Validierung

```bash
make validate
make generate
```

Beide Befehle müssen ohne Fehler durchlaufen.

### 5. PR erstellen

- PR-Template: `experiment-run.md`
- PR-Typ: `experiment_reconciliation` ankreuzen
- Reconciliation-Sektion vollständig ausfüllen

---

## Ziel

> Konsistenz wiederherstellen — nicht Ergebnisse verbessern.

Reconciliation ist ein epistemischer Reparaturmodus. Das Ziel ist ausschließlich,
den dokumentierten Zustand mit dem tatsächlichen Zustand in Einklang zu bringen.

---

## Sichtbarkeit im Epistemic State

Der [Epistemic State Report](../_generated/epistemic-state.md) zeigt den
Reconciliation-Zustand jedes Experiments als abgeleitetes Feld:

| Wert | Bedeutung |
| ---- | --------- |
| **active** | Explizites Reconciliation-Artefakt gefunden (`reconciliation.md` oder `iteration*-reconciliation.md` in `artifacts/`) |
| **inferred** | Mögliche Inkonsistenz erkannt: `execution_status` ist `designed`/`prepared`, aber `evidence.jsonl` enthält Einträge |
| **none** | Kein Reconciliation-Signal erkannt |

**Hinweis:** Die Erkennung ist *heuristisch und indikativ*. Ein `none`-Wert
bedeutet nicht zwingend Konsistenz — er bedeutet nur, dass kein automatisch
erkennbares Signal vorliegt. Umgekehrt kann `active` auch einen bereits
abgeschlossenen Reconciliation-Prozess anzeigen.

### Typischer Workflow

1. `epistemic-state.md` zeigt `inferred` oder `active` → Signal zur Prüfung
2. Manueller Review: Ist das Experiment tatsächlich inkonsistent?
3. Falls ja: Reconciliation-Ablauf (siehe oben) durchführen
4. Nach erfolgreichem Reconciliation: `make generate` → Zustand aktualisiert sich automatisch
