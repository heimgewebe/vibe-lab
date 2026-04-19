---
title: "Cross-Run-Auswertung: Generated Artifact Contract Validation"
status: draft
canonicality: operative
relations:
  - type: informed_by
    target: result.md
---

# Cross-Run-Auswertung — Generated Artifact Contract Validation

## 1. Bewertungsrahmen

### Zielhypothese
Die Trennung in `canonical` / `derived` / `ephemeral` plus das CI-Splitting in `blocking` / `non-blocking` / `artifact-only` reduziert Friktion oder macht sie klarer lokalisierbar.

### Diagnosefokus dieses PRs
Dieser PR bewertet nicht "noch einen Run", sondern isoliert ein wiederkehrendes Strukturmuster:
- stale `docs/_generated/system-map.md` nach Hinzufuegen von Run-Artefakten,
- wiederholter Konsolidierungs-Fix-Commit,
- offene Einordnung: Workflow-Artefakt vs Architekturproblem.

### Trigger
`triggered_by: user-request-new-pr-structural-friction-isolation-2026-04-19`

## 2. Run-Matrix (nur Run-003 bis Run-006)

| Run | PR | stale system-map | Wann | Lokaler Vorlauf | Ausloeser | Zusatz-Commit |
|---|---|---|---|---|---|---|
| Run-003 | PR-62 | ja | nach Artifact-Write, im PR-CI | lokal unauffaellig dokumentiert | Konsolidierungs-Commit mit neuen run-003 Artefakten | ja (1x) |
| Run-004 | PR-63 | ja | nach Artifact-Write, im PR-CI | kein lokaler Vorabfail dokumentiert | Konsolidierungs-Commit mit neuen run-004 Artefakten | ja (1x) |
| Run-005 | PR-64 | ja | nach Artifact-Write, im PR-CI | kein lokaler Vorabfail dokumentiert | Konsolidierungs-Commit mit neuen run-005 Artefakten | ja (1x) |
| Run-006 | PR-67 | ja | nach Artifact-Write, im PR-CI | vor Artifact-Write clean (double-generate + validate) | Write von run-006 Artefakten und anschliessender validate-Lauf | ja (1x) |

## 3. Strukturelles Friktionsmuster (Diagnoseoberflaeche)

### 3.1 Belegt
- In allen Runs 003-006 trat stale `system-map.md` im PR-CI nach Konsolidierung auf.
- Pro Run war ein zusaetzlicher Commit zur canonical-Regeneration noetig.
- Die jeweilige `system-map`-Diff zeigt konsistent +2 Dateien im Block `experiments/` und +2 im Total.
- Generatorlogik zaehlt getrackte Dateien via `git ls-files`; neue Artefaktdateien sind damit direkt relevant fuer die `system-map`.

### 3.2 Plausibel
- Primaerer Treiber ist die Workflow-Reihenfolge: Artefakte werden geschrieben, danach wird canonical state nicht sofort nachgezogen.
- Das Muster ist deterministisch genug, um als stabiler Konsolidierungspfad zu gelten (kein sporadischer Zufall, kein einmaliger Ausrutscher).

### 3.3 Offen
- Ob die Friktion nur ein Workflow-Artefakt ist, bleibt offen, solange canonical/blocking `system-map` auf run-interne Artefakte reagiert, die im selben Durchlauf entstehen.
- Damit bleibt eine architekturelle Restfrage: Ist die aktuelle Kopplung (run writes artifacts -> canonical drift -> blocking gate) gewollte Strenge oder unnoetige Selbstkopplung.

## 4. Workflow-Artefakt vs Architekturproblem

### Vorlaeufige Einordnung
- Arbeitsdiagnose: primaer workflowbedingt.
- Begruendung: Trigger sitzt konsistent nach Artifact-Write, Fix ist konsistent `generate-canonical`, und Ursache ist in der Zaehllogik transparent.

### Architektureller Restzweifel
- Die Workflow-Diagnose schliesst einen Architekturanteil nicht aus.
- Solange dieselbe Run-Durchfuehrung zwingend artefaktinduzierte canonical-Drift erzeugen kann, bleibt die Frage nach der Contract-Grenze offen.

## 5. Beobachtungen (nur belegt)

### Run-003
- Vor Konsolidierung keine canonical-Aenderung in system-map.
- Nach run-003 Artifact-Konsolidierung stale system-map im validate-Job.

### Run-004
- Kontrollierte semantic_friction injiziert.
- Blocking failure absichtlich erzeugt und schnell lokalisiert.
- Zusaetzlicher structural failure bei Konsolidierung (stale system-map).

### Run-005
- Kontrollierte semantic_friction erneut injiziert.
- Reproduzierbare Messung mit konsistenten Zeitmetriken.
- Structural consolidation failure erneut beobachtet.

### Run-006
- Natuerlicher Minimal-Run ohne kontrollierte Injektion.
- Pre-artifact Generatorlauf sauber und deterministisch.
- Structural consolidation failure (`stale system-map`) erneut beobachtet.

## 6. Minimaler Beweisplan (abgehakt)

1. Welche tracked files fliessen in system-map ein?
- Abgehakt: `generate_system_map.py` basiert auf `git ls-files`.

