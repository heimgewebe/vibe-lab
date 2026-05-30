---
title: "Blueprint — Model-Lab Control Plane v1"
status: draft
canonicality: exploratory
created: "2026-05-30"
updated: "2026-05-30"
author: "ChatGPT"
triggered_by: "user-request-2026-05-30-model-lab-blueprint"
relations:
  - type: derived_from
    target: ../foundations/vision.md
  - type: derived_from
    target: ../foundations/repo-plan.md
  - type: references
    target: ./blueprint-v2.md
  - type: references
    target: ./blueprint-evidence-control-plane-v1.md
  - type: references
    target: ../playbooks/evidence-control-plane-roadmap-checklist.md
  - type: references
    target: ../../schemas/experiment.manifest.schema.json
  - type: references
    target: ../../schemas/run_meta.schema.json
  - type: references
    target: ../../schemas/decision.schema.json
---

# Blueprint — Model-Lab Control Plane v1

## Status dieser Datei

Diese Datei ist ein **explorativer Blueprint**. Sie beschreibt eine geplante
Kontrollschicht für vergleichbare Vibe-Coding-Experimente, aktiviert aber keine
neuen Pflichtfelder, keinen Staleness-Generator, keine Validatoren und keine
CI-Enforcement-Regeln.

Maßgebliche Wahrheitsquellen bleiben `repo.meta.yaml`, `AGENTS.md`,
`agent-policy.yaml`, `contracts/`, `schemas/` und `.vibe/`. Die hier genannten
Arbeitspakete werden erst durch spätere, explizit geprüfte Änderungen operativ.

---

## 0. Kurzfassung

Diese Blaupause macht aus dem aktuellen `vibe-lab` kein größeres Archiv, sondern
ein prüfbares Modell-Labor: Vibe-Coding-Praktiken werden nicht nur gesammelt,
sondern als kontrollierte, replizierbare und vergleichbare Experimente geführt.

Der nächste sinnvolle Entwicklungsschritt ist **nicht** zuerst ein großer
Experimentausbau, sondern eine kurze **Lab-Control-Schicht**:

1. Benchmark-Versionierung als Welle-1-Enforcement vorbereiten.
2. Run-/Model-Metadaten standardisieren.
3. Staleness nur nach expliziter Systementscheidung reaktivieren.
4. Ein erstes replizierbares Experimentbündel über Modelle, Aufgaben und Modi
   definieren.
5. Aus den Ergebnissen nicht sofort neue Best Practices ableiten, sondern
   zunächst Vergleichbarkeit herstellen.

Humorige Warnung: Ohne diese Kontrollschicht wird das Lab schnell zum Gewächshaus
für schöne Prompts. Es wächst viel, aber niemand weiß, ob es Tomaten sind oder
epistemischer Efeu.

## 1. These / Antithese / Synthese

### These

Das `vibe-lab` ist bereits stark genug, um als Modell-Lab zu funktionieren: Es
besitzt Experimente, Katalog, Prompts, Agentenartefakte, Evidence Packs,
Playbooks, Schemas, CI-Validatoren und generierte Metriken.

### Antithese

Genau diese Stärke erzeugt ein neues Risiko: Das Repo kann sehr viel
dokumentieren, ohne dass Ergebnisse zwischen Modellen, Aufgaben, Agenten und
Zeitpunkten wirklich vergleichbar sind. Dann entsteht kein Modell-Lab, sondern
ein gut validiertes Erinnerungszimmer.

### Synthese

Die nächste Optimierung muss Vergleichbarkeit vor Expansion stellen. Erst wenn
`challenge_version`, `model_id`, `tooling`, `run_meta`, Kontrollbedingung und
Outcome-Metrik sauber greifbar sind, lohnt sich eine größere Experimentreihe.

## 2. Zielbild

Das `vibe-lab` wird zu einem **Model-Lab für Vibe-Coding-Praktiken**.

Ein Model-Lab bedeutet hier:

