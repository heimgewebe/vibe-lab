---
title: "Policy — Model-Lab Control Minimum"
status: active
canonicality: operative
created: "2026-05-30"
updated: "2026-05-30"
author: "ChatGPT"
triggered_by: "user-request-2026-05-30-model-lab-control-ap1"
relations:
  - type: references
    target: ../blueprints/blueprint-model-lab-control-plane-v1.md
  - type: references
    target: ../../schemas/run_meta.schema.json
  - type: references
    target: ../roadmap.md
---

# Policy — Model-Lab Control Minimum

## Zweck

Diese Policy definiert den kleinsten maschinenlesbaren Kontrollsatz fuer neue,
vergleichbare Model-Lab-Runs. Sie operationalisiert RM-008 / AP-1 als
opt-in-Vorbau: Ein Run kann sichtbar machen, ob die fuer Modell-, Tool-,
Challenge- und Evidence-Vergleichbarkeit noetigen Mindestfelder vorhanden sind.

Der zugehoerige Validator ist bewusst additiv. Er erzeugt einen fruehen,
reportierbaren Check fuer aktivierte Runs, ohne bestehende Experimente oder das
globale `run_meta`-Schema rueckwirkend zu haerten.

## Anwendungsbereich

Die Policy gilt fuer `run_meta.json`-Dateien, die explizit aktivieren:

```json
{
  "model_lab_control": true
}
```

Nur solche Dateien sind fuer den Lab-Control-Minimum-Validator
anwendungspflichtig. Runs ohne diese Aktivierung bleiben historische oder
nicht vergleichbarkeitsbezogene Runs und werden durch diese Policy nicht
beanstandet.

## Pflichtfelder bei Aktivierung

Ein aktivierter Run muss folgende Felder im `run_meta.json` fuehren:

- `model_id`
- `model_provider`
- `model_version_or_date`
- `tooling`
- `agent_mode`
- `challenge_id`
- `challenge_version`
- `condition`
- `control_condition`
- `temperature_or_sampling`
- `run_started_at`
- `run_finished_at`
- `human_intervention_level`
- `evidence_artifacts`

`evidence_artifacts` muss eine nicht-leere Liste nicht-leerer String-Referenzen
sein. Die uebrigen Mindestfelder muessen als nicht-leere Strings vorhanden sein.

## Aktivierungsmodus

- Aktivierung erfolgt ausschliesslich ueber `model_lab_control: true` im
  jeweiligen `run_meta.json`.
- Der Validator darf Verzeichnisse scannen, enforced aber nur aktivierte Runs.
- Fixture-Tests duerfen blocking sein, damit die Validator-Logik stabil bleibt.
- Ein globaler Block gegen alle historischen `run_meta.json`-Dateien ist durch
  diese Policy nicht vorgesehen.

## Altbestandsschutz

Bestehende Runs ohne `model_lab_control: true` werden nicht migriert, nicht
umgedeutet und nicht wegen fehlender Model-Lab-Felder beanstandet. Insbesondere
werden keine neuen Pflichtfelder in `schemas/run_meta.schema.json` eingefuehrt
und keine bestehenden Experimente nachtraeglich auf Vergleichbarkeit hochgestuft.

## Nicht-Ziele

Diese Policy aktiviert nicht:

- globale Schema-Haertung fuer `run_meta.json`,
- verpflichtendes `challenge_version` fuer alle `decision.yml`,
- Migration historischer Experimente,
- Reaktivierung von Catalog-Staleness,
- Start einer neuen Model-Lab-Replication-Series,
- Outcome-, Adoption- oder Best-Practice-Hochstufungen.

## Traceability

- `triggered_by`: `user-request-2026-05-30-model-lab-control-ap1`
- `policy`: RM-008 / AP-1 Lab-Control-Minimum als opt-in Validator-Vorbau
- `action`: Policy-Dokument und Validator-Fixture-Surface anlegen
- `outcome`: Vergleichbarkeits-Metadaten werden fuer aktivierte Runs pruefbar,
  ohne Altbestand zu blockieren