2. Gehen Artifact-Dateien unter `artifacts/run-*` in die Zaehlung ein?
- Abgehakt: Ja, indirekt ueber Top-Level-Aggregation `experiments/`; alle vier Fix-Commits zeigen +2 Dateien in diesem Block.

3. Entsteht Drift erst nach Artifact-Write?
- Abgehakt: Run-006 dokumentiert pre-artifact clean und post-artifact stale.

4. Bleibt Effekt bei reinem Doku-PR ohne neue Artefakte aus?
- Nicht vollstaendig abgehakt in diesem Datensatz; als Leerstelle markiert.

## 7. Kontrastive Deutung

### Deutung A (optimistisch)
Die Architektur entmischt Friktion:
- semantic failures werden schnell lokalisierbar,
- structural failures werden als eigener Typ sichtbar,
- clean runs bleiben moeglich,
- kontrollierte Friktion ist reproduzierbar messbar.

### Deutung B (skeptisch)
Die Architektur koennte Friktion eher umlagern als reduzieren:
- ein Teil der Kosten verschiebt sich in formale Fehlerklassen,
- Konsolidierungsfehler (`stale system-map`) treten wiederholt auf,
- der staerkste Vorteil liegt eventuell in Diagnoseklarheit statt Friktionssenkung.

## 8. Zwischenfazit

### Belastbar sagbar
- Friktion ist klarer klassifizierbar als vor dem Contract-Split.
- Clean runs sind moeglich.
- Semantic friction ist schnell detektierbar und behebbar.
- Structural friction bei Konsolidierung zeigt ein wiederkehrendes Muster.
- Kontrollierte Friktion ist reproduzierbar messbar.

### Noch nicht belastbar sagbar
- Dass das Modell Friktion insgesamt reduziert.
- Dass das CI-System insgesamt effizienter ist.
- Dass die Architektur bereits adoptable ist.
- Dass der beobachtete Vorteil generalisiert.

## 9. Structural Friction Pattern

Beobachtung:
- Wiederholter CI-Fehler: stale `system-map.md` bei Artefakt-Konsolidierung.

Eigenschaften:
- tritt nach Artifact-Adds auf,
- unabhaengig von semantic_friction,
- deterministisch reproduzierbar in mehreren Runs.

Offene Frage:
- Workflow-Artefakt (expected)
- oder Architekturproblem (unexpected)

Status:
- Triggerpfad ist hinreichend isoliert fuer ein `mixed`-Urteil.
- Vollstaendige Trennung Workflow-only vs Architekturanteil bleibt offen.

## 10. Vorschlag fuer Decision-Switch

### Auf `result_assessment` wechseln, wenn
- Friktionstypen und Messung ueber mehrere Runs stabil vergleichbar sind,
- die Hypothese teilweise inhaltlich beurteilt werden kann,
- und das Urteil explizit begrenzt formuliert wird.

## 11. Candidate Verdict Mapping

### `mixed`
Wenn belegt ist:
- Diagnoseklarheit steigt,
- Friktionstypen werden getrennt und lokalisierbar,
- aber Gesamtreduktion der Friktion bleibt unbelegt.

### `confirms`
Nur wenn belegt ist:
- clean runs sind keine Ausnahme,
- Friktion wird im Mittel geringer oder billiger,
- structural failure pattern ist verstanden oder behoben.

### `mixed`
Wenn belegt ist:
- Diagnoseklarheit steigt,
- Friktion sinkt aber nicht klar,
- oder Friktionstypen eher getrennt als reduziert werden.

### `inconclusive`
Wenn belegt ist:
- Runs existieren,
- aber Scope und Vergleichslogik noch nicht stabil genug sind.

### `refutes`
Nur wenn belegt ist:
- Contract-Split erzeugt systematisch neue oder teurere Friktion,
- clean runs bleiben Ausnahme,
- Wiederholung verbessert nichts.

## 12. Abschlussurteil

Urteil: `result_assessment: mixed`.

Warum `mixed`:
- Semantic friction ist gut lokalisierbar und behebbar.
- Structural friction ist wiederkehrend und an den Konsolidierungspfad gekoppelt.
- Clean runs sind moeglich, aber nicht stabil garantiert.

Warum nicht `confirms`:
- Keine belastbare Evidenz fuer robuste Gesamtsenkung der Friktion.

Warum nicht `adopt`:
- Structural pattern ist nicht isoliert; Architekturreife bleibt offen.

Delegierte Leerstelle fuer Folgeexperiment:
- Isolieren, ob `stale system-map` primaer Workflow-Artefakt oder Architekturproblem ist.

## 13. Aktueller methodischer Default

Empfohlener Zielkorridor fuer einen spaeteren `result_assessment`: `mixed` oder `inconclusive`.
Noch nicht freigeben, bis Vergleichsnormalisierung explizit abgeschlossen ist.

## 14. Offene Leerstelle

Es fehlt:
- eine explizite Baseline-Definition ohne Contract,
- eine bereinigte Vergleichsmatrix ohne Altlastverzerrung,
- ein sauberer Gegenlauf ohne neue Run-Artefakte, um Workflow-only gegen Architekturanteil haerter zu trennen.