- Praktiken werden als Hypothesen behandelt, nicht als Stilvorlieben.
- Jede relevante Aussage ist an ein Experiment, einen Run, ein Modell, eine
  Aufgabe und eine Entscheidung rückbindbar.
- Positive, negative und inkonklusive Ergebnisse bleiben sichtbar.
- Katalogeinträge sind nicht bloß „nützlich“, sondern zeitlich,
  domänenspezifisch und evidenzgebunden.
- Agentenarbeit wird operationalisiert: Vorbereitung, Durchführung, Prüfung,
  Rework und Review werden als Artefaktfluss erfasst.

## 3. Nicht-Ziele

Diese Blaupause soll ausdrücklich nicht:

- sofort ein automatisches Best-Practice-Orakel bauen,
- Vibe-Coding allgemein bewerten,
- Modelle pauschal ranken,
- Staleness-Generatoren aktivieren, solange die bestehende dormant-Entscheidung
  nicht aufgehoben ist,
- neue Katalogclaims ohne neue Evidenz erzeugen,
- das Repo in ein Tool-Monster verwandeln, das mehr misst als es versteht.

## 4. Ausgangslage

### Belegt im Repo

- Das Repo arbeitet bereits mit dem Fluss `raw-vibes/` → `experiments/` →
  `catalog/` / `prompts/adopted/`.
- Es existieren strukturierte Experimente mit `manifest.yml`, `method.md`,
  `CONTEXT.md`, `INITIAL.md`, `evidence.jsonl` und `decision.yml`; mehrere
  spätere Runs führen zusätzlich `run_meta.json` als Execution-Proof.
- Es existieren Katalogeinträge, Anti-Patterns, Workflows, Combos und
  Tool-Exports.
- Es existiert ein Guard-/Validator-Stack mit Schemas und Regressionstests.
- Es existieren Agent-Operability- und Evidence-Control-Plane-Stränge.
- Der Repo-Plan markiert mehrere Phase-C- und Phase-D-Funktionen als offen oder
  bewusst zurückgestellt.

### Plausibel

- Der nächste Qualitätsgewinn entsteht weniger durch noch mehr
  Einzel-Experimente als durch Vergleichbarkeit, Versionierung und bessere
  Ergebnis-Synthese.
- Die vorhandenen Evidence-Control-Plane-Artefakte sind ein geeigneter Hebel, um
  das Lab von „gute Notizen“ zu „prüfbarer Laborbetrieb“ zu verschieben.

### Spekulativ

- Ein interaktives Dashboard oder ein MCP-Onboarding-Bot kann später nützlich
  sein, ist aber erst nach stabilen Datengrundlagen sinnvoll.

## 5. Prämissencheck

Die Empfehlung gilt nur, wenn folgende Annahmen wahr sind:

1. Das Ziel ist nicht bloß bessere Dokumentation, sondern bessere
   Entscheidbarkeit.
2. Das Repo soll Praktiken über mehrere Modelle, Tools und Aufgaben hinweg
   vergleichen können.
3. Bestehende Experimente sollen nicht entwertet, sondern sauberer eingeordnet
   werden.
4. Die vorhandenen Guardrails sollen weiter als CI-/Schema-Disziplin wirken,
   nicht durch menschliches Bauchgefühl ersetzt werden.
5. Die Lab-Struktur soll bewusst klein genug bleiben, um tatsächlich benutzt zu
   werden.

Wenn stattdessen das Ziel primär „schneller produktiv coden“ ist, wäre der
Alternativpfad: weniger Lab, mehr Playbooks, weniger Metrik. Das wäre nicht
falsch, aber ein anderes Projekt.

## 6. Alternative Sinnachse

Die naheliegende Frage lautet: „Wie verbessern wir das Repo?“

Die tiefere Frage lautet: „Welche Unsicherheit soll das Repo künftig besser
auflösen?“

