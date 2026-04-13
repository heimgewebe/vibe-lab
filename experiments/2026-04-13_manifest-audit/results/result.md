---
title: "Ergebnis: Manifest-Audit"
status: inconclusive
canonicality: exploratory
---

# Ergebnis: Manifest-Audit

## Aufgabe

Ein ~60-LOC-Python-Skript schreiben und ausführen, das Inkonsistenzen zwischen
`execution_status` in `manifest.yml` und dem tatsächlichen Zustand der `evidence.jsonl`-Dateien
erkennt.

## Durchführung

Das Skript (`artifacts/audit.py`) wurde geschrieben und einmal ausgeführt:

```
python3 artifacts/audit.py
```

Ausgabe (vollständig in artifacts/audit_output.txt, verkürzt hier):

```
Geprüfte Experimente: 3
Inkonsistenzen: 3
[!] 2026-04-08_spec-first    — execution_status fehlt, aber 13 Evidenzeinträge
[!] 2026-04-11_yolo-vs-spec-first — execution_status fehlt, aber 5 Evidenzeinträge
[!] 2026-04-12_spec-first-legacy  — execution_status fehlt, aber 5 Evidenzeinträge
```

## Beobachtungen (rein deskriptiv)

- Alle 3 vorhandenen Experimente haben kein `execution_status`-Feld in manifest.yml.
- Alle 3 haben `evidence.jsonl`-Dateien mit mindestens 5 Einträgen.
- Das Skript lief ohne Fehler (exit code 1 = Inkonsistenzen gefunden, wie vorgesehen).
- Kein anderer Inkonsistenz-Typ wurde ausgelöst (nur Typ: "Feld fehlt trotz Evidenz").
- Die Erwartung (≥1 Inkonsistenz) wurde übertroffen (3/3 Experimente betroffen).

## Deutung / Interpretation

Das fehlende Feld ist eine Deklarationslücke, keine Täuschung:
Die Evidenz existiert — die Experimente wurden faktisch durchgeführt.
Das `execution_status`-Feld wurde schlicht nie gesetzt.

Das Schema macht `execution_status` optional. Das Template zeigt es als Standard-Feld.
Diese Divergenz zwischen Schema (optional) und Template (prominent als Default) erzeugt
einen stillen Spielraum: Autoren können das Feld weglassen, ohne gegen das Schema zu verstoßen,
aber das Template legt nahe, es zu setzen.

Ob das Skript hier "richtig" meldet, hängt davon ab, was man prüfen möchte:
- Deklarativer Zustand vs. tatsächlicher Zustand → Inkonsistenz, korrekt erkannt
- Wahrheitsgehalt der Evidenz → kein Problem, Evidenz ist real

## Ergebnisurteil

**Inconclusive.**

Die Hypothese ("das Skript findet mindestens eine echte Inkonsistenz") trifft technisch zu.
Die inhaltliche Bedeutung dieser Inkonsistenz ist jedoch ambivalent.
Eine Empfehlung für Systemänderungen wäre hier verfrüht.

---

## Beobachtungsauftrag — Reflexion

### 1. Wo hat die Struktur zu sauberem Denken gezwungen?

Die Trennung in `evidence.jsonl` hat mich gezwungen, die Vorab-Erwartung explizit als
eigenen Eintrag zu deklarieren (event_type: observation, metric: pre_run_expectation).
Das war nützlich: es macht sichtbar, dass ich das Ergebnis vorhergesehen habe, und verhindert,
dass ein bestätigtes Ergebnis retrospektiv wie eine Entdeckung aussieht.

### 2. Wo war unklar, wie etwas einzuordnen ist?

Unklar war: Gehört die Reflexion nach `result.md` oder in eine separate `CONTEXT.md`?
Das Template verlangt `CONTEXT.md` für die Promotion, aber der Beobachtungsauftrag ist
kein Kontext, sondern Meta-Reflexion. Ich habe mich für `result.md` entschieden, da die
Reflexion Teil des Ergebnisses ist und keine Promotionsvoraussetzung besteht.

Außerdem: Ist ein `false_positive` ein Beobachtungs- oder Messwert? Ich habe es als
`observation` geführt, weil keine numerische Grundlage für eine Messung bestand.

### 3. Wo hat die Struktur geholfen?

Die `method.md` hat mich gezwungen, die Inkonsistenz-Regeln vor der Skript-Implementierung
zu definieren. Das vermied post-hoc Regelanpassung an gefundene Ergebnisse.

Die Trennung execution_status / status / evidence_level im Schema ist konzeptuell klar
und hat die Audit-Logik vereinfacht: drei orthogonale Achsen, die unabhängig inkonsistent
sein können.

### 4. Wo hat Struktur Reibung erzeugt?

Die `execution_refs`-Anforderung im Schema (`required` wenn `execution_status: executed`)
ist sinnvoll, aber unbequem: für dieses Experiment müsste ich einen Pfad zu
`artifacts/audit.py` und `results/evidence.jsonl` als `execution_refs` angeben —
das wirkt zirkulär (das Experiment referenziert seine eigenen Artefakte als Beweis
seiner Durchführung). Ich habe `execution_status: designed` behalten und am Ende
manuell auf `executed` gesetzt — das ist die ehrlichere Darstellung der Zeitlinie.

### 5. War ich versucht, etwas epistemisch aufzuwerten?

Ja: Nach dem Skriptlauf war der Impuls vorhanden, den Status auf `adopted` zu setzen —
"hat funktioniert, Ergebnis bestätigt". Das wäre falsch gewesen:
- Ein einziger Lauf, 3 Datenpunkte
- Die "Inkonsistenz" ist semantisch ambivalent
- Kein Vergleich mit alternativer Methode
- Keine unabhängige Replikation

`inconclusive` ist das ehrlichere Urteil.

---

## Kurze Reflexion

**Was hat funktioniert:**
Die Aufgabenauswahl war gut — klein, real, ausführbar, mit messbarem Output.
Das Festhalten der Vorab-Erwartung als eigenem evidence-Eintrag war epistemisch wertvoll.

**Was war unklar:**
Wo genau die Grenze zwischen "observation" und "interpretation" in JSONL-Notizen liegt.
Die Felder `notes` und `metric`+`value` laden dazu ein, Beobachtung und Deutung zu mischen.

**Gerechtfertigte Verbesserung (eine):**
Template-Kommentar für `execution_status` klarstellen: Feld sollte gesetzt werden,
sobald `evidence.jsonl` Einträge hat — auch wenn das Schema es nicht erzwingt.

**Verfrühte Verbesserung:**
`execution_status` zum Pflichtfeld im Schema machen. Das würde alle bestehenden
Manifests schema-invalid machen und ist eine Systemänderung mit breitem Impact —
ohne hinreichende Grundlage aus einem einzelnen Audit.
