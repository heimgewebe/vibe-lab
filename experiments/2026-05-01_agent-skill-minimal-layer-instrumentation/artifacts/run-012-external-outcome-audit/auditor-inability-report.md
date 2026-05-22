# Auditor Inability Report — run-012 external outcome audit

Datum: 2026-05-21
Run-Pfad: experiments/2026-05-01_agent-skill-minimal-layer-instrumentation/artifacts/run-012-external-outcome-audit/
Status: HISTORISCHER STOP (am 2026-05-21 durch schema-kompatibles Mapping aufgelöst; auditor-output.yml ist im Run-Bundle vorhanden)

## 1) Welches Schema/Contract fehlt oder blockiert

Die geforderte Pflichtstruktur fuer auditor-output ist mit dem aktuell aktiven Contract/Schema nicht kompatibel:

- Aktiv im Repo:
  - Contract: auditor_output
  - Schema: schemas/auditor-output.v1.schema.json
- Erwartete Top-Level-Felder laut aktivem Schema:
  - schema_version, contract, run_id, auditor, overall_verdict, claims
- Zuschnitt laut Audit-Anweisung (Pflichtstruktur):
  - claim_assessments (statt claims)
  - overall_verdict mit Werten aus {sufficient, insufficient, mixed, invalid, CLAIM_NOT_PROVEN}
  - auditor-Objekt mit Feldern wie same_execution_context_as_run_011, produced_prior_related_artifacts, inspected_commit, base_commit, independence_claim, independence_reason

Konflikte zum aktiven Schema:

1. claim_assessments ist im aktuellen Schema nicht erlaubt (additionalProperties: false auf Top-Level; erwartetes Feld ist claims).
2. overall_verdict-Werte sind nicht kompatibel. Das Schema erlaubt nur:
   PASS, CLAIM_NOT_PROVEN, CONTRADICTION, MISSING_EVIDENCE, OUT_OF_SCOPE, NOT_REPRODUCIBLE.
3. claim_assessments.verdict-Werte (PASS, FAIL, MIXED, CLAIM_NOT_PROVEN, NOT_APPLICABLE) sind nicht kompatibel mit den im Claim-Schema erlaubten Verdicts.
4. Mehrere geforderte Auditor-Felder sind im aktuellen auditor-Objekt nicht definiert und wuerden wegen additionalProperties: false scheitern.

## 2) Warum kein valider Audit-Output erzeugt werden kann

Der Auftrag fordert gleichzeitig:

- Nutzung des bestehenden Contracts auditor_output (kein neuer Contract), und
- eine Pflichtstruktur, die vom bestehenden auditor-output.v1-Schema nicht akzeptiert wird.

Da die Validatoren den aktiven auditor-output.v1-Contract erzwingen, waere ein solcher auditor-output.yml nicht schema-valid und wuerde in den verpflichtenden Validation-Checks fehlschlagen.

Eine improvised Struktur mit nicht akzeptierten Feldern ist laut Auftrag explizit verboten.

## 3) Minimale Contract-/Schema-Entscheidung, die noetig waere

Es gibt zwei minimale, saubere Wege. Einer muss vor Erstellung eines validen run-012 auditor-output entschieden werden:

Option A (Schema-Erweiterung innerhalb auditor_output):

- auditor-output.v1 um kompatible Mapping-Felder erweitern, z. B.:
  - claim_assessments als erlaubtes Alias zu claims, oder
  - claims als kanonisches Feld beibehalten und claim_assessments als strukturtreues Zusatzfeld erlauben.
- overall_verdict-Mapping explizit festlegen:
  - sufficient -> PASS
  - insufficient/mixed/invalid -> CLAIM_NOT_PROVEN oder eigene, neu definierte Enum-Werte
- auditor-Objekt um die geforderten Unabhaengigkeitsfelder erweitern.

Option B (Instruktionsanpassung auf bestehendes Schema, ohne Schemaaenderung):

- Pflichtstruktur auf bestehende auditor_output-v1-Felder abbilden:
  - claim_assessments -> claims
  - neue Audit-Details ausschliesslich unter extensions
  - overall_verdict strikt innerhalb der existierenden Enum-Werte halten

## Follow-up 2026-05-21 — STOP resolved by schema-compatible mapping

Der ursprüngliche STOP-Zustand wurde durch Option B aufgelöst:
Die Auditstruktur wurde auf den bestehenden `auditor_output`-v1-Contract abgebildet, ohne Schemaänderung.
Dieser Report bleibt als historische Diagnose erhalten. Er beschreibt nicht mehr den aktuellen Zustand von run-012.

Aktueller Zustand:
- `auditor-output.yml` ist vorhanden.
- `overall_verdict` bleibt `CLAIM_NOT_PROVEN`.
- Outcome utility bleibt unbewiesen.
- RM-002 und RM-005 bleiben offen.
- Der Run ist audit-only und nicht als vergleichbarer Outcome-Run zu zählen.