Diese Blaupause ordnet daher nicht nach Ordnern, sondern nach
Unsicherheitsklassen:

| Unsicherheit | Optimierungshebel | Artefakt |
|---|---|---|
| Funktioniert eine Praktik nur in einem Task? | Benchmark-Versionierung | `challenge_version` |
| Funktioniert sie nur mit einem Modell? | Model-Metadaten | `run_meta.json` / `evidence.jsonl` |
| Ist der Effekt nur Tokenlänge oder Struktur? | Kontrollarme | `method.md` / `decision.yml` |
| Ist ein Katalogeintrag veraltet? | Staleness-Signal | `stale-entries.md` |
| Ist eine Aussage zu stark? | Interpretation Budget | `decision.yml` / Policy |
| Ist Agentenarbeit wirklich überprüfbar? | Evidence Control Plane | Evidence Pack / Review Events |

## 7. Arbeitspakete

### AP-0 — Blueprint verankern

#### Ziel

Diese Blaupause als Orientierungspunkt im Repo ablegen.

#### Zielpfad

`docs/blueprints/blueprint-model-lab-control-plane-v1.md`

#### Umsetzung

- Datei mit Frontmatter, Relationen und `triggered_by` anlegen.
- Von `docs/roadmap.md` referenzieren.
- In `docs/index.md` als Blueprint aufnehmen.

#### Akzeptanzkriterien

- `make validate` läuft grün.
- Relations-Validator akzeptiert alle Targets.
- Der Blueprint enthält Scope, Nicht-Ziele, Phasen, Gates und Risiken.

#### Optimierungsgrad

- **Was:** Orientierung und Priorisierung.
- **Wie:** Ein zusammenhängender Blueprint statt verstreuter Planpunkte.
- **Wodurch:** Entscheidungs- und Umsetzungsachsen werden explizit.
- **Wirkung:** Mittel. Kein Codegewinn, aber weniger Drift bei Folge-PRs.

### AP-1 — Lab-Control-Minimum definieren

#### Ziel

Ein Minimalset an Feldern festlegen, ohne das neue Experimente nicht
vergleichbar sind.

#### Pflichtfelder für neue replizierbare Runs

In `run_meta.json` oder zugehörigem Evidence Pack:

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

In `evidence.jsonl`:

- `event_type`
- `metric`
- `value`
- `context`
- `iteration`
- `artifact_ref`
- optional: `model_id`, falls nicht eindeutig über Run-Kontext ableitbar

#### Akzeptanzkriterien

- Schema oder Validator erkennt fehlende Pflichtfelder bei neuen
  Lab-Control-Runs.
- Bestehende historische Experimente bleiben kompatibel.
- Neue Pflicht gilt nur für Experimente mit `execution_status: executed` oder
  `replicated` ab Aktivierungsdatum.

#### Stop-Kriterium

Kein Schema-Hardening gegen Altbestand ohne Migrationsregel.

### AP-2 — Benchmark-Challenge-Versionierung hart machen

#### Ziel

Jede vergleichende Entscheidung muss auf eine versionierte Challenge
referenzieren.

#### Umsetzung

- `benchmarks/challenges/*.md` erhalten ein standardisiertes Frontmatter:
  - `challenge_id`
  - `version`
  - `task_family`
  - `expected_outputs`
  - `evaluation_criteria`
  - `known_confounders`
- `decision.yml` erhält für vergleichende Experimente ein Pflichtfeld:
  - `challenge_version`
- Validator ergänzen:
  - prüft, ob Challenge-Datei existiert,
  - prüft, ob Version passt,
  - blockiert neue vergleichende Decisions ohne Version.

#### Akzeptanzkriterien

- Mindestens drei vorhandene Challenges sind versioniert.
- Ein Testfixture ohne `challenge_version` schlägt fehl.
- Ein Testfixture mit gültiger Version besteht.

#### Nutzen

Ergebnisse werden zwischen Experimenten vergleichbar. Ohne Versionierung sagt
„Spec-First war besser“ ungefähr so viel wie „dieser Kaffee war wach“:
wahrscheinlich wahr, aber laboruntauglich.

### AP-3 — Staleness nur bewusst reaktivieren

#### Ziel

Katalog-Verfall sichtbar machen, ohne die bestehende dormant-Entscheidung zu
übergehen.

#### Umsetzung

1. Systementscheidung anlegen:
   - `decisions/system/YYYY-MM-DD-catalog-staleness-reactivation-preimage.yml`
2. Entscheidung klärt:
   - Welche Katalogtypen werden geprüft?
   - Welche Felder sind Pflicht?
   - Ist der Generator blocking, non-blocking oder report-only?
   - Werden Issues automatisch erstellt oder nur Reports erzeugt?
3. Erst danach:
   - `generate_stale_entries.py` implementieren oder aktivieren.
   - `docs/_generated/stale-entries.md` erzeugen.

#### Akzeptanzkriterien

- Kein Generator ohne Systementscheidung.
- Katalogeinträge erhalten `last_validated`, `review_cycle`, `next_review_due`
  nur, wenn Schema und Policy geklärt sind.
- `make validate` bleibt für Altbestand stabil.

#### Risiko

Zu frühe Staleness-Automatik erzeugt Review-Lärm. Dann hat man zwar ein lernendes
System, aber es klingt wie ein Rauchmelder in einer Teeküche.

### AP-4 — Experimentreihe „Model-Lab Replication Series“ starten

#### Ziel

Die wichtigsten bestehenden Praktiken über mehrere Aufgaben, Modelle und
Kontrollbedingungen replizieren.

#### Zielpfad

`experiments/YYYY-MM-DD_model-lab-replication-series/`

#### Fokuspraktiken

1. Spec-First Prompting
2. Prompt-Length Control
3. TDD-/Test-First Vibe
4. Premortem Prompting
5. Agent-Skill Minimal Layer / Evidence-Control-Plane

#### Task-Familien

- REST API
- CLI Parser
- UI-Komponente
- Legacy Refactoring
- Test-Hardening
- Dokumentations-/Contract-Fix

#### Modelle / Agenten

- Copilot / GitHub Agent Mode
- Claude Code
- Gemini
- optional: lokales Modell oder Open-Source-Agent

#### Minimaldesign

Pro Praktik:

- 2 Aufgabenfamilien
- 2 Modelle oder Agentensysteme
- 1 Kontrollbedingung
- 1 replizierter Run

#### Primärmetriken

- `test_pass_rate`
- `edge_cases_missed`
- `rework_steps_required`
- `rework_lines`
- `manual_intervention_count`
- `time_to_validated_change_seconds`
- `scope_drift_count`
- `review_findings_count`

#### Sekundärmetriken

- `flow_confidence`
- `cognitive_load_score`
- `diagnosis_clarity_score`
- `artifact_completeness_score`

#### Akzeptanzkriterien

- Jeder Run besitzt `run_meta.json`.
- Jeder Run verweist auf eine Challenge-Version.
- Jeder Run hat mindestens einen maschinenlesbaren Evidence-Eintrag.
- Jede Decision trennt Ergebnis, Interpretation und Adoption.

### AP-5 — Evidence-Control-Plane als Lab-Rückgrat nutzen

#### Ziel

Agenten- und Review-Ergebnisse nicht nur als Dateien sammeln, sondern als
wiederholbares Kontrollsystem verwenden.

#### Umsetzung

- Bestehende Evidence-Pack-Struktur als Pflicht für replizierte Agentenläufe
  definieren.
- Review Events standardisieren.
- Auditor-Output und Make-Validate-Output als primäre Belege behandeln.
- Self-Reported-Only-Pass verbieten.

#### Akzeptanzkriterien

- Ein replizierter Agentenlauf kann nicht `pass` sein, wenn nur Selbstauskunft
  vorliegt.
- Externe oder repo-lokale Belege werden getrennt klassifiziert.
- Review-Rework-Ereignisse sind maschinenlesbar.

### AP-6 — Model-Lab-Metriken ausbauen

#### Ziel

Das bestehende Metrik-Dashboard von Ereigniszählung zu Lab-Auswertung erweitern.

#### Umsetzung

Neue Reports:

- `docs/_generated/metrics/model-comparison.md`
- `docs/_generated/metrics/challenge-outcomes.md`
- `docs/_generated/metrics/practice-replication.md`
- `docs/_generated/metrics/interpretation-risk.md`

Aggregationen:

- pro Praktik
- pro Challenge
- pro Modell / Tooling
- pro Kontrollbedingung
- pro Outcome-Status

#### Akzeptanzkriterien

- Reports sind generated und nicht manuell editiert.
- Fehlende Metadaten werden sichtbar, aber nicht still geglättet.
- Kein Ranking ohne Mindest-N und Challenge-Vergleichbarkeit.

### AP-7 — Tool-Exports verbreitern, aber nach Lab-Control

#### Ziel

Exports für weitere Agentensysteme bereitstellen, ohne die IR zu verwässern.

#### Reihenfolge

1. Erst Export-Zielmatrix dokumentieren.
2. Dann Adapter-Schema definieren.
3. Dann Generator erweitern.
4. Dann Parity-Test ergänzen.

#### Zielsysteme

- Copilot: vorhanden
- Cursor: vorhanden
- Claude: ergänzen / prüfen
- Gemini: ergänzen / prüfen
- generisches Markdown-Agent-Profil: ergänzen

#### Akzeptanzkriterien

- Jeder Export enthält deterministische Herkunftsmetadaten.
- Kein Export hat manuelle Abweichungen von `instruction-blocks/`.
- `validate_export_parity.py` blockiert Drift.

### AP-8 — Onboarding und Playbooks auf Lab-Betrieb ausrichten

#### Ziel

Neue Nutzer oder Agenten sollen nicht nur wissen, wo Dateien liegen, sondern wie
ein valider Lab-Run entsteht.

#### Neue oder zu ergänzende Dokumente

- `docs/onboarding/model-lab-quickstart.md`
- `docs/playbooks/run-comparative-experiment.md`
- `docs/playbooks/review-model-lab-run.md`
- `docs/playbooks/promote-replicated-practice.md`

#### Inhalte

- Wie wähle ich eine Challenge?
- Wie definiere ich Kontrollbedingungen?
- Wie verhindere ich Overclaiming?
- Wie dokumentiere ich menschliche Eingriffe?
- Wann ist ein Ergebnis `adopt`, `defer`, `mixed`, `reject`?

#### Akzeptanzkriterien

- Ein Anfänger kann einen Minimal-Run vorbereiten, ohne Schemawissen auswendig zu
  kennen.
- Ein Agent kann dieselben Schritte als Checkliste ausführen.
- Reviewer bekommen klare Stop-Kriterien.

### AP-9 — Reaktiver Minimal-Loop als Proof, nicht als Plattform

#### Ziel

Einen kleinen, prüfbaren Loop bauen: Signal erzeugt Handlungsvorschlag, aber
nicht unkontrollierte Aktion.

#### Minimalbeispiel

`STATE`: Katalogeintrag hat `next_review_due` überschritten.  
`SIGNAL`: `stale-entries.md` markiert Eintrag.  
`POLICY`: Staleness-Policy entscheidet report-only oder issue-proposed.  
`ACTION`: GitHub-Issue wird vorgeschlagen oder manuell erstellt.  
`EVALUATION`: Review aktualisiert Katalogstatus oder setzt neue Prüfung an.

#### Akzeptanzkriterien

- Jede Aktion hat `triggered_by`, `policy`, `action`, `outcome`.
- Keine automatische Katalogänderung ohne Review.
- Loop ist testbar über Fixture.

## 8. Umsetzungsreihenfolge

### Welle 1 — Kontrollbasis, klein und hart

1. AP-0 Blueprint verankern.
2. AP-1 Lab-Control-Minimum definieren.
3. AP-2 Benchmark-Versionierung einführen.
4. AP-4 Experimentreihe als leeren, aber validen Skeleton-Ordner anlegen.

**Warum zuerst:** Ohne diese Punkte sind spätere Experimente schwer vergleichbar.

### Welle 2 — Erste replizierte Evidenz

1. Eine kleine Model-Lab-Replication-Series durchführen.
2. Evidence-Control-Plane-Pflicht für replizierte Runs schärfen.
3. Metrikreports für Practice/Challenge/Model ergänzen.

**Warum danach:** Erst echte Daten zeigen, ob die neue Struktur nützt oder nur
hübsch sortiert ist.

### Welle 3 — Reaktive Diagnostik

1. Staleness-Preimage-Decision erstellen.
2. Staleness-Generator report-only aktivieren.
3. Knowledge-Gaps / Weak-Links nachziehen.
4. Reaktiven Minimal-Loop als Proof bauen.

**Warum spät:** Automatisierung ohne klare Semantik skaliert Fehler. Das ist
dann keine Evolution, sondern ein Staubsaugerroboter mit Promotionsrecht.

### Welle 4 — Distribution und Tooling

1. Export-Zielmatrix.
2. Claude/Gemini/generischer Agent-Export.
3. Onboarding vertiefen.
4. Optionaler MCP-/Agent-Onboarding-Prototyp.

## 9. Risiko- und Nutzenabschätzung

| Klasse | Nutzen | Risiko | Gegenmaßnahme |
|---|---|---|---|
| Technisch | Vergleichbare Runs, bessere Validatoren | Schema-Brüche im Altbestand | Aktivierungsdatum, historische Escape-Regel |
| Organisatorisch | Klarere PR-Reihenfolge | Mehr Prozesslast | Minimalfelder, gute Playbooks |
| Epistemisch | Weniger Overclaiming | Falsche Sicherheit durch Metriken | Interpretation Budget, Mindest-N, Counterevidence |
| Sozial | Bessere Agent-/Mensch-Koordination | Reviewer-Müdigkeit | Report-only zuerst, keine Auto-Flut |
| Sicherheit/Privacy | Bessere Evidence-Kontrolle | Secrets/Personendaten in Runs | Privacy-Lint, Redaction-Policy |
| Strategisch | Modell-Lab statt Prompt-Sammlung | Tool-Fokus statt Erkenntnis-Fokus | Praktik/Challenge als Primärachse |

## 10. Messgrößen für den Erfolg der Blaupause

### Nach Welle 1

- Neue vergleichende Decisions ohne `challenge_version` schlagen fehl.
- Neue replizierbare Runs ohne Model-/Tool-Metadaten schlagen fehl oder werden
  als incomplete markiert.
- Blueprint ist im Docs-Index auffindbar.

### Nach Welle 2

- Mindestens eine replizierte Experimentreihe enthält mehrere Modelle oder
  Agenten.
- Mindestens zwei Aufgabenfamilien sind beteiligt.
- Mindestens eine Praktik bleibt `mixed` oder `defer`, statt künstlich auf
  `adopt` gezogen zu werden.

### Nach Welle 3

- Staleness ist sichtbar, aber nicht automatisch normativ.
- Mindestens ein Knowledge-Gap wird maschinell vorgeschlagen und menschlich
  eingeordnet.
- Der reaktive Loop erzeugt nachvollziehbare Traceability.

### Nach Welle 4

- Mindestens ein neuer Tool-Export besteht Parity-Tests.
- Ein neuer Nutzer kann mit Onboarding einen Minimal-Run durchführen.
- Agenten können Playbooks ohne implizite Repo-Kenntnis befolgen.

## 11. Resonanz- und Kontrastprüfung

### Deutung A — Das Repo braucht jetzt mehr Experimente

Plausibel, weil bereits genug Struktur vorhanden ist und ein Lab ohne Daten nur
ein Archiv mit Klemmbrett ist.

**Konsequenz:** Sofort neue Experimentreihen starten.

**Risiko:** Uneinheitliche Runs erzeugen Daten, die später schwer vergleichbar
sind.

### Deutung B — Das Repo braucht zuerst mehr Kontrollsemantik

Plausibel, weil die offenen Punkte vor allem Vergleichbarkeit, Versionierung,
Staleness und reaktive Traceability betreffen.

**Konsequenz:** Erst Lab-Control-Minimum und Challenge-Versionierung, dann
Replikationsserie.

**Risiko:** Zu viel Meta-Arbeit kann die Experimentlust dämpfen.

### Synthese

Eine kleine Kontrollschicht zuerst, aber sofort mit einer realen Experimentserie
koppeln. Kein abstrakter Kontrollpalast. Ein Labor braucht Regeln, aber auch
Dinge, die gelegentlich knallen.

## 12. Epistemische Leeren

Folgendes fehlt für eine patchreife Umsetzung der späteren Arbeitspakete:

- Ob Staleness weiterhin dormant bleiben soll oder reaktiviert werden darf.
- Gewünschte erste Modell-/Tool-Auswahl für die Replication-Series.
- Ob neue Schema-Felder sofort blocking oder zunächst report-only sein sollen.
- Ob einzelne Arbeitspakete nach der Blueprint-Verankerung als operative Policy,
  Validator oder Experiment-Skeleton umgesetzt werden sollen.

Diese Lücken blockieren keine Blaupause, aber sie blockieren einen idealen
Umsetzungs-Patch über AP-0 hinaus.

## 13. Empfehlung

Die nächste konkrete Umsetzung sollte **Welle 1** sein:

1. Blueprint ins Repo legen.
2. Lab-Control-Minimum als Policy/Concept dokumentieren.
3. Challenge-Versionierung als Validator-Vorbau bauen.
4. Eine kleine `model-lab-replication-series` als Skeleton anlegen.

Nicht zuerst Staleness bauen. Nicht zuerst Dashboard bauen. Nicht zuerst
Tool-Exports verbreitern. Die Reihenfolge ist wichtig: Erst Vergleichbarkeit,
dann Wachstum.

## 14. Mini-Glossar für Anfänger

- **Blueprint:** Ein Bauplan für eine Repo-Entwicklung. Nicht der fertige Code,
  sondern die prüfbare Richtung.
- **Benchmark:** Eine wiederholbare Aufgabe, an der verschiedene Methoden
  verglichen werden.
- **Challenge-Version:** Die genaue Version einer Benchmark-Aufgabe. Wichtig,
  damit Ergebnisse nicht auf veränderten Aufgaben verglichen werden.
- **Run:** Eine konkrete Durchführung eines Experiments.
- **run_meta.json:** Maschinenlesbare Metadaten zu einem Run.
- **Evidence:** Belegmaterial, etwa Testausgaben, Review-Kommentare, Messwerte
  oder Artefakte.
- **Staleness:** Wissensverfall. Ein Katalogeintrag war einmal plausibel, kann
  aber veraltet sein.
- **Control Condition:** Kontrollbedingung. Sie zeigt, ob ein Effekt wirklich an
  der getesteten Methode liegt oder an etwas anderem.
- **Overclaiming:** Eine Aussage stärker machen, als die Evidenz erlaubt. In
  Laboren ist das der kleine Bruder der Selbsttäuschung mit Krawatte.

## 15. Essenz

**Hebel:** Vergleichbarkeit vor Expansion.  
**Entscheidung:** Welle 1 starten, Staleness noch nicht automatisieren.  
**Nächste Aktion:** Blueprint committen, dann Lab-Control-Minimum und
Challenge-Versionierung als ersten kleinen PR umsetzen.
